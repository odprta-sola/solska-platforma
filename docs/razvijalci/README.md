# Navodila za razvijalce modulov M1 in M2

Status: navodila za izvajalce (mentorji in ekipe), 13. november 2026, po pogodbi `1.0.0`. Navodila pojasnjujejo, kaj ekipa dobi in kaj izdela; ne spreminjajo obsega iz [razvojnega naročila](../projekt/razvojno-narocilo-P0-M1-M2.md). Pogodba D12 je sprejeta in zamrznjena kot `1.0.0` (oznaka `v1.0.0`); predloge sprememb oddajte v issueju ali pull requestu, odloči naročnik ([vloge](../projekt/odlocitve.md#vloge-naročnik-in-izvajalec-13-novembra-2026)).

## Pred prvo vrstico kode

1. Preberite [predstavitev](../mentorji/predstavitev-projekta.md) in [kratko specifikacijo](../arhitektura/kratka-specifikacija-P0-M1-M2.md) (20 skupin preizkusov).
2. Namestite razvojno okolje po [DEVELOPER.md](../../DEVELOPER.md) in poženite teste. Če ne gredo skozi, ne začnite z delom.
3. Preglejte [api/openapi.yaml](../../api/openapi.yaml) in poženite `registry/tests/test_contract.py`: ti testi so primer, kako se preverja pogodba.
4. Z mentorjem potrdite svoj samostojni izdelek ([M1](ekipa-M1.md), [M2](ekipa-M2.md)). Vsak dijak mora imeti razpoznaven izdelek in prispevek.

## Kaj dobite pripravljeno

| Del | Kje | Opomba |
| --- | --- | --- |
| P0: osebe, računi, prijava, povezave, upravičenja | `p0/registry`, `/p0/api/v1/` | Prevzem T še ni opravljen ([stanje](../projekt/stanje-prevzema-T.md)) |
| Uvoz CSV in izmišljeni nabor | `data/testni-uvoz`, `seed_test_data` | Samo izmišljeni podatki |
| Pogodba in sheme | `api/openapi.yaml` | Različica `1.0.0`, zamrznjena (`api/zamrznitve.txt`) |
| Nadomestka M1 in M2 | `p0/stubs` | Referenca obnašanja po pogodbi; ne pošiljata pošte, stanje v bazi; obdelavo sproži `_stub/process` |
| Ogrodje modula | `p0/m1`, `p0/m2` | Aplikacija Django z začetnim zaslonom, praznim API in odjemalcem za P0 in sosednji modul |
| Odjemalec API | `p0/core/api_client.py`, `core/testing.py` | Servisni in uporabniški klic, napake; testni prenos brez omrežja |
| Pogodbeni testi | `registry/tests/test_contract.py` | Vzorec za svoje teste |
| Prestrezni poštni predal | http://localhost:8025 | Vsa razvojna e-pošta |

## Kaj mora veljati za vsako ekipo

- **Samo izmišljeni podatki.** Brez resničnih oseb, naslovov, izvozov, gesel in ključev v repozitoriju, issue-jih in pull requestih.
- **Meje modulov.** Koda M1 živi v `p0/m1/`, koda M2 v `p0/m2/` (D12, C05: ena namestitev, ločene aplikacije in tabele, klici samo prek API, tudi znotraj procesa). Modul ne uvaža `registry` ali tujega modula in ne bere tujih tabel. Podatke o osebah in pravice dobi prek API-ja P0, drugi modul pokliče prek njegovega API-ja. Test `core/tests/test_boundaries.py` to preverja za mapi `m1` in `m2` in pade ob prepovedanem uvozu.
- **Pravice se vedno preverijo.** Za vsak zaščiten vpogled, oddajo in dostavo pokličite `POST /p0/api/v1/authorizations/check`. Če P0 ni dosegljiv, dejanja ne dovolite (ne »dovoli« in ne »nepotrebno«).
- **Odprtje ni potrditev, potrditev ni soglasje, predaja strežniku ni prejem.** Ločeni podatki, ločeni dogodki.
- **Brez gesel in kriptografije po svoje.** Prijava je `django-allauth` v P0.
- **Pogodbe ne spreminjate sami.** Spremembo `api/openapi.yaml` predlagate z issue-jem ali pull requestom; odloči naročnik, druga ekipa je obveščena. Vsaka sprememba zahteva novo različico (test `test_pogodba_je_zamrznjena_razlicica`).
- **Skupni P0 spreminjate samo po odobritvi naročnika** (omejena razširitev).

## Struktura modula

| Datoteka | Kaj vsebuje |
| --- | --- |
| `apps.py`, `models.py`, `migrations/` | Aplikacija Django in lastne tabele (samo vaše) |
| `urls.py`, `views.py`, `templates/<modul>/` | Zasloni pod `/m1/` oziroma `/m2/`; začetni zaslon je vzorec (prijava, identiteta iz P0, zavrnitev ob izpadu) |
| `api_urls.py` | Strežniški API po pogodbi pod `/m1/api/v1/` oziroma `/m2/api/v1/`; zdaj prazen |
| `p0_client.py` | Vsi klici v P0 in sosednji modul na enem mestu |
| `tests/` | Vaši testi; `test_zacetek.py` je vzorec s testnim prenosom brez omrežja |

## Povezava z drugimi deli

- **Uporabnik:** prijava je skupna v isti namestitvi (seja P0). Zaslon preveri `request.user.is_authenticated`, nato kliče P0 z `UserSession.from_request(request)`; identiteto vzame iz `GET /p0/api/v1/me`, ne iz tabel P0. Klici s sejo nosijo CSRF.
- **Servis:** servisni klici nosijo žeton modula iz okolja (`M1_SERVICE_TOKEN`, `M2_SERVICE_TOKEN`). Žeton ustvarite lokalno s `create_service_client` (glej [DEVELOPER.md](../../DEVELOPER.md)); ne shranjujte ga v repozitorij.
- **Napake:** `Unavailable` (izpad ali 5xx) pomeni zavrni dejanje oziroma zadrži dostavo. `ApiError` nosi status in kodo iz pogodbe.
- **Nadomestek in pravi modul:** dokler pravi sosednji modul ne obstaja, delate proti nadomestku. Ko je vaš API pripravljen, izklopite svoj nadomestek z `STUBS` (npr. `STUBS=m2`, če je M1 pravi). `/m1/api/v1/` se takrat usmeri v `m1/api_urls.py`. Pogodbeni testi morajo ostati zeleni.
- **Strežnik:** modul v isti namestitvi kliče P0 po HTTP (`P0_API_URL`), zato strežnik potrebuje več niti ali procesov (razvojni `runserver` jih ima).

## Kdaj je prispevek končan

- [ ] Ustreza pogodbi `1.0.0` in shemam; pogodbeni testi zeleni, tudi z izklopljenim lastnim nadomestkom.
- [ ] Testi za vaš obseg, vključno z zavrnitvami (tuja družina, brez pravice, izpad P0).
- [ ] `ruff check`, `ruff format --check`, `makemigrations --check` in `manage.py test` brez napak.
- [ ] Zasloni delujejo s tipkovnico, imajo viden fokus, označena polja in razumljive napake.
- [ ] Brez osebnih podatkov v dnevnikih in sporočilih napak.
- [ ] Dokumentacija: kako zagnati, kaj deluje, kaj ne.
- [ ] Zapis prispevka (spodaj) v opisu pull requesta.
- [ ] Človeški pregled pred združitvijo; AI pregled ga ne nadomesti.

## Zapis prispevka

Vsak pull request navede: avtorja, izvor predhodne kode, kje in kako je bil uporabljen AI, nove odvisnosti z licencami, obseg človeškega pregleda in samostojni prispevek dijaka. To zahteva [CONTRIBUTING.md](../../CONTRIBUTING.md) in ocena po D08. Dijaki z mentorjem uredijo izjave o pravicah prispevkov; do dogovora koda ne gre v `main` brez nosilca.

## Uporaba AI

Pravila za uporabo AI pri maturitetnem izdelku določi mentor. Ne vnašajte resničnih podatkov v AI orodja. Kodo, ki jo je napisal AI, morate znati razložiti in preizkusiti.
