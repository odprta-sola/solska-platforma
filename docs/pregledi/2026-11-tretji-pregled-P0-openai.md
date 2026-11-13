# Tretji neodvisni pregled P0 – paket T (OpenAI)

Pregledani commit: **`d261ace2902a13788b4a36f75399ebc20eb400a9`**. Novejši `main` ni predmet tega pregleda.

## 1. Podatki

| Podatek | Vrednost |
| --- | --- |
| Datum | 13. november 2026, Europe/Ljubljana |
| Repozitorij | https://github.com/odprta-sola/solska-platforma |
| Veja poročila | `pregled-p0-tretji-openai`, iz pregledanega commita |
| Sistem in ponudnik | Codex, OpenAI; različice modela ne navajam |
| Odgovorni človek | Mitja Pirih; sprejem še ni potrjen |
| Gostitelj | Ubuntu 24.04.5 LTS, x86_64, Linux 7.0.0-113042-tuxedo; Python 3.12.3 |
| Docker / Compose | 29.9.3 / v5.7.0 |
| Aplikacijsko okolje | Python 3.12.16, Debian 13.7, Django 5.2.19, django-allauth 65.22.0, psycopg 3.3.9 |
| Zbirka / pošta | PostgreSQL 16.15; pripeta razvojna slika Mailpit 1.33.1 |
| Orodja | pip 26.3, Ruff 0.17.4, pip-audit 2.10.1, Trivy 0.76.2; Chrome 157.0.8103.38, Playwright |
| Zamrznitev | `v1.0.0` → `68fea198176d7fe26660dbfb9eddb1a8fee14c8e`; OpenAPI na tej oznaki in pregledanem commitu enak |

Pregledovane kode in popravkov nisem napisal. Projekt jih pripisuje Claude (Anthropic); starejša dokumentacija je nastajala tudi s pomočjo OpenAI. Isti sistem je opravil predhodna pregleda OpenAI, zato ta pregled ni neodvisen od njunih presoj. Je pregled kode z drugim sistemom AI, ne institucionalno neodvisen ali človeški prevzem. Izvora ne potrjujem forenzično.

Prebrana so poročila obeh krogov, oba zapisa o odpravi, šest objavljenih varnostnih nasvetov, pogodba in OpenAPI, paket D12 s tabelo B, register odločitev z razdelkom o naročniku in izvajalcih, kontrolni seznam, kratka specifikacija, stanje T, varstvo podatkov, pregled dostopnosti, odvisnosti in licence, CONTRIBUTING, DEVELOPER, SECURITY in navodila ekip. Pregledane so spremembe od `184c8f9`, nova koda, povezani modeli, predloge, testi, migracije, CI in konfiguracija.

Edina sprememba v veji je to poročilo. Main, koda, testi in register prispevkov niso spremenjeni. Mutacije in dodatni skripti so zunaj repozitorija, v lastni začasni kopiji. Uporabljeni so samo izmišljeni podatki. Lastna gesla, servisni žetoni in ključ za produkcijski preizkus so naključni, brez objave v repozitoriju ali poročilu. Obstoječih konstant v projektnih testih nisem spreminjal.

## 2. Povzetek

**Prevzema T še ne priporočam.** Obe izvedbi celotne zbirke imata **275 testov, OK, 0 preskočenih**, druga po odstranitvi volumna in svežem zagonu. Pričakovano število se ujema. Prvotne programske reprodukcije drugega kroga so preprečene, vključno z dejansko sočasnostjo R-09 in mejo roka R-10. Dokumentacija ostaja delno neusklajena, opozorila razvojne slike ostajajo.

**Varnostno občutljivi izsledki: 4 — 3 srednje, 1 nizka, 0 visokih, 0 kritičnih.** Lokacije, opisi in reprodukcije niso del javnega poročila; pobudniku so predani ločeno v pogovoru. Zadetki skenerjev odvisnosti se ne prištevajo temu številu. To ni zagotovilo odsotnosti drugih težav.

**Ogrodja in navodil še ne priporočam kot brezpogojno zanesljive reference za začetek odvisne implementacije.** Za nadaljnje lokalno delo na izmišljenih podatkih sta uporabna, vendar je treba pred predajo ekipam obravnavati zasebne izsledke, popraviti dejanski sejni HTTP klic (T-02), razjasniti trajno shranjeno dostavno zahtevo (T-01), utrditi zamrznitev (T-03) in uskladiti status D12 v navodilih (T-05). Meje modulov so koristno opozorilo za učilnico, niso popoln nadzor (T-04).

D12 je po registru **sprejet pri naročniku 13. 11. 2026**; mentorji so izvajalci in ga ne potrjujejo. Ponovna mentorska potrditev D12 ni pogoj, ki bi ga dodajal ta pregled. Ostajajo sprejem ugotovitev pri odgovornem človeku, pregled dostopnosti z bralnikom, organizacijski pogoji za vključitev ekip in poznejši preizkus pravih modulov iz točke 8. Naloge pred B oziroma produkcijo niso avtomatično razširjene v T.

### Izvedeni ukazi

`dc` spodaj pomeni `docker compose -p pregled-p0-tretji-openai` v ločenem worktreeju. Uporabljeni so samo lastni vsebniki in lasten volumen; obstoječa delovna okolja niso bila ustavljena.

```text
dc up --build -d --wait
  db, mail, p0, cleanup: Healthy
seed_test_data [SEED_PASSWORD ustvarjen s secrets.token_urlsafe]
  Testni nabor naložen.
dc exec -T p0 python manage.py test -v 2
  Ran 275 tests in 36.890s
  OK                         [brez preskokov]
dc build --no-cache p0
  Image pregled-p0-tretji-openai-p0 Built
ruff check .
  All checks passed!
ruff format --check .
  86 files already formatted
python manage.py makemigrations --check --dry-run
  No changes detected
python manage.py check
  System check identified no issues (0 silenced).
python -m pip check
  No broken requirements found.
python3 scripts/check_docs_links.py
  Notranje povezave in sidra so veljavni.
dc restart p0
  pred in po: 3 StubDelivery, 3 StubItem
dc down -v
dc up --build -d --wait
seed_test_data [novo naključno geslo]
dc exec -T p0 python manage.py test -v 2
  Ran 275 tests in 30.557s
  OK                         [brez preskokov]
dc down -v                  [končno čiščenje lastnega okolja]
```

Ponovni zagon potrdi ohranitev zapisov ob obnovitvi procesa, ne popolnosti njihove vsebine ali obnove varnostne kopije. Prvi neuspešni dostop Git je bil DNS peskovnika, prvi Docker dostop pa zavrnitev socketa; oba sta po odobrenem dostopu uspela. Pip je opozoril na nezapisljiv domači predpomnilnik in ga izklopil; `pip check` je uspel.

## 3. Tabela odprave drugega kroga

Za ponovitev vrstic s testi je ukaz `dc exec -T p0 python manage.py test <navedeni modul ali razred>`. Vsi navedeni testi so bili izvedeni v celotni zbirki; oznaka »odpravljeno« velja za ponovljeno reprodukcijo, ne za vse mogoče vhode. Kjer je stari protokol zamenjan, je naveden tudi novi ekvivalent.

| ID | Prejšnja resnost | Novo stanje | Lastni dokaz |
| --- | --- | --- | --- |
| OA R-01 | srednja | odpravljeno | `registry.tests.test_ponovni_api.DateTimeFormatTests`: prvotni datum `2099-01-01X00:00:00+00:00` in osem drugih neveljavnih oblik → 400; štiri veljavne oblike sprejete; enakost z validatorjem RFC 3339. |
| OA R-02 | srednja | odpravljeno | `ApiErrorEdgeTests`: preveliko telo ob DEBUG 0/1 → 400 JSON; `class_id="²"` z avtorjevo sejo → 403, brez 500. Staro servisno predogledovanje avtorja je zamenjano s sejo; več neveljavnih ID preverjenih tudi v novem protokolu. |
| OA R-03 | srednja | odpravljeno | `registry.tests.test_uvoz_zasloni.CsvLimitTests` in `ScreenErrorTests`: polje 131073 znakov, ime 201 znakov, predolg ključ in napaka parserja → `too_long`/`bad_csv`; zaslon 200 z napako, brez možnosti uveljavitve in brez delnega vpisa. |
| OA R-04 | srednja | odpravljeno | `PreviewPagingTests`: vseh 501 postavk dosegljivih po straneh, zadnja prisotna; nova sprememba za 500 nespremenjenimi vidna tudi s filtrom; stabilen vrstni red. |
| OA R-05 | nizka | odpravljeno | Chrome pri 320 × 900: stran iste testne osebe `scrollWidth=320`, ne več 325. Kontakt, seznam, uvoz, novi izvoz in /m1/, /m2/ ne razširijo strani. |
| OA R-06 | nizka | odpravljeno | `registry.tests.test_ponovni_api.CheckerUnknownPathTests`: prvotni `check_response('post', '/p0/api/v1/typo', 200, 'text/html', b'not JSON')` sproži `ContractViolation`; pomožne poti in health so izrecne izjeme. |
| OA R-07 | nizka | delno | Prvotne navedbe o viru kontakta, allauth, osnovnih zaslonih in Dependabotu so usklajene. Nove trenutne trditve o D12 in predaji ekipam si nasprotujejo (T-05); pregled dokumentov ni zgolj povzetek zapisa o odpravi. |
| OA R-08 | nizka | odpravljeno | `DiscardOutcomeTests`: dve seji, uveljavitev v prvi in zavrženje v drugi → stanje ostane applied, besedilo »Zavrženje ni bilo izvedeno«, brez lažnega »nič ni bilo spremenjeno«. |
| OA R-09 | visoka | odpravljeno za ponovljeno tekmo | `registry.tests.test_varovala_uvoza.ConcurrentRevocationTests`, vseh 10 uspe: ločene povezave PostgreSQL, oba vrstna reda, premaknjen začetek in vrsta, grant, zastarel zaslon, vse štiri poti. Uvoz/odvzem uporabljata isto poslovno ključavnico; po tekmi odvzeti obseg ostane zaprt. [Objavljeni nasvet](https://github.com/odprta-sola/solska-platforma/security/advisories/GHSA-mhxg-gwxv-32xw). |
| OA R-10 | srednja | odpravljeno | `UploadExpiryTests` (7) in `UploadPurgeTests` (1): meja ±1 µs, neposreden ogled/uveljavitev, iztek med branjem in zaklepom, mešana starost in čiščenje brez prometa. Rok se ne podaljša. Storitev cleanup obstaja. [Objavljeni nasvet](https://github.com/odprta-sola/solska-platforma/security/advisories/GHSA-99hv-w9pg-2mwj). |
| DS R-01 | nizka | odpravljeno | Isti časovno nadzorovani preizkusi kot OA R-10; datotek po roku ni mogoče uporabiti, neposreden dostop jih odstrani, ukaz jih čisti brez prometa. |
| DS R-02 | nizka | odpravljeno | `CsvLimitTests`: prvotni 300-znakovni prikazni podatek zajet z mejo 200; 65-znakovni ključ že zavrnjen zaradi sedanje meje 64. Brez `DataError` in brez delnega prepisa. |
| DS R-03 | nizka | odpravljeno | `ApiErrorEdgeTests.test_preveliko_telo_je_json`: 400 application/json, veljavna shema Error; DEBUG 0 in 1. |
| DS R-04 | nizka | odpravljeno | `ImportRestrictionTests.test_premaknjen_zacetek_granta` uspe brez mutacije. Ponovljena prvotna mutacija `_manual_revocation_at` samo za grant ga zdaj podre: manjka `('grants', 'manual_restriction')`. Ni več lažno zelen. |
| DS R-05 | nizka | odpravljeno | Ista dejanska ponovitev pri 320 px kot OA R-05; ni zgolj branje CSS ali test prisotnosti sloga. |
| DS R-06 | nizka | odpravljeno | `FutureValidityTests`: prihodnja povezava/grant → »še ne velja«, gumb za odvzem ostane; po odvzemu prihodnje dejanje zavrnjeno. Znana ograda +1 µs ostaja dokumentirana omejitev. |
| DS R-07 | nizka | ni odpravljeno; tveganje dokumentirano | Ponovljeni Trivy razvojne slike še vrne tri ista opozorila za vgrajeni setuptools 70.3.0 v pip: 1 visoko, 1 srednje, 1 nizko; produkcijska slika jih nima. Zapis o odpravi to razvrsti kot opombo, ne odstrani zadetkov. Splošne neizkoristljivosti nisem dokazal. |

Dodatno ponovno izvedeni `test_varovala` preverjajo S-02, S-03 in S-04; vse uspe. Za S-01 je začasna zapora zamenjana z delujočo vezavo na posnetek in namen. Osem `ContactContract` testov ter dodatna matrika potrdijo 200 za dovoljenega prejemnika in enak 403 za zavrnjene veljavne oblike vhoda. Stara nepravilna shema z `delivery_request_id` ne odpre kontakta. Neveljavna shema je še vedno 400; zahteva »enak 403« ne velja za napačno shemo ali neavtenticiran klic.

## 4. Nove javne ugotovitve

Varnostno občutljivi izsledki so v javni različici navedeni samo s številom in resnostjo v povzetku. Spodaj so funkcionalne, pogodbene in dokumentacijske ugotovitve.

| ID | Resnost | Kje | Opis, ponovitev, predlog |
| --- | --- | --- | --- |
| T-01 | srednja | `p0/stubs/models.py:12`, `p0/stubs/m1.py:114` | Trajni prevzem izgubi obvezna `params` in `target`. Oddajte veljavno dostavno zahtevo z različnima vrednostma teh polj, preberite `StubDelivery` in ponovno zaženite P0: model hrani template_id in hash celotne zahteve, nima pa vsebine params, ciljnega modula ali resource_id. Hash vsebine ne obnovi. Obstoječa testa trajnosti dokazujeta zapis glave/postavk in rollback, ne popolnega podatka za obnovitev dostave po C11. Nadomestek res ne pošilja pošte, vendar je ekipam predstavljen kot vedenjska referenca. Predlog: shraniti potrebno vsebino in dodati preizkus obnove s ponovnim branjem; ali izrecno omejiti pogodbeno dokazilo in zagotoviti ločen obvezen test za pravi M1. |
| T-02 | srednja | `p0/core/api_client.py:39`, `:62`, `:86`; `DEVELOPER.md` | Privzeti HTTP naslov ne ustreza Origin uporabniškega sejnega POST-a po dokumentiranem zagonu. S prijavo na `http://localhost:8000`, `UserSession.from_request` in privzetim `P0_API_URL=http://127.0.0.1:8000` pokličite `resolve_audience`: prava HTTP pot vrne 403 `csrf_failed`. Z istim veljavnim parom seja/CSRF in Origin `http://127.0.0.1:8000` vrne 200. HTTPS Origin proti notranjemu HTTP ima enak problem. GET /me in začetna zaslona zato delujeta, prvi uporabniški POST pa ne. Testni prenos/testserver ne preveri te razlike. Predlog: določiti in konfigurirati dovoljene zunanje izvore ter notranji naslov za isto namestitev; dodati integracijski preizkus dokumentiranega izvora. Ne reševati z izklopom CSRF. |
| T-03 | srednja | `p0/registry/tests/test_contract.py:602`, `api/zamrznitve.txt` | Test ne zagotovi nove različice ob vsaki spremembi pogodbe. Sam dodani komentar v YAML test pravilno podre; če preračunate in prepišete hash obstoječe vrstice **1.0.0**, isti test uspe brez nove različice. To je neposreden nasprotni primer trditvi v navodilih. Sedanja datoteka je sicer skladna z oznako v1.0.0 in zabeleženim SHA-256 `7c16a8eee671d229a29948ec6a5ee537a17d676500d53f8200457a99f05955fd`. Predlog: preveriti nespremenljivost že objavljenih vrstic proti osnovni veji oziroma izdajni oznaki in zahtevati nov version/hash za novo vsebino. |
| T-04 | nizka | `p0/core/tests/test_boundaries.py:13`, `docs/razvijalci/README.md` | Regex zazna le prvo ime v vrstici uvoza. `import os, registry.models` in `importlib.import_module('registry.models')` uspešno prestaneta `_check`, neposredni `from registry.models import Person` pade. Vodilna pika pri relativnem uvozu da prazen prvi segment in se prav tako ne normalizira; tak uvoz mora biti tudi dejansko veljaven v strukturi paketov, zato ni vsak primer s pikami izvršljiv. Za učno okolje je preverjanje koristno, trditev »pade ob prepovedanem uvozu« je preširoka. Predlog: AST za vse alias-e in razrešene relativne uvoze, dogovor o dinamičnih uvozih in človeški pregled; test ni meja med nezaupanja vredno kodo in podatki. |
| T-05 | nizka | `DEVELOPER.md`, `docs/projekt/stanje-prevzema-T.md`, `docs/projekt/d12-paket-za-odlocitev.md`, `docs/arhitektura/vmesnik-P0-M1-M2.md`, `docs/projekt/odvisnosti-in-licence.md` | Trenutna navodila nasprotujejo novi odločitvi naročnika. DEVELOPER pravi »Osnutek D12, ni potrjena«, pozneje isto pogodbo razglasi za zamrznjeno. Stanje T med vrzelmi prepoveduje vezavo ekip na osnutek, register in navodila ekip pa potrjujejo 1.0.0. Uvod paketa D12 pravi, da mentorji ne potrjujejo, nato »potrdita ... in mentorji«; tabela A hrani stara stanja in staro potrditev obeh mentorjev brez jasne zgodovinske ločitve. Pogodba govori hkrati o sprejeti pogodbi in o tem, da ni nadomeščena s potrjeno. Odvisnosti še navajajo D15 kot odprto licenco, čeprav obstaja CC BY-SA 4.0 in osebni sprejem; potrditev zavodov je ločena. Predlog: uskladiti sedanje normativne trditve in stare odstavke jasno označiti kot zgodovinske. Ne spreminjati starih poročil pregledovalcev. |

### Dodatna preverjanja nove izvedbe

- Kontakt: sedem kombinacij (neobstoječi posnetek, tuj/neobstoječi sklic ali prejemnik, točna meja izteka, potekel in izbrisan posnetek) je dalo enak status 403 in `{code: scope_not_allowed, message: ""}`; iz primerjave je izključen naključni trace_id. `ContactContract` dodatno preveri tuj dejanski posnetek, odvzem in namensko dovoljenje; `AudiencesContract` zavrne avtorja brez veljavne dodelitve. Samo ugibani sklic ni dovoljenje. Izčrpne analize časovnih kanalov ni bilo.
- Čiščenje posnetka: točna meja `<=`, člani odstranjeni; osebe, upravičenja in sklici ohranjeni. Dostava, ki se na posnetek sklicuje z nizom, po purge ostane v bazi. Novo razreševanje kontakta je zavrnjeno. Dolga čakajoča dostava po izteku posnetka potrebuje poslovno obravnavo; purge ne obnovi posnetka.
- Izvoz: devet projektnih testov potrdi vloge, POST, CSRF, odsotnost gesla, drugih kontaktov in tujih ID-jev v zajetih scenarijih, izvoz učenca, avtorja in starša ter sled pred izvozom. Dinamično dodan model `registry.ReviewNew` s FK na Person brez migracije je pravilno podrl `test_vsi_modeli_z_osebo_so_zajeti`. Ta test pregleda neposredne FK/OneToOne samo v registry, ne zazna poljubne vsebinske opustitve izvoza ali vseh posrednih povezav; pozitivni testi niso splošno potrdilo njegove popolnosti.
- D12 B: obdelava ima vrstni red iztek → negotova predaja → urnik → aktualna vezava/upravičenje → potreba → kontakt → jezik. Projektni testi potrdijo meje 7.00/20.00, vikend, oba prehoda poletnega časa, odvzem med čakanjem, odsoten kontakt, neznano potrebo, izklop M2, manjkajoč prevod in ročno odločitev po negotovi predaji. Tuj/potekel need_ref da 404 brez needed, ne »nepotreben«. Negotov preklic vrne too_late, postavi no_retry; iztek ohrani HANDOFF_UNCERTAIN. To ni dejanska SMTP predaja.
- Sočasnost M1: dodatni dve niti z ločenima povezavama sta namenoma ustavljeni tik pred `StubDelivery.objects.create`, po predhodnih preverjanjih. Isti ključ/vsebina: 202/202 z istim ID, en zapis in ena postavka. Različna ključa/isti dogodek: 202/409 duplicate_event, en zapis in ena postavka. S tem sta preverjeni tudi poti IntegrityError, ne samo zaporedni ponovitvi. Projektni test izpada bulk_create vrne 503, nič delno prevzetega; nova ponovitev 202.
- API odjemalec: projektni testi potrdijo servisni Bearer, posredovanje seje, CSRF zavrnitev, 5xx in ne-JSON kot Unavailable, zaprta vrata kot omrežno napako in zavrnitev file sheme. V kodi je timeout 5 sekund; mejnega časovnega preizkusa počasnega strežnika nisem izvedel. `P0_API_URL` prihaja iz okolja, obstoječi zasloni ga ne jemljejo iz parametra uporabniške zahteve; ni dokazan neposreden uporabniški SSRF prek te nastavitve. Dodatni občutljivi rezultati prenosa niso javni.
- Produkcijski način: pravi zagon z `DJANGO_DEBUG=0`, `STUBS=m1,m2` in potrebnim naključnim ključem se ustavi z ImproperlyConfigured. Pri praznem STUBS sta pomožni poti /m1/api/v1/_stub/process in /m2/api/v1/_stub/needs nerazrešljivi (404); projektni testi preverijo tudi preklop na pravi API. **Tri tabele stubs vseeno obstajajo**, ker je aplikacija stalno v INSTALLED_APPS in ima migracijo; komentar DEVELOPER to pravilno pove. STUBS omeji poti, ni odstranjevanje tabel ali ločena dovolilna plast baze.
- SECURITY: ukrepi is_active, odstranitev sej, deaktivacija ServiceClient in odvzem prek authz imajo ustrezne gradnike. To niso namenski incidentni ukazi ali dokaz izvedene vaje. `create_service_client` obstoječega imena ne rotira: tudi po deaktivaciji vrne `CommandError: Servisni račun že obstaja.` Nov žeton je treba izdati pod novim imenom in nastavitve modulov ustrezno zamenjati. Izbris vseh sej je po postopku zajezitev in ni izbris AccessAudit/ChangeAudit. Pravnega dosega 72 ur, pogojev obveščanja in zakonitosti obdelave nisem potrjeval; dokument je osnutek za šolo/DPO.
- CI licenciranja: DCO preveri prisotnost oblike vrstice, ne resničnosti izjave. Preverjanje avtorja bere seznam vzdrževalcev iz osnovne veje in ne dovoli samorazširitve seznama s PR; oznaka avtor-urejen in šolska izjava ostajata človeški postopek. Pregled ne potrjuje polnoletnosti ali pravic posameznih prispevajočih.

## 5. Rezultat preizkusa testov

Vsaka mutacija je bila izvedena posamično v kopiji `/tmp/openai-third`, pred naslednjo je obnovljena. Ukaz je `dc run --rm --no-deps -v <kopija-p0>:/app -v <kopija-api>:/api:ro p0 python manage.py test <test> -v 1 --noinput`. Izvirna zbirka je pred mutacijami zelena. Izpisi spodaj so dejanski, skrajšani za ponovljene poti, naključne ID-je in Dockerjevo pripravo.

| Mutacija | Izbrani test | Dejanski rezultat |
| --- | --- | --- |
| Odstranjen zapis record_view | `AccessAuditTests.test_vsak_zaslon_osebe_zapise_vpogled` | `Ran 1 test; FAILED (failures=4)`; `Lists differ: [] != [{...}]`, vsak od štirih podprimerov zazna manjkajočo sled. |
| Purge uporablja `<` namesto `<=` | `AudienceSnapshotPurgeTests.test_meja_roka` | `Ran 1 test; FAILED (failures=1)`; `AssertionError: 0 != 1`. |
| Odstranjen 30-dnevni prag replay | `IdempotencyWindowTests.test_okno_ponovitve` | `Ran 1 test; FAILED (errors=1)`; `KeyError: 'code'`, ker je vrnjen 202 namesto pričakovanega konflikta. Test mutacijo zazna, vendar bi bil neposredni assert statusa jasnejši. |
| Odstranjen zgodnji return za negotovo predajo | `UncertainHandoffTests.test_obdelava_ne_ponovi_sama` | `Ran 1 test; FAILED (failures=1)`; `('handed_off', None) != ('held', 'HANDOFF_UNCERTAIN')`. |
| Neznan need_ref postane NO_LONGER_REQUIRED | `NeedRefTests.test_neznana_potreba_zadrzi` | `Ran 1 test; FAILED (failures=1)`; `('cancelled', 'NO_LONGER_REQUIRED') != ('held', 'CHECK_UNAVAILABLE')`. |
| Odstranjen filter scope_ref pri vezavi kontakta | vseh 8 `ContactContract` | `Ran 8 tests; FAILED (failures=2)`; v obeh `AssertionError: 200 != 403`. To je mutacija varovala za že objavljeni S-01, ne nova javna reprodukcija ranljivosti. |
| Komentar dodan v zamrznjeni YAML | `SpecCoverage.test_pogodba_je_zamrznjena_razlicica` | `Ran 1 test; FAILED (failures=1)`; `pogodba se je spremenila brez nove različice`, hasha različna. |
| Isti komentar, posodobljen hash vrstice 1.0.0 | isti test | **`Ran 1 test; OK`**; brez nove različice. Lažno zelen dokaz za močnejšo trditev o zamrznitvi, T-03. |
| Samo grant varovalo vrne None (izvirni DS R-04) | `ImportRestrictionTests.test_premaknjen_zacetek_granta` | `Ran 1 test; FAILED (failures=1)`; `Items in the second set but not the first: ('grants', 'manual_restriction')`. |

Šest izbranih pravil iz nove izvedbe ima test, ki se ob odstranitvi pokvari. Preizkus zamrznitve zazna samostojno spremembo datoteke, ne pa prepisane zamrznitve z isto različico. To ni odstotek mutacijske pokritosti celotnega projekta.

## 6. Devet točk in dvajset skupin

### Devet točk kontrolnega seznama

»Pokrit« pomeni dokaz za navedeni referenčni obseg, ne človeškega prevzema ali odsotnosti napak.

| # | Točka | Ocena | Dokaz in razlika do odprave drugega kroga/stanja T |
| --- | --- | --- | --- |
| 1 | Lastni otroci, tuja družina | pokrit | UserEndpointsContract, AuthorizationCheckContract in testi družin v celotni zbirki; tuji/ugibani sklic zavrnjen. Novo brskalniško prijavo sem izvedel kot tajništvo; samostojnega ponovnega ročnega prijavljanja vsakega starša nisem izvedel. Ocena nespremenjena. |
| 2 | Skupen kontakt, ločena računa | pokrit | Modelni in prijavni testi ter pogodba; ločene osebe in pravice. Nespremenjeno. |
| 3 | Odvzem povezave/granta | pokrit | Neposredni in zaslonski testi, vseh 10 sočasnih testov; prvotna R-09 ne uspe. Nespremenjeno glede zapisa o odpravi, zdaj neodvisno izvedeno. |
| 4 | CSV, ponovitev, sled | pokrit | test_import, test_varovala, test_uvoz_zasloni; tudi celoten predogled in pravilno zavrženje. Nespremenjeno. |
| 5 | Kontakt vezan na zahtevo/prejemnika | pokrit za C07 | Dejanski shranjeni posnetek in trenutna namensko pravilna pravica, matrika 403 in ContactContract. **Napredek** od varne zapore 503 v drugem krogu; stanje T za ta del pravilno navaja izvedbo. |
| 6 | Neodvisen pregled kode | delno | Pregled z drugim AI izveden, prejšnji poročili ne nadomestita branja. Človeški pregled/sprejem ni izveden. Enaka formalna omejitev kot prej. |
| 7 | Ponastavitev in pogodbeni testi | pokrit | Po down -v ponovni zagon in celotnih 275 testov, vključno s pogodbo in robnimi primeri. Širši izvedeni obseg kot prej, ista ocena. |
| 8 | Izpad P0, zaščiteno dejanje/dostava | delno | Novi HomeTests zavrnejo začetni zaslon s 503, API odjemalec zavrne omrežno napako, nadomestek zadrži neznano potrebo. **Delni napredek**; pravi zaščiteni poslovni postopek in SMTP ne obstajata. Po registru ta točka čaka prava modula; ni izpolnjena v celoti. |
| 9 | Dostopnost | delno | Ponovitev v Chromu, 320 px in novi izvoz ter /m1/, /m2/; bralnik in človeška razumljivost nista izvedena. Stara napaka prelivanja odpravljena, formalno merilo ostaja odprto. |

### Dvajset skupin kratke specifikacije

| # | Skupina | Ocena | Dokaz, meja in razlika |
| --- | --- | --- | --- |
| 1 | Dva računa z istim kontaktom | delno | P0 identitete/pravice pokrite; odzivi M2 in individualna aktivacija še ne. Enako. |
| 2 | Druga družina, ugiban ID/sklic | delno | Kontaktna in avtorizacijska matrika uspe; vseh podatkovnih poti in bodočih modulov ne potrjujem. Enako. |
| 3 | Zaposleni zunaj oddelka | delno | Avtorjeva seja in aktivna dodelitev preverjeni, prava objava še manjka. Enako. |
| 4 | Učenčev račun/ciljna skupina | ni v obsegu T | Pogojena razširitev. Enako. |
| 5 | Povezava brez granta in odvzem | pokrit | Dejanska avtorizacija v modelnih/pogodbenih testih ter odvzem. Enako. |
| 6 | Starejši uvoz po ročni omejitvi | pokrit | Poslovni obseg, grant mutacija in dejanska tekma PostgreSQL; ne obnovi pravice. Potrjena ocena zapisa o odpravi. |
| 7 | Napačen CSV/referenca | pokrit | Validacija, parser, meje in atomska uveljavitev brez delnega vpisa. Potrjena ocena zapisa. |
| 8 | Ponovitev, dvojnik, manjkajoča vrstica | pokrit | IdempotencyTests in uvozni testi; stabilni ključi, ni samodejnega odvzema manjkajoče vrstice. Enako. |
| 9 | Aktivacija/obnova skupnega predala | ni v obsegu T | Začasna zapora ostane; individualni postopek pred B. Enako. |
| 10 | Seja, CSRF, podtaknjen uporabnik, servis | pokrit za P0 | Pogodbeni testi, avtor iz dejanske seje, ne iz ID servisa; invalid Bearer ne preide na sejo. **Iz delno v pokrit** za osnovno P0 merilo po D12; odjemalčeva integracijska napaka T-02 ostaja posebej odprta in ni potrjena končna integracija. |
| 11 | M1: odprtje/seznanitev | ni v obsegu T | Poslovna implementacija M1. Enako. |
| 12 | M1: dva otroka/različica | ni v obsegu T | Poslovna implementacija M1. Dostavna postavka je zdaj par oseba/obseg. |
| 13 | M2: nameni, Ne/brez odziva | ni v obsegu T | Poslovna implementacija M2. Enako. |
| 14 | M2: dva otroka/odločevalca | ni v obsegu T | Poslovna implementacija M2. Enako. |
| 15 | M2: odobrena različica | ni v obsegu T | Poslovna implementacija M2. Enako. |
| 16 | M2: sprememba/preklic/zgodovina | ni v obsegu T | Poslovna implementacija M2. Enako. |
| 17 | Izpad, izgubljen 202, ključi/dogodek | delno | Trajna glava/postavke, izpad zapisa in obe sočasni poti preverjeni; vsebina zahteve nepopolna (T-01), trajne namere pravega M2 in izgubljenega HTTP odgovora nisem preizkusil. Ocena ista, dokaz močnejši. |
| 18 | Potreba, selektivni preklic, izpadi, urnik, iztek | delno | NeedRefTests, QuietHoursTests in preklic po item_id; izklop M2 zadrži. Pravi HTTP izpad P0/M2 med dostavo in razporejevalnik manjkajo. Ista ocena, napredek po B. |
| 19 | Negotov SMTP, odvzem med dostavo, obnova | delno | **Iz nepokrit v delno:** UncertainHandoffTests, AuthorizationAtActionTests in ponovni zagon preverijo stanje/pravilo reference. Dejanske negotove SMTP predaje in obnove kopije ni; tega ne označujem za pokrito. |
| 20 | Sveža namestitev, nadomestki, izvoz, dostopnost | delno | Gradnja brez predpomnilnika, ponastavitev, 275 testov, izvoz in Chrome; človeški pregled z bralnikom manjka. Ista ocena, širši dokaz. |

Skupaj **5 pokritih / 7 delnih / 0 nepokritih / 8 zunaj obsega T**. Zapis o odpravi drugega kroga ima 4/7/1/8. Razliki sta skupini 10 (po D12 pokrit osnovni P0 protokol) in 19 (zdaj delno preizkušeno obnašanje reference). Nobena druga skupina ni brez pojasnila zvišana. Stanje T pravilno opozarja na odsotnost prave pošte in človeškega bralnika, njegova vrstica o nepotrjenem D12 pa je zastarela (T-05).

### Dostopnost brez bralnika zaslona

Prava prijava v Chromu z naključnim geslom, viewport 320 × 900. Preverjene strani: prijava, seznam oseb, podrobnosti, kontakt, uvoz, /m1/ in /m2/. Vsaka je vrnila 200, `lang=sl`, en h1, eno main, nobenega vidnega vnosnega polja brez oznake; `document.documentElement.scrollWidth=320` pri `innerWidth=320`.

Prvi Tab doseže »Preskoči na vsebino« z obrobo 3 px. Prazna prijava premakne fokus na `#napake`, dve polji imata aria-invalid. Neveljaven kontakt prav tako premakne fokus na `#napake`, eno polje je označeno kot napačno. Novi gumb za izvoz ima opisno ime, dosegljiv fokus z obrobo 3 px in širino 288 px na 320 px strani. Pregledane so povezave oznak/napak in semantične regije; osnovni testi strukture in napak uspejo.

Ta ponovitev ni zajela celotnega vrstnega reda Tab vsakega zaslona, dejanskega prenosa izvoza samo s tipkovnico, vseh potrditvenih zaslonov pri 320 px ali celotnega uvoza z izbirnikom datotek. Te poti imajo projektne funkcionalne teste. **Bralnik zaslona, povečava 200/400 %, izračun kontrasta in razumljivost z uporabnikom: ni izvedeno**; potreben je človek in ustrezno orodje. Sam HTML ali uspešen Playwright ni tak pregled.

## 7. Odvisnosti

Ponovljeni `pip-audit` 2.10.1 za vsak od treh zaklepov z `--disable-pip --no-deps -r <zaklep> --format json`:

```text
requirements.lock        No known vulnerabilities found
requirements-dev.lock    No known vulnerabilities found
requirements-build.lock  No known vulnerabilities found
```

To je preverjanje paketov točno navedenih v zaklepih, ne vseh datotek slike. Zaklepi in digesti se od drugega kroga niso spremenili; gradnja s hashi in pip check sta uspela. Opozorilo pip-audit o --no-deps ni zadetek ranljivosti; zaklepi vsebujejo tudi posredne odvisnosti. Napačnega hasha tokrat nisem posebej ponovno vnašal.

Trivy 0.76.2 je prenesel svežo bazo in skeniral izvoza slik iz pregledane kode. Razvojna slika je zgrajena z zahtevanim `build --no-cache p0`; produkcijska z `INSTALL_DEV=0`.

| Cilj | Rezultat tega pregleda | Primerjava z dokumentacijo |
| --- | --- | --- |
| Produkcijska P0 | 205 Debian: 47 visokih, **89 srednjih**, 65 nizkih, **4 neznane**; 0 s popravkom; Python 0 | Skupno število in odsotnost popravkov enaka; dokument ima 74 srednjih/19 neznanih. Razvrstitev 15 zadetkov se je s svežo bazo spremenila. |
| Razvojna P0 | Isti Debian + 3 Python/setuptools: 1 visoko, 1 srednje, 1 nizko, vsa s popravkom | Potrjuje preostanek DS R-07 in opombo o vgrajenem pkg_resources v pip. |
| PostgreSQL in Mailpit | ni ponovno skenirano | Zahtevano dodatno skeniranje slike je izvedeno za obe različici P0; rezultatov drugih dveh slik iz starega poročila ne predstavljam kot lastne nove meritve. |

Produkcijska slika v tej gradnji: `sha256:6673cb405e1b6ee15dd8d3645de63899ba8d084ae73209501ecc49b00edf3953`. Slike so uporabljene lokalno in niso objavljene. Zadetki skenerja niso dokaz izkoristljivosti ali neizkoristljivosti.

Licenčni popis glavnih paketov se po nespremenjenih zaklepih ujema: Django/asgiref/sqlparse BSD-3-Clause, allauth/gunicorn MIT, psycopg LGPL-3.0-only. Projektna koda je EUPL 1.2; dokumentacija ima LICENSE-dokumentacija.md, CC BY-SA 4.0, kar del trenutnega popisa še napačno označi kot odprto odločitev. **SBOM, točne različice/licence vgrajenih binarnih knjižnic psycopg in celovita presoja distribucije slike: ni izvedeno**; to ostaja pred distribucijo, kakor določa register. Ne potrjujem pravne skladnosti zgolj iz oznak licenc ali zelene baze CVE.

## 8. Omejitve pregleda

- Pregled je opravil Codex (OpenAI). Odgovorni človek poročila še ni sprejel. Ni izvedena forenzična presoja avtorstva, veljavnosti DCO ali šolskih izjav.
- Pregled je vezan na d261ace. Novejši main, poznejši popravki in njihovi CI niso pregledani. Isti uspeh v dveh namestitvah na istem stroju ni dokaz reproducibilnosti na drug dan ali platformi.
- Prvotne programske reprodukcije drugega kroga so ponovljene z imenovanimi regresijskimi testi, katerih koda je bila prebrana; 320 px je ponovno izmerjen v brskalniku. Samostojnega novega skripta za prav vsak stari test ni bilo. Dokumentacijski ugotovitvi nimata avtomatskega dokaza in sta presojeni z branjem sedanjih datotek.
- Prvotni dodatni skript za meje modulov je imel ValueError zaradi relative_to zunaj /app. Popravljeno je samo pregledovalčevo začasno ogrodje in preizkus ponovljen. Prvi produkcijski podpreizkus s praznim STUBS ni imel obveznega gesla zbirke; ponovljen z obstoječo razvojno konfiguracijo. Prvi klic dodatnega preverjanja rotacije je uporabil napačno ime argumenta scope; končni klic uporablja --scope. To niso napake izdelka ali padci projektne zbirke.
- Človeški bralnik zaslona, razumljivost, celotna tipkovnična opravila in kontrast: ni izvedeno iz razlogov, navedenih pri dostopnosti.
- Prava poslovna M1/M2, SMTP, dejanski izpad P0 med pošiljanjem, izgubljen HTTP 202, obnova kopije, prazniki in periodični dostavni delavec: ni izvedeno, ker implementacije oziroma namestitve še ni. Preizkus ponovnega zagona procesa in umetno sočasna prevzema imata ožji pomen.
- Produkcijski HTTPS/proxy, pravilni zaupanja vredni izvori, časovni pragi počasnega HTTP strežnika, izčrpni časovni kanali, obremenitev/fuzzing, vse napake in vse poti admina niso izčrpno preverjeni.
- Tabele nadomestkov v produkcijskem načinu ostajajo prisotne; preverjena je blokada njihovega HTTP usmerjanja, ne ločen uporabnik baze ali odstranitev aplikacije stubs.
- Mehanizma cleanup nisem čakal 24/30 dni: uporabljeni so nadzorovana ura, robni testi in izvedba ukazov. Najpoznejši izbris predpostavlja delujočo storitev oziroma produkcijski razporejevalnik; odpoved gostitelja lahko to zagotovilo prekine.
- Celovit pravni pregled postopka kršitve, podlag obdelave, licenc in distribucije ni izveden; dokumentacija je tehnično primerjana z izvedbo, ne pravno potrjena.
- Javno poročilo ne vsebuje novih občutljivih reprodukcij. Lokalne dokaze dobi pobudnik v pogovoru; niso poslani drugim osebam ali objavljeni kot issue/komentar.

## 9. Izjava

Ta pregled **ni človeški prevzem in ni pravno mnenje**. Ne potrjuje produkcijske pripravljenosti, pravic prispevkov ali sprejema ugotovitev v imenu Mitje Piriha. Uspešnih 275 testov ne nadomesti preostalih pogojev T in človeške odločitve o predaji ekipam.
