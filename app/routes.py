import logging
from typing import List, Optional

import fastapi
import markdown
from fastapi import Request, Response, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pyldapi import Renderer
import utils
from api.link import *
from config import LANDING_PAGE_URL

router = fastapi.APIRouter()
templates = Jinja2Templates(directory="templates")

MEDIATYPE_NAMES = {
    "text/html": "HTML",
    "application/json": "JSON",
    "application/geo+json": "GeoJSON",
    "text/turtle": "Turtle",
    "application/rdf+xml": "RDX/XML",
    "application/ld+json": "JSON-LD",
    "text/n3": "Notation-3",
    "application/n-triples": "N-Triples",
}


@router.get("/")
async def home(request: Request):
    try:
        logging.info(f"Landing page request: {request.path_params}")
        return LandingPageRenderer(request).render()
    except Exception as e:
        logging.info(e)
        return HTTPException(detail=e, status_code=500)


class LandingPageRenderer(Renderer):
    def __init__(
            self,
            request,
            other_links: List[Link] = None,
    ):
        logging.debug("LandingPageRenderer()")
        self.request = request
        super().__init__(request,
                         self.request.base_url,
                         utils.get_profiles("http://www.w3.org/ns/dcat#Catalog"),
                         MEDIATYPE_NAMES=MEDIATYPE_NAMES)

        # make links
        self.links = [
            Link(
                LANDING_PAGE_URL,
                rel=RelType.SELF,
                type=MediaType.JSON,
                hreflang=HrefLang.EN,
                title="This document"
            ),
            Link(
                LANDING_PAGE_URL + "/spec",
                rel=RelType.SERVICE_DESC,
                type=MediaType.OPEN_API_3,
                hreflang=HrefLang.EN,
                title="API definition"
            ),
            Link(
                LANDING_PAGE_URL + "/docs",
                rel=RelType.SERVICE_DOC,
                type=MediaType.HTML,
                hreflang=HrefLang.EN,
                title="API documentation"
            ),
            Link(
                LANDING_PAGE_URL + "/conformance",
                rel=RelType.CONFORMANCE,
                type=MediaType.JSON,
                hreflang=HrefLang.EN,
                title="API conformance classes implemented by this server"
            ),
            Link(
                LANDING_PAGE_URL + "/timelines",
                rel=RelType.DATA,
                type=MediaType.JSON,
                hreflang=HrefLang.EN,
                title="Information about the timelines"
            ),
        ]
        # Others
        if other_links is not None:
            self.links.extend(other_links)

        self.headers["Link"] = self.headers["Link"] + ", ".join(
            [link.render_as_http_header() for link in self.links])

    def render(self):
        logging.debug("render()")
        # for v in self.request.query_params.items():
        #     if v[0] not in self.ALLOWED_PARAMS:
        #         return Response("The parameter {} you supplied is not allowed".format(v[0]), status_code=400)

        # try returning alt profile
        response = super().render()
        if response is not None:
            return response
        elif self.profile == "dcat":
            if self.mediatype in Renderer.RDF_SERIALIZER_TYPES_MAP:
                q = """
                    PREFIX dcat: <http://www.w3.org/ns/dcat#>
                    PREFIX dcterms: <http://purl.org/dc/terms/>

                    CONSTRUCT {
                        ?s ?p ?o
                    }
                    WHERE {
                        GRAPH <http://system.com> {
                            ?s ?p ?o 
                        }
                    }
                    """
                return utils.render_rdf(utils.sparql_construct(q), self.mediatype)
            else:
                logging.debug("render DCAT HTML")
                q = """
                    PREFIX dcat: <http://www.w3.org/ns/dcat#>
                    PREFIX dcterms: <http://purl.org/dc/terms/>

                    SELECT * 
                    WHERE {
                        GRAPH <http://system.com> {
                            ?uri a dcat:Catalog ;
                                dcterms:title ?title ;
                                dcterms:publisher ?publisher .

                            OPTIONAL {
                                ?uri dcterms:description ?description ;
                            }
                        }
                    }
                    """
                r = utils.sparql_query(q)
                _template_context = {}
                for row in r:
                    _template_context = {
                        "uri": row["uri"]["value"],
                        "title": row["title"]["value"],
                        "description": markdown.markdown(row["description"]["value"])
                        if row.get("description") else None,
                        "request": self.request
                    }

                _template_context["links"] = self.links
                _template_context["api_title"] = "TimePrez"
                _template_context["request"] = self.request

                return templates.TemplateResponse(
                    name="landing_page_dcat.html",
                    context=_template_context,
                    headers=self.headers
                )


@router.get("/conformance")
async def conformance(request: Request):
    try:
        logging.info(f"Conformance page request: {request.path_params}")
        return ConformanceRenderer(request).render()
    except Exception as e:
        logging.info(e)
        return HTTPException(detail=e, status_code=500)


class ConformanceRenderer(Renderer):
    def __init__(self, request, other_links: List[Link] = None, ):

        import api.profiles as p
        import pyldapi as py
        self.conformance_classes = []
        for i in dir(p):
            prf = getattr(p, i)
            if type(prf) == py.profile.Profile:
                self.conformance_classes.append({"uri": prf.uri, "label": prf.label})

        super().__init__(
            request,
            LANDING_PAGE_URL + "/conformance",
            utils.get_profiles("http://example.com/ConformancePage")
        )

    def render(self):
        # for v in self.request.query_params.items():
        #     if v[0] not in self.ALLOWED_PARAMS:
        #         return Response("The parameter {} you supplied is not allowed".format(v[0]), status=400)

        # try returning alt profile
        response = super().render()
        if response is not None:
            return response
        elif self.profile == "oai":
            if self.mediatype in ["application/json",
                                  "application/vnd.oai.openapi+json;version=3.0",
                                  "application/geo+json"]:
                return self._render_oai_json()
            else:
                return self._render_oai_html()

    def _render_oai_json(self):
        page_json = {
            "conformsTo": [x.uri for x in self.conformance_classes]
        }

        return JSONResponse(
            page_json,
            media_type=str(MediaType.JSON.value),
            headers=self.headers,
        )

    def _render_oai_html(self):
        _template_context = {
            "uri": LANDING_PAGE_URL + "/conformance",
            "conformance_classes": self.conformance_classes,
            "request": self.request
        }

        return templates.TemplateResponse(name="conformance.html",
                                          context=_template_context,
                                          headers=self.headers)


@router.get("/items")
@router.get("/timelines")
async def timelines(request: Request):
    try:
        logging.info(f"Timelines page request: {request.path_params}")
        return TimelinesRenderer(request).render()
    except Exception as e:
        logging.info(e)
        return HTTPException(detail=e, status_code=500)


class TimelinesRenderer(Renderer):
    def __init__(self, request, other_links: List[Link] = None, ):
        logging.debug("TimelinesPageRenderer()")
        self.request = request
        self.members = []
        q = """
            PREFIX tl: <https://data.surroundaustralia.com/def/timeline/>
            PREFIX dcterms: <http://purl.org/dc/terms/>

            SELECT *
            WHERE {
                ?tl a tl:Timeline ;
                     dcterms:title ?title
            }
            ORDER BY ?title
            """
        for row in utils.sparql_query(q):
            self.members.append((utils.make_system_uri(row["tl"]["value"], endpoint="timeline"), row["title"]["value"]))

        super().__init__(
            request=request,
            instance_uri=self.request.base_url,
            profiles=utils.get_profiles("https://data.surroundaustralia.com/def/time-ext/Timeline"),
            default_profile_token="mem",
        )

        # make links
        self.links = [
            Link(
                self.request.base_url,
                rel=RelType.SELF,
                type=MediaType.JSON,
                hreflang=HrefLang.EN,
                title="This document"
            ),
            Link(
                LANDING_PAGE_URL,
                rel=RelType.SELF,
                type=MediaType.HTML,
                hreflang=HrefLang.EN,
                title="API Home"
            ),
        ]
        # Others
        if other_links is not None:
            self.links.extend(other_links)

        self.headers["Link"] = self.headers["Link"] + ", ".join(
            [link.render_as_http_header() for link in self.links])

    def render(self):
        logging.debug("Timelines render()")
        logging.debug(f"Timelines render(), profile: {self.profile}")
        # for v in self.request.query_params.items():
        #     if v[0] not in self.ALLOWED_PARAMS:
        #         return Response("The parameter {} you supplied is not allowed".format(v[0]), status_code=400)

        if self.profile == "mem":
            if self.mediatype in Renderer.RDF_SERIALIZER_TYPES_MAP:
                # TODO: mem RDF
                q = """

                    """
                return utils.render_rdf(utils.sparql_construct(q), self.mediatype)
            else:
                return self._render_mem_html()
        else:  # alt
            response = super().render()
            if response is not None:
                return response
            elif self.profile == "dcat":
                if self.mediatype in Renderer.RDF_SERIALIZER_TYPES_MAP:
                    # TODO: dcat RDF
                    q = """
    
                        """
                    return utils.render_rdf(utils.sparql_construct(q), self.mediatype)
                else:
                    return self._render_dcat_html()

    def _render_mem_html(self):
        logging.debug("render mem HTML")
        q = """
            PREFIX dcterms: <http://purl.org/dc/terms/>
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            PREFIX sdo: <https://schema.org/>

            SELECT *
            WHERE {
                ?uri a dcat:Resource ;
                     dcterms:identifier ?id ;
                     dcterms:title ?title .
            }
            """
        _template_context = {
            "api_title": "TimePrez",
            "uri": self.request.base_url,
            "title": "Timelines",
            "links": self.links,
            "description": markdown.markdown("The timelines within this instance of TimePrez, presented as a "
                                             "list of links."),
            "request": self.request
        }
        members = []
        for row in utils.sparql_query(q):
            logging.debug(row["title"]["value"])
            members.append({
                "uri": utils.make_system_uri(row["uri"]["value"], endpoint="timeline"),
                "id": row["id"]["value"],
                "title": row["title"]["value"],
            })
        _template_context["members"] = members

        return templates.TemplateResponse(
            name="timelines_mem.html",
            context=_template_context,
            headers=self.headers
        )

    def _render_dcat_html(self):
        logging.debug("render DCAT HTML")
        q = """
            PREFIX dcterms: <http://purl.org/dc/terms/>
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            PREFIX sdo: <https://schema.org/>

            SELECT *
            WHERE {
                ?uri a dcat:Resource ;
                     dcterms:identifier ?id ;
                     dcterms:title ?title ;
                     dcterms:description ?description ;
                     dcterms:publisher ?pub .

                ?pub sdo:name ?pub_name .
            }
            """
        _template_context = {
            "api_title": "TimePrez",
            "uri": self.request.base_url,
            "title": "Timelines",
            "links": self.links,
            "description": markdown.markdown("The timelines within this instance of TimePrez, presented as a "
                                             "[DCAT](https://www.w3.org/TR/vocab-dcat/) catalogue of items."),
            "request": self.request
        }
        members = []
        for row in utils.sparql_query(q):
            logging.debug(row["title"]["value"])
            members.append({
                "uri": utils.make_system_uri(row["uri"]["value"], endpoint="timeline"),
                "id": row["id"]["value"],
                "title": row["title"]["value"],
                "description": markdown.markdown(row["description"]["value"]),
                "publisher": (utils.make_system_uri(row["pub"]["value"], endpoint="agent"), row["pub_name"]["value"]),
            })
        _template_context["members"] = members

        return templates.TemplateResponse(
            name="timelines_dcat.html",
            context=_template_context,
            headers=self.headers
        )


@router.get("/timeline/{id}")
async def timeline(id, request: Request):
    logging.debug(f"route /timeline/{id}")
    q = """
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX tl: <https://data.surroundaustralia.com/def/timeline/>

        SELECT ?uri 
        WHERE {
            ?uri a tl:Timeline ;
                 dcterms:identifier "xxx" .
        }   
        """.replace("xxx", id)
    uri = None
    for row in utils.sparql_query(q):
        uri = row["uri"]["value"]
    if uri is None:
        return HTTPException(
            status_code=400,
            detail="The ID you requested is not the ID of any Timeline in the database"
        )
    else:
        return HTMLResponse(f"Timeline {uri}")


class Timeline:
    pass


@router.get("/agents")
async def agents(request: Request):
    try:
        logging.info(f"Agents page request: {request.path_params}")
        return AgentsRenderer(request).render()
    except Exception as e:
        logging.info(e)
        return HTTPException(detail=e, status_code=500)


class AgentsRenderer(Renderer):
    def __init__(self, request, other_links: List[Link] = None, ):
        logging.debug("AgentsPageRenderer()")
        # self.timelines = Timelines(other_links=other_links)
        self.request = request
        self.members = []
        q = """
            PREFIX dcterms: <http://purl.org/dc/terms/>
            PREFIX sdo: <https://schema.org/>
            PREFIX prov: <http://www.w3.org/ns/prov#>

            SELECT *
            WHERE {
                ?a a prov:Agent ;
                   dcterms:identifier ?id ;
                   sdo:name ?name .
            }
            ORDER BY ?name
            """
        for row in utils.sparql_query(q):
            self.members.append((utils.make_system_uri(row["a"]["value"], endpoint="agent"), row["name"]["value"]))

        super().__init__(
            request=request,
            instance_uri=self.request.base_url,
            profiles=["mem", "sdo"],
            default_profile_token="mem",
        )

        # make links
        self.links = [
            Link(
                self.request.base_url,
                rel=RelType.SELF,
                type=MediaType.JSON,
                hreflang=HrefLang.EN,
                title="This document"
            ),
            Link(
                LANDING_PAGE_URL,
                rel=RelType.SELF,
                type=MediaType.HTML,
                hreflang=HrefLang.EN,
                title="API Home"
            ),
        ]
        # Others
        if other_links is not None:
            self.links.extend(other_links)

        self.headers["Link"] = self.headers["Link"] + ", ".join(
            [link.render_as_http_header() for link in self.links])

    def render(self):
        logging.debug("Agents render()")
        for v in self.request.query_params.items():
            if v[0] not in self.ALLOWED_PARAMS:
                return Response("The parameter {} you supplied is not allowed".format(v[0]), status_code=400)

        # try returning alt or mem profile
        # TODO: add API_TITLE to context passed to super()

        if self.profile == "mem":
            if self.mediatype in Renderer.RDF_SERIALIZER_TYPES_MAP:
                # TODO: mem RDF
                q = """

                    """
                return utils.render_rdf(utils.sparql_construct(q), self.mediatype)
            else:
                return self._render_mem_html()
        else:  # alt
            response = super().render()
            if response is not None:
                return response
            elif self.profile == "dcat":
                if self.mediatype in Renderer.RDF_SERIALIZER_TYPES_MAP:
                    # TODO: dcat RDF
                    q = """

                        """
                    return utils.render_rdf(utils.sparql_construct(q), self.mediatype)
                else:
                    return self._render_dcat_html()

    def _render_mem_html(self):
        logging.debug("render mem HTML")
        q = """
            PREFIX dcterms: <http://purl.org/dc/terms/>
            PREFIX sdo: <https://schema.org/>
            PREFIX prov: <http://www.w3.org/ns/prov#>

            SELECT *
            WHERE {
                ?uri a prov:Agent ;
                   dcterms:identifier ?id ;
                   sdo:name ?name .
            }
            ORDER BY ?name
            """
        _template_context = {
            "api_title": "TimePrez",
            "uri": self.request.base_url,
            "links": self.links,
            "request": self.request
        }
        members = []
        for row in utils.sparql_query(q):
            logging.debug(row["name"]["value"])
            members.append({
                "uri": utils.make_system_uri(row["uri"]["value"], endpoint="agent"),
                "id": row["id"]["value"],
                "name": row["name"]["value"],
            })
        _template_context["members"] = members

        return templates.TemplateResponse(
            name="agents_mem.html",
            context=_template_context,
            headers=self.headers
        )


@router.get("/agent/{id}")
async def agent(id, request: Request):
    logging.debug(f"route /agent/{id}")
    q = """
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX tl: <https://data.surroundaustralia.com/def/timeline/>

        SELECT ?uri 
        WHERE {
            ?uri a prov:Agent ;
                 dcterms:identifier "xxx" .
        }   
        """.replace("xxx", id)
    uri = None
    for row in utils.sparql_query(q):
        uri = row["uri"]["value"]
    if uri is None:
        return HTTPException(
            status_code=400,
            detail="The ID you requested is not the ID of any Timeline in the database"
        )
    else:

        # return RedirectResponse(url=f"/object?uri={uri}")
        return HTMLResponse(f"Agent {uri}")


class AgentRender():
    pass


@router.get("/object")
async def object(uri, request: Request):
    logging.debug(f"route /object?uri={uri}")

    # determine the classes of the object
    q = """
        SELECT ?c
        WHERE {
            
        }
        """
    # select relevant class, based on any _profile vars

    q = """
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX tl: <https://data.surroundaustralia.com/def/timeline/>

        SELECT ?uri 
        WHERE {
            ?uri a prov:Agent ;
                 dcterms:identifier "xxx" .
        }   
        """.replace("xxx", id)
    uri = None
    for row in utils.sparql_query(q):
        uri = row["uri"]["value"]
    if uri is None:
        return HTTPException(
            status_code=400,
            detail="The ID you requested is not the ID of any Timeline in the database"
        )
    else:

        # return RedirectResponse(url=f"/object?uri={uri}")
        return HTMLResponse(f"Agent {uri}")
