from django.urls import path

from . import api

urlpatterns = [
    path("me", api.me, name="me"),
    path("me/relationships", api.my_relationships, name="me-relationships"),
    path("me/classes", api.my_classes, name="me-classes"),
    path("audiences/resolve", api.audiences_resolve, name="audiences-resolve"),
    path("authorizations/check", api.authorization_check, name="authorizations-check"),
    path(
        "delivery-contacts/resolve", api.delivery_contact_resolve, name="delivery-contacts-resolve"
    ),
]
