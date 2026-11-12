# Navodila za razvijalce

Status: osnutek, faza 4 (ogrodje, model, prijava, API in uvoz CSV P0). Pogodbe M1/M2 (D12) sledijo po [načrtu priprave P0](docs/projekt/priprava-referencnega-P0.md). Za pravila dela glej [CONTRIBUTING.md](CONTRIBUTING.md).

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

| Pot | Pomen |
| --- | --- |
| `GET /p0/api/v1/me` | Lastna oseba iz seje |
| `GET /p0/api/v1/me/relationships` | Lastne veljavne povezave |
| `GET /p0/api/v1/me/classes` | Dodeljeni oddelki zaposlenega |
| `POST /p0/api/v1/authorizations/check` | Telo `{"scope_key", "permission"}`; preveri lastno aktualno upravičenje, odgovor `{"allowed", "reason"}` |

Pravice se odločajo samo v `registry/authz.py`. Povezava sama ne dovoli dejanja; odvzem povezave ali upravičenja prevlada. Preverjanje za drugo osebo in servisna identiteta še nista narejena (D12). Poti še niso zapisane v OpenAPI.

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
