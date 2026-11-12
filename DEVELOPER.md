# Navodila za razvijalce

Status: osnutek, faza 5 (ogrodje, model, prijava, API, uvoz CSV, osnutek pogodbe D12 z nadomestkoma M1/M2). Navodila po ekipah sledijo po [načrtu priprave P0](docs/projekt/priprava-referencnega-P0.md). Za pravila dela glej [CONTRIBUTING.md](CONTRIBUTING.md).

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
docker compose up --build
```

- Aplikacija: http://localhost:8000/p0/api/v1/health
- Prestrezni poštni predal (vsa razvojna e-pošta): http://localhost:8025

## Zagon brez Dockerja za aplikacijo

```bash
docker compose up -d db mail
python3 -m venv .venv && . .venv/bin/activate
pip install -r p0/requirements-dev.txt
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

Znana omejitev: aktivacija in obnova gesla za račune s skupnim predalom še nista individualni postopek; to je dopolnitev pred B ([načrt](docs/projekt/priprava-referencnega-P0.md)). V razvoju ne uporabljajte skupnega predala za resnično obnovo.

Celotna pogodba (P0, M1, M2) je v [api/openapi.yaml](api/openapi.yaml), pojasnila v [pogodbi vmesnikov](docs/arhitektura/vmesnik-P0-M1-M2.md). **Osnutek D12, ni potrjena**; odvisna ekipa se nanjo veže šele po potrditvi.

| Pot P0 | Klicatelj | Pomen |
| --- | --- | --- |
| `GET /me`, `/me/relationships`, `/me/classes` | seja | Lastna oseba, povezave z `scope_ref` in oddelki |
| `POST /authorizations/check` | seja ali servis | `{subject_id?, scope_ref, permission}` -> `{allowed, reason_code, checked_at}` |
| `POST /audiences/resolve` | servis | Predogled prejemnikov oddelka za avtorja; brez kontaktov |
| `POST /delivery-contacts/resolve` | servis (M1) | Kontakt za točno prejemnika in veljaven obseg tik pred pošiljanjem |

`scope_ref` je neprosojen sklic, ki ga izda P0 za par (oseba, obseg); tuj ali ugiban sklic vrne `NOT_ALLOWED`. Šifrant dovoljenj: `m1.confirm`, `m2.decide`.

### Servisne identitete in nadomestka M1/M2

Servisni klic uporablja `Authorization: Bearer <žeton>`, nikoli seje. Žeton se hrani zgoščen. Neveljaven žeton je 401 in ne preide na sejo.

```bash
cd p0
python manage.py create_service_client m2 --scope m1.delivery --scope p0.authorizations.check
```

Žeton se izpiše enkrat; ne shranjujte ga v repozitorij. Dovoljenja: `p0.authorizations.check`, `p0.audiences.resolve`, `p0.contacts.resolve`, `m1.delivery`, `m2.reminders.check`.

Nadomestka M1 (`/m1/api/v1/`) in M2 (`/m2/api/v1/`) sta v `p0/stubs/` in se vklopita s `STUBS=m1,m2` (privzeto v razvoju; pravi modul odstrani svoj nadomestek, npr. `STUBS=m2`). Ne pošiljata e-pošte, stanje je v pomnilniku procesa. Za preizkus stanj sta na voljo samo v nadomestkih `POST /m1/api/v1/_stub/advance` in `POST /m2/api/v1/_stub/mark-done`. Ekipa M1 zamenja nadomestek M1 s pravim modulom, ekipa M2 nadomestek M2, z istimi shemami.

Pogodbeni testi (`registry/tests/test_contract.py`) preverjajo vsak odgovor proti shemi in scenarije: tuj sklic, servisni klic brez seje, nepooblaščen kontaktni klic, podvojena zahteva in konflikt ključa, delna stanja, ponovljen in selektivni preklic, iztek, odsoten kontakt.

Pravice se odločajo samo v `registry/authz.py`. Povezava sama ne dovoli dejanja; odvzem povezave ali upravičenja prevlada. Zaščitenih dejanj se ne dovoli na slepo: neznan ali tuj obseg ni nikoli »dovoljeno«.

## Uvoz CSV

Format: mapa z datotekami `classes`, `persons`, `roles`, `students`, `memberships`, `relationships`, `staff_assignments`, `grants` (`.csv`; UTF-8, ločilo `;`, datumi ISO 8601 s časovnim pasom). Primer: [data/testni-uvoz](data/testni-uvoz). Dve stopnji, brez izjem:

```bash
cd p0
python manage.py import_csv ../data/testni-uvoz --source testni --actor UPORABNIK   # predogled
python manage.py import_csv ../data/testni-uvoz --source testni --actor UPORABNIK --apply-batch ID
```

`UPORABNIK` je račun osebe z vlogo `office` ali `admin`. Predogled nič ne spremeni; uveljavitev zahteva isto vsebino kot predogled in je vse ali nič.

- Napaka (neznana referenca, neveljaven datum ali šifrant, podvojen ključ) zavrne celotno serijo.
- Ponovni uvoz ne podvoji oseb; manjkajoča vrstica ne izbriše in ne odvzame ničesar.
- Starejši uvoz ne obnovi povezave ali upravičenja, ki jo je pooblaščena oseba ročno odvzela (`authz.revoke_*`): to je konflikt in serija se zavrne.
- Gesla niso del uvoza. Predogled hrani samo imena spremenjenih polj.

Predlog, ki ga mora potrditi D12: datoteka `classes` ni v prvotnem formatu, a oddelki morajo nekje nastati; šifrant dovoljenj je za zdaj `acknowledge`, `decide`; obseg upravičenj je `student:<source_student_key>`. Delni uvoz in popolna uskladitev (zaključki veljavnosti) nista narejena.

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
