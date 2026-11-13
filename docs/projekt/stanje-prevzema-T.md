# Stanje paketa T (referenčni P0)

Datum: 12. november 2026. Status: pregled dejanskega stanja proti [načrtu priprave P0](priprava-referencnega-P0.md) po prvem neodvisnem pregledu. Izvedba faz 0 do 6 je v `main` (PR #31 do #38). Prvi pregled sta opravila druga sistema AI, Codex (OpenAI) in DeepSeek (PR #39, #40); poročil človek še ni sprejel. Odprava ugotovitev je v [zapisu o odpravi](../pregledi/2026-11-odprava-prvega-pregleda-P0.md); po njej je potreben ponovni neodvisni pregled. Človeški prevzem ni opravljen.

## Kaj je narejeno in preizkušeno

| Zahteva iz načrta (prvi prevzem) | Stanje |
| --- | --- |
| Ena izmišljena šola, osebe, učenci, oddelki, povezave, dodelitve, dovoljenja | Narejeno (`registry`, `seed_test_data`) |
| Lokalna prijava z vzdrževano rešitvijo | Narejeno (`django-allauth`, prijava z uporabniškim imenom, brez samoregistracije) |
| Preverjanje uporabniških in servisnih pravic | Narejeno (`authz.py`, `authorizations/check`, servisni žetoni) |
| Odvzem povezave in dovoljenja | Narejeno v logiki, testih in na zaslonu `/p0/evidenca/osebe/` |
| Osnovni CSV uvoz s predogledom, validacijo, celovito potrditvijo, ponovitvijo | Narejeno (ukaz `import_csv` in zaslon `/p0/evidenca/uvoz/`) |
| Sprememba kontakta (sledljiva) | Prek uvoza (`person.import_updated`) in zaslona (`person.contact_updated`); vir resnice je uvoz (odločitev 12. 11. 2026) |
| Omejen kontaktni klic | Narejeno: kontakt samo za prejemnika iz posnetka občinstva z aktualnim upravičenjem za namen (D12, C07; sprejeto 13. 11. 2026) |
| API, testni podatki, ponovljiva namestitev | Narejeno; testi so bili izmerjeni na določenem commitu (glej zapis o odpravi), gradnja brez predpomnilnika izvedena (zapisa o odpravi) |
| Nadomestka M1/M2 in pogodbeni testi | Narejeno kot osnutek pogodbe D12 (`api/openapi.yaml`, `p0/stubs`); nadomestka ne dokazujeta vedenjske zamenljivosti (glej spodaj) |

## Kar manjka do prevzema T

| Vrzel | Posledica |
| --- | --- |
| Neodvisni pregled (9 točk, [kontrolni seznam](pregled-P0-kontrolni-seznam.md)) | Prvi in ponovni pregled z dvema sistemoma AI izvedena (priporočilo obakrat: ne oziroma pogojno); odprava ponovnega pregleda je v [zapisu](../pregledi/2026-11-odprava-ponovnega-pregleda-P0.md); tretji pregled ni izveden |
| Zasebne varnostne ugotovitve | Šest ugotovitev obeh krogov odpravljenih in objavljenih kot varnostni nasveti repozitorija |
| Pogodba proti izvedbi (vhod, napake, formati) | Popravljeno za preizkušene poti; omejitve dolžin in splošne napake so predlog D12 |
| Zaklep odvisnosti s hashi, določene slike, popis licenc slike, HSTS/HTTPS | Zaklep, digesti in skeniranje narejeni; popis licenc delen (brez vgrajenih knjižnic psycopg-binary in SBOM); HSTS/HTTPS čaka na namestitev ([odvisnosti in licence](odvisnosti-in-licence.md)) |
| Točka 8: obnašanje modulov ob izpadu P0 | Nepreverljivo, dokler pravi M1/M2 ne obstajata |
| Točka 9: zasloni in dostopnost | Prijava in odjava imata dostopni predlogi z avtomatskimi preizkusi; ročni pregled z bralnikom ni narejen; zasloni za osnovna opravila (obseg sprejet 12. 11. 2026) so narejeni in preizkušeni s tipkovnico, ne z bralnikom ([pregled dostopnosti](pregled-dostopnosti-P0.md)) |
| Potrditev D12 (sheme, šifranti, servisni mehanizem, topologija) | Pogodba je osnutek; ekipe se ne smejo vezati nanjo |
| Potrditev strukture `p0/m1`, `p0/m2` in imen dovoljenj | Predlogi, ne odločitve (`django-allauth` potrjen 12. 11. 2026) |
| Drugi skrbnik/namestnik (D09), namestnik in roki D14 | Pogoj za vključitev dijakov ([register](odlocitve.md)) |
| Pravice prispevkov dijakov (D08), izjave | Pred sprejemom dijaške kode |
| Imenovanje pregledovalca ter potrditev, da pregled z drugim AI zadošča | Pobudnikova osebna odločitev; formalna enakovrednost človeškemu pregledu ni potrjena |

## Pred B (ne za prvi prevzem T)

Individualna aktivacija in obnova gesla pri skupnem predalu (samopostrežna obnova je do takrat izklopljena), izvoz in njegov dokumentiran postopek (zasloni za osebe, uvoz in popravek kontakta so narejeni za T), politika popolne uskladitve uvoza, računi učencev (predlog D01/D06/D07/D16).

## Znane omejitve nadomestkov in pogodbe

Nadomestka po točkah B (13. 11. 2026) hranita stanje v bazi (`p0/stubs/models.py`) in preizkušata: trajni zapis pred 202 in izpad zapisa, okno ponovitve 30 dni, poslovni ključ dogodka, `need_ref` na postavko, ponovno presojo ob obdelavi (odvzem, kontakt, potreba, jezik), osnutek urnika z iztekom in poletnim časom ter negotovo predajo (`registry/tests/test_d12_tocke_b.py`). Niso preizkušeni: prava pošta in ponovni poskusi SMTP, prazniki in urnik šole, periodični razporejevalnik (obdelavo sproži pomožna pot `_stub/process`), sočasni klici pri pravem M1, nadomestni jezik (D05). Nadomestek M1 kliče P0 in M2 v istem procesu prek istih funkcij kot njuna API; pravi M1 kliče API.

Odločitve D12, točke A (sprejel tehnični nosilec 12. 11. 2026; D12 kot celoto sprejel naročnik 13. 11. 2026, pogodba `1.0.0`): predogled občinstva z avtorjevo sejo in shranjen posnetek; kontakt vezan na posnetek in namen; postavka dostave (person_id, scope_ref) z `item_id`; meje dolžin in splošne napake 404/405/500/503. Ponovitev že prevzete zahteve po `expires_at` vrne isti prevzem. Točke B (13. 11. 2026, enako): glej [paket](d12-paket-za-odlocitev.md#b-odločiti-pred-integracijo-mejnik-i).
