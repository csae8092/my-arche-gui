import pandas as pd
import requests
from django.conf import settings
from rdflib import Graph
from collections import defaultdict


ARCHE_API = settings.ARCHE_API
ARCHE_SEARCH = f"{ARCHE_API}search"
ARCHE_THUMB_SERVICE = "https://arche-thumbnails.acdh.oeaw.ac.at/"


TOP_COL_SIMPLE = """
PREFIX acdh: <https://vocabs.acdh.oeaw.ac.at/schema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>


SELECT ?subject ?title ?description
WHERE {
  ?subject ?predicate acdh:TopCollection .
  ?subject acdh:hasTitle ?title .
  ?subject acdh:hasDescription ?description
}
"""


LABEL_QUERY = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX arche: <https://arche.acdh.oeaw.ac.at/api/>

SELECT  ?subject ?title
WHERE {
  arche:28107 acdh:hasTitle ?title .
}
"""


def extract_arche_id(uri):
    arche_id = uri.split('/')[-1]
    return arche_id


def fetch_label_form_arche_id(g, arche_id, lang=None):
    sparql_query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX arche: <https://arche.acdh.oeaw.ac.at/api/>
    PREFIX acdh: <https://vocabs.acdh.oeaw.ac.at/schema#>

    SELECT  ?title
    WHERE {{
    arche:{arche_id} acdh:hasTitle ?title .
    }}
    """
    qres = g.query(sparql_query)
    labels = []
    for x in qres:
        labels.append(
            {
                'label': f"{x[0]}",
                'label__lang': x[0].language,
                'arche_id': arche_id
            }
        )
    if lang:
        labels = [x for x in labels if x['label__lang'] == lang]
    return labels


def get_thumb(uri, width="350", height="200"):
    thumb_url = f"{ARCHE_THUMB_SERVICE}{uri.replace('https://', '')}?width={width}&height={height}"
    return thumb_url


def top_col_dict(graph, lang='de'):
    top_cols = {}
    if lang:
        for uri, title, description in graph:
            if title.language == lang and description.language == lang:
                arche_uri = f"{uri}"
                top_cols[arche_uri] = {
                    "uri": arche_uri,
                    "arche_id": extract_arche_id(arche_uri),
                    "arche_thumb": get_thumb(arche_uri),
                    "title": f"{title}",
                    "title_lang": f"{title.language}",
                    "description": f"{description}",
                    "description_title": f"{description.language}"
                }
    else:
        for uri, title, description in graph:
            arche_uri = f"{uri}"
            top_cols[arche_uri] = {
                "uri": arche_uri,
                "arche_id": extract_arche_id(arche_uri),
                "arche_thumb": get_thumb(arche_uri),
                "title": f"{title}",
                "title_lang": f"{title.language}",
                "description": f"{description}",
                "description_title": f"{description.language}"
            }
    return top_cols


def fetch_data(url=ARCHE_SEARCH, params={}, read_mode='neighbors'):
    headers = {
        'Accept': 'application/n-triples',
    }
    params['readMode'] = read_mode
    print(params)
    r = requests.get(
        url, params=params, headers=headers
    )
    print(url)
    g = Graph().parse(data=r.text, format="nt")
    print(len(g))
    return g


def yield_triples(g, lang=None):
    for s, p, o in g:
        p = p.split('#')[-1]
        arche_id = extract_arche_id(s)
        property__object = False
        if f"{o}".startswith(ARCHE_API):
            cur_arche_id = extract_arche_id(f"{o}")
            property__object = fetch_label_form_arche_id(g, cur_arche_id, lang=lang)

        item = {
            "uri": f"{s}",
            "arche_id": arche_id,
            "property__name": f"{p}",
            "property__value": f"{o}",
            "property__type": f"{type(o)}",
            "property__lang": getattr(o, 'language', None),
            "property__object": property__object
        }
        yield item


def resource_to_dict(g, lang=None):
    df = pd.DataFrame.from_records(yield_triples(g, lang=lang))
    all_dict = {}
    for i, gdf in df.groupby('uri'):
        records = gdf.to_dict(orient='records')
        my_dict = [{k: v for k, v in x.items() if v == v} for x in records]
        item = defaultdict(list)
        for x in my_dict:
            item[x['property__name']].append(x)
        all_dict[extract_arche_id(i)] = item
    return all_dict


def filter_by_lang(data: dict, lang: str = None):
    new_data = {}
    if not lang:
        new_data = data
    else:
        for key, value in data.items():
            new_data[key] = [x for x in value if x['property__lang'] == lang]
            if not new_data[key]:
                new_data[key] = value
    return new_data
