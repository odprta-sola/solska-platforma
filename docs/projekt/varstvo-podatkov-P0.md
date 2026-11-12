# Varstvo osebnih podatkov: stanje in vrzeli (za šolo in DPO)

Status: osnutek za posvet s pooblaščeno osebo za varstvo podatkov (DPO), 12. november 2026. Pripravil Claude (Anthropic) po navodilih pobudnika. **Ni pravno mnenje in ni ocena učinka.** Namen je, da DPO in šola začneta s konkretnim popisom, ne s praznim listom; odločitve so v [registru](odlocitve.md) pod D07 (hramba, dostopi, podatkovne poti), D04 (gostovanje, e-pošta, kopije), D11 in D16.

**Trenutno stanje:** projekt obdeluje **samo izmišljene podatke**. Pravih podatkov šole ni dovoljeno uvoziti, dokler D07 ni odločen in DPO ni pregledal obdelave. Moduli M1 (obveščanje) in M2 (obrazci in soglasja) še ne obstajajo; spodaj so opisani le kot predvidena obdelava.

## 1. Vloge

| Vloga | Kdo | Stanje |
| --- | --- | --- |
| Upravljavec | Šola, ki sistem uporablja | Predlog; potrdi šola |
| Obdelovalec | Gostitelj strežnika, ponudnik e-pošte, morebitna podpora | Ni določen (D04); potrebna pogodba po čl. 28 |
| Razvijalci (pobudnik, dijaki, mentorji) | Ne dostopajo do pravih podatkov; delajo na izmišljenih | Pravilo projekta |
| Repozitorij GitHub | Hrani samo kodo in dokumentacijo, brez osebnih podatkov šole | Ločena obdelava podatkov prispevajočih (razdelek 8) |

## 2. Kateri osebni podatki se obdelujejo (P0)

Popis iz podatkovnega modela (`p0/registry/models.py`) na commitu z odločitvami D12.

| Podatki | Posamezniki | Namen | Kje |
| --- | --- | --- | --- |
| Prikazno ime, kontaktni e-naslov, želeni jezik | starši in skrbniki, zaposleni, učenci (le ime) | identiteta v evidenci, obveščanje | `Person` |
| Uporabniško ime, zgoščeno geslo, e-naslov, čas zadnje prijave | uporabniki z računom | prijava | `Account`, seje |
| Vloge (starš, učenec, učitelj, tajništvo, skrbnik) | vsi | pravice | `PersonRole` |
| Pripadnost oddelku, dodelitev zaposlenega oddelku | učenci, zaposleni | ciljno obveščanje | `Membership`, `StaffAssignment` |
| Povezava skrbnik–učenec z vrsto in veljavnostjo | starši, učenci | kdo sme prejemati in odločati | `Relationship` |
| Upravičenja (seznanitev, odločanje) s sklicem na šolsko potrditev | starši | pravica dejanja | `Grant`, `Approval` |
| Neprosojni sklici na obseg | starši | da moduli ne uporabljajo ID otrok | `ScopeRef` |
| Posnetek občinstva (avtor, oddelek, namen, prejemniki) | zaposleni, starši | vezava kontakta na dostavo (D12) | `AudienceSnapshot`, `AudienceMember` (30 dni, predlog) |
| Sled sprememb: kdo, kaj, kdaj, imena polj (brez vrednosti) | vsi | odgovornost, sledljivost | `ChangeAudit` |
| Izvorni ključi uvoza | vsi | ponovljiv uvoz | `SourceMapping` (ključi morajo biti neosebni, ne EMŠO) |
| Povzetek uvoza in postavke predogleda | vsi (ključi) | pregled pred uveljavitvijo | `ImportBatch`, `ImportPreview` |
| Začasne datoteke CSV z imeni in e-naslovi | vsi v uvozu | uveljavitev predogleda | `ImportUpload` (največ 24 ur) |

**Ne obdeluje se:** EMŠO, datum rojstva, naslov, telefon, zdravstveni ali drugi posebni podatki. Učenci v prvi različici nimajo računov.

**Predvideno v M1/M2 (še ni izvedeno):** vsebina obvestil, potrditve seznanitve, odločitve in soglasja po namenih z zgodovino, opomniki, stanje dostave e-pošte.

## 3. Kar je že izvedeno (vgrajena zasebnost, čl. 25 in 32)

- Samo izmišljeni podatki v razvoju in testih; nobenih gesel ali ključev v repozitoriju; razvojna e-pošta se prestreže lokalno.
- **Minimizacija:** predogled prejemnikov ne vrne kontaktov; kontakt se razreši šele tik pred pošiljanjem, samo za prejemnika iz posnetka občinstva in ob veljavnem upravičenju; M2 kontaktov ne vidi.
- E-naslov ni identiteta: starša s skupnim naslovom sta ločeni osebi z ločenimi pravicami.
- **Dostop po vlogah:** zasloni evidence samo za tajništvo in skrbnika; vloge `admin` in `office` dodeli z uvozom le skrbnik.
- Odvzem povezave ali upravičenja prevlada takoj in ga uvoz ne obnovi.
- Sled sprememb brez starih in novih vrednosti; predogled uvoza hrani imena polj, ne vrednosti.
- Začasne datoteke uvoza: nedostopne po 24 urah, izbrisane najpozneje po 25 urah (samodejno).
- Posnetki občinstva: neuporabni ob izteku (30 dni, predlog), s člani izbrisani najpozneje uro pozneje (samodejno, `purge_audience_snapshots`).
- Napake ne razkrivajo tehničnih podrobnosti ali obstoja tujih podatkov.
- Varnost: zaklenjene in skenirane odvisnosti, piškotki `Secure`/`HttpOnly`/`SameSite` v produkcijskem načinu, CSRF, postopek zasebnih varnostnih prijav ([SECURITY.md](../../SECURITY.md)); šest ranljivosti je bilo odpravljenih pred kakršnimikoli pravimi podatki.

## 4. Vrzeli pred uporabo pravih podatkov

| Področje | Vrzel | Kdo |
| --- | --- | --- |
| Pravna podlaga (čl. 6) | Ni določena. Za obveščanje predvidoma naloga šole po področni zakonodaji; za obrazce M2 odvisno od namena (privolitev ali druga podlaga) | DPO, šola (D11, D16) |
| Evidenca dejavnosti obdelave (čl. 30) | Ni vodena; osnutek v razdelku 7 | šola |
| Ocena učinka (čl. 35) | Ni izvedena; zaradi mladoletnih in sistematične obdelave verjetno potrebna | DPO |
| Obvestilo posameznikom (čl. 13) | Ni pripravljeno (starši, zaposleni, dijaki) | šola, DPO |
| Roki hrambe in izbris (čl. 5(1)(e)) | Niso določeni. Zapisi se zaključijo, ne izbrišejo; posnetki občinstva se po izteku (30 dni, predlog) samodejno izbrišejo, rok potrdi D07; seje veljajo privzeto 2 tedna | D07; tehnično izvedba po odločitvi |
| Pravica dostopa in prenosljivosti (čl. 15, 20) | Ni izvoza podatkov posamezne osebe | tehnično (predlog spodaj) |
| Pravica do popravka (čl. 16) | Popravek kontakta na zaslonu obstaja; uvoz je vir resnice | izvedeno delno |
| Pravica do izbrisa in omejitve (čl. 17, 18) | Ni postopka; razmerje do hrambe zgodovine odločitev določi D07 | DPO |
| Sled vpogledov (čl. 5(2)) | Beležijo se spremembe, **ne beleži pa se, kdo je odprl podatke osebe** na zaslonih evidence | tehnično (predlog spodaj) |
| Kršitve (čl. 33, 34) | SECURITY.md ureja ranljivosti, ne pa obveščanja Informacijskega pooblaščenca v 72 urah | šola, nosilec (D14) |
| Obdelovalci in prenosi (čl. 28, 44) | Gostovanje in e-pošta nista izbrana; prenos v tretje države ni predviden, a ni preverjen | D04 |
| Mladoletni | Starostna meja 15 let za privolitev pri storitvah informacijske družbe (ZVOP-2) se uporabi le, če je podlaga privolitev | DPO (D16) |
| Varnost v produkciji | HTTPS/HSTS, šifrirane varnostne kopije, ločitev okolij, dnevniki strežnika | D04 |

## 5. Predlagane tehnične dopolnitve (ne potrebujejo čakanja na DPO)

1. Sled vpogledov: zapis, kdo je odprl podrobnosti osebe ali predogled uvoza (brez vsebine).
2. Izvoz podatkov ene osebe za odgovor na zahtevo po dostopu.
3. Mehanizem rokov hrambe (seje, zaključeni zapisi), z dejanskimi roki iz D07; čiščenje potekle vsebine po vzoru `purge_import_uploads`. Za posnetke občinstva je izvedeno (`purge_audience_snapshots`).
4. Dopolnitev SECURITY.md s postopkom ob kršitvi varstva podatkov.

## 6. Vprašanja za DPO

1. Katera pravna podlaga velja za obveščanje (M1) in katera za posamezne vrste obrazcev (M2)?
2. Ali je potrebna ocena učinka in kdo jo pripravi?
3. Roki hrambe: povezave in upravičenja po zaključku, sled sprememb, posnetki občinstva, obvestila in potrditve (M1), odločitve in soglasja z zgodovino (M2), računi po izstopu iz šole.
4. Ali ima učenec, ki dopolni 15 oziroma 18 let, lastne pravice v obrazcih, in kako to vpliva na prejemnike (D16)?
5. Pogoji za gostitelja in ponudnika e-pošte (lokacija, pogodba, varnostne kopije).
6. Kdo v šoli odgovarja na zahteve posameznikov in v kakšnem roku?
7. Ali so izvorni ključi iz šolskega informacijskega sistema primerni ali jih je treba psevdonimizirati?

## 7. Osnutek evidence dejavnosti obdelave

| Dejavnost | Namen | Posamezniki | Podatki | Prejemniki | Hramba |
| --- | --- | --- | --- | --- | --- |
| Evidenca uporabnikov in upravičenj (P0) | prijava, pravice, ciljno obveščanje | starši, učenci, zaposleni | razdelek 2 | zaposleni po vlogah; moduli M1/M2 prek API | D07 |
| Uvoz iz šolskega sistema (P0) | posodobitev evidence | kot zgoraj | datoteke CSV, povzetki | tajništvo, skrbnik | datoteke 24 ur; povzetki D07 |
| Obveščanje (M1, predvideno) | šolska obvestila, potrditve seznanitve | starši, zaposleni | vsebina, potrditve, stanje dostave | prejemniki, ponudnik e-pošte | D07 |
| Obrazci in soglasja (M2, predvideno) | odločitve staršev po namenih | starši, učenci | odločitve z zgodovino | zaposleni po vlogah | D07, D16 |
| Prispevki k projektu | razvoj odprte kode | prispevajoči (tudi mladoletni) | ime ali vzdevek, uporabniško ime GitHub v javni zgodovini; izjave hrani šola | javnost (repozitorij) | trajno (git zgodovina); izjave po roku šole |

## 8. Prispevajoči (GitHub)

Podatki prispevajočih niso podatki šolske evidence. Ime ali vzdevek in uporabniško ime sta trajno v javni zgodovini repozitorija; zato mladoletnim priporočamo vzdevek. Izjave s soglasjem staršev hrani šola, v repozitoriju je le oznaka `avtor-urejen` ([CONTRIBUTING.md](../../CONTRIBUTING.md)).
