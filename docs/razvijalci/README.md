# Navodila za razvijalce modulov M1 in M2

Status: osnutek za mentorski pregled, 12. november 2026. Navodila pojasnjujejo, kaj ekipa dobi in kaj izdela; ne spreminjajo obsega iz [razvojnega naročila](../projekt/razvojno-narocilo-P0-M1-M2.md). Pogodba D12 je sprejeta in zamrznjena kot `1.0.0` (naročnik, 13. 11. 2026); predloge sprememb oddajte v issueju ali pull requestu, odloči naročnik.

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
| Pogodba in sheme | `api/openapi.yaml` | Osnutek D12 |
| Nadomestka M1 in M2 | `p0/stubs` | Ne pošiljata pošte; stanje v pomnilniku |
| Pogodbeni testi | `registry/tests/test_contract.py` | Vzorec za svoje teste |
| Prestrezni poštni predal | http://localhost:8025 | Vsa razvojna e-pošta |

## Kaj mora veljati za vsako ekipo

- **Samo izmišljeni podatki.** Brez resničnih oseb, naslovov, izvozov, gesel in ključev v repozitoriju, issue-jih in pull requestih.
- **Meje modulov.** Koda M1 živi v `p0/m1/`, koda M2 v `p0/m2/` (predlog; topologijo potrdi D12). Modul ne uvaža `registry` ali tujega modula in ne bere tujih tabel. Podatke o osebah in pravice dobi prek API-ja P0, drugi modul pokliče prek njegovega API-ja. Test `core/tests/test_boundaries.py` to preverja za mapi `m1` in `m2`.
- **Pravice se vedno preverijo.** Za vsak zaščiten vpogled, oddajo in dostavo pokličite `POST /p0/api/v1/authorizations/check`. Če P0 ni dosegljiv, dejanja ne dovolite (ne »dovoli« in ne »nepotrebno«).
- **Odprtje ni potrditev, potrditev ni soglasje, predaja strežniku ni prejem.** Ločeni podatki, ločeni dogodki.
- **Brez gesel in kriptografije po svoje.** Prijava je `django-allauth` v P0.
- **Pogodbo spreminja skupina.** Nezdružljivo spremembo `api/openapi.yaml` predlagate z issue-jem in jo uskladite z drugo ekipo ter tehničnim nosilcem, ne enostransko.
- **Skupni P0 spreminjate samo po dogovoru** z mentorjem in nosilcem (omejena razširitev).

## Povezava z drugimi deli

Dokler pravi sosednji modul ne obstaja, delate proti nadomestku. Ko je vaš modul pripravljen, izklopite svoj nadomestek z `STUBS` (npr. `STUBS=m2`, če je M1 pravi). Pogodbeni testi morajo ostati zeleni z obema.

Servisni žeton za svoj modul ustvarite lokalno (`create_service_client`, glej [DEVELOPER.md](../../DEVELOPER.md)); žetonov ne shranjujte v repozitorij.

Dostop uporabnika do vašega zaslona (seja, preusmeritev na prijavo, vrnitev) je v D12 še odprt. Do odločitve vso komunikacijo s P0 zberite v eno datoteko (`p0_client.py`), da je zamenjava enostavna.

## Kdaj je prispevek končan

- [ ] Ustreza pogodbi in shemam; pogodbeni testi zeleni.
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
