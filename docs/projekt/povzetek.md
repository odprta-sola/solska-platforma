# Projekt Odprta šola

Različica: V6, javni osnutek  
Datum: 5. oktober 2026  
Status: osnutek dokumenta za pregled; sodelovanje obeh šol je dogovorjeno  
Izhodišče: projektni povzetek V5 z dne 1. oktobra 2026

## Namen in stanje

Odprta šola je pobuda za modularno odprtokodno rešitev elektronskega poslovanja šol. Nastala je ob sodelovanju pobudnika z OŠ Vojke Šmuc Izola in GEPŠ Piran. Po sestanku 1. oktobra 2026 je v pripravi prvi modul eSporočanje in dogovor o razvoju z mentorji ter morebitnimi drugimi šolami.

Pobudnik je Mitja Pirih, v vlogi starša in strokovnega svetovalca. OŠ Vojke Šmuc Izola in GEPŠ Piran sta se odločili za sodelovanje v projektu. Obseg pilota, razdelitev odgovornosti, roki in pogoji produkcijske uvedbe se še usklajujejo. Odločitev za sodelovanje ne pomeni potrditve vsakega delovnega dokumenta ali posamezne finančne obveznosti.

Organizacija GitHub odprta-sola in javni repozitorij solska-platforma sta vzpostavljena. Obstaja osnutek specifikacije M1. Produkcijska aplikacija še ni na voljo.

## Cilji

Šole naj uvajajo posamezne uporabne module postopoma, brez obveznega nakupa celotnega sistema. Rešitev mora omogočati izvoz in prenos podatkov, preprosto uporabo, dostopnost ter strokovno vzdrževanje. Elektronska pot naj bo za starše brezplačna, papirna možnost ostane del zasnove.

Projekt ima tudi učni namen: razvoj omejenih modulov lahko postane maturitetna naloga. Učni izdelek, strokovni prevzem in produkcijska uvedba so ločeni mejniki.

## Uporabniške potrebe

Anketa staršev na OŠ Vojke Šmuc je opozorila na pomen preproste uporabe, varstva osebnih podatkov, obstoječega komunikacijskega kanala in ohranitve papirne možnosti. Te ugotovitve pomagajo oblikovati uporabniško izkušnjo; izhodišče za nadaljevanje projekta je odločitev obeh šol za sodelovanje. Podrobni rezultati in omejitve ostajajo v [podpornem poročilu ankete](../raziskave/anketa-starsi.md).

## Predlog prvega pilota

M1 eSporočanje je namenjen organizacijskim obvestilom, prilogam, e-poštnemu obveščanju, potrditvi seznanitve, opomnikom in papirni poti. Ne obravnava soglasij, privolitev, ocen ali formalnega upravnega vročanja.

Pilot mora ločiti objavo, predajo e-pošte strežniku, odprtje vsebine in izrecno potrditev konkretne različice. Prejemnike določa preverjena evidenca upravičenih oseb.

Predlagani prvi obseg vključuje uvoz, varno prijavo, pravice dostopa, različice, pregled odzivov, izvoz, kopije in mobilno dostopnost. Potisna obvestila, povezave z državnimi prijavami, integracije drugih modulov in avtomatizacija šolskega leta so predlog za naslednjo fazo. Potrebni jeziki pilotne šole sodijo že v pilot.

Obseg še pregleda mentor. [Osnutek M1](https://github.com/odprta-sola/solska-platforma/pull/1) je odprt za pripombe.

## Predvideni moduli

Spodnja razčlenitev je razvojna smer, ne potrjen program izvedbe.

| Gradnik | Namen | Faza |
| --- | --- | --- |
| P0 Jedro | Identitete, povezave z učenci, šifranti, pravice in skupne storitve | Minimalne skupne komponente ob M1; razvoj vodi strokovni nosilec |
| M1 eSporočanje | Obvestila in seznanitev | Prvi pilot |
| M2 eSoglasja | Soglasja, privolitve in dokazni zapisi | Po izkušnjah M1 in pravnem pregledu |
| M3 Govorilne ure | Termini, rezervacije in opomniki | Poznejša faza |
| M4 Prijave | Dejavnosti in programi | Poznejša faza |
| M5 Odsotnosti | Sporočila in obravnava izostankov | Poznejša faza |
| M6 Prehrana | Obroki in izvoz za obračun | Poznejša faza z ločeno presojo občutljivih podatkov |
| M7 Urnik | Urniki in nadomeščanja | Poznejša faza |
| M8 Knjižnica | Izposoja in učbeniški sklad | Poznejša faza po preverjanju obstoječih rešitev |
| M9 Dnevnik in redovalnica | Predpisane evidence | Šele po stabilni platformi in ločeni presoji |
| M10 Obračun | Povezava z računovodstvom | Prednost ima izvoz v obstoječe sisteme |
| M11 Poročila | Statistike in izvozi | Glede na potrjene potrebe |

## Arhitektura in infrastruktura

Moduli imajo dokumentirane vmesnike in ne dostopajo do tabel drugih modulov. Samostojna namestitev uporablja skupne vzdrževane komponente za prijavo in pravice, da vsaka ekipa ne razvija varnostnih funkcij na novo.

Za pilot je predlagana ločena namestitev posamezne šole. Arnes je kandidat za infrastrukturo, vendar je treba pred potrditvijo preveriti storitve, pogoje in odgovornosti upravljanja. SI-PASS in ArnesAAI sta predvideni prihodnji povezavi, ne že potrjeni integraciji.

Gostovanje pri šoli ne izključuje zunanjih podatkovnih poti. E-pošto, kopije, podporo in zunanje prijave je treba dokumentirati. Tehnologijo z mentorjem potrdi tehnični nosilec. [Arhitekturna izhodišča](../arhitektura/izhodisca.md) ostajajo osnutek.

## Vodenje in vzdrževanje

Pred začetkom razvoja se določijo mentor, tehnični nosilec, šola pilota in nosilec prevzema. Pred produkcijo se določita vzdrževalec in njegova zamenjava ter postopek podpore, posodobitev in incidentov.

Razvoj poteka na izmišljenih podatkih. Dostop do produkcije je ločen od sodelovanja v javnem repozitoriju. Pooblaščena oseba za varstvo podatkov sodeluje pri presoji obdelave in potrebi po oceni učinka. Podrobnosti so v [predlogu odgovornosti](odgovornosti.md).

## Delo in financiranje

V5 navaja 150–250 ur za modul. Ta ocena se ne prevzame kot potrjena ocena celotnega produkcijskega M1. Mentor naj pripravi razrez prototipa, strokovnega dela in produkcijskega prevzema.

Brezplačna infrastruktura ali prostovoljno delo ne pomenita ničelnega stroška: mentorsko delo, pregledi, uvajanje in vzdrževanje potrebujejo čas. Pred pilotom se evidentirajo ure, neposredni stroški in odgovornosti.

Možni viri so redno delo šol, projektna partnerstva, občina ter razpisi za sodelovanje in digitalizacijo. V6 ne potrjuje razpoložljivosti, rokov ali upravičenosti posameznega razpisa. Razpisni pregled je ločena naloga.

## Pravne in organizacijske odločitve

Pred produkcijo se preverijo pravna podlaga, vloge upravljavca in morebitnih obdelovalcev, hramba, pogodbeni odnosi ter pogoji elektronskega poslovanja. Nekomercialna pomoč se presoja po dejanskih nalogah in dostopih.

Pravne trditve iz V5 o arhiviranju, certificiranju, notranjih pravilih in posameznih predpisih niso s tem osnutkom potrjene. Za M1 je najprej potrebna konkretna politika obdelave in hrambe. Elektronski žig in kvalificirani časovni žig nista samodejna pogoja za vsak dogodek M1; njihova uporaba se presodi za konkretno vrsto dokumenta.

Pred vključevanjem kode se uredijo licenca in pravice prispevkov. Predvidena licenca je EUPL 1.2. Dokumentirati je treba tudi dejanske vloge podjetij in morebitna nasprotja interesov. Predlagana nekomercialna vloga ne predstavlja že sklenjenega dogovora.

## Naslednji koraki

1. Mentor pregleda obseg M1 in oceni izvedljivost ter roke.
2. Zavoda konkretizirata dogovorjeno sodelovanje, razdelitev dela in odgovorne osebe.
3. Potrdijo se minimalna arhitektura, jeziki, politika dostopov in infrastruktura.
4. Uredijo se licence in prispevki avtorjev.
5. Razvojni prototip se preveri na testnih podatkih.
6. O produkcijskem pilotu se odloči na podlagi ločenega strokovnega prevzema.

Kratkoročno preverjanje možnosti obstoječega ponudnika eAsistent lahko poteka vzporedno. Njegovih cen, integracij ali funkcij ta dokument ne predpostavlja.

## Spremembe glede na V5

- V5, poslan ravnateljema v PDF, ostane zgodovinsko izhodišče.
- V6 je nova javna različica brez osebnih kontaktov in podrobnih internih zapisov.
- Navedena je odločitev obeh šol za sodelovanje; izvedbeni dogovori ostajajo odprti.
- Anketa je v povzetku omejena na uporabniške potrebe; podrobna razlaga in popravki so v podpornem poročilu.
- Ločeni so prototip, produkcijski pilot in poznejše funkcije.
- Ocenjena zahtevnost in stroški so predmet preverjanja.
- Natančneje so opredeljene skupne komponente, dostopi, odgovornosti in podatkovne poti.
- Nepreverjene pravne, infrastrukturne in razpisne trditve so obravnavane kot odprte naloge.

Izvor in status gradiv sta opisana v [evidenci izvorov](izvor-gradiva.md).
