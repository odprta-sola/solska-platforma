# D12: paket za odločitev (sestanek z mentorji)

Status: točke A je 12. 11. 2026 sprejel skupni tehnični nosilec (pobudnik) in so izvedene v P0; **potrditev mentorjev obeh ekip je odprta**, pogodba se zamrzne kot `1.0.0` šele po njej. Točke B ostajajo predlog. Pripravil Claude (Anthropic) po navodilih pobudnika; potrdita skupni tehnični nosilec in mentorji ([register](odlocitve.md)). Podrobna razlaga točk C01 do C16 je v [pripravi odločitev](priprava-odlocitev-D03-D09-D12-D14.md#d12-seznam-odločitev-in-nasprotnih-primerov), kanonični osnutek v [pogodbi](../arhitektura/vmesnik-P0-M1-M2.md) in [OpenAPI](../../api/openapi.yaml). Ta paket doda stanje izvedbe po prvem neodvisnem pregledu (`main` = `184c8f9`) in loči, kaj je treba odločiti **pred začetkom dela ekip** in kaj šele **pred integracijo** (mejnik I).

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

| Točka | Stanje v P0 danes | Predlog |
| --- | --- | --- |
| C02 Oznake za prikaz | `audiences/resolve` vrne ime prejemnika in otroka | Potrdi kot zdaj; zgodovinski posnetek oznak po D07 |
| C03 Jezik | `preferred_language` na osebi, vrne se s kontaktom | Jezik prejemnika iz P0; nadomestni jezik po D05 |
| C06 Avtorizacija ob času dejanja | Brez predpomnjenja; odvzem prevlada; izpad 503 | Potrdi kot zdaj; odvzem med čakanjem zadrži dostavo (M1) |
| C08 Idempotenca | Nadomestek: isti ključ in vsebina = isti prevzem, tudi po izteku; drugačna vsebina 409; hramba v pomnilniku | Okno hrambe ključa (predlog 30 dni) in poslovni ključ dogodka v M1 |
| C09 `need_ref` | Nadomestek M2 odloča po globalnem sklicu | Sklic na eno potrebo (oseba, otrok, namen, različica) |
| C10 Tihi čas, `expires_at` | Ni izvedeno | M1 lastnik urnika; M2 odda ob dospelosti; po izteku ni predaje |
| C11 Trajnost | Nadomestek ne hrani trajno | 202 šele po trajnem zapisu; preizkus izpada v M1 |
| C13 Negotova poštna predaja | Ni izvedeno | Stanje `held` z razlogom, ročna odločitev o ponovitvi |
| C14 Uskladitev ob spremembi evidence | Preverjanje ob dejanju; ni periodične uskladitve | Periodična ponovna presoja odprtih postopkov, interval pred pilotom |

## Kaj sestanek potrebuje

- Prisotni: skupni tehnični nosilec (pobudnik) in mentorja obeh ekip.
- Odločitev za vsako točko A: sprejeto / spremenjeno (kako) / zavrnjeno (zakaj).
- Zapis v [register odločitev](odlocitve.md) z datumom in commitom; povezan issue D12 (#21) ostane odprt do zamrznitve pogodbe.
- Ocena: točke A so izvedljive v enem sestanku; točke B se obravnavajo, ko ekipi dosežeta mejnik A.
