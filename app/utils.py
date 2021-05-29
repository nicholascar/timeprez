import logging
from pathlib import Path
import httpx
import os
import config
from fastapi import Response
from rdflib import Graph


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


if __name__ == "__main__":
    # uri = "http://example.com/demo"
    # print(sparql_query("SELECT ?p WHERE {<xxx> <http://purl.org/dc/terms/conformsTo> ?p }".replace("xxx", uri)))
    config.SPARQL_ENDPOINT = "http://fuseki.surroundaustralia.com/catprez-testing"
    config.SPARQL_USERNAME = "admin"
    config.SPARQL_PASSWORD = "Fu53kiD8ta"
    q = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        
        INSERT {
          GRAPH <http://inferred.com> {
                ?r dcterms:isPartOf ?c .
                ?c dcterms:hasPart ?r .
            }
        }
        WHERE { 
            GRAPH ?g {
              ?r a dcat:Resource .
              
              ?c a dcat:Catalog .
            }
        }
        """
    print(sparql_update(q))
