"""Vsi klici M1 v P0 in M2 na enem mestu (pogodba 1.0.0). Ekipa M1 jih dopolni po potrebi.

Uporabniški klici dobijo `UserSession.from_request(request)`, servisni uporabijo žeton M1
(`M1_SERVICE_TOKEN`, dovoljenja: p0.authorizations.check, p0.contacts.resolve,
m2.reminders.check). Napake: `Unavailable` (zavrni ali zadrži) in `ApiError` (koda iz pogodbe).
"""

from django.conf import settings

from core.api_client import Api, ApiError, Unavailable, UserSession

__all__ = ["ApiError", "Unavailable", "UserSession", "Client"]


class Client:
    def __init__(self, api=None, token=None):
        self.api = api or Api()
        self.token = token if token is not None else settings.M1_SERVICE_TOKEN

    # Uporabniški klici (seja prijavljenega uporabnika)
    def me(self, session):
        return self.api.call("GET", "/p0/api/v1/me", session=session)

    def my_relationships(self, session):
        return self.api.call("GET", "/p0/api/v1/me/relationships", session=session)

    def my_classes(self, session):
        return self.api.call("GET", "/p0/api/v1/me/classes", session=session)

    def resolve_audience(self, session, class_id, purpose="notice"):
        body = {"class_id": class_id, "purpose": purpose}
        return self.api.call("POST", "/p0/api/v1/audiences/resolve", body, session=session)

    def check_own_authorization(self, session, scope_ref, permission="m1.confirm"):
        body = {"scope_ref": scope_ref, "permission": permission}
        return self.api.call("POST", "/p0/api/v1/authorizations/check", body, session=session)

    # Servisni klici (žeton M1)
    def check_authorization(self, subject_id, scope_ref, permission="m1.confirm"):
        body = {"subject_id": subject_id, "scope_ref": scope_ref, "permission": permission}
        return self.api.call("POST", "/p0/api/v1/authorizations/check", body, token=self.token)

    def delivery_contact(self, audience_ref, recipient_id, scope_ref):
        """Kontakt tik pred pošiljanjem; ne shranjujte ga trajno."""
        body = {"audience_ref": audience_ref, "recipient_id": recipient_id, "scope_ref": scope_ref}
        return self.api.call("POST", "/p0/api/v1/delivery-contacts/resolve", body, token=self.token)

    def reminder_needed(self, need_ref, recipient_id, scope_ref):
        """Potreba v M2; napaka ali 404 ni »nepotreben« (zadrži dostavo)."""
        body = {"need_ref": need_ref, "recipient_id": recipient_id, "scope_ref": scope_ref}
        return self.api.call("POST", "/m2/api/v1/reminders/check", body, token=self.token)
