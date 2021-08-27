from django.urls import path

from . import views

app_name = "about"

urlpatterns = [
    path("author/", views.PageAboutAuthor.as_view(), name="author"),
    path("tech/", views.PageAboutTech.as_view(), name="tech"),
]
