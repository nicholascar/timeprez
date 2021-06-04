from typing import List, Optional

import fastapi
import logging
from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi import Response
from api.profiles import *
from api.link import *
from api.timelines import Timelines
from pyldapi.fastapi_framework import Renderer, ContainerRenderer
from config import MEDIATYPE_NAMES, LANDING_PAGE_URL
import utils
import markdown

router = fastapi.APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/items",
            summary="Timelines",
            responses={
                200: {"description": "Timelines page correctly loaded."},
                400: {"description": "Parameter not found or not valid."},
            })
@router.get("/timelines",
            summary="Timelines",
            responses={
                200: {"description": "Timelines page correctly loaded."},
                400: {"description": "Parameter not found or not valid."},
            })
async def home(request: Request,
               _profile: Optional[str] = None,
               _mediatype: Optional[str] = None):
    try:
        logging.info(f"Timelines page request: {request.path_params}")
        return TimelinesRenderer(request).render()
    except Exception as e:
        logging.info(e)
        return HTTPException(detail=e, status_code=500)


class TimelinesRenderer(ContainerRenderer):
    def __init__(
            self,
            request,
            other_links: List[Link] = None,
    ):
        logging.debug("TimelinesPageRenderer()")
        # self.timelines = Timelines(other_links=other_links)
        self.request = request
        self.members = []
        q = """
            PREFIX tx: <https://data.surroundaustralia.com/def/time-ext/>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            
            SELECT *
            WHERE {
              GRAPH ?g {
                ?tl a tx:Timeline ;
                     dcterms:title ?title
              }
            }
            ORDER BY ?title
            """
        for row in utils.sparql_query(q):
            self.members.append((row["tl"]["value"], row["title"]["value"]))

        super().__init__(
            request,
            self.request.base_url,
            "Timelines",
            "All the timelines delivered by this instance of TimePrez",
            None,
            None,
            members=self.members,
            members_total_count=len(self.members),
            profiles={"dcat": dcat},
            default_profile_token="mem",
            register_template="timelines.html"
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

        self.ALLOWED_PARAMS = ["_profile", "_mediatype", "version"]

    def render(self):
        logging.debug("render()")
        logging.debug(f"request.profile: {self.profile}")
        logging.debug(f"request.mediatype: {self.mediatype}")
        for v in self.request.query_params.items():
            if v[0] not in self.ALLOWED_PARAMS:
                return Response("The parameter {} you supplied is not allowed".format(v[0]), status_code=400)

        # try returning alt or mem profile
        # TODO: add API_TITLE to context passed to super()
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
                return self._render_dcat_html()

    def _render_dcat_html(self):
        logging.debug("render DCAT HTML")
        q = """
            PREFIX dcterms: <http://purl.org/dc/terms/>
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            PREFIX sdo: <https://schema.org/>
            
            SELECT *
            WHERE {
                GRAPH ?g {
                    ?uri a dcat:Resource ;
                         dcterms:title ?title ;
                         dcterms:description ?description ;
                         dcterms:publisher ?pub
                }
              
                GRAPH ?g2 {
                    ?pub sdo:name ?pub_name .
                }
            }
            """
        _template_context = {
            "uri": self.request.base_url,
            "title": "Timelines",
            "description": markdown.markdown("The timelines within this instance of TimePrez, presented as a "
                                             "[DCAT](https://www.w3.org/TR/vocab-dcat/) catalogue of items."),
            "request": self.request
        }
        members = []
        for row in utils.sparql_query(q):
            logging.debug(row["title"]["value"])
            members.append({
                "uri": row["uri"]["value"],
                "title": row["title"]["value"],
                "description": markdown.markdown(row["description"]["value"]),
                "publisher": (row["pub"]["value"], row["pub_name"]["value"]),
            })
        print(members)
        _template_context["members"] = members
        _template_context["links"] = self.links
        _template_context["api_title"] = "TimePrez"

        return templates.TemplateResponse(
            name="timelines_dcat.html",
            context=_template_context,
            headers=self.headers
        )
