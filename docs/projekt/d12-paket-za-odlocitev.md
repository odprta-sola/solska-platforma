# D12: paket za odločitev

Status: **sprejeto 13. 11. 2026.** Točke A (12. 11.) in B (13. 11.) je sprejel pobudnik, ki je od 13. 11. 2026 naročnik; mentorji so izvajalci in pogodbe ne potrjujejo ([register](odlocitve.md#vloge-naročnik-in-izvajalec-13-novembra-2026)). Točke A so izvedene v P0, točke B v pogodbi in nadomestkih M1/M2 (pravi M1/M2 jih izvedeta sama). Pogodba je zamrznjena kot `1.0.0` ([zapis](../../api/zamrznitve.txt)). Pripravil Claude (Anthropic) po navodilih pobudnika; potrdita skupni tehnični nosilec in mentorji ([register](odlocitve.md)). Podrobna razlaga točk C01 do C16 je v [pripravi odločitev](priprava-odlocitev-D03-D09-D12-D14.md#d12-seznam-odločitev-in-nasprotnih-primerov), kanonični osnutek v [pogodbi](../arhitektura/vmesnik-P0-M1-M2.md) in [OpenAPI](../../api/openapi.yaml). Ta paket doda stanje izvedbe po prvem neodvisnem pregledu (`main` = `184c8f9`) in loči, kaj je treba odločiti **pred začetkom dela ekip** in kaj šele **pred integracijo** (mejnik I).

## Zakaj zdaj

Ekipe M1 in M2 se po pravilu projekta ne smejo vezati na nepotrjeno pogodbo. Za začetek dela (mejnik A: samostojni modul proti nadomestku P0) ni treba odločiti vsega; dovolj je sedem točk spodaj. Ostale lahko ekipe razvijajo vzporedno in jih potrdimo pred integracijo.

## A. Odločiti pred začetkom ekip

| Točka | Stanje v P0 danes | Predlog | Zakaj zdaj |
| --- | --- | --- | --- |
| **C04** Identitete in klicatelji | `person_id` (UUID) je identiteta osebe; uporabniški klic iz seje, servisni z žetonom (Bearer), ločeno in testirano | Potrdi tako. `subject_id`, `recipient_id`, `author_id` so vloge iste `person_id` | Vsak klic ekip uporablja te pojme |
| **C05** Topologija | En proces Django z moduli kot aplikacijami; nadomestka M1/M2 v istem procesu; servisni žetoni s seznamom dovoljenj | Za učni B: ena namestitev, ločene aplikacije in tabele, klici samo prek API (tudi znotraj procesa); fizična ločitev kasneje | Določa, kako ekipe strukturirajo kodo (`p0/m1`, `p0/m2`) |
| **C04/C05** Delegiranje avtorja | `audiences/resolve` sprejme `author_id` od servisa brez dokaza, da je avtor res prijavljen | M1 kliče z uporabnikovo sejo (ista namestitev, isti piškotek) za predogled občinstva; servisni žeton samo za dostavo | Brez tega lahko vsak servis bere prejemnike katerega koli oddelka |
| **C01** `scope_ref` | En neprosojen sklic na (oseba, otrok), z rokom; pravico vedno preveri P0 ob dejanju | Potrdi: en sklic na otroka; več otrok = seznam sklicev, nikoli sklic na skupino | M1 potrditve in M2 odločitve so vezane na sklic |
| **C07** Kontakt za dostavo | **Začasno zaprt** (503) po varnostnem nasvetu S-01; pravila upravičenosti pripravljena in testirana | P0 ob `audiences/resolve` shrani posnetek občinstva (`audience_ref`: avtor, namen, prejemniki z obsegi, rok). M1 pri `delivery-contacts/resolve` navede `audience_ref`; P0 vrne kontakt le za prejemnika iz posnetka, s še veljavno pravico. Za opomnike M2 enak posnetek ob izdaji obrazca | Brez tega M1 ne more poslati nobenega e-sporočila |
| **C12** Postavka dostave | Nadomestek zavrne isti `person_id` dvakrat v eni zahtevi (`duplicate_recipient`) | Postavka = (oseba, `scope_ref`); preklic in stanje po postavki (`delivery_item_id`); ista oseba z dvema otrokoma = dve postavki | Določa sheme M1 in M2 |
| **C15/C16** Sheme, omejitve, različica | OpenAPI 3.1 z omejitvami kot predlog (ID ≤ 256, ≤ 200 prejemnikov, `params` ≤ 50 polj), splošne napake 404/405/500/503 v JSON; pogodbeni testi in preverjevalnik | Potrdi omejitve in napake; **zamrzni** pogodbo kot `1.0.0` na določenem commitu; spremembe z vplivom na ekipe prek PR s potrditvijo obeh mentorjev | Ekipe potrebujejo stabilno tarčo |

Po potrditvi zgornjih točk pripravim spremembe P0 (posnetek občinstva, seja za predogled, `delivery_item_id`), posodobim OpenAPI in nadomestka ter pogodbene teste; nato se pogodba zamrzne.

## B. Odločiti pred integracijo (mejnik I)

Sprejel tehnični nosilec 13. 11. 2026 po predlogu. Stolpec »Izvedba« pove, kako je pravilo zapisano v pogodbi ([OpenAPI](../../api/openapi.yaml)) in nadomestkih; podrobnosti, ki jih predlog ni določil, so označene kot predlog za mentorje.

| Točka | Predlog (sprejet) | Izvedba v pogodbi in nadomestkih |
| --- | --- | --- |
| C02 Oznake za prikaz | Potrdi kot zdaj; zgodovinski posnetek oznak po D07 | Brez spremembe: `audiences/resolve` vrne `display_label` in `student_label` samo za avtorjev oddelek |
| C03 Jezik | Jezik prejemnika iz P0; nadomestni jezik po D05 | `locale` ni več skupno polje zahteve; neobvezen `recipients[].locale` je izrecna preglasitev postavke. Brez prevoda: `held`, `TRANSLATION_MISSING` (brez tihe zamenjave do D05) |
| C06 Avtorizacija ob času dejanja | Potrdi kot zdaj; odvzem med čakanjem zadrži dostavo (M1) | Obdelava ponovno preveri posnetek, sklic in upravičenje; odvzem: `held`, `NOT_ALLOWED`; brez kontakta: `held`, `NO_CONTACT` |
| C08 Idempotenca | Okno hrambe ključa (30 dni) in poslovni ključ dogodka v M1 | Novo obvezno polje `event_key`; ponovitev istega ključa 30 dni po prevzemu, nato 409 `replay_window_expired`; ista postavka istega dogodka pod novim ključem: 409 `duplicate_event`, nič prevzeto |
| C09 `need_ref` | Sklic na eno potrebo (oseba, otrok, namen, različica) | `need_ref` na postavki (obvezen samo pri `reminder`); M2 preveri pripadnost prejemniku in obsegu; tuj, neznan ali potekel sklic: 404; napaka preverjanja: `held`, `CHECK_UNAVAILABLE`; odgovorjeno: `cancelled`, `NO_LONGER_REQUIRED` |
| C10 Tihi čas, `expires_at` | M1 lastnik urnika; M2 odda ob dospelosti; po izteku ni predaje | Osnutek urnika delavniki 7–20 Europe/Ljubljana (prazniki po šoli); izven: `queued`, `QUIET_HOURS`; če pred iztekom ni dovoljenega časa ali ob `now >= expires_at`: `expired`, `DELIVERY_WINDOW_EXPIRED` |
| C11 Trajnost | 202 šele po trajnem zapisu; preizkus izpada v M1 | Nadomestek M1 hrani zahteve in postavke v bazi v eni transakciji; izpad zapisa: 503, nič delno prevzetega |
| C13 Negotova poštna predaja | Stanje `held` z razlogom, ročna odločitev o ponovitvi | `held`, `HANDOFF_UNCERTAIN`; obdelava je ne ponovi sama; preklic vrne `too_late` (morda že predano) in prepreči ponovitev; ob izteku `expired` z istim razlogom |
| C14 Uskladitev ob spremembi evidence | Periodična ponovna presoja odprtih postopkov, interval pred pilotom | Naloga M2 (in M1 za čakajoče dostave); nadomestek M1 ob vsaki obdelavi ponovno presodi čakajoče in samodejno zadržane postavke. Interval določi nosilec pred pilotom |

Vidni razlogi so v novem polju `recipients[].reason_code` stanja dostave.

## Kaj je sestanek potreboval (zgodovinsko, pred 13. 11. 2026)

- Prisotni: skupni tehnični nosilec (pobudnik) in mentorja obeh ekip.
- Odločitev za vsako točko A: sprejeto / spremenjeno (kako) / zavrnjeno (zakaj).
- Zapis v [register odločitev](odlocitve.md) z datumom in commitom; povezan issue D12 (#21) ostane odprt do zamrznitve pogodbe.
- Ocena: točke A so izvedljive v enem sestanku; točke B se obravnavajo, ko ekipi dosežeta mejnik A.
