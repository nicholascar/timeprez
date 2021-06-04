from typing import Optional

import fastapi
import logging
from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates

from api.landing_page import LandingPageRenderer

router = fastapi.APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/",
            summary="Landing Page",
            responses={
                200: {"description": "Landing page correctly loaded."},
                400: {"description": "Parameter not found or not valid."},
            })
async def home(request: Request,
               _profile: Optional[str] = None,
               _mediatype: Optional[str] = None,
               version: Optional[str] = None):
    try:
        logging.info(f"Landing page request: {request.path_params}")
        return LandingPageRenderer(request).render()
    except Exception as e:
        logging.info(e)
        return HTTPException(detail=e, status_code=500)
