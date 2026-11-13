"""Sočasna prva izdaja sklica na obseg (DS T-02) in geslo testnega nabora (DS T-09)."""

import os
import secrets
import threading
from unittest import mock

from django.core.management import call_command
from django.db import connection
from django.db.models.query import QuerySet
from django.test import TestCase, TransactionTestCase

from registry import models as m
from registry import services


class ConcurrentScopeRefTests(TransactionTestCase):
    def setUp(self):
        self.person = m.Person.objects.create(display_name="Testni Starš")

    def test_socasna_prva_zahteva_vrne_isti_sklic(self):
        barrier = threading.Barrier(2, timeout=10)
        original = QuerySet.create
        results, errors = [], []

        def create(qs, **kwargs):
            if qs.model is m.ScopeRef:
                barrier.wait()  # obe niti sta že ugotovili, da sklica še ni
            return original(qs, **kwargs)

        def worker():
            try:
                results.append(services.issue_scope_ref(self.person, "student:x").ref)
            except Exception as exc:  # noqa: BLE001 - test zbira napake niti
                errors.append(exc)
            finally:
                connection.close()

        with mock.patch.object(QuerySet, "create", create):
            threads = [threading.Thread(target=worker) for _ in range(2)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(15)
        self.assertEqual(errors, [])
        self.assertEqual(len(results), 2)
        self.assertEqual(len(set(results)), 1)
        self.assertEqual(m.ScopeRef.objects.filter(person=self.person).count(), 1)


class SeedPasswordTests(TestCase):
    def test_geslo_se_nastavi_tudi_obstojecim_racunom(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SEED_PASSWORD", None)
            call_command("seed_test_data", verbosity=0)
        self.assertFalse(m.Account.objects.get(username="parent-01").has_usable_password())
        password = secrets.token_urlsafe(18)
        with mock.patch.dict(os.environ, {"SEED_PASSWORD": password}):
            call_command("seed_test_data", verbosity=0)
        self.assertTrue(m.Account.objects.get(username="parent-01").check_password(password))

    def test_brez_gesla_obstojece_geslo_ostane(self):
        password = secrets.token_urlsafe(18)
        with mock.patch.dict(os.environ, {"SEED_PASSWORD": password}):
            call_command("seed_test_data", verbosity=0)
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SEED_PASSWORD", None)
            call_command("seed_test_data", verbosity=0)
        self.assertTrue(m.Account.objects.get(username="parent-01").check_password(password))
