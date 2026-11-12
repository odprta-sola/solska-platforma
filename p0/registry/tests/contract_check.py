"""Skupno preverjanje odgovorov proti operaciji v osnutku pogodbe (api/openapi.yaml).

Preveri status (naveden pri operaciji ali splošen po opisu pogodbe), vsebinski tip, shemo s
formati in vedenjska pravila, ki jih JSON Schema ne izrazi (npr. counts in postavke).
"""

import json
import re
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

SPEC = yaml.safe_load((Path(__file__).resolve().parents[3] / "api" / "openapi.yaml").read_text())
GENERIC = {"405", "503"}  # splošni napaki po opisu pogodbe; 500 ni nikoli sprejemljiv
FORMATS = Draft202012Validator.FORMAT_CHECKER


class ContractViolation(AssertionError):
    pass


def validate(schema, data):
    root = {"$ref": f"#/components/schemas/{schema}", "components": SPEC["components"]}
    Draft202012Validator(root, format_checker=FORMATS).validate(data)


def operation(method, path):
    """(predloga poti, operacija) ali None, če pot ni v pogodbi."""
    path = path.split("?", 1)[0]
    for template, ops in SPEC["paths"].items():
        if re.fullmatch(re.sub(r"\{[^}]+\}", "[^/]+", template), path):
            return template, ops.get(method.lower())
    return None


def _response_schema(op, status):
    resp = op["responses"].get(status) or SPEC["components"]["responses"]["Error"]
    if "$ref" in resp:
        resp = SPEC["components"]["responses"][resp["$ref"].rsplit("/", 1)[1]]
    return resp["content"]["application/json"]["schema"]["$ref"].rsplit("/", 1)[1]


def check_response(method, path, status, content_type, body):
    """Dvigne ContractViolation, če odgovor ne ustreza pogodbi."""
    found = operation(method, path)
    if found is None:
        return
    template, op = found
    where = f"{method.upper()} {template} {status}"
    if op is None:
        if status != 405:
            raise ContractViolation(f"{where}: metoda ni v pogodbi, pričakovan 405")
        op = {"responses": {}}
    code = str(status)
    if code not in op["responses"] and code not in GENERIC:
        raise ContractViolation(f"{where}: status ni v pogodbi")
    if not content_type.startswith("application/json"):
        raise ContractViolation(f"{where}: vsebinski tip {content_type}")
    try:
        data = json.loads(body)
        schema = _response_schema(op, code)
        validate(schema, data)
    except (ValueError, ValidationError) as exc:
        raise ContractViolation(f"{where}: {exc}") from exc
    if schema == "DeliveryStatus":
        states = [r["state"] for r in data["recipients"]]
        expected = {s: states.count(s) for s in set(states)}
        if data["counts"] != expected:
            raise ContractViolation(f"{where}: counts se ne ujema s postavkami")


def check(method, path, response):
    check_response(
        method, path, response.status_code, response.get("Content-Type", ""), response.content
    )
    return response
