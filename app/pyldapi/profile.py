from typing import List, Tuple
from pydantic import BaseModel


class Profile(BaseModel):
    uri: str
    id: str
    label: str
    comment: str
    mediatypes: List[Tuple[str, str]]
    default_mediatype: Tuple[str, str]  # the ID of one of those in the mediatypes list of tuples
