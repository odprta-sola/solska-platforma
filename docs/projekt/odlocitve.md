# Register odločitev

Status: začetni delovni register  
Datum: 5. oktober 2026

## Način vodenja

Predlog se odpre v issueju ali pull requestu. Sprejeta odločitev navede datum, odgovorno osebo, povezavo na gradivo, razlog in posledice. Tehnična združitev ni samodejna institucionalna potrditev.

| ID | Vprašanje | Status | Nosilec potrditve |
| --- | --- | --- | --- |
| D01 | Obseg učnega izdelka in prvega pilota M1 | Odprto | Naročnik (pobudnik) in pilotna šola; mentor oceni izvedljivost |
| D02 | Mentor, dijaki in roki | Odprto | Razvojni zavod |
| D03 | Skupni tehnični nosilec in skupni gradniki | Osebni sprejem pobudnika 12. 11. 2026 (nosilec: pobudnik); potrditev sodelujočih zavodov odprta | Sodelujoči zavodi |
| D04 | Gostovanje, e-pošta in kopije | Odprto | Pilotna šola in skupni tehnični nosilec |
| D05 | Jeziki in dostopnost pilota (podatkovni model je večjezičen od začetka; zahtevani jeziki za namestitve po državi, npr. italijanščina in madžarščina, se pravno preverijo) | Odprto | Pilotna šola in nosilec projekta |
| D06 | Upravičeni prejemniki in pravila potrjevanja | Odprto | Pilotna šola |
| D07 | Hramba, dostopi in podatkovne poti | Odprto; gradivo za posvet: [varstvo podatkov, stanje in vrzeli](varstvo-podatkov-P0.md) | Pilotna šola ob posvetu z DPO |
| D08 | Licenca EUPL 1.2 in pravice prispevkov | EUPL 1.2 za kodo potrjena 12. 11. 2026; postopek prispevkov (inbound = outbound, DCO, vzdevek, izjava s soglasjem staršev ob prvem prispevku, brez praga) sprejel pobudnik 12. 11. 2026; pravni pregled obrazca pri šoli odprt | Nosilec projekta in avtorji |
| D09 | Vzdrževanje, podpora in namestnik | Pobudnik je edini vzdrževalec in skrbnik repozitorija; drugi skrbnik ni imenovan (določitev z 12. 11. 2026 umaknjena 13. 11. 2026, [vloge skrbnikov](#vloge-skrbnikov-13-novembra-2026)); tveganje enega skrbnika je priznano, drugi skrbnik je pogoj pred produkcijskim pilotom | Sodelujoči zavodi |
| D10 | Merila produkcijskega prevzema M1 in M2 | Predlog v specifikacijah | Skupni tehnični nosilec in pilotna šola |
| D11 | Postopek pilota M2, besedilo obrazca in pravila odločanja | Odprto | Pilotna šola ob vsebinskem in pravnem pregledu |
| D12 | [Pogodba P0–M1–M2](../arhitektura/vmesnik-P0-M1-M2.md): minimalno obveščanje in skupni vir identitet ter upravičenj | **Sprejeto 13. 11. 2026** (naročnik): točke A in B po [paketu](d12-paket-za-odlocitev.md), izvedene v P0, pogodbi in nadomestkih; pogodba zamrznjena kot `1.0.0` ([zapis zamrznitve](../../api/zamrznitve.txt)) | Naročnik (pobudnik) |
| D13 | Razdelitev ekip, nosilci modulov in ocena ur po fazah | Odprto | Sodelujoči zavodi in mentorji |
| D14 | Nosilec obravnave zasebnih prijav, namestnik in roki odziva | Kanal omogočen; nosilec: pobudnik; namestnik ni imenovan (določitev z 12. 11. 2026 umaknjena 13. 11. 2026); roki odziva odprti | Nosilec projekta in skrbnik repozitorija |
| D15 | Licenca dokumentacije in pravice besedil; ločeno od licence kode | CC BY-SA 4.0 za dokumentacijo, osebni sprejem pobudnika 12. 11. 2026 ([LICENSE-dokumentacija.md](../../LICENSE-dokumentacija.md)); potrditev zavodov odprta | Nosilec projekta in avtorji |
| D16 | Prejemniki in odločevalci pri polnoletnih dijakih, prehod med letom in ustreznost privolitve za postopek | Odprto | Pilotna šola ob pravnem in podatkovnem pregledu |

Osnutek D12 z dne 8. oktobra 2026 konkretizira že predvidene skupne identitete in obveščanje. Sheme, prijavni protokol, nosilci, testni nadomestki in pogodbeni preizkusi še niso potrjeni; D12 ostaja odprt. Izhodišča za razdelitev dijaškega dela so v [vodniku za mentorje](../mentorji/razvojni-paket-P0-M1-M2.md).

## Izhodiščni obseg pobudnika

8. oktobra 2026 je pobudnik določil pripravo [konkretnega razvojnega naročila P0–M1–M2](razvojno-narocilo-P0-M1-M2.md). D01 in D13 zato obravnavata izvedljivost, razdelitev ter morebitne spremembe podanega obsega. Cilja projekta ni treba na novo oblikovati mentorjem. Naročilo ne zaključi D01–D16; potrditve virov, izvajalcev, pogodbe in produkcije ostajajo pri določenih nosilcih.

9. oktobra 2026 je pobudnik usmeritev dopolnil: osebno s pomočjo AI pripravi referenčni P0 in paket T; dijaki razvijajo predvsem M1/M2. Mentorji ocenijo izvedljivost in predlagajo utemeljene spremembe, pobudnik pa cilj in obseg uskladi s šolo uporabnico. Zapis ne spremeni statusov ali nosilcev D01–D16 v zgornji tabeli; njihovo morebitno spremembo je treba posebej obravnavati v ustreznem issueju.

## Usmeritev pobudnika 13. oktobra 2026

Pobudnik je predložil dopolnjeno predstavitev in nadaljnje korake ter izrecno naročil uskladitev GitHub. Navedel je uskladitev s Claude AI; to ne predstavlja institucionalne potrditve ali neodvisnega človeškega prevzema. [Izvor](izvor-gradiva.md#dopolnitev-13-oktobra-2026) vsebuje datoteki in kontrolni vsoti.

| Usmeritev | Status in povezane odločitve |
| --- | --- |
| Najprej predstavitev, mentorska ocena in odziv šole; nato dogovor o izvedbi in ločene dodatne vloge | Sprejeta usmeritev pobudnika. D02/D03/D09/D13/D14 ostajajo odprti; Mitjevi osebni sprejemi ostanejo, Aleksandarjeve naloge niso dodeljene. |
| Delovna raven: predstavitev, naročilo in kratka specifikacija; dolga priloga in AI pregledi kot neobvezen arhiv | Sprejeta usmeritev pobudnika. Kratka specifikacija je nov osnutek, ne formalni sprejem D12 ali izveden test. |
| CSV ostane osnovna pot; eAsistent le dodatna prihodnja možnost | Sprejeta razvojna usmeritev. Izvoz/API, preslikava in dejanske pravice niso potrjeni; D04/D06/D07/D12. |
| Ločena namestitev vsake šole; brez centralne večšolske storitve | Sprejeta razvojna usmeritev. Šola še potrdi konkretne skrbnike, vire, gostovanje in obnovo v D04/D09. |
| ArnesAAI in SI-PASS ob lokalnih računih, push, letni prehod in dodatni moduli pozneje | Poznejše razvojne smeri brez rokov, izvajalcev ali že delujočih povezav; niso obseg učnega B. |
| Računi učencev/dijakov in ciljna skupina M1 starši/učenci/oboje | Predlog za prvo mentorsko in šolsko oceno. Faza, starost/razred, kontakt, aktivacija, ločeni odzivi in vpogled v M2 še niso potrjeni; D01/D06/D07/D12/D13/D16. |
| Omilitev predkodnih pogojev za lokalne učne prototipe | V prilogi izrecno [P], ni sprejeta. Do posebne odločitve velja D03/D09/D14 tudi za lokalno prvo kodo. |

Opis »prve različice« v predstavitvi pomeni ciljni B, ne samodejne širitve T/A. Aktivacija/obnova ostaneta dopolnitev pred B; v T so računi pripravljeni vnaprej. Sedanji neodvisni človeški prevzem T pred A/I ostane; predlog avtorjevega pregleda z AI še ni potrjen.

Noben D01–D16 se s to posodobitvijo ne zapre. Potrebna pravna in podatkovna pravila za šolo niso potrjena z uredniško objavo.

## Osebni sprejemi pobudnika 12. novembra 2026

Pobudnik Mitja Pirih je v pogovoru z Claude AI, ki pripravlja P0 in navodila, sprejel naslednje. To so osebni sprejemi, ne institucionalna potrditev šol ali mentorjev. Povezani issuei (#12, #17, #18, #23) ostajajo odprti do ustrezne potrditve.

| Odločitev | Sprejeto | Kaj ostaja odprto |
| --- | --- | --- |
| D03 | Pobudnik je skupni tehnični nosilec in nosilec skupnih gradnikov. Osnova: Django 5.2 LTS, PostgreSQL, Docker Compose. Predlagana prijavna komponenta django-allauth še čaka na izrecno potrditev v pregledu pull requesta. | Potrditev sodelujočih zavodov (mentorji od 13. 11. 2026 kot izvajalci tehnologije ne potrjujejo) |
| D08 | Za programsko kodo velja EUPL 1.2; besedilo je v datoteki LICENSE. | Pravice prispevkov in izjave dijakov (dogovor z mentorjem), licenca dokumentacije (D15) |
| D09 | Pobudnik je edini vzdrževalec in skrbnik repozitorija. | Drugi skrbnik/namestnik ni imenovan (stanje 13. 11. 2026). |
| D14 | Pobudnik obravnava zasebne prijave ranljivosti. | Namestnik in roki odziva |

Neodvisni pregled P0/T (paket T) po kontrolnem seznamu opravi drug AI, mentor je rezerva (osebna odločitev pobudnika, 12. 11. 2026). To ni potrjeno kot enakovredno človeškemu prevzemu iz načrta; ugotovitve mora prebrati in sprejeti človek ([kontrolni seznam](pregled-P0-kontrolni-seznam.md)).

Pobudnik šteje pogoje D03, D08, D09 in D14 za zadostne za pripravo in lokalni razvoj osnove P0 na izmišljenih podatkih. Pogoj »drugi skrbnik« iz D09 ostaja nepopolno izpolnjen, zato velja pred vključitvijo zunanjih ekip (dijakov) še imenovanje namestnika (13. 11. 2026 nadomeščeno s priznanim tveganjem, glej [vloge skrbnikov](#vloge-skrbnikov-13-novembra-2026)). Neodvisni človeški prevzem T pred A/I ostane; zanj je predviden drug AI s pomočjo kontrolnega seznama, mentor je rezerva, vsakokratno odločitev o ustreznosti pa sprejme pobudnik.

Obseg zaslonov P0 za prvi prevzem T (osebni sprejem pobudnika, 12. 11. 2026, po prvem neodvisnem pregledu): prijava in odjava; uvoz CSV s predogledom in uveljavitvijo; seznam in podrobnosti oseb z odvzemom povezave ali upravičenja; popravek kontakta s sledjo. Celoten administrativni portal, izvoz in zasloni za starše zunaj M1/M2 niso v obsegu T. Točka 9 ostane odprta do izvedbe teh zaslonov in ročnega pregleda dostopnosti ([pregled dostopnosti](pregled-dostopnosti-P0.md)).

Odločitve pobudnika po prvem neodvisnem pregledu (osebni sprejem predlogov, ki jih je pripravil Claude, 12. 11. 2026; formalni sprejem poročil pregledovalcev ostaja odprt):

| Vprašanje | Odločitev |
| --- | --- |
| Prijavna komponenta `django-allauth` (D03) | Potrjena |
| Razvojna odvisnost `rfc3339-validator` (MIT) | Sprejeta |
| Predlogi pogodbe po pregledu (meje dolžin, splošne napake, podvojen prejemnik, ponovitev po izteku) | Sprejeti z D12 13. 11. 2026 in del pogodbe `1.0.0` |
| Ročni popravek kontakta in poznejši uvoz | Uvoz ostane vir resnice; predogled pokaže spremembo, tajništvo popravi tudi izvorni sistem |
| Samodejne posodobitve | Dependabot za GitHub Actions in slike; paketi Python ročno, mesečno ([postopek](odvisnosti-in-licence.md)) |
| HSTS in HTTPS | Ob odločitvi o gostovanju (D04) |
| SBOM in pravni pregled licenc | Pred prvo distribucijo slike šoli |
| Ročni pregled dostopnosti z bralnikom zaslona | Mentor ali učitelj z izkušnjo NVDA ali Orca; oseba še ni imenovana |
| Poročili prvega pregleda (PR #39, #40) | Obe se ohranita pod ločenima imenoma; v registru prispevkov ostaneta oba vpisa |
| Ponovni neodvisni pregled | Po združitvi popravkov, z istima pregledovalcema in posodobljenim navodilom |
| Točka 8 | Počaka na prava M1 in M2 |

Licenciranje prispevkov (D08, D15; osebni sprejem pobudnika 12. 11. 2026): koda pod EUPL 1.2, dokumentacija pod CC BY-SA 4.0; prispevek se licencira pod licenco dela projekta, v katerega spada (inbound = outbound). Vsak commit ima podpis DCO; ime je lahko vzdevek, identiteto mladoletnega pozna šola. Za združitev prispevka mladoletnega avtorja je potrebna enkratna izjava avtorja s soglasjem staršev, ki se pridobi ob prvem prispevku ali s šolsko prijavnico; praga »majhnih« prispevkov ni. Izjave hrani šola, v repozitoriju je le oznaka `avtor-urejen`. Ocena ne sme biti odvisna od soglasja. Obrazec mora pred uporabo pravno pregledati šola. Postopek: [CONTRIBUTING.md](../../CONTRIBUTING.md#licenciranje-prispevkov).

## Vloge naročnik in izvajalec (13. novembra 2026)

Pobudnik Mitja Pirih je kot pobudnik in skupni tehnični nosilec 13. 11. 2026 odločil, da projekt zaradi hitrosti odziva vseh vključenih vodi po razmerju naročnik–izvajalec:

| Vloga | Kdo | Kaj odloča oziroma dela |
| --- | --- | --- |
| Naročnik | Pobudnik (skupni tehnični nosilec) | Obseg naročila, arhitektura, tehnologija, pogodba vmesnikov in njene spremembe; sprejme ali zavrne predloge izvajalcev |
| Izvajalec | Mentorji s svojimi ekipami dijakov | Ocena izvedljivosti, razrez na individualne izdelke, vodenje in ocenjevanje dijakov, izvedba M1/M2 po pogodbi; spremembe predlagajo v issueju ali pull requestu |

Posledice:
- Tehnične odločitve, ki so čakale na potrditev mentorjev, sprejme naročnik. D12 je s tem sprejet (točke A in B, kot so predlagane) in pogodba zamrznjena kot `1.0.0`.
- Sprememba pogodbe z vplivom na ekipe gre prek pull requesta z odobritvijo naročnika; nezdružljiva sprememba zahteva novo različico ali dogovorjen prehod (C16). Vsaka zamrznjena različica je zapisana v [`api/zamrznitve.txt`](../../api/zamrznitve.txt), test pa pade, če se pogodba spremeni brez nove različice.

Ne spremeni se: odločitve in potrditve zavodov ter pilotne šole (D04–D07, D10, D11, D15, D16, sodelovanje), maturitetne teme in ocenjevanje (šola in mentor), razpoložljivost mentorjev in dijakov (D02, D13), neodvisni pregled T in pravni pregled obrazca D08. Pogoj namestnika iz D09/D14 je spremenjen v razdelku [vloge skrbnikov](#vloge-skrbnikov-13-novembra-2026).

## Vloge skrbnikov (13. novembra 2026)

Pobudnik je kot naročnik 13. 11. 2026 odločil:

- **Aleksandar** (`alexlandich`) ostane **mentor** (izvajalec z ekipami dijakov). Določitev za drugega skrbnika (D09) in namestnika obravnave zasebnih prijav (D14) z 12. 11. 2026 je umaknjena; vloge ni pisno sprejel. Na seznamu vzdrževalcev (`.github/vzdrzevalci.txt`) ni več; pravice na GitHubu se uskladijo z mentorsko vlogo (ne admin).
- **Edini vzdrževalec, skrbnik repozitorija in nosilec D14 je pobudnik.** Namestnik ni imenovan.
- **Sistemi AI niso vzdrževalci.** Ne morejo sprejeti vloge ali odgovornosti, ne delujejo brez človeka in nimajo lastnega dostopa. So orodja pod odgovornostjo pobudnika: Claude (Anthropic) izvaja, Codex (OpenAI) in DeepSeek neodvisno pregledujeta. Neodvisnost pregledov ostane le, dokler pregledovalca nista soodgovorna za kodo.

Posledica: pogoj »drugi skrbnik oziroma namestnik pred vključitvijo dijakov« (D09/D14) pobudnik nadomesti s **priznanim tveganjem enega skrbnika** za razvojno fazo na izmišljenih podatkih. Ob pobudnikovi odsotnosti zasebne prijave čakajo; roki D14 v tem času ne tečejo zanesljivo. Drugi človeški skrbnik in namestnik sta pogoj **pred produkcijskim pilotom** oziroma pred obdelavo resničnih osebnih podatkov. Pogoja D08 (soglasje za mladoletne avtorje) to ne spremeni.

## Roki in sledenje

D01–D03, D11–D14 in D16 blokirajo začetek odvisnega razvoja. D07, D09 in D10 se zaključijo pred produkcijskim pilotom; imenovanje drugega skrbnika iz D09 je izjema in je potrebno že pred prvo kodo oziroma vključitvijo zunanjih ekip. D04–D06 se rešijo pred razvojem odvisnih funkcij, D08 pred sprejemom kode in D15 pred potrditvijo pogojev ponovne uporabe besedil. Koledarske roke in GitHub dodelitve določijo potrjeni nosilci; vloge niso samodejno imenovanja oseb.

Odločitve se spremljajo v issueih #10–#25 (D01–D16). Dokaz izpolnitve posameznega merila in potrditev se zapišeta v ustrezni issue in register.

## Stanje sodelovanja

Po potrditvi pobudnika z dne 5. oktobra 2026 sta se OŠ Vojke Šmuc Izola in GEPŠ Piran odločili za sodelovanje v projektu. Pisna potrditev vodstev v repozitoriju ni evidentirana. Obseg pilota, odgovornosti, viri in pogoji uvedbe se še usklajujejo. Podatek je potrdil pobudnik Mitja Pirih. Datum prvotne odločitve in zapis dogovora tu nista določena. Ko bo pisna potrditev na voljo, se zabeležita datum in sklic na ustrezno gradivo; javna objava se omeji na podatke, primerne za objavo.

## Evidentirana dejstva

- 5. oktobra 2026 sta bila vzpostavljena javna organizacija GitHub in repozitorij.
- Specifikaciji M1 in M2 sta vključeni v main prek združenih PR #1 in #7; ostajata delovna osnutka za mentorjev pregled.
- Uporabnik je nastavil aktivno zaščito glavne veje z obveznim pull requestom, brez obveznih odobritev, z blokado brisanja in prisilnega prepisa.

- 5. oktobra 2026 je bila omogočena zasebna prijava ranljivosti; navodila so v SECURITY.md. Nosilec obravnave, namestnik in roki odziva ostajajo odprti v D14.
- Odprti so issuei #10–#25 za odločitve D01–D16.
- Omogočeno je samodejno brisanje vej po združitvi.

Ta dejstva ne pomenijo potrditve obsega ali produkcijske uvedbe.
