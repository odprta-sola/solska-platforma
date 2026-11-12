from datetime import timedelta

from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from registry import models as m


class IdentityTests(TestCase):
    def test_osebi_lahko_delita_kontakt(self):
        a = m.Person.objects.create(display_name="A", contact_email="x@example.invalid")
        b = m.Person.objects.create(display_name="B", contact_email="x@example.invalid")
        self.assertNotEqual(a.pk, b.pk)

    def test_dva_racuna_z_istim_email_naslovom(self):
        m.Account.objects.create(username="a", email="x@example.invalid")
        m.Account.objects.create(username="b", email="x@example.invalid")
        self.assertEqual(m.Account.objects.count(), 2)

    def test_racun_je_dodeljen_najvec_eni_osebi(self):
        p = m.Person.objects.create(display_name="A")
        m.Account.objects.create(username="a", person=p)
        with self.assertRaises(IntegrityError), transaction.atomic():
            m.Account.objects.create(username="b", person=p)

    def test_enolicna_preslikava_izvornega_kljuca(self):
        kw = dict(source="s", entity_type="person", source_key="k")
        m.SourceMapping.objects.create(target_id=m.Person.objects.create(display_name="A").pk, **kw)
        with self.assertRaises(IntegrityError), transaction.atomic():
            m.SourceMapping.objects.create(
                target_id=m.Person.objects.create(display_name="B").pk, **kw
            )


class ValidityTests(TestCase):
    def setUp(self):
        self.parent = m.Person.objects.create(display_name="P")
        self.student = m.Student.objects.create(person=m.Person.objects.create(display_name="S"))
        self.now = timezone.now()

    def _rel(self, start, end=None):
        return m.Relationship.objects.create(
            guardian=self.parent,
            student=self.student,
            relationship_type="parent",
            valid_from=start,
            valid_until=end,
        )

    def test_konec_mora_biti_po_zacetku(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            self._rel(self.now, self.now - timedelta(days=1))

    def test_active_upošteva_zacetek_in_konec(self):
        self._rel(self.now - timedelta(days=10), self.now - timedelta(days=1))  # zaključena
        self._rel(self.now + timedelta(days=1))  # prihodnja
        open_rel = self._rel(self.now - timedelta(days=1))
        self.assertEqual(list(m.Relationship.objects.active()), [open_rel])

    def test_povezava_sama_ne_podeli_pravice(self):
        self._rel(self.now - timedelta(days=1))
        self.assertFalse(m.Grant.objects.filter(person=self.parent).exists())

    def test_upravicenje_zahteva_potrditev(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            m.Grant.objects.create(
                person=self.parent, scope_key="x", permission="y", valid_from=self.now
            )


class SeedTests(TestCase):
    def test_seed_je_idempotenten_in_ima_posebne_primere(self):
        call_command("seed_test_data", verbosity=0)
        call_command("seed_test_data", verbosity=0)
        self.assertEqual(m.Person.objects.count(), 11)
        p1 = m.SourceMapping.objects.get(source_key="parent-01", entity_type="person")
        p2 = m.SourceMapping.objects.get(source_key="parent-02", entity_type="person")
        a = m.Person.objects.get(pk=p1.target_id)
        b = m.Person.objects.get(pk=p2.target_id)
        self.assertEqual(a.contact_email, b.contact_email)  # skupni kontakt
        self.assertEqual(a.relationships.count(), 2)  # dva otroka
        self.assertEqual(m.Person.objects.filter(contact_email="", roles__role="parent").count(), 1)

    def test_testni_racuni_nimajo_gesla(self):
        call_command("seed_test_data", verbosity=0)
        self.assertFalse(m.Account.objects.get(username="parent-01").has_usable_password())
