# Prvi neodvisni pregled P0 – paket T

Pregledani commit: `e854f60c7f2e9918b09f0b7db0108c6ab8f62b8f` (veja `main`, merge PR #38).

## 1. Podatki

| Podatek | Vrednost |
| --- | --- |
| Datum pregleda | 12. november 2026, Europe/Ljubljana |
| Repozitorij | https://github.com/odprta-sola/solska-platforma |
| Commit | `e854f60c7f2e9918b09f0b7db0108c6ab8f62b8f` |
| Pregledovalec | DeepSeek (ponudnik: DeepSeek); različica modela: **ni znano** |
| Odgovorni človek, ki poročilo sprejme | Mitja Pirih |
| Gostiteljski OS | Ubuntu 24.04.5 LTS, Linux x86_64, jedro 7.0.0-113042-tuxedo |
| Docker / Compose | 29.9.3 (build 5457199) / v5.7.0 |
| Python | gostitelj 3.12.3; aplikacijski vsebnik 3.12.16 |
| Aplikacijski vsebnik | `python:3.12-slim` (Debian GNU/Linux 13, trixie) |
| Django | 5.2.19 |
| Podatkovna zbirka | PostgreSQL 16.15 |
| Poštni predal | Mailpit (axllent/mailpit:latest) |

### Razkritje neodvisnosti in izvora

Pregledovane kode **ni napisal ta pregledovalec**. Po navedbi pobudnika in registru prispevkov jo je napisal **Claude (Anthropic)** po navodilih Mitje Piriha; starejše osnutke dokumentacije je pobudnik pripravljal tudi s pomočjo **OpenAI**. Ta pregled je opravil **drug sistem AI (DeepSeek)**; ni institucionalno neodvisen in ni človeški pregled. Navedba izvora ni forenzična potrditev avtorstva.

Opomba o pregledovalcu: navodilo za pregled (`docs/projekt/navodilo-za-pregled-OpenAI.md`) je bilo pripravljeno za sistem OpenAI, pregled pa je dejansko opravil sistem **DeepSeek**. Po pravilu »zapiši le, kar sistem zanesljivo ve o sebi« je v register vpisan DeepSeek, ne OpenAI.

### Kaj je bilo prebrano

Kontrolni seznam, načrt priprave P0 (»Človeški prevzem«), stanje T, kratka specifikacija, besedilni vmesnik, celoten `api/openapi.yaml`, `DEVELOPER.md`, `CONTRIBUTING.md`, `SECURITY.md`, register prispevkov. Od kode: `p0/registry/{authz,api,services,importer,models,adapters,admin}.py`, `p0/stubs/*`, `p0/config/{settings,urls}.py`, `p0/core/*`, upravljalni ukazi, migracije, vsi testi, `docker-compose.yml`, `p0/Dockerfile`, `requirements*.txt`, CI (`p0.yml`) in `LICENSE`.

## 2. Povzetek

**Kaj je preverjeno:** namestitev z Dockerjem, prava HTTP prijava z uporabniškim imenom in CSRF, ločeni identiteti pri skupnem kontaktu, izolacija družin (tuj/ugiban `scope_ref`), odvzem povezave in dovoljenja s sledjo, CSV uvoz (predogled, uveljavitev, ponovitev, pokvarjena datoteka), omejen servisni kontaktni klic, ločitev seje in servisnega žetona, nadomestka M1/M2, pogodbeni testi, odvisnosti in licence.

**Rezultat testov:** vseh **85 testov zelenih** (`Ran 85 tests … OK`); po `down -v` in novi namestitvi tudi vseh **39 pogodbenih testov** (`registry.tests.test_contract`). `ruff check`, `ruff format --check` in `makemigrations --check` brez napak.

**Kaj ni preverjeno:** točka 8 (obnašanje ob izpadu P0 — pravih M1/M2 ni), točka 9 (dostopnost — ni zaslonov P0, ni bralnika zaslona), dejanska SMTP dostava, produkcijska namestitev.

**Ugotovitve:** 1 srednja (neobdelana `ValidationError` pri malformed UUID → HTTP 500), 1 srednja že dokumentirana omejitev (ponastavitev gesla pri skupnem predalu), 2 opombi, 2 nizki. Varnostno občutljivih **novih** ugotovitev (vpogled v tuje podatke, obhod avtorizacije, uhajanje skrivnosti), ki bi zahtevale zasebno prijavo: **0 kritičnih, 0 visokih**.

**Skupna ocena:** jedro P0 (identiteta, povezave, upravičenja, odvzem, CSV uvoz, kontaktni klic, ločitev seje in žetona) je pregledno in dobro pokrito s testi. Prevzem T v celoti še ni dosegljiv, ker točki 8 in 9 nista izpolnjeni (to je znano stanje, ne napaka pregleda), D12 ni potrjen, obstaja pa tudi srednja ugotovitev glede obravnave napak.

**Priporočilo za prevzem T: pogojno.** Jedro P0 priporočam za nadaljnje delo, celoten prevzem T pa pod pogoji: (a) odprava srednje ugotovitve P0-01, (b) potrditev D12 pred vezavo modulov, (c) točki 8 in 9 ostajata odprti do nastanka pravih M1/M2 oziroma zaslonov in se ne štejeta za izpolnjeni, (d) obravnava že dokumentirane omejitve ponastavitve gesla (pred B). Odločitev o prevzemu sprejme pobudnik; ta pregled je dokaz, ne sam sprejem.

## 3. Devet točk kontrolnega seznama

Oznaka »izvedeno« pomeni opravljen pregled, ne nujno izpolnjeno merilo.

| # | Točka | Stanje | Dokaz (ukaz / korak in rezultat) |
| --- | --- | --- | --- |
| 1 | Prijava starša prikaže le njegove otroke; tuja družina zavrnjena | izvedeno | HTTP prijava `parent-03` (302 → `/p0/api/v1/me`), `GET /me/relationships` vrne samo `Učenec Testni 03`. Kot `parent-03` POST `authorizations/check` s `scope_ref` od `parent-01` in z ugibanim `sr_ugibam`: oba `{"allowed": false, "reason_code": "NOT_ALLOWED"}`; lastni sklic `ALLOWED`. Testi `test_starsa_vidita_samo_svoje_otroke`, `test_tuj_in_ugiban_sklic_enako_zavrnjena`. |
| 2 | Skupen kontakt, različna uporabnika; dovoljenje vezano na povezavo in obseg | izvedeno | Ločeni prijavi `parent-01` in `parent-02` (isti `family01@example.invalid`): različna `person_id` in `display_name`; `parent-01` ima otroka 01 in 02, `parent-02` samo otroka 01, z ločenima `scope_ref`. Testi `test_racun_s_skupnim_naslovom_se_prijavi_locen`, `test_skupni_kontakt_ostane_dve_osebi`, `test_dovoljenje_se_ne_prenasa_med_dejanji`. |
| 3 | Odvzem povezave ali dovoljenja prepreči novo dejanje | izvedeno | `manage.py shell`: `authz.revoke_relationship` za `parent-02` → `authorizations/check` vrne `NOT_ALLOWED`, `/me/relationships` prazen; `authz.revoke_grant` za `parent-01`/student-01 → `NOT_ALLOWED`, a student-02 še `ALLOWED`. `ChangeAudit` vsebuje `relationship.revoked` in `grant.revoked` (`changed_fields=["valid_until"]`). Testi `test_odvzem_povezave_in_upravicenja_prevlada`, `test_odvzem_pusti_sled`. |
| 4 | Napačen CSV brez delnega prepisa; ponovni uvoz brez dvojnikov; sled kontakta | izvedeno | `import_csv ../data/testni-uvoz --source testni --actor staff-03`: predogled `person:+8, grant:+4, relationship:+4 …`; `--apply-batch` uveljavljen; ponovni predogled vse `=unchanged`. Pokvarjena datoteka (`student-99`) → `unknown_student`, serija zavrnjena, število zapisov nespremenjeno. Testi `test_import.py` (22) in `test_sprememba_kontakta_je_sledljiva`. |
| 5 | Servisni kontaktni klic samo za evidentirano zahtevo in prejemnika; tuj obseg zavrnjen | izvedeno | `create_service_client m1`; brez žetona → 401; veljaven žeton + sklic → 200 (`email`, `locale`); tuj `scope_ref` → 403 `scope_not_allowed`; ugiban `recipient_id` → 403; žeton brez `p0.contacts.resolve` (m2) → 403. Testi `ContactContract`, `AuthorizationCheckContract.test_servisni_klic_*`. |
| 6 | Neodvisen pregled izvorne kode | izvedeno | Prebrani `authz.py`, `api.py`, `services.py`, `importer.py`, `models.py`, `stubs/*`, `settings.py` in povezane poti. Odgovori na vprašanja v razdelku 4 in spodaj. Pregled je opravil AI, ne človek. |
| 7 | Po ponastavitvi pogodbeni testi proti nadomestkoma | izvedeno | `docker compose down -v`, `up -d`, `seed_test_data` z novim `SEED_PASSWORD`; `python manage.py test registry.tests.test_contract`: **39/39 OK**. P0 in nadomestka tečejo v istem Django procesu; to niso omrežni preizkusi samostojnih modulov ali SMTP dostave. |
| 8 | Ob izpadu P0 moduli ne dovolijo dejanja in ne pošljejo na slepo | ni izvedeno | Končnega scenarija ni mogoče izvesti: pravih M1/M2 ni, nadomestka ne kličeta P0 in ne pošiljata. Potrjena neizpolnjenost iz stanja T. Test z imenom »izpad« (P0-04) izpada ne povzroči. |
| 9 | Prijava in osnovna opravila s tipkovnico, fokus, napake, bralnik | ni izvedeno | Zaslonov P0 (seznam oseb, uvoz) ni; obstaja samo privzeta prijava allauth. Bralnik zaslona in ročni prehod s tipkovnico nista izvedena (ni postopka). Potrjena neizpolnjenost iz stanja T. |

### Ključni izvedeni ukazi

```text
docker compose up --build -d          # z DOCKER_BUILDKIT=0 zaradi okolja pregleda
docker compose exec -T -e SEED_PASSWORD="<testno-geslo>" p0 python manage.py seed_test_data
  → Testni nabor naložen.
docker compose exec -T p0 python manage.py test
  → Found 85 test(s). Ran 85 tests … OK
docker compose exec -T p0 python manage.py test registry.tests.test_contract
  → Ran 39 tests … OK
docker compose exec -T p0 sh -c "ruff check . && ruff format --check . && python manage.py makemigrations --check --dry-run"
  → All checks passed! / 39 files already formatted / No changes detected
```

Testno geslo in servisni žetoni so bili naključni, izmišljeni in niso del poročila ali repozitorija.

## 4. Ugotovitve

Varnostno občutljive ugotovitve, ki bi zahtevale zasebno prijavo po SECURITY.md: **0 kritičnih, 0 visokih** (novih). Spodnje ugotovitve so javne.

| ID | Resnost | Kje | Opis | Ponovljiv korak | Predlog |
| --- | --- | --- | --- | --- | --- |
| P0-01 | srednja | `p0/registry/api.py:44-48` (`person_by_id`) | Nepravilen niz v `subject_id` / `author_id` / `recipient_id` sproži neobdelano `django.core.exceptions.ValidationError` (ki **ni** podrazred `ValueError`) → HTTP 500 z namesto 400/403. V `DEBUG=True` se prikaže tehnična sled (vsebina je Django-maskirana, ni skrivnosti). | `POST /p0/api/v1/audiences/resolve` (Bearer) s telesom `{"author_id":"not-a-uuid","class_id":"1","purpose":"notice"}` → 500. Enako `authorizations/check` (`subject_id`) in `delivery-contacts/resolve` (`recipient_id`). | V `person_by_id` ujeti še `django.core.exceptions.ValidationError` ali vhod validirati s `forms.UUIDField` in vrniti 400. |
| P0-02 | opomba | `p0/registry/api.py:270-272` | `delivery_contact_resolve` preverja »katerokoli« veljavno upravičenje (`acknowledge` **ali** `decide`), ne dovoljenja, ki ustreza dostavi. Vzrok: `scope_ref` je vezan na (oseba, obseg), ne na dovoljenje. | Branje kode. | Razrešiti v D12 (semantika `scope_ref` in `grants.scope_key`); trenutno ni zlorabno, ker seed uporablja samo `acknowledge`. |
| P0-03 | srednja (že dokumentirano) | `p0/config/settings.py:93` (`ACCOUNT_UNIQUE_EMAIL=False`, `ACCOUNT_EMAIL_VERIFICATION="none"`) + allauth `ResetPasswordForm` | Ponastavitev gesla po e-naslovu pošlje ponastavitveno pošto **vsem** računom z istim naslovom → v skupnem predalu lahko ena oseba prevzame račun druge. V repozitoriju že javno navedeno (`stanje-prevzema-T.md`, `DEVELOPER.md`) kot omejitev pred B. | Branje kode (allauth `request_password_reset` pošilja za vsakega uporabnika z istim e-naslovom). | Uvesti individualno aktivacijo/obnovo (že načrtovano pred B); do takrat se reset ne sme uporabljati za resnične račune. |
| P0-04 | opomba | `p0/registry/tests/test_contract.py:484` | Ime testa `test_zadrzek_dostave_ob_izpadu_ni_uspesen_preklic` ne ustreza vsebini: testira izolacijo tujega klicočega (404), ne zadržka/izpada. Točko 8 ne pokriva noben test. | Branje kode. | Preimenovati test ali dodati pravi scenarij izpada P0 (ko bo izvedljiv). |
| P0-05 | nizka | `p0/config/settings.py:22,122-127` | Pred produkcijo manjkajo `SECURE_HSTS_SECONDS`, `SECURE_SSL_REDIRECT`, `CSRF_TRUSTED_ORIGINS`; `ALLOWED_HOSTS` privzeto `localhost,127.0.0.1`. V `not DEBUG` so piškotki `Secure` in `Nosniff` pravilno vklopljeni. | Branje kode. | Določiti v produkcijski namestitvi (zdaj »ni za produkcijo«). |
| P0-06 | nizka | `docs/projekt/pregled-P0-kontrolni-seznam.md:18`, `docs/projekt/stanje-prevzema-T.md:16` | Zastarelo število testov: dokumentacija navaja 82, dejansko jih je 85. | Poganjanje `manage.py test`. | Posodobiti števili. |

### Odgovori na vprašanja za pregled kode (točka 6)

- **Pot do podatkov mimo `check_grant`/preverjanja sklica?** Ne najdem. `me`, `me/relationships`, `me/classes` izhajajo iz seje; `authorizations/check`, `audiences/resolve`, `delivery-contacts/resolve` gredo skozi `service_client`/`check_scope`/`check_grant`. `delivery_contact_resolve` preverja obseg in aktualno upravičenje (glej P0-02).
- **Razkritje obstoja tujega sklica/osebe/otroka (vsebina, koda, čas)?** Vsebinsko ne: tuj in neobstoječ sklic vrneta enak `NOT_ALLOWED`/`scope_not_allowed`; kontaktni klic ne razlikuje med neobstoječo osebo in tujim sklicem. Časovno je razlika v eni poizvedbi (zanemarljiva, ni praktično izkoriščljiva).
- **Ločitev seje in žetona?** Da. `service_client` ob veljavnem žetonu ne pade na sejo; neveljaven žeton (`Bearer svc_napacen`) je 401 tudi ob prisotni seji; neaktiven odjemalec 401; `service_only` ne upošteva seje. Preverjeno s testi in ročno.
- **Uvoz pravic zunaj pooblastila ali iz ugibane reference?** Ne. Uvoznik mora imeti vlogo `office`/`admin` (`actor_not_authorized`); reference se validirajo (`unknown_person`, `unknown_student`, `grant_without_relationship`); `staff_assignments` zahteva zaposlenega; dovoljenja so omejena na šifrant in obseg `student:<ključ>`.
- **Dnevnik/`ChangeAudit` z osebnimi vrednostmi?** Ne. Hrani `action`, `entity_id`, `changed_fields` (imena polj), brez vrednosti polj; predogled hrani samo imena spremenjenih polj (test `test_predogled_ne_spremeni_evidence`).
- **Uveljavitev z drugo vsebino kot predogled?** Ne. `apply_batch` primerja `content_hash` in zavrne (`ValueError`) ob razliki; serija je vse-ali-nič v transakciji.
- **Surove poizvedbe ali neomejen vnos?** Surova poizvedba samo `SELECT 1` v `core/views.py` (health). Uvoz ima `MAX_FILE_BYTES` (5 MB) in `MAX_ROWS` (50 000). Seznami API niso paginirani, a so omejeni z dejanskim številom zapisov. Nepravilen UUID ni ujet (P0-01).
- **Odvzeta povezava/upravičenje prevlada v vseh poteh?** Da v preverjenih poteh: `/me/relationships` (odvzeto izpade), `audiences/resolve` (izpade), `authorizations/check` (NOT_ALLOWED), `delivery-contacts/resolve` (403). `check_grant` ponovno preveri aktivnost povezave ob vsakem dejanju.

## 5. Pokritost 20 preizkusov kratke specifikacije

| # | Scenarij | Stanje |
| --- | --- | --- |
| 1 | Dva računa z istim kontaktnim naslovom | pokrit |
| 2 | Druga družina, ugiban ID, tuji scope_ref | pokrit |
| 3 | Zaposleni zunaj dodeljenega oddelka | pokrit |
| 4 | Učenčev račun in ciljna skupina | ni v obsegu T (predlog/razširitev) |
| 5 | Povezava brez potrjenega granta, nato odvzem | pokrit |
| 6 | Starejši uvoz po ročni omejitvi | pokrit |
| 7 | Napačen CSV ali neznana referenca | pokrit |
| 8 | Ponoven uvoz, dvojnik, manjkajoča vrstica | pokrit |
| 9 | Aktivacija/obnova dveh oseb pri skupnem predalu | nepokrit (pred B) |
| 10 | Odjava, CSRF, podtaknjen uporabnik, servisni klic | pokrit |
| 11 | Informativno obvestilo, odprtje, seznanitev | ni v obsegu T (M1) |
| 12 | Dva otroka, sprememba različice M1 | ni v obsegu T (M1) |
| 13 | Več namenov, Ne/brez odziva | ni v obsegu T (M2) |
| 14 | Dva otroka, dva odločevalca | ni v obsegu T (M2) |
| 15 | Neodobrena/spremenjena različica M2 | ni v obsegu T (M2) |
| 16 | Sprememba/preklic, zaključen/umaknjen obrazec | ni v obsegu T (M2) |
| 17 | Izpad M1, izgubljen 202, dvojni ključ | delno (idempotenca/konflikt pokrit v nadomestku; izpad/izguba 202 ne) |
| 18 | Opomnik, selektivni preklic, izpad P0/M2, tihi čas, iztek | delno (potreba, selektivni preklic, iztek pokrit; tihi čas in izpad ne) |
| 19 | Negotov SMTP, odvzem med dostavo, obnova kopije | ni v obsegu T / nepokrit |
| 20 | Sveža namestitev, P0/nadomestki, izvoz, dostopnost | delno (namestitev + P0 + nadomestka pokrit; izvoz in dostopnost ne) |

## 6. Odvisnosti in licence

| Odvisnost | Različica | Licenca | Združljivost z EUPL 1.2 |
| --- | --- | --- | --- |
| Django | 5.2.19 | BSD-3-Clause | da (permissivna) |
| django-allauth | 65.22.0 | MIT | da (permissivna) |
| psycopg / psycopg-binary | 3.3.9 | LGPL-3.0-only | da (knjižnica, dinamična vezava; EUPL 1.2 je združljiv z GPL/LGPL) |
| gunicorn | 27.0.0 | MIT | da (permissivna) |
| jsonschema (dev) | 4.26.0 | MIT | da |
| PyYAML (dev) | 6.0.3 | MIT | da |
| ruff (dev) | 0.17.4 | MIT | da |
| Osnovna slika | python:3.12-slim | Debian (mešano, standardna) | običajna osnova |
| PostgreSQL | 16.15 | PostgreSQL licence | storitev, ne distribuirana koda |
| Mailpit | latest | MIT | razvojno orodje |

Licenca projekta: **EUPL 1.2** (`LICENSE`). Odvisnosti so permissivne oziroma LGPL-3.0-only; slednja se uporablja kot knjižnica in ne vsiljuje copylefta na kodo P0. Znanih ranljivosti odvisnosti v pregledanih različicah nisem preverjal z zunanjo bazo CVE (omejitev).

## 7. Omejitve pregleda

- Gradnja slike je zahtevala `DOCKER_BUILDKIT=0`, ker je buildx v okolju pregleda pisal v read-only `~/.docker/buildx`; funkcionalno ni vplivalo na rezultat.
- Točki 8 in 9 nista izvedljivi (pravih M1/M2 in zaslonov ni); potrjeno kot znano stanje.
- Nisem preverjal: dejanske SMTP dostave, produkcijske namestitve (gunicorn/HTTPS), znanih CVE odvisnosti prek zunanje baze, bralnika zaslona, pisanja v repozitorij (brez pisalnega dostopa).
- Pregled je statičen + izvedeni testi in ročni HTTP klici; ni dinamičnega varnostnega skeniranja ali fuzzinga.

## 8. Izjava

Ta pregled **ni** človeški prevzem, **ni** pravno mnenje in **ni** potrditev D12. Ne nadomešča presoje pobudnika, mentorjev ali skupnega tehničnega nosilca. Ugotovitve so dokaz za odločitev o prevzemu T, ki jo sprejme pobudnik.
