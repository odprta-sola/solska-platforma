# Arhitekturna izhodišča

Status: predlog za pregled z mentorjem  
Datum: 5. oktober 2026

## Posodobljena usmeritev 13. oktobra 2026

Vsaka šola ima ločeno namestitev in podatke; centralna storitev za več šol ni predvidena. Dejansko upravljanje infrastrukture, kopij, dostopov in posodobitev potrdi šola v D04/D09. CSV ostane osnovna pot tudi ob poznejši dodatni integraciji eAsistent. ArnesAAI in SI-PASS sta prostovoljni prihodnji prijavi ob ohranjenih lokalnih računih.

Mitja je osebno izbral Django 5.2 LTS/Python, PostgreSQL in Docker Compose za razvoj; skupni tehnološki dogovor in konkretne izdaje potrebujejo potrditev. [Kratka specifikacija](kratka-specifikacija-P0-M1-M2.md) je delovna vstopna točka; tu opisana razmejitev ne potrjuje implementacije.

## Samostojni modul in skupno jedro

Samostojnost pomeni, da je M1 uporabna namestitev brez ostalih modulov. Ne pomeni, da dijaki ponovno razvijejo prijavo, kriptografijo ali upravljanje pravic.

Skupne vzdrževane komponente zagotavljajo identitete, povezave z učenci, šifrante in osnovne varnostne funkcije. V samostojni namestitvi so vključene lokalno; poznejše razširitve jih lahko uporabljajo prek pregledanih lokalnih vmesnikov v isti šolski namestitvi.

Vsak modul upravlja svoj podatkovni model. Moduli se povezujejo prek dokumentiranih API in dogodkov. Ločena logična podatkovna shramba ne zahteva ločenega fizičnega strežnika za vsak modul.

## Minimalni dogovori pred razvojem

| Področje | Potrebna odločitev |
| --- | --- |
| Identitete | Stabilni identifikatorji in preslikava lokalnih računov v prihodnje jedro |
| Povezave | Kdo preverja upravičenje do podatkov učenca in kdaj preneha |
| API | Avtentikacija, preverjanje dovoljenj, različice in obravnava napak |
| Dogodki | Enoličen identifikator, ponovitve in preprečevanje dvojnih posledic |
| Čas | Časi dogodkov v UTC, prikaz in urniki v Europe/Ljubljana |
| Zgodovina | Različice obvestil in nespremenjene povezave potrditev |
| Izvoz | Vsebina, priponke, metapodatki in dokumentirana shema |
| Namestitev | Ponovljiv paket, skrivnosti zunaj kode, posodobitve in obnova |

## Predlog izvedbe M1

Spletna aplikacija z mobilnim vmesnikom, podatkovna baza, trajna čakalna vrsta za e-pošto, zaščitena shramba prilog in dnevnik dogodkov. Tehnologijo potrdi naročnik (skupni tehnični nosilec), mentor kot izvajalec oceni izvedljivost; Izbrana osnova je Django 5.2 LTS s PostgreSQL (D03).

Prvi pilot vključuje minimalni dokumentirani vmesnik M1–M2 za obveščanje. Razširjen API za vse prihodnje module ni pogoj pilota. M2 vodi odločitve in določa potrebne opomnike; M1 izvaja pošiljanje, tihi čas in ponovne poskuse.

Razlaga pogodbe in skupnega vira identitet ter upravičenj je v [vmesniku P0–M1–M2](vmesnik-P0-M1-M2.md). Nadomešča načrtovano ime vmesnik-M1-M2.md. Opredeljuje predlagane osnovne poti, prijavo, prejemnike, servisna dovoljenja, dostavo in napake. D12 je sprejet 13. 11. 2026 in pogodba zamrznjena kot [OpenAPI `1.0.0`](../../api/openapi.yaml); topologija in prijavni protokol sta del nje. Upravičenja se preverjajo ob uporabi; način periodične uskladitve odprtih postopkov oziroma dogodkov se potrdi pred pilotom. Nadomestka M1/M2 sta v `p0/stubs`.

## Meje okolij

Razvoj in testi uporabljajo izmišljen nabor podatkov. Produkcija ima ločene poverilnice in pooblaščene skrbnike. Javni repozitorij ne vsebuje podatkovnih baz, kontaktnih seznamov, podpisnih ključev ali produkcijskih kopij.

## Odprte odločitve

Gostovanje, poštna storitev, tehnologija, prijavna komponenta, velikost pilota, cilji obnovitve in načrt prehoda na jedro se zabeležijo v registru odločitev. Pred potrditvijo se ne razvija nepotrebna infrastruktura za vse prihodnje module.
