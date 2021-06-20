import sys
import os
from calls import *
import config

config.SPARQL_ENDPOINT = sys.argv[1] if len(sys.argv) > 1 else os.getenv("SPARQL_ENDPOINT")
config.SPARQL_USERNAME = sys.argv[2] if len(sys.argv) > 1 else os.getenv("SPARQL_USERNAME")
config.SPARQL_PASSWORD = sys.argv[3] if len(sys.argv) > 1 else os.getenv("SPARQL_PASSWORD")

cases = [
    {
        "id": 1,
        "message": "Unknown IRI",
        "iri": "http://resource.geosciml.org/vocabulary/timescale/isc2005x",
        "profile": None,
        "mediatype": None,
        "expected_response": {
            "status_code": 404,
            "message": "",
            "profile": None,
            "mediatype": None,
        }
    },
    {
        "id": 2,
        "message": "Known IRI, no profile or mediatype",
        "iri": "http://resource.geosciml.org/vocabulary/timescale/isc2005",
        "profile": None,
        "mediatype": None,
        "expected_response": {
            "status_code": 200,
            "message": "",
            "profile": "https://www.w3.org/TR/vocab-dcat/",
            "mediatype": "https://w3id.org/mediatype/text/html"
        }
    },
    {
        "id": 3,
        "message": "Known IRI, profile_iri, no mediatype",
        "iri": "http://resource.geosciml.org/vocabulary/timescale/isc2005",
        "profile": "https://www.w3.org/TR/vocab-dcat/",
        "mediatype": None,
        "expected_response": {
            "status_code": 200,
            "message": "",
            "profile": "https://www.w3.org/TR/vocab-dcat/",
            "mediatype": "https://w3id.org/mediatype/text/html"
        }
    },
    {
        "id": 4,
        "message": "Known IRI, profile_iri & mediatype",
        "iri": "http://resource.geosciml.org/vocabulary/timescale/isc2005",
        "profile": "https://www.w3.org/TR/vocab-dcat/",
        "mediatype": "text/html",
        "expected_response": {
            "status_code": 200,
            "message": "",
            "profile": "https://www.w3.org/TR/vocab-dcat/",
            "mediatype": "https://w3id.org/mediatype/text/html"
        }
    },
    {
        "id": 5,
        "message": "Known IRI, bad profile_iri",
        "iri": "http://resource.geosciml.org/vocabulary/timescale/isc2005",
        "profile": "https://www.w3.org/TR/vocab-dcat/x",
        "mediatype": "text/html",
        "expected_response": {
            "status_code": 200,
            "message": "",
            "profile": "https://www.w3.org/TR/vocab-dcat/",
            "mediatype": "https://w3id.org/mediatype/text/html"
        }
    },
    {
        "id": 6,
        "message": "Known IRI, bad mediatype",
        "iri": "http://resource.geosciml.org/vocabulary/timescale/isc2005",
        "profile": None,
        "mediatype": "text/htmlx",
        "expected_response": {
            "status_code": 200,
            "message": "",
            "profile": "https://www.w3.org/TR/vocab-dcat/",
            "mediatype": "https://w3id.org/mediatype/text/html"
        }
    },
    {
        "id": 7,
        "message": "Known IRI, other profile",
        "iri": "http://resource.geosciml.org/vocabulary/timescale/isc2005",
        "profile": "https://schema.org",
        "mediatype": "text/htmlx",
        "expected_response": {
            "status_code": 200,
            "message": "",
            "profile": "https://schema.org",
            "mediatype": "https://w3id.org/mediatype/text/html"
        }
    },
    {
        "id": 8,
        "message": "Known IRI, other mediatype",
        "iri": "http://resource.geosciml.org/vocabulary/timescale/isc2005",
        "profile": "https://schema.org",
        "mediatype": "application/json",
        "expected_response": {
            "status_code": 200,
            "message": "",
            "profile": "http://www.w3.org/ns/dx/conneg/altr",
            "mediatype": "https://w3id.org/mediatype/text/html"
        }
    },
]

if __name__ == "__main__":
    for case in cases:
        print(f"Case {case['id']}")
        expected = case["expected_response"]
        print("expected")
        print(expected)
        print("actual")
        actual = get_object_profile_and_mediatype(case["iri"], profile_iri=case["profile"], mediatype=case["mediatype"])
        print(actual)

        assert expected["status_code"] == actual[0]
        if actual[0] == 200:
            assert expected["profile"] == actual[1][0]
            assert expected["mediatype"] == actual[1][1]
