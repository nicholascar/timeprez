from pyldapi.profile import Profile
from pyldapi.fastapi_framework import Renderer

openapi = Profile(
    "http://www.opengis.net/spec/ogcapi-features-1/1.0/req/oas30",
    label="OpenAPI 3.0",
    comment="The OpenAPI Specification (OAS) defines a standard, language-agnostic interface to RESTful APIs which "
            "allows both humans and computers to discover and understand the capabilities of the service without "
            "access to source code, documentation, or through network traffic inspection.",
    mediatypes=[
        "text/html", "application/geo+json", "application/json", "application/vnd.oai.openapi+json;version=3.0"],
    default_mediatype="application/geo+json",
    languages=["en"],  # default 'en' only for now
    default_language="en",
)

dcat = Profile(
    "https://www.w3.org/TR/vocab-dcat/",
    label="DCAT",
    comment="Dataset Catalogue Vocabulary (DCAT) is a W3C-authored RDF vocabulary designed to "
            "facilitate interoperability between data catalogs "
            "published on the Web.",
    mediatypes=["text/html", "application/json"] + Renderer.RDF_MEDIA_TYPES,
    default_mediatype="text/html",
    languages=["en"],  # default 'en' only for now
    default_language="en",
)

agop = Profile(
    "https://linked.data.gov.au/def/agop",
    label="Australian Government Ontology Profile",
    comment="""A profile of OWL for the purposes of Australian Government multi-ontology alignment and ontology 
presentation.

This profile contains several resources that specify the elements required of an ontology for it to be conformant with 
this profile and validation resources to test conformance.""",

    mediatypes=Renderer.RDF_MEDIA_TYPES + ["text/html"],
    default_mediatype="text/turtle",
    languages=["en"],  # default 'en' only for now
    default_language="en",
)

vocpub = Profile(
    "https://w3id.org/profile/vocpub",
    label="VocPub Profile",
    comment="This profile of SKOS defines what ConceptScheme, Concept and Collection properties and their relative "
            "arrangements Geoscience Australia requires of its vocabularies for its business purposes",
    mediatypes=Renderer.RDF_MEDIA_TYPES + ["text/html"],
    default_mediatype="text/turtle",
    languages=["en"],  # default 'en' only for now
    default_language="en",
)
