# Kontrolni seznam za neodvisni pregled P0 (paket T)

Status: osnutek, 12. november 2026. Podlaga je devet točk iz [načrta priprave P0](priprava-referencnega-P0.md#človeški-prevzem). Seznam pregledovalcu olajša delo; ne nadomešča njegove presoje in ne pomeni, da je prevzem opravljen.

## Kdo pregleduje

Pregledovalec ne sme biti avtor pregledovane kode. Pobudnik je določil, da pregled opravi drug AI, mentor je rezerva (odločitev 12. 11. 2026, [register](odlocitve.md)). Opomba: v načrtu je pregledovalec »človek, ki ni izdelal kode«. Zamenjava s pregledom z AI je osebna odločitev pobudnika in ni potrjena kot enakovredna človeškemu prevzemu. Zato naj pregled poleg ugotovitev vsebuje tudi ime človeka, ki je ugotovitve prebral in sprejel (pobudnik ali mentor).

## Priprava

```bash
git clone https://github.com/odprta-sola/solska-platforma.git && cd solska-platforma
docker compose up --build -d
docker compose exec -T -e SEED_PASSWORD="<izberite-testno-geslo>" p0 python manage.py seed_test_data
docker compose exec -T p0 python manage.py test
```

Pričakovano: vsi testi zeleni; število na posameznem commitu je v [zapisu o odpravi](../pregledi/2026-11-odprava-prvega-pregleda-P0.md), preskočeni testi so označeni z razlogom. Geslo je samo testno in ne sme biti uporabljeno nikjer drugje. Pošta je v http://localhost:8025. Po koncu: `docker compose down -v`.

## Točke pregleda

Pri vsaki točki zapišite: izvedeno / ni izvedeno, ugotovitev, ponovljiv ukaz ali korak.

| # | Točka | Kako preveriti | Avtomatski dokaz |
| --- | --- | --- | --- |
| 1 | Prijava testnega starša prikaže le njegova otroka; naslov druge družine zavrnjen | Prijava `parent-03` na `/accounts/login/`, nato `GET /p0/api/v1/me/relationships`. Z `scope_ref` iz seje `parent-01` pokličite `POST /p0/api/v1/authorizations/check` kot `parent-03` | `test_starsa_vidita_samo_svoje_otroke`, `test_tuj_in_ugiban_sklic_enako_zavrnjena` |
| 2 | Starša s skupnim kontaktom ostaneta različna uporabnika; dovoljenje je vezano na povezavo in obseg | Prijava `parent-01` in `parent-02` (isti `family01@example.invalid`); primerjajte `/me` | `test_racun_s_skupnim_naslovom_se_prijavi_locen`, `test_skupni_kontakt_ostane_dve_osebi` |
| 3 | Odvzem povezave ali dovoljenja prepreči novo dejanje | Kot `staff-03` na `/p0/evidenca/osebe/` odvzemite povezavo ali upravičenje (ali v `manage.py shell` `registry.authz.revoke_*`), nato ponovite `authorizations/check` | `test_odvzem_povezave_in_upravicenja_prevlada`, `test_odvzem_pusti_sled` |
| 4 | Napačen CSV ne povzroči delnega prepisa; ponovni uvoz ne podvoji; sprememba kontakta je sledljiva | `import_csv` na `data/testni-uvoz` (predogled, uveljavitev, ponovitev), nato pokvarjena datoteka. Preglejte `ChangeAudit` | `registry/tests/test_import.py` (22 testov) |
| 5 | Servisni klic za kontakt samo za evidentirano zahtevo in prejemnika; tuj obseg zavrnjen | `create_service_client` z/brez `p0.contacts.resolve`; poskusite brez žetona, s tujim in ugibanim `scope_ref` | `ContactContract`, `AuthorizationCheckContract.test_servisni_klic_*` |
| 6 | Neodvisen pregled izvorne kode | Preberite `registry/authz.py`, `registry/api.py`, `registry/services.py`, `registry/importer.py`; vprašanja spodaj | Ni (človeška presoja) |
| 7 | Po ponastavitvi podatkov pogodbeni testi proti nadomestkoma | `down -v`, ponovna priprava, `test registry.tests.test_contract registry.tests.test_robni` | `test_contract.py`, `test_robni.py`, preverjevalnik `contract_check.py` |
| 8 | Ob izpadu P0 moduli ne dovolijo zaščitenega dejanja in ne pošljejo na slepo | Za zdaj nepreverljivo: pravi M1/M2 še ne obstajata; nadomestki ne kličejo P0 | Ni |
| 9 | Prijava in osnovna opravila s tipkovnico, fokus, razumljive napake, bralnik zaslona | Ročno po [pregledu dostopnosti](pregled-dostopnosti-P0.md): prijava, osebe, odvzem, kontakt, uvoz pod `/p0/evidenca/` | `test_dostopnost.py`, `test_zasloni.py` (struktura, ne nadomesti ročnega pregleda) |

Točke 8 in 9 trenutno ne morejo biti izpolnjene; to je ugotovitev, ne napaka pregledovalca ([stanje](stanje-prevzema-T.md)).

## Vprašanja za pregled kode (točka 6)

- Ali obstaja pot do podatkov osebe ali kontakta, ki ne gre skozi `check_grant` ali preverjanje sklica?
- Ali kateri koli odgovor napake ali uspeha razkrije obstoj tujega sklica, osebe ali otroka (vsebina, koda, čas)?
- Ali `authorization_check` in servisni dekoraterji res ločujejo sejo od žetona (neveljaven žeton, žeton in seja skupaj)?
- Ali uvoz lahko poda pravice zunaj pooblastila uvoznika ali iz ugibane reference?
- Ali kateri dnevnik ali `ChangeAudit` hrani osebne vrednosti, ki jih ne bi smel?
- Ali je mogoče uveljaviti serijo z drugo vsebino, kot je bila v predogledu?
- Ali so kje uporabljene surove poizvedbe ali neomejen vnos?
- Ali odvzeta povezava ali upravičenje res prevlada v vseh poteh (`/me/relationships`, `audiences/resolve`, `delivery-contacts/resolve`)?

## Zapis ugotovitev

Ugotovitve zapišite v issue (brez osebnih podatkov, tudi izmišljenih ne več kot nujno): točka, ukaz, rezultat, resnost, predlog. Sprejem prevzema T je odločitev pobudnika; neodvisni pregled je dokaz zanj, ne sam sprejem.
