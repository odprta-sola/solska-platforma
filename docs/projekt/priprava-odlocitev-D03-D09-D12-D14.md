# Predkodni pogoji in priprava odločitev D03, D09, D12 in D14

Datum pregleda: 9. oktober 2026

Status: priprava odločitev z izvedbenim zapisom potrjenih osebnih sprejemov in dogovorov; institucionalne potrditve, dejanski dostopi ter preostala merila ostajajo odprti
Preverjeni GitHub `main`: `28598e22f52799c9ec964ce8af3c8e4006d11d94`

Dokument pripravi izvedljive odločitve in dokazila. Merodajna ostajata [register](odlocitve.md) in [načrt priprave P0/T](priprava-referencnega-P0.md). Združitev tega predloga ne izpolni nobenega predkodnega pogoja. Izvedbeni zapis in statusi v tabelah ločijo osebno potrjene dogovore od preostalih predlogov. Predlagana pravila in številke zahtevajo izrecno potrditev.

## Preverjeno stanje in omejitve preverjanja

| Predmet | Neposredno preverjeno ob začetnem pregledu 9. 10. 2026 | Posledica |
| --- | --- | --- |
| [PR #29](https://github.com/odprta-sola/solska-platforma/pull/29) | Združen 9. 10. 2026 ob 14:10:29 UTC; merge commit je navedeni `main` | Stare razvojne veje niso osnova tega pregleda |
| [Preverjanje dokumentacije na main](https://github.com/odprta-sola/solska-platforma/actions/runs/37942219900) | Zaključeno uspešno za navedeni commit | Dokaz veljavnih povezav; ne dokaz implementacije ali varnosti |
| Vsebina repozitorija | Dokumentacija in skripta za povezave; brez aplikacije P0, OpenAPI in delujočih nadomestkov M1/M2 | T še ni izdelan ali sprejet |
| [D03 #12](https://github.com/odprta-sola/solska-platforma/issues/12), [D09 #18](https://github.com/odprta-sola/solska-platforma/issues/18), [D14 #23](https://github.com/odprta-sola/solska-platforma/issues/23) | Odprti, brez dodeljenih oseb in brez komentarjev | Imenovanja, razpoložljivost in dokazila niso evidentirani |
| [D08 #17](https://github.com/odprta-sola/solska-platforma/issues/17) | Odprt, status vsebine »Predlog«; licence kode v drevesu ni | EUPL 1.2 še ni sprejeta licenca |
| [D12 #21](https://github.com/odprta-sola/solska-platforma/issues/21) | Odprt; en [komentar z vprašanji N1–N7](https://github.com/odprta-sola/solska-platforma/issues/21#issuecomment-6066527084) | Komentar je seznam nalog po starejšem pregledu, ne potrditev trenutne pogodbe |
| Preostale odločitve | Vsi issuei D01–D16 (#10–#25) so odprti | Ta priprava ne sprosti samodejno drugih odvisnosti |
| D01 | Tabela še navaja »Mentor in pilotna šola«; opis razlikuje cilj pobudnika in presojo mentorjev | Morebitna sprememba nosilca se obravnava v #10, ne tiho v tabeli |

[SECURITY.md](../../SECURITY.md) in register evidentirata omogočeno zasebno prijavo. To je preverjeno stanje dokumentacije, ne nov praktični preizkus nastavitve GitHub. Dejanski dostop posameznih računov, obvestila, nadomeščanje in sprejem zasebne prijave v tem pregledu niso bili preizkušeni. Javni podatki o članstvu, avtorstvo commitov in dodelitev issuea tega ne dokazujejo.

Repozitorij navaja sodelovanje dveh zavodov po potrditvi pobudnika; pisna potrditev vodstev ni evidentirana. Osebni prispevek pobudnika pri P0/T je zapisana usmeritev. To ni imenovanje skupnega tehničnega nosilca ali zaveza njegovega podjetja.

## Izvedbeni zapis po začetnem pregledu

9. oktobra 2026 je pobudnik Mitja Pirih predlagal Aleksandarja Lazarevića iz GEPŠ za drugega skrbnika in izrecno odobril povabilo z vlogo Admin na repozitoriju. GitHub je zasebno navedeni kontakt povezal z računom [alexlandich](https://github.com/alexlandich). Kontaktnih naslovov v tem dokumentu ne objavljamo.

Po oddaji povabila je bilo 9. 10. 2026 ob 15:05 UTC v upravljanju dostopov neposredno preverjeno: račun alexlandich, vloga admin, stanje **Pending Invite / Awaiting alexlandich’s response**. Povabilo je poslano; sprejem povabila in aktiven dostop še nista potrjena. To je neposredno opazovan rezultat, ne zgolj predlog.

9. oktobra 2026 je Mitja Pirih izrecno potrdil, da osebno prevzame vlogo nosilca obravnave zasebnih varnostnih prijav D14, ter podprl predlog Aleksandarja Lazarevića za namestnika. Mitjev osebni sprejem vloge je potrjen; Aleksandarjev sprejem odgovornosti namestnika in drugega skrbnika še ni evidentiran. Ta dogovor ne pomeni obveznosti Mitjevega podjetja. Mitja je istega dne izrecno dovolil javni zapis imen, vlog in statusa potrditve; zasebni kontaktni naslov je izključen.

Razlog predlagane razdelitve je jasen nosilec zasebne obravnave in nadomeščanje z drugim skrbnikom. Mitja je 9. oktobra 2026 potrdil koordinacijsko naravo svoje vloge in pregled obvestil o novih varnostnih prijavah vsaj enkrat vsak delovni dan, od ponedeljka do petka, razen praznikov in dogovorjenih odsotnosti. Izrecno je dovolil tudi javni zapis tega dogovora. To ni zagotovilo stalne dežurne službe ali rok za odpravo napake.

Mitja je istega dne za javni dogovor D14 potrdil cilj človeške zasebne potrditve prejema v dveh delovnih dneh od prejema prijave. Razlog je, da prijavitelj prejme jasno povratno informacijo; ta cilj ne določa roka odprave napake.

Mitja je potrdil tudi cilj začetne ocene v petih delovnih dneh od prejema prijave: vpliv, prizadeti obseg in nujnost ukrepanja oziroma jasno navedene manjkajoče informacije. Obravnavo koordinira in po potrebi vključi tehnično pomoč; konkretni tehnični sodelavec s tem ni imenovan. Razlog je zgodnja razjasnitev tveganja in naslednjih korakov.

Mitja je potrdil tudi cilj načrta ukrepanja v petih delovnih dneh po začetni oceni, najpozneje v desetih delovnih dneh od prejema prijave. Prijavitelju se zasebno sporočijo predvideni ukrepi in termin naslednje posodobitve; rok odprave se določi glede na konkreten primer. Razlog je, da začetni oceni sledi jasen načrt obravnave.

Mitja je potrdil tudi zasebno posodobitev prijavitelju vsaj vsakih pet delovnih dni, dokler je obravnava odprta. Posodobitev vsebuje stanje in naslednji korak tudi takrat, ko popravka še ni; razlog je redno obveščanje brez dolgotrajne tišine.

Mitja je 9. oktobra 2026 potrdil, da ob zaznavi kritične prijave med dogovorjeno pokritostjo takoj prednostno začne obravnavo in koordinacijo omejitve škode v okviru svojih pooblastil. Primer sta javno razkrito geslo ali sum nepooblaščenega dostopa; to nista ugotovljeni napaki projekta. Razlog je hitro omejevanje izpostavljenosti pri nujnih primerih. Dogovor ne uvaja pokritosti 24/7 in ne pomeni zagotovila takojšnje odprave.

Mitja je 9. oktobra 2026 potrdil slovenski koledar za štetje rokov: delovni dnevi so od ponedeljka do petka brez zakonsko določenih dela prostih dni v Sloveniji, časovni pas je Europe/Ljubljana. Razlog je enotno štetje rokov in pregledov. Mitja je 9. oktobra 2026 potrdil štetje rokov od prejema v zasebni kanal: dan prejema ne šteje, prvi naslednji delovni dan je dan 1, cilj pa poteče ob koncu zadnjega delovnega dne po potrjenem slovenskem koledarju in času Europe/Ljubljana. Razlog je nedvoumno štetje, neodvisno od trenutka, ko obravnavalec prijavo prebere. Natančna ura pregleda, obravnava nenapovedane odsotnosti, izvedba izbranega e-poštnega obveščanja in eskalacija ob nedosegljivosti obeh še niso potrjeni; razpoložljivost predlaganega namestnika ni potrjena. Potrditev sodelujočih zavodov za D09 ter preizkus zasebnih prijav in obvestil ostajata potrebna. Mitjev osebni sprejem skupnega tehničnega vodenja je evidentiran pri D03 spodaj; imenovanje s strani zavodov še ni potrjeno. D09/D14 ostajata odprta; predkodni pogoj še ni izpolnjen.


Mitja je 9. oktobra 2026 potrdil način predaje pred napovedano odsotnostjo: namestniku preda odprte prijave in spremljanje novih ter pred odhodom pridobi njegovo izrecno potrditev prevzema. Dogovorjeni roki tečejo naprej in se ob predaji ne ponastavijo. Aleksandar lahko prevzame šele po izrecnem sprejemu vloge in preverjenem dostopu. Razlog je neprekinjena obravnava s potrjenim prevzemom; ta zapis še ne dokazuje izvedene predaje ali Aleksandarjevega sprejema.

Mitja je 9. oktobra 2026 izrecno potrdil e-pošto kot zadosten način nujnega zasebnega obveščanja med nosilcem in namestnikom. Naslovi se hranijo zasebno in niso objavljeni. Razlog je Mitjeva ocena, da e-pošta za ta dogovor zadošča. Aleksandarjev sprejem, dogovor o spremljanju tega kanala in praktični preizkus dostave ter opaženega obvestila ostajajo odprti; izbrani kanal ne dokazuje dejanskega odziva.

Mitja je 9. oktobra 2026 navedel, da kandidata za zasebno eskalacijo nujne prijave ob nedosegljivosti nosilca in namestnika še ni. Oseba oziroma izvedljiva rezervna pot ni določena; ta odločitev D14 ostaja odprta in je treba pred izpolnitvijo predkodnega pogoja potrditi konkretno ureditev.

## Zaporedje sprostitve dela

| Korak | Potreben rezultat | Delo, ki ga rezultat sprosti |
| --- | --- | --- |
| Priprava | Ta predlog, obrazci odločitev in scenariji | Dokumentacijsko usklajevanje; predlog shem brez implementacije |
| D09 predkodni del + D14 | Drugi skrbnik, nosilec prijav in namestnik; sprejeti odzivni cilji, dejanski dostopi in preverjena zasebna pot | Varnostni pogoj pred prvo kodo oziroma vključitvijo zunanjih ekip |
| D03 | Potrjen tehnični nosilec, čas, nadomeščanje, lastništvo gradnikov in dogovor o tehnologiji ter skupnih varnostnih funkcijah | Prva koda P0 oziroma primerjalni prototip, ko je izpolnjen tudi varnostni pogoj |
| D08 | Licenca, pravice prispevkov, navodila in skladnost odvisnosti | Sprejem kode v repozitorij |
| D12 | Pregledana pogodba/OpenAPI, dogovorjeni pogodbeni testi in potrditev nosilca ter mentorjev | Implementacija API, na katerega se vežejo P0/M1/M2 |
| T in druge predhodne odločitve | Celoten neodvisni človeški prevzem T ter ustrezne odprte odločitve iz registra | Odvisni razvoj A/I |
| C | Ločene organizacijske, vsebinske, pravne, varnostne in operativne potrditve | Morebitni produkcijski pilot |

Najstrožji pogoj za posamezno dejanje velja tudi pri lokalnem prototipu. D09 se po izpolnitvi zgodnjega dela ne zapre v celoti: vzdrževanje, podpora in obnova pred produkcijo ostanejo odprti.

## D09/D14: predlog konkretne organizacije

### Vloge, dostopi in potrjevanje

| Vloga | Kaj mora oseba izrecno sprejeti | Zahtevan dokaz | Kdo potrdi po registru |
| --- | --- | --- | --- |
| Skrbnik repozitorija | Upravljanje repozitorija in varnostne poti; preverjanje pravic | Identificiran individualni račun, dejanska vloga in opravljen preizkus | Nosilec projekta in skrbnik za D14; zavodi za D09 |
| Drugi skrbnik | Nadomeščanje upravljanja in samostojen dostop do novih zasebnih prijav | Sprejeto povabilo, preverjena pravica in preizkus brez pomoči prvega skrbnika | Sodelujoči zavodi (D09) |
| Nosilec obravnave prijav | Spremljanje, potrditev prejema, ocena resnosti, koordinacija ukrepa in komunikacija s prijaviteljem | Pisni sprejem vloge, dosegljivost in uspešen preizkus obvestila ter odgovora | Nosilec projekta in skrbnik (D14) |
| Namestnik obravnave | Prevzem ob odsotnosti ali prekoračitvi dogovorjenega cilja | Samostojen ogled nove prijave, odgovor in zasebno evidentiran prevzem | Nosilec projekta in skrbnik (D14) |

Predlog: za začetek zadoščata dve različni človeški osebi z individualnima računoma, če vsaka izrecno sprejme potrebne združene vloge. Drugi skrbnik je lahko tudi namestnik prijav. En človek z dvema računoma ne zagotavlja nadomeščanja. Neodvisni pregledovalec T ne sme prevzemati svoje kode, tudi če ima druge vloge.

Po [uradnih dovoljenjih GitHub](https://docs.github.com/en/code-security/reference/permissions/repository-security-advisory) imajo dostop do vseh varnostnih advisoryjev lastniki repozitorija/organizacije, security managers in računi z vlogo admin. Sodelovanje v posameznem advisoryju ne dokazuje dostopa do prihodnjih prijav. Predlog za dva skrbnika je preverjena vloga admin na tem repozitoriju; ne predlagamo samodejnega lastništva celotne organizacije. Druga ureditev je sprejemljiva le z dokazom vseh potrebnih opravil in nadomeščanja. Običajni write/maintain ali javna navedba računa nista zadosten dokaz.

### Zasebni kanal in preizkus dostopa

Predlagani primarni kanal ostane [GitHub Report a vulnerability](https://github.com/odprta-sola/solska-platforma/security/advisories/new). Osebnega naslova ali drugega rezervnega kanala ne dodajamo brez izrecne določitve in preizkusa. Dogovor mora določiti tudi ravnanje ob nedostopnem GitHubu in kam namestnik zasebno zabeleži prevzem.

Postopek za potrjena skrbnika:

1. Oba v svojih prijavah preverita sprejeto povabilo, dejansko vlogo, dostop do Security in nastavitve obvestil. Povabilo v čakanju ne šteje.
2. V Security preverita dejansko omogočeno zasebno prijavo. Gumb in obrazec preveri tudi dogovorjeni preizkuševalec brez admin/security pravic. Skrbnik po [navodilih GitHub](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/report-privately) praviloma ustvari osnutek advisoryja; to samo po sebi ne preizkusi zunanje poti prijavitelja.
3. Preizkuševalec odda dogovorjeno neobčutljivo testno prijavo, jasno označeno »TEST D14 — ni dejanska ranljivost«. Uporabi izmišljene podatke. Imenovanje preizkuševalca in izvedbo uskladita skrbnika; ta predlog prijave še ne odda.
4. Oba skrbnika neodvisno preverita vidnost iste nove zasebne prijave. Nosilec preveri prejem obvestila, odgovori zasebno; namestnik nato samostojno odgovori in zabeleži prevzem. Preizkus ne temelji zgolj na ročni naknadni dodelitvi pravic do te prijave.
5. Zabeležita čas oddaje, prejem obvestil, odgovora in prevzema. Preverita, da vsebina ni objavljena v javnih Issues. Test zapreta zasebno, brez javne objave advisoryja ali zahteve za CVE.
6. Zasebno ohranita dokazne posnetke in podrobnosti pravic. V D09/D14 objavita le primeren povzetek: datum, preverjeni vlogi/računa, preizkušena opravila, uspeh ali napaka in potrjevalec. Ne objavita zasebne vsebine ali kontaktov. Ponovita preizkus ob menjavi skrbnika ali spremembi pravic.

GitHubova [obvestila o zasebnih prijavah](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository) so odvisna tudi od naročnine na dejavnost/varnostna opozorila in uporabnikovih nastavitev. Zato preverjamo obvestilo in odgovor, ne le ogled strani.

### Odzivni cilji za potrditev

Cilji veljajo za pripravo dokumentacijske/razvojne faze z izmišljenimi podatki. Mitja je 9. oktobra 2026 potrdil svoj pregled novih prijav vsak delovni dan ter cilja potrditve prejema v dveh in začetne ocene v petih delovnih dneh od prejema prijave. Potrdil je tudi načrt ukrepanja v petih delovnih dneh po začetni oceni, najpozneje v desetih od prejema prijave. Potrjena je tudi posodobitev prijavitelju vsaj vsakih pet delovnih dni med odprto obravnavo. Potrjen je tudi takojšen prednostni začetek obravnave kritične prijave ob zaznavi med dogovorjeno pokritostjo. Cilje je osebno potrdil Mitja; koledar je potrjen v izvedbenem zapisu; štetje rokov od prejema je potrjeno spodaj; način predaje pred napovedano odsotnostjo je osebno potrdil Mitja; sprejem namestnika in izvedba predaje ostajata odprta.

| Korak | Največji čas | Merljiv rezultat | Status |
| --- | --- | --- | --- |
| Potrditev prejema | 2 delovna dneva od prejema prijave | Človeški zasebni odgovor in imenovan obravnavalec | Mitja potrdil 9. 10. 2026; sprejem namestnika in izvedba nadomeščanja še odprta |
| Začetna ocena resnosti | 5 delovnih dni od prejema prijave | Vpliv, prizadeti obseg in stopnja resnosti ali jasno navedene manjkajoče informacije | Mitja potrdil 9. 10. 2026; sprejem namestnika in izvedba nadomeščanja še odprta |
| Vsebinski odziv oziroma načrt ukrepanja | 5 delovnih dni od ocene, največ 10 od prejema | Odločitev o obravnavi, omejitveni ukrep, odgovorna oseba in naslednja posodobitev | Mitja potrdil 9. 10. 2026; sprejem namestnika in izvedba nadomeščanja še odprta |
| Kritična prijava oziroma razkritje skrivnosti | Takojšen prednostni začetek obravnave ob zaznavi med dogovorjeno pokritostjo | Začetek obravnave in koordinacija omejitve škode v okviru pooblastil | Mitja potrdil 9. 10. 2026; sprejem namestnika in izvedba nadomeščanja še odprta |
| Posodobitev odprte obravnave | Največ vsakih 5 delovnih dni | Napredek, preostalo tveganje in naslednji korak | Mitja potrdil 9. 10. 2026; sprejem namestnika in izvedba nadomeščanja še odprta |

Potrjeni koledar (Mitja, 9. 10. 2026): delovni dnevi od ponedeljka do petka brez zakonsko določenih dela prostih dni v Sloveniji, časovni pas Europe/Ljubljana. Potrjeno štetje rokov od prejema v zasebni kanal (Mitja, 9. 10. 2026): dan prejema ne šteje; prvi naslednji delovni dan je dan 1, rok poteče ob koncu zadnjega delovnega dne. Primer: prijava v petek pomeni cilj potrditve prejema do konca torka, če vmes ni dela prostih dni. Mitjev ritem pregleda je potrjen v izvedbenem zapisu; natančne ure, razpoložljivost namestnika in izvedba pokritja odsotnosti še niso potrjeni. Potrjena predaja pred napovedano odsotnostjo (Mitja, 9. 10. 2026): nosilec preda odprte prijave in spremljanje novih, pred odhodom pridobi namestnikovo izrecno potrditev prevzema, roki pa tečejo naprej brez ponastavitve. Prevzem je pogojen s sprejemom vloge in preverjenim dostopom namestnika. Predlog za preostale primere, ki še ni potrjen: manjkajoče informacije ne opravičijo tišine; ob zamudi ciljnega odziva prevzame namestnik. Če sta oba nedosegljiva, mora dogovor določiti potrjeno zasebno eskalacijsko pot in odgovorno vlogo.

Odziv pomeni odgovor in načrt, ne obljubljenega popravka v tem času. Čas odprave se določi po presoji konkretnega primera. Pokritost 24/7, datum prve kode in produkcijski odzivni roki niso določeni. Če ta predlog ni izvedljiv, se pred kodo potrdi druga merljiva ureditev.

### Dokaz zaključka

- D09: zgodnje merilo za drugega skrbnika izpolnjeno s potrditvijo sodelujočih zavodov in povezavo na neobčutljiv povzetek preverjanja. Poznejša merila ostanejo neoznačena; issue ostane odprt.
- D14: nosilec in namestnik izrecno sprejmeta vlogo, pokritost, odzivne cilje, nadomeščanje in zasebno eskalacijo; dejanski preizkus uspe. Potrditev nosilca projekta in skrbnika navede datum, različico tega dogovora, razlog in posledice. Nato se uskladijo SECURITY.md, register in merila issuea.
- Predkodni prehod se evidentira posebej. Dodelitev issuea ali združitev dokumenta ga ne nadomesti.

## D03: mandat tehničnega nosilca in predaja gradnikov

### Osebni sprejem tehničnega vodenja — 9. oktober 2026

Mitja Pirih je izrecno osebno sprejel vlogo skupnega tehničnega nosilca D03: arhitekturo, pogodbo API, skupne gradnike in usklajevanje z mentorji. Sprejem in nadaljnji izrecno potrjeni organizacijski dogovori D03 se javno evidentirajo po njegovem pritrdilnem odgovoru na vprašanje o sprejemu vloge in javnem zapisu. Razlog je enotno tehnično usklajevanje skupnih gradnikov in odločitev. Ta osebni sprejem ne pomeni obveznosti Mitjevega podjetja.

Mitja je 9. oktobra 2026 dovolil zapis približno treh ur načrtovanega dela tedensko ob podpori AI za tehnično vodenje, usklajevanje in preglede ter izrecno pojasnil, da razvoj P0 ni vključen v ta okvir. Obseg teh nalog se prilagaja tej kapaciteti; roki izvedbe niso obljubljeni. Čas razvoja P0 se vodi ločeno in še ni ocenjen. Razlog je merljiv planski okvir, ki loči vodenje od razvoja referenčnega jedra.

Mitja je 9. oktobra 2026 določil začetni model D03 brez ločenega tehničnega namestnika; Aleksandarja za to vlogo ne predlagamo. To je pobudnikov potrjeni predlog organizacije, ki ga morajo sprejeti sodelujoči zavodi. Razlog je omejena sestava ekipe in razporeditev dela. Mitja je 9. oktobra 2026 potrdil ravnanje ob svoji odsotnosti: nove skupne tehnične odločitve in spremembe pogodbe API počakajo na njegov pregled, delo po že potrjenih dogovorih pa lahko poteka naprej. Razlog je nadaljevanje dogovorjenega dela ob ohranjeni odgovornosti za skupne spremembe. Potrditev zavodov ter konkretni pogoji in izvedba predaje posameznih gradnikov še ostajajo odprti. Osebno sprejeta priprava gradnikov je evidentirana spodaj; obstoječe merilo #12 o gradnikih in nadomeščanju ostaja odprto. Ta odločitev ne spreminja ločenega dogovora D14 o predlaganem namestniku za varnostne prijave.

Potrditev imenovanja, časovnega okvira in modela brez ločenega tehničnega namestnika s strani sodelujočih zavodov, formalna potrditev nosilcev in pogojev predaje posameznih gradnikov ter potrditev Mitjeve tehnološke izbire in skupnih varnostnih funkcij še niso urejeni; osebno sprejeti način ravnanja ob odsotnosti morajo sprejeti tudi zavodi. Aleksandarju ta zapis ne dodeljuje novih odgovornosti. D03 ostaja odprta; osebni sprejem še ne izpolni celotnega predkodnega pogoja.

Mitja je 9. oktobra 2026 izrecno osebno prevzel pripravo in predajo referenčnega paketa T ob pomoči AI: P0, skupno prijavo, predlog pogodbe API in teste, nadomestka M1/M2 ter ponovljivo razvojno namestitev. Razlog je določitev enega človeškega nosilca izvedbe in predaje skupne razvojne osnove. Čas razvoja se oceni ločeno; razvoj P0 ostaja izključen iz triurnega tedenskega okvira. Osebni prevzem priprave ne pomeni izdelanega paketa, njegovega neodvisnega prevzema ali obveznosti produkcijskega vzdrževanja.

### Predlog spremembe prevzema T: Mitja ob pomoči AI

9. oktobra 2026 je Mitja določil, da želi pregled in prevzem T opraviti osebno ob pomoči AI; Aleksandar za pregledovalca T ni predlagan. Osebna izbira izvajalca je potrjena. Sedanji [načrt P0/T na main](priprava-referencnega-P0.md#človeški-prevzem) zahteva človeka, ki ni izdelal prevzemane kode, in neodvisen človeški pregled avtorizacije, obsegov, kontaktnega klica ter CSV uvoza. Zato je sprememba merila formalnega prevzema še predlog za potrditev sodelujočih zavodov in mentorjev.

Predlagano nadomestno merilo: Mitja osebno izvede celoten človeški prevzem ob pomoči AI, vključno s samostojno svežo namestitvijo, pregledom izvorne kode in vsemi devetimi scenariji sedanjega načrta. Pregled avtorja in AI se evidentira pod tema nazivoma; ne označi se kot neodvisen človeški pregled.

Predlog dokazil in postopka za tak prevzem:

1. Evidentirajo se točen commit paketa, navodila, izmišljeni podatki in preizkušeno razvojno okolje.
2. Mitja po navodilih izvede svežo namestitev in vse človeške scenarije, vključno s tipkovnico ter osnovnim bralnikom zaslona. Evidentira dejanske rezultate in ponovitve po popravkih.
3. Pogodbeni testi preverijo dovoljene in zavrnjene klice, odvzem pravic, izpade, ponovitve in selektivni preklic po potrjeni pogodbi D12.
4. AI opravi dodaten pregled kode in dokazil; zabeležijo se uporabljeni model oziroma orodje, različica, obseg pregleda in ugotovitve. Zapis AI sam ne dokazuje izvedenega testa.
5. Mitja razreši ugotovitve ali jasno evidentira odprte omejitve; v sprejemnem zapisniku navede, da je tudi nosilec priprave kode.
6. Zavodi in mentorji pred formalnim sprejemom T potrdijo spremembo merila in sprejemni zapis. Produkcijski prevzem ostane ločen.

Razlog predloga je izvedljivost v trenutni ekipi. Posledica je opustitev ločitve avtorja in človeškega pregledovalca; dodaten pregled AI te ločitve ne vzpostavi. Dokler sprememba ni potrjena, ostaja merodajen sedanji načrt. To vprašanje se reši pred formalnim prevzemom T in sprostitvijo A/I; ne ustvarja novega roka ali že izvedenega prevzema.

### Predlog mandata

Sodelujoči zavodi potrdijo eno odgovorno človeško osebo za skupno tehnično odločanje in razpoložljivost. Mitjev začetni predlog je brez ločenega tehničnega namestnika; zavodi morajo potrditi tudi osebno sprejeti način ravnanja ob odsotnosti iz izvedbenega zapisa. Pobudnik ostane pripravljavec P0/T po sedanji usmeritvi; lahko je tudi tehnični nosilec samo po ločenem izrecnem imenovanju. AI in podjetje pobudnika nista samodejna nosilca.

Mandat naj pokrije arhitekturo, skupno prijavo, identitete in dovoljenja, D12/OpenAPI, združljivost modulov, tehnični pregled sprememb in predajo ekipam. Določi se način reševanja nesoglasij z mentorji. Vsebinska in pravna pravila šole ter produkcijski prevzem ostanejo pri svojih potrjevalcih.

| Gradnik/izdelek | Osebni sprejem oziroma predlagana vloga | Kaj mora biti predano | Preostale potrditve |
| --- | --- | --- | --- |
| P0: osebe, povezave, dodelitve, dovoljenja in osnovni CSV | Mitja osebno sprejel pripravo in predajo ob pomoči AI | Model, sledljiv uvoz, scenariji odvzema in testni nabor | Potrditev zavodov, ločen čas razvoja in konkretni pogoji predaje |
| Skupna lokalna prijava in servisna avtentikacija | Mitja osebno sprejel pripravo in predajo ter lokalno uporabniško prijavo za T prek Django; servisni mehanizem še za D12 | Vzdrževana komponenta, zaščita sej/CSRF, odjava, omejena servisna dovoljenja | Servisna avtentikacija D12, potrditev mentorjev/zavodov, izvedba in lastnik posodobitev po predaji |
| OpenAPI, šifranti in pogodbeni testi | Mitja osebno sprejel pripravo predloga in testov ter predajo; pregled in potrditev mentorjev še odprta | Pogodba za vse tri smeri klicev in ponovljivi dovoljeni/zavrnjeni primeri | Imenovani pregledovalci in potrditev D12 |
| Nadomestka M1/M2 | Mitja osebno sprejel pripravo in predajo ob pomoči AI po potrjeni pogodbi | Zagon, izpadi, ponovitve, selektivni preklic; ista shema kot pravi moduli | Pogoji predaje, potrditev zavodov in D12 |
| Razvojna namestitev in prestrezna pošta | Mitja osebno sprejel pripravo razvojnega paketa in predajo ob pomoči AI | Ponovljiva namestitev z izmišljenimi podatki, skrivnosti zunaj repozitorija | Ciljno razvojno okolje, dostopi in lastnik po predaji |
| Prevzem T | Mitja je izbral osebni pregled ob pomoči AI; sprememba merila še predlog | Sveža namestitev, pregled kode, dejanski rezultati vseh scenarijev in dodatnega pregleda AI | Potrditev spremembe sedanjega neodvisnega človeškega merila; čas in formalni sprejem T |

Za vsak gradnik se v dogovoru vpiše dejanski nosilec, način ravnanja ob odsotnosti skladno z merilom #12 o nadomeščanju, obseg vzdrževanja do predaje in meja odgovornosti po T. Nadomeščanje pri gradniku ne pomeni samodejnega imenovanja ločenega tehničnega namestnika D03. Oseba lahko vodi več gradnikov. Izdelava gradnika ne ustvari avtomatične obveznosti produkcijskega vzdrževanja.

### Obrazec razpoložljivosti brez izmišljene ocene

| Podatek za dogovor | Polje, ki ga izpolni imenovani nosilec |
| --- | --- |
| Obdobje sodelovanja | Ni določeno |
| Razpoložljive ure ali druga merljiva kapaciteta | Mitja: približno 3 ure načrtovanega dela tedensko ob podpori AI za tehnično vodenje, usklajevanje in preglede; razvoj P0 je izključen in se oceni ločeno; potrditev zavodov še odprta |
| Običajna pokritost in odsotnosti | Mitja je osebno potrdil: nove skupne tehnične odločitve in spremembe API ob odsotnosti počakajo na njegov pregled; delo po potrjenih dogovorih lahko poteka naprej. Redni termini in sprejem zavodov še niso določeni. |
| Ločen tehnični namestnik | Mitjev potrjeni začetni predlog: brez te vloge; sprejem zavodov še odprt; osebno ravnanje ob odsotnosti potrjeno spodaj |
| Izdelki T in pričakovano trajanje po izdelkih | Ocena po potrditvi tehnologije in pregleda; brez obljubljenega datuma |
| Pregledovalec T in njegov termin | Mitja želi osebni pregled ob pomoči AI; sprememba neodvisnega človeškega merila in termin še nista potrjena |
| Predaja ob odhodu | Potrjen seznam dokumentacije, verzij, pravic in zasebne predaje potrebnih skrivnosti |

Pred prvo kodo se evidentira tudi način osebnega, nekomercialnega izvajanja pobudnika iz [načrta P0](priprava-referencnega-P0.md#projektni-pogoji-in-sled-izvora): obseg, izvor kode, uporaba AI, avtorstvo in odsotnost avtomatične zaveze podjetja. Pravice ostanejo za D08; ta zapis jih ne razreši.

### Tehnični predlog za pregled

Mitja je 9. oktobra 2026 osebno sprejel Django 5.2 LTS (Python) in PostgreSQL kot svojo izbiro tehnološke osnove D03. Razlog je izbira vzdrževanega ogrodja in relacijske baze za skupno razvojno osnovo; pregled znanja ekip in potrditev mentorjev še sledita. Django je že kandidat v [arhitekturnih izhodiščih](../arhitektura/izhodisca.md). [Uradni pregled podpore](https://www.djangoproject.com/download/), ponovno preverjen 9. 10. 2026, za vejo 5.2 navaja podaljšano podporo do aprila 2028.

Predlog za izvedbo: ob začetku se uporabi najnovejša podprta varnostno popravljena izdaja veje Django 5.2; konkretna različica PostgreSQL se izbere in evidentira po preverjanju podpore ter združljivosti. Skupen HTTPS vhod in ponovljiv kontejnerski razvojni paket ostajata predlog za nadaljnjo obravnavo. Osebna izbira osnove ne nadomesti potrditve mentorjev, podrobnega dogovora o skupnih varnostnih funkcijah ali D12.

Predlagamo eno namestitev s tremi logično ločenimi moduli in skupno prijavno komponento. Ni zahteve po treh strežnikih. To, ali bodo moduli procesno ločeni, potrdi D12. Vsak modul upravlja svojo shrambo in migracije; ne bere tujih poslovnih tabel. Izbira fizične baze ne sme izničiti meja API in pravic.

Mitja je 9. oktobra 2026 sprejel lokalno prijavo za prvi paket T z uporabniškim imenom in geslom prek [Django prijavne komponente](https://docs.djangoproject.com/en/5.2/topics/auth/default/). Vsaka oseba ima svoj račun tudi pri skupnem kontaktnem e-poštnem naslovu; za T se vnaprej pripravijo individualni testni računi. ArnesAAI se obravnava pozneje. Razlog je ponovljiv začetni prevzem z ločenimi identitetami. To je osebna izbira smeri D03; potrditev mentorjev, pogodba D12 in izvedba še ostajajo odprte.

Tehnični predlog izvedbe uporablja Django seje in zaščito CSRF ter uporabniška imena, ločena od kontaktnih e-poštnih naslovov. Širša aktivacija/obnova pri skupnem naslovu ostane pred B. Testni računi še niso ustvarjeni. P0 poveže preverjen račun s stabilnim person_id. Splošna prijava ne zadošča za šolsko avtorizacijo: ta mora preveriti konkretne povezave, pooblastila in obseg brez pozitivnega predpomnjenja. Django ModelBackend predpomni dovoljenja na uporabniškem objektu; tega ne smemo nekritično uporabiti namesto aktualnega preverjanja P0.

Servisna identiteta ostane ločena od seje uporabnika. Konkretni vzdrževani mehanizem, omejitve dovoljenj, delegiranje, rotacija in hramba skrivnosti so obvezne odločitve D12; ne uvajamo lastnega podpisovanja žetonov. P0-jeva aktivacijska pošta ne potrebuje poslovnega API M1. Testna e-pošta se prestreže lokalno. Trajna opravila morajo preživeti izpad; o orodju za vrsto se odloči po potrditvi trajnosti in atomarnosti, brez predpostavke, da pomnilniška vrsta zadostuje.

Tehnični nosilec in mentorji preverijo znanje ekip, življenjsko dobo podpore, licence odvisnosti, cilj namestitve ter zmožnost predaje. Če ne sprejmejo te osnove, predlagajo drugo s primerljivimi zahtevami. Pred potrditvijo ne nameščamo ogrodja, ne ustvarjamo migracij, ne pišemo prijavnega prototipa ali aplikacijskih testov.

### Merilo za zaključek D03

Odločitev zavodov vsebuje imenovanje in sprejem mandata, kapaciteto, sprejem začetnega modela brez ločenega tehničnega namestnika, ravnanje ob odsotnosti, lastnike vseh skupnih gradnikov ter predajo; tehnični nosilec in mentorji potrdijo tehnološko osnovo in skupne varnostne funkcije. V #12 in registru se navedejo datum, različica, razlog in posledice. Imenovanje ni prevzem T. Po sedanjem načrtu mora biti neodvisni pregledovalec dejansko zagotovljen pred prevzemom T; alternativni predlog Mitja + AI zgoraj zahteva izrecno potrditev spremembe merila pred formalnim sprejemom T.

## D12: seznam odločitev in nasprotnih primerov

[Pogodba P0–M1–M2](../arhitektura/vmesnik-P0-M1-M2.md) ostaja kanonični osnutek. Naslednja tabela je priprava pregleda, ne sprememba pogodbe. Tehnične odločitve potrdita skupni tehnični nosilec in mentorji; šola dodatno določi poslovna pravila po D05–D07, D11 in D16. Za učne preizkuse se uporabljajo izrecna izmišljena pravila, brez trditve o produkcijski ustreznosti.

| Točka in sled | Kaj mora biti odločeno | Predlog za pregled | Obvezni nasprotni primer oziroma dokaz |
| --- | --- | --- | --- |
| C01 / N1: scope_ref, več otrok | Izdajatelj, veljavnost, odvzem, šola, oseba, otrok, vir, dejanja in povezava z grants.scope_key | En neprosojen sklic za konkreten dovoljeni obseg; P0 preveri podlago, modul svoj vir. Za več otrok izrecen seznam obsegov; ne sklepa iz oddelka ali skupnega kontakta. scope_key je ključ odobrene podlage, ne dokaz pravice. | Enemu staršu odvzamemo povezavo do enega od dveh otrok: nova skupinska potrditev ne sme potrditi odvzetega obsega; ostale pravice se ne izbrišejo. Določiti atomarnost ali izrecno delno obravnavo. |
| C02 / N2: oznake za prikaz | Kdo vrne imena/oznake otrok, oddelkov in prejemnikov ter kdo jih vidi | Omejene oznake iz P0 v avtoriziranem kontekstu; brez kontaktov in občutljivih razlogov. Modul hrani ID, zgodovinski dokazni posnetek le po D07. | Uganjen ID druge družine ne vrne imena; sprememba imena ne prepiše zgodovine odločitve. |
| C03 / N4: jezik | Vir jezika, dovoljeni jeziki, odsoten prevod, nadomestni jezik in izrecna preglasitev | Jezik prejemnika iz P0; locale neobvezen in nikoli skupna prisilna vrednost za vse. Nadomestni jezik samo po pregledanem pravilu D05, sicer zadržanje z vidnim razlogom. | Dve osebi s skupnim naslovom imata različna jezika; odsoten prevod ne ustvari tihe zamenjave. |
| C04 / N5: identitete in prijava | Slovar person_id, student_id, recipient_id/subject_id, sej, servisov in delegiranja | Person_id je poslovna identiteta osebe; druga poimenovanja pomenijo njeno vlogo v klicu. Uporabniški akter iz preverjenega konteksta; servisni prejemnik v telesu ni prijava v njegovem imenu. | Podtaknjen person_id zaposlenega, servis brez dovoljenja, servis z uporabniškim piškotkom, seja po odjavi, CSRF in preusmeritev zunaj dovoljenega cilja. |
| C05: topologija in meje zaupanja | Procesi, skupna prijava, notranji transport, dokaz delegiranja in dovoljene klicne smeri | En HTTPS izvor; en vzdrževan prijavni sistem; ločena dovoljenja P0/M1/M2. Skupnega izvora ali lokalnega omrežja ne šteje za avtentikacijo. | M2 ne more brati kontaktov; ponarejen kontekst uporabnika v notranji zahtevi se zavrne. |
| C06: avtorizacija in zgodovinski dostop | Odvzem, čas preverjanja, izpad, zgodovina in hramba | Ohraniti smer osnutka: brez pozitivnega predpomnjenja; odvzeta podlaga prevlada nad grants. Ob izpadu zaščiteno dejanje zavrniti/dostavo zadržati. Zgodovina se ohrani, nadaljnji vpogled zahteva aktualno pooblastilo. | Nov član oddelka ne vidi starih objav; odvzem med čakanjem zadrži dostavo. Izrecno določiti mejo tekmovanja med zadnjim preverjanjem in predajo pošte. |
| C07 / N7: kontakt in dokaz zahteve | Kako P0 preveri pripadnost delivery_request_id osebi/obsegu, odsoten kontakt in spremembo kontakta | Le pooblaščeni M1 ob vsaki predaji/ponovitvi ponovno razreši veljaven kontakt za evidentirano dostavo. Zgolj podan request_id ni dokaz lastništva. Odsoten kontakt ni 503; izrecna koda in pot za papirno obravnavo. | Izmišljen/tuj request_id ne razkrije kontakta; kontakt zamenjamo med čakanjem; dva računa z istim naslovom ohranita dve identiteti in odziva. |
| C08 / N7: idempotentnost in poslovna podvojitev | Okno ponovitev, hramba, kanonizacija vsebine, poslovni ključ in poznejša ponovitev | Isti ključ/vsebina vrne isti logični rezultat, drugačna 409. Ločen poslovni ključ vsebuje dogodek/različico, osebo, obseg, vrsto in zaporedno številko legitimnega opomnika. Prepozna ponovitev se ne spremeni samodejno v nov dogodek. | Izgubljen 202; nov ključ po izteku okna ne podvoji istega dogodka; naslednji načrtovani opomnik je dovoljen. Določiti hrambo zaščitenega zapisa deduplikacije. |
| C09 / N7: need_ref | Izdaja v M2, vezava na dostavo, osebo, otroka/namen/različico ter potek | Neprosojen sklic na eno konkretno potrebo; selektivno preverjanje. M1 prejme le REQUIRED/NO_LONGER_REQUIRED ali napako, brez vsebine odločitev. | Odgovor za otroka A oziroma namen A ne ustavi še potrebnega opomnika za B. Tuj ali potekel sklic se ne razloži kot običajen »nepotreben«. |
| C10 / N6: tihi čas in expires_at | Avtoriteta urnika, dostop M2 do dovoljene dostavne ure, poletni čas, meje in najdaljše zadržanje | M1 lastnik urnika; M2 odda ob dospelosti. Predlagan omejen bralni vpogled v urnik oziroma earliest_delivery_at kot informacija; M1 vedno ponovno preveri urnik. M1 privzeti 20–7 in vikendi sta osnutek, ne potrjen urnik šole. | Dospelo v petek z iztekom pred ponedeljkom; sprememba urnika; prehod poletnega časa; ob now >= expires_at ni nove predaje. |
| C11: trajnost in izpadi | Kaj 202 jamči, atomarnost M2, ponovitve in delna dostava | M2 odločitev in trajno namero za dostavo zapiše skupaj; M1 vrne 202 šele po trajnem zapisu. Po izpadu nadaljuje le veljavne in neobdelane dostave. | Izpad pred/po commitu in izgubljen odgovor; brez izgubljene odločitve ali sprejete zahteve, ki po ponovnem zagonu manjka. |
| C12: selektivni preklic | Identifikator posamezne dostave/obsega, shema izbire, atomarnost, odgovor in ponovitev | Ločen delivery_item_id za osebo in konkretno potrebo/obseg. Preklic samo izbranih postavk; ne preklic vseh oseb ali vseh otrok iste osebe. Ohraniti rezultate cancelled_now/already_cancelled/too_late/already_terminal. | Dve osebi v zahtevi in dve potrebi iste osebe; prekličemo eno postavko. Ponovitev, prepozen preklic in tuja postavka ne ustvarijo lažnega uspeha. |
| C13: negotova poštna predaja | Stanje negotovosti, pravilo ponovitve, vidnost in dokazovanje | Predlog held z izrecnim razlogom negotovosti in omejeno ročno/politično odločitvijo o ponovitvi; brez obljube enkratnega fizičnega prejema. Ob znanem SMTP sprejemu handed_off, ne »prejeto«. | SMTP sprejme, odgovor ali lokalni zapis se izgubi; ponovitev lahko fizično podvoji sporočilo. Dogovorjeno ravnanje se preskusi ob preklicu in izteku. |
| C14: spremembe evidence in odprti postopki | Periodična uskladitev ali dogodki, interval, ponovitve, vrstni red in izpad | Za prvo različico predlagana periodična ponovna presoja odprtih postopkov skupaj s preverjanjem ob dejanju. Interval določi nosilec pred pilotom, brez izmišljene kapacitete. | Odvzem brez nove uporabniške zahteve, izpad in zamujena obdelava; polnoletstvo po izrecnih pravilih D16, brez prepisa zgodovine. |
| C15 / N3: OpenAPI, šifranti in omejitve | Sheme vseh poti, razlogi/HTTP napake, največ prejemnikov, strani, parametrov, velikosti in lastništvo testov | Najprej pregledan slovar in sheme, nato isti pogodbeni primeri za nadomestka in pravi P0; omejitve so izrecna polja za potrditev. 503 ostane napaka, ne zavrnitev upravičenja ali nepotrebnost. | Mejne vrednosti, neznano polje/predloga, napačen tip, tuji vir, paginacija brez podvajanja/izpuščanja po potrjeni politiki. |
| C16 / N3: različice in sprejem | Kdo potrdi, katera verzija, prehod ob spremembi in pogoji T | Tehnični nosilec in mentorji pisno potrdijo točen commit/OpenAPI; sprememba z vplivom na ekipe zahteva uskladitev, nezdružljiva sprememba verzijo/prehod. | Nadomestek in pravi modul z različnima shemama ne prestaneta prevzema; sprejet mock ne nadomesti P0. |

Predlog posamezne postavke dostave omogoča tudi več obsegov istega starša: več postavk z isto person_id in različnim obsegom ni združitev identitet. Morebitno združevanje splošnih e-pošt v eno fizično pošiljanje je ločena odločitev z vplivom na preverjanje potrebe in preklic; za prvo pogodbo predlagamo, da se temu izognemo. To ne odstrani zahteve, da M1 v uporabniškem vmesniku podpira jasno prikazano potrditev za več otrok.

Smeri trenutnega osnutka (ločena uporabniška/servisna identiteta, preverjanje ob dejanju, trajnost pred 202, idempotentnost in selektivni preklic pred I) so dokumentirana izhodišča. Kot celota še niso formalno potrjena pogodba D12.

### Pripravljena matrika dokazov za T

To so opisani scenariji za prihodnje teste in človeški pregled; niso izvedeni testi aplikacije.

| Skupina | Scenariji | Dokaz, ki ga mora vsebovati T |
| --- | --- | --- |
| Identitete/dovoljenja | Druga družina, drug oddelek, skupen kontakt, več otrok, odvzem povezave in grants, servisni klic brez uporabniške seje | Dovoljeni in zavrnjeni klici ter neodvisen pregled kode za avtorizacijo/obsege |
| Kontakti/uvoz | Brez e-pošte, zamenjava kontakta med poskusi, tuj request_id, napačen in ponovljen CSV | Brez razkritja kontakta, brez delnega prepisa ali dvojnikov; pošta v testnem predalu |
| Dostava | Trajni zapis pred 202, izgubljen odgovor, izpad M1/P0/M2, delna dostava | Ponovljiv ponovni zagon in pogodbeni rezultati za vse prizadete postavke |
| Potreba/preklic | Odziv med čakanjem, otrok/namen A in B, dve osebi, ponovljen in prepozen preklic | Ustavljena samo izbrana potreba; M2 ne razkrije vsebine odločitve |
| Čas/prevodi/pošta | Vikend, iztek, sprememba urnika, poletni čas, manjkajoč prevod, negotov SMTP izid | Vidni razlogi zadržanja/izteka in ravnanje po potrjeni politiki |
| Predaja | Sveža namestitev P0 in nadomestkov po istih shemah, tipkovnica in osnovni bralnik zaslona | Neodvisen človeški zapis celotnega sprejema iz načrta T |

## Obrazci dejanskih odločitev

Obrazci ostanejo neizpolnjeni do potrditve. V javni zapis se prenesejo le podatki, primerni za objavo; zasebna dokazila ostanejo na potrjenem zasebnem mestu. Vsaka odločitev navede točno različico/commit, datum, razlog in posledice.

| Evidenca | Obvezna polja |
| --- | --- |
| D09 — zgodnji del | Prvi in drugi skrbnik ter individualna računa; sprejem vlog; dejanske pravice; datum in povzetek praktičnega preizkusa; potrditev zavodov; preostala produkcijska merila |
| D14 | Nosilec in namestnik; potrjene ure/dnevi pokritosti, koledar, odzivni cilji, odsotnosti in eskalacija; preizkus prijave/obvestila/odgovora/prevzema; potrditev nosilca projekta in skrbnika; usklajen SECURITY.md |
| D03 | Nosilec; mandat in kapaciteta; sprejem modela brez ločenega tehničnega namestnika in ravnanje ob odsotnosti; lastnik vsakega gradnika in predaja; potrjena tehnologija/skupne varnostne funkcije; način osebne priprave P0/T; potrditev zavodov ter tehničnega dogovora z mentorji |
| D12 | Sprejet rezultat C01–C16 ali razlog zavrnitve predloga; slovar ID/šifrantov; commit OpenAPI in testnih primerov; lastniki; potrditvi tehničnega nosilca in mentorjev; povezane šolske odločitve in omejitve učnih pravil |

Potrditev zapišemo v ustrezni issue; s pull requestom uskladimo register in povezane dokumente. Dodelitev računa se izvede šele po potrditvi osebe in računa. Kjer dokazila manjkajo, ostane merilo odprto. D09 zgodnji del in produkcijski del se vodita ločeno.

## Naslednji koraki in manjkajoči odgovori

1. Nosilec projekta in sodelujoči zavodi pridobijo izrecna imenovanja: drugi skrbnik, nosilec prijav in namestnik, skupni tehnični nosilec. Za D03 se potrdi model brez ločenega tehničnega namestnika in ravnanje ob odsotnosti. Vloge se lahko združijo po zgornjih omejitvah. Kandidatov ne sklepamo iz repozitorija.
2. Imenovana nosilec prijav in namestnik sprejmeta ali prilagodita odzivne cilje ter določita pokritost in zasebno eskalacijo. Skrbnika nato izvedeta opisani preizkus. Za spremembo pravic je potreben dejansko pooblaščen skrbnik; ta pregled pravic ni dodelil.
3. Zavodi potrdijo mandat, čas in lastnike skupnih gradnikov za D03; nosilec in mentorji sprejmejo ali nadomestijo tehnološki predlog. Pred prvo kodo se v issueih preveri izpolnitev vseh zgodnjih pogojev.
4. V D08 nosilec projekta in avtorji uredijo licenco, pravice in odvisnosti pred sprejemom kode. Mentorji pripravijo odgovore D02/D13, ne da bi jim naložili novo oblikovanje cilja.
5. Tehnični nosilec in mentorji obravnavajo C01–C16. Pripravi se pregledana OpenAPI pogodba in primeri; odvisna implementacija se začne po izrecni potrditvi D12. Sedanjih primerov ne razglasimo za dokončno pogodbo.
6. Pobudnik in nosilec ocenita T po izdelkih, tveganjih in razpoložljivosti pregledovalca. Po sedanjem načrtu neodvisen človek preveri pravi P0, kodo in celoten paket T. Mitjev predlog osebnega pregleda ob pomoči AI zahteva predhodno potrditev spremembe merila; A/I se sprosti šele po formalnem prevzemu T po potrjenih merilih in drugih predhodnih pogojih.

Za nadaljevanje so zato resnično manjkajoči odgovori: potrjene osebe/računi in njihov sprejem vlog, pokritost/odzivni dogovor, mandat in razpoložljivi čas, lastništvo gradnikov, tehnološka potrditev ter pozneje konkretne odločitve D12. Datum začetka, ure zavodov, dostopi in produkcijski pilot niso ugotovljeni ali obljubljeni.
