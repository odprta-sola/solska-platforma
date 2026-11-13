"""Vsi klici M2 v P0 in M1 na enem mestu (pogodba 1.0.0). Ekipa M2 jih dopolni po potrebi.

Uporabniški klici dobijo `UserSession.from_request(request)`, servisni uporabijo žeton M2
(`M2_SERVICE_TOKEN`, dovoljenja: m1.delivery, p0.authorizations.check). M2 kontaktov ne vidi.
Napake: `Unavailable` (zavrni; odločitev in namera za obveščanje ostaneta shranjeni) in
`ApiError` (koda iz pogodbe).
"""

from django.conf import settings

from core.api_client import Api, ApiError, Unavailable, UserSession

__all__ = ["ApiError", "Unavailable", "UserSession", "Client"]


class Client:
    def __init__(self, api=None, token=None):
        self.api = api or Api()
        self.token = token if token is not None else settings.M2_SERVICE_TOKEN

    # Uporabniški klici (seja prijavljenega uporabnika)
    def me(self, session):
        return self.api.call("GET", "/p0/api/v1/me", session=session)

    def my_relationships(self, session):
        return self.api.call("GET", "/p0/api/v1/me/relationships", session=session)

    def my_classes(self, session):
        return self.api.call("GET", "/p0/api/v1/me/classes", session=session)

    def resolve_audience(self, session, class_id, purpose="form"):
        body = {"class_id": class_id, "purpose": purpose}
        return self.api.call("POST", "/p0/api/v1/audiences/resolve", body, session=session)

    def check_own_authorization(self, session, scope_ref, permission="m2.decide"):
        body = {"scope_ref": scope_ref, "permission": permission}
        return self.api.call("POST", "/p0/api/v1/authorizations/check", body, session=session)

    # Servisni klici (žeton M2)
    def check_authorization(self, subject_id, scope_ref, permission="m2.decide"):
        body = {"subject_id": subject_id, "scope_ref": scope_ref, "permission": permission}
        return self.api.call("POST", "/p0/api/v1/authorizations/check", body, token=self.token)

    def create_delivery(self, request_body):
        """Zahteva za dostavo v M1 (DeliveryRequest); 202 pomeni trajno prevzeto."""
        return self.api.call("POST", "/m1/api/v1/delivery-requests", request_body, token=self.token)

    def delivery_status(self, delivery_request_id):
        path = f"/m1/api/v1/delivery-requests/{delivery_request_id}"
        return self.api.call("GET", path, token=self.token)

    def cancel_delivery(self, delivery_request_id, item_ids):
        path = f"/m1/api/v1/delivery-requests/{delivery_request_id}/cancel"
        return self.api.call("POST", path, {"item_ids": item_ids}, token=self.token)
