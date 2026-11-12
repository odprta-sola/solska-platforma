# Stanje paketa T (referenčni P0)

Datum: 12. november 2026. Status: pregled dejanskega stanja proti [načrtu priprave P0](priprava-referencnega-P0.md). Nič od tega ni neodvisno pregledano; pull requesti #31 do #36 do tega dne niso bili združeni ali pregledani s strani druge osebe.

## Kaj je narejeno in preizkušeno

| Zahteva iz načrta (prvi prevzem) | Stanje |
| --- | --- |
| Ena izmišljena šola, osebe, učenci, oddelki, povezave, dodelitve, dovoljenja | Narejeno (`registry`, `seed_test_data`) |
| Lokalna prijava z vzdrževano rešitvijo | Narejeno (`django-allauth`, prijava z uporabniškim imenom, brez samoregistracije) |
| Preverjanje uporabniških in servisnih pravic | Narejeno (`authz.py`, `authorizations/check`, servisni žetoni) |
| Odvzem povezave in dovoljenja | Narejeno v logiki in testih; **brez zaslona** (samo koda) |
| Osnovni CSV uvoz s predogledom, validacijo, celovito potrditvijo, ponovitvijo | Narejeno (ukaz `import_csv`); **brez zaslona** |
| Sprememba kontakta (sledljiva) | Prek uvoza (`person.import_updated`); **brez ločenega postopka ali zaslona** |
| Omejen kontaktni klic | Narejeno (`delivery-contacts/resolve`) |
| API, testni podatki, ponovljiva namestitev | Narejeno; namestitev z Dockerjem preverjena od začetka (82 testov v kontejnerju) |
| Nadomestka M1/M2 in pogodbeni testi | Narejeno kot osnutek pogodbe D12 (`api/openapi.yaml`, `p0/stubs`) |

## Kar manjka do prevzema T

| Vrzel | Posledica |
| --- | --- |
| Neodvisni pregled (9 točk, [kontrolni seznam](pregled-P0-kontrolni-seznam.md)) | Sprosti odvisni razvoj A/I; še ni izveden |
| Točka 8: obnašanje modulov ob izpadu P0 | Nepreverljivo, dokler pravi M1/M2 ne obstajata |
| Točka 9: zasloni in dostopnost | Ni zaslonov P0 (prijava je privzeta allauth); osnovni pregled s tipkovnico in bralnikom ni narejen |
| Potrditev D12 (sheme, šifranti, servisni mehanizem, topologija) | Pogodba je osnutek; ekipe se ne smejo vezati nanjo |
| Potrditev `django-allauth`, strukture `p0/m1`, `p0/m2` in imen dovoljenj | Predlogi v PR-jih, ne odločitve |
| Drugi skrbnik/namestnik (D09), namestnik in roki D14 | Pogoj za vključitev dijakov ([register](odlocitve.md)) |
| Pravice prispevkov dijakov (D08), izjave | Pred sprejemom dijaške kode |
| Imenovanje pregledovalca ter potrditev, da pregled z drugim AI zadošča | Pobudnikova osebna odločitev; formalna enakovrednost človeškemu pregledu ni potrjena |

## Pred B (ne za prvi prevzem T)

Individualna aktivacija in obnova gesla pri skupnem predalu (reset gesla je zdaj nevaren za račune s skupnim predalom in se ne sme uporabljati za resnične račune), administrativni zasloni (seznam oseb, uvoz, popravki, izvoz), dokumentiran izvoz, politika popolne uskladitve uvoza, računi učencev (predlog D01/D06/D07/D16).

## Znane omejitve nadomestkov in pogodbe

Stanje nadomestka M1 je v pomnilniku procesa. Niso preizkušeni: tihi čas, obnova po izpadu, trajni zapis pred 202, negotov izid poštne predaje, hramba idempotenčnih ključev, vir jezika in prikaznih oznak, več otrok v eni dostavi, delegiranje seje avtorja. Vse so odprte v D12.
