"""Sled vpogledov zaposlenih v podatke osebe (varstvo podatkov, čl. 5(2); D07)."""

from unittest import mock

from django.contrib import admin
from django.test import Client, RequestFactory

from registry import models as m

from .test_zasloni import BASE, ScreenBase, csv_files


class AccessAuditTests(ScreenBase):
    def person_screens(self):
        rel = m.Relationship.objects.filter(guardian=self.p1).first()
        grant = m.Grant.objects.filter(person=self.p1).first()
        return {
            "oseba": f"{BASE}/osebe/{self.p1.pk}/",
            "kontakt": f"{BASE}/osebe/{self.p1.pk}/kontakt/",
            "odvzem:relationship": f"{BASE}/osebe/{self.p1.pk}/povezave/{rel.pk}/odvzem/",
            "odvzem:grant": f"{BASE}/osebe/{self.p1.pk}/upravicenja/{grant.pk}/odvzem/",
        }

    def rows(self):
        return list(m.AccessAudit.objects.values("actor", "screen", "entity_type", "entity_id"))

    def test_vsak_zaslon_osebe_zapise_vpogled(self):
        client = self.login()
        for screen, url in self.person_screens().items():
            with self.subTest(screen=screen):
                m.AccessAudit.objects.all().delete()
                self.assertEqual(client.get(url).status_code, 200)
                self.assertEqual(
                    self.rows(),
                    [
                        {
                            "actor": self.office.pk,
                            "screen": screen,
                            "entity_type": "person",
                            "entity_id": str(self.p1.pk),
                        }
                    ],
                )

    def test_predogled_uvoza_zapise_vpogled(self):
        client = self.login()
        url = client.post(f"{BASE}/uvoz/", {"source": "sled", "files": csv_files()})["Location"]
        batch_id = url.rstrip("/").split("/")[-1]
        m.AccessAudit.objects.all().delete()
        client.get(url)
        client.get(url, {"stran": 2})
        self.assertEqual(
            [(r["screen"], r["entity_type"], r["entity_id"]) for r in self.rows()],
            [("uvoz", "import_batch", batch_id)] * 2,
        )

    def test_brez_pravice_ali_neobstojeca_oseba_brez_zapisa(self):
        url = self.person_screens()["oseba"]
        Client().get(url)  # neprijavljen
        self.login("parent-01").get(url)  # brez vloge
        missing = f"{BASE}/osebe/00000000-0000-0000-0000-000000000000/"
        self.assertEqual(self.login().get(missing).status_code, 404)
        self.assertEqual(self.rows(), [])

    def test_seznam_oseb_ne_hrani_iskalnega_niza(self):
        self.login().get(f"{BASE}/osebe/", {"q": "Testni"})
        self.assertEqual(self.rows(), [])

    def test_brez_zapisa_ni_prikaza(self):
        client = self.login()
        with mock.patch.object(
            m.AccessAudit.objects, "create", side_effect=RuntimeError("baza ni dosegljiva")
        ):
            with self.assertRaises(RuntimeError):
                client.get(self.person_screens()["oseba"])

    def test_skrbniski_vmesnik_samo_za_branje(self):
        model_admin = admin.site._registry[m.AccessAudit]
        request = RequestFactory().get("/")
        request.user = m.Account(is_staff=True, is_superuser=True)
        self.assertFalse(model_admin.has_add_permission(request))
        self.assertFalse(model_admin.has_change_permission(request))
        self.assertFalse(model_admin.has_delete_permission(request))
