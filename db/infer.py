import sys
from pathlib import Path
import httpx
import os

SPARQL_ENDPOINT = sys.argv[1] if len(sys.argv) > 1 else os.getenv("SPARQL_ENDPOINT")
SPARQL_USERNAME = sys.argv[2] if len(sys.argv) > 1 else os.getenv("SPARQL_USERNAME")
SPARQL_PASSWORD = sys.argv[3] if len(sys.argv) > 1 else os.getenv("SPARQL_PASSWORD")

files = [
    "sdo_catalog.sparql",
    "sdo_resources.sparql",
    "sdo_agents.sparql",
    "catprez_distributions.sparql",
    "catalog_resource_parts.sparql",
    "distributions_dataservice.sparql",
    "distributions_ranges.sparql",
    "distributions_titles.sparql",
    "alt_conformance.sparql",
    "profile_defaults_dcat.sparql",
    "profile_defaults_agents.sparql",
]

for f in files:
    print("running query {}".format(f))
    r = httpx.post(
        SPARQL_ENDPOINT + "/update",
        data=open(Path(__file__).parent / "inference" / f, "r").read(),
        headers={"Content-Type": "application/sparql-update"},
        auth=(SPARQL_USERNAME, SPARQL_PASSWORD)
    )
    if 200 <= r.status_code < 300:
        print("ok")
    else:
        print(r.status_code)
        print(r.text)

# run from command line like this:
#   python infer.py http://localhost:3030/test-catalogue admin pw123
