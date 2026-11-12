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
| Sprememba kontakta (sledljiva) | Prek uvoza (`person.import_updated`) in zaslona (`person.contact_updated`); razmerje med ročnim popravkom in poznejšim uvozom ni določeno |
| Omejen kontaktni klic | Začasno zaprto (503) do odločitve D12 o preverljivi vezavi na dostavo; pravila upravičenosti testirana |
| API, testni podatki, ponovljiva namestitev | Narejeno; testi so bili izmerjeni na določenem commitu (glej zapis o odpravi), gradnja brez predpomnilnika ni preverjena |
| Nadomestka M1/M2 in pogodbeni testi | Narejeno kot osnutek pogodbe D12 (`api/openapi.yaml`, `p0/stubs`); nadomestka ne dokazujeta vedenjske zamenljivosti (glej spodaj) |

## Kar manjka do prevzema T

| Vrzel | Posledica |
| --- | --- |
| Neodvisni pregled (9 točk, [kontrolni seznam](pregled-P0-kontrolni-seznam.md)) | Prvi pregled z dvema sistemoma AI izveden (priporočilo: ne oziroma pogojno); ponovni pregled po popravkih ni izveden |
| Zasebne varnostne ugotovitve prvega pregleda | Število in stanje v [zapisu o odpravi](../pregledi/2026-11-odprava-prvega-pregleda-P0.md); objava po SECURITY.md |
| Pogodba proti izvedbi (vhod, napake, formati) | Popravljeno za preizkušene poti; omejitve dolžin in splošne napake so predlog D12 |
| Zaklep odvisnosti s hashi, določene slike, popis licenc slike, HSTS/HTTPS | Zaklep, digesti in skeniranje narejeni; popis licenc delen (brez vgrajenih knjižnic psycopg-binary in SBOM); HSTS/HTTPS čaka na namestitev ([odvisnosti in licence](odvisnosti-in-licence.md)) |
| Točka 8: obnašanje modulov ob izpadu P0 | Nepreverljivo, dokler pravi M1/M2 ne obstajata |
| Točka 9: zasloni in dostopnost | Prijava in odjava imata dostopni predlogi z avtomatskimi preizkusi; ročni pregled z bralnikom ni narejen; zasloni za osnovna opravila (obseg sprejet 12. 11. 2026) so narejeni in preizkušeni s tipkovnico, ne z bralnikom ([pregled dostopnosti](pregled-dostopnosti-P0.md)) |
| Potrditev D12 (sheme, šifranti, servisni mehanizem, topologija) | Pogodba je osnutek; ekipe se ne smejo vezati nanjo |
| Potrditev `django-allauth`, strukture `p0/m1`, `p0/m2` in imen dovoljenj | Predlogi v PR-jih, ne odločitve |
| Drugi skrbnik/namestnik (D09), namestnik in roki D14 | Pogoj za vključitev dijakov ([register](odlocitve.md)) |
| Pravice prispevkov dijakov (D08), izjave | Pred sprejemom dijaške kode |
| Imenovanje pregledovalca ter potrditev, da pregled z drugim AI zadošča | Pobudnikova osebna odločitev; formalna enakovrednost človeškemu pregledu ni potrjena |

## Pred B (ne za prvi prevzem T)

Individualna aktivacija in obnova gesla pri skupnem predalu (samopostrežna obnova je do takrat izklopljena), administrativni zasloni (seznam oseb, uvoz, popravki, izvoz), dokumentiran izvoz, politika popolne uskladitve uvoza, računi učencev (predlog D01/D06/D07/D16).

## Znane omejitve nadomestkov in pogodbe

Stanje nadomestka M1 je v pomnilniku procesa. Niso preizkušeni: tihi čas, obnova po izpadu, trajni zapis pred 202, samodejni iztek (stanje `expired` nastavi le pomožna pot nadomestka), negotov izid poštne predaje, hramba idempotenčnih ključev, vir jezika in prikaznih oznak, več otrok v eni dostavi, delegiranje seje avtorja. Nadomestek M2 odloča po globalnem `need_ref`, brez modela naročene potrebe. Vse so odprte v D12.

Predlogi D12 po prvem pregledu (niso potrjeni): isti `person_id` se v eni dostavni zahtevi ne ponovi (nadomestek ga zavrne z `duplicate_recipient`, dokler identiteta postavke ni določena); ponovitev že prevzete zahteve vrne isti prevzem tudi po `expires_at`, nova zahteva s pretečenim rokom je 400; omejitve dolžin in števil v shemah zahtev; splošne napake 404/405/500/503 v opisu pogodbe.
