# Ponovni neodvisni pregled P0 – paket T (DeepSeek)

Pregledani commit: `184c8f97191f5500e4308870f13fab7d19fee76f` (izhodišče iz navodila). Ob začetku pregleda je bil `main` že na `127f1d5f2aef3ae1b55afe4ad5a21054b7fa5a53`; med tema commitoma so samo dokumentacija in `.github/dependabot.yml`, koda P0 se ne spremeni. Meritve in ukazi so zato izvedeni na `127f1d5`, kar je v nadaljevanju označeno.

## 1. Podatki

| Podatek | Vrednost |
| --- | --- |
| Datum pregleda | 12. november 2026, Europe/Ljubljana |
| Repozitorij | https://github.com/odprta-sola/solska-platforma |
| Pregledani commit | `184c8f97191f5500e4308870f13fab7d19fee76f` |
| Dejansko izmerjeni commit | `127f1d5f2aef3ae1b55afe4ad5a21054b7fa5a53` (`main` ob začetku; koda P0 enaka) |
| Pregledovalec | DeepSeek (ponudnik: DeepSeek); različica modela: **ni znano** |
| Odgovorni človek, ki poročilo prebere in sprejme | Mitja Pirih; njegov sprejem ob pripravi tega poročila **ni potrjen** |
| Gostiteljski OS | Ubuntu 24.04.5 LTS, Linux x86_64, jedro 7.0.0-113042-tuxedo |
| Docker / Compose | 29.9.3 (build 5457199) / v5.7.0 |
| Python | gostitelj 3.12.3; aplikacijski vsebnik 3.12.16 |
| Aplikacijski vsebnik | `python:3.12-slim` (Debian GNU/Linux 13.7, trixie), digest `sha256:5e2bdb1b…` |
| Django | 5.2.19 |
| psycopg | 3.3.9 |
| Podatkovna zbirka | PostgreSQL 16.15 |
| Poštni predal | Mailpit 1.33.1 |

### Razkritje neodvisnosti in izvora

Pregledovane kode **nisem napisal**. Po registru prispevkov jo je napisal **Claude (Anthropic), model Claude Sonnet 5.5**, po navodilih pobudnika; popravke po prvem pregledu je napisal **Claude Opus 5.5** (Anthropic). Prvi pregled sta opravila sistema Codex/OpenAI in DeepSeek; **poročilo DeepSeek prvega kroga je napisal isti sistem kot to poročilo**, zato ta ponovni pregled ni neodvisen od tistega poročila. Pregled je opravil **drug sistem AI glede na pisca kode**, ne pa glede na prvo poročilo DeepSeek. Ni institucionalno neodvisen in ni človeški prevzem. Navedba izvora ni forenzična potrditev avtorstva.

Opomba: navodilo za pregled je bilo pripravljeno za sistema OpenAI in DeepSeek; to poročilo uporablja oznako **deepseek**. O sebi ne ugibam: sistem je DeepSeek, ponudnik DeepSeek, različica modela ni znana.

### Kaj je bilo prebrano

Poročili prvega kroga (`2026-11-prvi-pregled-P0-openai.md`, `…-deepseek.md`), zapis o odpravi, kontrolni seznam, stanje T, register odločitev, pregled dostopnosti, odvisnosti in licence, `DEVELOPER.md`, `SECURITY.md`, `CONTRIBUTING.md`, `api/openapi.yaml`, `docker-compose.yml`, `p0/Dockerfile`, `.github/workflows/p0.yml`, `docs-links.yml`, `.github/dependabot.yml` in `LICENSE`. Od kode: `p0/core/{middleware,views,http}.py`, `p0/config/{settings,urls,checks}.py`, `p0/registry/{api,authz,services,importer,contract_schemas,ui,forms,models,adapters,context}.py`, `p0/stubs/*`, ukazi, migracije, predloge in vsi testi. Prebrani so bili tudi podatki `data/testni-uvoz` in objavljeni varnostni nasveti S-01 do S-04 (naslovi in javni opisi).

## 2. Povzetek

**Priporočilo za celoten prevzem T: ne.** Jedro P0 po popravkih priporočam za nadaljnje delo **pogojno**, celotnega prevzema T pa še ne: D12 ni potrjen, točka 8 ni preverljiva brez pravih M1/M2, točka 9 ni zaključena brez človeškega pregleda z bralnikom zaslona, S-01 je začasno zaprta (ne izpolnjena), S-03 pa potrebuje individualni postopek pred B.

**Kaj je potrjeno:** vseh **173 testov** je uspešnih, **2 sta izrecno preskočena** (meji modulov M1/M2, ker mapi še ne obstajata). Po `docker compose down -v`, ponovni namestitvi in `seed_test_data` je **98 testov** pogodbe, robnih primerov in zaslonov uspešnih. S-01 do S-04 so preverjene z lastno reprodukcijo; pri S-01 in S-03 je učinek začasno onemogočen, ne pa funkcionalno dokončan.

**Kaj ostaja:** D12; prava M1/M2 in točka 8; človeški pregled dostopnosti; S-01 (preverljiva vezava na dostavo) in S-03 (individualna obnova); SBOM/pravni pregled licenc, HSTS/HTTPS ob namestitvi; omejitve nadomestkov. Nove javne ugotovitve so nizke (R-02 do R-07); ena nova zasebna ugotovitev je nizke resnosti (R-01) in je opisana pobudniku v pogovoru, v tem poročilu samo kot število.

**Pogojno za jedro P0:** (a) odpraviti R-02 in R-03 ter uskladiti dokumentacijo; (b) odpraviti 5 px prelivanje pri 320 px in opraviti človeški pregled z bralnikom; (c) potrditi D12 in urediti S-01/S-03; (d) ohraniti točko 8 odprto do pravih modulov. Brez teh pogojev prevzema T ne bi priporočil.

## 3. Tabela odprave

### 3.1 Zasebne varnostne ugotovitve S-01 do S-04

| ID | Prejšnja resnost | Novo stanje | Dokaz |
| --- | --- | --- | --- |
| S-01 | visoka | **odpravljeno začasno** (klic zaprt, 503) | `ContactBindingContract`: 5/5; veljaven, tuj, neobstoječ in odvzet vhod vrnejo 503 brez `email` in brez razlike v kodi. Ročno: m1 žeton z veljavnim, tujim in neobstoječim sklicem -> 503; brez žetona -> 401; m2 žeton -> 403; seja -> 401. Merilo točke 5 ni izpolnjeno do D12. |
| S-02 | visoka | **odpravljeno** | `ImportRestrictionTests`: 9/9. Ročni odvzem povezave ali upravičenja, nato uvoz s spremenjenim `valid_from`, spremenjeno vrsto povezave ali obojim -> `manual_restriction`, serija zavrnjena, vse štiri poti zavrnejo. Ročno po odvzemu: `/me/relationships` prazen, `authorizations/check` `NOT_ALLOWED`, v `audiences/resolve` osebe ni; kontaktni klic je 503 (s simulirano vezavo v testu 403). En test je lažno zelen (R-04), kritje granta pa obstaja v `test_odvzem_enega_dovoljenja_ne_vpliva_na_drugega`. |
| S-03 | visoka | **odpravljeno** | `PasswordRecoveryTests`: 6/6. Vse poti pod `/accounts/password/reset/` vrnejo 404 (tudi prej izdan ključ), `send_password_reset_mail` ne pošlje ničesar, prijava ne kaže povezave. Ob začasni odstranitvi zapora: 6/6 testov pade. Individualna obnova ostaja pred B. |
| S-04 | srednja | **odpravljeno** | `ImportRoleTests`: 6/6. Tajništvo z uvozom ne doda `admin` ali `office`; ponovni uvoz obstoječe vloge je dovoljen; skrbnik sme dodati obe. Ob odstranitvi varovala: 2/6 testov padeta. |

### 3.2 Ugotovitve poročila OpenAI

| ID | Prejšnja resnost | Novo stanje | Dokaz |
| --- | --- | --- | --- |
| P0-01 | srednja | **odpravljeno** | `RequestValidation` (6 testov) in `RequestSchemaParity`; manjkajoče, dodatno, ugnezdeno polje, napačen tip, prazen in predolg niz ter napačen JSON -> 400. Ob odstranitvi preverjanja: 112 padlih podtestov. Meje dolžin in števil ostajajo predlog D12. |
| P0-02 | srednja | **odpravljeno** (z novo omejitvijo R-03) | `ApiErrorContract`: neveljaven UUID -> 200 `NOT_ALLOWED` oziroma 400; `OperationalError` -> 503 brez `allowed`; nepričakovana napaka -> 500 JSON brez podrobnosti; seja brez CSRF -> 403 JSON; napačna metoda -> 405 JSON z `Allow`; neznana pot -> 404 JSON; napačen žeton ob seji -> 401. Preveliko telo zahteve še vedno vrne 400 HTML (R-03). |
| P0-03 | srednja | **delno** | `StubEdgeContract`: ista oseba z dvema obsegoma -> 400 `duplicate_recipient`, brez tihega prepisa. Identiteta dostavne postavke ostaja D12. |
| P0-04 | opomba | **delno** | `test_ponovitev_po_izteku…`: ista zahteva po izteku vrne isti prevzem 202 brez nove dostave; nova pretečena zahteva -> 400. Okno hrambe ključa ostaja D12. |
| P0-05 | srednja | **odpravljeno** | `PreviewApplyTests` (5) in `ConcurrentApplyTests` (1): sprememba osebe, granta ali pooblastila po predogledu -> `preview_stale` in zavrnitev; dve sočasni uveljavitvi -> ena uspe, ena zavrnjena; napaka pred končnim zapisom ne pusti podatkov. Ob odstranitvi vezave: 2/5 testov padeta. |
| P0-06 | srednja | **odpravljeno za `ContractBase.call`** | `contract_check.py` preveri status, vsebinski tip, shemo s formati, pogojne sheme in `counts`; `CheckerSelfTest` (3) pade ob odstranitvi `format_checker`. Klici neposredno prek Django odjemalca niso samodejno preverjeni, kar je v dokumentaciji navedeno. |
| P0-07 | srednja | **delno** | Preimenovana sta testa preklica in izteka, test odnosa brez granta kliče `authz`, manjkajoči mapi M1/M2 sta izrecno preskočeni. Vendar je `test_premaknjen_zacetek_granta` lažno zelen (R-04), pravega izpada pa še vedno ne pokriva noben test (točka 8). |
| P0-08 | srednja | **odprto** | Nadomestka sta še v pomnilniku procesa, ne dokazujeta trajnosti, obnove, izpada ali urnika; omejitve so navedene v stanju T in v pogodbi. |
| P0-09 | nizka | **delno** | Dokumentacija je posodobljena na 173 testov in večinoma usklajena, a ostajajo trditve, ki jih koda ne podpira: ena zasebna ugotovitev o hrambi (R-01), „napake na poteh API so vedno JSON“ (R-03), „predogled hrani samo imena spremenjenih polj“ (hrani tudi `entity_type`, `source_key`, `action`). |
| P0-10 | srednja | **delno** | Zasloni in predloge obstajajo; `test_dostopnost.py` 8/8 in `test_zasloni.py` 25/25; ročno prek CDP sem preveril jezik, naslove, oznake, vrstni red fokusa, viden fokus, povzetek napak in povezave do polj. Pri 320 px se stran osebe preliva za 5 px (R-05); bralnik zaslona ni bil uporabljen. |
| P0-11 | nizka | **delno** | Zaklepi s hashi, digesti slik in Actions; `pip-audit` za vse tri zaklepe brez zadetkov; produkcijska slika P0 po Trivy: 205 opozoril Debiana (47 visokih, 74 srednjih, 65 nizkih, 19 neznanih), **nobeno s popravkom**, 0 paketov Python. Razvojna slika ima 3 opozorila `setuptools` (R-07). SBOM, pravni pregled licenc in HSTS/HTTPS ostajajo odprti. |

### 3.3 Ugotovitve poročila DeepSeek (prvi krog)

| ID | Prejšnja resnost | Novo stanje | Dokaz |
| --- | --- | --- | --- |
| P0-01 | srednja | **odpravljeno** | `person_by_id` ujame `ValueError`, `TypeError` in `ValidationError`; neveljaven UUID v `authorizations/check` vrne 200 `NOT_ALLOWED`, v `audiences/resolve` 400. `ApiErrorContract` potrjuje, da ni 500. |
| P0-02 | opomba | **ni odpravljeno, a ni dosegljivo** | `_resolve_contact` še vedno preverja katerokoli veljavno upravičenje (`any(check_grant(...) for perm in GRANT_TO_CODE)`), ne le tistega, ki ustreza dostavi. Ker je klic do D12 zaprt s 503, ni zlorabljiv; ostaja opomba za D12. |
| P0-03 | srednja (že dokumentirano) | **odpravljeno** | Enako kot S-03: poti 404, adapter ne pošlje, prijava brez povezave; individualni postopek ostaja pred B. |
| P0-04 | opomba | **odpravljeno** | Starega zavajajočega imena ni več; preklic tuje zahteve se preverja kot 404 (`test_preklic_tuje_zahteve_je_404`), stanja so ločena. Točka 8 s tem ni pokrita. |
| P0-05 | nizka | **ni odpravljeno** | `check --deploy` z dolgo sintetično skrivnostjo vrne W004 (HSTS) in W008 (HTTPS preusmeritev); `CSRF_TRUSTED_ORIGINS` ni določen. Odločitev je pri D04. |
| P0-06 | nizka | **odpravljeno** | Dokumenti in zapis o odpravi navajajo 173 testov; stale številke 82 ni več v pregledanih dokumentih. |

## 4. Nove ugotovitve

**Javne:** R-02 do R-07, vse nizke. **Zasebno:** ena nova nizka ugotovitev (R-01); v tem javnem poročilu sta navedena samo število in resnost, podrobnosti so pobudniku v pogovoru oziroma po SECURITY.md. Novih kritičnih, visokih ali srednjih varnostnih ugotovitev ni.

| ID | Resnost | Kje | Opis | Ponovljiv korak | Predlog |
| --- | --- | --- | --- | --- | --- |
| R-02 | nizka | `p0/registry/importer.py` (`parse_files`, `validate_rows`, `do_persons`, `do_students`, `do_grants`); modelne meje `Person.display_name=200`, `SourceMapping.source_key=128` itd. | UVoz ne preverja dolžin polj pred zapisom v bazo. Predolg `display_name` ali `source_person_key` sproži `django.db.utils.DataError`; predogled se konča s 500, ne s `Problem`. | `importer.preview({"persons": b"source_person_key;display_name;contact_email\nprobe-1;" + b"x"*300 + b";\n"}, "probe", actor)` -> `DataError: value too long for type character varying(200)`; 200-znakovni ključ -> `character varying(128)`. | Pred validacijo izpeljati meje iz modelov in vrniti `too_long`/`bad_length`; dodati teste za 201/129 znakov in za vse tabele. |
| R-03 | nizka | `p0/core/middleware.py:37-41`; `p0/registry/api.py:38-43` (`json_body`) | `ApiErrorMiddleware` izrecno izvzame `SuspiciousOperation`; preveliko telo zahteve zato na poti API vrne 400 HTML, ne pogodbenega JSON `Error`. Dokumentacija trdi, da so napake na poteh API vedno JSON. | `Client().post("/p0/api/v1/authorizations/check", data=b"x"*(3*1024*1024), content_type="application/json", HTTP_AUTHORIZATION="Bearer …")` -> 400 `text/html`, `<h1>Bad Request (400)</h1>`; v odgovoru ni `code`/`trace_id`. | Za API tudi `RequestDataTooBig`/`SuspiciousOperation` pretvoriti v JSON 400 ali 413; dodati negativni test. |
| R-04 | nizka (test) | `p0/registry/tests/test_varovala.py:76-92` (`test_premaknjen_zacetek_granta`) | Test premakne samo `grants`, a nespremenjena vrstica `relationships` po ročnem odvzemu povezave že sproži `manual_restriction`. Test zato ne preizkusi varovala za grant in ostane zelen tudi, ko grant varovalo odstranimo. | Z začasno onemogočenim grantom varovalom (`_manual_revocation_at` vrne `None` za `entity_type == "grant"`) `test_premaknjen_zacetek_granta` ostane `ok`; `test_odvzem_enega_dovoljenja_ne_vpliva_na_drugega` v istih pogojih pade (`manual_restriction` manjka). | V testu odstraniti/ zaključiti vrstico povezave ali uporabiti svež vir; dodati ločen test, ki preveri konflikt prav za vrstico granta. |
| R-05 | nizka (dostopnost) | `p0/templates/base.html:56` (`dl.facts`), `p0/templates/evidenca/oseba.html` | Pri 320 px se stran osebe preliva za 5 px. Vzrok je `dl.facts` z `grid-template-columns: max-content 1fr`; `dd` z e-naslovom se ne more skrčiti. Merilo ročnega pregleda zahteva brez vodoravnega drsenja pri 320 px. | Headless Chrome 157, CDP `Emulation.setDeviceMetricsOverride` 320×900: `innerWidth=320`, `document.documentElement.scrollWidth=325`; `dd` z `family01@example.invalid` ima `right=325.2`. Pri 375 px prelivanja ni. | `dd { min-width: 0; overflow-wrap: anywhere; }` oziroma enostolpčna postavitev `dl` na ozkem zaslonu; dodati avtomatski preizkus 320 px in vnos v ročni pregled. |
| R-06 | nizka (UI) | `p0/registry/ui.py:74-80` (`_grant_state`), `p0/templates/evidenca/oseba.html` | Prihodnja povezava ali upravičenje (`valid_from` v prihodnosti) je prikazano kot „zaključena“/„zaključeno“, čeprav se še ni začelo. | Ustvariti povezavo z `valid_from = now + 30 dni`; `GET /p0/evidenca/osebe/<id>/` prikaže „od 12. 12. 2026“ in „zaključena“. | Uvesti tri stanja: „še ne velja“ (`valid_from > now`), „veljavna“, „zaključena“; enako za grant; dodati test. |
| R-07 | nizka (razvoj) | Razvojna slika `odprta-sola-p0:latest` (`INSTALL_DEV=1`); osnovna slika prinaša `setuptools 70.3.0` | Trivy v razvojni sliki najde 3 opozorila `setuptools`: CVE-2025-47273 (visoka, popravek 78.1.1), CVE-2026-59890 (srednja, 83.0.0) in GHSA-xmj3-9gf7-h52w (nizka, 84.1.0). Produkcijska slika (`INSTALL_DEV=0`) teh paketov ne vsebuje in je čista; dokumentacija skenira le produkcijsko sliko. | `trivy image odprta-sola-p0:latest` -> 205 Debian + 3 Python; `odprta-sola-p0-prod:review` -> 205 Debian + 0 Python. | `setuptools` odstraniti iz razvojne slike ali ga zakleniti/posodobiti; v dokumentacijo dodati rezultat za razvojno sliko in po možnosti skeniranje v CI. |

### Dokumentacija: trditve, ki jih koda ali ukazi ne podpirajo

- Ena trditev v `DEVELOPER.md` o hrambi začasnih datotek ni podprta s kodo; podrobnosti so v zasebni R-01 in niso v tem javnem poročilu.
- `DEVELOPER.md:68` pravi, da so napake na poteh API vedno JSON; preveliko telo vrne 400 HTML (R-03).
- `DEVELOPER.md:106` pravi, da predogled hrani „samo imena spremenjenih polj“; `ImportPreview` hrani tudi `entity_type`, `source_key` in `action`, `ImportBatch` pa vir in `problems`.
- Zapis o odpravi označi P0-07 kot „popravljeno“; en nov test je lažno zelen (R-04), zato je v tem poročilu stanje **delno**.
- Zapis o odpravi označi P0-09 kot „popravljeno“; poleg zgornjih ostajajo manjše neusklajenosti, zato **delno**.
- Pregled dostopnosti navaja 375 px (tam prelivanja ni); ročni kontrolni seznam zahteva 320 px, kjer stran osebe preliva 5 px (R-05).
- Tabela pripetih Actions v `odvisnosti-in-licence.md` navaja `actions/checkout` v4.4.0; workflow `docs-links.yml` uporablja v6 (`d23441a…`). Obe sta pripeti, popis pa ni popoln.

## 5. Rezultat preizkusa testov (točka 3)

### 5.1 Osnovni zagon

```text
docker compose exec -T p0 python manage.py test
Found 173 test(s)
Ran 173 tests in 15.286s
OK (skipped=2)
```

Preskočena sta podtesta `core.tests.test_boundaries.ModuleBoundaryTests.test_moduli_ne_uvazajo_tujih_modelov` za `m1` in `m2`, ker mapi modulov še ne obstajata; izpis: `skipped 'Modul m1 še ne obstaja: meja ni preverjena.'` oziroma enako za `m2`.

Po `docker compose down -v`, ponovnem `up -d`, `seed_test_data` z novim naključnim `SEED_PASSWORD` in ponovni namestitvi:

```text
python manage.py test registry.tests.test_contract registry.tests.test_robni registry.tests.test_zasloni
Ran 98 tests in 6.198s
OK
```

Posamezni moduli: `test_contract` 44/44, `test_robni` 29/29, `test_zasloni` 25/25, `test_varovala` 21/21, `test_dostopnost` 8/8, `test_import` 22/22, `test_api` 10/10, `test_model` 10/10.

```text
ruff check .                         All checks passed!
ruff format --check .                52 files already formatted
python manage.py makemigrations --check --dry-run   No changes detected
python manage.py check               System check identified no issues (0 silenced).
python3 scripts/check_docs_links.py  Notranje povezave in sidra so veljavni.
DJANGO_DEBUG=0 STUBS=m1 python manage.py check
  django.core.exceptions.ImproperlyConfigured: STUBS je dovoljen samo z DJANGO_DEBUG=1
DJANGO_DEBUG=0 python manage.py check --deploy
  W004 (HSTS), W008 (HTTPS); z dolgo sintetično skrivnostjo brez W009
```

### 5.2 Ali novi testi res padejo ob odstranitvi popravka

Vsa začasna razveljavitev je bila narejena v delovni kopiji in po zagonu povrnjena z `git checkout --`; po poskusih je bil `git diff` prazen.

| Popravek, ki je bil začasno odstranjen | Ukaz | Rezultat |
| --- | --- | --- |
| S-01: `delivery_binding_verified` vedno `False` | `test registry.tests.test_contract.ContactBindingContract` | `Ran 5`, `FAILED (failures=4)`; npr. `200 != 503`, `403 != 503` |
| S-03: zapora `/accounts/password/reset/` | `test registry.tests.test_varovala.PasswordRecoveryTests` | `Ran 6`, `FAILED (failures=6)`; `200 != 404`, `302 != 404` |
| S-04: pravilo `admin`/`office` pri uvozu | `test registry.tests.test_varovala.ImportRoleTests` | `Ran 6`, `FAILED (failures=2)`; `role_not_authorized` manjka |
| P0-01: preverjanje zahtev po shemi | `test registry.tests.test_robni.RequestValidation` | `Ran 6`, `FAILED (failures=112)`; npr. `200 != 400`, `202 != 400` |
| P0-05: vezava uveljavitve na načrt predogleda | `test registry.tests.test_robni.PreviewApplyTests` | `Ran 5`, `FAILED (failures=2)`; `preview_stale` manjka, serija `APPLIED` |
| P0-02: pretvorba napak v `ApiErrorMiddleware` | `test registry.tests.test_robni.ApiErrorContract` | `Ran 7`, `FAILED (failures=1, errors=1)`; 500 HTML oziroma `status ni v pogodbi` |
| P0-06: `format_checker` v `contract_check.py` | `test registry.tests.test_robni.CheckerSelfTest` | `Ran 3`, `FAILED (failures=1)`; `ContractViolation not raised` za `checked_at="not-a-date"` |
| S-02: varovalo za grant (začasno onemogočeno) | `test_premaknjen_zacetek_granta` | **`ok`** — lažno zelen (R-04), ker konflikt sproži nespremenjena vrstica povezave |
| S-02: varovalo za grant (začasno onemogočeno) | `test_odvzem_enega_dovoljenja_ne_vpliva_na_drugega` | `FAILED (failures=1)`; pravo kritje granta je v tem testu |

Zaključek: šest od sedmih preverjenih popravkov ima test, ki ob odstranitvi pade; varovalo za grant je pokrito, a eden od testov, ki naj bi ga pokrival, je lažno zelen. To je R-04, ne trditev, da je popravek odstranjen.

## 6. Devet točk in dvajset skupin

### 6.1 Devet točk kontrolnega seznama

| # | Točka | Stanje | Dokaz in primerjava z zapisom o odpravi |
| --- | --- | --- | --- |
| 1 | Lastni otroci, tuja družina zavrnjena | **izvedeno** | Prava HTTP prijava `parent-03` (302) in `GET /me/relationships` -> samo `Učenec Testni 03`; `authorizations/check` z lastnim sklicem `ALLOWED`, s tujim in ugibanim `NOT_ALLOWED`; tuj `subject_id` -> 403 `subject_not_self`. Zapis o odpravi je imel le avtomatski dokaz; tokrat je ročna ponovitev izvedena. |
| 2 | Skupen kontakt, ločena računa | **izvedeno** | Ločeni prijavi `parent-01` in `parent-02` z istim `family01@example.invalid`; različna `person_id` in imeni; `parent-02` vidi samo otroka 01. Enako kot zapis, le ročno ponovljeno. |
| 3 | Odvzem povezave ali upravičenja | **izvedeno** | `authz.revoke_relationship` za `parent-02`: `/me/relationships` prazen, `authorizations/check` `NOT_ALLOWED`, v `audiences/resolve` osebe ni; kontaktni klic 503 (s simulirano vezavo 403 v testu). Sled ostane. Enako kot zapis, ročno ponovljeno. |
| 4 | CSV brez delnega prepisa, ponovitev, sled | **izvedeno** | `import_csv /data/testni-uvoz --source review2 --actor staff-03`: predogled (+8 oseb, +4 povezave, +4 granti itd.), uveljavitev; ponovni predogled vse `=unchanged`. Pokvarjena datoteka (`student-99`) -> `unknown_student`, serija zavrnjena, število zapisov nespremenjeno (19/9/9). |
| 5 | Omejen servisni kontaktni klic | **ni izpolnjeno** | Klic je do D12 zaprt: veljaven, tuj in neobstoječ vhod -> 503 brez kontakta; brez žetona 401, m2 žeton 403, seja 401. Pravila so testirana, merilo pa ni izpolnjeno; enako kot zapis. |
| 6 | Neodvisen pregled kode | **izvedeno (AI)** | Prebrani vsi glavni moduli, predloge, testi, CI in dokumentacija; odgovori na vprašanja so v tem poročilu. Pregled je opravil AI, ne človek; enako kot zapis. |
| 7 | Pogodbeni testi po ponastavitvi | **izvedeno** | `down -v`, `up -d`, `seed_test_data`, nato `test_contract` + `test_robni` + `test_zasloni`: **98/98 OK**. Enako kot zapis; število se ujema (44+29+25). |
| 8 | Izpad P0, brez zaščitenega dejanja in slepe dostave | **ni izvedeno** | Pravih M1/M2 ni; nadomestka ne kličeta P0 in ne pošiljata. Ločena injekcija napake v P0 ni ta scenarij. Enako kot zapis. |
| 9 | Tipkovnica, fokus, napake, bralnik | **delno, ni izpolnjeno** | Zasloni obstajajo; 8/8 in 25/25 testov; ročno prek CDP: jezik `sl`, en `h1`, ena `main`, oznake, preskok, vrstni red fokusa, 3 px obroba, povzetek napak z fokusom in povezavami. Pri 320 px stran osebe preliva 5 px (R-05). Bralnik zaslona ni bil uporabljen; človeški pregled ostaja. Zapis je imel „ni izpolnjeno“; dodajam 320 px in potrditev fokusa. |

### 6.2 Dvajset skupin preizkusov kratke specifikacije

| # | Scenarij | Stanje | Dokaz oziroma vrzel |
| --- | --- | --- | --- |
| 1 | Dva računa z istim kontaktom | delno | Identiteti, povezave in pravice so preizkušene; odzivi M2 in individualna aktivacija sta pred B. Enako kot zapis. |
| 2 | Druga družina, ugiban ID, tuj sklic | delno | P0 poti zavrnejo tuj/ugiban sklic in ne vrnejo kontaktov; niso preverjene vse osebne/podatkovne poti (npr. prihodnji moduli, admin). Enako kot zapis; DeepSeek prvega kroga je imel „pokrit“. |
| 3 | Zaposleni zunaj oddelka | delno | `AudiencesContract` zavrne predogled; prava objava M1 ne obstaja. Enako. |
| 4 | Učenčev račun in ciljna skupina | ni v obsegu T | Pogojena razširitev; seed ne ustvarja računov učencev. Enako. |
| 5 | Povezava brez granta, nato odvzem | **pokrit** | `test_povezava_sama_ne_podeli_pravice` kliče `authz.check_grant`; odvzem povezave/granta je preverjen v vseh štirih poteh. Enako kot zapis (sprememba 5). |
| 6 | Starejši uvoz po ročni omejitvi | **pokrit** | Varovalo za poslovni obseg; `ImportRestrictionTests` (9/9); konflikt in zavrnitev. Enako kot zapis, z opombo R-04 (en test je lažno zelen, kritje je drugje). |
| 7 | Napačen CSV ali neznana referenca | pokrit | `ValidationTests`, `AtomicityTests`; brez delnega vpisa. Enako. |
| 8 | Ponoven uvoz, dvojnik, manjkajoča vrstica | pokrit | `IdempotencyTests`, validacija dvojnikov, CLI ponovitev; manjkajoča vrstica ne odvzame. Enako. |
| 9 | Aktivacija/obnova pri skupnem predalu | ni v obsegu T | Izrecna dopolnitev pred B; S-03 je začasno zaprta. Enako. |
| 10 | Odjava, CSRF, podtaknjen uporabnik, servis | **pokrit** | `test_odjava_konca_sejo`, `test_seja_brez_csrf_je_json_403`, `test_tuj_subject_id_403`, `test_napacen_zeton_ob_veljavni_seji`, `test_servisni_klic_*`; pogodbene napake. **Razlika:** zapis o odpravi je ohranil „delno“ po poročilu OpenAI; po novih testih ocenjujem „pokrit“ za P0. Delegirana identiteta avtorja je D12 in ni del tega scenarija. |
| 11 | Informativno obvestilo, odprtje, seznanitev | ni v obsegu T | M1. Enako. |
| 12 | Dva otroka, sprememba različice M1 | ni v obsegu T | M1. Enako. |
| 13 | Več namenov, Ne/brez odziva | ni v obsegu T | M2. Enako. |
| 14 | Dva otroka, dva odločevalca | ni v obsegu T | M2. Enako. |
| 15 | Neodobrena/spremenjena različica M2 | ni v obsegu T | M2. Enako. |
| 16 | Sprememba/preklic, zaključen obrazec | ni v obsegu T | M2. Enako. |
| 17 | Izpad M1, izgubljen 202, dvojni ključ | delno | Idempotenca in konflikt sta preizkušena; izpad, izgubljen odgovor in trajna namera niso. Enako. |
| 18 | Opomnik, selektivni preklic, izpad, tihi čas, iztek | delno | Potreba, selektivni preklic in ročno stanje `expired` so preizkušeni; samodejni iztek, tihi čas in izpad niso. Enako. |
| 19 | Negotov SMTP, odvzem med dostavo, obnova | nepokrit | Ni dostave, SMTP predaje ali obnove. Enako. |
| 20 | Sveža namestitev, nadomestki, izvoz, dostopnost | delno | Namestitev in 98 pogodbenih/robnik/zaslonskih testov uspe; izvoz in človeški bralnik nista izvedena, 320 px preliva. Enako, z R-05. |

**Skupaj: 5 pokritih, 6 delnih, 1 nepokrit, 8 zunaj obsega T.** Zapis o odpravi navaja 4/7/1/8; edina razlika je skupina 10, ki jo zaradi novih pogodbenih in identitetnih testov dvigujem iz „delno“ v „pokrit“. Skupine 1, 2, 3, 17, 18 in 20 ostajajo delne; 19 ostaja nepokrita; 4, 9 in 11–16 so zunaj obsega T. Ocene niso prepisane iz zapisa, ampak izvedene iz zgoraj navedenih testov in ročnih preveritev.

### 6.3 Razlike do zapisa o odpravi

- **Točke 1–4:** zapis je imel predvsem avtomatski dokaz; tokrat sem jih ponovil tudi ročno prek HTTP/CLI. Stanje ostaja izvedeno.
- **Točka 9:** zapis je „ni izpolnjeno“; strinjam se, dodajam pa konkretno prelivanje pri 320 px (R-05) in potrditev fokusa/napak prek CDP. Bralnik zaslona ostaja neizveden.
- **P0-07:** zapis „popravljeno“; zaradi lažno zelenega testa R-04 ocenjujem **delno**.
- **P0-09:** zapis „popravljeno“; zaradi R-01/R-03 in trditve o predogledu ocenjujem **delno**.
- **Skupina 10:** zapis „delno“; ocenjujem **pokrit** (razlika je pojasnjena zgoraj).
- **Skupina 6:** ostaja „pokrit“, vendar z opombo, da je eden od testov lažno zelen; kritje je v `test_odvzem_enega_dovoljenja_ne_vpliva_na_drugega`.
- **P0-11:** zapis „delno“; strinjam se, dodajam razvojno sliko z 3 opozorili `setuptools` (R-07), ki jih zapis ne omenja.

## 7. Odvisnosti

**Zaklepi in namestitev.** `p0/requirements.lock`, `requirements-dev.lock` in `requirements-build.lock` vsebujejo točne različice in hashe; gradnja z `--require-hashes` je uspela, `pip check` ni našel zlomljenih odvisnosti. `requirements-build.lock` vsebuje `pip==26.3`; produkcijska slika po namestitvi `pip` odstrani. Googljivi `Dockerfile` uporablja digest osnovne slike, `docker-compose.yml` in CI pa digesta PostgreSQL in Mailpita; Actions so pripete na commit. `docker compose build --no-cache p0` je uspel (z `DOCKER_BUILDKIT=0` zaradi read-only buildx v okolju pregleda).

**`pip-audit` 2.10.1** za vse tri zaklepe:

```text
requirements.lock        No known vulnerabilities found
requirements-dev.lock    No known vulnerabilities found
requirements-build.lock  No known vulnerabilities found
```

**Trivy 0.76.2.** Produkcijska slika P0 (`INSTALL_DEV=0`) ima 205 opozoril Debiana (47 visokih, 74 srednjih, 65 nizkih, 19 neznanih), **nobeno s popravkom**, in **0 paketov Python**; to se ujema z zapisom v `odvisnosti-in-licence.md` (205; 47/74/65/19; brez popravkov; Python 0). Razvojna slika (`INSTALL_DEV=1`) ima dodatna 3 opozorila `setuptools` (1 visoko, 1 srednje, 1 nizko; vsa s popravkom) — R-07; zapis skenira le produkcijsko sliko. PostgreSQL 16.15: 492 zadetkov, 2 kritična, 65 s popravkom (60 `stdlib`, 3 `zlib1g`, 2 Go); ujema se z zapisom (2 kritična, 65 popravljivih, 62 v `gosu`). Mailpit 1.33.1: 2 neznani, oba s popravkom; zapis navaja 2 neznani.

**CI.** `p0.yml` namesti oba zaklepa z `--require-hashes`, preveri `pip check`, usklajenost zaklepov z vhodnimi zahtevami (`pip install --no-index --dry-run`; lokalno 0 vrstic „Would install“), `ruff`, `makemigrations --check`, `check` in celotno zbirko. Ne gradi slike in ne izvaja `pip-audit`/Trivy; dokumentacija tega tudi ne trdi. `docs-links.yml` preveri povezave. Dependabot je nastavljen za Actions in slike, brez večjih različic; paketi Python so ročni.

**Odprto:** SBOM in pravni pregled licenc pred distribucijo slike; HSTS/HTTPS ob odločitvi o gostovanju (D04); celovit popis vgrajenih knjižnic `psycopg-binary`; `CSRF_TRUSTED_ORIGINS`; razvojna slika z `setuptools` (R-07); popis Actions v dokumentaciji ni popoln (v4.4.0 proti v6 v `docs-links.yml`). To ni pravno mnenje in ne potrjuje popolne skladnosti z EUPL 1.2.

## 8. Omejitve pregleda

- Pregled je opravil AI (DeepSeek); Mitja Pirih in neodvisen človek ga v tej izvedbi nista potrdila. Poročilo DeepSeek prvega kroga je napisal isti sistem, zato ponovni pregled ni neodvisen od prvega poročila DeepSeek.
- Samo izmišljeni podatki; testno geslo in servisni žetoni so bili naključni in niso v poročilu ali repozitoriju. Po koncu je `docker compose down -v` odstranil vsebnike in volumen.
- Meritev je na `127f1d5`; koda P0 je med `184c8f9` in `127f1d5` nespremenjena, spremenita se le dokumentacija in `.github/dependabot.yml`.
- `docker compose build --no-cache p0` je prvi poskus ustavil buildx zaradi read-only `~/.docker/buildx`; ponovitev z `DOCKER_BUILDKIT=0` je uspela. To je omejitev okolja, ne izdelka.
- Bralnik zaslona, povečava 200 %/400 %, kontrast z orodjem, glasovno upravljanje in razumljivost z uporabniki **niso** preverjeni. 320 px je izmerjen z headless Chrome 157 prek CDP, ne z bralnikom.
- Dejanski SMTP, prava M1/M2, izpad P0 med dostavo, obnova kopije, trajnost prevzema 202, izgubljen omrežni odgovor in produkcijska namestitev (gunicorn/HTTPS) **niso** izvedeni.
- Nalaganje datoteke v brskalniku (izbira datoteke) ni bilo izvedeno; uvoz je preverjen z Django odjemalcem in ukazom. Velikost, ime in vsebina so preverjeni v kodi in testih, ne z dejanskim izbirnikom datotek.
- Niso izvedeni: celovit SBOM, popis licenc vseh sistemskih/binarnih komponent, fuzzing, obremenitveni preizkus, izčrpen pregled vseh časovnih kanalov, sočasni uvoz z več delavci in obnova po izpadu.
- Niso preverjene vse veje Django admina, prihodnji moduli M1/M2, vsi infrastrukturni dnevniki in pravice prispevkov dijakov (D08).
- Pregled ne potrjuje, da so vse najdene ali nenajdene težave edine; odsotnost zadetka ni dokaz odsotnosti ranljivosti.

## 9. Izjava

Ta pregled **ni človeški prevzem, ni pravno mnenje in ni potrditev D12**. Uspešna izvedba 173 testov in 98 testov po ponastavitvi ni dokaz izpolnitve vseh prevzemnih pogojev. Pregledovalec ne potrjuje produkcijske pripravljenosti, pravic prispevkov dijakov ali sprejema poročila v imenu Mitje Piriha. Odločitev o prevzemu T sprejme pobudnik; to poročilo je dokaz zanjo, ne sam sprejem.
