from typing import Union, List
import httpx
import config
from fastapi import Response
from rdflib import Graph, URIRef
import urllib.parse
from pyldapi.profile import Profile


def sparql_query(query: str):
    r = httpx.post(
        config.SPARQL_ENDPOINT + "/query",
        data=query,
        headers={"Content-Type": "application/sparql-query"},
        auth=(config.SPARQL_USERNAME, config.SPARQL_PASSWORD)
    )
    if 200 <= r.status_code < 300:
        result = r.json()["results"]["bindings"]
        return result
    else:
        return r.status_code, r.text


def sparql_construct(query: str):
    r = httpx.post(
        config.SPARQL_ENDPOINT + "/query",
        data=query,
        headers={"Content-Type": "application/sparql-query"},
        auth=(config.SPARQL_USERNAME, config.SPARQL_PASSWORD)
    )
    if 200 <= r.status_code < 300:
        result = r.text
        return result
    else:
        return r.status_code, r.text


def sparql_ask(query: str):
    r = httpx.post(
        config.SPARQL_ENDPOINT + "/query",
        data=query,
        headers={"Content-Type": "application/sparql-query"},
        auth=(config.SPARQL_USERNAME, config.SPARQL_PASSWORD)
    )
    if 200 <= r.status_code < 300:
        return r.json()["boolean"]
    else:
        return r.status_code, r.text


def sparql_update(query: str):
    r = httpx.post(
        config.SPARQL_ENDPOINT + "/update",
        data=query,
        headers={"Content-Type": "application/sparql-update"},
        auth=(config.SPARQL_USERNAME, config.SPARQL_PASSWORD)
    )
    if r.status_code == 401:
        print("SPARQL endpoint requires authentication")
    if 200 <= r.status_code < 300:
        return True
    else:
        return False


def render_rdf(rdf_in_turtle, format_to_render):
    if format_to_render == "text/turtle":
        return Response(rdf_in_turtle, media_type="text/turtle")
    else:
        return Response(
            Graph().parse(data=rdf_in_turtle, format="text/turtle").serialize(format=format_to_render),
            media_type="text/turtle"
        )


def make_system_uri(uri: Union[str, URIRef], endpoint="object") -> str:
    if type(uri) == URIRef:
        uri = str(uri)
    uri = urllib.parse.quote(uri)
    return f"{config.LANDING_PAGE_URL}/{endpoint}?uri={uri}"


def get_profiles(class_or_stmt: Union[str, URIRef]) -> List[Profile]:
    q = """
        PREFIX altr: <http://www.w3.org/ns/dx/conneg/altr#>
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT *
        WHERE {
            dcat:Catalog altr:hasDefaultRepresentation ?dr .
          
            {
                dcat:Catalog altr:hasRepresentation ?r .
        
                ?r dcterms:conformsTo ?p ;
                   dcterms:format ?mt .
            }
            UNION
            {
                rdf:Resource altr:hasRepresentation ?r .
        
                ?r dcterms:conformsTo ?p ;
                   dcterms:format ?mt .
            }
          
            ?p dcterms:identifier ?pid ;
               rdfs:label ?plabel ;
               rdfs:comment ?pcomment .
          
            ?mt rdfs:label ?mtlabel ;
        }    
        """
    profiles = []
    profile = None
    profile_uri = None
    default_mediatype = None
    for row in sparql_query(q):
        if profile_uri != row["p"]["value"]:
            if profile_uri is not None:
                profiles.append(profile)

            profile_uri = row["p"]["value"]
            profile = Profile(
                uri=row["p"]["value"],
                # id=row["pid"]["value"],  # TODO: why can't I use this inst var?
                label=row["plabel"]["value"],
                comment=row["pcomment"]["value"],
                mediatypes=[],
                default_mediatype=None
            )
        if row["r"]["value"] == row["dr"]["value"]:
            default_mediatype = (row["mt"]["value"], row["mtlabel"]["value"])

        if profile is not None:
            profile.id = row["pid"]["value"]
            profile.default_mediatype = default_mediatype
            profile.mediatypes.append((row["mt"]["value"], row["mtlabel"]["value"]))
    profiles.append(profile)

    return profiles


def get_timeline(id_or_uri: Union[str, URIRef]):
    pass


if __name__ == "__main__":
    # q = """
    #     PREFIX dcat: <http://www.w3.org/ns/dcat#>
    #     PREFIX dcterms: <http://purl.org/dc/terms/>
    #
    #     INSERT {
    #       GRAPH <http://inferred.com> {
    #             ?r dcterms:isPartOf ?c .
    #             ?c dcterms:hasPart ?r .
    #         }
    #     }
    #     WHERE {
    #         GRAPH ?g {
    #           ?r a dcat:Resource .
    #
    #           ?c a dcat:Catalog .
    #         }
    #     }
    #     """
    # print(sparql_update(q))
    print([x.uri for x in get_profiles("blah")])
