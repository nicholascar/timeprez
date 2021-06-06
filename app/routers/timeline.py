import fastapi
import logging
from fastapi import Request, HTTPException
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from utils import sparql_query

router = fastapi.APIRouter()
templates = Jinja2Templates(directory="templates")


