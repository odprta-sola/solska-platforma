# Odprava ugotovitev prvega neodvisnega pregleda P0

Status: osnutek, 12. november 2026. Ta zapis ne spreminja izvirnih poročil pregledovalcev (PR #39, Codex/OpenAI; PR #40, DeepSeek), ki ostaneta zgodovinski dokaz za commit `e854f60`. **Ni človeški prevzem, ni potrditev D12 in ne zapira paketa T.** Po popravkih je potreben ponovni neodvisni pregled.

## Podatki

| Podatek | Vrednost |
| --- | --- |
| Izhodišče | `main` = `e854f60c7f2e9918b09f0b7db0108c6ab8f62b8f` |
| Popravki | lokalne veje; ob objavi se commiti ponovno zložijo, zato se SHA spremenijo in se tu posodobijo |
| Izvedel | Claude (Anthropic), model Claude Opus 5.5, po navodilih pobudnika |
| Odgovorni človek | Mitja Pirih; sprejem tega zapisa še ni potrjen |
| Okolje preverjanja | izolirana PostgreSQL 16 in slika iz `p0/Dockerfile` (Python 3.12, Django 5.2.19, django-allauth 65.22.0); ločeno od okolij pregledovalcev, po koncu odstranjeno |

## Primerjava poročil

Poročili se ujemata pri: vseh 85 obstoječih testih in 39 pogodbenih testih, neizpolnjenih točkah 8 in 9, neobravnavani napaki pri neveljavni obliki ID (500), testu z »izpadom« v imenu, ki izpada ne povzroči, in zastarelem številu testov v dokumentih. Poročilo OpenAI navaja več neskladij pogodbe, nadomestkov in uvoza ter priporoča »ne«; poročilo DeepSeek priporoča »pogojno«. Vsaka ugotovitev je bila neodvisno preverjena z reprodukcijo; lažnih alarmov ni bilo, razlike so v resnosti in obsegu.

## Zasebne varnostne ugotovitve

Tri visoke (poročilo OpenAI) in ena srednja (dodatno ugotovljena ob preverjanju). Vse so potrjene; popravki in regresijski testi so pripravljeni in preverjeni, objava se uskladi po [SECURITY.md](../../SECURITY.md). Podrobnosti do takrat niso javne.

## Tabela odprave javnih ugotovitev

ID se nanašajo na poročilo OpenAI; DeepSeek P0-01 je enak OpenAI P0-02, DeepSeek P0-04 del P0-07, DeepSeek P0-05 del P0-11, DeepSeek P0-06 del P0-09. DeepSeek P0-02 (kontaktni klic sprejme katerokoli dovoljenje obsega) ostaja opomba za D12.

| ID | Stanje | Dokaz | Preostala odločitev (kdo) |
| --- | --- | --- | --- |
| P0-01 vhod ni skladen s shemo | popravljeno | `RequestValidation` (manjkajoča, dodatna, ugnezdena polja, tipi, prazni in predolgi nizi, napačen JSON), `RequestSchemaParity` | meje dolžin in števil so predlog (D12) |
| P0-02 obdelava napak | popravljeno | `ApiErrorContract`: neveljaven UUID, izpad evidence 503 brez `allowed`, 500 brez podrobnosti, CSRF 403 JSON, 405 z `Allow`, 404 JSON, napačen žeton ob seji | splošne napake v opisu pogodbe so predlog (D12) |
| P0-03 ista oseba, dva obsega | delno | nadomestek izrecno zavrne podvojenega prejemnika (`StubEdgeContract`) | identiteta dostavne postavke (D12) |
| P0-04 ponovitev po izteku | delno | isti prevzem po izteku, brez nove dostave; nova pretečena zahteva 400 | okno hrambe ključa po izteku (D12) |
| P0-05 predogled proti uveljavitvi | popravljeno | `PreviewApplyTests` (sprememba osebe, granta, pooblastila, napaka pred končnim zapisom, ponovitev), `ConcurrentApplyTests` (dve transakciji PostgreSQL) | — |
| P0-06 pogodbeni testi | popravljeno za klice prek `ContractBase.call` | `contract_check.py` (status, vsebinski tip, formati, pogojne sheme, `counts`), `CheckerSelfTest` z namerno pokvarjenimi odgovori | klici neposredno prek odjemalca niso samodejno preverjeni |
| P0-07 lažno pomirjujoči testi | popravljeno | preimenovana testa preklica in izteka, test odnosa brez granta kliče avtorizacijo, manjkajoča modula M1/M2 izrecno preskočena | pravi izpad ostaja točka 8 |
| P0-08 nadomestki | odprto | omejitve navedene v [stanju T](../projekt/stanje-prevzema-T.md) | prava M1/M2 (ekipi, mentorji) |
| P0-09 dokumentacija | popravljeno | DEVELOPER, stanje T, kontrolni seznam, SECURITY, specifikacija, register | — |
| P0-10 dostopnost | delno | `lang`, struktura, oznake, fokus in povezane napake prijave; `test_dostopnost.py`; omejen preizkus s tipkovnico ([pregled dostopnosti](../projekt/pregled-dostopnosti-P0.md)) | ročni pregled z bralnikom (človek); zasloni za T (obseg sprejet 12. 11. 2026, izvedba odprta) |
| P0-11 odvisnosti, slike, licence | delno | `STUBS` brez `DJANGO_DEBUG=1` ustavi zagon; `check --deploy` s sintetičnimi skrivnostmi: W004 (HSTS), W008 (HTTPS) | zaklep s hashi, digesti slik, popis licenc slike, HTTPS ob dejanski namestitvi |

## Izvedeni ukazi in rezultati

```text
python manage.py test                      [DJANGO_DEBUG=1, izolirana PostgreSQL 16]
  Found 145 test(s). Ran 145 tests. OK (skipped=2)   [s preizkusi dostopnosti prijave]
  preskočena: meja modulov M1 in M2 (mapi pravih modulov ne obstajata)
python manage.py test registry.tests.test_robni   [na kodi pred javnimi popravki]
  FAILED (failures=26, errors=8)           pričakovano: dokaz, da testi zaznajo napake
ruff check . / ruff format --check .        All checks passed / already formatted
python manage.py makemigrations --check --dry-run   No changes detected
python manage.py check                      no issues
python manage.py check   [DJANGO_DEBUG=0, STUBS=m1,m2]   ImproperlyConfigured (namerno)
python manage.py check --deploy   [DJANGO_DEBUG=0, sintetične skrivnosti]   W004, W008
python3 scripts/check_docs_links.py         veljavno
```

Ni izvedeno, z razlogom: `docker compose up --build` z repozitorijsko konfiguracijo in ponastavitev volumna (vrata 5432 in 8000 sta zasedla okolja pregledovalcev, ki jih nisem ustavljal); gradnja brez predpomnilnika; pregled odvisnosti in slik (`pip-audit`, pregledovalnik slik); ročni pregled dostopnosti. Nova razvojna odvisnost `rfc3339-validator` (MIT) omogoči preverjanje formata `date-time` v `jsonschema`; sprejem odvisnosti potrdi pobudnik.

## Ocena devetih točk po popravkih

| # | Točka | Stanje |
| --- | --- | --- |
| 1 | Lastni otroci, tuja družina zavrnjena | avtomatski dokaz obstaja; ročna ponovitev ni izvedena po popravkih |
| 2 | Skupen kontakt, ločena računa | avtomatski dokaz obstaja |
| 3 | Odvzem povezave/granta | avtomatski dokaz obstaja |
| 4 | CSV brez delnega prepisa, ponovitev, sled | dopolnjeno z vezavo na potrjen načrt in sočasnostjo |
| 5 | Omejen servisni kontaktni klic | stanje se objavi skupaj z zasebnimi popravki |
| 6 | Pregled kode | opravila sta ga sistema AI; ponovni pregled ni izveden |
| 7 | Pogodbeni testi po ponastavitvi | testi zeleni v izolirani zbirki; `compose down -v` po popravkih ni izveden |
| 8 | Izpad P0, brez zaščitenega dejanja in slepe dostave | ni izpolnjeno (prava M1/M2 ne obstajata) |
| 9 | Tipkovnica, fokus, napake, bralnik | ni izpolnjeno: prijava popravljena in preizkušena s tipkovnico, ročni pregled z bralnikom ni izveden, zasloni za osnovna opravila ne obstajajo |

## Dvajset skupin preizkusov

Spremenjene glede na poročilo OpenAI: 5 (odnos brez granta zdaj preveri zavrnitev avtorizacije; odvzem v vseh štirih poteh) postane pokrit; 6 se oceni ob objavi zasebnih popravkov; 17 in 18 ostaneta delno (iztek in izpad nista samodejno preizkušena); 20 ostane delno (gradnja brez predpomnilnika, izvoz in dostopnost niso). Druge ocene poročila OpenAI ostanejo nespremenjene. Brez izmišljene pokritosti: skupaj 3 pokrite, 8 delno, 1 nepokrita, 8 zunaj obsega T.
