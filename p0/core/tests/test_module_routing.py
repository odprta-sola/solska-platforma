"""Usmerjanje API modulov: nadomestek, dokler je v STUBS, sicer pravi modul (m1/m2 api_urls)."""

import importlib

from django.test import SimpleTestCase, override_settings
from django.urls import Resolver404, clear_url_caches, resolve

import config.urls


class ModuleRoutingTests(SimpleTestCase):
    def reload(self):
        clear_url_caches()
        importlib.reload(config.urls)

    def tearDown(self):
        self.reload()

    def test_nadomestek_v_razvoju(self):
        with override_settings(STUBS={"m1", "m2"}):
            self.reload()
            self.assertEqual(resolve("/m1/api/v1/delivery-requests").func.__module__, "stubs.m1")
            self.assertEqual(resolve("/m2/api/v1/reminders/check").func.__module__, "stubs.m2")

    def test_pravi_modul_po_izklopu_nadomestka(self):
        with override_settings(STUBS={"m2"}):
            self.reload()
            with self.assertRaises(Resolver404):  # api M1 še ni izdelan
                resolve("/m1/api/v1/delivery-requests")
            self.assertEqual(resolve("/m2/api/v1/reminders/check").func.__module__, "stubs.m2")

    def test_zasloni_modulov(self):
        self.assertEqual(resolve("/m1/").url_name, "m1-home")
        self.assertEqual(resolve("/m2/").url_name, "m2-home")
