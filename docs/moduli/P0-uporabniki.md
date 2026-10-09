# P0 – uporabniki, prijava in upravičenja

Datum: 8. oktober 2026  
Status: predlog za mentorjev in tehnični pregled

Referenčni P0 po [načrtu priprave in predaje](../projekt/priprava-referencnega-P0.md) pripravi pobudnik s pomočjo AI. Ta dokument opisuje model in ciljni obseg B; prvi prevzem T je podrobno določen v načrtu. Dijaki razvijajo predvsem M1/M2, omejene razširitve P0 pa so možne po dogovoru z mentorjem.

[Uvod za mentorje](../mentorji/razvojni-paket-P0-M1-M2.md) · [Pogodba vmesnikov](../arhitektura/vmesnik-P0-M1-M2.md)

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

Ponovni uvoz istega vira ne ustvari novih oseb. Preslikava izvornega ključa v notranji ID je stabilna. Odsotnost vrstice pri delnem uvozu ne pomeni samodejnega izbrisa ali odvzema pravic. Razlikovanje celotnega in delnega uvoza potrdita pilotna šola in skupni tehnični nosilec. Ročni popravki so sledljivi; konflikt z naslednjim uvozom se pokaže v predogledu.

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
| Zgodovinski zapis | Ohranimo ID osebe, različico in obseg dogodka; brez rutinskega podvajanja imen. Morebitni dokazni posnetek in hramba se potrdita v D07 |

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


## Aktivacijska pošta brez krožne odvisnosti

P0 za aktivacijo in obnovitev dostopa uporablja pošiljanje izbrane vzdrževane prijavne rešitve oziroma skupni infrastrukturni poštni mehanizem. Ne kliče poslovnega API M1. M1 lahko uporablja istega ponudnika SMTP, vendar ima svojo vrsto poslovnih dostav. Testna pošta obeh se prestreže v testnem predalu. Odločitev o izbiri rešitve in izvajalcu ostaja D03/D04.

## Predlog uvoznega formata

UTF-8, ločilo podpičje, prva vrstica so imena polj; narekovaji in ubežanje po pravilih CSV. Prazno valid_until pomeni odprt konec. Datumi veljavnosti so ISO 8601 UTC. Zahtevana polja ne smejo biti prazna. To ni zagotovljena shema izvoza eAsistenta.

| Tabela | Polja | Obveznost in omejitve |
| --- | --- | --- |
| persons | source_person_key; display_name; contact_email | Ključ in ime obvezna; ključ enoličen v viru in šoli; e-pošta neobvezna in ni enolična |
| roles | source_person_key; role | Obe obvezni; parent, student, teacher, office, admin; več vrstic za več vlog |
| students | source_student_key; source_person_key | Obe obvezni in enolični; ime iz persons |
| memberships | source_student_key; class_key; school_year; valid_from; valid_until | Vse razen konca obvezno; reference morajo obstajati |
| relationships | source_person_key; source_student_key; relationship_type; valid_from; valid_until | Konec neobvezen; parent ali guardian; naziv ne podeli pravic |
| staff_assignments | source_person_key; class_key; valid_from; valid_until | Konec neobvezen; zahtevana ustrezna vloga |
| grants | source_person_key; scope_key; permission; valid_from; valid_until; approval_ref | Vse razen konca obvezno; potrjen šifrant dovoljenj in sklic na pooblaščeno potrditev |

Viri in šola so določeni v metapodatkih uvoza. Šifranti oddelkov, dovoljenj in obsegov so verzionirani; neznana vrednost je napaka. Validacije preverijo reference, podvojene ključe, zaporedje datumov, obliko kontakta in dovoljeno kombinacijo vloge ter dodelitve. Uvoznik ne sme sam podeliti pravic zunaj svojega pooblastila. Skrbniške pravice zahtevajo ločen odobren postopek.

Za prvi uvoz uporabljamo izrecna dodajanja in spremembe. Manjkajoča vrstica nikoli sama ne izbriše osebe ali povezave. Poznejši način popolne uskladitve mora posebej pokazati predlagane zaključke veljavnosti in zahtevati pooblaščeno potrditev. Politiko potrdita šola in tehnični nosilec.

P0 je lastnik osnovne evidence in njenega uvoza. Uvozni zasloni M1/M2 ga uporabljajo prek dogovorjenega vmesnika oziroma vloge; ne ustvarjajo druge neodvisne evidence. Specifični vsebinski uvozi modulov so ločeni. Podrobni API za administrativni uvoz še potrebuje shemo in pregled dovoljenj.

## Dopolnitve testnega nabora

- parent-04: Starš Testni 04, brez e-pošte, papirna pot, veljavna povezava na student-04.
- student-04: Učenec Testni 04, razred-7a.
- staff-03: Tajništvo Testno 03, vloga office; le izrecno odobreni obsegi za uvoz in papirno pot.
- parent-01: preizkus potrditve za student-01 in student-02 skupaj; pred klikom oba jasno prikazana.

V API primerih uporabljamo iste ID parent-01, student-01 in staff-01. Testne poverilnice ustvari namestitev; gesla in skrivnosti niso del javnih CSV.
