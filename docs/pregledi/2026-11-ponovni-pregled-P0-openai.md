# Ponovni neodvisni pregled P0 – paket T (OpenAI)

Pregledani commit: **`184c8f97191f5500e4308870f13fab7d19fee76f`**. Novejši `main` ni predmet tega pregleda.

## 1. Podatki

| Podatek | Vrednost |
| --- | --- |
| Datum | 12. november 2026, Europe/Ljubljana |
| Repozitorij | https://github.com/odprta-sola/solska-platforma |
| Izhodišče prvega pregleda | `e854f60c7f2e9918b09f0b7db0108c6ab8f62b8f` |
| Veja poročila | `pregled-p0-ponovni-openai`, iz pregledanega commita |
| Sistem in ponudnik | Codex, OpenAI; različice modela ne navajam |
| Odgovorni človek | Mitja Pirih; sprejem še ni potrjen |
| Gostitelj | Ubuntu 24.04.5 LTS, Linux 7.0.0-113042-tuxedo, x86_64 |
| Docker / Compose | 29.9.3 / v5.7.0 |
| Vsebnik | Python 3.12.16, Debian 13.7, Django 5.2.19, django-allauth 65.22.0, psycopg 3.3.9, gunicorn 27.0.0 |
| Zbirka in prestreznik pošte | PostgreSQL 16.15; Mailpit 1.33.1 |
| Razvojna orodja | pip 26.3, ruff 0.17.4, jsonschema 4.26.0 |
| Brskalniški pregled | Google Chrome 157.0.8103.38, Playwright, brez bralnika zaslona |

Pregledovane kode in popravkov ni napisal ta pregledovalec. Po navedbi pobudnika in projektni dokumentaciji jih je pripravil Claude (Anthropic). Starejša dokumentacija je nastajala tudi s pomočjo OpenAI. To je pregled z drugim sistemom AI, ne institucionalno neodvisen ali človeški prevzem; navedba avtorstva ni forenzična potrditev.

Prebrani so obe izvirni poročili, zapis o odpravi, vsi štirje objavljeni varnostni nasveti, kontrolni seznam, stanje T, kratka specifikacija, register odločitev z odločitvami 12. 11., pregled dostopnosti, odvisnosti in licence, DEVELOPER, SECURITY in OpenAPI. Pregledane so spremembe kode od prvega commita, nova koda, povezani modeli, avtorizacija, storitve, usmerjanje, predloge in testi.

Edina sprememba v veji je to poročilo. Koda, konfiguracija, testi in register prispevkov niso spremenjeni. Mutacije so bile izvedene v ločeni začasni kopiji. Uporabljeni so samo izmišljeni podatki; lastna testna gesla, ključi okolja in servisni žetoni so naključni in niso del poročila ali repozitorija. Obstoječih fiksnih gesel v projektnih testih nisem spreminjal.

## 2. Povzetek

**Priporočilo za prevzem T: ne.** Popravki prinašajo pomemben napredek in prvotne reprodukcije večinoma uspešno preprečijo. Neodvisno izvedena zbirka ima **173 testov, OK (skipped=2)**. Ponovitev 16 prvotnih preverjanj z upoštevanjem novih, izrecno zavrnjenih oziroma zaprtih poti je uspešna. Vseh šest izbranih mutacij povzroči padec novih regresijskih testov.

V dodatnih 13 preizkusih pa je **8 neuspešnih pričakovanj**, brez napak testnega ogrodja v končnem zagonu. Šest se nanaša na javne ugotovitve spodaj. **Novi varnostno občutljivi ugotovitvi: 2, od tega 1 visoka in 1 srednja; 0 kritičnih.** Podrobnosti so iz javnega poročila izključene in predane pobudniku v pogovoru. To ni zagotovilo, da drugih težav ni. Opozorila skenerja odvisnosti se ne prištevajo tema dvema ugotovitvama.

Pred ponovnim priporočilom so potrebni obravnava teh ugotovitev, odprava javnih neskladij vhoda, napak in uvoznega vmesnika ter ponovitev prizadetih testov. Točka 5 nima delujoče vezave dostave na kontakt, temveč varno začasno zaporo. Točka 9 ostaja delna, človek z bralnikom zaslona še ni izvedel pregleda. Točka 8 po odločitvi pobudnika čaka na prava M1/M2. D12 ostaja odprt. Individualna aktivacija/obnova, izvoz, SBOM in pravni pregled niso s tem poročilom prestavljeni iz dogovorjenih poznejših faz v T.

### Izvedba in ključni izpisi

Uporabljen je ločen projekt Compose `p0-repeat-openai`, lasten volumen in lokalna vrata 18009, 15439, 18029/11029. Izvirni Compose je dopolnjen samo z začasnim prekrivanjem vrat, naključnih skrivnosti in priklopom pregledovalčevih skriptov. Drugo že delujoče okolje na običajnih vratih ni bilo ustavljeno. Spodaj `dc` pomeni `docker compose -p p0-repeat-openai -f docker-compose.yml -f <začasni-override>`.

```text
dc up --build -d
  db Healthy; p0 Started; mail Started
seed_test_data [naključni SEED_PASSWORD v okolju]
  Testni nabor naložen.
dc exec -T p0 python manage.py test --verbosity 2
  Ran 173 tests in 15.845s
  OK (skipped=2)
dc build --no-cache p0
  Image p0-repeat-openai-p0 Built
ruff check .
  All checks passed!
ruff format --check .
  52 files already formatted
python manage.py makemigrations --check --dry-run
  No changes detected
python manage.py check
  System check identified no issues (0 silenced).
python -m pip check
  No broken requirements found.
python -m pip install --no-index --dry-run -r requirements-dev.txt -r requirements-build.txt
  Requirement already satisfied [brez Would install]
python3 scripts/check_docs_links.py
  Notranje povezave in sidra so veljavni.
```

Preskoka sta **dva podprimera istega testa** `ModuleBoundaryTests.test_moduli_ne_uvazajo_tujih_modelov`, ne dva dodatna uspešna testa:

```text
(module='m1') skipped 'Modul m1 še ne obstaja: meja ni preverjena.'
(module='m2') skipped 'Modul m2 še ne obstaja: meja ni preverjena.'
```

Prvi `seed_test_data` takoj po `down -v` in `up -d` je prehitel migracije:

```text
django.db.utils.ProgrammingError: relation "registry_sourcemapping" does not exist
subprocess.CalledProcessError: Command '['python', 'manage.py', 'seed_test_data']'
returned non-zero exit status 1.
```

To je dejanski neuspešni pripravljalni ukaz. Po preverjenem zaključku migracij z `manage.py migrate --noinput` je seed ponovljen. Rezultat testov po ponastavitvi je naveden v razdelku 6. `Started` ni pripravljenost aplikacije; ponovljiv postopek mora počakati na zaključene migracije oziroma uspešen health klic.

## 3. Tabela odprave prvega kroga

»Odpravljeno« pomeni odpravljeno v navedenem reprodukcijskem primeru. »Delno« vključuje preostalo funkcionalno vrzel, nepotrjeno odločitev ali dodatno dokazano neskladje. Poročil avtorjev nisem uporabil kot nadomestilo izvedbe.

### Objavljene varnostne ugotovitve

| ID | Prejšnja resnost | Novo stanje | Lastni dokaz |
| --- | --- | --- | --- |
| [S-01](https://github.com/odprta-sola/solska-platforma/security/advisories/GHSA-h7jp-rfj3-89xr) | visoka | odpravljeno z začasno zaporo; funkcionalnost do D12 manjka | `ContactBindingContract` in dodatna matrika: veljaven, tuj, neobstoječ in odvzet sklic ter nepravilni UUID pri veljavni obliki telesa vrnejo 503, isto vsebino razen `trace_id`, brez kontakta. Izvirni poskus s poljubnim `delivery_request_id` ne dobi kontakta. Neveljavna shema je 400, brez žetona 401, brez dovoljenja 403: navedba »503 za vse vhode« ni dobesedno pravilna. Branje vseh vej potrdi, da `delivery_binding_verified` vedno vrne False. |
| [S-02](https://github.com/odprta-sola/solska-platforma/security/advisories/GHSA-8h4f-w469-mr34) | visoka | delno; prvotna zaporedna reprodukcija odpravljena | Izvirna ponovitev in `ImportRestrictionTests` uspeta. Dodatno: odvzem povezave in odvzem granta × spremenjen začetek, samo vrsta, oboje; vseh šest serij zavrnjenih z `manual_restriction`. V vsaki kombinaciji preverjene vse štiri poti. Sklic ni izdan, občinstvo ga izloči, preverjanje dejanja zavrne, kontakt je 503; ob testno simulirani vezavi je kontakt 403. Celotnega varovala ne označujem za zaprtega; novi občutljivi izsledki so vključeni samo v skupno štetje v razdelku 2. |
| [S-03](https://github.com/odprta-sola/solska-platforma/security/advisories/GHSA-gfrq-669g-95fq) | visoka; omejitev pred B | odpravljeno z izklopom; individualna obnova ostaja pred B | `PasswordRecoveryTests`, izvirna ponovitev in dodatni preizkus z dejansko veljavnim ključem allauth: 8 poti pod `/accounts/password/reset/` × GET/POST/PUT/PATCH/DELETE/HEAD/OPTIONS vrne 404. Ključ je pred klicem potrjen z `UserTokenForm.is_valid()`. Geslo se ne spremeni, poštnih sporočil je 0. Regex zapira tudi poljubne podpoti. |
| [S-04](https://github.com/odprta-sola/solska-platforma/security/advisories/GHSA-42r3-qhw4-9xx2) | srednja | odpravljeno za zahtevane primere | `ImportRoleTests` ter dodatna matrika za `admin` in `office`: tajništvu nova dodelitev zavrnjena; skrbniku dovoljena; odvzem vloge admin med predogledom in uveljavitvijo povzroči `role_not_authorized`; tajništvo sme obstoječo vlogo znova uvoziti, tudi dejansko uveljaviti. |

Kontaktna zapora dokazuje odsotnost razkritja, ne delovanja dostave. Testi `ContactContract` namenoma simulirajo potrjeno vezavo; njihovi uspešni odgovori 200 niso odgovori trenutno odprtega javnega klica. Matrika enakosti primerja status in vsebino, ne dokazuje odsotnosti vseh časovnih kanalov.

### OpenAI

| ID | Prejšnja resnost | Novo stanje | Ponovitev in rezultat |
| --- | --- | --- | --- |
| P0-01 | srednja | delno | Izvirna dodatna lastnost `extra` je 400; manjkajoči `params` je 400. `RequestValidation` in `RequestSchemaParity` uspeta, sheme so strukturno enake OpenAPI. Neveljavni format časa pa še dobi 202 (R-01). |
| P0-02 | srednja | delno | Izvirni `subject_id="not-a-uuid"` zdaj vrne 200/`NOT_ALLOWED`, ne 500; neveljaven avtor 400. Izpad `check_scope` → 503 brez `allowed`; CSRF → 403 JSON; napačna metoda → 405 JSON z `Allow`; nepričakovana izjema → 500 brez tehničnega sporočila. Dodatna robna vhoda še kršita opis napak (R-02). |
| P0-03 | srednja | delno | Dve postavki iste osebe z različnima obsegoma: 400 `duplicate_recipient`, nič več tihega prepisovanja. `StubEdgeContract` uspe. Identiteta postavke in podpora več obsegom čakata D12. |
| P0-04 | opomba | delno | Isti JSON pri t in po izteku pri t+10 s: 202/202, isti ID. Nova že pretečena zahteva: 400. `StubEdgeContract.test_ponovitev_po_izteku_vrne_isti_prevzem_brez_podaljsanja` uspe. Okno hrambe ključa ostaja D12. |
| P0-05 | srednja | odpravljeno za prvotni primer; omejitve spodaj | Prvotni predogled `unchanged`, nato sprememba imena: uveljavitev zavrnjena s `preview_stale`, ročna vrednost ostane. Vseh 5 `PreviewApplyTests` in `ConcurrentApplyTests` uspe. Zaklep iste serije je dokazan; to ni dokaz serializacije vseh različnih posegov v evidenco. Nova uporabniška omejitev predogleda: R-04. |
| P0-06 | srednja | delno | Neveljaven datum/e-naslov in logično neskladje zdaj povzročijo napako validatorja; `CheckerSelfTest` uspe in mutacija formatov ga podre. Pri znanih operacijah preveri status, medij, shemo in `counts`. Za neznano pot tiho preskoči vse preverjanje (R-06); neposredni klici odjemalca ostajajo izven avtomatizma. |
| P0-07 | srednja | odpravljeno glede napačnih imen in navedenih testov | Preimenovana testa preverjata tuji preklic in ročno nastavljen iztek. `ValidityTests.test_povezava_sama_ne_podeli_pravice` zdaj kliče avtorizacijo in uspe. Manjkajoča modula sta izrecna preskoka. Točka 8 s tem ni pokrita. |
| P0-08 | srednja | ni odpravljeno | Ponovno prebrani `stubs/state.py`, `m1.py`, `m2.py`: stanje je procesno, ni trajne dostave, urnika ali klica P0 ob pošiljanju. Funkcionalno to ostaja nadomestek, omejitve so zdaj jasneje opisane. Pravi moduli po odločitvi pobudnika pridejo pozneje. |
| P0-09 | nizka | delno | Zastarelih 82/85 ni več kot trenutnega rezultata; 173 izmerjeno. SECURITY in specifikacija zdaj priznavata referenčno kodo. Ostajajo protislovja o že sprejetih odločitvah, gradnji in obsegu zaslonov (R-07). |
| P0-10 | srednja | delno | Prijava ima `lang="sl"`, strukturo in povezane napake; osnovni zasloni obstajajo. Osem testov dostopnosti in 25 testov zaslonov uspe. Chrome potrdi tipkovnico, fokus, napake, uvoz in odvzem; pri 320 px se podrobnosti prelivajo (R-05). Bralnik zaslona: ni izvedeno, potreben človek. |
| P0-11 | nizka | delno | Obe različici slike zgrajeni brez predpomnilnika, hashi uveljavljeni, slike in Actions pripeti; negativen preizkus napačnega hasha zavrnjen. Tri ponovitve pip-audit brez zadetkov in Trivy produkcijske slike se ujemajo z zapisom. SBOM, binarne knjižnice in pravna presoja distribucije ostajajo odprti v dogovorjeni fazi. |

### DeepSeek

| ID | Prejšnja resnost | Novo stanje | Ponovitev in rezultat |
| --- | --- | --- | --- |
| P0-01 | srednja | odpravljeno za prvotni UUID; širša obravnava napak delna | `audiences/resolve` z `author_id="not-a-uuid"` vrne 400; preverjanje pravice z neveljavnim subjectom 200/`NOT_ALLOWED`; kontakt z neveljavnim recipientom 503 zaradi zapore. `ApiErrorContract`, dodatna matrika S-01 in izvirna ponovitev. Glej tudi R-02. |
| P0-02 | opomba | delno | Pot do kontakta je zaprta. `_resolve_contact` še preverja katerokoli od `acknowledge`/`decide`; namensko dovoljenje dostave in identiteta obsega nista določena. Branje `api.py`, `ContactBindingContract` in `ContactContract`; pred ponovno odprtjem potreben D12. |
| P0-03 | srednja, že dokumentirano | odpravljeno z izklopom | Isti dokazi kot S-03, vključno z veljavnim ključem allauth in nespremenjenim geslom. Individualna aktivacija/obnova ni implementirana in ostaja pred B. |
| P0-04 | opomba | odpravljeno | `test_preklic_tuje_zahteve_je_404` in `test_rocno_nastavljen_iztek_je_koncno_stanje` pravilno poimenujeta dejansko preverjanje; uspešna v celotni zbirki. Izpad pravih modulov ni izveden. |
| P0-05 | nizka | ni odpravljeno; namerno odloženo | Branje nastavitev: HSTS in SSL redirect še nista določena, varni piškotki so vezani na `DEBUG`. Pobudnik ju je izrecno prestavil na dejansko namestitev D04. Produkcijski preizkus HTTPS ni izveden, ker namestitev ni določena; to ni nova blokada lokalnega T. |
| P0-06 | nizka | odpravljeno | Izvedba potrdi 173 in dva preskoka, trenutni kontrolni seznam napoti na rezultat za konkretni commit. Druge dokumentacijske nedoslednosti so R-07. |

## 4. Nove javne ugotovitve

Novi varnostno občutljivi ugotovitvi sta javno navedeni **samo s številom in resnostjo v razdelku 2**. Spodaj so funkcionalne, pogodbene in dokumentacijske ugotovitve. Lokacije se nanašajo na pregledani commit.

| ID | Resnost | Kje | Opis, reprodukcija, predlog |
| --- | --- | --- | --- |
| R-01 | srednja | `p0/stubs/m1.py:25`, `p0/registry/contract_schemas.py:127` | Validator zahteve odloži preverjanje formata klicatelju, `_expires` pa sprejme širši Python ISO zapis. Veljaven `DeliveryRequest` z `expires_at="2099-01-01X00:00:00+00:00"` validator OpenAPI zavrne, endpoint pa vrne 202. Ponovitev: ista zahteva kot `delivery_body`, zamenjan samo datum. Predlog: format preveriti skladno s pogodbo in dodati negativne primere ločila, osnovnega datuma in časovnega pasu. Strukturna enakost slovarjev ni enakost vedenja validatorjev. |
| R-02 | srednja | `p0/core/middleware.py:17`, `:38`; `p0/registry/api.py:198` | Pretvorba napak ni celovita. Preveliko telo, ki sproži `RequestDataTooBig`, dobi 400 HTML, ker se `SuspiciousOperation` prepusti Django in se pretvarjata samo 404/405. Preizkus z znižano mejo `DATA_UPLOAD_MAX_MEMORY_SIZE=100` in 200-znakovnim sklicem: `400 text/html; charset=utf-8`. Ločeno: servisni audience klic z veljavnim avtorjem, `class_id="²"`, `purpose="notice"` vrne 500 JSON (`isdigit()` je True, `int()` pa dvigne ValueError). Predlog: dosledni varni odgovori tudi za te napake in preverjanje oblike pred pretvorbo. Izpad v prvotni reprodukciji se pravilno vrne kot 503, ne kot dovoljenje ali poslovna zavrnitev. |
| R-03 | srednja | `p0/registry/importer.py:164`; `p0/registry/ui.py:217` | Nekateri neveljavni CSV ne vrnejo uporabne napake predogleda, temveč HTTP 500. Kot office naložite `persons.csv` z glavo `source_person_key;display_name`, vrstico `x;` in 131073 znaki `x` v drugem polju. Datoteka je pod 5 MiB, `csv.DictReader` pa sproži `_csv.Error: field larger than field limit (131072)`, ki ni prestrežen. Predlog: omejitve in izjeme parserja pretvoriti v zavrnjen predogled oziroma napako obrazca; preveriti tudi dolžine modelskih polj pred pisanjem. Običajni napačen UTF-8 in prekoračitev 5 MiB sta pravilno zavrnjena. |
| R-04 | srednja | `p0/registry/ui.py:237`; `p0/templates/evidenca/serija.html:32` | Predogled izriše le prvih 500 postavk, nima naslednje strani ali druge poti do preostanka, uveljavi pa celotno serijo. Za `persons.csv` s 501 osebami `person-0000` … `person-0500` je zadnja oseba odsotna iz predogleda, gumb za uveljavitev ostane. Napis opozori na prvih 500, vendar uporabnik preostalih sprememb ne more pregledati. Predlog: omogočiti pregled vseh postavk, npr. strani in filtriranje sprememb, ali preprečiti potrditev nepopolno predstavljene serije. To je pregled načrta, ne zahteva za izvoz pred B. |
| R-05 | nizka | `p0/templates/base.html:40`; `p0/templates/evidenca/oseba.html:9` | Pri širini 320 CSS px stran osebe s testnim naslovom `family01@example.invalid` dobi `scrollWidth=325`, desni rob opisa je 325,17 px. Vzrok je mreža `max-content 1fr` brez zmanjšanja/preloma vsebine drugega stolpca. Ponovitev v Chromu: office → osebe → Starš Testni 01 ali 02, širina 320. Predlog: omogočiti krčenje in prelom e-naslova oziroma na ozki širini zložiti opis. Drsenje širokih tabel v njihovih lastnih regijah deluje in ni vzrok te napake. |
| R-06 | nizka | `p0/registry/tests/contract_check.py:48` | Za neznano pot `check_response` tiho vrne, tudi pri očitno neveljavnem odgovoru. `check_response('post', '/p0/api/v1/typo', 200, 'text/html', b'not JSON')` ne dvigne ničesar. Zato splošna trditev »vsak odgovor skozi ContractBase.call je preverjen« ni pravilna. Predlog: zahtevati prepoznano operacijo, izjeme za dokumentirane pomožne poti `/_stub/` pa dovoliti izrecno; dodati samopreizkus. Izmerjena vrzel ne pomeni, da vsi obstoječi testi uporabljajo napačne poti. |
| R-07 | nizka | `DEVELOPER.md`; `docs/projekt/stanje-prevzema-T.md`; `docs/pregledi/2026-11-odprava-prvega-pregleda-P0.md` | Dokumenti še niso usklajeni. DEVELOPER in stanje T pravita, da razmerje ročnega kontakta do uvoza ni določeno, register pa določa uvoz kot vir resnice. Stanje T še čaka na potrditev allauth, ki je v zadnji tabeli odločitev potrjena; hkrati pravi, da gradnja brez predpomnilnika ni preverjena, zapis o odpravi pa jo navaja kot izvedeno. Seznam oseb/uvoz/popravki so še med manjkajočimi pred B, čeprav so že dogovorjeni in izvedeni za T. Tabela P0-11 v odpravi še čaka na vklop samodejnih posodobitev, `.github/dependabot.yml` pa obstaja. Predlog: časovno uskladiti konkretne trditve in ločiti zgodovinsko stanje od trenutnega. |
| R-08 | nizka | `p0/registry/ui.py:268–285` | Zavrženje že uveljavljene serije lažno poroča uspeh: `import_discard` spremeni status samo za `previewed`, vedno pa izpiše »Predogled je zavržen; nič ni bilo spremenjeno.« Ponovitev: odprite isti predogled v dveh zavihkih, v prvem uveljavite, v drugem zavrzite. Izmerjeno: status ostane `applied`, uvožene osebe obstajajo, prikazano je navedeno sporočilo. Predlog: ob drugem statusu prikazati dejansko stanje in pojasniti, da zavrženje ni bilo izvedeno. |

Dodatno preverjeno pri novi kodi:

- Vsi zasloni evidence zahtevajo vlogo office/admin, starš in učitelj sta zavrnjena. Pri ugibanju ID povezave in granta druge osebe je 404 brez spremembe; dostop do uvozne serije in dejanj je za starša/učitelja 403. Tajništvo ima po trenutnem modelu dostop do celotne šolske evidence, ne samo svojih serij; tega nisem napačno označil za obhod lastništva.
- Vseh šest spreminjajočih poti (kontakt, povezava, grant, predogled, uveljavitev, zavrženje) je z `enforce_csrf_checks=True` brez žetona CSRF zavrnjenih s 403. GET ne uveljavi serije. Neveljaven Bearer ob seji ostane 401, veljaven servisni žeton uporablja servisno vejo.
- Predloge uporabljajo običajno ubežanje Django; v izvedenem preizkusu imena `<script>…</script>` se oznake izpišejo ubežano. V pregledanih predlogah ni izklopa ubežanja ali vstavljanja CSV v izvršljivo skripto. To ni izčrpen dokaz za vse možne XSS vhode.
- Datoteke se berejo kot bajti, ime določa tabelo prek `Path(...).stem`; uporabniško ime datoteke ni cilj zapisovanja v datotečni sistem. Preverjeni so dvojnik imena, neznana tabela, vsebina, UTF-8 in meja 5 MiB. Neveljavna končnica z veljavnim imenom tabele sama ni varnostna meja; vsebino mora preveriti parser. Celovito obremenitveno preverjanje ni izvedeno.
- Ročni kontakt in odvzemi imajo sled z akterjem, virom `zaslon` ter imeni spremenjenih polj. Uspešno je preverjeno tudi brisanje datotek po običajni uveljavitvi in zavrženju. Varnostno občutljivi rezultati dodatnih preverjanj niso del javnega opisa.
- `apply_batch` ponovno preveri pooblastilo, hash in načrt ter zaklene isto serijo v transakciji. Mutacije in dva dejanska sočasna klica potrdita navedene lokalne lastnosti. Splošne varnosti vseh sočasnih operacij iz tega ni mogoče sklepati.

### Dejanski neuspešni izpisi dodatnih preizkusov

Skrajšani so samo ponovljene sledi in vsebina HTML. Podrobnosti dveh varnostno občutljivih primerov so izključene.

```text
RFC3339 invalid separator: schema rejects, endpoint HTTP 202
AssertionError: 202 != 400
Oversized JSON: 400 text/html; charset=utf-8
AssertionError: False is not true
Unicode digit class_id: 500
AssertionError: 500 not found in (400, 403)
CSV field > parser limit but < file limit: HTTP 500
AssertionError: 500 not less than 500
Preview items= 501 last visible= False
AssertionError: False is not true : 501st item missing; no paging control
check_response(unknown path)
AssertionError: ContractViolation not raised
Ran 13 tests in 3.382s
FAILED (failures=8)  [6 javnih neuspelih pričakovanj; 2 občutljivi]

Ločen poznejši preizkus sporočila:
DISCARD_AFTER_APPLY: batch= applied data_exists= True claims_unchanged= True
AssertionError: True is not false
Ran 1 test
FAILED (failures=1)
```

## 5. Preizkus regresijskih testov z odstranitvijo popravkov

Uporabljena je kopija `p0`, `api` in `data` zunaj repozitorija. Vsaka sprememba je narejena samostojno, po zagonu izbranih projektnih testov je izvirna datoteka obnovljena. Celotna zbirka na izvirnem commitu je pred tem uspešna. Spodnje mutacije niso popravki aplikacije in niso vključene v vejo.

Ukaz za vsako vrstico: `python manage.py test <navedeni-test> --verbosity 2` v začasni kopiji, z enakim PostgreSQL in paketnim okoljem.

| Mutacija | Test | Dejanski rezultat |
| --- | --- | --- |
| V `_valid` pogoj za prepoved dodatnih lastnosti zamenjan z `if False:` | `registry.tests.test_robni.RequestValidation.test_dodatno_polje` | `Ran 1 test; FAILED (failures=6)`. Vseh šest shem zazna napako; npr. `AssertionError: 200 != 400`, pri dostavi `202 != 400`. |
| Odgovor `DatabaseError` v middleware zamenjan iz 503 v 500 | `registry.tests.test_robni.ApiErrorContract.test_nedosegljiva_evidenca_je_503_ne_zavrnitev` | `Ran 1 test; FAILED (failures=1)`; `ContractViolation: POST /p0/api/v1/authorizations/check 500: status ni v pogodbi`. |
| V `upsert_validity` `revoked_at = _manual_revocation_at(...)` zamenjan z `revoked_at = None` | `registry.tests.test_varovala.ImportRestrictionTests` | `Ran 9 tests; FAILED (failures=5)`. Prestavljen začetek, oboje, druga vrsta, odvzem dovoljenja in preverjanje štirih poti zaznajo odstranitev. Primer: `'manual_restriction' not found in set()`. |
| V `staff_required` preverjanje `if not is_staff(request.user)` zamenjano z `if False:` | `registry.tests.test_zasloni.AccessTests.test_stars_in_ucitelj_nimata_dostopa` | `Ran 1 test; FAILED (failures=1)`; `200 != 403` za starša na seznamu oseb. |
| V osnovni predlogi odstranjen atribut `lang` | `registry.tests.test_dostopnost.LoginAccessibilityTests.test_jezik_naslov_in_struktura` | `Ran 1 test; FAILED (failures=1)`; `None != 'sl'`. |
| V `contract_check.validate` `format_checker=FORMATS` zamenjan z `None` | `registry.tests.test_robni.CheckerSelfTest.test_pokvarjeni_odgovori` | `Ran 1 test; FAILED (failures=1)`; `ContractViolation not raised`. |

**Vseh šest mutacij je zaznanih.** To potrjuje koristnost izbranih regresijskih testov, ne njihove popolnosti. Preostale vrzeli kažejo dodatni preizkusi iz razdelka 4. Test neznane poti je konkreten primer tihega preskoka preverjanja.

Pri pregledu S-03 je bila preverjena še kakovost dokazila s ključem: projektni test uporablja Django `default_token_generator`, allauth pa svojega; ključ prvega v izvedenem okolju ni veljaven za allauth. Zato sem dodal neodvisen preizkus z allauth generatorjem in predhodno pozitivno validacijo ključa. Tudi ta je uspešen. To ni dokaz obhoda zapore, temveč omejitev prvotnega dokazila o »prej izdanem ključu«.

## 6. Devet točk in dvajset skupin

### Devet točk kontrolnega seznama

Oznaka pokritosti pomeni obseg dokaza za merilo, ne človeškega sprejema. Kjer je izveden le del, je to izrecno navedeno.

| # | Merilo | Ocena | Izvedba, rezultat in razlika do zapisa o odpravi |
| --- | --- | --- | --- |
| 1 | Lastni otroci in druga družina | pokrit | Izvedeno: pogodbena zbirka, izvirna ponovitev tujega/neobstoječega sklica in dejanske HTTP prijave v Chromu. `parent-03` vidi samo otroka 03, tuj in ugiban sklic sta `NOT_ALLOWED`. Odprava ni izvedla ročne ponovitve po popravkih; tukaj je opravljena avtomatizirana brskalniška ponovitev. |
| 2 | Skupen kontakt, ločena računa | pokrit | Izvedeno: ločeni HTTP prijavi `parent-01`/`parent-02` in različna person_id, modelni/uvozni testi, neodvisna ponovitev. Po brskalniškem odvzemu otrok 01 ni več pri parent-01, pri parent-02 ostane. Brez razlike v vsebinski oceni. |
| 3 | Odvzem povezave/granta | delno | Neposredni odvzem in šest zaporednih uvoznih kombinacij preverjenih v vseh štirih poteh; običajni scenariji uspejo. Splošnega merila zaradi dodatnih občutljivih izsledkov ne označujem za pokritega. To je strožja ocena od splošne navedbe »avtomatski dokaz obstaja«. |
| 4 | CSV, celovitost, ponovitev, sled | delno | Izvedenih vseh 22 izvirnih uvoznih testov, testi predogleda in iste sočasne serije ter brskalniški predogled/uveljavitev. Osnovna atomskost in ponovitev uspeta; R-03/R-04/R-08 omejujejo uporabnost in resničnost potrditve. Dopolnjeni testi iz odprave niso dokaz celotnega merila. |
| 5 | Omejen kontakt za evidentirano zahtevo | delno | Zapora in zavrnitve preverjene; uporabna razrešitev kontakta za evidentirano dostavo ne obstaja. Enako kot odprava: ni izpolnjeno, čaka D12. |
| 6 | Neodvisen pregled kode | pokrit kot pregled z AI | Ta ponovni pregled je izveden, kar posodablja navedbo »ponovni pregled ni izveden«. Človek poročila še ni sprejel; ni izenačeno s človeškim prevzemom. |
| 7 | Pogodbeni testi po ponastavitvi | pokrit v okviru nadomestkov | Izvedeno: `down -v`, `up -d` z brezpredpomnilniško zgrajeno sliko, zaključene migracije, nov naključni seed, `test_contract test_robni test_zasloni`: **98 testov, OK, 7.024 s**. Ujema se s številom v odpravi. Prvi prezgodnji seed je naveden v razdelku 2. |
| 8 | Izpad pravih modulov in varno zadržanje | ni v obsegu trenutne izvedbe T po odločitvi pobudnika; merilo ostaja neizpolnjeno | Ni izvedeno: prava M1/M2 ne obstajata. Odločitev 12. 11. izrecno pravi, naj počaka. Test sintetičnega `OperationalError` v P0 ni dokaz vedenja modulov. Brez nove vsebinske razlike do odprave. |
| 9 | Dostopnost osnovnih opravil | delno | Izvedeni struktura, oznake, fokus, napake, tipkovnica in širina 320 px, tudi uvoz datotek ter uveljavitev. R-05 je nova ugotovitev. Bralnik zaslona ni izveden, potreben človek; zaključna ocena ostaja neizpolnjeno. |

Izpis ponovitve po ponastavitvi:

```text
python manage.py test registry.tests.test_contract registry.tests.test_robni registry.tests.test_zasloni --verbosity 2
Ran 98 tests in 7.024s
OK
```

Po vseh preizkusih je izolirano okolje ponovno ustavljeno z `dc down -v`. V njem ni ostala zbirka s testnimi gesli. Drugi uporabnikovi vsebniki niso bili odstranjeni.

### Dostopnost brez bralnika zaslona

V Chromu pri 320 × 800 CSS px imajo prijava, začetek, seznam oseb, kontakt, odvzem, uvoz, predogled, uveljavljena serija in odjava `lang=sl`, en h1 in eno main regijo; pregledana polja imajo oznake in sklici `aria-describedby` imajo cilje. Izjema glede širine je podrobnost osebe (R-05); ostale navedene strani imajo `scrollWidth=320`.

Tab na prijavi preide preskok, povezavo Prijava, uporabniško ime, geslo, zapomni si me in gumb. Izmerjena obroba fokusa je 3 px. Oddaja prazne prijave z Enter prestavi fokus na `napake`; Enter na povezavi napake ga prestavi v `id_login`. Napačen kontakt, manjkajoča datoteka in napačna glava CSV imajo fokus na povzetku napak. Tabelo je mogoče fokusirati in pomakniti s puščico; izmerjeno `scrollLeft: 0 → 40`.

Prijava, oddaja obrazcev, potrjeni odvzem in uveljavitev uvoza so izvedeni v pravem brskalniku. Nekateri prehodi so avtomatizirani s kliki in izbira datotek s Playwrightom; to ni trditev, da je bil celoten scenarij izveden izključno s tipkovnico. Napake pripravljalnega skripta (natančni izbirnik oznake gesla) so bile popravljene samo v pregledovalčevem skriptu; opisani končni prehodi so uspešni.

**Ni izvedeno:** človeški pregled z NVDA/Orca, preverjanje z uporabniki, visok kontrast, glasovno upravljanje, povečava 200/400 % in meritev kontrasta. Potreben je imenovan človek; avtomatski dokaz jih ne nadomesti.

### Dvajset skupin kratke specifikacije

Primerjava ohranja razmejitev prvega poročila OpenAI, na katero se sklicuje zapis o odpravi. »Pokrit« ni dokaz poslovne izvedbe M1/M2.

| # | Skupina | Ocena | Dokaz / omejitev / razlika |
| --- | --- | --- | --- |
| 1 | Dva računa z istim kontaktom | delno | Ločena prijava, identiteta in pravice dokazani; individualni postopek in odzivi pravega M2 ne. Enako odpravi. |
| 2 | Druga družina, ugiban ID, tuj sklic | delno | API in novi zasloni preverjeni na navedenih primerih; celote vseh podatkovnih poti ni mogoče potrditi. Enako odpravi. |
| 3 | Zaposleni zunaj oddelka | delno | Audience zavrnitev preizkušena, poslovna objava M1 ne obstaja. Enako odpravi. |
| 4 | Račun učenca in ciljna skupina | ni v obsegu T | Pogojena poznejša razširitev, ne dodana zahteva tega pregleda. |
| 5 | Odnos brez granta in neposredni odvzem | pokrit | Modelni test zdaj preveri dejansko zavrnitev; neposredni odvzem povezave in granta preverjen v vseh štirih poteh. Enako popravljeni oceni odprave; poznejši uvoz je skupina 6. |
| 6 | Starejši uvoz po ročni omejitvi | delno | Prvotne in razširjene zaporedne reprodukcije zavrnjene; celotnega merila ne potrdim. Razlika do »pokrit« v odpravi zaradi dodatnih občutljivih izsledkov, ki javno ostanejo samo prešteti. |
| 7 | Napačen CSV, neznana referenca | delno | Atomska zavrnitev običajnih napak uspe; dodatni CSV povzroči 500 namesto razložene zavrnitve (R-03). Razlika do »pokrit« v odpravi. |
| 8 | Ponovni uvoz, dvojnik, manjkajoča vrstica | pokrit | `IdempotencyTests`, `ValidationTests`, CLI test in ponovitev v celotni zbirki uspejo. Enako odpravi. |
| 9 | Aktivacija/obnova pri skupnem predalu | ni v obsegu T | Pred B; trenutna zapora preverjena, individualni postopek ne obstaja. |
| 10 | Odjava, CSRF, podtaknjen uporabnik, servis | delno | Seje, žetoni in CSRF preverjeni tudi na novih poteh; delegiranje avtorja in celota napak ostajata nedokončana. Enako odpravi. |
| 11 | Odprtje in izrecna seznanitev M1 | ni v obsegu T | Pravi M1. |
| 12 | Dva otroka in različice M1 | ni v obsegu T | Poslovni del M1; podporna dostavna zavrnitev je posebej P0-03. |
| 13 | Več namenov, Ne/brez odziva | ni v obsegu T | Pravi M2. |
| 14 | Dva otroka, dva odločevalca | ni v obsegu T | Pravi M2. |
| 15 | Pregled in sprememba različice M2 | ni v obsegu T | Pravi M2. |
| 16 | Preklic in zgodovina obrazca | ni v obsegu T | Dostavni preklic nadomestka ni preklic izjave. |
| 17 | Izpad M1, izgubljen 202, ključi/dogodek | delno | Idempotenca, konflikt in ponovitev po izteku preizkušeni; trajnost, izgubljen odgovor in obnova ne. Enako odpravi. |
| 18 | Potreba, selektivni preklic, izpadi, urnik, iztek | delno | Izidi stanj in preklic preizkušeni; pravi izpadi, tihi čas in samodejni iztek niso. Enako odpravi. |
| 19 | Negotov SMTP, odvzem med dostavo, obnova | nepokrit | Nadomestka ne pošiljata in ne obnavljata. Ohranitev prejšnje ocene, ne zahteva za nedogovorjeno produkcijsko funkcijo v P0. |
| 20 | Sveža namestitev, nadomestki, izvoz, dostopnost | delno | Tokrat gradnja brez predpomnilnika in ponastavitev izvedeni; uvoz tudi v brskalniku. Bralnik manjka, 320 px ima napako. Izvoz ostaja pred B. Ocena enaka, dokaz širši. |

Skupaj: **2 pokriti, 9 delno, 1 nepokrita, 8 zunaj obsega T**. Odprava navaja 4/7/1/8; razliki sta skupini 6 in 7. Preložitev točke 8 ne dokazuje njenega uspeha in ne spremeni nadomestkov v prave module.

## 7. Odvisnosti, gradnja in CI

Izvedeni sta `dc build --no-cache p0` z `INSTALL_DEV=1` in ločena `docker build --no-cache --build-arg INSTALL_DEV=0 -t p0-repeat-openai-production:184c8f9 p0`. Produkcijska slika ima ID `sha256:b36dea7540359c9bcfcfdd4a6ee2f3db85b434fa68cf8781054dc3a913ef938d`. To je identiteta te gradnje, ne obljuba bitno enake prihodnje gradnje.

Dockerfile in CI dejansko uporabljata `--require-hashes`, razvojni in produkcijski zaklep tudi `--no-deps` in `pip check`. V ločenem negativnem preizkusu z `asgiref==3.13.0` in namerno napačnim hashom je `pip download --require-hashes --no-deps --no-cache-dir` končal s kodo 1:

```text
ERROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE.
Expected sha256 0000...0000
Got             f9596a2434512686473d50f96ff6207fbba49ae1a785dfac614df4aeb085674d
```

Zahtevani paketi in vhodni razponi se v preverjenem okolju ujemajo. Slike Python/PostgreSQL/Mailpit imajo digeste; checkout/setup-python imata polna SHA, Python v CI točno različico. Dependabot je nastavljen mesečno za Actions, Docker in Compose. Prisotnost konfiguracije ni dokaz, da je že uspešno odprl posodobitveni PR. Sistemska namestitev še uporablja živi repozitorij Debian z določeno različico zlib, zato nedostopnost te različice v prihodnosti lahko ustavi gradnjo; to ni vsebinska sprememba zahtev tega pregleda.

CI preveri namestitev zaklepov, skladnost vhodnih zahtev, ruff, oblikovanje, migracije, Django check in teste. **Ne izvaja** gradnje Docker, pip-audit, Trivy, brskalniške dostopnosti ali preskusa pravih M1/M2 ob izpadu. Dokumentirani ročni postopek skeniranja zato ostaja ločen od uspeha CI.

`pip-audit` 2.10.1 je izveden iz ločenega okolja, za vsak zaklep posebej:

```text
pip-audit --disable-pip --no-deps -r p0/requirements.lock --format json
pip-audit --disable-pip --no-deps -r p0/requirements-dev.lock --format json
pip-audit --disable-pip --no-deps -r p0/requirements-build.lock --format json
```

| Cilj | Lastni rezultat | Primerjava z dokumentom |
| --- | --- | --- |
| `requirements.lock` | 8 paketov, 0 znanih ranljivosti | ujema se |
| `requirements-dev.lock` | 17 paketov, 0 znanih ranljivosti | ujema se |
| `requirements-build.lock` | 1 paket, 0 znanih ranljivosti | ujema se |
| Produkcijska slika P0, Python | 0 opozoril Trivy | ujema se |
| Produkcijska slika P0, Debian | 205 zapisov: 47 HIGH, 74 MEDIUM, 65 LOW, 19 UNKNOWN, 0 CRITICAL; 0 z `FixedVersion` | ujema se |

Pip-audit izpiše običajno opozorilo o `--no-deps`; preverjeni so vsi paketi v zaklepih, odvisnosti ne razrešuje na novo. Trivy 0.76.2 je uporabljen iz slike `aquasec/trivy@sha256:8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb`, nad `docker save` arhivom produkcijske slike, s `--scanners vuln --format json`. Podatkovna zbirka ima `UpdatedAt=2026-11-12T12:59:19Z`.

**Ni izvedeno:** ponovna skeniranja slik PostgreSQL in Mailpit, razvojne slike in prvotne osnovne slike kot samostojnih ciljev; cilj ponovitve Trivy je bila produkcijska P0 slika. Zato njihovih števil iz dokumenta ne predstavljam kot lastno meritev. Prav tako niso izvedeni inventar vgrajenih knjižnic `psycopg-binary`, SBOM celotne distribucije in pravna presoja licenc. Paketni popis sem primerjal z nameščenimi različicami in zaklepi; ne potrjujem pravne skladnosti distribucije. Odsotnost znanih zadetkov ali popravka ni dokaz odsotnosti ranljivosti oziroma neizkoristljivosti.

## 8. Omejitve pregleda

- Pregled velja samo za navedeni SHA. Novejši commiti na `main` niso bili vključeni; obstoječa uporabnikova veja prvega pregleda ni bila spremenjena.
- Ni produkcijskih podatkov, resnične šole ali zunanje e-poštne dostave. Vsi dodatni posegi so omejeni na lastno lokalno testno okolje.
- Pogodbeni testi uporabljajo Django testni proces in nadomestka. Ne dokazujejo porazdeljenih odpovedi, SMTP predaje, trajnosti, obnove ali enakega vedenja bodočih modulov.
- Dodatni primeri so izbrani, ne izčrpno preverjanje vseh kombinacij, časovnih kanalov ali obremenitev. Test dveh transakcij iste serije ima omejen obseg. Šest zaznanih mutacij ni splošna ocena kakovosti celotne zbirke.
- Pregled brskalnika je avtomatiziran s strani AI. Človeški pregled z bralnikom zaslona in razumevanje besedil z uporabniki nista izvedena.
- Namestitev in povezave do Docker/GitHub so zahtevale izvajanje zunaj omejenega omrežnega okolja. Začetni omejeni `git fetch` ni razrešil gostitelja, omejeni Docker ni dostopal do vtičnice; po dovoljenem dostopu sta uspela. Varnostne nasvete sem po neuspehu spletnega pregledovalnika prebral prek javnega GitHub API; vsi štirje so objavljeni.
- Prvi seed po ponastavitvi je padel zaradi nedokončanih migracij; ta neuspeh ni zamolčan. Diagnostični poskus neposrednega uvoza allauth brez `django.setup()` je prav tako padel z `ImproperlyConfigured`; končni neodvisni preizkus teče v pravilno inicializiranem Django okolju.
- Dodatni skripti in dnevniki niso dodani v javno vejo, ker dovoljuje le poročilo in nekateri vsebujejo občutljive ugotovitve. Javne reprodukcije in natančne mutacije so opisane zgoraj; zasebne podrobnosti prejme pobudnik v pogovoru. Gesla in žetoni niso vključeni.
- Pravne, organizacijske in institucionalne potrditve niso nadomeščene s tehničnim pregledom. D09/D14, D12 in sprejem poročila ostajajo pri določenih ljudeh; pregled ne določa novih nosilcev.

## 9. Izjava

Ta pregled **ni človeški prevzem, ni pravno mnenje in ni potrditev D12**. Ne zapira paketa T in ne potrjuje produkcijske pripravljenosti. Odločitev o sprejemu sprejme odgovorni človek po branju poročila in zasebnih ugotovitev.
