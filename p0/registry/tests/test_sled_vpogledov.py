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

    def test_seznam_oseb_zapise_prikazane_osebe_brez_iskalnega_niza(self):
        r = self.login().get(f"{BASE}/osebe/", {"q": "Testni"})
        shown = {str(p.pk) for p in r.context["page"].object_list}
        self.assertTrue(shown)
        rows = self.rows()
        self.assertEqual({x["entity_id"] for x in rows}, shown)
        self.assertEqual(len(rows), len(shown))
        self.assertEqual(
            {(x["actor"], x["screen"], x["entity_type"]) for x in rows},
            {(self.office.pk, "seznam", "person")},
        )
        values = m.AccessAudit.objects.values_list("screen", "entity_type", "entity_id")
        self.assertNotIn("Testni", str(list(values)))

    def test_seznam_brez_zapisa_ni_prikaza(self):
        client = self.login()
        with mock.patch.object(
            m.AccessAudit.objects, "bulk_create", side_effect=RuntimeError("baza ni dosegljiva")
        ):
            with self.assertRaises(RuntimeError):
                client.get(f"{BASE}/osebe/")

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


class AdminAuditTests(ScreenBase):
    """Skrbniški vmesnik: vpogled v sled pred prikazom, dokazi in odvzem niso spremenljivi."""

    def setUp(self):
        super().setUp()
        self.admin = self.office.account  # tehnični skrbnik z osebo v evidenci
        self.admin.is_staff = self.admin.is_superuser = True
        self.admin.save(update_fields=["is_staff", "is_superuser"])
        self.client = Client()
        self.client.force_login(self.admin)

    def rows(self):
        return list(
            m.AccessAudit.objects.values_list("actor", "screen", "entity_type", "entity_id")
        )

    def test_seznam_in_obrazec_osebe_zapiseta_vpogled(self):
        r = self.client.get("/admin/registry/person/")
        self.assertEqual(r.status_code, 200)
        shown = {str(p.pk) for p in r.context["cl"].result_list}
        self.assertIn(str(self.p1.pk), shown)
        self.assertEqual(
            set(self.rows()), {(self.office.pk, "admin:person", "person", pk) for pk in shown}
        )
        m.AccessAudit.objects.all().delete()
        r = self.client.get(f"/admin/registry/person/{self.p1.pk}/change/")
        self.assertContains(r, self.p1.contact_email)
        self.assertEqual(self.rows(), [(self.office.pk, "admin:person", "person", str(self.p1.pk))])

    def test_vsi_modeli_z_osebnimi_podatki_zapisejo_vpogled(self):
        for model, obj in (
            (m.Account, m.Account.objects.get(username="parent-01")),
            (m.Relationship, m.Relationship.objects.filter(guardian=self.p1).first()),
            (m.Grant, m.Grant.objects.filter(person=self.p1).first()),
            (m.Student, m.Student.objects.first()),
            (m.SourceMapping, m.SourceMapping.objects.first()),
        ):
            name = model._meta.model_name
            with self.subTest(model=name):
                m.AccessAudit.objects.all().delete()
                url = f"/admin/registry/{name}/{obj.pk}/change/"
                self.assertEqual(self.client.get(url).status_code, 200)
                self.assertEqual(
                    self.rows(), [(self.office.pk, f"admin:{name}", name, str(obj.pk))]
                )

    def test_brez_zapisa_ni_prikaza(self):
        with mock.patch.object(
            m.AccessAudit.objects, "create", side_effect=RuntimeError("baza ni dosegljiva")
        ):
            with self.assertRaises(RuntimeError):
                self.client.get(f"/admin/registry/person/{self.p1.pk}/change/")
        with mock.patch.object(
            m.AccessAudit.objects, "bulk_create", side_effect=RuntimeError("baza ni dosegljiva")
        ):
            with self.assertRaises(RuntimeError):
                self.client.get("/admin/registry/person/")

    def test_dokazi_in_odvzem_niso_spremenljivi(self):
        request = RequestFactory().get("/")
        request.user = self.admin
        for model in (m.ChangeAudit, m.AccessAudit):
            ma = admin.site._registry[model]
            with self.subTest(model=model.__name__):
                self.assertFalse(ma.has_add_permission(request))
                self.assertFalse(ma.has_change_permission(request))
                self.assertFalse(ma.has_delete_permission(request))
        for model in (m.Person, m.Approval, m.Relationship, m.Grant):
            with self.subTest(model=model.__name__):
                self.assertFalse(admin.site._registry[model].has_delete_permission(request))
        for model in (m.Relationship, m.Grant):
            ma = admin.site._registry[model]
            with self.subTest(model=model.__name__):
                self.assertFalse(ma.has_add_permission(request))
                self.assertFalse(ma.has_change_permission(request))
        audit = m.ChangeAudit.objects.create(action="x", entity_type="person", entity_id="1")
        r = self.client.post(f"/admin/registry/changeaudit/{audit.pk}/delete/", {"post": "yes"})
        self.assertEqual(r.status_code, 403)
        self.assertTrue(m.ChangeAudit.objects.filter(pk=audit.pk).exists())
