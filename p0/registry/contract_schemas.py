"""Sheme zahtev iz osnutka pogodbe D12 (api/openapi.yaml) in preverjanje vhoda.

Sheme so tu prepisane razrešene (brez $ref), ker slika P0 ne vsebuje mape api/.
Pogodbeni test preveri, da so enake shemam v api/openapi.yaml. Preverjevalnik podpira
samo podmnožico JSON Schema, ki jo pogodba uporablja za zahteve.
"""

import re
from datetime import datetime

ID = {"type": "string", "minLength": 1, "maxLength": 256}

REQUESTS = {
    "AuthCheckRequest": {
        "type": "object",
        "required": ["scope_ref", "permission"],
        "additionalProperties": False,
        "properties": {
            "subject_id": ID,
            "scope_ref": ID,
            "permission": {"type": "string", "minLength": 1, "maxLength": 64},
        },
    },
    "AudienceRequest": {
        "type": "object",
        "required": ["author_id", "class_id", "purpose"],
        "additionalProperties": False,
        "properties": {
            "author_id": ID,
            "class_id": ID,
            "purpose": {"type": "string", "enum": ["notice", "form"]},
        },
    },
    "ContactRequest": {
        "type": "object",
        "required": ["recipient_id", "scope_ref", "delivery_request_id"],
        "additionalProperties": False,
        "properties": {"recipient_id": ID, "scope_ref": ID, "delivery_request_id": ID},
    },
    "DeliveryRequest": {
        "type": "object",
        "required": [
            "idempotency_key",
            "kind",
            "recipients",
            "template_id",
            "locale",
            "params",
            "target",
            "expires_at",
        ],
        "additionalProperties": False,
        "properties": {
            "idempotency_key": ID,
            "kind": {
                "type": "string",
                "enum": ["notification", "reminder", "receipt", "change_notice"],
            },
            "recipients": {
                "type": "array",
                "minItems": 1,
                "maxItems": 200,
                "items": {
                    "type": "object",
                    "required": ["person_id", "scope_ref"],
                    "additionalProperties": False,
                    "properties": {"person_id": ID, "scope_ref": ID},
                },
            },
            "template_id": ID,
            "locale": {"type": "string", "minLength": 2, "maxLength": 16},
            "params": {"type": "object", "maxProperties": 50},
            "target": {
                "type": "object",
                "required": ["module", "resource_id"],
                "additionalProperties": False,
                "properties": {
                    "module": {"type": "string", "enum": ["M1", "M2"]},
                    "resource_id": ID,
                },
            },
            "need_ref": ID,
            "expires_at": {"type": "string", "format": "date-time", "maxLength": 64},
        },
    },
    "CancelRequest": {
        "type": "object",
        "required": ["recipient_ids"],
        "additionalProperties": False,
        "properties": {
            "recipient_ids": {"type": "array", "minItems": 1, "maxItems": 200, "items": ID}
        },
    },
    "ReminderCheckRequest": {
        "type": "object",
        "required": ["need_ref", "recipient_id", "scope_ref"],
        "additionalProperties": False,
        "properties": {"need_ref": ID, "recipient_id": ID, "scope_ref": ID},
    },
}

TYPES = {"object": dict, "array": list, "string": str, "boolean": bool}

# RFC 3339 date-time (format OpenAPI); ločilo T ter časovni pas Z ali odmik sta obvezna.
DATE_TIME = re.compile(r"\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(\.\d+)?([Zz]|[+-]\d{2}:\d{2})")


def parse_date_time(value):
    """Datum in čas po RFC 3339 ali None (tudi neobstoječ datum ali čas)."""
    if not isinstance(value, str) or not DATE_TIME.fullmatch(value):
        return None
    try:
        return datetime.fromisoformat(value.upper().replace("Z", "+00:00"))
    except ValueError:
        return None


def _valid(value, schema):
    kind = schema.get("type")
    if kind and not isinstance(value, TYPES[kind]):
        return False
    if "enum" in schema and value not in schema["enum"]:
        return False
    if kind == "string":
        if schema.get("format") == "date-time" and parse_date_time(value) is None:
            return False
        return schema.get("minLength", 0) <= len(value) <= schema.get("maxLength", 10**9)
    if kind == "array":
        if not schema.get("minItems", 0) <= len(value) <= schema.get("maxItems", 10**9):
            return False
        return all(_valid(v, schema["items"]) for v in value) if "items" in schema else True
    if kind == "object":
        if len(value) > schema.get("maxProperties", 10**9):
            return False
        props = schema.get("properties", {})
        if any(k not in value for k in schema.get("required", [])):
            return False
        if schema.get("additionalProperties") is False and any(k not in props for k in value):
            return False
        return all(_valid(v, props[k]) for k, v in value.items() if k in props)
    return True


def valid_request(name, body):
    """Ali telo ustreza shemi zahteve `name`, vključno s formatom date-time (RFC 3339)."""
    return isinstance(body, dict) and _valid(body, REQUESTS[name])
