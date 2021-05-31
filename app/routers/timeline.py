import fastapi
import logging
from fastapi import Request, HTTPException
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from utils import sparql_query

router = fastapi.APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/timeline/{id}",
            summary="Timelines",
            responses={
                200: {"description": "Timelines page correctly loaded."},
                400: {"description": "Parameter not found or not valid."},
            })
async def timeline(id):
    logging.debug(f"route /timeline/{id}")
    q = """
        PREFIX dcterms: <http://purl.org/dc/terms/>
        SELECT ?uri 
        WHERE {
          GRAPH ?g {
            ?uri dcterms:identifier "xxx" .
          }
        }    
        """.replace("xxx", id)
    uri = None
    for row in sparql_query(q):
        uri = row["uri"]["value"]
    if uri is None:
        return HTTPException(
            status_code=400,
            detail="The ID you requests is not the ID of any object in the database"
        )
    else:
        logging.debug(f"redirect to /object?uri={uri}")
        return RedirectResponse(url=f"/object?uri={uri}")
