from typing import Optional

import fastapi
import logging
from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates

from api.obj import ObjectRenderer

router = fastapi.APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/agent",
            summary="Agent Endpoint",
            responses={
                200: {"description": "Object page correctly loaded."},
                400: {"description": "Parameter not found or not valid."},
            })
async def agent(request: Request,
                _profile: Optional[str] = None,
                _mediatype: Optional[str] = None):
    try:
        logging.info(f"Agent Endpoint request: {request.path_params}")
        # render_content = ObjectRend erer(request).render()
        return "Nothing yet"
    except Exception as e:
        return HTTPException(detail=e, status_code=500)
