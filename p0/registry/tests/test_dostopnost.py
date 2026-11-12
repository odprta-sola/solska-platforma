"""Avtomatski preizkusi strukture prijave (P0-10).

Ne nadomeščajo ročnega pregleda s tipkovnico in bralnikom zaslona
(docs/projekt/pregled-dostopnosti-P0.md).
"""

from html.parser import HTMLParser

from django.core.management import call_command
from django.test import TestCase

from registry import models as m


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tags, self.ids, self.labels_for, self.text = [], set(), set(), []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append((tag, a))
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "label" and a.get("for"):
            self.labels_for.add(a["for"])

    def handle_data(self, data):
        self.text.append(data)

    def all(self, tag):
        return [a for t, a in self.tags if t == tag]

    def inputs(self):
        return [a for a in self.all("input") if a.get("type") != "hidden"]


class LoginAccessibilityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_test_data", verbosity=0)
        account = m.Account.objects.get(username="parent-01")
        account.set_password("testno-geslo-123!")
        account.save()

    def page(self, response):
        self.assertEqual(response["Content-Type"], "text/html; charset=utf-8")
        return Page(response.content.decode())

    def test_jezik_naslov_in_struktura(self):
        p = self.page(self.client.get("/accounts/login/"))
        self.assertEqual(p.all("html")[0].get("lang"), "sl")
        self.assertIn("Prijava – Odprta šola", "".join(p.text))
        self.assertEqual(len(p.all("h1")), 1)
        self.assertEqual(len(p.all("main")), 1)
        self.assertEqual(p.all("a")[0].get("href"), "#vsebina")  # preskok na vsebino
        self.assertIn("vsebina", p.ids)

    def test_vsako_polje_ima_oznako(self):
        p = self.page(self.client.get("/accounts/login/"))
        inputs = p.inputs()
        self.assertGreaterEqual(len(inputs), 2)
        for field in inputs:
            self.assertIn(field.get("id"), p.labels_for, field)

    def test_ni_povezav_na_zaprte_postopke(self):
        html = self.client.get("/accounts/login/").content.decode()
        self.assertNotIn("/accounts/signup/", html)

    def test_viden_fokus_je_dolocen(self):
        html = self.client.get("/accounts/login/").content.decode()
        self.assertIn(":focus-visible", html)
        self.assertNotIn("outline: none", html)
        self.assertNotIn("outline:0", html.replace(" ", ""))

    def test_napaka_je_povzeta_in_povezana_s_poljem(self):
        r = self.client.post("/accounts/login/", {"login": "", "password": ""})
        self.assertEqual(r.status_code, 200)
        p = self.page(r)
        alerts = [a for t, a in p.tags if a.get("role") == "alert"]
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].get("tabindex"), "-1")  # fokus se premakne na povzetek
        self.assertIn('getElementById("napake").focus()', r.content.decode())
        invalid = [a for a in p.inputs() if a.get("aria-invalid") == "true"]
        self.assertGreaterEqual(len(invalid), 1)
        for field in invalid:
            for ref in field.get("aria-describedby", "").split():
                self.assertIn(ref, p.ids, f"aria-describedby kaže na manjkajoč id {ref}")
            self.assertIn(f"{field['id']}_error", field.get("aria-describedby", ""))
        links = [a["href"][1:] for a in p.all("a") if a.get("href", "").startswith("#id_")]
        self.assertTrue(links)
        self.assertTrue(set(links) <= p.ids)

    def test_napacno_geslo_in_neznan_uporabnik_enako_sporocilo(self):
        a = self.client.post("/accounts/login/", {"login": "parent-01", "password": "napacno"})
        b = self.client.post("/accounts/login/", {"login": "nihce", "password": "napacno"})
        alert = lambda r: r.content.decode().split('role="alert"')[1].split("</div>")[0]  # noqa: E731
        self.assertEqual(alert(a), alert(b))
        self.assertNotIn("parent-01", alert(a))

    def test_uspesna_prijava_s_tipkovnico_enakovredna(self):
        r = self.client.post(
            "/accounts/login/", {"login": "parent-01", "password": "testno-geslo-123!"}
        )
        self.assertEqual(r.status_code, 302)

    def test_odjava_ima_isto_strukturo(self):
        self.client.force_login(m.Account.objects.get(username="parent-01"))
        p = self.page(self.client.get("/accounts/logout/"))
        self.assertEqual(p.all("html")[0].get("lang"), "sl")
        self.assertEqual(len(p.all("main")), 1)
        self.assertEqual(len(p.all("h1")), 1)
