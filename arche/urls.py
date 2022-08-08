# urls.py
from django.urls import path
from arche import views


urlpatterns = [
    path('', views.TopColListView.as_view(), name="top_col_list"),
    path('collection/<int:arche_id>', views.TopColDetailView.as_view(), name="top_col_detail"),
]
