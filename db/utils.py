import httpx
import config


def sparql_select(query: str):
    r = httpx.post(
        config.SPARQL_ENDPOINT,
        data=query,
        headers={"Content-Type": "application/sparql-query"},
        auth=(config.SPARQL_USERNAME, config.SPARQL_PASSWORD)
    )
    if 200 <= r.status_code < 300:
        return r.status_code, r.json()["results"]["bindings"]
    else:
        return r.status_code, r.text


def sparql_ask(query: str):
    r = httpx.post(
        config.SPARQL_ENDPOINT,
        data=query,
        headers={"Content-Type": "application/sparql-query"},
        auth=(config.SPARQL_USERNAME, config.SPARQL_PASSWORD)
    )
    if 200 <= r.status_code < 300:
        return r.status_code, r.json()["boolean"]
    else:
        return r.status_code, r.text
