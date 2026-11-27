# Odvisnosti, slike, posodobitve in licence P0

Status: osnutek, 12. november 2026 (P0-11 prvega neodvisnega pregleda). Tehnični popis in omejena presoja, **ne pravno mnenje** in ne trditev o popolni skladnosti distribucije slike z EUPL 1.2. Licenca projekta ostaja EUPL 1.2 ([LICENSE](../../LICENSE)).

## Zaklep

| Datoteka | Namen | Ureja |
| --- | --- | --- |
| `p0/requirements.txt`, `requirements-dev.txt`, `requirements-build.txt` | Vhodne zahteve (razponi) | človek |
| `p0/requirements.lock` | Aplikacija: točne različice in hashi vseh paketov (tudi posrednih) | `pip-compile` |
| `p0/requirements-dev.lock` | Razvoj in CI; vezan na `requirements.lock` (`-c`) | `pip-compile` |
| `p0/requirements-build.lock` | `pip` za namestitev v sliki | `pip-compile --allow-unsafe` |

Slika in CI nameščata samo iz zaklepov z `--require-hashes` (posredne odvisnosti so v zaklepu, zato `--no-deps`), nato `pip check`. CI preveri, da zaklep izpolnjuje vhodne zahteve (`pip install --no-index --dry-run`). Produkcijska slika po namestitvi odstrani `pip`.

Pripete reference:

| Komponenta | Referenca |
| --- | --- |
| Osnovna slika P0 | `python:3.12-slim@sha256:191083cdf6c7bda8c76158983163ead5d5cf7b77cf3033e805bb0f5296f51b4b` (Python 3.12.16, Debian 13.8) |
| Popravki Debiana v sliki | `libzstd1=1.5.7+dfsg-1+deb13u1`, `passwd` in `login.defs=1:4.17.4-2+deb13u1` (dokler jih osnovna slika nima) |
| PostgreSQL (razvoj, CI) | `postgres:16@sha256:ce81150802644ddfac1db4da9e63be6f2a3818aa6ee98a7a28838aeea65dc37a` (16.16) |
| Mailpit (razvoj) | `axllent/mailpit:v1.34.0@sha256:23a2ef85bc50853ab3093645d1d64679afd8887e89da5e48a88940c172591a4e` |
| GitHub Actions | `p0.yml`: `actions/checkout@11d5960a…` (v4.4.0), `actions/setup-python@a26af69b…` (v5.6.0), Python 3.12.16; `docs-links.yml`: `actions/checkout@d23441a4…` (v6) |

## Postopek posodobitve

Najmanj mesečno in ob objavi varnostnega opozorila za uporabljeno komponento; vsaka posodobitev je ločen pull request s pregledom diffa zaklepa.

1. Python: v osnovni sliki zaženite `pip-compile --generate-hashes --strip-extras --no-emit-index-url` za `requirements.txt`, nato `requirements-dev.txt`, in z `--allow-unsafe` za `requirements-build.txt` (ukazi in izhodne datoteke kot v tabeli zgoraj). Posamezen paket: `--upgrade-package IME`.
2. Slike: `docker pull` oznake, `docker inspect --format '{{index .RepoDigests 0}}'`, zamenjajte digest v `p0/Dockerfile`, `docker-compose.yml` in `.github/workflows/p0.yml`; preverite različice (`python --version`, `postgres --version`, `mailpit version`). Ko nova osnovna slika vsebuje popravljene pakete iz koraka `apt-get` v Dockerfile, ta korak odstranite.
3. Actions: oznako razrešite v commit (`gh api repos/<repo>/commits/<oznaka>`) in pripnite SHA z oznako v komentarju.
4. Preverite: gradnja brez predpomnilnika, celotna zbirka testov, `pip-audit` za vse tri zaklepe, Trivy za sliko P0; rezultate zapišite v pull request.
5. Licence: ob novem ali zamenjanem paketu dopolnite popis spodaj.

Dependabot (`.github/dependabot.yml`) mesečno odpre pull requeste za GitHub Actions in slike (Dockerfile, Compose), vendar le znotraj iste večje različice (za osnovno sliko Python znotraj iste manjše različice, npr. 3.12.x; za PostgreSQL znotraj 16.x). Nadgradnjo Pythona, PostgreSQL ali večje različice Actions pripravimo ročno v ločenem PR s pregledom. Paketi Python ostanejo ročni postopek zgoraj, dokler Dependabot z zaklepi s hashi ni preizkušen.

## Skeniranje 12. 11. 2026

Orodji: `pip-audit` 2.10.1 (baza PyPI/OSV), Trivy 0.76.2 (`aquasec/trivy@sha256:8f6bb947…`). Sliki P0 sta zgrajeni brez predpomnilnika; sliki PostgreSQL in Mailpit sta skenirani kot izvoženi arhivi.

| Cilj | Rezultat |
| --- | --- |
| `requirements.lock`, `requirements-dev.lock`, `requirements-build.lock` (pip-audit) | brez znanih ranljivosti |
| `pip` 25.0.1 v osnovni sliki (pred posodobitvijo) | 6 različnih opozoril (12 zapisov z dvojniki); vsa odpravljena v zaklenjenem pip 26.3; v produkcijski sliki pip ni nameščen |
| Produkcijska slika P0 (Trivy) | paketi Python: 0; Debian: 205 opozoril (47 visokih, 74 srednjih, 65 nizkih, 19 neznanih; ponovitev 13. 11. 2026 s svežo bazo: 47/89/65/4, ista skupna številka), **nobeno nima popravka v Debianu** (stanje `affected` ali `fix_deferred`); največ v `util-linux` in `libsqlite3-0` |
| PostgreSQL 16.15 (Trivy, samo razvoj in CI) | 2 kritični: `libxml2` (brez popravka v Debianu) in `gosu`, zgrajen s starejšo standardno knjižnico Go (popravljivo le z novo sliko); 65 popravljivih opozoril, od tega 62 v `gosu` |
| Mailpit 1.33.1 (Trivy, samo razvoj) | 2 opozorili neznane resnosti v binarni datoteki Go |

Presoja uporabnosti: preostalih opozoril sistemskih paketov ni mogoče odpraviti brez novih paketov Debiana; P0 ne izvaja `util-linux` ali `login` med delovanjem, SQLite ne uporablja. Opozorila `pip` (vgrajen `pkg_resources` iz setuptools 70.3.0) produkcijske slike ne zadevajo več. Sliki PostgreSQL in Mailpit nista del produkcijske namestitve; ta še ni določena (D04). To ni dokaz neizkoristljivosti.

Razvojna slika (`INSTALL_DEV=1`) obdrži pip 26.3, ki ima vgrajen `pkg_resources` iz setuptools 70.3.0; Trivy zato v njej prijavi tri opozorila setuptools (ponovni pregled DeepSeek). Zadevajo `package_index`, gradnjo sdist in poti v Windows, ki jih `pkg_resources` ne uporablja; produkcijska slika pip nima. Opomba, ne ugotovitev.

Ni preverjeno: knjižnice, ki jih prinaša `psycopg-binary` (`psycopg_binary.libs`: libpq, OpenSSL, Kerberos, OpenLDAP, Cyrus SASL, libcrypt, keyutils, com_err), ker jih Trivy kot nepaketirane datoteke ne prepozna zanesljivo; njihove različice niso popisane.

## Posodobitev 27. 11. 2026

`pip-audit` 2.10.1 za vse tri zaklepe: brez znanih ranljivosti; paketi Python niso spremenjeni (Django 5.2.19 je zadnja izdaja 5.2 LTS). Posodobljene so slike: osnovna `python:3.12-slim` (Debian 13.8; vsebuje popravljeni `zlib1g`, zato je ta korak odstranjen), PostgreSQL 16.16 in Mailpit 1.34.0. Trivy 0.76.2 za produkcijsko sliko P0 (sveža baza, isti dan):

| Slika | Visoke | Srednje | Nizke | Neznane | Skupaj | S popravkom |
| --- | --- | --- | --- | --- | --- | --- |
| Prejšnja (`main` pred posodobitvijo) | 54 | 105 | 79 | 15 | 253 | 31 |
| Nova osnovna slika | 54 | 79 | 77 | 15 | 225 | 3 |
| Nova + popravki Debiana v Dockerfile | 53 | 79 | 77 | 13 | 222 | 0 |

Paketi Python v produkcijski sliki: 0 zadetkov. Preostala opozorila nimajo popravka v Debianu.

## Licence

Paketi Python v produkcijski sliki (iz metapodatkov paketov):

| Paket | Različica | Licenca |
| --- | --- | --- |
| Django | 5.2.19 | BSD-3-Clause |
| asgiref | 3.13.0 | BSD-3-Clause |
| sqlparse | 0.6.1 | BSD-3-Clause |
| django-allauth | 65.22.0 | MIT |
| gunicorn | 27.0.0 | MIT |
| psycopg, psycopg-binary | 3.3.9 | LGPL-3.0-only |
| typing_extensions | 4.16.0 | PSF-2.0 |

Samo razvoj in CI: ruff 0.17.4, jsonschema 4.26.0, jsonschema-specifications 2025.9.1, referencing 0.37.0, rpds-py 2026.9.1, attrs 26.1.0 (MIT), PyYAML 6.0.3 (MIT), rfc3339-validator 0.1.4 (MIT), six 1.17.0 (MIT); orodje pip 26.3 (MIT).

`psycopg-binary` vključuje binarne knjižnice z lastnimi licencami (med njimi PostgreSQL License, Apache-2.0 za OpenSSL 3, MIT za Kerberos, OpenLDAP Public License, licenco Cyrus SASL, LGPL za libcrypt in keyutils); točne različice in besedila niso popisani. Pri distribuciji je treba izpolniti obveznosti LGPL (besedilo licence, dostop do izvora, možnost zamenjave knjižnice).

Sistemski paketi v sliki P0: 87 paketov Debiana; Trivy je prepoznal licence za 91 komponent, med njimi copyleft (GPL-2.0/3.0, LGPL; 320 zapisov kategorije `restricted`), permisivne (134 `notice`) in 173 neprepoznanih. Gre za orodja in knjižnice osnovnega sistema, ki se distribuirajo kot ločena dela v sliki; obveznosti GPL (izvor, besedila v `/usr/share/doc/*/copyright`) veljajo, če se slika distribuira tretjim.

Ocena za EUPL 1.2: pri permisivnih licencah ni prepoznane ovire; LGPL-3.0 je v prilogi EUPL med združljivimi licencami, kar ne pomeni prelicenciranja knjižnice. **Popolna skladnost distribucije slike ni potrjena**: manjkata popis točnih različic vgrajenih binarnih knjižnic in ponudba izvorov za sistemske pakete. Pred distribucijo slike šoli je potreben SBOM (npr. `trivy image --format cyclonedx`) in pravni pregled. Dokumentacija je pod CC BY-SA 4.0 (D15, osebni sprejem pobudnika 12. 11. 2026); potrditev sodelujočih zavodov je ločena.
