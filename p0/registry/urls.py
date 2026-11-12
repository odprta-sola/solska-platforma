from django.urls import path

from . import api

urlpatterns = [
    path("me", api.me, name="me"),
    path("me/relationships", api.my_relationships, name="me-relationships"),
    path("me/classes", api.my_classes, name="me-classes"),
    path("authorizations/check", api.authorization_check, name="authorizations-check"),
]
