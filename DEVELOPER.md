# Navodila za razvijalce

Status: osnutek, 12. november 2026, po popravkih prvega neodvisnega pregleda (ogrodje, model, prijava, API, uvoz CSV, osnutek pogodbe D12 z nadomestkoma M1/M2). Navodila po ekipah sledijo po [načrtu priprave P0](docs/projekt/priprava-referencnega-P0.md). Za pravila dela glej [CONTRIBUTING.md](CONTRIBUTING.md).

## Pravila

- Samo izmišljeni podatki. Gesel, ključev in resničnih izvozov ne dajajte v repozitorij.
- Koda, imena v API-ju in komentarji so v angleščini ali slovenščini po dogovoru modula; dokumentacija je v slovenščini.
- Gesel, sej in kriptografije ne pišemo na novo; uporabimo vzdrževano rešitev, ki jo potrdi skupni tehnični nosilec.
- E-naslov ni identiteta osebe. Dva računa lahko delita naslov.
- Moduli ne berejo tabel drug drugega; komunicirajo prek dokumentiranih vmesnikov.

## Zahteve

Docker z Docker Compose. Za delo brez Dockerja še Python 3.12.

## Zagon (Docker)

```bash
docker compose up --build -d --wait
```

- Aplikacija: http://localhost:8000/p0/api/v1/health
- Prestrezni poštni predal (vsa razvojna e-pošta): http://localhost:8025

## Zagon brez Dockerja za aplikacijo

```bash
docker compose up -d db mail
python3 -m venv .venv && . .venv/bin/activate
python -m pip install --require-hashes -r p0/requirements-build.lock
python -m pip install --require-hashes --no-deps -r p0/requirements-dev.lock
cd p0
export DJANGO_DEBUG=1
python manage.py migrate
python manage.py runserver
```

## Testni podatki

```bash
cd p0 && python manage.py seed_test_data
```

Naloži izmišljeni nabor (staff-01…03, parent-01…04, student-01…04), ponovljivo in idempotentno. Računi imajo neuporabno geslo; za lokalni razvoj ga lahko nastavite z `SEED_PASSWORD` v okolju.

## Model v kratkem

`Account` je prijavni uporabnik (`AUTH_USER_MODEL`), vezan na največ eno `Person`; e-naslov ni enoličen. `Relationship` ne podeli pravic: ta je ločen `Grant` s šolsko `Approval`. Povezave in upravičenja imajo `valid_from`/`valid_until` in se zaključijo, ne brišejo.

## Prijava in API

Prijava: `django-allauth` (samo `allauth.account`), prijava z uporabniškim imenom na `/accounts/login/`, odjava je POST. Samoregistracije ni; račune ustvari pooblaščena oseba. E-naslov ni enoličen in ni identiteta.

Samopostrežna obnova gesla je izklopljena: vse poti pod `/accounts/password/reset/` vrnejo 404, sporočilo se ne pošlje, prijava ne kaže povezave. Razlog: računi lahko delijo e-naslov, zato obnova po naslovu ni individualna. Novo geslo nastavi šola; individualna aktivacija in obnova sta dopolnitev pred B ([načrt](docs/projekt/priprava-referencnega-P0.md)).

Celotna pogodba (P0, M1, M2) je v [api/openapi.yaml](api/openapi.yaml), pojasnila v [pogodbi vmesnikov](docs/arhitektura/vmesnik-P0-M1-M2.md). **Osnutek D12, ni potrjena**; odvisna ekipa se nanjo veže šele po potrditvi.

| Pot P0 | Klicatelj | Pomen |
| --- | --- | --- |
| `GET /me`, `/me/relationships`, `/me/classes` | seja | Lastna oseba, povezave z `scope_ref` in oddelki |
| `POST /authorizations/check` | seja ali servis | `{subject_id?, scope_ref, permission}` -> `{allowed, reason_code, checked_at}` |
| `POST /audiences/resolve` | seja avtorja (CSRF) | `{class_id, purpose}` → predogled prejemnikov oddelka in shranjen posnetek občinstva `audience_ref` (rok 30 dni, predlog); brez kontaktov; avtor je oseba iz seje |
| `POST /delivery-contacts/resolve` | servis (M1) | `{recipient_id, scope_ref, audience_ref}` → kontakt samo za prejemnika iz neizteklega posnetka, z aktualnim upravičenjem za namen posnetka; sicer enak 403 |

`scope_ref` je neprosojen sklic, ki ga izda P0 za par (oseba, obseg); tuj ali ugiban sklic vrne `NOT_ALLOWED`. Šifrant dovoljenj: `m1.confirm`, `m2.decide`.

Zahteve se preverijo proti shemam pogodbe (`registry/contract_schemas.py`, enakost s `api/openapi.yaml` preveri test): manjkajoče ali dodatno polje, napačen tip ali predolg niz je 400. Napake na poteh API so vedno JSON `{code, message, trace_id}`, tudi 400 in 403, ki jih vrne Django (npr. preveliko telo zahteve): 404 neznana pot, 405 napačna metoda (z `Allow`), 403 `csrf_failed` pri sejnem klicu brez CSRF, 503 nedosegljiva evidenca (nikoli `allowed=false`), 500 brez tehničnih podrobnosti (sled je v dnevniku strežnika `p0.api`).

### Servisne identitete in nadomestka M1/M2

Servisni klic uporablja `Authorization: Bearer <žeton>`, nikoli seje. Žeton se hrani zgoščen. Neveljaven žeton je 401 in ne preide na sejo.

```bash
cd p0
python manage.py create_service_client m2 --scope m1.delivery --scope p0.authorizations.check
```

Žeton se izpiše enkrat; ne shranjujte ga v repozitorij. Dovoljenja: `p0.authorizations.check`, `p0.contacts.resolve`, `m1.delivery`, `m2.reminders.check`.

Nadomestka M1 (`/m1/api/v1/`) in M2 (`/m2/api/v1/`) sta v `p0/stubs/` in se vklopita s `STUBS=m1,m2` (samo z `DJANGO_DEBUG=1`, sicer se aplikacija ne zažene; privzeto v razvoju; pravi modul odstrani svoj nadomestek, npr. `STUBS=m2`). Ne pošiljata e-pošte, stanje je v pomnilniku procesa. Za preizkus stanj sta na voljo samo v nadomestkih `POST /m1/api/v1/_stub/advance` in `POST /m2/api/v1/_stub/mark-done`. Ekipa M1 zamenja nadomestek M1 s pravim modulom, ekipa M2 nadomestek M2, z istimi shemami.

Pogodbeni testi (`registry/tests/test_contract.py`, `test_robni.py`) vsak odgovor, ki gre skozi `ContractBase.call`, preverijo proti operaciji v pogodbi (neznana pot API je napaka; izvzeti sta le pomožni poti nadomestkov in `health`) (`registry/tests/contract_check.py`: status, vsebinski tip, shema s formati, pogojne sheme, `counts`). Odgovori, pridobljeni neposredno z Django odjemalcem, niso samodejno preverjeni. Nadomestka dokazujeta le sheme in omejena stanja, ne trajnosti, obnove, izpada ali urnika. Scenariji: tuj sklic, servisni klic brez seje, nepooblaščen kontaktni klic, podvojena zahteva in konflikt ključa, delna stanja, ponovljen in selektivni preklic, iztek, odsoten kontakt.

Pravice se odločajo samo v `registry/authz.py`. Povezava sama ne dovoli dejanja; odvzem povezave ali upravičenja prevlada. Zaščitenih dejanj se ne dovoli na slepo: neznan ali tuj obseg ni nikoli »dovoljeno«.

## Zasloni evidence

Po prijavi vodi `/p0/` na začetno stran. Tajništvo in skrbnik (vlogi `office`, `admin`) imata pod `/p0/evidenca/` zaslone za osebe (iskanje, podrobnosti, odvzem povezave ali upravičenja, popravek kontakta) in uvoz CSV. Odločanje ostane v `authz.py` in `importer.py`; zasloni so le vmesnik (`registry/ui.py`, predloge v `p0/templates/`). Ročni odvzem in popravek kontakta se v sledi zapišeta z virom `zaslon`. Datoteke predogleda uvoza se začasno hranijo v zbirki (`ImportUpload`). Predogled poteče 24 ur po najstarejši datoteki serije: od takrat ga ni mogoče uveljaviti in datoteke se ob dostopu takoj izbrišejo; brez dostopa jih izbriše ukaz `purge_import_uploads`, ki ga v razvoju vsako uro zažene storitev `cleanup` (najpozneje po 25 urah). Ista storitev z ukazom `purge_audience_snapshots` izbriše potekle posnetke občinstva s člani (rok 30 dni je predlog D12/D07; potekel posnetek je neuporaben že ob izteku, izbrisan najpozneje uro pozneje). Za produkcijo mora namestitev (D04) zagotoviti enakovreden razporejevalnik za oba ukaza. Predogled prikaže vse postavke po straneh, s filtrom »samo spremembe«. Odvzem povezave ali upravičenja zaključi vse še veljavne in prihodnje zapise istega poslovnega obsega. Kontakt: vir resnice je uvoz (odločitev 12. 11. 2026); predogled pokaže spremembo `contact_email`, tajništvo popravi tudi izvorni sistem. Dostopnost: [pregled dostopnosti](docs/projekt/pregled-dostopnosti-P0.md).

## Uvoz CSV

Format: mapa z datotekami `classes`, `persons`, `roles`, `students`, `memberships`, `relationships`, `staff_assignments`, `grants` (`.csv`; UTF-8, ločilo `;`, datumi ISO 8601 s časovnim pasom). Primer: [data/testni-uvoz](data/testni-uvoz). Dve stopnji, brez izjem:

```bash
cd p0
python manage.py import_csv ../data/testni-uvoz --source testni --actor UPORABNIK   # predogled
python manage.py import_csv ../data/testni-uvoz --source testni --actor UPORABNIK --apply-batch ID
```

`UPORABNIK` je račun osebe z vlogo `office` ali `admin`; vlogi `admin` in `office` lahko z uvozom na novo dodeli samo uvoznik z vlogo `admin` (ponovni uvoz že dodeljene vloge je dovoljen). Predogled nič ne spremeni; uveljavitev zahteva isto vsebino kot predogled in je vse ali nič. Če se je evidenca od predogleda spremenila tako, da bi uveljavitev izvedla drugačne operacije, je serija zavrnjena (`preview_stale`) in je potreben nov predogled. Serija je med uveljavitvijo zaklenjena; ponovna ali sočasna uveljavitev ne uspe.

- Napaka (neznana referenca, neveljaven datum ali šifrant, podvojen ključ) zavrne celotno serijo.
- Ponovni uvoz ne podvoji oseb; manjkajoča vrstica ne izbriše in ne odvzame ničesar.
- Uvoz ne obnovi povezave ali upravičenja, ki jo je pooblaščena oseba ročno odvzela (`authz.revoke_*` ali zaslon): varovalo velja za poslovni obseg (skrbnik in učenec; oseba, obseg in dovoljenje), ne glede na začetek veljavnosti ali vrsto v CSV. Uvoz, ki bi zapis ustvaril ali podaljšal po odvzemu, je konflikt in serija se zavrne; zgodovinski zapis, ki se konča pred odvzemom, je dovoljen.
- Uvoz in ročni odvzem istega obsega sta usklajena s transakcijsko ključavnico PostgreSQL; sočasni odvzem počaka ali pa uvoz zavrne.
- Meje polj izhajajo iz modelov (npr. `display_name` 200 znakov); izvorni ključi imajo največ 64 znakov. Predolgo polje ali napaka razčlenjevalnika je težava predogleda (`too_long`, `bad_csv`).
- Gesla niso del uvoza. Predogled hrani vrsto zapisa, izvorni ključ, dejanje in imena spremenjenih polj, ne vrednosti; serija hrani vir, števila in opise težav.

Predlog, ki ga mora potrditi D12: datoteka `classes` ni v prvotnem formatu, a oddelki morajo nekje nastati; šifrant dovoljenj je za zdaj `acknowledge`, `decide`; obseg upravičenj je `student:<source_student_key>`. Delni uvoz in popolna uskladitev (zaključki veljavnosti) nista narejena.

## Odvisnosti in slike

Nameščamo samo iz zaklepov s hashi (`p0/requirements*.lock`); slike in GitHub Actions so pripete na digest oziroma commit. Vhodne zahteve so v `p0/requirements*.txt`; po njihovi spremembi zaklepe ustvarite z `pip-compile`. Postopek posodobitve, rezultati skeniranja in popis licenc: [odvisnosti in licence](docs/projekt/odvisnosti-in-licence.md).

## Preverjanja pred pull requestom

Isto teče v CI ([p0.yml](.github/workflows/p0.yml)).

```bash
cd p0
ruff check . && ruff format --check .
python manage.py makemigrations --check --dry-run
python manage.py test
```

## Struktura

| Pot | Vsebina |
| --- | --- |
| `p0/config/` | Nastavitve in usmerjanje; vse skrivnosti iz okolja |
| `p0/core/` | Skupne poti API pod `/p0/api/v1/` |
| `p0/registry/` | Evidenca: osebe, računi, oddelki, povezave, upravičenja, sled sprememb |
| `docker-compose.yml` | Razvojna zbirka PostgreSQL in prestrezni poštni predal |

## Prispevek

Vsak prispevek zabeleži avtorja, izvor predhodne kode, uporabo AI, odvisnosti in obseg človeškega pregleda (glej [CONTRIBUTING.md](CONTRIBUTING.md)). Varnostne težave sporočite zasebno po [SECURITY.md](SECURITY.md).
