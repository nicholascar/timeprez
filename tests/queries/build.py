from pathlib import Path
import httpx
import os

files = [
    "00_create_default_graph.sparql",
    "01_catprez_build.sparql",
    "02_items_build.sparql",
    "03_distributions_build.sparql",
    "04_distributions_build.sparql",
    "05_distributions_build.sparql",
    "06_conformance_cp.sparql",
]

for f in files:
    print("running query {}".format(f))
    r = httpx.post(
        os.environ["SPARQL_ENDPOINT"] + "/update",
        data=open(Path(__file__).parent / f, "r").read(),
        headers={"Content-Type": "application/sparql-update"},
        auth=(os.environ["SPARQL_USERNAME"], os.environ["SPARQL_PASSWORD"])
    )
    if 200 <= r.status_code < 300:
        print("ok")
    else:
        print(r.status_code)
        print(r.text)
