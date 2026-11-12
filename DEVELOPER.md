# Navodila za razvijalce

Status: osnutek, faza 2 (ogrodje in podatkovni model P0). Prijava, API in uvoz sledijo po [načrtu priprave P0](docs/projekt/priprava-referencnega-P0.md). Za pravila dela glej [CONTRIBUTING.md](CONTRIBUTING.md).

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
