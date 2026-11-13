# Tretji neodvisni pregled P0 – paket T (DeepSeek)

Pregledani commit: `d261ace2902a13788b4a36f75399ebc20eb400a9`. Ob začetku pregleda je bil `main` na `ac6bc18cc7ea5b2df096b4d92d56f2f6baf1baee`; razlika do pregledanega commita je samo dokumentacija navodila za tretji pregled (`docs/projekt/navodilo-za-tretji-pregled.md`, `docs/projekt/navodilo-za-ponovni-pregled.md`), koda P0 se ne spremeni. Pogodba je označena z `v1.0.0`; oznaka kaže na `68fea198176d7fe26660dbfb9eddb1a8fee14c8e`.

## 1. Podatki

| Podatek | Vrednost |
| --- | --- |
| Datum pregleda | 13. november 2026, Europe/Ljubljana |
| Repozitorij | https://github.com/odprta-sola/solska-platforma |
| Pregledani commit | `d261ace2902a13788b4a36f75399ebc20eb400a9` |
| `main` ob začetku | `ac6bc18cc7ea5b2df096b4d92d56f2f6baf1baee` (samo dokumentacija navodila) |
| Pogodba | `v1.0.0` -> `68fea198176d7fe26660dbfb9eddb1a8fee14c8e`; SHA-256 `api/openapi.yaml` = `7c16a8eee671d229a29948ec6a5ee537a17d676500d53f8200457a99f05955fd` |
| Pregledovalec | DeepSeek (orodje DeepSeek Harness); ponudnik DeepSeek; različica modela ni znana in je ne ugibam |
| Odgovorni človek | Mitja Pirih; njegov sprejem tega poročila ob pripravi **ni potrjen** |
| Gostiteljski OS | Ubuntu 24.04.5 LTS, Linux x86_64, jedro 7.0.0-113042-tuxedo |
| Docker / Compose | Docker 29.9.3 (build 5457199) / Docker Compose v5.7.0 |
| Python | gostitelj 3.12.3; aplikacijski vsebnik 3.12.16 |
| Aplikacijski vsebnik | `python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b` (Python 3.12.16, Debian 13.7); zgrajena slika `odprta-sola-p0:latest`, ID `sha256:0ce44d3dccca2d765787ce8ea7605e0232275d311f47a14b06e006afbf1a3080` |
| Django | 5.2.19 |
| psycopg | 3.3.9 |
| Podatkovna zbirka | PostgreSQL 16.15 (digest `sha256:f9a7b9ebf6f56201f949db745e47bc423c0f0f8294bafe991cc10bf74b029657`) |
| Poštni predal | Mailpit v1.33.1 (digest `sha256:aef2aacc11f075ec0fb6874275ee4a421e688e11a96ebb296134d1735c7761ce`) |
| Brskalnik | Google Chrome 157.0.8103.38 (headless, CDP), brez bralnika zaslona |
| Orodji | `pip-audit` 2.10.1; Trivy 0.76.2 (`aquasec/trivy@sha256:8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb`), baza OSV/Trivy osvežena 13. 11. 2026 |
| Produkcijska slika za skeniranje | `odprta-sola-p0-prod:review3`, ID `sha256:6673cb405e1b6ee15dd8d3645de63899ba8d084ae73209501ecc49b00edf3953` |

### Razkritje neodvisnosti in izvora

Pregledovane kode **nisem napisal**. Po navodilu pobudnika in projektni dokumentaciji je kodo faz 0 do 6 napisal **Claude Sonnet 5.5**, poznejše popravke in dopolnitve pa **Claude Opus 5.5** (oba Anthropic), po navodilih pobudnika. Navedba izvora ni forenzična potrditev avtorstva.

Poročili DeepSeek prvega in drugega kroga je napisal isti sistem, zato ta tretji pregled **ni neodvisen od teh dveh poročil DeepSeek**; je pa drug sistem AI glede na pisca kode. Poročilo OpenAI/Codex drugega kroga sem prebral in ga upošteval. Pregled ni institucionalno neodvisen in ni človeški prevzem. O sebi ne ugibam: sistem je DeepSeek, ponudnik DeepSeek, različice modela ne navajam.

### Kaj je bilo prebrano

Poročili drugega kroga ([OpenAI](2026-11-ponovni-pregled-P0-openai.md), [DeepSeek](2026-11-ponovni-pregled-P0-deepseek.md)), zapis o odpravi ([prvi](2026-11-odprava-prvega-pregleda-P0.md), [drugi](2026-11-odprava-ponovnega-pregleda-P0.md)), kontrolni seznam, stanje T, kratka specifikacija, register odločitev, paket D12, pogodba in OpenAPI, pregled dostopnosti, odvisnosti in licence, varstvo podatkov, `DEVELOPER.md`, `SECURITY.md`, `CONTRIBUTING.md`, `.github/`, `docker-compose.yml`, `p0/Dockerfile` in vsa nova koda PR #56 do #65 ter pripadajoči testi. Prebrani so bili tudi objavljeni varnostni nasveti S-01 do S-04, R-09 in R-10 prek javnega GitHub API.

## 2. Povzetek

**Priporočilo za celoten prevzem T: ne.** Jedro P0 po tem krogu priporočam **pogojno** za nadaljnje delo ekip, celotnega prevzema T pa še ne: točka 8 ni preverljiva brez pravih M1/M2, točka 9 nima človeškega pregleda z bralnikom zaslona, nova zasebna ugotovitev T-01 je srednja, pred uporabo pravih podatkov pa je treba urediti še upravljanje skrbniškega vmesnika in sledi (T-04/T-05).

**Kaj je potrjeno:** vseh **275 testov** je uspešnih, **0 preskočenih**; meje modulov M1/M2 se zdaj res izvajajo. Po `docker compose down -v`, ponovni namestitvi in `seed_test_data` je vseh 275 testov ponovno uspešnih; pogodbeni, robni in zaslonski sklop je **100/100**. S-01 do S-04, R-09 in R-10 ostajajo odpravljeni po lastni ponovitvi. Kontakt je vezan na posnetek občinstva in aktualno upravičenje; tuj, neobstoječ, potekel, izbrisan in odvzet vhod vrnejo enak 403. Širina 320 px je popravljena tudi z 80-znakovnim e-naslovom; `/m1/` in `/m2/` sta brez prelivanja. Nadomestka po točkah B hranita stanje v bazi in imata trajni zapis pred 202, okno ponovitve, poslovni ključ in obdelavo po urniku.

**Kaj ostaja:** točka 8 (prava M1/M2 in izpad), točka 9 (človeški pregled z NVDA/Orca, povečava, kontrast), D09/D14 (pisni sprejem namestnika), D08 (pravni pregled obrazca za mladoletne), SBOM in pravni pregled distribucije, HSTS/HTTPS ob D04, produkcijski razporejevalnik čiščenja. Nove javne ugotovitve so tri srednje (T-04, T-05, T-08) in več nizkih; ena zasebna srednja (T-01). Ni novih kritičnih ali visokih ugotovitev.

**Ali so navodila in ogrodje dovolj zanesljiva, da ekipi začneta delo?** **Pogojno da.** Pogodba `1.0.0`, nadomestka, pogodbeni testi, `core/api_client.py` in ogrodji `p0/m1`/`p0/m2` so uporabna izhodišča. Pred začetkom je treba popraviti dokumentacijo, ki še vedno govori, da D12 ni potrjena (T-08), in vsaj T-01 (zasebno) ter T-07 (meja modulov je obhodljiva); T-04/T-05 pa pred uporabo pravih podatkov. Brez tega bi dijaki delali po nasprotujočih si navodilih, ekipe pa bi lahko obšle mejo modulov.

## 3. Tabela odprave drugega kroga

»Odpravljeno« pomeni, da sem prvotno reprodukcijo ali njen novi ustreznik ponovil na `d261ace` in ni več uspešen. »Delno« pomeni, da je prvotni primer odpravljen, a ostaja vsebinska ali dokumentacijska vrzel. Ocen iz zapisa o odpravi nisem prepisal brez lastnega zagona.

### 3.1 Objavljene varnostne ugotovitve

| ID | Prejšnja resnost | Novo stanje | Dokaz |
| --- | --- | --- | --- |
| [S-01](https://github.com/odprta-sola/solska-platforma/security/advisories/GHSA-h7jp-rfj3-89xr) | visoka | **odpravljeno po D12 C07** | `ContactContract` 8/8, `AudiencesContract` 8/8, `test_ciscenje_posnetkov` 5/5. Kontakt se vrne samo za člana neizteklega posnetka z ujemajočim `scope_ref`, veljavnim `ScopeRef` in aktualnim grantom za namen posnetka; tuj, neobstoječ, potekel, izbrisan in odvzet vhod -> 403 `scope_not_allowed` brez e-naslova. Vezava je na posnetek občinstva, ne na posamezno dostavno zahtevo; to je sprejeta izvedba D12 C07. |
| [S-02](https://github.com/odprta-sola/solska-platforma/security/advisories/GHSA-8h4f-w469-mr34) | visoka | **odpravljeno** | `test_varovala.ImportRestrictionTests` in `test_varovala_uvoza.ConcurrentRevocationTests` (18/18 skupaj z R-10); ročni odvzem povezave ali granta, premaknjen začetek, druga vrsta in oboje -> `manual_restriction`, serija zavrnjena, vse štiri poti zavrnejo. |
| [S-03](https://github.com/odprta-sola/solska-platforma/security/advisories/GHSA-gfrq-669g-95fq) | visoka | **odpravljeno** | `PasswordRecoveryTests` 6/6: vse poti pod `/accounts/password/reset/` vrnejo 404, tudi veljaven prej izdan ključ allauth; `send_password_reset_mail` ne pošlje ničesar; prijava ne kaže povezave. Individualna obnova ostaja pred B. |
| [S-04](https://github.com/odprta-sola/solska-platforma/security/advisories/GHSA-42r3-qhw4-9xx2) | srednja | **odpravljeno** | `ImportRoleTests` 6/6: tajništvo ne dodeli `admin`/`office`; skrbnik sme; ponovni uvoz obstoječe vloge je dovoljen; ob odstranitvi varovala 2/6 testov padeta. |
| [R-09](https://github.com/odprta-sola/solska-platforma/security/advisories/GHSA-mhxg-gwxv-32xw) | visoka | **odpravljeno** | `test_varovala_uvoza` 18/18: 10 sočasnih scenarijev z ločenimi povezavami PostgreSQL, oba vrstna reda, zastarel zaslon, vse štiri poti; brez ključavnice test pade. |
| [R-10](https://github.com/odprta-sola/solska-platforma/security/advisories/GHSA-99hv-w9pg-2mwj) | srednja | **odpravljeno** | `UploadExpiryTests` + `UploadPurgeTests` (8/8): meja ±1 µs, ogled ne podaljša roka, neposredna uveljavitev po izteku zavrnjena, mešana starost ne omogoči delnega uvoza, čiščenje brez prometa je ponovljivo. |

### 3.2 Ugotovitve poročila OpenAI (drugi krog)

| ID | Prejšnja resnost | Novo stanje | Dokaz |
| --- | --- | --- | --- |
| P0-01 | srednja | **odpravljeno** | `RequestValidation` + `RequestSchemaParity`: manjkajoče/dodatno/ugnezdeno polje, napačen tip, prazen in predolg niz, napačen JSON -> 400; `DateTimeFormatTests` 13 zapisov, enakost z validatorjem pogodbe. |
| P0-02 | srednja | **odpravljeno** | `ApiErrorContract`, `ApiErrorEdgeTests`: preveliko telo -> 400 JSON, `class_id="²"` -> 400/403 JSON, 503 brez `allowed`, 405 z `Allow`, 500 brez podrobnosti, seja brez CSRF -> 403 JSON. |
| P0-03 | srednja | **odpravljeno** | D12 C12: postavka je `(person_id, scope_ref)`, `item_id` na postavko; ponovljen par -> 400 `duplicate_recipient`; ista oseba z dvema obsegoma sta dve postavki (`DeliveryStubContract`, `test_d12_tocke_b`). |
| P0-04 | opomba | **odpravljeno** | `IdempotencyWindowTests`: isti ključ in vsebina 29 dni -> isti prevzem 202; ob 30 dneh -> 409 `replay_window_expired`; po `expires_at` isti prevzem brez podaljšanja. |
| P0-05 | srednja | **odpravljeno** | `PreviewApplyTests` 5/5 in `ConcurrentApplyTests` 1/1; sprememba po predogledu -> `preview_stale`; dve sočasni uveljavitvi -> ena uspe; napaka ne pusti delnih zapisov. |
| P0-06 | srednja | **odpravljeno** | `CheckerUnknownPathTests` + `CheckerSelfTest`: neznana pot API zdaj dvigne `ContractViolation`; `format_checker` je vključen; pomožne poti so izvzete izrecno. |
| P0-07 | srednja | **odpravljeno** | Preimenovana testa preverjata tuji preklic in ročni iztek; `test_povezava_sama_ne_podeli_pravice` kliče `authz`; meji M1/M2 se zdaj izvajata (0 preskočenih). Točka 8 s tem ni pokrita. |
| P0-08 | srednja | **odpravljeno v okviru nadomestka** | `p0/stubs/models.py`, migracija `0001_stub_state`; `DurabilityTests` (izpad `bulk_create` -> 503, nobene vrstice; ponovitev -> 202). Pravi M1/M2 in prava pošta nista izvedena. |
| P0-09 | nizka | **delno** | Dokumentacija je večinoma posodobljena, a ostajajo trditve, da je D12 osnutek, in zastareli statusi (T-08). |
| P0-10 | srednja | **delno** | 320 px je popravljen (izmerjeno 305/320), fokus, oznake in napake delujejo; bralnik zaslona, povečava 200/400 % in kontrast niso izvedeni. |
| P0-11 | nizka | **delno** | Zaklepi, digesti, `pip-audit` in Trivy so ponovljeni; SBOM, pravni pregled in vgrajene knjižnice `psycopg-binary` ostajajo odprti; razvojna slika ima 3 opozorila `setuptools`. |
| R-01 | srednja | **odpravljeno** | `DateTimeFormatTests`: `2099-01-01X...` in drugi neveljavni zapisi -> 400; `parse_date_time` se ujema s pogodbenim `format: date-time`. |
| R-02 | srednja | **odpravljeno** | `ApiErrorEdgeTests`: preveliko telo je JSON 400 v DEBUG in brez; unicode števke v `class_id` niso več 500. |
| R-03 | srednja | **odpravljeno** | `CsvLimitTests` + `ScreenErrorTests`: polje nad mejo razčlenjevalnika -> `too_long`/`bad_csv`, ne 500; dolžine po modelih, meje dovoljene. |
| R-04 | srednja | **odpravljeno** | `PreviewPagingTests`: vseh 501 postavk dosegljivih po straneh, filter sprememb, stabilen vrstni red; gumb za uveljavitev ostane le ob celotnem predogledu. |
| R-05 | nizka | **odpravljeno** | Headless Chrome 157, 320 × 900: `documentElement.scrollWidth` = 305 pri osebi tudi z 80-znakovnim e-naslovom; tabela se drsi znotraj `.tablewrap`, stran ne. |
| R-06 | nizka | **odpravljeno** | `CheckerUnknownPathTests.test_neznana_pot_api_pade`; neznana pot API ni več tiho preskočena. |
| R-07 | nizka | **delno** | Nekatere dokumentacijske nedoslednosti so odpravljene, druge ostajajo (T-08); glej tudi T-11. |
| R-08 | nizka | **odpravljeno** | `DiscardOutcomeTests`: zavrženje po uveljavitvi ali ponovno zavrženje prikaže dejansko stanje, ne lažnega uspeha. |

### 3.3 Ugotovitve poročila DeepSeek (drugi krog)

| ID | Prejšnja resnost | Novo stanje | Dokaz |
| --- | --- | --- | --- |
| P0-01 | srednja | **odpravljeno** | `person_by_id` ujame `ValueError`, `TypeError` in `ValidationError`; neveljaven UUID v `authorizations/check` -> 200 `NOT_ALLOWED`, v `audiences/resolve` -> 400/403; `ApiErrorContract` brez 500. |
| P0-02 | opomba | **odpravljeno** | `delivery_contact` zahteva člana posnetka, ujemajoči `scope_ref`, veljaven `ScopeRef` in aktualni grant za namen posnetka; katerokoli upravičenje ne zadošča več (`ContactContract.test_upravicenje_mora_ustrezati_namenu_posnetka`). |
| P0-03 | srednja (že dokumentirano) | **odpravljeno** | Enako kot S-03: poti 404, adapter ne pošlje, prijava brez povezave; individualni postopek ostaja pred B. |
| P0-04 | opomba | **odpravljeno** | Preklic tuje zahteve je 404 (`test_preklic_tuje_zahteve_je_404`); ročno nastavljen iztek je končno stanje; imena testov ustrezajo vedenju. |
| P0-05 | nizka | **ni odpravljeno, odloženo** | `manage.py check --deploy` še vrne W004 (HSTS) in W008 (HTTPS); `CSRF_TRUSTED_ORIGINS` ni določen. Odločitev je pri D04; ni nova blokada lokalnega T. |
| P0-06 | nizka | **odpravljeno** | Izvedba potrjuje 275 testov in 0 preskočenih; dokumenti, ki navajajo 173/214, so zgodovinski, trenutno stanje pa je treba še zapisati (T-08). |
| R-01 | nizka (zasebna) | **odpravljeno** | `p0/registry/uploads.py`, `purge_import_uploads`, `UploadExpiryTests`/`UploadPurgeTests`: rok 24 h od najstarejše datoteke, preverjen ob ogledu, uveljavitvi in v transakciji; brez prometa cleanup vsako uro. Podrobnosti ostajajo zasebne. |
| R-02 | nizka | **odpravljeno** | `CsvLimitTests`, `ScreenErrorTests`; dolžine po modelih in `too_long`, ne `DataError`/500. |
| R-03 | nizka | **odpravljeno** | `ApiErrorEdgeTests.test_preveliko_telo_je_json`; JSON 400 tudi v DEBUG in brez. |
| R-04 | nizka | **odpravljeno** | `test_premaknjen_zacetek_granta` zdaj pade ob onemogočenem grantovem varovalu (2/2 padeta skupaj s `test_odvzem_enega_dovoljenja_ne_vpliva_na_drugega`). |
| R-05 | nizka | **odpravljeno** | 320 px meritev zgoraj; `dl.facts` ima `minmax(0, 1fr)` in `overflow-wrap: anywhere`; tudi `/m1/`, `/m2/` sta 320. |
| R-06 | nizka | **odpravljeno** | `FutureValidityTests`: prihodnja povezava in grant -> „še ne velja“, odvzem prihodnjega zapisa je mogoč in ga zaključi po začetku. |
| R-07 | nizka | **ni napaka; opomba** | Razvojna slika ima 3 opozorila `setuptools` (CVE-2025-47273 visoka, CVE-2026-59890 srednja, GHSA-xmj3-9gf7-h52w nizka); produkcijska slika ima 0 paketov Python. Dokumentacija to že opisuje. |

### 3.4 Kontakt, posnetek in varstvo podatkov – povzetek preveritev

- **Ugibanje.** `audience_ref` in `scope_ref` sta `secrets.token_urlsafe(16)` (približno 128 bitov), `recipient_id` je UUID; brez poznavanja posnetka ju ni mogoče praktično uganiti. Vsi neveljavni vhodi vrnejo enak 403; nisem pa izvedel obremenitvenega ali časovnega preizkusa, zato časovnih kanalov ne izključujem.
- **Avtor posnetka.** `audiences_resolve` zahteva `StaffAssignment.objects.active(now)` za osebo iz seje in izbrani oddelek; `test_zaposleni_zunaj_oddelka_zavrnjen` vrne 403 in ne ustvari posnetka. Posnetek za oddelek brez veljavne dodelitve ni mogoč; prihodnja dodelitev se ne šteje.
- **Brisanje posnetkov.** `purge_expired` izbriše posnetke z `expires_at <= now` in njihove člane; meja je preverjena na ±1 µs. V ločenem testu sem ustvaril čakajočo dostavo, nato posnetek potekel in izbrisal: obdelava je postavko zadržala (`held`, `NOT_ALLOWED`), ni bilo tihega uspeha ali kontakta.
- **Sled vpogledov.** Podrobnosti osebe, kontakt, potrditev odvzema in predogled uvoza zapišejo `AccessAudit` pred prikazom; brez zapisa ni prikaza (`test_brez_zapisa_ni_prikaza`). Sled ne hrani vsebine, iskalnega niza, IP ali brskalnika. Seznam oseb in `/admin/` ostaneta brez zapisa (T-04); dokument `varstvo-podatkov-P0.md` to že priznava kot odprto vrzel D07.
- **Izvoz.** `person_export` je `POST` s CSRF, dovoljen samo vlogama `office`/`admin`; test `test_dostop_in_metoda` potrjuje 405 za GET, 302 za neprijavljenega, 403 za starša in 403 brez CSRF. Izvoz ne vsebuje gesla, sej, tujih kontaktov ali ID-jev drugih oseb; `test_brez_gesla_in_brez_tujih_podatkov` to preveri, mutacija z dodanimi tujimi kontakti pa test podre. Vsebinske vrzeli so v T-10.

### 3.5 Nadomestka po točkah B

- **Skladnost s pogodbo.** `RequestSchemaParity` primerja vse zahtevne sheme z `api/openapi.yaml`; `ContractBase.call` preverja status, medij, shemo s formati in `counts`. V pregledanih primerih nisem našel neskladja med opisom v pogodbi in vedenjem nadomestkov.
- **Trajnost in izpad (C11).** `DurabilityTests`: `DatabaseError` pri `bulk_create` vrne 503 in ne pusti `StubDelivery`; ponovitev iste zahteve uspe. `StubDelivery` in `StubItem` sta v bazi, ne v pomnilniku.
- **Idempotenca in poslovni ključ (C08).** `IdempotencyWindowTests`: 29 dni -> isti prevzem, 30 dni -> 409 `replay_window_expired`, druga vsebina -> 409 `idempotency_conflict`; nov ključ za isto postavko istega dogodka -> 409 `duplicate_event` brez delnega prevzema. Unikatna omejitev `uniq_stub_event` in pot `IntegrityError` sta preverjeni; sočasni različni ključi se zanašajo na to omejitev.
- **Vrstni red v `_stub/process`.** Koda preverja: iztek; če ni iztekel, `HANDOFF_UNCERTAIN`; nato tihi čas -> kontakt/upravičenje -> potreba M2 -> odsoten kontakt -> jezik -> `handed_off`. To ustreza dokumentiranemu vrstnemu redu „pravica, kontakt, potreba, preklic, urnik in iztek“ iz navodil M1; kontakt se torej razreši pred preverjanjem potrebe, kar je za opomnik, ki ni več potreben, dodatna izpostavljenost (ne kršitev pogodbe). Če je potreba neznana ali preverjanje ne uspe, postavka ostane `held/CHECK_UNAVAILABLE`; če je odgovorjena, `cancelled/NO_LONGER_REQUIRED`.
- **Urnik in iztek (C10).** `QuietHoursTests`: delavniki 7–20 Europe/Ljubljana, petek 20.30 -> `queued/QUIET_HOURS`, ponedeljek 7.00 -> `handed_off`, ob `now >= expires_at` -> `expired/DELIVERY_WINDOW_EXPIRED`; prehod poletnega/zimskega časa je preverjen (29. 3. 2026 in 25. 10. 2026). Prazniki in šolski urnik niso podprti (D05/šola).
- **Negotova predaja in preklic (C13).** `HANDOFF_UNCERTAIN` se ne ponovi sam; preklic vrne `too_late` in prepreči ročno ponovitev; ročna ponovitev je mogoča le pred preklicem; ob izteku ostane `expired/HANDOFF_UNCERTAIN`.
- **`need_ref`.** Tuj, neznan ali potekel sklic v M2 vrne 404, ne „nepotreben“; M1 ga zadrži kot `CHECK_UNAVAILABLE`. `need_ref` je obvezen samo pri `reminder` in samo tam; skupnega `locale` ni.
- **Produkcijski način.** Z `DJANGO_DEBUG=0` in `STUBS=` sem preveril: `/m1/api/v1/*`, `/m2/api/v1/*` in `/_stub/*` -> 404, `/m1/` in `/m2/` -> prava zaslona, `/p0/api/v1/health` -> 200; `STUBS=m1` z `DJANGO_DEBUG=0` se ne zažene (`ImproperlyConfigured`). Tabele nadomestkov se ob migracijah vseeno ustvarijo (dokumentirano), v produkciji pa se ne uporabljajo in niso v adminu.

### 3.6 Ogrodje modulov in odjemalec API

- **Seja in CSRF (C04/C05).** `UserSession.from_request` pošlje `sessionid`, `csrftoken`, `X-CSRFToken`, `Origin` in `Referer`; `core/tests/test_api_client.py` potrjuje uporabniški klic s sejo in CSRF, zavrnitev brez CSRF, servisni klic z žetonom in ločitev seje od žetona. `m1`/`m2` začetna zaslona uporabljata `UserSession` in ob izpadu vrneta 503.
- **Vbrizg glave / razkritje.** Z vrednostjo piškotka ali glave nisem dobil vbrizga v privzeti `urllib` transport; ta neveljavno vrednost zavrne z `ValueError` (T-03). Dodatna zasebna ugotovitev T-01 je v tem javnem poročilu navedena samo s številom in resnostjo (razdelek 4); podrobnosti prejme pobudnik v pogovoru.
- **Napake in čas.** 5xx, odgovor brez JSON in omrežna napaka se pretvorijo v `Unavailable`; 5 s časovna omejitev je trda. `IncompleteRead` in neveljavna glava nista zajeta (T-03). `P0_API_URL` je samo okoljska nastavitev, ne uporabniški vhod; shema `file://` je zavrnjena. Poti v odjemalcu so fiksne; morebitno pot iz uporabniškega vnosa je treba še preveriti v prihodnjih modulih.
- **Usmerjanje.** `STUBS` vsebuje `m1`/`m2` -> `stubs.urls_*`; sicer `m1.api_urls`/`m2.api_urls` (zdaj prazna). `test_module_routing` preverja oba načina; produkcijski 404 je potrjen zgoraj.
- **Meje modulov.** `test_boundaries` 2/2; obhod z `importlib` je mogoč (T-07). Za učno okolje je to opozorilo, ne varnostna meja.

## 4. Nove ugotovitve

**Zasebna varnostno občutljiva ugotovitev: 1, srednja (T-01).** Podrobnosti niso v tem javnem poročilu; pobudnik jih prejme v pogovoru oziroma po [SECURITY.md](../../SECURITY.md). V javnem poročilu so zato samo število in resnost.

Javne ugotovitve so tri srednje (T-04, T-05, T-08) in sedem nizkih (T-02, T-03, T-06, T-07, T-09, T-10, T-11). Ni novih kritičnih ali visokih ugotovitev. Nekatere spodnje ugotovitve so povezane z že dokumentiranimi odprtimi vrzelmi D07; to je izrecno navedeno.

| ID | Resnost | Kje | Opis | Ponovljiv korak | Predlog |
| --- | --- | --- | --- | --- | --- |
| T-02 | nizka | `p0/registry/services.py:58-72` | `issue_scope_ref` ni atomski: dve sočasni prvi zahtevi za isti `(oseba, scope_key)` obe vidita prazno in ena `create` sproži `IntegrityError` na `uniq_scoperef_person_scope`; klicatelj dobi 500. | V testni kopiji sem za `QuerySet.first()` vstavil bariero dveh niti; obe sta prebrali `None`, ena je ustvarila, druga je dobila `IntegrityError: duplicate key value violates unique constraint "uniq_scoperef_person_scope"` (1 uspeh, 1 napaka). | Uporabiti `get_or_create` oziroma ujeti `IntegrityError` in znova prebrati obstoječi `ScopeRef`; dodati sočasni test za `/me/relationships` in `audiences/resolve`. |
| T-03 | nizka | `p0/core/api_client.py:56-66`, `:84-92` | `UrllibTransport` ne pretvori `http.client.HTTPException` (npr. `IncompleteRead` pri skrajšanem odgovoru) v `Unavailable`; enako ne ujame `ValueError` pri neveljavni vrednosti glave (npr. CRLF v piškotku). Modul v takem primeru vrne 500, namesto da bi dejanje zadržal. | Lokalni strežnik je poslal `Content-Length: 100`, 5 bajtov in zaprl povezavo: `Api(...).call("GET", "/x")` je vrgel `IncompleteRead` (ni `Unavailable`). `UserSession(session_id="s", csrf_token="a\\r\\nX-Evil: 1", ...)` je vrgel `ValueError: Invalid header value` (ni `Unavailable`). | Ujeti `http.client.HTTPException` in `ValueError` ter ju pretvoriti v `Unavailable`; za piškotke/glave preveriti znake pred sestavljanjem; dodati teste. |
| T-04 | srednja | `p0/registry/ui.py:65-74`; `p0/registry/admin.py:6-20` | Seznam oseb prikaže ime, vloge in e-naslov do 50 oseb, ne da bi zapisal `AccessAudit`; `/admin/` prikaže vse osebe, povezave in upravičenja brez sledi. `ChangeAudit` je v adminu ureljiv in brisljiv, `Person` (kjer ni zaščite `PROTECT`), `Relationship` in `Grant` pa so brisljivi, kar nasprotuje trditvi v `SECURITY.md`, da se dokazi ne brišejo. | Kot `staff-03` z `is_staff=True`: `GET /p0/evidenca/osebe/` -> 200, `GET /admin/registry/person/` -> 200, število `AccessAudit` se ne poveča (0). `ChangeAudit` admin: add/change/delete = True; `AccessAudit`: False/False/False. Test `test_seznam_oseb_ne_hrani_iskalnega_niza` to celo pričakuje. | Za `/admin/` omejiti dostop na tehničnega skrbnika in ga izvzeti iz poslovnih podatkov ali ga zajeti v sled; seznam oseb in admin vsaj evidentirati v D07; `ChangeAudit` narediti samo za branje in onemogočiti brisanje oseb/povezav/upravičenj v adminu. |
| T-05 | srednja | `SECURITY.md` (razdelek »Kršitev varstva osebnih podatkov«); `p0/registry/management/commands/`; `p0/registry/admin.py` | Postopek zajezitve navaja dejanja, za katera ni orodja: ni ukaza za deaktivacijo/rotacijo `ServiceClient` (`create_service_client` zavrne obstoječe ime, `active` ni v adminu), ni ukaza za izbris vseh sej (`clearsessions` izbriše le potekle, `Session` ni v adminu), `ChangeAudit` pa je mogoče urejati/brisati. | `python manage.py help` v `[registry]` našteje le `create_service_client`, `import_csv`, `purge_audience_snapshots`, `purge_import_uploads`, `seed_test_data`; `clearsessions` opisuje le potekle seje; `ServiceClient` in `Session` nista v `admin.site._registry`. | Dodati ukaze `service_client_deactivate`/`rotate` in `sessions_purge_all`, ju dokumentirati v SECURITY.md ter preizkusiti; `ChangeAudit` zaščititi pred urejanjem/brisanjem; po potrebi omejiti admin. |
| T-06 | nizka | `p0/registry/tests/test_contract.py:602-614` | Test zamrznitve preveri le, da se trenutna različica ujema z vrstico v `api/zamrznitve.txt`. Če se pogodba spremeni in se **obstoječa** vrstica `1.0.0` prepiše z novim SHA-256, test uspe brez nove različice; zapis ni append-only. | V kopiji sem dodal komentar v `api/openapi.yaml`: test pade („pogodba se je spremenila brez nove različice“). Po prepisu iste vrstice `1.0.0` z novim SHA-256 test **uspe**. | V testu zahtevati, da se prejšnje vrstice `api/zamrznitve.txt` ne spremenijo (npr. primerjava z `git show HEAD:...` ali ločen seznam), in prepovedati prepis obstoječe različice; vsaka sprememba naj doda novo vrstico in dvigne `info.version`. |
| T-07 | nizka | `p0/core/tests/test_boundaries.py:11-42` | Meja modulov se preverja z regularnim izrazom samo za literalne `import`/`from` vrstice. `importlib.import_module("registry")`, `django.apps.apps.get_model("registry", ...)` in `from stubs import m1` (ki posredno uvozi `registry.api`) testu uidejo. | V kopiji sem v `p0/m1/views.py` dodal `import importlib` in `importlib.import_module("registry")`; `test_boundaries` je ostal **OK** (2 testa). `from stubs import m1` prav tako ni v `FORBIDDEN`. | Za učno okolje je to honor-system, ne varnostna meja; vseeno dodati AST-preverjanje dinamičnih klicev, prepovedati `stubs` in `apps.get_model`, ter v dokumentaciji jasno zapisati, da test ni dokaz izolacije. |
| T-08 | srednja | `DEVELOPER.md:3,57`; `docs/projekt/odlocitve.md:29`; `docs/projekt/stanje-prevzema-T.md:17,25,29`; `docs/arhitektura/kratka-specifikacija-P0-M1-M2.md:5`; `docs/arhitektura/vmesnik-P0-M1-M2.md:8`; `docs/README.md:12`; `docs/mentorji/navodilo-za-pregled.md:27`; `docs/arhitektura/izhodisca.md:39`; `docs/projekt/prispevki.md`; `docs/projekt/pregled-dostopnosti-P0.md` | Dokumentacija ni časovno usklajena z D12 `1.0.0`: `DEVELOPER.md` pravi „Osnutek D12, ni potrjena“, register odločitev pravi „D12 ostaja odprt“, stanje T „Pogodba je osnutek; ekipe se ne smejo vezati nanjo“, kratka specifikacija in več dokumentov še govori o osnutku; `prispevki.md` pravi, da ponovni pregled ni izveden; dostopnost pravi, da izvoz ni v obsegu T, čeprav je implementiran; `odvisnosti-in-licence.md` navaja staro razčlenitev skeniranja. | Branje navedenih vrstic in primerjava z `api/openapi.yaml` (`info.version: 1.0.0`), `api/zamrznitve.txt`, tagom `v1.0.0` in izvedenimi 275 testi. | V ločenem dokumentacijskem PR uskladiti status D12 na „sprejeto 13. 11. 2026, pogodba 1.0.0“, dodati 275 testov in datum tretjega pregleda, jasno ločiti zgodovinske zapise od trenutnega stanja ter uskladiti obseg izvoza in razčlenitev Trivy. |
| T-09 | nizka | `p0/registry/management/commands/seed_test_data.py:114-124`; `DEVELOPER.md:36-40` | `SEED_PASSWORD` se uporabi le ob **prvem** ustvarjanju računa. Če razvijalec najprej požene seed brez gesla in nato z `SEED_PASSWORD`, se geslo ne nastavi; računi ostanejo z neuporabnim geslom, čeprav navodilo pravi, da ga lahko nastavite. | V tekoči bazi sem obstoječemu `parent-01` nastavil staro geslo, nato zagnal `seed_test_data` z novim `SEED_PASSWORD`: `old_still_valid=True`, `new_valid=False`. | Ob nepraznem `SEED_PASSWORD` posodobiti geslo tudi obstoječim računom (ali v navodilu jasno zapisati, da velja le ob prvem zagonu); dodati test. |
| T-10 | nizka | `p0/registry/tests/test_izvoz_osebe.py:14-30,138-145`; `p0/registry/export.py:73-78,167-170`; `p0/registry/models.py:238-240` | Varovalo `test_vsi_modeli_z_osebo_so_zajeti` zazna le nov **neposredni** FK/OneToOne na `Person` v aplikaciji `registry`; nov model v `m1` z `ForeignKey("registry.Person", ...)` testu uide. Prav tako preverja samo imena modelov, ne polj: izvoz ne vsebuje `ImportBatch.applied_by` (oseba je serijo uveljavila, a `lastna_dejanja.uvozi` bere le `created_by`) in ne vključi `SourceMapping` z `entity_type="student"` za učenca. | V kopiji sem dodal `MutationLink` v `p0/m1/models.py` z `ForeignKey("registry.Person")`: izvozni test in meja ostaneta **OK**. Neposredni model v `registry` test pravilno zavrne (`MutationPersonLink`). Ločen test z uveljavitvijo serije kot druga oseba: `lastna_dejanja.uvozi == []`, čeprav je 30 uvoznih sprememb. | Razširiti varovalo na vse aplikacije in na FK na `Student`/posredne povezave; preverjati tudi polja; v izvoz dodati `applied_batches` in studentske izvorne ključe. |
| T-11 | nizka | `.github/vzdrzevalci.txt`; `.github/workflows/prispevki.yml`; `docs/projekt/odlocitve.md` (D09/D14) | `alexlandich` je na seznamu vzdrževalcev, zato njegovi PR-ji ne potrebujejo oznake `avtor-urejen`; register D09/D14 hkrati pravi, da je njegov pisni sprejem vloge še odprt. To je nedosleden prehod med potrjenim in nepotrjenim skrbnikom ter vpliva na preverjanje pravic mladoletnih avtorjev. | Primerjava `.github/vzdrzevalci.txt` z vrsticama D09/D14 v registru in pogojem v `prispevki.yml` (`grep -qxF "$AUTHOR"` -> vzdrževalec). | Do pisnega sprejema odstraniti `alexlandich` s seznama ali v registru izrecno zapisati, da je njegov dostop že potrjen; dodati test/preverjanje skladnosti seznama in registra. |

## 5. Rezultat preizkusa testov (točka 7)

### 5.1 Okolje in zagon

Prvi `docker compose up --build -d --wait` v tem okolju ni uspel zaradi read-only `~/.docker/buildx` (`failed to update builder last activity time ... read-only file system`). Ponovitev z `DOCKER_CONFIG` v pisni delovni mapi je uspela; to je omejitev okolja pregleda, ne izdelka. Nato:

```text
docker compose build --no-cache p0
  Image odprta-sola-p0 Built
  ID sha256:0ce44d3dccca2d765787ce8ea7605e0232275d311f47a14b06e006afbf1a3080
docker compose down -v
docker compose up -d --wait
  db, p0, mail, cleanup: Healthy
docker compose exec -T -e SEED_PASSWORD=<naključno> p0 python manage.py seed_test_data
  Testni nabor naložen.
docker compose exec -T p0 python manage.py test
  Ran 275 tests in 33.399s
  OK
```

V izpisu ni `skipped`; **0 preskočenih**. Meje modulov M1/M2 se izvajajo, ker mapi obstajata. Po ponastavitvi je bilo tudi:

```text
python manage.py test registry.tests.test_contract registry.tests.test_robni registry.tests.test_zasloni
  Ran 100 tests in 6.496s
  OK
```

Dodatni ciljni sklopi:

```text
test_varovala_uvoza (sočasnost in rok datotek)        18/18 OK
test_contract.ContactContract + AudiencesContract
  + test_ciscenje_posnetkov + test_izvoz_osebe
  + test_sled_vpogledov                                 36/36 OK
test_ponovni_api + test_uvoz_zasloni + test_d12_tocke_b 44/44 OK
test_robni.PreviewApplyTests + ConcurrentApplyTests
  + test_varovala.ImportRestriction/ImportRole/PasswordRecovery 28/28 OK
```

### 5.2 Statična preverjanja

```text
ruff check .                         All checks passed!
ruff format --check .                86 files already formatted
python manage.py makemigrations --check --dry-run   No changes detected
python manage.py check               System check identified no issues (0 silenced).
python -m pip check                  No broken requirements found.
python3 scripts/check_docs_links.py  Notranje povezave in sidra so veljavni.  (čista delovna kopija)
```

V glavni delovni mapi je skript med pregledom našel povezavo v začasnem `.p0-review/venv`, ki ni del repozitorija; v čisti kopiji (`d261ace`) je rezultat veljaven. To ni napaka repozitorija.

### 5.3 Preizkus odprave popravkov z začasno razveljavitvijo

Vse mutacije so bile narejene v ločeni kopiji `d261ace` (`.p0-review/mut`) in po vsakem zagonu povrnjene; `main` in pregledana koda se nista spremenila. Ukaz je bil `python manage.py test <navedeni test>` v isti sliki in zbirki.

| Začasno odstranjeno pravilo | Test | Rezultat |
| --- | --- | --- |
| Vezava kontakta na prejemnika (odstranjen filter `person=person`) | `ContactContract` | `Ran 8`, `FAILED (failures=1)`: `200 != 403` pri tujem prejemniku. |
| Atomski zapis zahteve (zamenjan `transaction.atomic()` z `nullcontext()`) | `DurabilityTests` | `Ran 2`, `FAILED (failures=1)`: po izpadu `StubDelivery.objects.exists()` je `True`. |
| Neznan `need_ref` ni „nepotreben“ (vrnjen `REQUIRED`) | `ReminderCheckContract` + `NeedRefTests` | `Ran 7`, `FAILED (failures=2)`: `held/CHECK_UNAVAILABLE` namesto `handed_off`. |
| Urnik 7–20 (konec prestavljen na 21) | `QuietHoursTests` | `Ran 4`, `FAILED (failures=2)`: ob 20.00 `handed_off` namesto `expired`. |
| Ponovna presoja kontakta v obdelavi (preskočen `delivery_contact`) | `AuthorizationAtActionTests` | `Ran 2`, `FAILED (failures=2)`: odvzet prejemnik `handed_off` namesto `held/NOT_ALLOWED`. |
| Prepoved tujih kontaktov v izvozu (dodani vsi kontakti) | `PersonExportTests.test_brez_gesla_in_brez_tujih_podatkov` | `Ran 1`, `FAILED (failures=1)`: `family03@example.invalid` se pojavi v izvozu. |
| Sled vpogleda pred prikazom (odstranjen `record_view`) | `AccessAuditTests.test_vsak_zaslon_osebe_zapise_vpogled` | `Ran 1`, `FAILED (failures=1)`: pričakovana vrstva, dobljeno `[]`. |
| Varovalo granta pri uvozu (onemogočeno za `grant`) | `ImportRestrictionTests.test_premaknjen_zacetek_granta` + `test_odvzem_enega_dovoljenja_ne_vpliva_na_drugega` | `Ran 2`, `FAILED (failures=2)`: `manual_restriction` manjka; R-04 je res odpravljen. |
| Zamrznitev pogodbe (sprememba `openapi.yaml` brez vrstice) | `SpecCoverage.test_pogodba_je_zamrznjena_razlicica` | `Ran 1`, `FAILED (failures=1)`; po prepisu iste različice `1.0.0` z novim SHA-256 pa **OK** — T-06. |
| Meja modulov (dodan `importlib.import_module("registry")` v `m1`) | `core.tests.test_boundaries` | `Ran 2`, **OK** — T-07. |
| Nov model s FK na osebo v `registry` | `test_vsi_modeli_z_osebo_so_zajeti` | `FAILED`: `MutationPersonLink` ni v `COVERED` — varovalo deluje za ta primer. |
| Nov model s FK na osebo v `m1` | isti test + `test_boundaries` | **OK** — T-10. |

Zaključek: izbranih 8 pravil iz točk 2 do 6 ima test, ki ob odstranitvi pade; dva nova primera (T-06, T-07) pa kažeta, da varovali nista popolni. To ni ocena celotne zbirke, le preizkus izbranih pravil.

### 5.4 Dostopnost brez bralnika zaslona

Headless Chrome 157, 320 × 900, prijavljeni izmišljeni uporabniki:

| Zaslon | `lang` | `h1` | `main` | `scrollWidth` | Opomba |
| --- | --- | --- | --- | --- | --- |
| `/p0/` | sl | 1 | 1 | 320 | brez prelivanja |
| `/p0/evidenca/osebe/` | sl | 1 | 1 | 305 | tabela se drsi znotraj `.tablewrap` |
| `/p0/evidenca/osebe/<id>/` | sl | 1 | 1 | 305 | tudi z 80-znakovnim e-naslovom; gumb za izvoz je v obrazcu s CSRF in `aria-describedby` |
| `/p0/evidenca/osebe/<id>/kontakt/` | sl | 1 | 1 | 320 | oznaka polja |
| `/p0/evidenca/uvoz/` | sl | 1 | 1 | 305 | tabela v regiji |
| `/m1/` | sl | 1 | 1 | 320 | novi zaslon |
| `/m2/` | sl | 1 | 1 | 320 | novi zaslon |

Tipkovnica na prijavi: preskok, Prijava, uporabniško ime, geslo, zapomni si me, gumb; vsak element ima viden fokus `solid 3px` (`:focus-visible`). Prazna oddaja premakne fokus na `#napake`; povezavi vodita na `#id_login` in `#id_password`. To je avtomatski pregled; **bralnik zaslona, povečava 200/400 %, kontrast in razumljivost z uporabniki niso izvedeni**.

## 6. Devet točk in dvajset skupin

### 6.1 Devet točk kontrolnega seznama

| # | Točka | Stanje | Dokaz in razlika do zapisa o odpravi |
| --- | --- | --- | --- |
| 1 | Lastni otroci, tuja družina zavrnjena | **izvedeno** | `AuthorizationCheckContract`, `Me`/`Relationships`; tuj in ugiban sklic -> `NOT_ALLOWED`; tuj `subject_id` -> 403. Enako kot prej. |
| 2 | Skupen kontakt, ločena računa | **izvedeno** | `parent-01` in `parent-02` z istim e-naslovom imata različna `person_id` in ločene pravice; `test_racun_s_skupnim_naslovom_se_prijavi_locen`. Enako. |
| 3 | Odvzem povezave ali upravičenja | **izvedeno** | `authz.revoke_*` zapre poslovni obseg; `ImportRestrictionTests` + `ConcurrentRevocationTests`; vse štiri poti zavrnejo; sled ostane. Enako, zdaj tudi sočasno. |
| 4 | CSV brez delnega prepisa, ponovitev, sled | **izvedeno** | `test_import` 22, `CsvLimitTests`, `PreviewPagingTests`, `DiscardOutcomeTests`; atomskost, ponovitev, sled; R-03/R-04/R-08 odpravljeni. Enako, z novimi primeri. |
| 5 | Omejen servisni kontaktni klic | **izvedeno v P0** | `ContactContract` 8/8; kontakt samo za člana neizteklega posnetka z aktualnim grantom; vsi neveljavni vhodi 403. **Razlika:** zapis je imel „ni izpolnjeno“ (klic 503 do D12); zdaj je D12 C07 izveden. Pravi M1, ki bi kontakt dejansko uporabil, še ne obstaja. |
| 6 | Neodvisen pregled kode | **delno** | Ta pregled je opravil AI; človeški pregled in sprejem nista izvedena. Enako kot prej, z novo vsebino. |
| 7 | Pogodbeni testi po ponastavitvi | **izvedeno** | `down -v`, ponovna namestitev, seed, 275/275; pogodbeni/robni/zaslonski sklop 100/100. Enako, z večjim številom. |
| 8 | Izpad P0, varno zadržanje | **ni izvedeno** | Pravih M1/M2 ni; nadomestka ne kličeta P0 po omrežju in ne pošiljata. Enako; trajni zapis nadomestka tega scenarija ne nadomešča. |
| 9 | Tipkovnica, fokus, napake, bralnik | **delno, ni izpolnjeno** | 320 px, struktura, oznake, fokus in napake preverjeni tudi na `/m1/`, `/m2/` in ob izvozu; bralnik zaslona, povečava in kontrast niso. **Razlika:** zapis je imel „ni izpolnjeno“; zdaj je delno. |

Skupaj: **6 izvedenih, 2 delna, 1 ni izvedena**. Razlika do zapisa o odpravi: točka 5 je iz „ni izpolnjeno“ postala „izvedeno v P0“; točka 9 je iz „ni“ postala „delno“; točka 8 ostaja odprta; točka 6 ostaja človeško nepotrjena.

### 6.2 Dvajset skupin kratke specifikacije

| # | Scenarij | Stanje | Dokaz / vrzel |
| --- | --- | --- | --- |
| 1 | Dva računa z istim kontaktom | delno | P0 identitete in pravice so preizkušene; individualna aktivacija in odzivi pravega M2 ne. |
| 2 | Druga družina, ugiban ID, tuj sklic | delno | P0 API in kontakt zavrneta tuj/ugiban sklic; vse podatkovne poti, `/admin/` in prihodnji moduli niso zajeti. |
| 3 | Zaposleni zunaj oddelka | delno | `audiences/resolve` zavrne tujo dodelitev; prava objava M1 ne obstaja. |
| 4 | Učenčev račun in ciljna skupina | ni v obsegu T | Pogojena razširitev; seed ne ustvarja računov učencev. |
| 5 | Povezava brez granta, nato odvzem | **pokrit** | `test_povezava_sama_ne_podeli_pravice` kliče `authz`; odvzem povezave/granta v vseh štirih poteh. |
| 6 | Starejši uvoz po ročni omejitvi | **pokrit** | `ImportRestrictionTests` in sočasni scenariji; konflikt, zavrnitev, nobenega delnega vpisa. |
| 7 | Napačen CSV ali neznana referenca | **pokrit** | `ValidationTests`, `AtomicityTests`, `CsvLimitTests`; R-03 odpravljen. |
| 8 | Ponoven uvoz, dvojnik, manjkajoča vrstica | **pokrit** | `IdempotencyTests`, validacija dvojnikov, CLI ponovitev; manjkajoča vrstica ne odvzame. |
| 9 | Aktivacija/obnova pri skupnem predalu | ni v obsegu T | S-03 je zaprta; individualni postopek ostaja pred B. |
| 10 | Odjava, CSRF, podtaknjen uporabnik, servis | **pokrit** | `test_odjava_konca_sejo`, `test_seja_brez_csrf_je_json_403`, `test_tuj_subject_id_403`, `test_napacen_zeton_ob_veljavni_seji`, `test_servisni_klic_*`, `core.tests.test_api_client`; pogodbene napake. |
| 11 | Informativno obvestilo, odprtje, seznanitev | ni v obsegu T | M1. |
| 12 | Dva otroka, sprememba različice M1 | ni v obsegu T | M1. |
| 13 | Več namenov, Ne/brez odziva | ni v obsegu T | M2. |
| 14 | Dva otroka, dva odločevalca | ni v obsegu T | M2. |
| 15 | Neodobrena/spremenjena različica M2 | ni v obsegu T | M2. |
| 16 | Sprememba/preklic, zaključen obrazec | ni v obsegu T | M2. |
| 17 | Izpad M1, izgubljen 202, dvojni ključ | delno | Idempotenca, konflikt in trajni zapis v nadomestku so preizkušeni; pravi izpad, izgubljen odgovor in obnova niso. |
| 18 | Opomnik, selektivni preklic, izpad, tihi čas, iztek | delno | Potreba, selektivni preklic, urnik, iztek in DST so preizkušeni v nadomestku; pravi izpad, tihi čas šole in samodejni razporejevalnik niso. |
| 19 | Negotov SMTP, odvzem med dostavo, obnova | nepokrit | Ni prave SMTP predaje, obnove ali razporejevalnika. |
| 20 | Sveža namestitev, nadomestki, izvoz, dostopnost | delno | Namestitev in 275 testov uspeta; izvoz je izveden (T-10 za vrzeli); bralnik zaslona ni, 320 px je popravljen. |

**Skupaj: 5 pokritih, 6 delnih, 1 nepokrit, 8 zunaj obsega T.** To se ujema s prejšnjo oceno DeepSeek (5/6/1/8) in se razlikuje od zapisa o odpravi (4/7/1/8): skupina 10 je zdaj pokrita zaradi novih pogodbenih in identitetnih testov. V primerjavi z OpenAI drugim krogom (2/9/1/8) so razlike predvsem v tem, da so skupine 5, 6, 7 in 10 po novih testih pokrite, skupina 4 pa je po obsegu T izven. Skupine 1, 2, 3, 17, 18 in 20 ostajajo delne; 19 ostaja nepokrita; 4, 9 in 11–16 so zunaj obsega T.

## 7. Odvisnosti

**Zaklepi.** `p0/requirements.lock`, `requirements-dev.lock` in `requirements-build.lock` se od drugega kroga niso spremenili; vsebujejo točne različice in hashe. `pip check` ni našel zlomljenih odvisnosti.

**`pip-audit` 2.10.1** (ločeno okolje, `--disable-pip --no-deps`):

```text
requirements.lock        8 paketov, 0 znanih ranljivosti
requirements-dev.lock   17 paketov, 0 znanih ranljivosti
requirements-build.lock  1 paket,  0 znanih ranljivosti
```

**Trivy 0.76.2** nad zgrajenima slikama P0 (baza osvežena 13. 11. 2026):

| Cilj | Rezultat |
| --- | --- |
| Razvojna slika `odprta-sola-p0:latest` | 208 zapisov: 205 Debian (48 HIGH, 90 MEDIUM, 66 LOW, 4 UNKNOWN) + 3 Python (`setuptools` 70.3.0: CVE-2025-47273 visoka, CVE-2026-59890 srednja, GHSA-xmj3-9gf7-h52w nizka; vsa s popravkom) |
| Produkcijska slika `odprta-sola-p0-prod:review3` | 205 zapisov: 47 HIGH, 89 MEDIUM, 65 LOW, 4 UNKNOWN; **0 s popravkom**, **0 paketov Python** |

To se v skupnem številu in „0 s popravkom“ ujema z dokumentom (205; 47/74/65/19; 0 popravkov; Python 0), **razčlenitev po resnosti pa ne**: dokument navaja 74 srednjih in 19 neznanih, današnja baza pa 89 srednjih in 4 neznane. Vzrok je osvežitev podatkovne zbirke Trivy, ne sprememba zaklepa; vseh 205 je še vedno brez popravka. Razvojna slika ima dodatna 3 opozorila `setuptools`, kar dokumentacija že opisuje kot opombo, ne kot napako.

**Licence.** Novih paketov ni; popis v `docs/projekt/odvisnosti-in-licence.md` (Django/asgiref/sqlparse BSD-3, allauth/gunicorn MIT, psycopg LGPL-3.0, typing PSF, razvojna orodja MIT) se ujema z zaklepi. Odprto ostaja: SBOM, pravni pregled distribucije, točne različice in besedila vgrajenih knjižnic `psycopg-binary`, izvor sistemskih paketov. To ni pravno mnenje.

**CI.** `p0.yml` preveri namestitev zaklepov, `pip check`, skladnost z vhodnimi zahtevami, `ruff`, `makemigrations`, `check` in test; **ne** gradi slike, ne izvaja `pip-audit`/Trivy in ne preverja dostopnosti. To je skladno z dokumentacijo, ki skeniranje opisuje kot ročni postopek.

## 8. Omejitve pregleda

- Pregled je opravil AI (DeepSeek); Mitja Pirih ga v tej izvedbi ni prebral ali sprejel. Poročili prvega in drugega kroga DeepSeek je napisal isti sistem, zato ta pregled ni neodvisen od njiju; je pa drug sistem AI glede na pisca kode.
- Samo izmišljeni podatki. Testno geslo in servisni žetoni so bili naključni in niso v poročilu ali repozitoriju. Po koncu je `docker compose down -v` odstranil vsebnike in volumen; začasna mapa pregleda je odstranjena.
- Pregled velja za `d261ace`; `main` `ac6bc18` doda samo dokumentacijo navodila. Novejših commitov po `ac6bc18` nisem pregledal.
- `docker compose up --build` je v tem okolju prvič padel zaradi read-only `~/.docker/buildx`; uspel je z `DOCKER_CONFIG` v pisni mapi. To je omejitev okolja, ne izdelka. Gradnja brez predpomnilnika je uspela; produkcijska slika je bila zgrajena ločeno.
- Trivy je skeniral le razvojno in produkcijsko sliko P0; slik PostgreSQL in Mailpit ter razvojne osnovne slike tokrat nisem skeniral. Trivy baza se je med pregledom osvežila, zato se razčlenitev resnosti razlikuje od dokumenta.
- Bralnik zaslona (NVDA/Orca), povečava 200/400 %, kontrast z orodjem, visok kontrast, glasovno upravljanje in razumljivost z uporabniki **niso** preverjeni. 320 px in fokus sta izmerjena z headless Chrome, ne z bralnikom.
- Prava M1/M2, prava SMTP predaja, izpad P0 med dostavo, obnova kopije, trajnost prevzema 202 prek ponovnega zagona in produkcijska namestitev (gunicorn/HTTPS) **niso** izvedeni.
- Niso izvedeni: celovit SBOM, pregled vseh sistemskih/binarnih komponent, fuzzing, obremenitveni preizkus, izčrpen pregled vseh časovnih kanalov, sočasni uvoz z več delavci, obnova po izpadu in ocena kontakta med sočasnim odvzemom (TOCTOU). Slednje ostaja nepreizkušena omejitev, ne ugotovitev.
- Niso preverjene vse veje Django admina, prihodnji moduli M1/M2, vsi infrastrukturni dnevniki in pravice prispevkov dijakov. `/admin/` sem preveril le z začasnim `is_staff` računom.
- Mutacije so ciljne, ne izčrpne; uspeh 275 testov ni dokaz popolnosti. Odsotnost zadetka ni dokaz odsotnosti ranljivosti.

## 9. Izjava

Ta pregled **ni človeški prevzem, ni pravno mnenje in ni potrditev D12**. Uspešna izvedba 275 testov in 100 testov po ponastavitvi ni dokaz izpolnitve vseh prevzemnih pogojev. Pregledovalec ne potrjuje produkcijske pripravljenosti, pravic prispevkov dijakov ali sprejema poročila v imenu Mitje Piriha. Odločitev o prevzemu T sprejme pobudnik; to poročilo je dokaz zanjo, ne sam sprejem. Nova zasebna ugotovitev T-01 ni v tem javnem besedilu; pobudnik jo prejme po [SECURITY.md](../../SECURITY.md).
