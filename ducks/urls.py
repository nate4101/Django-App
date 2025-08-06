from django.urls import path

from . import views

app_name = "ducks"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="duck_by_id"),
    path("name/<slug:name>/", views.duck_by_name, name="duck_by_name"),
    path("<int:duck_id>/rate/", views.rate, name="rate"),
    path("<int:duck_id>/facts/add/", views.add_fact, name="add_fact"),
    path("<int:duck_id>/delete", views.delete_duck_by_id, name="delete_duck_by_id"),
    path(
        "fact/<int:fact_id>/delete/", views.delete_fact_by_id, name="delete_fact_by_id"
    ),
]
