"""Zasloni M2 eSoglasja pod /m2/ (seja P0 v isti namestitvi)."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="m2-home"),
]
