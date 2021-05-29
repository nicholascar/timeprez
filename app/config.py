import os
__version__ = "0.1"


DEBUG = os.getenv("DEBUG", True)
HOST = os.getenv("HOST", '0.0.0.0')
PORT = os.getenv("PORT", 5000)

APP_DIR = os.getenv("APP_DIR", os.path.dirname(os.path.realpath(__file__)))
TEMPLATES_DIR = os.getenv("TEMPLATES_DIR", os.path.join(APP_DIR, "view", "templates"))
STATIC_DIR = os.getenv("STATIC_DIR", os.path.join(APP_DIR, "view", "style"))
VERSION = os.getenv("VERSION", __version__)
MEDIATYPE_NAMES = {
    "text/html": "HTML",
    "application/json": "JSON",
    "application/geo+json": "GeoJSON",
    "text/turtle": "Turtle",
    "application/rdf+xml": "RDX/XML",
    "application/ld+json": "JSON-LD",
    "text/n3": "Notation-3",
    "application/n-triples": "N-Triples",
}

SPARQL_ENDPOINT = os.getenv("SPARQL_ENDPOINT", "")
SPARQL_USERNAME = os.getenv("SPARQL_USERNAME", "")
SPARQL_PASSWORD = os.getenv("SPARQL_PASSWORD", "")
LANDING_PAGE_URL = os.getenv("LANDING_PAGE_URL", "http://localhost:5000")
