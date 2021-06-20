from typing import Union, Optional, AnyStr
from pydantic import AnyHttpUrl
from rdflib import URIRef
from utils import *
import sys
import os

SPARQL_ENDPOINT = sys.argv[1] if len(sys.argv) > 1 else os.getenv("SPARQL_ENDPOINT")
SPARQL_USERNAME = sys.argv[2] if len(sys.argv) > 1 else os.getenv("SPARQL_USERNAME")
SPARQL_PASSWORD = sys.argv[3] if len(sys.argv) > 1 else os.getenv("SPARQL_PASSWORD")


def get_object_profile_and_mediatype(iri: Union[AnyHttpUrl, URIRef], profile_iri: Optional[Union[AnyHttpUrl, URIRef]],
                                     mediatype: Optional[AnyStr]):
    # is an object with iri known?
    q = """
        PREFIX profx: <https://w3id.org/profile/profx/>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?p ?mt
        WHERE {
            BIND (<xxx> AS ?iri)
            BIND (<yyy> AS ?requested_profile)
            BIND (<zzz> AS ?requested_mediatype)
            
            OPTIONAL {
            ?iri dcterms:conformsTo ?requested_profile .
            
            ?x # Representation
                dcterms:conformsTo ?requested_profile ;
                dcterms:format ?requested_mediatype .
            BIND (?requested_mediatype AS ?received_mediatype)
            }
            
            OPTIONAL {    
            ?iri dcterms:conformsTo ?requested_profile .
            ?requested_profile profx:hasDefaultMediatype ?requested_profile_default_mediatype .
            }
            
            #  OPTIONAL {    
            #    ?iri dcterms:conformsTo ?other_profile .
            #    ?x # Representation
            #    	dcterms:conformsTo ?other_profile ;
            #    	dcterms:format ?requested_mediatype .
            #    BIND (?requested_mediatype AS ?other_mediatype)
            #  }  
            
            ?iri profx:hasDefaultProfile ?default_profile .
            ?default_profile profx:hasDefaultMediatype ?default_profile_default_mediatype .
            
            BIND (IF(BOUND(?received_mediatype), 
                   ?requested_profile, 
                   IF(BOUND(?requested_profile_default_mediatype), 
                      ?requested_profile,
                      ?default_profile
                   )
               ) 
            AS ?p)
            BIND (IF(BOUND(?received_mediatype), 
                   ?requested_mediatype, 
                   IF(BOUND(?requested_profile_default_mediatype), 
                      ?requested_profile_default_mediatype, 
                      ?default_profile_default_mediatype
                   )
                ) 
            AS ?mt)
        }    
        """ \
        .replace("xxx", iri) \
        .replace("yyy", profile_iri if profile_iri is not None else "y") \
        .replace("zzz", "https://w3id.org/mediatype/application/" + mediatype if mediatype is not None else "z")
    r = sparql_select(q)
    if 200 <= r[0] < 300:
        profile = None
        mediatype = None
        for row in r[1]:
            profile = row["p"]
            mediatype = row["mt"]
        if profile is not None and mediatype is not None:
            return 200, (profile["value"], mediatype["value"])
        else:
            return 404, "The IRI you supplied doesn't correspond to any known object in this system"
    else:
        return 500, f"The system encountered an internal error: {r[1]}"
