from django.urls import path

from . import m1

urlpatterns = [
    path("delivery-requests", m1.create_delivery),
    path("delivery-requests/<str:delivery_request_id>", m1.get_delivery),
    path("delivery-requests/<str:delivery_request_id>/cancel", m1.cancel_delivery),
    path("_stub/advance", m1.stub_advance),
    path("_stub/process", m1.stub_process),
]
