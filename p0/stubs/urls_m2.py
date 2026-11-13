from django.urls import path

from . import m2

urlpatterns = [
    path("reminders/check", m2.reminder_check),
    path("_stub/needs", m2.stub_issue_need),
    path("_stub/mark-done", m2.stub_mark_done),
]
