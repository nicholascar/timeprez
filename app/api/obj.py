from typing import List

from config import *
from api.link import *
from api.profiles import *
# from utils import utils

from fastapi import Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pyldapi.fastapi_framework import Renderer

import markdown
import logging
from utils import sparql_query

templates = Jinja2Templates(directory="templates")


class ObjectRenderer(Renderer):
    def __init__(
            self,
            request,
            other_links: List[Link] = None,
    ):
        logging.debug("ObjectRenderer()")

        self.uri = request.query_params.get("uri")
        logging.debug("uri: " + self.uri)

        # work out all the profiles available for this Object
        conforms_to = []
        results = sparql_query(
            "SELECT ?p WHERE {<xxx> <http://purl.org/dc/terms/conformsTo> ?p }".replace("xxx", self.uri))
        logging.debug("results: " + str(results))
        for r in results:
            conforms_to.append(r["p"]["value"])

        from api.profiles import dcat, agop, vocpub
        known_profiles = [
            dcat.uri,
            agop.uri,
            vocpub.uri
        ]
        logging.debug("conforms_to: " + ", ".join(conforms_to))
        logging.debug("known_profiles: " + ", ".join(known_profiles))
        self.available_profiles = sorted([x for x in set(conforms_to) & set(known_profiles)])
        logging.debug("self.available_profiles " + ",".join(self.available_profiles))

        super().__init__(
            request,
            self.uri,
            {"dcat": dcat},
            "dcat",
            MEDIATYPE_NAMES=MEDIATYPE_NAMES,
        )

    def render(self):
        return self._render_dcat_html()

    def _render_dcat_html(self):
        logging.debug("ObjectRenderer._render_dcat_html()")
        _template_context = {
            "uri": self.uri,
            "label": "Dummy Object Page",
            "description": markdown.markdown("Dummy Object Page Description"),
            "request": self.request,
            "available_profiles": self.available_profiles
        }

        logging.debug("available_profiles: {}".format(self.available_profiles))

        return templates.TemplateResponse(name="test.html",
                                          context=_template_context,
                                          headers=self.headers)
