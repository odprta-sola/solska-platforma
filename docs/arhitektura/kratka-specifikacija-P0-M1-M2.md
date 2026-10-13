# Kratka tehnična specifikacija P0, M1 in M2

Datum: 13. oktober 2026

Status: delovni osnutek za pogovor in dopolnitev D12; ni dokončen OpenAPI ali dovoljenje za odvisno implementacijo

Ta dokument povzame model, vmesnike, sprejemna pravila in 20 skupin prihodnjih preizkusov. [Predstavitev](../mentorji/predstavitev-projekta.md) pojasni uporabniške postopke, [naročilo](../projekt/razvojno-narocilo-P0-M1-M2.md) določa T/A/I/B/C. Podrobni [osnutek pogodbe](vmesnik-P0-M1-M2.md) ostaja stalno mesto D12; preostale sheme, šifranti, omejitve in podpisi se potrdijo tam. Noben test aplikacije še ni izveden.

## Okolje in meje

- Ena izmišljena testna šola, lokalni individualni računi in testni poštni predal.
- Osebno izbrana osnova Mitje: Django 5.2 LTS/Python, PostgreSQL in Docker Compose. Formalna potrditev skupne osnove in konkretne izdaje še sledijo.
- Vsaka šola ima svojo namestitev in svoje podatke. Centralna večšolska storitev ni predvidena. Dejansko upravljanje, gostovanje, kopije in vzdrževanje potrdita šola in nosilec v D04/D09.
- CSV je osnovna in trajno ohranjena možnost uvoza. Oblika izvoza ali API eAsistenta ni potrjena. Prihodnja povezava bo dodatna možnost, ne pogoj ali zamenjava CSV.
- ArnesAAI, SI-PASS, potisna obvestila in avtomatiziran prehod leta so poznejše smeri, brez zagotovljene integracije ali roka.
- Skupna osnova hrani identitete in pravice; moduli hranijo svoje poslovne podatke. Klici uporabljajo pregledane vmesnike, ne neposrednega branja tujih poslovnih tabel. Procesno topologijo potrdi D12; ločeni moduli ne zahtevajo treh strežnikov.

## Predlagani podatkovni model

Imena so opisne entitete, ne dokončane tabele ali migracije. Končni ključi, omejitve, hramba in dokazni posnetki zahtevajo pregled D12/D07.

| Lastnik | Entitete | Pomen |
| --- | --- | --- |
| P0 | Person, Account, SourceMapping | Stabilna oseba, individualni prijavni račun in preslikava uvoznega ključa; e-naslov ni identiteta. |
| P0 | Student, Class, Membership | Učenec kot evidenčna oseba, oddelek in časovno članstvo. Evidenčni zapis sam ne ustvari računa. |
| P0 | Relationship, StaffAssignment | Preverjena povezava starš–otrok in dodelitev zaposlenega. |
| P0 | Grant, Approval, ChangeAudit | Šolsko potrjen obseg in dejanja, potrjevalec, veljavnost, izvor in sled sprememb. |
| P0 | ImportBatch, ImportPreview | Validirana serija, predogled, konflikti in celovita aktivacija po pooblaščeni potrditvi. |
| M1 | Notice, NoticeVersion, AudienceItem | Obvestilo, objavljena različica in konkretna naslovljenost; prihodnji člani ne dobijo samodejno starih objav. |
| M1 | Acknowledgement, PaperEvent | Izrecna seznanitev ter ločeno papirna izročitev in potrditev. |
| M1 | DeliveryRequest, DeliveryItem, DeliveryAttempt | Logična zahteva, posamezna dostava in poskusi z izidom oziroma negotovostjo. |
| M2 | Form, FormVersion, Purpose | Pregledan obrazec, različica in ločeni nameni. |
| M2 | Decision, DecisionEvent, Task, ReminderNeed | Izbire po osebi/otroku/namenu, zgodovina, nadaljnja naloga in potreba po konkretnem opomniku. |

Račun učenca/dijaka in ciljna skupina M1 sta predlog: šola določi starost/razred, izdajo računa, kontakt in dovoljene vsebine. Račun učenca ne odpre obvestil ali odločitev samo za starše. Njegova seznanitev ne nadomesti odziva starša. Pri polnoletstvu ne pretvorimo starih izjav in ne dodelimo vseh pravic samo iz datuma rojstva; uporabimo potrjena pravila D16.

## Seznam poti vmesnikov za D12

Poti izhajajo iz sedanjega osnutka. Končne zahteve/odgovori, dovoljeni konteksti in administrativne poti še potrebujejo OpenAPI. Uporabniške poti za objave in odločitve določijo ekipe v skupnem dogovoru; spodaj so skupni klici.

| Pot | Namen in omejitev |
| --- | --- |
| GET /p0/api/v1/me | Identiteta prijavljene osebe iz preverjene seje; poljuben person_id ni prijava. |
| GET /p0/api/v1/me/relationships | Lastne dovoljene povezave. Bralna pot/shema za lastni učenčev obseg se posebej določi v D12; ni roditeljska povezava. |
| GET /p0/api/v1/me/classes | Dodeljeni oddelki pooblaščenega zaposlenega. |
| POST /p0/api/v1/audiences/resolve | Predogled dovoljenih prejemnikov in obsegov. Predlog nove izbire starši/učenci/oboje potrebuje shemo, šifrant in preverjene pravice. |
| POST /p0/api/v1/authorizations/check | Aktualna pravica osebe za konkretni obseg/dejanje; ni nadomestilo za poslovno presojo lastnika vira. |
| POST /p0/api/v1/delivery-contacts/resolve | Samo pooblaščena storitev M1 za lastno evidentirano dostavo in poskus. M2 ne pridobi kontaktov za dostavo. |
| POST /m1/api/v1/delivery-requests | Trajni prevzem zahteve; 202 šele po zapisu, potrebnem za obnovo. |
| GET /m1/api/v1/delivery-requests/{id} | Samo lastna zahteva klicočega modula, stanja posameznih postavk. |
| POST /m1/api/v1/delivery-requests/{id}/cancel | Izbor konkretnih postavk; rezultat preklica je ločen od dostavnega stanja. |
| POST /m2/api/v1/reminders/check | Samo potreben/nepotreben in koda razloga za točno potrebo; brez izbire Da/Ne ali vsebine odločitve. |

Prijavne in aktivacijske poti uporablja vzdrževana komponenta Django, ne nov protokol. Aktivacija računa in poslovna pošta M1 sta ločeni poti. V T se pripravijo testni računi vnaprej; individualna aktivacija in obnova pri skupnem predalu sodita v dopolnitev pred B.

## Pravila v preprostem jeziku

1. Osebo, račun, odnos, glavni kontakt in dovoljeni obseg obravnavamo ločeno. Šola izrecno potrdi pravice; lahko potrdi točen preverjen nabor s profilom in izjemami, ne vsakega uporabniškega klika.
2. Starejši uvoz ne obnovi novejše ročne omejitve. Konflikt se pokaže pooblaščeni osebi; napaka serije ne aktivira delnih sprememb.
3. Za vsak zaščiten vpogled, oddajo in novo dostavno obdelavo preverimo aktualno podlago. Nedosegljivost pomeni začasno napako ali zadržanje; uporabniškega dejanja ne izvedemo tiho pozneje.
4. M1 loči odprtje od izrecne seznanitve. Pri izbrani skupini otrok se nova potrditev izvede za vse dovoljene obsege ali za nobenega.
5. M2 v prvi različici obravnava enega otroka naenkrat in izbire po namenih. Brez odziva in potek roka ne pomenita Da ali Ne. Odgovor ene osebe ne ustvari odziva druge.
6. Obrazec pred objavo vsebinsko pregledamo. Sprememba različice zahteva nov pregled; dovoljene izjeme od ločenega potrjevalca so sledljive in posebej pooblaščene po pravilih M2.
7. Odločitve in zgodovina ostanejo ohranjene; dovoljena sprememba ali preklic ne prepiše prejšnjega dogodka. Šolsko pravilo določi skupno stanje in nadaljnjo obravnavo spora.
8. M2 odločitev in trajno namero za obveščanje shrani skupaj. M1 beleži dostavo; nobeno e-poštno stanje ne nadomesti odločitve uporabnika.
9. Ponovljena veljavna zahteva z istim ključem in vsebino vrne isti logični rezultat; drugačna vsebina vrne konflikt. Ločen poslovni ključ prepreči podvojitev istega dogodka tudi z novim ključem.
10. Pred pošiljanjem se preverijo pravica, kontakt, potreba, preklic, urnik in iztek. Preklic ene postavke ne ustavi drugih potreb. 503 ni odgovor »nepotreben« ali znan neuspeh dostave.
11. Negotov poštni izid ostane viden; brez samodejne ponovne predaje. Dokaz ponudnika ali pooblaščena izrecna ročna odločitev s svežimi preverjanji se obravnavata po potrjeni politiki. Predaja releju ni dokaz prejema.
12. Mitja je osebno sprejel možnost, da že veljavno prevzeto generično opozorilo fizično začne odhajati po odvzemu pravice. To ni dovoljenje za nov prevzem ali ponovno pošiljanje po odvzemu. Formalna meja ter tekma opomnika in odziva ostajata za D12/šolo; časovnih ali atomarnih zagotovil še ne trdimo.
13. Časi so v UTC, prikaz/urniki v Europe/Ljubljana. Osebni predlog redne dostave ponedeljek–petek 7.00–20.00 še potrebuje šolski dogovor, vključno s prazniki, izjemami in najdaljšim zadržanjem.
14. Hramba, izvoz, bralni dostop do zgodovine, podatkovne poti in pravila za mladoletne uporabnike potrebujejo šolsko/DPO presojo. Za test uporabimo izrecna sintetična pravila.

## Dvajset skupin prihodnjih preizkusov

To so merila za pripravo testov in človeške demonstracije, ne uspešno izvedeni testi. Združevanje ne ukinja posamičnih varnostnih ali pogodbenih preverjanj iz podrobnih gradiv.

| Št. | Scenarij | Pričakovani rezultat |
| --- | --- | --- |
| 1 | Dva računa z istim kontaktnim naslovom | Ločeni identiteti, pravice in odzivi; aktivacija predala ne dokazuje odnosa. |
| 2 | Druga družina, ugiban ID ali tuji scope_ref | Brez vsebine, kontaktov ali tujih prikaznih oznak. |
| 3 | Zaposleni zunaj dodeljenega oddelka | Predogled in objava zavrnjena. |
| 4 | Predlagani učenčev račun in ciljna skupina | Le lastna naslovljena obvestila; brez starševskih odločitev; ločena seznanitev. Scenarij je pogojen s sprejetjem razširitve. |
| 5 | Povezava obstaja brez potrjenega granta, nato odvzem | Odnos sam ne dovoli dejanja; odvzem podlage prevlada nad preostalim dovoljenjem. |
| 6 | Starejši uvoz po ročni omejitvi | Omejitev ostane; konflikt gre v pooblaščeno razrešitev. |
| 7 | Napačen CSV ali neznana referenca | Nobena delna aktivacija podatkov. |
| 8 | Ponoven uvoz, dvojnik in manjkajoča vrstica | Stabilni ID brez dvojnikov; manjkajoča vrstica sama ne odvzame pravice. |
| 9 | Aktivacija/obnova dveh oseb pri skupnem predalu | Pregledan individualni postopek; brez samodejne združitve oseb. |
| 10 | Odjava, CSRF, podtaknjen uporabnik in servisni klic | Uporabniška in servisna identiteta ločeni; neveljavna dejanja zavrnjena. |
| 11 | Informativno obvestilo, odprtje in seznanitev | Le izrecno dejanje ustvari potrditev konkretne različice. |
| 12 | Dva otroka in sprememba različice M1 | Skupinska potrditev brez delnega zapisa; stara potrditev ne potrdi novega navodila. |
| 13 | Več namenov in izpolnjen Ne oziroma brez odziva | Ločene odločitve; odgovor Ne ni pozabljen odgovor. |
| 14 | Dva otroka, dva odločevalca in nasprotni odgovori | Ločeni dogodki, en otrok na oddajo; skupno stanje po pravilu, spor v obravnavo. |
| 15 | Neodobrena ali po pregledu spremenjena različica M2 | Brez objave/oddaje mimo veljavne vsebinske odobritve. |
| 16 | Sprememba/preklic, potrdilo, zaključen ali umaknjen obrazec | Nova sled, zgodovina ostane; preklic veljavne privolitve sledi pregledanemu postopku. |
| 17 | Izpad M1, izgubljen odgovor 202, dvojni ključ in nova oznaka dogodka | Odločitev/namera ostaneta trajni; en logični prevzem, konflikt drugačne vsebine. |
| 18 | Potreba po opomniku, selektivni preklic, izpad P0/M2, tihi čas in iztek | Napaka zadrži dostavo; le izbrana potreba se ustavi; brez nove veljavnosti po izteku. |
| 19 | Negotov SMTP, odvzem med dostavo in obnova kopije | Vidna negotovost, brez samodejne ponovne predaje; že prevzet poskus in nov prevzem sta ločena; obnova ne oživi nedokazanih opravil. |
| 20 | Sveža namestitev, pravi P0/nadomestki, izvoz in dostopnost | Ponovljivi pogodbeni rezultati in človeški scenariji; dostop s tipkovnico/bralnikom ter pregledan izvoz. |

## Kaj še preprečuje formalni sprejem

D12 potrebuje dokončan slovar ID/obsegov, sheme OpenAPI in napak, meje, servisni mehanizem, politiko veljavnosti, konkretne dostavne meje in pogodbeno potrditev tehničnega nosilca ter mentorjev. Razširitev za učence dodatno potrebuje D01/D06/D07/D13/D16. D03/D09/D14 še veljajo pred prvo kodo oziroma vključitvijo zunanjih ekip, D08 pred sprejemom kode, celoten neodvisni človeški prevzem T pred A/I. Predloga omilitve prototipov ali avtorskega prevzema T nista sprejeta.
