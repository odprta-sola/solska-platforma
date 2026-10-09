# Razvojno naročilo P0, M1 in M2

Datum: 9. oktober 2026

Različica: predlog izvedbe 2

Avtorstvo usmeritve: pobudnik projekta Mitja Pirih  
Status: projektna usmeritev pobudnika in predlog za izvedbeni dogovor; ne potrditev virov zavodov ali produkcijske uvedbe

## Cilj prve različice

Izdelamo povezano spletno rešitev za eno testno šolo. Zaposleni objavi obvestilo ali pripravi obrazec; upravičeni starš oziroma dijak se prijavi, vidi samo svoje vsebine ter potrdi seznanitev ali odda odločitev. Šola vidi odzive in opravi potrebno nadaljnjo obravnavo.

P0 zagotavlja skupne račune, evidenco in upravičenja. M1 zagotavlja obvestila, seznanitev in dostavo. M2 zagotavlja obrazce, odločitve in preklice; za obveščanje uporablja M1. M1 je uporaben s P0 tudi brez M2. Isti uporabnik uporablja isti račun.

Razvijamo izključno na izmišljenih podatkih. OŠ Vojke Šmuc Izola je predlagana šola uporabnica; vključitev GEPŠ v preizkus se preveri. Rešitev deluje z lokalno prijavo in CSV uvozom brez neposredne povezave z eAsistentom ali ArnesAAI. Možnost poznejše povezave ArnesAAI ostane zahtevana razvojna smer, njena uporaba za šolo prostovoljna.

## Kaj je določeno in kaj ostaja za dogovor

Ta dokument določa naš izhodiščni cilj, funkcionalni obseg, vloge, zaporedje in merila uspeha. Mentorjem ga predložimo kot konkretno naročilo za oceno izvedljivosti. Ne prosimo jih, naj sami oblikujejo namen projekta.

| Področje | Izhodišče |
| --- | --- |
| Namen in prioritete | Določi pobudnik; spremembe uskladi s šolo uporabnico |
| Obvezne funkcije in demonstracije | Določene spodaj; zmanjšanje obsega je izrecen dogovor, ne tiha opustitev |
| Vmesniki in pravila dostopa | Skupen tehnični predlog za vse ekipe; pred odvisno implementacijo pregled in potrditev D12 |
| Dijaki, ure, roki in maturitetna primernost | Mentor in razvojni zavod določita na podlagi tega naročila |
| Tehnologija in prijavna komponenta | Pobudnik predlaga osnovo; skupni tehnični nosilec in mentorji pregledajo in potrdijo skupno izbiro pred izvedbo; ni prosta ločena izbira vsake ekipe |
| Priprava P0 in paketa T | Pobudnik osebno s pomočjo AI pripravi referenčno osnovo; ne nastopa samodejno njegovo podjetje. Neodvisni človeški pregledovalec jo preveri pred predajo. |
| Oblikovanje in notranja organizacija kode | Prostor za dijake ob izpolnjenih skupnih pravilih |
| Dodatne funkcije | Šele po obveznih demonstracijah, brez spremembe pogodbe na lastno pobudo |
| Produkcija in pravna ustreznost postopka | Ločen pregled in odločitev šole; učni rezultat je ne nadomesti |

Odprti register D01–D16 se s tem ne zaključi. Zlasti ne imenujemo oseb, ne obljubljamo ur zavodov in ne potrjujemo še nedokončane pogodbe API.

## Uporabniške vloge in odgovornosti modulov

| Vloga | P0 | M1 | M2 |
| --- | --- | --- | --- |
| Starš/skrbnik | Prijava, lastni račun in dovoljene povezave | Lastna obvestila, seznanitev in potrdila | Dovoljeni obrazci, lastne odločitve, preklic |
| Upravičeni dijak | Lastna identiteta in dovoljenja po pravilih postopka | Lastna obvestila | Lastne odločitve po pregledanih pravilih |
| Učitelj/razrednik | Dodeljeni oddelki | Priprava in objava v dovoljenem obsegu, odzivi | Priprava obrazca ali izvajanje postopka, če ima to vlogo |
| Vsebinski potrjevalec | Račun in pooblastilo | Brez samodejnih dodatnih pravic | Pregled konkretne različice pred objavo |
| Tajništvo/vodstvo | Pooblaščen uvoz in potrjevanje evidence | Širše objave, papirna pot | Papirni vnosi in ročna obravnava po pooblastilu |
| Tehnični skrbnik | Računi, tehnične nastavitve in nadzor | Dostava in tehnične napake | Tehnično delovanje |
| Pooblaščeni pregledovalec | Dovoljenje za določen namen | Dnevnik in izvoz v obsegu pooblastila | Dokazni zapisi in izvoz v obsegu pooblastila |

Tehnična vloga ne daje rutinskega vpogleda v vsebine. Povezava starš–otrok sama ni dovoljenje za vsako dejanje. Vloge se lahko združujejo, vendar se pravice preverijo za konkretni vir in postopek.

## Referenčna osnova P0

**Priprava pobudnika:** delujoči P0 je predajna osnova za dijake, ne obvezna začetna maturitetna naloga. Podroben razrez prvega prevzema in dopolnitev za B določa [načrt priprave P0](priprava-referencnega-P0.md); spodnji seznam opisuje ciljni obseg B, ne drugega neodvisnega prevzemnega merila.

| Vprašanje za dijaka | Izhodišče |
| --- | --- |
| Kaj dobi pripravljeno? | Prevzeti P0, v D12 potrjeno pogodbo, izmišljene podatke, nadomestka in pogodbene teste. |
| Kaj izdela sam? | Dodeljeni del M1 ali M2, povezavo s P0, lastne teste, navodila in demonstracijo. |
| Kaj je obvezno? | Dogovorjeni del obveznega jedra B in sodelovanje pri povezani demonstraciji. |
| Kaj je izbirno? | Dodatna funkcija ali omejena razširitev P0 po dogovoru z mentorjem. |
| Kako dokaže uspeh? | Pri A objava → prijava → dovoljeni prikaz → potrditev; pri I oddaja odločitve in zanesljiva dostava tudi po izpadu. |

1. Evidenca oseb, otrok, oddelkov, šolskih let, povezav in dovoljenj s stalnimi ID.
2. Lokalna prijava z vzdrževano rešitvijo; gesel in kriptografije dijaki ne razvijajo na novo.
3. Uvoz CSV s predogledom dodajanj/sprememb, validacijo in celovito potrditvijo; posamezni sledljivi popravki.
4. Upravljanje aktivacije, sprememb kontakta in odvzema dostopa na testnem okolju.
5. Vmesniki za identiteto, oddelke, prejemnike in preverjanje upravičenj.
6. Omejen dostop dostavne storitve do kontakta tik pred pošiljanjem.
7. Testni nabor s staršema s skupnim kontaktom, več otroki, osebo brez e-pošte, tajništvom in odvzemom povezave.

**Zasloni:** prijava, seznam oseb, podrobnosti osebe in povezav, uvoz s predogledom, spremembe upravičenj.

**Vhodi:** izmišljeni CSV in pooblaščeni popravki. **Izhodi:** stabilne identitete in preverjena dovoljenja; brez kopiranja gesel drugim modulom.

P0 ne pošilja aktivacijskih sporočil prek poslovnega API M1. Uporabi poštni mehanizem izbrane prijavne rešitve. Razvojna e-pošta gre v prestrezni testni predal.

Za prvo demonstracijo so računi pripravljeni vnaprej. Prvi prevzem P0 vključuje spremembo kontakta in odvzem povezave ter dovoljenja. Individualna aktivacija in obnova prek skupnega predala sta dopolnitev pred B; sam dostop do skupnega predala ne zagotavlja ločitve oseb. Podrobnosti evidence in uvoza: [P0 uporabniki](../moduli/P0-uporabniki.md).

## Obvezni izdelek M1

**Naloga ekipe:** omogočiti celoten potek šolskega organizacijskega obvestila.

1. Osnutek, izbira skupine, predogled prejemnikov in objava.
2. Informativno obvestilo ter obvestilo z zahtevano seznanitvijo.
3. Zaščiten prikaz besedila in preverjenih prilog PDF/slik.
4. Izrecna potrditev konkretne različice in jasno prikazanega obsega otrok; ločeni odzivi oseb.
5. Pregled nepotrjenih odzivov, napak dostave in papirne poti.
6. Različice in ponovna seznanitev po bistveni spremembi; umik.
7. E-poštna vrsta, tihi čas, omejeni ponovni poskusi in opomniki.
8. Evidentiranje izročitve in papirne potrditve kot ločenih dogodkov.
9. Minimalni sprejem zahtev M2, stanje dostave in preklic.
10. Dokumentiran izvoz obvestil, različic, prilog in potrditev.

**Zasloni:** seznam obvestil, prikaz vsebine/potrdilo, priprava in predogled, pregled odzivov, papirna pot, dostavna opravila za pooblaščene.

**Vhodi:** vsebina zaposlenega, prejemniki P0 in zahteve M2. **Izhodi:** objavljena vsebina, potrditve in stanja dostave.

Odprtje ni potrditev, potrditev ni soglasje. Predaja strežniku ni dokaz prejema. Omejen prvi mejnik in celoten učni izdelek sta ločena spodaj. Podrobnosti: [M1](../moduli/M1-eSporocanje.md).

## Obvezni izdelek M2

**Naloga ekipe:** izdelati potek pregledanega obrazca od osnutka do odločitve in dovoljene spremembe.

1. Predloga z omejenim naborom polj, različica, predogled in vsebinski pregled pred objavo.
2. Dva izmišljena učna postopka: organizacijsko soglasje in privolitev z več ločenimi nameni.
3. Upravičenci iz P0 in izrecne izbire brez vnaprej izbranih odgovorov.
4. Pravilo odziva enega ali vseh zahtevanih upravičencev, ločeni posamezni odzivi.
5. Odločitev, dokazni dogodek, skupno stanje in dostava kot ločeni podatki.
6. Potrdilo in zgodovina, spremembe ter preklic po pravilih testnega postopka.
7. Nasprotujoči odzivi sprožijo ročno obravnavo; sistem ne izmisli izjave uporabnika.
8. Obvestila in opomniki prek M1; preklic nepotrebnih opomnikov.
9. Papirni vnos z izvorom, različico in zaposlenim; dokumentiran izvoz.

**Zasloni:** seznam obrazcev, obrazec in pregled pred oddajo, potrdilo/zgodovina/preklic, priprava, vsebinska odobritev, stanje postopka in ročna obravnava.

**Vhodi:** testne predloge, pravila postopka, upravičenja P0 in izbire uporabnika. **Izhodi:** odločitve, zgodovina, potrdila in zahteve za dostavo M1.

Brez odziva ni zavrnitev ali privolitev. Preklic veljavne privolitve ostane dostopen tudi po zaključku zbiranja ali umiku obrazca. M2 ne zahteva predhodnega klika »Seznanjen/-a sem« v M1. Podrobnosti: [M2](../moduli/M2-eSoglasja.md).

## Skupni vmesniki

Ekipe dobijo isti [osnutek pogodbe P0–M1–M2](../arhitektura/vmesnik-P0-M1-M2.md). API je del naročila, ne izbirna dodatna funkcija. Njegov pregled in dopolnitev do prve potrjene sheme je skupna začetna tehnična naloga.

| Povezava | Obvezni dogovor |
| --- | --- |
| P0 → uporabniški del M1/M2 | Preverjena identiteta, dovoljena dejanja, lastni otroci/dodeljeni oddelki in dovoljene prikazne oznake |
| P0 → poslovni del modulov | Razrešitev pooblaščenega občinstva in preverjanje trenutnih upravičenj |
| P0 → dostavna storitev M1 | Kontakt za konkretnega dovoljenega prejemnika in zahtevo |
| M2 → M1 | Zahteva za dostavo, povratno stanje, ponovljiv preklic |
| M1 → M2 | Minimalna informacija, ali je opomnik še potreben; brez vsebine odločitve |

Moduli ne berejo tabel drug drugega. Imena ID, čas, napake in različice sledijo eni pogodbi. M2 določi čas opomnika in odda zahtevo ob dospelosti; M1 upošteva tihi čas in iztek. Spremembo pogodbe uskladijo vse prizadete ekipe.

Začetni tehnični paket mora pripraviti predlog rešitve tudi za preostale ugotovitve pregleda:
- vezava osebe, dovoljenja, vira in dostave v scope_ref, tudi pri več otrocih;
- prednost odvzema povezave pred dovoljenji, ki iz nje izhajajo;
- prikazna imena in jezik po prejemniku;
- ločena uporabniška in servisna avtorizacija;
- obvezna polja po vrstah dostave ter poslovna identiteta za ponovitve;
- negotov izid poštne predaje in meje zagotovila ene dostave;
- individualna aktivacija in obnova pri skupnem e-poštnem predalu.

Te vrzeli niso prepuščene domišljiji posamezne ekipe. Pobudnik s pomočjo AI pripravi eno izhodiščno rešitev, skupni tehnični nosilec in mentorji jo preverijo v D12. P0 sam ne določi povezav M2 → M1 in M1 → M2; paket T mora vključiti njuni shemi, nadomestka in pogodbene teste. Obstoječi osnutek še ni dokončni OpenAPI ali delujoč testni strežnik.

## Vloge pri izvedbi

| Vloga | Konkretni rezultat |
| --- | --- |
| Pobudnik in koordinator | Cilj, prioritete in izhodiščni obseg; osebna priprava referenčnega P0/T s pomočjo AI; usklajene vsebinske spremembe s šolo uporabnico |
| Predstavnik šole uporabnice | Preveri realnost postopkov, pravila upravičenj in uporabniški prevzem |
| Skupni tehnični nosilec | Z mentorji pregleda in potrdi predlagano skupno tehnologijo in pogodbo; vodi integracijske preglede |
| Nosilec skupnih gradnikov | Koordinira tehnično predajo P0/T in skladnost skupnih gradnikov; prihodnje vzdrževanje se dodeli posebej |
| Neodvisni pregledovalec T | Človek, ki ni izdelal pregledovane kode; po navodilih preveri namestitev, kodo in demonstracije. Imenovanje je pogoj pred prevzemom T. |
| Mentorji | Ocenijo izvedljivost podanega naročila, določijo individualne izdelke, dijake in roke ter preverjajo napredek |
| Dijaki | Razvijejo predvsem M1 in M2 ter njuno povezavo s P0, teste, dokumentacijo in demonstracijo; omejene razširitve P0 so možne po dogovoru z mentorjem |
| Skrbnik repozitorija in namestnik | Dovoljenja, pregled sprememb in obravnava varnostnih prijav |
| Vzdrževalec in namestnik | Poznejši prevzem podpore ter produkcijskega delovanja |

Osebe se imenujejo posebej. Predlog 2–3 dijakov na modul je izhodišče za razporeditev, ne zahteva ali obljuba razpoložljivosti. Primerjalni prototipi so dovoljeni do zgodnjega izbora osnove; pogodba in preizkusi veljajo za vse. Vsak dijak mora imeti razpoznaven izdelek in prispevek.

Za mentorjev razrez so mogoči ločeni individualni izdelki M1 objave in seznanitev, M1 dostava in papirna evidenca, M2 priprava in pregled obrazcev ter M2 odločitve, zgodovina in preklic. Dostopnost, testi, navodila in povezovanje so del vsakega ustreznega izdelka. Mentorji preverijo zahtevnost, samostojnost in formalno ustreznost; razrez ne predpostavlja števila razpoložljivih dijakov.

## Mejniki in demonstracije

| Mejnik | Obvezni rezultat | Dokaz zaključka |
| --- | --- | --- |
| T – skupna tehnična priprava | Delujoči referenčni P0, izbrana razvojna osnova, v D12 potrjena različica pogodbe OpenAPI, izmišljeni nabor, nadomestki, pogodbeni testi in navodila za namestitev | Celoten seznam dokazov je v [človeškem prevzemu P0/T](priprava-referencnega-P0.md#človeški-prevzem). |
| A – prvi uporabniški potek | Besedilni M1 na prevzetem P0, vnaprej pripravljeni računi | Učitelj objavi; pravi starš vidi in potrdi; druga družina nima dostopa |
| I – povezava | Minimalni M2 z enim pregledanim testnim obrazcem, eno izrecno odločitvijo in trajno zahtevo za dostavo; M1 prevzame zahtevo po pogodbi | Odločitev ostane shranjena med izpadom M1; dostava se nadaljuje; dvojna zahteva se ne podvoji logično |
| B – celoten učni izdelek | Obvezni obseg P0/M1/M2 iz tega naročila | Skupna demonstracija spodnjih primerov, namestitev, testi in dokumentacija |
| C – morebitni produkcijski pilot | Poseben potrjen postopek in strokovni prevzem | Vsa produkcijska merila iz specifikacij ter imenovani nosilci |

A in I se lahko razvijata vzporedno šele po celotnem človeškem prevzemu T. Pravi P0 je na kritični poti; nadomestka M1/M2 ga ne nadomestita. Če se T zamakne, se zamakne začetek odvisnega razvoja, pri čemer mentorji lahko pripravljajo neodvisne učne naloge brez trditve, da je A/I že stekel. Roke in obremenitev predlaga razvojni zavod; naročilo ne določa nepreverjenih ur.

| Preizkus | Mejnik | Pričakovano |
| --- | --- | --- |
| Informativno obvestilo in zahtevana seznanitev | A | Prvo brez potrditve; drugo z izrecnim dejanjem |
| Odprtje in ponovljen klik | A | Odprtje ni potrditev; ponovitev ima en logični učinek |
| Dva starša in druga družina | A | Ločeni odzivi; tuji neposredni naslov je zavrnjen |
| Osnovna dostopnost | A | Potek s tipkovnico, vidni fokus, označena polja in razumljive napake; osnovni pregled z bralnikom zaslona |
| M2 odda zahtevo dvakrat in jo prekliče | I | En logični prevzem; sledljiv preklic ali pojasnjen prepozen preklic |
| Izpad M1 med odločitvijo | I | M2 ohrani odločitev in trajno zahtevo; ob obnovi povezave se dostava nadaljuje |
| Izgubljen odgovor 202 | I | M1 zapiše zahtevo pred odgovorom; ponovitev z istim ključem vrne isti logični rezultat |
| Preklic ene od dveh dostav | I | Ustavi se samo izbrani prejemnik; druga dostava ostane veljavna |
| Napačen in ponovljen CSV | T za osnovni uvoz; B za celotni obseg | Brez delnega prepisa in podvojenih oseb |
| Odvzem povezave ob obstoječem grants | T | Dovoljenje, ki temelji na odvzeti povezavi, ne omogoči novega dejanja |
| Skupni kontakt dveh računov | B | Aktivacija/obnova sledi pregledanemu individualnemu postopku |
| Več otrok in spremenjena različica | B | Jasno izbran obseg; stara potrditev ne potrdi novega navodila |
| Priloga in papirna pot | B | Dostop zaščiten; izročitev ločena od potrditve |
| Več namenov in več odločevalcev | B | Ločene izbire; pravilno skupno stanje; spor gre v obravnavo |
| Preklic pri zaključenem/umaknjenem obrazcu | B | Veljavno privolitev je mogoče preklicati; dogodek in potrdilo sta sledljiva |
| Opomnik med izpadom ali tihim časom | B | Po izteku ni pošiljanja, razlog je viden |
| Negotov izid poštne predaje | B | Izvedba sledi dogovorjeni politiki; ne trdi dokazljive enkratne fizične dostave brez podlage |
| Jeziki | B | Jezik prejemnika in izrecna nadomestna možnost; večjezični model od začetka |
| Namestitev in izvoz | B | Druga ekipa iz navodil ponovi demonstracijo; izvoz vsebuje dokumentiran obseg |
| Dostopnost celotnega jedra | B | Osnovni postopki M1/M2 so izvedljivi s tipkovnico in preverjeni z bralnikom zaslona |
| Skupni integracijski preizkus | B | Pravi P0/M1/M2 prestanejo pogodbeni in uporabniški potek brez nadomestkov |
| Organizacijsko soglasje | B | Ločeni upravičenci, pravila skupnega stanja in potrdilo |
| Privolitev po namenih | B | Vsak namen je ločena izbira; preklic in zgodovina sta sledljiva |
| Vsebinski pregled M2 | B | Avtor sam ne odobri svoje različice; objavljena je le pregledana različica |

## Kaj pustimo za pozneje

ArnesAAI, neposredna integracija z eAsistentom, potisna obvestila, avtomatiziran prehod šolskega leta, napredni obrazci, drugi moduli in centralna namestitev več šol niso obvezni za učni izdelek B. Potrebni jeziki dejanskega pilota in dostopnost niso izbirna produkcijska nadgradnja.

Za B so dostopnost, ponovljiva namestitev, integracijski preizkusi, izvoz, papirna pot in dva učna postopka obvezno jedro. Izbirne so dodatne funkcije in po dogovoru omejene dijaške razširitve P0. Če ocena izvedljivosti pokaže prevelik obseg B, mentorji predlagajo konkreten rez v številu podprtih možnosti ali postopkov; sprememba obveznega jedra zahteva izrecen dogovor pobudnika s šolo. Dostopov, sledljivosti in osnovne dostopnosti zaradi rokov ne opustimo. Oblikovanje zaslonov in organizacija kode dopuščata ustvarjalnost, pomen odločitev, dostopi, podatkovni tokovi in API pa so skupni dogovor.

## Odgovor razvojnega zavoda

Odgovor pričakujemo na konkretni predlog: kateri del lahko zavod izvede, koliko dijakov in časa ima na voljo, kdo prevzame mentorstvo ter katere natančne spremembe predlaga in zakaj. Izvedbeni dogovor zabeleži sprejeti obseg, izjeme in roke.

Mentorjem ni treba na novo določati cilja. Njihova presoja izvedljivosti in formalna potrditev maturitetnih nalog ostajata potrebni. Pogoji iz [registra](odlocitve.md) veljajo pred odvisnim razvojem; posebej D09/D14 pred prvo kodo oziroma vključitvijo zunanjih ekip.

[Praktični primeri in razlaga modulov](../mentorji/razvojni-paket-P0-M1-M2.md) dopolnjujejo to naročilo.
