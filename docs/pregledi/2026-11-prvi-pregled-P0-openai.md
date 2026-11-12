# Prvi neodvisni pregled P0 – paket T

Pregledani commit: `e854f60c7f2e9918b09f0b7db0108c6ab8f62b8f` (veja `main`).

## 1. Podatki

| Podatek | Vrednost |
| --- | --- |
| Datum | 12. november 2026, Europe/Ljubljana |
| Repozitorij | https://github.com/odprta-sola/solska-platforma |
| Veja poročila | `pregled-p0-prvi`, iz zgornjega commita |
| Pregledovalec | Codex; ponudnik OpenAI; različica modela: **ni znano** |
| Odgovorni človek za branje in sprejem | Mitja Pirih; njegov sprejem ob pripravi tega poročila še ni potrjen |
| Gostiteljski sistem | Ubuntu 24.04.5 LTS, Linux x86_64, jedro 7.0.0-113042-tuxedo |
| Docker / Compose | 29.9.3 (5457199) / v5.7.0 |
| Python | gostitelj 3.12.3; aplikacijski vsebnik 3.12.16 |
| Drugo izvajalno okolje | Debian 13.7 v aplikacijskem vsebniku; PostgreSQL 16.15; Mailpit 1.33.1 |

Razkritje izvora in neodvisnosti: pregledovane kode ni napisal ta pregledovalec. Po navedbi pobudnika in registru prispevkov jo je napisal Claude (Anthropic) po navodilih Mitje Piriha. Starejše osnutke dokumentacije je pobudnik pripravljal tudi s pomočjo OpenAI. Gre za pregled z drugim sistemom AI, ne za institucionalno neodvisen ali človeški prevzem. Navedba izvora ni forenzična potrditev avtorstva.

Prebrani so bili zahtevani kontrolni seznam, načrt priprave P0 (zlasti »Človeški prevzem«), stanje T, kratka specifikacija, besedilni vmesnik, celoten `api/openapi.yaml`, `DEVELOPER.md`, `CONTRIBUTING.md`, `SECURITY.md` in register prispevkov. Prebrani so bili tudi zahtevana koda, vsi aplikacijski testi, usmerjanje, skrbniški vmesnik, ukazi, CI, Docker konfiguracija in `LICENSE`.

Izvorna koda, testi in konfiguracija niso spremenjeni. Edini spremembi v veji sta ta datoteka in vpis pregledovalca v register prispevkov. Dodatni preverjevalni skripti so tekli zunaj repozitorija, nad ločeno testno zbirko in izmišljenimi podatki. Naključno testno geslo in servisni žetoni niso del poročila ali prispevka.

## 2. Povzetek

**Priporočilo za prevzem T: ne.** Referenčna osnova se zažene, vseh **85 obstoječih testov** je uspešnih, po odstranitvi volumnov in novi namestitvi pa tudi vseh **39 pogodbenih testov**. To ne dokazuje izpolnitve vseh prevzemnih meril. Dodatni robni preizkusi so pokazali neskladnosti pogodbe, predogleda in nadomestkov. Točki 8 in 9 ostajata neizpolnjeni. D12 ni potrjen.

Varnostno občutljive ugotovitve: **3 visoke, 0 kritičnih**. Njihovi opisi, lokacije in reprodukcije so iz javnega poročila izključeni ter se predajo pobudniku v pogovoru. Število ni potrdilo, da drugih ranljivosti ni. Ločeni zadetki javne baze za odvisnosti so navedeni v razdelku 6 in se ne prištevajo tem trem ugotovitvam.

Preverjeni so zagon, prava HTTP prijava s CSRF, ločene identitete pri skupnem kontaktu, osnovna izolacija družin, običajni odvzem povezave in granta v vseh štirih poteh, uvoz in njegovi obstoječi testi, izbrani odgovori API ter omejitve testov. Ni izveden celovit pregled dostopnosti, dejansko medmodulsko zadržanje ob izpadu, produkcijska namestitev, celoten pregled slik ali dokaz enakega vedenja vseh možnih zahtev.

Za ponovno presojo T so potrebni obravnava zasebnih ugotovitev, uskladitev pogodbe in izvedbe, dopolnjeni pogodbeni testi, demonstracija točke 8, pregled točke 9 ter zahtevane človeške in projektne potrditve. Dopolnitev, ki sodi šele pred B, sama po sebi ne širi obsega T.

## 3. Devet točk in dokaz izvedbe

Oznaka »izvedeno« pomeni opravljen pregled, ne nujno uspešno izpolnjeno merilo.

| # | Točka | Stanje pregleda | Ukaz oziroma korak in dejanski rezultat |
| --- | --- | --- | --- |
| 1 | Lastni otroci in zavrnitev tuje družine | izvedeno | HTTP `GET /accounts/login/`, POST z veljavnim CSRF in lastnim testnim geslom, nato `GET /p0/api/v1/me/relationships`. `parent-01`: otroka 01 in 02; `parent-03`: samo otrok 03. Kot `parent-03` POST `authorizations/check` s tujim in neobstoječim sklicem: oba HTTP 200, `allowed=false`, `reason_code=NOT_ALLOWED`. Odgovor je po pogodbi preverjanje pravice, zato HTTP 200 sam ne pomeni dovoljenja. |
| 2 | Skupen kontakt, različna računa in dovoljenja | izvedeno | Ločeni pravi HTTP prijavi `parent-01` in `parent-02`, `GET /me`: različna `person_id`; drugi račun vidi samo otroka 01. Prebrani model in uspešni testi `test_racun_s_skupnim_naslovom_se_prijavi_locen`, `test_skupni_kontakt_ostane_dve_osebi`, `test_dovoljenje_se_ne_prenasa_med_dejanji`. |
| 3 | Odvzem povezave oziroma granta | izvedeno | Obstoječi testi odvzema ter dodatni ločeni transakcijski ponovitvi `revoke_relationship` in `revoke_grant`: isti sklic ni več izdan v `/me/relationships`, izpade iz `audiences/resolve`, `authorizations/check` zavrne, kontaktni klic vrne 403. Zapisa in sled odvzema ostaneta. To velja za preizkušene neposredne odvzeme, ne za vse poznejše spremembe evidence. |
| 4 | CSV: napaka, ponovitev, sled kontakta | izvedeno | V celotni zbirki vseh 22 testov `registry.tests.test_import` uspe. Z ukazom `import_csv /data/testni-uvoz --source review-cli --actor staff-03` izdelan predogled, `--apply-batch` uveljavitev, nato nov predogled in uveljavitev istih datotek: drugi uvoz vse označi `unchanged`. Obstoječi test neznanega učenca potrdi brez delnega vpisa, test spremembe kontakta preveri `person.import_updated` in `changed_fields=[contact_email]`. Dodatno ugotovljena vrzel pri spremembi zbirke med predogledom in uveljavitvijo (P0-05). |
| 5 | Omejen servisni kontaktni klic | izvedeno | Prebrani `services.py` in API; izvedeni vsi testi `ContactContract` in servisni testi ter dodatni robni klici. Seja brez žetona je 401, manjkajoče dovoljenje 403, tuj sklic 403, odsoten kontakt je izrecen rezultat. Celotnega merila ni mogoče označiti kot izpolnjenega; občutljivi izsledki so izključeni iz javne različice. |
| 6 | Pregled kode | izvedeno | Prebrani `p0/registry/{authz,api,services,importer,models}.py`, vsi `p0/stubs/*.py`, `p0/config/settings.py` in povezane poti. Odgovori in meje so spodaj. Pregled je opravil AI, ne človek. |
| 7 | Ponastavitev in pogodbeni testi | izvedeno | `docker compose down -v`; `docker compose up --build -d`; `seed_test_data` z novim naključnim `SEED_PASSWORD`; `docker compose exec -T p0 python manage.py test registry.tests.test_contract`: **39/39 OK**. Pravi P0 in nadomestka tečejo v istem Django testnem procesu; to niso omrežni preizkusi samostojnih modulov ali SMTP dostave. |
| 8 | Zaščiteno dejanje/dostava ob izpadu P0 in obnovi | ni izvedeno | Končnega scenarija ni mogoče izvesti: mapi pravih M1/M2 ne obstajata. Branje vseh nadomestkov potrdi, da ne kličeta P0, nimata dostavnega delavca in ne pošiljata. Pogodbeni test z »izpadom« v imenu izpada ne povzroči (P0-07). Nepopolnost, navedena v stanju T, je potrjena. Ločena injekcija napake P0 ni nadomestilo tega scenarija. |
| 9 | Tipkovnica, fokus, napake, bralnik zaslona | delno | Pridobljen in pregledan HTML privzete prijave: oznaki za uporabniško ime in geslo obstajata, atribut `lang` manjka. Prijava funkcionalno uspe prek HTTP. Ročni prehod s tipkovnico, vidni fokus, razumevanje napak z uporabnikom in bralnik zaslona: **ni izvedeno**, ni razpoložljivega postopka z bralnikom. Zaslona za seznam oseb in uvoz ne obstajata. Merilo ni izpolnjeno; P0-10. |

### Izvedeni ukazi in izpisi

Priprava je sledila kontrolnemu seznamu. `SEED_PASSWORD` je bil ustvarjen s `secrets.token_urlsafe`, posredovan v okolju in nikoli izpisan. Po koncu je izveden tudi drugi `docker compose down -v`.

```text
docker compose up --build -d
  db: Healthy; p0: Started; mail: Started
python manage.py seed_test_data  [znotraj vsebnika, SEED_PASSWORD iz okolja]
  Testni nabor naložen.
docker compose exec -T p0 python manage.py test --verbosity 2
  Found 85 test(s).
  Ran 85 tests in 4.264s
  OK
ruff check .
  All checks passed!
ruff format --check .
  39 files already formatted
python manage.py makemigrations --check --dry-run
  No changes detected
python manage.py check
  System check identified no issues (0 silenced).
python manage.py test registry.tests.test_contract  [po ponastavitvi volumnov]
  Found 39 test(s).
  Ran 39 tests in 1.249s
  OK
python3 scripts/check_docs_links.py
  Notranje povezave in sidra so veljavni.
```

Dodatni preverjevalni skript zunaj repozitorija je v zadnjem zagonu izvedel **16 preizkusov: 5 uspešnih, 11 neuspešnih pričakovanj**, brez napak pomožnega ogrodja (`Ran 16 tests in 1.298s; FAILED (failures=11)`). Uspeh preizkusa, ki dokazuje pomanjkljivost validatorja, ne pomeni pravilnosti izdelka. Dve neuspešni pričakovanji sta varnostno občutljivi in tu nimata podrobnega izpisa. Ostalih devet:

```text
neveljavna oblika UUID:       pričakovano 400 ali zavrnitev; dejansko 500 text/html
seja brez CSRF:              403 text/html; pričakovanje JSON ni uspelo
dodatno nedovoljeno polje:   pričakovano 400; dejansko 200
manjkajoči obvezni params:   pričakovano 400; dejansko 202
ista oseba, dva obsega:      pričakovani 2 postavki; dejansko 1
ista zahteva po izteku:      pričakovan isti prevzem 202; dejansko 400
sprememba po predogledu:     predogled unchanged; uveljavitev spremeni osebo
napačna metoda /me:          405 text/html; pričakovanje JSON ni uspelo
sintetična nedosegljivost:   pričakovano 503; dejansko 500 text/html
```

Preizkus po izteku preverja predlagano razlago ponovljivosti, ki potrebuje odločitev D12 (P0-04); rezultat ni samostojna potrditev te razlage. Prvi zagon pomožnega skripta je imel še dve napaki pregledovalčevega ogrodja (položaj povratka transakcije in neposreden klic allauth brez konteksta zahteve). Odpravljeni sta bili samo v začasnem skriptu; navedeni končni rezultat ju ne vsebuje.

## 4. Ugotovitve

Vrstice kode se nanašajo na pregledani commit, ne na prihodnje popravke. Ocenjena resnost spodnjih javnih ugotovitev upošteva razvojno, sintetično okolje.

| ID | Resnost | Kje | Opis, ponovljiv korak in predlog |
| --- | --- | --- | --- |
| P0-01 | srednja | `p0/registry/api.py:133`; `p0/stubs/m1.py:30`; `api/openapi.yaml:193` in `:249` | Vhod ni dosledno skladen s shemo. Prijavljena seja pošlje sicer veljaven `AuthCheckRequest` z dodatnim `extra`: 200, čeprav shema določa `additionalProperties: false`. Servis z `m1.delivery` odda veljavno dostavno zahtevo brez `params`: 202, čeprav je polje obvezno. Predlog: enotno preverjanje zahtev po dejanski pogodbi, tudi ugnezdenih objektov, ter negativni pogodbeni primeri. |
| P0-02 | srednja | `p0/registry/api.py:44`, `:146`; `api/openapi.yaml:37` | Obdelava napak in shema odgovorov nista celoviti. Servisni `authorizations/check` s `subject_id="not-a-uuid"` vrne 500 HTML, ker `ValidationError` ni prestrežen. Injekcija `OperationalError` v `registry.authz.check_scope` vrne 500 namesto opisane 503. Seja brez CSRF vrne 403 HTML; napačna metoda `/me` 405 HTML brez pogodbene sheme. Predlog: validacija identifikatorjev, dosledna pretvorba pričakovanih napak v JSON in določitev/implementacija 405 ter 503 v OpenAPI. Napaka ne sme biti prikrita kot `allowed=false`. |
| P0-03 | srednja | `p0/stubs/m1.py:89`; `api/openapi.yaml:256` | Nadomestek združi dve postavki iste osebe v eno, ker slovar uporablja samo `person_id`. Ponovitev: dve postavki z istim izmišljenim `person_id` in različnima `scope_ref` vrneta 202, toda eno postavko in `counts.queued=1`. Shema taki dve postavki dopušča, odgovor pa izgubi razlikovanje obsegov. Predlog: D12 določi identiteto dostavne postavke in preklic; do takrat nedvoumna zavrnitev ali ohranitev obeh, ne tiho prepisovanje. V stanju T je več otrok že navedeno kot odprto. |
| P0-04 | opomba | `p0/stubs/m1.py:50`, `:75`; `api/openapi.yaml:79` | Ponovitev iste prej sprejete zahteve po `expires_at` vrne 400, ker preverjanje časa prehiti preverjanje idempotence. Ponovitev: prevzem pri času t, nato isti nespremenjeni JSON pri t+10 s in izteku t+5 s; izmerjeno 202 → 400. Ne gre za čakanje, ampak za nadzorovano zamenjavo ure v testu. Predlog: D12 loči iztek dostave od dovoljenega okna ponovitev in določi rezultat po izteku; nato to vedenje preveri. |
| P0-05 | srednja | `p0/registry/importer.py:659`, `:665` | Enak hash CSV ni enak potrjenemu seznamu sprememb. Ponovitev: po prvem uvozu predogled istih datotek kaže vse `unchanged`; neposredno spremenimo prikazno ime v zbirki; uveljavitev istega predogleda ime prepiše nazaj in izvede `update`, ki ni bil prikazan. Predlog: vezava potrditve tudi na različico podatkov oziroma primerjava izračunanih operacij s potrjenimi; spremenjen predogled zahteva novo potrditev. Podatkovne spremembe in zaključek serije naj imajo usklajeno transakcijsko mejo. Sočasna tekma ni bila izmerjena. |
| P0-06 | srednja | `p0/registry/tests/test_contract.py:25`, `:80`, `:300`; `api/openapi.yaml:241` | Trditev »vsak odgovor« ni podprta. Validator nima `FormatChecker`; neposredni `validate("AuthCheckResponse", {..., "checked_at": "not-a-date"})` uspe. Uspe tudi kontakt z neveljavnim e-naslovom in medsebojno neskladnima `deliverable`/`reason_code`, ker manjka tako preverjanje formata kot pogojna shema. Nekateri testi sploh ne kličejo `validate`, pomožni klic ne preveri vsakega odgovora in ne validira vhodov/statusa/vsebinskega tipa proti operaciji. Predlog: skupni preverjevalnik operacij, statusov in medijev, preverjanje formatov, smiselne pogojne sheme ter namerno pokvarjeni primeri, ki morajo pasti. |
| P0-07 | srednja | `p0/registry/tests/test_contract.py:461`, `:484`; `p0/core/tests/test_boundaries.py:21`; `p0/registry/tests/test_model.py:62` | Lažno pomirjujoča zelena preverjanja. Test z »izpadom« preveri samo 404 pri tujem lastniku, brez izpada. Test izteka ročno nastavi `expired`, ne preizkusi avtomatskega izteka. Test meja preskoči neobstoječi mapi M1/M2 in nadomestkov ne pregleda. Test odnosa brez granta preveri le odsotnost vrstic, ne pokliče avtorizacije. Predlog: ustrezna imena oziroma izrecni preskoki in dejanski scenariji z napako, uro ter zabeleženimi stranskimi učinki. |
| P0-08 | srednja | `p0/stubs/state.py:3`; `p0/stubs/m1.py:86`; `p0/stubs/m2.py:17`; `api/openapi.yaml:78` | Nadomestka sta primerna za omejene shematske primere, ne dokaz vedenjske zamenljivosti. M1 vrne 202 po zapisu v procesni slovar; ne hrani dostavnega roka, ne izvaja urnika/dostave ali poslovne deduplikacije. M2 odloča po globalnem `need_ref`, brez modela naročene potrebe. Dokaz: branje vseh treh datotek ter pogodbeni testi. Obnova po ponovnem zagonu in SMTP nista izvedena. Predlog: jasno omejena merila nadomestkov ter ločeni obvezni preizkusi trajnosti, izpada, potrebe in obnovitve pred T. |
| P0-09 | nizka | `DEVELOPER.md:80`, `:94`; `docs/projekt/stanje-prevzema-T.md:3`, `:16`; `SECURITY.md:3`; `docs/arhitektura/kratka-specifikacija-P0-M1-M2.md:5` | Dokumenti niso časovno usklajeni. Izmerjeno je 85 testov (od tega 39 pogodbenih in 22 uvoznih), seznam in stanje navajata 82. Stanje govori o nezdruženih PR #31–36, čeprav zgodovina pregledanega `main` vsebuje njihovo izvedbo. Kratka specifikacija in SECURITY še opisujeta stanje pred kodo/testi. »Vsak odgovor« in zagotovilo o predogledu presegata dokazano. Predlog: opise vezati na datum/commit in razlikovati načrt, sintetični test, neodvisni pregled ter človeški prevzem. V tem prispevku besedila niso popravljena. |
| P0-10 | srednja | `p0/config/settings.py:57`; `p0/config/urls.py:5`; `docs/projekt/stanje-prevzema-T.md:25` | Točka dostopnosti ostaja odprta. GET `/accounts/login/` vrne oznaki vnosov, brez atributa `lang` na `html`; lastnih predlog ni. Manjkajo osnovni zasloni evidence/uvoza. Predlog: dopolniti dogovorjene zaslone in predloge ter dokumentirati ročni pregled s tipkovnico, vidni fokus, napake in bralnik zaslona. Iz HTTP/HTML pregleda ni mogoče sklepati o dejanskem fokusu ali uporabnosti bralnika. |
| P0-11 | nizka | `p0/requirements.txt:1`; `p0/requirements-dev.txt:1`; `p0/Dockerfile:1`; `docker-compose.yml:4`, `:18` | Namestitev ni verzijsko zamrznjena: razponi paketov, `gunicorn>=23`, razvojna orodja brez omejitev ter premične oznake slik. Dva uspešna zagona sta uporabila predpomnilnik plasti; to ni dokaz enake gradnje iz nič na drug dan. Predlog: pregledan zaklep odvisnosti s hashi, določene slike/digesti in dokumentirana politika posodobitev; dodati licenčni popis slike. |

### Odgovori na vprašanja pregleda kode

| Vprašanje | Odgovor in meja dokaza |
| --- | --- |
| Pot do oseb/kontaktov mimo `check_grant` ali sklica? | Lastni `/me` uporablja `session_person`; seznam lastnih povezav preveri aktivni odnos in grant, ne kliče pa iste funkcije kot preverjanje dejanja. `/me/classes` filtrira aktivno dodelitev. Django admin je ločena privilegirana pot z Django dovoljenji. Vprašanje je pregledano; občutljivi deli odgovora so iz javne različice izvzeti. Ni splošne potrditve, da je vsaka pot varna. |
| Razkrivanje tujih sklicev: vsebina, status, čas? | Za uporabniški `authorizations/check` sta tuj in enako dolg neobstoječ sklic dala enak status in vsebino, razen pričakovano različnega `checked_at`. V dodatnem testu 40 prepletenih ponovitev na primer: mediani 1,951 ms in 1,896 ms, razpona 1,636–4,040 in 1,615–3,004 ms. To je meritev Django odjemalca v procesu, ne omrežni ali statistični dokaz odsotnosti časovnega kanala. Neobstoječe in tuje dostavne zahteve M1 se skrijejo z `_own` in 404. Druge poti niso s tem izčrpno potrjene. |
| Ločitev seje in servisnega žetona? | `service_only` bere samo Bearer in dovoljenje servisa. Pri mešanici veljavnega žetona ter seje je preverjanje servisno; neveljaven Bearer s sejo vrne 401, brez prehoda na uporabnika. Seja na servisnem kontaktu je 401. Dinamično preverjeno. Sejne GET poti uporabljajo sejo; žeton sam tam ni prijava. Delegiranje avtorjeve seje ostaja odprto vprašanje D12, ne potrjena integracija. |
| Izjeme `csrf_exempt`? | Dve lokaciji: servisni dekorater `services.py:50` in mešana pot `api.py:146`. Slednja za vejo seje znova vključi `csrf_protect`; odjemalec z `enforce_csrf_checks=True` brez CSRF je zavrnjen. Servisni žeton brez piškotkov deluje. Vsebina odgovora napake pa ni pogodbeni JSON (P0-02). |
| Hramba žetonov? | Naključni 32-bajtni izvor v `secrets.token_urlsafe(32)`, v bazi SHA-256 in `active`; žeton se pokaže ob ustvarjanju. Sklici prav tako uporabljajo `secrets`; sami niso dovoljenje in se preverjajo z osebo ter aktualnim grantom. Prebrano in preizkušena deaktivacija v obstoječih testih. Potek, rotacija in omejevanje servisnih klicev niso izvedena kot celovit življenjski cikel. |
| Uvoz: reference, pooblastilo in ugibanje? | `validate_references` preverja ključe znotraj vira oziroma uvoza; ne sprejema poljubnega UUID kot dokaza povezave. `process` zahteva vlogo `office` ali `admin`, pooblastilo ponovno preveri ob uveljavitvi. Neznane reference in navaden nepooblaščen uvoz so dinamično zavrnjeni. Pooblastilo je šolsko, brez modela delegiranega uvoza po oddelkih. CLI predpostavlja zaupanja vrednega operaterja strežnika; parameter `--actor` ni prijavni mehanizem. Občutljivi dodatni izsledki niso javni. |
| Dnevniki in `ChangeAudit`? | Sled sprememb hrani dejanje, identifikator, izvor in imena polj, ne stare/nove kontaktne vrednosti; preverjeno pri spremembi kontakta. Predogled dodatno hrani izvorne ključe, napake pa tudi sporočila. Za poljubno vhodno besedilo ni splošnega dokaza anonimnosti; ključi morajo ostati neosebni. Ni izveden celovit pregled vseh dnevnikov infrastrukture. Občutljivi dodatni izsledki ostanejo zasebni. |
| Drugačna vsebina od predogleda? | Spremenjeni bajti CSV so zavrnjeni s SHA-256, kar uspešno preveri obstoječi test. Spremenjeno stanje baze ob enakih bajtih pa lahko spremeni operacije (P0-05). Uveljavitev podatkov je atomska, zapis zaključnega stanja serije je zunaj notranje transakcije `process`. Sočasna uveljavitev oziroma izpad med tema zapisoma ni bila izvedena. |
| Surove poizvedbe in neomejen vnos? | Iskanje `raw`, `extra`, `cursor`, `execute`, `exec`, `eval` po Python kodi: edina surova poizvedba je konstantni `SELECT 1` v health, brez uporabniškega vnosa; uvoz in avtorizacija uporabljata ORM. CSV omejitvi sta 5 MiB na datoteko in 50.000 vrstic; ukaz datoteke prej v celoti prebere. Django privzeto omeji telo na 2.621.440 bajtov, M1 na 200 prejemnikov. Vsi nizi, seznami odgovorov in `recipient_ids` nimajo lastnih meja/paginacije; vhodne JSON sheme ne določajo `maxLength`. Ni izveden obremenitveni ali DoS preizkus. |
| Odvzem na vseh poteh? | Dodatno preverjeno za neposreden odvzem vsake vrste: `/me/relationships`, `audiences/resolve`, `delivery-contacts/resolve` in `authorizations/check`; dokaz v točki 3. Seznam lastne še aktivne povezave po odvzemu samo granta ostane, vendar brez tega dovoljenja; to ni odobritev dejanja. Vseh sprememb življenjskega cikla s tem ni mogoče potrditi. |
| DEBUG, STUBS, piškotki in glave? | Z `DEBUG=0` so privzeto prazni STUBS in zahtevane skrivnosti iz okolja; piškotka session/CSRF sta Secure, session tudi HttpOnly in SameSite=Lax. V razvojnem HTTP odzivu so izmerjene glave DENY, nosniff, same-origin za Referrer/COOP; session ni Secure, skladno z razvojnim HTTP. Izrecni `STUBS=m1,m2` se sprejme tudi pri `DEBUG=0`: dinamično razrešena pot M1, zato komentar »nikoli v produkciji« ni varovalo. `check --deploy` s sintetičnimi skrivnostmi izpiše W004 (HSTS) in W008 (HTTPS preusmeritev). HTTPS vhod, proxy in produkcijska konfiguracija niso nameščeni/preverjeni. |
| allauth in obnova pri skupnem e-naslovu? | Nastavitve, obrazec, obstoječa dokumentirana meja T/B in sintetični postopek so pregledani. Zaradi pravila o zasebnosti vsebuje javna različica samo skupno število/resnost varnostnih ugotovitev zgoraj; podroben odgovor je predan v pogovoru. Individualen postopek pred B ni s tem potrjen. |

### Pogodba in dejansko pokritje odgovorov

Odgovor na vprašanje »ali vsak odgovor ustreza OpenAPI« je **ne**. Uspešne reprezentativne odgovore vseh desetih operacij osnutka preverjajo obstoječi testi, ki so bili zagnani, vendar ne preverjajo vseh vej ali vseh zahtev. `SpecCoverage` preveri razrešitev poti in prisotnost ključev v YAML, ne ustreznosti vsakega HTTP odziva. Posebej so dokazani nepogodbeni 403/405/500, manjkajoča 503, sprejem nepogodbenih vhodov in prešibki formati (P0-01, P0-02, P0-06).

Vhodni `Id` je v shemi poljuben neprazen niz, izvajanje za osebe zahteva UUID; pogodba mora to razliko izrecno razrešiti. `AuthCheckResponse` ne poveže logično `allowed` z razlogom. `ContactResponse` ne zahteva e-naslova in jezika le pri uspehu. `DeliveryStatus.counts` ne zagotavlja ujemanja s postavkami. Tihi čas, trajnost pred 202, poslovni ključ dogodka in vezava potrebe zahtevajo vedenjske teste; validacija JSON sheme teh pravil ne dokazuje.

## 5. Pokritost dvajsetih skupin preizkusov

»Pokrit« se nanaša na navedeno merilo v okviru prvega T, ne na dokazan izdelek za produkcijo. »Delno« pomeni, da vsaj en zahtevan del nima ustreznega dokaza ali ne uspe. Poslovni scenariji pravih M1/M2 so zunaj prvega referenčnega P0; njihove pogodbe in nadomestki pa ostajajo obveznost T.

| # | Scenarij kratke specifikacije | Pokritost | Dokaz oziroma vrzel |
| --- | --- | --- | --- |
| 1 | Dva računa z istim kontaktom | delno | Ločeni identiteti, povezave in pravice so preizkušene; odzivi M2 ter individualni postopek niso delujoči. |
| 2 | Druga družina, ugiban ID, tuj sklic | delno | Uporabniški sklici imajo preverjeno zavrnitev; celovito merilo vseh osebnih/podatkovnih poti ni potrjeno. |
| 3 | Zaposleni zunaj oddelka | delno | `AudiencesContract` potrdi zavrnjen predogled; objava pravega M1 še ne obstaja. |
| 4 | Učenčev račun in ciljna skupina | ni v obsegu T | Pogojena razširitev; seed ne ustvarja prijavnih računov učencev. |
| 5 | Odnos brez granta, nato odvzem | delno | Pregled kode in modela; neposredni odvzem obeh vrst je preverjen prek vseh štirih poti. Test odnosa brez granta preveri le odsotnost granta, ne same zavrnitve dejanja (P0-07). |
| 6 | Starejši uvoz po ročni omejitvi | delno | Obstoječi test uspe za nespremenjeno identiteto vrstice. Celotnega merila ni mogoče potrditi; podrobnosti niso javne. |
| 7 | Napačen CSV ali neznana referenca | pokrit | `ValidationTests`, `AtomicityTests`: neznani učenec, datumi, šifranti, napaka med uveljavitvijo; brez delnega vpisa v preverjenih primerih. |
| 8 | Ponovitev, dvojnik, manjkajoča vrstica | pokrit | `IdempotencyTests`, validacija dvojnikov in dejanska CLI ponovitev; stabilni ključi istega vira, brez samodejnega odvzema manjkajoče vrstice. |
| 9 | Aktivacija/obnova pri skupnem predalu | ni v obsegu T | Izrecna dopolnitev pred B; izvedeni omejeni pregled ni prevzem individualnega postopka. |
| 10 | Odjava, CSRF, podtaknjen uporabnik, servis | delno | Odjava in sejni CSRF, tuj subject ter mešani žeton/seja so preizkušeni; delegirana identiteta in vse pogodbe napak niso potrjene. |
| 11 | Odprtje in izrecna seznanitev M1 | ni v obsegu T | Poslovna implementacija M1, ne referenčni P0. |
| 12 | Dva otroka, nova različica M1 | ni v obsegu T | Skupinska potrditev in različice M1 ne obstajajo; podporna dostavna vrzel je posebej P0-03. |
| 13 | Več namenov, Ne in brez odziva | ni v obsegu T | Poslovna implementacija M2. |
| 14 | Dva otroka/odločevalca, nasprotni odgovori | ni v obsegu T | Poslovna implementacija M2. |
| 15 | Pregled in sprememba različice M2 | ni v obsegu T | Poslovna implementacija M2. |
| 16 | Sprememba/preklic in zgodovina obrazca | ni v obsegu T | Poslovna implementacija M2; dostavni preklic nadomestka ni preklic izjave. |
| 17 | Izpad M1, izgubljen 202, ključi/dogodek | delno | Isti ključ in konflikt vsebine sta preizkušena v procesu; ni trajne namere M2, obnove, preizkusa izgubljenega odgovora ali poslovne deduplikacije novega ključa. |
| 18 | Potreba, selektivni preklic, izpadi, urnik, iztek | delno | Selektivni preklic in izidi stanj so preizkušeni; avtomatski iztek, tihi čas ter dejanska izpada P0/M2 niso. |
| 19 | Negotov SMTP, odvzem med dostavo, obnova | nepokrit | Ni dostave/obnove, noben test ne uvede negotove SMTP predaje. Zgolj ročni `handed_off` ni tak dokaz. |
| 20 | Sveža namestitev, nadomestki, izvoz, dostopnost | delno | Ponovna namestitev po odstranitvi volumnov in 39 pogodbenih testov uspeta; gradnja uporablja predpomnilnik. Izvoz pred B ni izveden; tipkovnica/bralnik nista pregledana. |

Skupaj: **2 pokrita, 9 delno, 1 nepokrit, 8 zunaj obsega T**. Izključitev poslovnih scenarijev ne odpravlja obveznosti pogodbenega in prevzemnega paketa T.

## 6. Odvisnosti in licence

Pregledani so `requirements.txt`, `requirements-dev.txt`, Dockerfile in Compose. Spodnje izdaje so bile izmerjene v dejansko uporabljenem vsebniku z `importlib.metadata`, ne izračunane iz dovoljenih razponov. Licenčne oznake izhajajo iz nameščenih metapodatkov; pri `sqlparse` je bilo dodatno prebrano priloženo besedilo BSD.

| Odvisnost | Deklaracija / dejanska izdaja | Licenca oziroma ugotovitev |
| --- | --- | --- |
| Django | `>=5.2,<5.3` / 5.2.19 | BSD-3-Clause |
| psycopg in psycopg-binary | `[binary]>=3.2,<4` / oba 3.3.9 | LGPL-3.0-only; binarna izdaja vključuje dodatne knjižnice, ki potrebujejo lasten popis |
| django-allauth | `>=65,<66` / 65.22.0 | MIT |
| gunicorn | `>=23` / 27.0.0 | MIT |
| Ruff, razvoj | brez zaklepa / 0.17.4 | MIT |
| jsonschema, razvoj | brez zaklepa / 4.26.0 | MIT |
| PyYAML, razvoj | brez zaklepa / 6.0.3 | MIT |
| asgiref | posredno / 3.13.0 | BSD-3-Clause |
| sqlparse | posredno / 0.6.1 | BSD-3-Clause, prebrana priložena licenca |
| attrs | posredno / 26.1.0 | MIT |
| rpds-py | posredno / 2026.9.1 | MIT |
| referencing | posredno / 0.37.0 | MIT |
| jsonschema-specifications | posredno / 2025.9.1 | MIT |
| typing_extensions | posredno / 4.16.0 | PSF-2.0 |
| pip | orodje v osnovni sliki / 25.0.1 | MIT; ni deklaracija aplikacijske odvisnosti |
| Python | `python:3.12-slim` / 3.12.16, Debian 13.7 | PSF-2.0 in vključene licence; gradilni recept Docker ima MIT, kar ni licenca vse vsebine slike |
| PostgreSQL | `postgres:16` / 16.15 | PostgreSQL License za strežnik; slika ima tudi sistemske pakete |
| Mailpit | `axllent/mailpit:latest` / 1.33.1 | MIT za projekt; licence vseh vključenih komponent niso popisane |

V izpisu gradnje je osnovni Python referenciran z `sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b`. Uporabljeni repozitorijski digest PostgreSQL je `sha256:f9a7b9ebf6f56201f949db745e47bc423c0f0f8294bafe991cc10bf74b029657`, Mailpit pa `sha256:aef2aacc11f075ec0fb6874275ee4a421e688e11a96ebb296134d1735c7761ce`. To so opažene reference pri tem pregledu, ne zaklep v projektu.

Ocena za EUPL 1.2: pri navedenih permisivnih licencah ni prepoznana neposredna ovira za uporabo z aplikacijo EUPL ob ohranitvi ustreznih obvestil in pogojev. Pri LGPL knjižnicah ostajajo njihove obveznosti (licence, izvor/ponudba izvora, možnost zamenjave glede na način distribucije); priloga EUPL med združljivimi licencami vsebuje LGPL v3. To ne pomeni, da so vse komponente prelicencirane v EUPL. **Popolna skladnost distribucije slike ni potrjena**, ker niso pregledane vse sistemske in vgrajene binarne knjižnice ter dobava njihovih izvorov/obvestil. Licenca dokumentacije D15 ostaja odprta. Gre za tehnični popis in omejeno presojo, ne pravno mnenje.

Preverjeni zunanji primarni viri: [licenca Psycopg](https://github.com/psycopg/psycopg/blob/master/LICENSE.txt), [binarna namestitev Psycopg](https://www.psycopg.org/psycopg3/docs/basic/install.html), [licence Python](https://docs.python.org/3.12/license.html), [licenca gradilnega recepta Docker Python](https://github.com/docker-library/python/blob/master/LICENSE), [licenca PostgreSQL](https://www.postgresql.org/about/licence/) in [licenca Mailpit](https://github.com/axllent/mailpit/blob/develop/LICENSE). EUPL je bila prebrana v projektni datoteki `LICENSE`. Zunanji viri so bili dostopani 12. 11. 2026; niso pripeti na hash in ne nadomestijo popisa točno distribuiranih datotek.

### Znane ranljivosti

V začasnem virtualnem okolju vsebnika je nameščen **pip-audit 2.10.1**. Aplikacijski paketi niso posodobljeni. Izvedeno:

```text
/tmp/p0-audit-tools/bin/pip-audit --cache-dir /tmp/p0-audit-cache \
  --path /usr/local/lib/python3.12/site-packages --format json \
  --output /tmp/p0-dependency-audit.json
Found 12 known vulnerabilities in 1 package
```

JSON vsebuje 16 pregledanih distribucij in podvojene zapise: **12 zadetkov pomeni 6 različnih opozoril**, ne 12 različnih ranljivosti. Gre za orodje v osnovni sliki; v preostalih 15 distribucijah baza ni vrnila zadetkov. Resnost šestih opozoril po pregledani GitHub Advisory Database je **5 srednjih in 1 nizka**. Uporabnost posameznega zadetka za točno okolje ni v celoti potrjena; en zadetek je izrecno pogojen s starejšim Pythonovim načinom razpakiranja. To ni izjava, da je vseh šest mogoče izkoristiti v aplikaciji. Metapodatki in datoteka JSON ostanejo zunaj javnega prispevka; opozorila so že javna, njihove povezave so predane pobudniku ločeno.

Prvi poskus pip-audit je padel zaradi nezapisljive privzete poti `/home/appuser/.cache/pip-audit` (`PermissionError`); ponovitev z zgornjim `--cache-dir` je zaključila pregled. Celovit pregled CVE sistemskih paketov, PostgreSQL/Mailpit slik in vgrajenih knjižnic psycopg: **ni izvedeno**, uporabljen je bil pregled Python distribucij, ne pregledovalnik slik. Priporočen je ločen popis slike, pregled orodij gradnje in ponovitev skeniranja ob zaklenjenih odvisnostih.

## 7. Omejitve pregleda

- Pregled je opravil AI. Mitja Pirih in neodvisen človek poročila v tej izvedbi še nista potrdila. Organizacijski pogoji D03/D08/D09/D14 niso bili potrjevani ali spreminjani.
- Samo sintetični podatki; ni resničnih uporabnikov, šolskih evidenc ali zunanjega pošiljanja. Preizkusi allauth uporabljajo testni poštni izhod; nadomestka e-pošte ne pošiljata.
- Ročna tipkovnica, vidni fokus, bralnik zaslona, uporabniško razumevanje napak in administrativni uporabniški postopki: **ni izvedeno**, ni potrebnega ročnega preverjanja/bralnika in dogovorjenih zaslonov.
- Dejanski izpad P0/M2 med dostavo, obnova procesa/kopije, trajnost prevzema 202, izgubljeni omrežni odgovor, negotov SMTP in tekma odvzema s pošiljanjem: **ni izvedeno**, pravi moduli/dostavni delavec niso na voljo. Injekcija napake v P0 preizkuša samo njegov odgovor.
- Produkcijski HTTPS/proxy, več delavcev, sočasni uvoz, vzdržljivost, poln življenjski cikel žetonov in izvoz: **ni izvedeno**; pregled omejuje lokalna referenčna namestitev in statično branje.
- Ni merjene odsotnosti vseh časovnih kanalov. Navedena meritev je majhen lokalni vzorec za eno pot. Ni izveden izčrpen varnostni ali obremenitveni pregled.
- Gradnja je uporabljala že obstoječi predpomnilnik odvisnosti. Ponastavljena sta vsebnika/podatkovni volumen, ne celoten Docker predpomnilnik. Čista namestitev je ponovljena na tem računalniku; reproducibilnost gradnje na drug dan/stroju ni potrjena.
- Celovit SBOM, licence vseh sistemskih/binarnih komponent in CVE slik: **ni izvedeno**, opravljeno je bilo ožje preverjanje Python paketov in glavnih licenc.
- Prvi običajni poskus kloniranja je bil blokiran z DNS peskovnika, prvi Docker z dostopom do socketa; po dovoljenem dostopu oba uspešno ponovljena. Pomožni poskus uvoza allauth brez inicializacije Django je vrnil `ImproperlyConfigured`; končni preizkus je bil izveden s pravo Django zahtevo. Ti zapleti niso ugotovitve o napaki projekta.
- Dodatni skripti in podrobni varnostni rezultati zaradi dovoljenega obsega sprememb ter zasebnosti niso dodani v repozitorij. Javne reprodukcije so opisane zgoraj; ne predstavljajo nove vzdrževane testne zbirke.

## 8. Izjava

Ta pregled **ni človeški prevzem, ni pravno mnenje in ni potrditev D12**. Uspešna izvedba obstoječih testov ni dokaz izpolnitve vseh prevzemnih pogojev. Pregledovalec ne potrjuje produkcijske pripravljenosti, pravic prispevkov dijakov ali sprejema poročila v imenu Mitje Piriha. Človek poročilo in vpis prebere ter o sprejemu odloči posebej.
