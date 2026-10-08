# P0, M1 in M2 – vodnik za mentorjev prvi pregled

Datum: 8. oktober 2026  
Status: osnutek za pregled; ne potrjen načrt ali dovoljenje za produkcijo

## Kaj potrebujemo od mentorja

1. Potrditev razumevanja primerov in meje prvega izdelka.
2. Predlog ekip ter individualnega izdelka vsakega dijaka.
3. Oceno ur dijakov, mentorja in strokovnega pregleda po mejnikih.
4. Rok prijave maturitetne teme, rok oddaje in vmesne preglede.
5. Dogovor, kdo pripravi P0 in testne nadomestke ter kdo potrdi pogodbo API.

Tehnična dodatka sta [P0 in uporabniška evidenca](../moduli/P0-uporabniki.md) ter [osnutek pogodbe P0–M1–M2](../arhitektura/vmesnik-P0-M1-M2.md). [Navodilo za pregled](navodilo-za-pregled.md) je ločeno. Podrobni specifikaciji [M1](../moduli/M1-eSporocanje.md) in [M2](../moduli/M2-eSoglasja.md) ostajata merilo celotnega obsega.

## 2. Izhodišča in status dogovorov

Pobudnik je 8. oktobra 2026 podal naslednja izhodišča za pripravo:
- Mentor oceni celoten cilj in posebej omejen prvi prototip.
- Predlagana pilotna šola je OŠ Vojke Šmuc Izola; preizkus pri GEPŠ je treba preveriti. To ni potrditev produkcijske uvedbe.
- Razvoj in demonstracije uporabljajo izključno izmišljene podatke.
- Šola uporablja eAsistent. Oblika in razpoložljivost izvoza nista preverjeni.
- Osnovna namestitev deluje z lokalnimi računi in CSV uvozom, brez obvezne povezave z eAsistentom ali ARNES.
- Možnost ArnesAAI ostane zahtevana razvojna smer, predvidoma v naslednji fazi; posamezni šoli njena uporaba ni obvezna. Termin in izvedba še nista potrjena.
- P0, M1 in M2 so predlagani za razvoj dijakov pod mentorskim in strokovnim vodstvom.
- Po navedbi pobudnika je na eni šoli približno 20–25 potencialnih maturantov. Sodelovanje vseh ni dogovorjeno.
- Ohranimo povezavo M2 z M1 za obveščanje. Nadomestni produkcijski kanal za M2 brez M1 ni del tega predloga.
- Vmesnike določimo pred vzporednim razvojem in zgodaj preverimo skupno delovanje.

Predlog 2–3 dijakov na modul, razrez nalog, API v tehničnem dodatku, podatkovna shema in mejniki so predlogi za mentorje. Ocen ur, oseb, tehnologije in rokov ne določajo. D01–D16 ostajajo odprte po registru; paket jih sam ne zaključi.

## 3. Razlika med P0, M1 in M2

| Del | Naloga | Tipičen rezultat |
| --- | --- | --- |
| P0 – minimalna skupna osnova | Osebe, računi, prijava, povezave z otroki, oddelki in upravičenja | Sistem ve, kdo je uporabnik in za katerega otroka sme delovati |
| M1 – eSporočanje | Obvestila, priloge, seznanitev, dostava in opomniki | »Seznanjen/-a sem z navodilom za športni dan.« |
| M2 – eSoglasja | Pregledani obrazci, odločitve, potrdila in preklici | Odločitev za določen namen, z različico in zgodovino |

P0 je že naveden v projektnem povzetku. Tukaj opisujemo njegov minimalni obseg za prva modula, ne celotnega prihodnjega jedra.

M1 deluje s P0 brez M2. M2 uporablja P0 in M1. M2 ima lastno vsebinsko logiko in shrambo odločitev; uporabniku razširi rešitev s soglasji. Potrditev seznanitve v M1 ni odločitev v M2.

Ena namestitev šole uporablja skupne račune. To ni predlog centralne baze vseh šol. Lokalno gostovanje lahko pomeni šolski strežnik ali izbranega ponudnika. Logično ločene shrambe ne zahtevajo treh fizičnih strežnikov. Moduli ne berejo tabel drug drugega.

Primer skupnega poteka:
1. P0 preveri prijavo in veljavno povezavo osebe z otrokom.
2. M2 pokaže obrazec in shrani odločitev.
3. M2 naroči M1 splošno obvestilo s povezavo.
4. M1 opravi pošiljanje; vsebina in izbira ostaneta v M2.
5. Ob izpadu M1 odločitev ostane shranjena, obveščanje počaka.


| Dejanje | Kaj se zapiše | Česa ne pomeni |
| --- | --- | --- |
| M1: »Seznanjen/-a sem« z navodilom za športni dan | Oseba, različica, čas in obseg seznanitve | Dovoljenja za dejavnost ali odločitve drugega starša |
| M2: oddaja izbire za namen objave fotografij | Odločitev po namenu, različica in dokazni dogodek | Splošne privolitve za vse namene |

Šola uporabnica določa potrebe in upravičenja; razvojni zavod organizira delo dijakov. Vloge se lahko pojavijo v isti ustanovi, vendar niso samodejno iste odgovornosti.

## 4. Kaj naj mentor oceni

Mentor za vsako nalogo navede: fazo, dijaka oziroma ekipo, ure dijakov, ure mentorja, potrebno strokovno delo, odvisnosti in merilo zaključka. Celoten M1 se ne ocenjuje avtomatično kot 150–250 ur.

| Naloga | Predlagana faza | Ocena ur in nosilec |
| --- | --- | --- |
| Dogovor o identitetah, upravičenjih in API | Pred vzporednim razvojem | Določi mentor s skupnim tehničnim nosilcem |
| P0: lokalna prijava, testna evidenca in pravice | Prvi prototip | Za oceno |
| P0: CSV predogled in varen uvoz | Naslednji razvojni mejnik | Za oceno |
| M1: objava, prikaz in potrditev | Prvi prototip | Za oceno |
| M1: minimalni sprejem zahtev drugih modulov | Zgodnji integracijski mejnik I | Za oceno |
| Testna nadomestka P0 in M1 iz iste pogodbe | Pred vzporednim razvojem; izdelajo dodeljeni dijaki ali strokovni sodelavec pod pregledom nosilca | Izvajalca je treba imenovati |
| M1: priloge, različice, opomniki in papirna pot | Naslednji razvojni mejnik | Za oceno |
| M2: testni obrazci in izrecne odločitve | Vzporedni prototip po dogovoru API | Za oceno |
| M2: preklici, spori, potrdila in zgodovina | Naslednji razvojni mejnik | Za oceno |
| Skupni preizkusi, dostopnost, namestitev | Skozi razvoj | Za oceno |
| Produkcijski pregled in vzdrževanje | Ločen prevzem | Potreben imenovani strokovni nosilec |

Možna začetna razporeditev je 2–3 dijake na modul. Mentor potrdi individualne prispevke in formalno primernost nalog. Vsak dijak mora znati razložiti in zagovarjati svoj del. Vsaka ekipa testira svojo izvedbo; neodvisen pregled je dodatna naloga.

Dovoljeni so primerjalni prototipi. Vsi uporabljajo iste dogovore in testne primere. Osnovo za nadaljevanje izberemo zgodaj po pravilnosti, dostopih, povezljivosti, razumljivosti kode, testih in namestitvi. Izbira najboljših ločenih izdelkov šele ob koncu ni načrt integracije.


### Mejniki in individualni izdelki

A je prva demonstracija M1 z minimalnim P0. I je zgodnja integracija, lahko najprej s testnim nadomestkom M1/P0, nato s pravima izvedbama. B je celoten učni prototip iz specifikacij. C je ločen produkcijski prevzem. M2 v mejniku B vključuje več namenov, pravila zahtevanih potrjevalcev, preklic in zgodovino. Predhodni delni prikaz ni celoten učni prototip M2.

| Predlagani individualni izdelek | Dokaz prispevka | Dijak, ure in rok |
| --- | --- | --- |
| P0 evidenca in uvoz | Shema, predogled, validacije, testi uvoza | Določi mentor |
| P0 prijava in pravice | Vključitev vzdrževane prijave, preverjanja dostopa, testi | Določi mentor |
| M1 objave in seznanitev | Vmesnik, različice, potrditve in testi | Določi mentor |
| M1 dostava | API, vrsta, preklic, iztek in testi izpadov | Določi mentor |
| M2 obrazci in pregled | Predloge, več namenov, odobritev različice | Določi mentor |
| M2 odločitve | Pravila odzivov, preklic, zgodovina in testi | Določi mentor |

Tabela ne predpisuje šestih obveznih nalog ali števila maturitetnih izdelkov. Mentor lahko naloge združi ali razdeli in preveri primernost za program. Nadomestek P0 omogoča vzporedno delo, ne nadomesti izdelave in prevzema pravega P0.

## 5. Prvi prototip M1

Cilj: zaposleni objavi besedilno obvestilo za oddelek; upravičeni uporabnik ga odpre in po potrebi potrdi; zaposleni vidi odzive.

V prvi oddaji:
- lokalna prijava prek vzdrževane rešitve;
- vnaprej pripravljeni izmišljeni računi, oddelki in povezave v P0;
- priprava osnutka, predogled prejemnikov in objava;
- informativno obvestilo ali zahtevana seznanitev;
- seznam in prikaz dovoljenih obvestil;
- potrditev osebe za konkretno različico in prikazan obseg;
- pregled posameznih odzivov;
- splošna e-pošta v testni predal, ločeno od stanja objave;
- navodila za ponovljivo namestitev in skupni preizkusi.

Priloge, CSV uvoz, načrtovanje, različice s ponovno potrditvijo, zanesljivi opomniki, papirna pot, izvozi in polni API sledijo v nadaljnjih mejnikih. Obstoječa merila pilota še vedno veljajo. Prototip ni namenjen resničnim uporabnikom.

Pot zaposlenega: prijava → moja skupina → novo obvestilo → naslov in besedilo → vrsta → prejemniki → predogled → objava → pregled odzivov.

Pot starša: splošna e-pošta ali neposredna prijava → seznam dovoljenih obvestil → vsebina in različica → prikazan otrok oziroma obseg → izrecna potrditev → potrdilo.

Predvideni zasloni:
| Zaslon | Nujne informacije in mejnik |
| --- | --- |
| Seznam | Naslov, otrok oziroma lastno obvestilo, manjkajoča potrditev ločeno od neodprte vsebine |
| Obvestilo | Besedilo in različica (A), priloge in rok (B) in obseg potrditve |
| Priprava | Vrsta, ciljna skupina, predogled vsebine in prejemnikov |
| Odzivi | Posamezni upravičenci, različica, potrditev, napaka pošiljanja, papirna pot (B) |
| P0 upravljanje | Osebe, povezave, veljavnost upravičenj (A), predogled uvoza (B) |

## 7. Praktični primeri M1 in dostave za M2

Vsi primeri so izmišljeni. E-pošta vsebuje splošno opozorilo in zaščiteno povezavo, brez imen otrok in javnih prilog. Vsebina je po prijavi. Lastni vrsti M1 sta dve; dostava za M2 je dodatna uporaba kanala, ne tretja vrsta seznanitve.

### 7.1 Informativno: knjižnica

Mejnik: A.

Pošiljatelj: knjižničarka. Prejemniki: upravičene osebe vseh oddelkov. Naslov: Urnik knjižnice v prihodnjem tednu. Priloga: brez. Rok: brez.

Besedilo: »Knjižnica bo prihodnji teden odprta med 8. in 12. uro. Izposoja po pouku ne bo mogoča. Naslednji teden spet velja običajni urnik.«

E-pošta: »V šolskem portalu je novo informativno obvestilo. Za ogled se prijavite.«

Prejemnik prebere; gumba za potrditev ni. Prikaz vsebine ne dokazuje dejanskega branja. Samodejni opomniki niso privzeti.

### 7.2 Informativno: dan odprtih vrat

Mejnik: A za besedilo; B za prilogo.

Pošiljatelj: vodstvo. Prejemniki: upravičene osebe vseh oddelkov. Naslov: Vabilo na dan odprtih vrat. Priloga: program PDF. Rok potrditve: brez.

Besedilo: »V četrtek ob 16. uri vas vabimo na dan odprtih vrat. Predstavili bomo dejavnosti in izdelke učencev. Program je v prilogi. Prijava ni potrebna.«

E-pošta: »V šolskem portalu je novo informativno obvestilo s prilogo.«

Prejemnik odpre program po prijavi. M1 ne vodi prijav in odprtja ne šteje kot udeležbo. Priloga sodi v naslednji razvojni mejnik.

### 7.3 Zahtevana seznanitev: športni dan

Mejnik: A za objavo in potrditev; B za priloge, opomnike, spremembe in papirno pot.

Pošiljatelj: razrednik. Prejemniki: upravičenci 7. a. Naslov: Zbirno mesto in oprema. Priloga: seznam opreme PDF. Rok: sreda ob 18. uri, konkretni datum določi avtor.

Besedilo: »Športni dan bo v petek. Zbor je ob 7.45 pred glavnim vhodom, vrnitev predvidoma ob 13. uri. Učenci naj imajo primerno obutev, pijačo in zaščito pred dežjem. Prosimo za potrditev seznanitve do navedenega roka.«

Pred gumbom je prikazan otrok in različica. Gumb: »Seznanjen/-a sem«. Gre za navodilo za že dogovorjen dogodek, ne pridobivanje dovoljenja za udeležbo.

E-pošta: »V šolskem portalu vas čaka obvestilo z zahtevano potrditvijo seznanitve.«

Odprtje ni potrditev. Opomnik prejme upravičenec, ki še ni potrdil aktualne zahtevane različice, po pravilih šole. Sprememba zbirnega mesta ustvari novo različico in novo zahtevo za potrditev. Prejšnja ostane v zgodovini.

### 7.4 Zahtevana seznanitev: začasni vhod

Mejnik: A za objavo in potrditev; B za priloge, opomnike, spremembe in papirno pot.

Pošiljatelj: vodstvo. Prejemniki: upravičenci prizadetih oddelkov. Naslov: Začasni vhod med obnovo. Priloga: skica; vse navodilo tudi v besedilu. Rok: pred začetkom spremembe.

Besedilo: »Od ponedeljka bo glavni vhod zaprt. Učenci bodo vstopali pri telovadnici. Pot bo označena. Prosimo, seznanite otroka in potrdite svojo seznanitev.«

Gumb: »Seznanjen/-a sem«. E-pošta je splošno opozorilo kot v prejšnjem primeru.

Potrditev prvega starša ne potrdi drugega. Ali za skupno obravnavo zadostuje eden, določi šola; posamezni statusi ostanejo ločeni. Pri papirni poti zaposleni posebej evidentira izročitev in morebitno papirno potrditev. Izročitev ni potrditev.

### 7.5 Dostava za M2: objavljen obrazec

Mejnik: I za dostavo prek testnega in nato pravega vmesnika; B za celoten postopek M2.

M2 objavi pregledani testni obrazec o objavi fotografij. Določi upravičence in M1 naroči: »V šolskem portalu vas čaka obrazec za odločitev.«

Povezava vodi v M2. Uporabnik tam prebere in odda izbire. Predhodna potrditev seznanitve v M1 ni potrebna. M1 hrani dostavo; M2 hrani obrazec, odločitev in potrdilo. Ta primer ni pravno potrjen obrazec za produkcijo.

### 7.6 Dostava za M2: opomnik

Mejnik: I za dostavo prek testnega in nato pravega vmesnika; B za celoten postopek M2.

M2 naroči opomnik osebi brez zahtevanega odziva in določi najpoznejši dovoljeni čas pošiljanja.

E-pošta: »V šolskem portalu vas še čaka obrazec za odločitev.«

Če uporabnik prej odgovori, M2 prekliče zahtevo, M1 pa pred pošiljanjem preveri potrebo. Zavrnitev je odziv in ni razlog za opominjanje kot pri pozabljenem odgovoru. Če preverjanje ni dosegljivo, je opomnik zadržan; po izteku se ne pošlje, razlog je viden. Že predane e-pošte ni mogoče priklicati; povezava pokaže aktualno stanje.

## 10. Merila demonstracije in prevzema

| Preizkus | Pričakovano |
| --- | --- |
| Informativna objava | Dovoljeni prejemniki vidijo vsebino; brez gumba za seznanitev |
| Odprtje zahtevane seznanitve | Še ni potrditve |
| Dvojni klik | Ena logična potrditev |
| Prvi starš potrdi | Drugi ostane nepotrjen |
| Neposreden naslov tujega vira | Dostop zavrnjen tudi mimo uporabniškega vmesnika |
| Učitelj drugega oddelka | Brez dostopa brez dodatnega pooblastila |
| Poštna napaka | Objavljeno obvestilo ostane; napaka dostave je vidna |
| Napačen CSV | Celovitost obstoječe evidence je ohranjena |
| Ponovni CSV | Brez podvojenih oseb in povezav |
| Odvzem pravice | Novo zaščiteno dejanje je zavrnjeno |
| Spremenjeno bistveno navodilo | Nova različica zahteva novo potrditev |
| M2 odda enako zahtevo dvakrat | Ena logična dostava |
| M2 prejme odziv pred opomnikom | Preklic in ponovno preverjanje ustavita zastarelo pošiljanje |
| Nedosegljiv M2 do izteka | Opomnik poteče in se po obnovi ne pošlje |
| Papirna izročitev | Ne ustvari elektronske potrditve |
| M2 zavrnitev | Ni predstavljena kot manjkajoči odziv |
| M2 izbere samo en namen | Drugi namen ostane ločen in ni samodejno potrjen |
| Preklic veljavne privolitve | Novo stanje in potrdilo; pot ostane dostopna tudi pri zaključenem/umaknjenem obrazcu |
| Nasprotujoča odziva | Blokada avtomatske izvedbe in ročna obravnava |
| Zahtevani odzivi več oseb | Čaka do izpolnitve potrjenega pravila |
| Avtor odobri lastno različico | Zavrnitev brez dovoljene, sledljive izjeme iz specifikacije M2 |
| Starš potrdi za vse prikazane otroke | Pred klikom jasen obseg; potrditev vsebuje prav ta obseg |
| Veljavnost opomnika samo v tihem času | Po izteku ni dostave, razlog DELIVERY_WINDOW_EXPIRED je viden |
| Skupna namestitev | Ponovljiva demonstracija brez produkcijskih poverilnic |

Prvih sedem vrstic tvori jedro prve demonstracije; ostale se dodajajo glede na mejnik. Vse produkcijske zahteve, tudi varnost, dostopnost, jeziki, kopije, hramba, pravni pregled M2 in vzdrževalec, ostanejo v obstoječih specifikacijah. Uspešna maturitetna naloga ne pomeni produkcijskega prevzema.

## 11. Odprte odločitve in naslednji sestanek

| Register | Kaj zahteva ta paket |
| --- | --- |
| D01 | Potrditev prvega prototipa in nadaljnjega obsega M1 |
| D02, D13 | Mentorji, ekipe, individualni izdelki, ure in mejniki |
| D03 | Nosilec skupnih gradnikov, izbira vzdrževane prijave in strokovni pregled |
| D04 | Testno in produkcijsko okolje, pošta, kopije ter stroški |
| D05, D06 | Jeziki, dostopnost, upravičenci in pravilo potrditve |
| D07, D09, D10 | Hramba, vzdrževanje, namestnik in produkcijski prevzem |
| D11, D16 | Izbrani postopek M2 in pravila za upravičence, tudi polnoletne |
| D12 | Potrditev pogodbe P0–M1–M2, shem in testov; konkretizacija skupnega vira identitet iz dosedanjega obsega |
| D08, D15 | Pravice prispevkov ter licenca kode in dokumentacije |
| D14 | Nosilec varnostne obravnave in nadomeščanje pred prvo kodo |

Na sestanku se najprej potrdita razumevanje primerov in obseg P0, nato delitev dela in API. Prva tehnična implementacija je odvisna od ustreznih odprtih odločitev v registru; datum nastanka tega paketa jih ne razreši.

Zgodovinski izvirniki in status potrjevanja so opisani v [evidenci izvorov](../projekt/izvor-gradiva.md).


### Pogoji in roki po registru

| Odločitve | Rok oziroma blokada |
| --- | --- |
| D01–D03, D11–D14, D16 | Pred začetkom odvisnega razvoja; ne zahtevamo M2 odločitev za nepovezano delo M1 |
| D04–D06 | Pred razvojem odvisnih funkcij |
| D08 | Pred sprejemom kode |
| D15 | Pred potrditvijo pogojev ponovne uporabe besedil |
| D07, D09, D10 | Pred produkcijskim pilotom |
| D09 drugi skrbnik in D14 obravnava | Že pred prvo kodo oziroma vključitvijo zunanjih ekip |

### Pojmovnik

- P0: minimalna skupna evidenca, prijava in pravice.
- Seznanitev: izrecna potrditev prikazanega obvestila; ločena od soglasja.
- Upravičena oseba: oseba, ki ji šola za konkreten postopek dovoli dostop ali dejanje.
- handed_off: pošta je predana strežniku; ne dokazuje prejema ali branja.
- Testni nadomestek: program z dogovorjenimi izmišljenimi odgovori, ki omogoča razvoj pred dokončanjem drugega modula.
