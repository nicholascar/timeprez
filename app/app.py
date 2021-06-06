import config
import routes
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
from routes import router
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


# TODO: move this to routes.py
@api.get("/spec", summary="API Description Page")
def spec():
    return JSONResponse(api.openapi())


def configure_routing():
    logging.debug("configure_routing()")
    api.mount('/static', StaticFiles(directory='static'), name='static')
    api.include_router(routes.router)


class TimePrezError(Exception):
    pass


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
        raise TimePrezError(
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
        raise TimePrezError("No dcat:Resource was found at the data source")


if __name__ == '__main__':
    logging.info("Running API...")

    check_data()

    configure_routing()

    uvicorn.run(
        api,
        port=PORT,
        host=HOST,
        log_config=logging_config.configure_logging(service="Uvicorn")
    )
