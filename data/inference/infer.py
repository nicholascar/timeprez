import sys
from pathlib import Path
import httpx
import os

SPARQL_ENDPOINT = sys.argv[1] if len(sys.argv) > 1 else os.getenv("SPARQL_ENDPOINT")
SPARQL_USERNAME = sys.argv[2] if len(sys.argv) > 1 else os.getenv("SPARQL_USERNAME")
SPARQL_PASSWORD = sys.argv[3] if len(sys.argv) > 1 else os.getenv("SPARQL_PASSWORD")

files = [
    "01_catprez_build.sparql",
    "02_items_build.sparql",
    "03_distributions_build.sparql",
    "04_distributions_build.sparql",
    "05_distributions_build.sparql",
    "06_conformance_cp.sparql",
    "07_agents.sparql",
    "10_add_items.sparql",
    "11_add_system.sparql",
    "12_add_inferred.sparql",
]

for f in files:
    print("running query {}".format(f))
    r = httpx.post(
        SPARQL_ENDPOINT + "/update",
        data=open(Path(__file__).parent / f, "r").read(),
        headers={"Content-Type": "application/sparql-update"},
        auth=(SPARQL_USERNAME, SPARQL_PASSWORD)
    )
    if 200 <= r.status_code < 300:
        print("ok")
    else:
        print(r.status_code)
        print(r.text)
