# P0, M1 in M2 – razvojni paket za mentorje

Datum: 8. oktober 2026  
Status: osnutek za mentorjev in tehnični pregled  
Namen: razumljiv začetek dela, ocena obsega in dogovor pred vzporednim razvojem  
Potrditev: ni potrjen izvedbeni načrt, maturitetna naloga ali dovoljenje za produkcijo

## 1. Kako brati ta paket

Najprej preberite razdelke 2–5 in praktične primere v razdelku 7. Nato preglejte P0, mejnike ter osnutek vmesnikov. Podrobne zahteve ostanejo v [M1](../moduli/M1-eSporocanje.md), [M2](../moduli/M2-eSoglasja.md), [arhitekturnih izhodiščih](../arhitektura/izhodisca.md) in [registru odločitev](../projekt/odlocitve.md).

Ta paket povezuje razlago za mentorje, razvojne naloge, primere, testne podatke in osnutek API. Namenoma je en dokument, ki ga je mogoče tudi prenesti in posredovati kot Markdown. Manjši prvi prototip ne zmanjšuje meril produkcijskega pilota iz specifikacij.

## 2. Izhodišča in status dogovorov

Pobudnik je 8. oktobra 2026 podal naslednja izhodišča za pripravo:
- Mentor oceni celoten cilj in posebej omejen prvi prototip.
- Predvidena pilotna šola je vsaj OŠ Vojke Šmuc Izola; preizkus pri GEPŠ je treba preveriti. To ni potrditev produkcijske uvedbe.
- Razvoj in demonstracije uporabljajo izključno izmišljene podatke.
- Šola uporablja eAsistent. Oblika in razpoložljivost izvoza nista preverjeni.
- Osnovna namestitev deluje z lokalnimi računi in CSV uvozom, brez obvezne povezave z eAsistentom ali ARNES.
- Možnost ArnesAAI ostane zahtevana razvojna smer, predvidoma v naslednji fazi; posamezni šoli njena uporaba ni obvezna. Termin in izvedba še nista potrjena.
- P0, M1 in M2 so predlagani za razvoj dijakov pod mentorskim in strokovnim vodstvom.
- Po navedbi pobudnika je na eni šoli približno 20–25 potencialnih maturantov. Sodelovanje vseh ni dogovorjeno.
- Ohranimo povezavo M2 z M1 za obveščanje. Nadomestni produkcijski kanal za M2 brez M1 ni del tega predloga.
- Vmesnike določimo pred vzporednim razvojem in zgodaj preverimo skupno delovanje.

Predlog 2–3 dijakov na modul, razrez nalog, spodnji API, podatkovna shema in mejniki so predlogi za mentorje. Ocen ur, oseb, tehnologije in rokov ne določajo. D01–D16 ostajajo odprte po registru; paket jih sam ne zaključi.

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

## 4. Kaj naj mentor oceni

Mentor za vsako nalogo navede: fazo, dijaka oziroma ekipo, ure dijakov, ure mentorja, potrebno strokovno delo, odvisnosti in merilo zaključka. Celoten M1 se ne ocenjuje avtomatično kot 150–250 ur.

| Naloga | Predlagana faza | Ocena ur in nosilec |
| --- | --- | --- |
| Dogovor o identitetah, upravičenjih in API | Pred vzporednim razvojem | Določi mentor s skupnim tehničnim nosilcem |
| P0: lokalna prijava, testna evidenca in pravice | Prvi prototip | Za oceno |
| P0: CSV predogled in varen uvoz | Naslednji razvojni mejnik | Za oceno |
| M1: objava, prikaz in potrditev | Prvi prototip | Za oceno |
| M1: priloge, različice, opomniki in papirna pot | Naslednji razvojni mejnik | Za oceno |
| M2: testni obrazci in izrecne odločitve | Vzporedni prototip po dogovoru API | Za oceno |
| M2: preklici, spori, potrdila in zgodovina | Naslednji razvojni mejnik | Za oceno |
| Skupni preizkusi, dostopnost, namestitev | Skozi razvoj | Za oceno |
| Produkcijski pregled in vzdrževanje | Ločen prevzem | Potreben imenovani strokovni nosilec |

Možna začetna razporeditev je 2–3 dijake na modul. Mentor potrdi individualne prispevke in formalno primernost nalog. Vsak dijak mora znati razložiti in zagovarjati svoj del. Vsaka ekipa testira svojo izvedbo; neodvisen pregled je dodatna naloga.

Dovoljeni so primerjalni prototipi. Vsi uporabljajo iste dogovore in testne primere. Osnovo za nadaljevanje izberemo zgodaj po pravilnosti, dostopih, povezljivosti, razumljivosti kode, testih in namestitvi. Izbira najboljših ločenih izdelkov šele ob koncu ni načrt integracije.

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
| Zaslon | Nujne informacije |
| --- | --- |
| Seznam | Naslov, otrok oziroma lastno obvestilo, manjkajoča potrditev ločeno od neodprte vsebine |
| Obvestilo | Besedilo, različica, priloge, rok in obseg potrditve |
| Priprava | Vrsta, ciljna skupina, predogled vsebine in prejemnikov |
| Odzivi | Posamezni upravičenci, različica, potrditev, napaka pošiljanja, papirna pot |
| P0 upravljanje | Osebe, povezave, veljavnost upravičenj, predogled uvoza |

## 6. P0 in evidenca uporabnikov

### 6.1 Tri različne naloge

| Naloga | Pomen |
| --- | --- |
| Evidenca | Kdo so osebe, oddelki in povezave starš–otrok |
| Prijava | Kako oseba dokaže identiteto računa |
| Upravičenja | Do katere vsebine sme dostopati in katera dejanja sme opraviti |

E-poštni naslov ni identifikator osebe. Starša s skupnim naslovom imata ločena računa in ločene potrditve. Učenec lahko obstaja v evidenci brez uporabniškega računa. Uporabnik si ne določi povezave z otrokom sam.

P0 uporablja vzdrževano rešitev za prijavo. Dijaki ne razvijajo lastne kriptografije ali novega sistema shranjevanja gesel. Izbor knjižnic oziroma storitve, sej in integracije potrdi skupni tehnični nosilec.

### 6.2 Kje so podatki

P0 je del namestitvenega paketa in uporablja podatkovno zbirko v dogovorjenem okolju šole. M1 hrani obvestila in potrditve, M2 obrazce in odločitve. Na osebe se sklicujeta s stalnimi identifikatorji P0. Skupna prijava ne daje samodejnega dostopa do vseh podatkov.

Lokalni način ne potrebuje ArnesAAI. Poznejša zunanja prijava se varno poveže z obstoječo identiteto; enak e-poštni naslov sam ni dovolj za samodejno združitev računov. ArnesAAI ne nadomesti šolske evidence povezav starš–otrok. Izvedbo in razpoložljive atribute je treba pred integracijo preveriti.

### 6.3 Uvoz in spremembe

Za razvoj AI pripravi izmišljene podatke. Pred produkcijo šola določi odgovorno osebo za pravilnost evidence in povezav; AI tega ne potrjuje namesto šole.

Predlagan postopek:
1. Šola pridobi dovoljen izvoz iz svoje evidence. Možnosti eAsistenta se preverijo; povezave ali formata ne predpostavljamo.
2. Podatke preslika v dokumentiran uvozni format P0.
3. Sistem prikaže dodajanja, spremembe, nejasne povezave in napake.
4. Pooblaščena oseba potrdi pravilnost.
5. Uvoz se izvede celovito ali se zavrne; napaka ne sme delno prepisati evidence.
6. Zabeležijo se izvajalec, čas, vir in rezultat brez nepotrebnega podvajanja osebnih podatkov v tehničnih dnevnikih.

Ponovni uvoz istega vira ne ustvari novih oseb. Preslikava izvornega ključa v notranji ID je stabilna. Odsotnost vrstice pri delnem uvozu ne pomeni samodejnega izbrisa ali odvzema pravic. Razlikovanje celotnega in delnega uvoza mora potrditi mentor. Ročni popravki so sledljivi; konflikt z naslednjim uvozom se pokaže v predogledu.

### 6.4 Aktivacija in podpora

Šola preveri osebo, kontakt in povezavo z otrokom; nato pošlje časovno omejeno povabilo za enkratno uporabo. Aktivacija preveri nadzor nad predalom, ne sorodstvenega razmerja. Uporabnik nastavi prijavo po pravilih izbrane rešitve. Povabilo je vezano na točno določen račun.

Obnovitev dostopa, sprememba kontakta in odvzem dostopa uporabljajo pregledane postopke izbrane rešitve. Uporabniku brez uporabne e-pošte šola zagotovi pomoč oziroma papirno pot. Konkretni časi veljavnosti, varovanje skrbniških računov in postopki podpore so odprti pred produkcijo.

Cilj je brezplačna uporaba za starša in rešitev brez nujnih plačljivih SMS. Gostovanje, pošiljanje, kopije, pregledi in vzdrževanje imajo stroške oziroma zahtevajo delo; ničelnega stroška šoli ne obljubljamo.

### 6.5 Posebni primeri

| Primer | Zahtevano ravnanje |
| --- | --- |
| Več otrok istega starša | Ena oseba, več preverjenih povezav; jasno izbran obseg |
| Dva starša z istim naslovom | Ločeni identiteti in odzivi |
| Sprememba oddelka | Sprememba članstva z veljavnostjo; brez samodejnega dostopa do stare zgodovine |
| Odvzem povezave | Preverjanje pri naslednjem dostopu in pred pošiljanjem; ustavitev neveljavnih opomnikov |
| Polnoletstvo med letom | Nova dejanja po pravilih, ki jih potrdi šola; stare odločitve se ne prepišejo |
| Konec šolskega leta | Novim članom ne odpremo starih obvestil; avtomatizacija prehoda je poznejša faza |
| Neznano upravičenje ali nedosegljiv P0 | Zaščiteno dejanje se ne dovoli na slepo; uporabniku razumljiva napaka |
| Zgodovinski zapis | Ohranimo tedanjo osebo, različico in obseg; hramba po potrjenih pravilih |

## 7. Praktični primeri M1

Vsi primeri so izmišljeni. E-pošta vsebuje splošno opozorilo in zaščiteno povezavo, brez imen otrok in javnih prilog. Vsebina je po prijavi. Lastni vrsti M1 sta dve; dostava za M2 je dodatna uporaba kanala, ne tretja vrsta seznanitve.

### 7.1 Informativno: knjižnica

Pošiljatelj: knjižničarka. Prejemniki: upravičene osebe vseh oddelkov. Naslov: Urnik knjižnice v prihodnjem tednu. Priloga: brez. Rok: brez.

Besedilo: »Knjižnica bo prihodnji teden odprta med 8. in 12. uro. Izposoja po pouku ne bo mogoča. Naslednji teden spet velja običajni urnik.«

E-pošta: »V šolskem portalu je novo informativno obvestilo. Za ogled se prijavite.«

Prejemnik prebere; gumba za potrditev ni. Prikaz vsebine ne dokazuje dejanskega branja. Samodejni opomniki niso privzeti.

### 7.2 Informativno: dan odprtih vrat

Pošiljatelj: vodstvo. Prejemniki: upravičene osebe vseh oddelkov. Naslov: Vabilo na dan odprtih vrat. Priloga: program PDF. Rok potrditve: brez.

Besedilo: »V četrtek ob 16. uri vas vabimo na dan odprtih vrat. Predstavili bomo dejavnosti in izdelke učencev. Program je v prilogi. Prijava ni potrebna.«

E-pošta: »V šolskem portalu je novo informativno obvestilo s prilogo.«

Prejemnik odpre program po prijavi. M1 ne vodi prijav in odprtja ne šteje kot udeležbo. Priloga sodi v naslednji razvojni mejnik.

### 7.3 Zahtevana seznanitev: športni dan

Pošiljatelj: razrednik. Prejemniki: upravičenci 7. a. Naslov: Zbirno mesto in oprema. Priloga: seznam opreme PDF. Rok: sreda ob 18. uri, konkretni datum določi avtor.

Besedilo: »Športni dan bo v petek. Zbor je ob 7.45 pred glavnim vhodom, vrnitev predvidoma ob 13. uri. Učenci naj imajo primerno obutev, pijačo in zaščito pred dežjem. Prosimo za potrditev seznanitve do navedenega roka.«

Pred gumbom je prikazan otrok in različica. Gumb: »Seznanjen/-a sem«. Gre za navodilo za že dogovorjen dogodek, ne pridobivanje dovoljenja za udeležbo.

E-pošta: »V šolskem portalu vas čaka obvestilo z zahtevano potrditvijo seznanitve.«

Odprtje ni potrditev. Opomnik prejme upravičenec, ki še ni potrdil aktualne zahtevane različice, po pravilih šole. Sprememba zbirnega mesta ustvari novo različico in novo zahtevo za potrditev. Prejšnja ostane v zgodovini.

### 7.4 Zahtevana seznanitev: začasni vhod

Pošiljatelj: vodstvo. Prejemniki: upravičenci prizadetih oddelkov. Naslov: Začasni vhod med obnovo. Priloga: skica; vse navodilo tudi v besedilu. Rok: pred začetkom spremembe.

Besedilo: »Od ponedeljka bo glavni vhod zaprt. Učenci bodo vstopali pri telovadnici. Pot bo označena. Prosimo, seznanite otroka in potrdite svojo seznanitev.«

Gumb: »Seznanjen/-a sem«. E-pošta je splošno opozorilo kot v prejšnjem primeru.

Potrditev prvega starša ne potrdi drugega. Ali za skupno obravnavo zadostuje eden, določi šola; posamezni statusi ostanejo ločeni. Pri papirni poti zaposleni posebej evidentira izročitev in morebitno papirno potrditev. Izročitev ni potrditev.

### 7.5 Dostava za M2: objavljen obrazec

M2 objavi pregledani testni obrazec o objavi fotografij. Določi upravičence in M1 naroči: »V šolskem portalu vas čaka obrazec za odločitev.«

Povezava vodi v M2. Uporabnik tam prebere in odda izbire. Predhodna potrditev seznanitve v M1 ni potrebna. M1 hrani dostavo; M2 hrani obrazec, odločitev in potrdilo. Ta primer ni pravno potrjen obrazec za produkcijo.

### 7.6 Dostava za M2: opomnik

M2 naroči opomnik osebi brez zahtevanega odziva in določi najpoznejši dovoljeni čas pošiljanja.

E-pošta: »V šolskem portalu vas še čaka obrazec za odločitev.«

Če uporabnik prej odgovori, M2 prekliče zahtevo, M1 pa pred pošiljanjem preveri potrebo. Zavrnitev je odziv in ni razlog za opominjanje kot pri pozabljenem odgovoru. Če preverjanje ni dosegljivo, je opomnik zadržan; po izteku se ne pošlje, razlog je viden. Že predane e-pošte ni mogoče priklicati; povezava pokaže aktualno stanje.

## 8. Osnutek dogovora API P0–M1–M2

Status: predlog za D12, ne potrjena implementacijska pogodba. Mentorji in skupni tehnični nosilec naj pred začetkom odvisne implementacije potrdijo konkretne sheme, načine prijave ter teste. OpenAPI, delujoči nadomestni strežnik in avtomatski pogodbeni testi še niso izdelani.

### 8.1 Skupna pravila

- Stabilni neprosojni identifikatorji; e-pošta in prikazno ime nista ključa.
- Različica poti v1; JSON; časovne oznake ISO 8601 v UTC; prikaz Europe/Ljubljana.
- Vsi produkcijski klici so zaščiteni in preverijo dovoljenje modula ter končnega uporabnika. Uporabniškega ID iz poljubnega zahtevka se ne zaupa brez preverjene identitete.
- Modul preverja tudi lastništvo lastnega vira. P0 ne odloča o vsebini obrazca ali različici obvestila.
- Minimalni odgovori; gesla, prijavni žetoni in vsebina odločitev ne potujejo v zahteve za obveščanje.
- Napaka ima code, razumljivo message in request_id. Dnevniki ne vsebujejo skrivnosti.
- Predlog HTTP: 400 napačna shema, 401 neprijavljen klic, 403 nedovoljeno dejanje, 404 nedostopen/neobstoječ vir po dogovorjeni politiki, 409 konflikt različice ali ključa ponovitve, 503 odvisnost ni dosegljiva.
- Ponovitev istega request_id z enako vsebino ima en logični učinek; drugačna vsebina z istim ključem vrne konflikt. Obseg ključa je klicoči modul in namestitev.
- API ne zahteva neposrednega branja tuje baze. Podrobnosti sej, avtorizacije med storitvami, omejitev klicev in življenjske dobe ključev se potrdijo v D12.

### 8.2 Predlagana dejanja

| Klic | Namen | Minimalni rezultat |
| --- | --- | --- |
| GET /api/v1/me v P0 | Preverjena identiteta trenutne seje | person_id in dovoljene vloge |
| GET /api/v1/me/relationships v P0 | Lastne veljavne povezave | student_id, obseg in veljavnost |
| POST /api/v1/authorizations/check v P0 | Preverjanje konkretnega dejanja | allowed, reason_code, checked_at |
| POST /api/v1/notifications v M1 | Prevzem zahteve M2 | notification_id, stanje queued, čas prevzema |
| GET /api/v1/notifications/{id} v M1 | Stanje lastne zahteve | Stanje dostave in minimalna koda napake |
| POST /api/v1/notifications/{id}/cancel v M1 | Ponovljiv preklic | cancelled ali already_handed_off oziroma drugo končno stanje |
| POST /api/v1/reminders/check v M2 | Preverjanje potrebe pred pošiljanjem | needed in reason_code; nedosegljivost je napaka |

Prijavni protokol se izbere iz vzdrževane rešitve; ta tabela ne predpisuje lastnega protokola za gesla. Za GET seznamske klice je treba pred potrditvijo določiti straničenje in meje.

Primer preverjanja pravice (identiteto klicočega in osebe strežnik preveri):
```json
{"person_id":"person-parent-01","student_id":"student-01","action":"m1.confirm","school_id":"school-demo"}
```
Primer odgovora:
```json
{"allowed":true,"reason_code":"ACTIVE_RELATIONSHIP","checked_at":"2026-10-08T10:00:00Z"}
```
M1 poleg tega preveri, da je obvestilo naslovljeno na osebo, da različica velja in da je zahtevana potrditev.

Primer zahteve M2 za opomnik:
```json
{
  "request_id":"demo-reminder-001",
  "kind":"reminder",
  "recipient_ids":["person-parent-01"],
  "text":"V šolskem portalu vas čaka obrazec za odločitev.",
  "target":{"module":"M2","resource_id":"form-demo-01"},
  "need_ref":"need-demo-001",
  "expires_at":"2026-10-09T16:00:00Z"
}
```
Zaščiteno povezavo M1 sestavi iz dovoljenega modula in sklica; poljubnih zunanjih URL ali callback naslovov ne sprejema. Pravice ponovno preveri ob kliku ciljni modul. Zahteva za običajno obvestilo ne potrebuje need_ref; polje expires_at je obvezno pri opomniku.

Predlog stanj zahteve: queued, held, handed_off, failed, cancelled, expired. handed_off pomeni predajo poštnemu strežniku, ne prejema. Pri več prejemnikih se vodi stanje posamezne dostave; ponavljanje ne sme ponovno poslati že obdelanim prejemnikom. Agregatni prikaz je treba potrditi.

Primer preverjanja potrebe:
```json
{"need_ref":"need-demo-001","recipient_id":"person-parent-01"}
```
```json
{"needed":false,"reason_code":"NO_LONGER_REQUIRED"}
```
Odgovor ne razkrije, ali je oseba privolila, zavrnila ali preklicala. M1 ne sklepa o potrebi ob napaki. Preverjanje upravičenja in potrebe sta dve ločeni preverjanji.

Pravila zadržanja in izteka ostajajo normativno opisana v [M1: veljavnost opomnikov](../moduli/M1-eSporocanje.md#veljavnost-opomnikov). Ta paket jih ne podvaja kot nov vir. Največji čas zadržanja mora biti potrjen pred pilotom. Preverjanje potrebe zmanjša tekmovanje med odzivom in dostavo, ne more pa priklicati že predane pošte.

### 8.3 Potrditev pogodbe in spremembe

Pred vzporednim razvojem:
1. Potrdimo obseg P0, identifikatorje, preverjanje pravic in odgovornega za pogodbo.
2. Navedene primere pretvorimo v strojno preverljive sheme, npr. OpenAPI.
3. Pripravimo testne odgovore oziroma nadomestni strežnik, ki uporablja iste sheme.
4. Pripravimo skupne preizkuse dovoljenih in zavrnjenih klicev, ponovitev, izpadov in preklicev.
5. Različico potrdijo mentorji in skupni tehnični nosilec v D12.
6. Zgodaj izvedemo pot P0 prijava → M2 odločitev → M1 dostava.

Nezdružljiva sprememba zahteva uskladitev vseh prizadetih ekip in novo različico oziroma dogovorjen prehod. Sprememba samo v eni ekipi ni potrjena sprememba pogodbe.

## 9. Izmišljeni testni podatki

Naslednji mali nabor je osnova za razširitev. ID so ponazoritveni nizi; končni format določi pogodba. Domene example.invalid se ne uporabljajo za resnično dostavo. Ves promet razvojne e-pošte prestreže lokalni testni predal.

| ID | Oseba/vloga | Povezava |
| --- | --- | --- |
| staff-01 | Učitelj Testni 01 | Oddelek razred-7a |
| staff-02 | Učitelj Testni 02 | Oddelek razred-8b |
| parent-01 | Starš Testni 01 | student-01 in student-02 |
| parent-02 | Starš Testni 02 | student-01; isti kontakt kot parent-01 |
| parent-03 | Starš Testni 03 | student-03; druga družina |
| student-01 | Učenec Testni 01 | razred-7a |
| student-02 | Učenec Testni 02 | razred-8b |
| student-03 | Učenec Testni 03 | razred-7a |

Primer kontaktov: parent-01 in parent-02 uporabljata family01@example.invalid. Povezava ne nastane na podlagi tega naslova. Vsak prijavni račun ima svoje enolično uporabniško ime.

Za uvoz se predlaga več povezanih tabel: osebe (source_person_key, display_name, contact_email), učenci in članstva (source_student_key, class_key, school_year), povezave (source_person_key, source_student_key, relationship_type, valid_from, valid_until) ter dodelitve zaposlenih. To je predlog sheme P0, ne format izvoza eAsistenta. Pravice se potrdijo ločeno od naziva razmerja. Gesla niso del uvoza.

Razširjeni testni scenariji: dvojnik izvornega ključa, neznan otrok, neveljaven kontakt, ponovni uvoz, odvzeta povezava, sprememba oddelka in testni dijak s prehodom v polnoletstvo. Zadnji je splošen preizkus P0/M2, ne potrditev GEPŠ pilota. Pravila po polnoletstvu so v testu eksplicitno nastavljena, ne domnevana iz datuma rojstva.

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
| Skupna namestitev | Ponovljiva demonstracija brez produkcijskih poverilnic |

Prvih sedem vrstic tvori jedro prve demonstracije; ostale se dodajajo glede na mejnik. Vse produkcijske zahteve, tudi varnost, dostopnost, jeziki, kopije, hramba, pravni pregled M2 in vzdrževalec, ostanejo v obstoječih specifikacijah. Uspešna maturitetna naloga ne pomeni produkcijskega prevzema.

## 11. Odprte odločitve in naslednji sestanek

| Register | Kaj zahteva ta paket |
| --- | --- |
| D01 | Potrditev prvega prototipa in nadaljnjega obsega M1 |
| D02, D13 | Mentorji, ekipe, individualni izdelki, ure in mejniki |
| D03 | Nosilec P0, izbira vzdrževane prijave in strokovni pregled |
| D04 | Testno in produkcijsko okolje, pošta, kopije ter stroški |
| D05, D06 | Jeziki, dostopnost, upravičenci in pravilo potrditve |
| D07, D09, D10 | Hramba, vzdrževanje, namestnik in produkcijski prevzem |
| D11, D16 | Izbrani postopek M2 in pravila za upravičence, tudi polnoletne |
| D12 | Potrditev pogodbe P0–M1–M2, shem in testov; razširitev dosedanjega obsega |
| D08, D15 | Pravice prispevkov ter licenca kode in dokumentacije |
| D14 | Nosilec varnostne obravnave in nadomeščanje pred prvo kodo |

Na sestanku se najprej potrdita razumevanje primerov in obseg P0, nato delitev dela in API. Prva tehnična implementacija je odvisna od ustreznih odprtih odločitev v registru; datum nastanka tega paketa jih ne razreši.

Paket ne potrjuje pošiljanja dogovora ravnateljema, njunih pisnih potrditev ali odziva Skupnosti šol. Ne spreminja zgodovinskega Doc 1, ki ni bil v tej nalogi usklajen.

## 12. Navodilo za neodvisni pregled s Claude AI

Preglej ta PR in celoten dokument, nato ga primerjaj s specifikacijama M1/M2, povzetkom, arhitekturo, odgovornostmi in registrom odločitev na osnovni veji. Preveri tudi dejanski diff, ne samo opisa PR.

Naloga je pregled, brez sprememb, objave komentarjev ali združevanja:
1. Preveri skladnost P0, M1 in M2 ter razmejitev evidenc, prijave in upravičenj.
2. Preveri, da je M2 za obveščanje povezan z M1 in da ni neopazno uvedena druga arhitektura.
3. Preveri razumljivost šestih primerov, razliko med seznanitvijo in odločitvijo ter papirno pot.
4. Preveri CSV predlog, podvojene kontakte, aktivacijo, spremembe pravic in polnoletstvo.
5. Preveri API predlog: avtorizacijo, minimalne podatke, ponovitve, preklice, stanja, izpade, iztek in tekmovanje odziva s pošiljanjem.
6. Opozori na manjkajoče sheme oziroma odločitve, ki še preprečujejo začetek implementacije.
7. Preveri izvedljivost razdelitve dijaškega dela, brez domneve, da so ure ali ekipe potrjene.
8. Loči blokirajoče napake, pomembne dopolnitve in uredniške predloge.
9. Za ugotovitev navedi datoteko, razdelek, konkreten problem in predlog popravka.
10. Povej, ali je dokument primeren za mentorjev pregled in posebej, ali je že zadosten za začetek razvoja.

Ne predstavljaj projektnih predlogov kot potrditve šole ali pravne ustreznosti. Če do PR nimaš dostopa, to izrecno povej; pregled pripetega MD ne potrjuje skladnosti s celotnim repozitorijem.
