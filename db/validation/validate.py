import sys
from pathlib import Path
import os

sys.path.append(str(Path(__file__).parent.parent.parent / "app"))
import utils
import config
import pyshacl
from rdflib import Graph

config.SPARQL_ENDPOINT = sys.argv[1] if len(sys.argv) > 1 else os.getenv("SPARQL_ENDPOINT")
config.SPARQL_USERNAME = sys.argv[2] if len(sys.argv) > 2 else os.getenv("SPARQL_USERNAME")
config.SPARQL_PASSWORD = sys.argv[3] if len(sys.argv) > 2 else os.getenv("SPARQL_PASSWORD")

if config.SPARQL_ENDPOINT is None:
    raise ValueError("You must set the SPARQL_ENDPOINT!")

print(f"Validating data in {config.SPARQL_ENDPOINT}")


def test_validate_graphs():
    expected_graphs = ["https://original.com", "https://inferred.com"]
    q = """
        SELECT DISTINCT ?g
        WHERE {
            GRAPH ?g {
                ?s ?p ?o 
            }
        }
        """
    r = utils.sparql_query(q)
    assert len(r) == 2, f"Two graphs must be present in the SPARQL endpoint, {', '.join(expected_graphs)}, got {len(r)}"
    for g in r:
        g_uri = g["g"]["value"]
        assert g_uri in expected_graphs, "Graph {} must be one of ".format(g_uri) + ", ".join(expected_graphs)
    print("Validated graphs")


def test_catalogue_count():
    q = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        SELECT (COUNT(?c) AS ?count)
        WHERE { ?c a dcat:Catalog }
        """
    count = int(utils.sparql_query(q)[0]["count"]["value"])
    assert count == 1, \
        f"There must be only one dcat:Catalog in the data, found {count}"
    print("Validated catalogue count")


def test_catalogue_rdf():
    # get the catalogue's RDF
    q = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        DESCRIBE ?c WHERE { ?c a dcat:Catalog }
        """
    data = utils.sparql_construct(q)

    v = pyshacl.validate(Graph().parse(data=data, format="turtle"), shacl_graph="catalogue.shapes.ttl")
    assert v[0], f"Failed catalogue.shapes calidation: {v[2]}"

    print("Validated Catalog RDF")


if __name__ == "__main__":
    # run from command line like this:
    #   python validate.py http://localhost:3030/test-catalogue admin pw123

    test_validate_graphs()
    test_catalogue_count()
    test_catalogue_rdf()
