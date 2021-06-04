from typing import List
from api.link import *
import logging
from config import LANDING_PAGE_URL


class Timelines:
    def __init__(
            self,
            other_links: List[Link] = None,
    ):
        logging.debug("Timelines()")
        self.uri = LANDING_PAGE_URL + "/timelines"
