from django.conf import settings
from django.views.generic import TemplateView
import json

from arche.arche_utils import (
    fetch_data,
    top_col_dict,
    TOP_COL_SIMPLE,
    resource_to_dict,
    filter_by_lang,
    fetch_children
)


ARCHE_API = settings.ARCHE_API


class TopColListView(TemplateView):
    template_name = "arche/top_col_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lang = self.request.GET.get('lang')
        if settings.DEBUG:
            with open("hansi.json", "r") as file:
                top_cols = json.load(file)
        else:
            params = {
                "property[0]": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                "value[0]": "https://vocabs.acdh.oeaw.ac.at/schema#TopCollection",
            }
            g = fetch_data(params=params, read_mode='resource')
            g = g.query(TOP_COL_SIMPLE)
            top_cols = top_col_dict(g, lang)
            context["top_cols"] = [value for _, value in top_cols.items()]
            with open('hansi.json', 'w') as file:
                json.dump(top_cols, file, ensure_ascii=False)
        context["top_cols"] = [value for _, value in top_cols.items()]
        return context


class TopColDetailView(TemplateView):
    template_name = "arche/top_col_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lang = self.request.GET.get('lang')
        arche_id = self.kwargs['arche_id']
        url = f"{ARCHE_API}{arche_id}/metadata"
        g = fetch_data(url=url, read_mode='0_0_1_0')
        data = resource_to_dict(g, lang=lang)
        data = filter_by_lang(dict(data[f"{arche_id}"]), lang=lang)
        children = fetch_children(arche_id, lang=lang)
        if settings.DEBUG:
            with open(f"asdf__{arche_id}.json", 'w') as file:
                json.dump(data, file, ensure_ascii=False)
        context["object"] = data
        context["lang"] = lang
        context["arche_id"] = f"{arche_id}"
        context["children"] = children
        return context
