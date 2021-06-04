import config
import utils
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn
import uuid
import logging
from config import *
from pyldapi.fastapi_framework import renderer, renderer_container
# from utils import utils

from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from routers import landing_page, timelines, timeline, obj, conformance
from monitoring import logging_config
from middlewares.correlation_id_middleware import CorrelationIdMiddleware
from middlewares.logging_middleware import LoggingMiddleware


logging_config.configure_logging(
    level="DEBUG" if config.DEBUG else "ERROR",
    service='timeprez-api',
    instance=str(uuid.uuid4())
)

api = FastAPI(docs_url='/docs',
              version='1.0',
              title='OGC LD API',
              description=f"Open API Documentation for this API")
api.add_middleware(LoggingMiddleware)
api.add_middleware(CorrelationIdMiddleware)
api.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["x-apigateway-header", "Content-Type", "X-Amz-Date"])


@api.get("/spec", summary="API Description Page")
def spec():
    openapi_json = api.openapi()
    return JSONResponse(openapi_json)


def configure_routing():
    logging.debug("configure_routing()")
    renderer.MEDIATYPE_NAMES = MEDIATYPE_NAMES
    renderer_container.MEDIATYPE_NAMES = MEDIATYPE_NAMES

    api.mount('/static', StaticFiles(directory='static'), name='static')
    api.include_router(landing_page.router)
    api.include_router(timelines.router)
    api.include_router(timeline.router)
    api.include_router(obj.router)
    api.include_router(conformance.router)


class CatPrezError(Exception):
    pass


def clear_inferred_data():
    logging.debug("clear_inferred_data()")
    # Clear inferred graph
    q = """DROP GRAPH <https://inferred.com>"""
    r = utils.sparql_update(q)
    if not r:
        raise CatPrezError("Clear inferred graph failed")


def check_data():
    logging.debug("check_data()")
    # check for a Catalog
    q = """        
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX time: <http://www.w3.org/2006/time#>
        
        ASK 
        WHERE {
            GRAPH ?g {
                ?c a time:TRS , void:Dataset ;
                    dcterms:title ?title ;
                    dcterms:publisher ?publisher .
            }
        }
        """
    if not utils.sparql_ask(q):
        raise CatPrezError(
            "At least one Temporal Reference System instance with a title and a publisher is not found "
            "at the data source (SPARQL endpoint)")

    # check for at least one Resource
    q = """
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX time: <http://www.w3.org/2006/time#>

        ASK 
        WHERE {
          ?c a time:ProperInterval ;
             skos:prefLabel ?title .
        }
        """
    if not utils.sparql_ask(q):
        raise CatPrezError("No dcat:Resource was found at the data source")


def build_data():
    logging.debug("build_data()")
    # Create Catalog / Resource links
    q = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        
        INSERT {
          GRAPH <https://inferred.com> {
                ?r dcterms:isPartOf ?c .
                ?c dcterms:hasPart ?r .
            }
        }
        WHERE { 
            GRAPH ?g {
              ?r a dcat:Resource .
              
              ?c a dcat:Catalog .
            }
        }
        """
    if not utils.sparql_update(q):
        raise CatPrezError("Create Catalog / Resource links failed")


def load_union_graph():
    logging.debug("load_union_graph()")
    q = "ADD <https://original.com> TO DEFAULT"
    if not utils.sparql_update(q):
        raise CatPrezError("Adding https://original.com to DEFAULT")
    q = "ADD <https://inferred.com> TO DEFAULT"
    if not utils.sparql_update(q):
        raise CatPrezError("Adding https://inferred.com to DEFAULT")


if __name__ == '__main__':
    logging.info("Running API...")

    clear_inferred_data()

    build_data()

    # load_union_graph()

    check_data()

    configure_routing()

    uvicorn.run(
        api,
        port=PORT,
        host=HOST,
        log_config=logging_config.configure_logging(service="Uvicorn")
    )
