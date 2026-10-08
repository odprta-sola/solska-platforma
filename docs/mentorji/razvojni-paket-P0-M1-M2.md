# P0, M1 in M2 – razlaga in praktični primeri

Datum: 8. oktober 2026  
Status: spremljevalno gradivo k predlogu izvedbe

## Najprej preberite razvojno naročilo

[Cilj, obvezni obseg, vloge, vmesniki in prevzemne demonstracije](../projekt/razvojno-narocilo-P0-M1-M2.md) so določeni v razvojnem naročilu pobudnika. Ta dokument jih pojasnjuje skozi primere.

Razvojni zavod oceni izvedljivost podanega obsega, razporedi dijake in mentorje ter predlaga roke oziroma konkretne spremembe. Naloga mentorjev ni ponovno oblikovanje cilja projekta. Potrebni tehnični in institucionalni pregledi ostajajo po registru.

Tehnična dodatka: [P0 uporabniki](../moduli/P0-uporabniki.md) in [pogodba API](../arhitektura/vmesnik-P0-M1-M2.md). [Navodilo za pregled](navodilo-za-pregled.md) je ločeno.

## Kratek pojmovnik

- P0: skupna evidenca, prijava in pravice.
- Seznanitev: izrecna potrditev prikazanega obvestila.
- Upravičena oseba: oseba z dovoljenjem za konkretno vsebino oziroma dejanje.
- handed_off: predaja poštnemu strežniku, brez dokaza prejema ali branja.
- Testni nadomestek: dogovorjeni izmišljeni odgovori za vzporedni razvoj.
- Mejniki: T skupna tehnična priprava; A prvi M1; I povezava modulov; B celoten učni izdelek; C ločen produkcijski prevzem.

## Izhodišča in status dogovorov

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

Razvojno naročilo določa obvezni izhodiščni obseg pobudnika. Razporeditev 2–3 dijakov na modul ostaja predlog; osebe, ure in roke potrdi razvojni zavod. Tehnične vrzeli pogodbe se rešijo v skupni pripravi T. D01–D16 ostajajo v statusih registra.

## Razlika med P0, M1 in M2

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

## Praktični primeri M1 in dostave za M2

Vsi primeri so izmišljeni. E-pošta vsebuje splošno opozorilo in zaščiteno povezavo, brez imen otrok in javnih prilog. Vsebina je po prijavi. Lastni vrsti M1 sta dve; dostava za M2 je dodatna uporaba kanala, ne tretja vrsta seznanitve.

### Informativno: knjižnica

Mejnik: A.

Pošiljatelj: knjižničarka. Prejemniki: upravičene osebe vseh oddelkov. Naslov: Urnik knjižnice v prihodnjem tednu. Priloga: brez. Rok: brez.

Besedilo: »Knjižnica bo prihodnji teden odprta med 8. in 12. uro. Izposoja po pouku ne bo mogoča. Naslednji teden spet velja običajni urnik.«

E-pošta: »V šolskem portalu je novo informativno obvestilo. Za ogled se prijavite.«

Prejemnik prebere; gumba za potrditev ni. Prikaz vsebine ne dokazuje dejanskega branja. Samodejni opomniki niso privzeti.

### Informativno: dan odprtih vrat

Mejnik: A za besedilo; B za prilogo.

Pošiljatelj: vodstvo. Prejemniki: upravičene osebe vseh oddelkov. Naslov: Vabilo na dan odprtih vrat. Priloga: program PDF. Rok potrditve: brez.

Besedilo: »V četrtek ob 16. uri vas vabimo na dan odprtih vrat. Predstavili bomo dejavnosti in izdelke učencev. Program je v prilogi. Prijava ni potrebna.«

E-pošta: »V šolskem portalu je novo informativno obvestilo s prilogo.«

Prejemnik odpre program po prijavi. M1 ne vodi prijav in odprtja ne šteje kot udeležbo. Priloga sodi v naslednji razvojni mejnik.

### Zahtevana seznanitev: športni dan

Mejnik: A za objavo in potrditev; B za priloge, opomnike, spremembe in papirno pot.

Pošiljatelj: razrednik. Prejemniki: upravičenci 7. a. Naslov: Zbirno mesto in oprema. Priloga: seznam opreme PDF. Rok: sreda ob 18. uri, konkretni datum določi avtor.

Besedilo: »Športni dan bo v petek. Zbor je ob 7.45 pred glavnim vhodom, vrnitev predvidoma ob 13. uri. Učenci naj imajo primerno obutev, pijačo in zaščito pred dežjem. Prosimo za potrditev seznanitve do navedenega roka.«

Pred gumbom je prikazan otrok in različica. Gumb: »Seznanjen/-a sem«. Gre za navodilo za že dogovorjen dogodek, ne pridobivanje dovoljenja za udeležbo.

E-pošta: »V šolskem portalu vas čaka obvestilo z zahtevano potrditvijo seznanitve.«

Odprtje ni potrditev. Opomnik prejme upravičenec, ki še ni potrdil aktualne zahtevane različice, po pravilih šole. Sprememba zbirnega mesta ustvari novo različico in novo zahtevo za potrditev. Prejšnja ostane v zgodovini.

### Zahtevana seznanitev: začasni vhod

Mejnik: A za objavo in potrditev; B za priloge, opomnike, spremembe in papirno pot.

Pošiljatelj: vodstvo. Prejemniki: upravičenci prizadetih oddelkov. Naslov: Začasni vhod med obnovo. Priloga: skica; vse navodilo tudi v besedilu. Rok: pred začetkom spremembe.

Besedilo: »Od ponedeljka bo glavni vhod zaprt. Učenci bodo vstopali pri telovadnici. Pot bo označena. Prosimo, seznanite otroka in potrdite svojo seznanitev.«

Gumb: »Seznanjen/-a sem«. E-pošta je splošno opozorilo kot v prejšnjem primeru.

Potrditev prvega starša ne potrdi drugega. Ali za skupno obravnavo zadostuje eden, določi šola; posamezni statusi ostanejo ločeni. Pri papirni poti zaposleni posebej evidentira izročitev in morebitno papirno potrditev. Izročitev ni potrditev.

### Dostava za M2: objavljen obrazec

Mejnik: I za dostavo prek testnega in nato pravega vmesnika; B za celoten postopek M2.

M2 objavi pregledani testni obrazec o objavi fotografij. Določi upravičence in M1 naroči: »V šolskem portalu vas čaka obrazec za odločitev.«

Povezava vodi v M2. Uporabnik tam prebere in odda izbire. Predhodna potrditev seznanitve v M1 ni potrebna. M1 hrani dostavo; M2 hrani obrazec, odločitev in potrdilo. Ta primer ni pravno potrjen obrazec za produkcijo.

### Dostava za M2: opomnik

Mejnik: I za dostavo prek testnega in nato pravega vmesnika; B za celoten postopek M2.

M2 naroči opomnik osebi brez zahtevanega odziva in določi najpoznejši dovoljeni čas pošiljanja.

E-pošta: »V šolskem portalu vas še čaka obrazec za odločitev.«

Če uporabnik prej odgovori, M2 prekliče zahtevo, M1 pa pred pošiljanjem preveri potrebo. Zavrnitev je odziv in ni razlog za opominjanje kot pri pozabljenem odgovoru. Če preverjanje ni dosegljivo, je opomnik zadržan; po izteku se ne pošlje, razlog je viden. Že predane e-pošte ni mogoče priklicati; povezava pokaže aktualno stanje.

