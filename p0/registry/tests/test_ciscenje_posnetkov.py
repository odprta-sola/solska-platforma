"""Čiščenje poteklih posnetkov občinstva (varstvo podatkov, D07; rok iz D12)."""

from datetime import timedelta
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.utils import timezone

from registry import audiences
from registry import models as m

from .test_contract import P0, ContractBase, person_of


class AudienceSnapshotPurgeTests(ContractBase):
    def setUp(self):
        super().setUp()
        self.old = self.audience()
        self.new = self.audience()
        m.AudienceSnapshot.objects.filter(ref=self.old["audience_ref"]).update(
            expires_at=timezone.now() - timedelta(seconds=1)
        )

    def snapshot_refs(self):
        return set(m.AudienceSnapshot.objects.values_list("ref", flat=True))

    def contact(self, aud, username="parent-01"):
        pid = str(person_of(username).pk)
        x = next(r for r in aud["recipients"] if r["person_id"] == pid)
        body = {
            "audience_ref": aud["audience_ref"],
            "recipient_id": x["person_id"],
            "scope_ref": x["scope_ref"],
        }
        return self.call("post", f"{P0}/delivery-contacts/resolve", token=self.t_m1, body=body)

    def test_ukaz_izbrise_potekle_s_clani_in_je_ponovljiv(self):
        old_members = m.AudienceMember.objects.filter(snapshot__ref=self.old["audience_ref"])
        self.assertTrue(old_members.exists())
        out = StringIO()
        call_command("purge_audience_snapshots", stdout=out)
        self.assertIn("Počiščenih posnetkov: 1", out.getvalue())
        self.assertEqual(self.snapshot_refs(), {self.new["audience_ref"]})
        self.assertFalse(old_members.exists())
        self.assertTrue(
            m.AudienceMember.objects.filter(snapshot__ref=self.new["audience_ref"]).exists()
        )
        self.assertEqual(audiences.purge_expired(), 0)
        self.assertEqual(self.snapshot_refs(), {self.new["audience_ref"]})

    def test_meja_roka(self):
        snap = m.AudienceSnapshot.objects.get(ref=self.new["audience_ref"])
        self.assertEqual(audiences.purge_expired(snap.expires_at - timedelta(microseconds=1)), 1)
        self.assertIn(snap.ref, self.snapshot_refs())  # pred rokom ostane
        self.assertEqual(audiences.purge_expired(snap.expires_at), 1)
        self.assertEqual(self.snapshot_refs(), set())  # ob roku je potekel, kot v razrešitvi

    def test_privzeti_cas_je_trenutni(self):
        snap = m.AudienceSnapshot.objects.get(ref=self.new["audience_ref"])
        with mock.patch("registry.audiences.timezone.now", return_value=snap.expires_at):
            self.assertEqual(audiences.purge_expired(), 2)

    def test_razresitev_po_ciscenju_enaka_kot_pred_njim(self):
        before = self.contact(self.old)
        audiences.purge_expired()
        after = self.contact(self.old)

        def shape(r):  # trace_id je za vsako zahtevo drug
            return r.status_code, {k: v for k, v in r.json().items() if k != "trace_id"}

        self.assertEqual(shape(before), shape(after))
        self.assertEqual(after.status_code, 403)
        self.assertEqual(self.contact(self.new).status_code, 200)  # veljaven ostane uporaben

    def test_ciscenje_ne_brise_oseb_in_upravicenj(self):
        counts = (m.Person.objects.count(), m.Grant.objects.count(), m.ScopeRef.objects.count())
        audiences.purge_expired()
        self.assertEqual(
            (m.Person.objects.count(), m.Grant.objects.count(), m.ScopeRef.objects.count()),
            counts,
        )
