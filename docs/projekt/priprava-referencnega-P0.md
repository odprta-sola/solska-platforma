# Priprava in predaja referenčnega P0

Datum: 9. oktober 2026
Status: načrt; delujoči P0, OpenAPI, nadomestki in pogodbeni testi še niso izdelani

Ta načrt podrobneje razdeli [razvojno naročilo](razvojno-narocilo-P0-M1-M2.md). Pobudnik osebno s pomočjo OpenAI in Claude pripravi razvojno osnovo in predlog paketa T. Pomoč AI ne pomeni človeškega tehničnega pregleda. Podjetje pobudnika s tem ni določeno za izvajalca. Pred izdelavo se zabeležijo izvajanje, obseg in način sodelovanja. Nosilec skupnih gradnikov koordinira izvedbo in predajo; prihodnje vzdrževanje se dodeli posebej.

## En vir obsega in prevzema P0

| Faza | Vključeno | Dokaz |
| --- | --- | --- |
| Prvi prevzem v T | Ena izmišljena šola; vnaprej pripravljeni individualni računi in skupen testni poštni predal; osebe, učenci, oddelki, povezave, dodelitve in dovoljenja; vir jezika ter prikaznih oznak po pravilih D12; vzdrževana lokalna prijava; preverjanje uporabniških in servisnih pravic; odvzem povezave in dovoljenja; sprememba kontakta; osnovni CSV uvoz s predogledom, validacijo, celovito potrditvijo in ponovitvijo; omejen kontaktni klic; API, testni podatki in ponovljiva namestitev | Neodvisni pregledovalec sistem namesti in izvede spodnje scenarije |
| Dopolnitev pred B | Individualna aktivacija in obnova računov pri skupnem e-poštnem predalu; celoten dogovorjeni obseg administrativnega uvoza, sledljivih popravkov in upravljanja; dokumentiran izvoz. Pripravo organizira pobudnik; omejen prepoznaven del je lahko dijaška razširitev le po dogovoru z mentorjem. | Preizkusi posebnih primerov iz naročila in dokumentacija |
| Pozneje | ArnesAAI, neposredna integracija eAsistent, avtomatizacija šolskega leta in večšolska centralna namestitev | Ločena odločitev |

Obseg v tabeli je merodajen za prvi prevzem P0; seznam v naročilu opisuje ciljni B. Prvi prevzem ne predpostavlja že pripravljene produkcijske prijave ali povezave s šolsko evidenco. Gesel, kriptografije in prijavnega protokola ne razvijamo na novo.

## Skupni paket T

P0 določa identiteto, povezave in pravice, ne pa sam vseh povezav modulov. Paket T mora dodati v D12 pregledano in potrjeno različico OpenAPI za P0 → M1/M2, M2 → M1 (dostava, stanje, posamezni preklic) in M1 → M2 (preverjanje potrebe po opomniku). Predlog pogodbe se lahko pripravi pred D12; odvisna implementacija uporablja šele potrjeno različico.

Izročiti je treba izmišljeni CSV in račune, razvojni prestrezni poštni predal, primer klica za vsako vrsto identitete, nadomestka M1/M2 z istimi shemami, pogodbeni test za dovoljeni in zavrnjeni klic ter za izpad in ponovitev dostave, opis podatkov in ukaze za ponovljivo namestitev. Testi vključijo tudi odsoten kontakt, več otrok, ločene račune z istim kontaktom, preklic samo posameznega opomnika ter negotov izid poštne predaje po potrjeni politiki.

Pred potrditvijo D12 je treba razrešiti slovar poslovnih ID, `scope_ref` in `grants.scope_key`, vir prikaznih oznak in jezika prejemnika, tihi čas, odsoten kontakt, zgodovinski dostop, trajni zapis pred odgovorom 202, selektivni preklic in meje ponavljanja pri negotovem izidu poštne predaje. To so naloge, ne že določene sheme.

## Človeški prevzem

Pregledovalec ni izdelal kode, ki jo prevzema. Po navodilih sam namesti osnovo in preveri:

1. Prijava testnega starša prikaže le njegova otroka; neposreden naslov druge družine je zavrnjen.
2. Dva starša s skupnim kontaktom ostaneta različna uporabnika; dovoljenje je vezano na konkretno povezavo in obseg.
3. Odvzem povezave prepreči novo dejanje kljub sicer veljavnemu dovoljenju; odvzem dovoljenja prav tako prepreči dejanje.
4. Napačen CSV ne povzroči delnega prepisa, ponovljen uvoz ne podvoji oseb; sprememba kontakta je sledljiva.
5. Servisni klic za kontakt je dovoljen samo za evidentirano zahtevo in prejemnika; tuj ali ugiban obseg je zavrnjen.
6. Izvorno kodo za avtorizacijo, `scope_ref`, kontaktni klic in CSV uvoz pregleda neodvisen človek; zabeleži ugotovitve in ponovitve testov.
7. Po ponastavitvi izmišljenih testnih podatkov zažene pogodbene teste proti nadomestkoma M1/M2, vključno z dovoljeno in zavrnjeno dostavo.
8. Ob izpadu P0 M1/M2 ne dovolita zaščitenega dejanja in ne pošljeta sporočila na slepo; po obnovi preverita trenutne pravice.
9. Prijava in osnovna opravila P0 delujejo s tipkovnico, imajo viden fokus in razumljive napake; opravi se osnovni pregled z bralnikom zaslona.

Šele celoten prevzem T sprosti odvisni razvoj A in I. Nadomestka M1/M2 ne nadomestita P0. Dijaki dobijo zagotovljeno kodo, navodila, pogodbo in testne podatke; mentor določi njihove samostojne izdelke in pravila uporabe AI. Razširitve P0 so dodatne individualne naloge po dogovoru, ne predpostavljena obveznost.

## Projektni pogoji in sled izvora

| Dejanje | Pogoj |
| --- | --- |
| Prva koda oziroma vključitev zunanjih ekip, tudi primerjalni prototipi | D09/D14: imenovan drugi skrbnik, nosilec zasebnih varnostnih prijav in namestnik, preverjeni dostopi ter odzivni roki; D03: imenovan skupni tehnični nosilec in dogovor o tehnologiji ter skupnih varnostnih funkcijah skladno s [CONTRIBUTING.md](../../CONTRIBUTING.md) |
| Priprava predloga pogodbe | Dovoljena kot osnutek; D12 ostaja odprt |
| Implementacija API P0, ki ga uporabljata M1/M2, in druga odvisna implementacija | V D12 potrjena različica pogodbe pred vezavo na ta API; predlog sheme in neodvisne raziskave se lahko pripravijo prej. Selektivni preklic mora biti potrjen pred I. |
| Sprejem kode v repozitorij | D08: pravice avtorja za objavo, pogoji prispevka in licence odvisnosti |
| Razdelitev maturitetnih izdelkov | Mentorjeva presoja izvedljivosti in samostojnega prispevka; institucionalni viri niso predpostavljeni |
| Začetek A/I | Celoten človeški prevzem T in izpolnjeni predhodni pogoji |

Za vsak prispevek se zabeležijo avtor, izvor predhodne kode, uporaba AI, odvisnosti in licence, obseg človeškega pregleda ter samostojni prispevek dijaka. Ta predloga ne potrjuje D08 ali formalne ustreznosti maturitetne naloge. D01–D16 ostajajo v statusih [registra](odlocitve.md).

Pred prvo kodo pobudnik v projektnem zapisu poveže način osebnega, nekomercialnega izvajanja z [razdelkom o nekomercialni vlogi](odgovornosti.md#nasprotje-interesov-in-nekomercialna-vloga). Zapis zajame obseg dela, odsotnost plačila podjetju iz projektnih sredstev, avtorstvo in izvor kode za poznejšo presojo D08. To ni pravno mnenje ali zaključena odločitev o pravicah.

Ker je P0 na kritični poti, pobudnik in tehnični nosilec pred dogovorom rokov z mentorji ocenita trajanje T po izdelkih, tveganjih in razpoložljivosti neodvisnega pregledovalca. Ocena ni obljuba ur ali datuma; A/I se začne šele po dejanskem prevzemu T.
