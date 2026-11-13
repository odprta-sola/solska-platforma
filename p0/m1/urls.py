"""Zasloni M1 eSporočanje pod /m1/ (seja P0 v isti namestitvi)."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="m1-home"),
]
