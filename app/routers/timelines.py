from typing import Optional

import fastapi
import logging
from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates

from api.timelines import TimelinesRenderer

router = fastapi.APIRouter()
templates = Jinja2Templates(directory="templates")


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
        render_content = TimelinesRenderer(request).render()
        return render_content
    except Exception as e:
        logging.info(e)
        return HTTPException(detail=e, status_code=500)
