import sys
from pathlib import Path
import httpx
import os

SPARQL_ENDPOINT = sys.argv[1] if len(sys.argv) > 1 else os.getenv("SPARQL_ENDPOINT")
SPARQL_USERNAME = sys.argv[1] if len(sys.argv) > 1 else os.getenv("SPARQL_USERNAME")
SPARQL_PASSWORD = sys.argv[1] if len(sys.argv) > 1 else os.getenv("SPARQL_PASSWORD")

if SPARQL_ENDPOINT is None:
    raise ValueError("You must set the SPARQL_ENDPOINT!")

print(f"Loading data into {SPARQL_ENDPOINT}")

# load all turtle files in ./items/* & ./system/*
for f in Path(__file__).parent.glob("*/*.ttl"):
    print("loading {}".format(f))
    r = httpx.post(
        SPARQL_ENDPOINT,
        params={"graph": "https://original.com"},
        headers={"Content-Type": "text/turtle"},
        content=open(Path(__file__).parent / f, "rb").read(),
        auth=(SPARQL_USERNAME, SPARQL_PASSWORD)
    )
    if 200 <= r.status_code < 300:
        print("ok")
    else:
        print(r.status_code)
        print(r.text)

# run from command line like this:
#   python load.py http://localhost:3030/test-catalogue admin pw123
