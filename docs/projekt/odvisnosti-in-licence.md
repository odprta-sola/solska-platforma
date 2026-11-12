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
| Osnovna slika P0 | `python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b` (Python 3.12.16, Debian 13.7) |
| Popravek Debiana v sliki | `zlib1g=1:1.3.dfsg+really1.3.1-1+deb13u1` (dokler ga osnovna slika nima) |
| PostgreSQL (razvoj, CI) | `postgres:16@sha256:f9a7b9ebf6f56201f949db745e47bc423c0f0f8294bafe991cc10bf74b029657` (16.15) |
| Mailpit (razvoj) | `axllent/mailpit:v1.33.1@sha256:aef2aacc11f075ec0fb6874275ee4a421e688e11a96ebb296134d1735c7761ce` |
| GitHub Actions | `actions/checkout@11d5960a…` (v4.4.0), `actions/setup-python@a26af69b…` (v5.6.0); Python 3.12.16 |

## Postopek posodobitve

Najmanj mesečno in ob objavi varnostnega opozorila za uporabljeno komponento; vsaka posodobitev je ločen pull request s pregledom diffa zaklepa.

1. Python: v osnovni sliki zaženite `pip-compile --generate-hashes --strip-extras --no-emit-index-url` za `requirements.txt`, nato `requirements-dev.txt`, in z `--allow-unsafe` za `requirements-build.txt` (ukazi in izhodne datoteke kot v tabeli zgoraj). Posamezen paket: `--upgrade-package IME`.
2. Slike: `docker pull` oznake, `docker inspect --format '{{index .RepoDigests 0}}'`, zamenjajte digest v `p0/Dockerfile`, `docker-compose.yml` in `.github/workflows/p0.yml`; preverite različice (`python --version`, `postgres --version`, `mailpit version`). Ko nova osnovna slika vsebuje popravljeni `zlib1g`, odstranite korak `apt-get` v Dockerfile.
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
| Produkcijska slika P0 (Trivy) | paketi Python: 0; Debian: 205 opozoril (47 visokih, 74 srednjih, 65 nizkih, 19 neznanih), **nobeno nima popravka v Debianu** (stanje `affected` ali `fix_deferred`); največ v `util-linux` in `libsqlite3-0` |
| PostgreSQL 16.15 (Trivy, samo razvoj in CI) | 2 kritični: `libxml2` (brez popravka v Debianu) in `gosu`, zgrajen s starejšo standardno knjižnico Go (popravljivo le z novo sliko); 65 popravljivih opozoril, od tega 62 v `gosu` |
| Mailpit 1.33.1 (Trivy, samo razvoj) | 2 opozorili neznane resnosti v binarni datoteki Go |

Presoja uporabnosti: preostalih opozoril sistemskih paketov ni mogoče odpraviti brez novih paketov Debiana; P0 ne izvaja `util-linux` ali `login` med delovanjem, SQLite ne uporablja. Opozorila `pip` (vgrajen `pkg_resources` iz setuptools 70.3.0) produkcijske slike ne zadevajo več. Sliki PostgreSQL in Mailpit nista del produkcijske namestitve; ta še ni določena (D04). To ni dokaz neizkoristljivosti.

Ni preverjeno: knjižnice, ki jih prinaša `psycopg-binary` (`psycopg_binary.libs`: libpq, OpenSSL, Kerberos, OpenLDAP, Cyrus SASL, libcrypt, keyutils, com_err), ker jih Trivy kot nepaketirane datoteke ne prepozna zanesljivo; njihove različice niso popisane.

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

Ocena za EUPL 1.2: pri permisivnih licencah ni prepoznane ovire; LGPL-3.0 je v prilogi EUPL med združljivimi licencami, kar ne pomeni prelicenciranja knjižnice. **Popolna skladnost distribucije slike ni potrjena**: manjkata popis točnih različic vgrajenih binarnih knjižnic in ponudba izvorov za sistemske pakete. Pred distribucijo slike šoli je potreben SBOM (npr. `trivy image --format cyclonedx`) in pravni pregled. Licenca dokumentacije (D15) ostaja odprta.
