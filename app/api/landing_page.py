from typing import List

from config import *
from api.link import *
from api.profiles import *
import utils

from fastapi import Response
from fastapi.templating import Jinja2Templates
from pyldapi.fastapi_framework import Renderer

import markdown
import logging

templates = Jinja2Templates(directory="templates")


class LandingPage:
    def __init__(
            self,
            other_links: List[Link] = None,
    ):
        logging.debug("LandingPage()")
        self.uri = LANDING_PAGE_URL

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


class LandingPageRenderer(Renderer):
    def __init__(
            self,
            request,
            other_links: List[Link] = None,
    ):
        logging.debug("LandingPageRenderer()")
        self.landing_page = LandingPage(other_links=other_links)

        super().__init__(request,
                         self.landing_page.uri,
                         {"dcat": dcat},
                         "dcat",
                         MEDIATYPE_NAMES=MEDIATYPE_NAMES)

        # add OGC API Link headers to pyLDAPI Link headers
        self.headers["Link"] = self.headers["Link"] + ", ".join(
            [link.render_as_http_header() for link in self.landing_page.links])

        self.ALLOWED_PARAMS = ["_profile", "_mediatype", "version"]

    def render(self):
        logging.debug("render()")
        logging.debug(f"request.profile: {self.profile}")
        logging.debug(f"request.mediatype: {self.mediatype}")
        for v in self.request.query_params.items():
            if v[0] not in self.ALLOWED_PARAMS:
                return Response("The parameter {} you supplied is not allowed".format(v[0]), status_code=400)

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
                    logging.debug(f"{r}")
                    _template_context = {
                        "uri": row["uri"]["value"],
                        "title": row["title"]["value"],
                        "description": markdown.markdown(row["description"]["value"])
                                       if row.get("description") else None,
                        "request": self.request
                    }

                _template_context["links"] = LandingPage().links
                _template_context["api_title"] = "TimePrez"

                return templates.TemplateResponse(
                    name="landing_page_dcat.html",
                    context=_template_context,
                    headers=self.headers
                )
