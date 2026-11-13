# Odprava ugotovitev tretjega neodvisnega pregleda P0

Status: osnutek, 13. november 2026. Ta zapis ne spreminja poročil pregledovalcev ([Codex/OpenAI](2026-11-tretji-pregled-P0-openai.md), PR #68; [DeepSeek](2026-11-tretji-pregled-P0-deepseek.md), PR #67). Poročili ostajata dokaz za commit `d261ace`. Zapis nadaljuje [odpravo ponovnega pregleda](2026-11-odprava-ponovnega-pregleda-P0.md). **Ni človeški prevzem in ne zapira paketa T.**

## Podatki

| Podatek | Vrednost |
| --- | --- |
| Pregledano | `d261ace` (koda P0 enaka `ac6bc18`) |
| Zasebni popravki | `11f749c` (Z-01, Z-03, Z-04); objavljena varnostna nasveta [T3-Z01](https://github.com/odprta-sola/solska-platforma/security/advisories/GHSA-5mgm-v2m7-8jw9) in [T3-Z03](https://github.com/odprta-sola/solska-platforma/security/advisories/GHSA-jg63-9wh9-9vm5) |
| Javni popravki | PR #69 (sled seznama in admina, zajezitev), #70 (zamrznitev, meja modulov), #71 (vloge skrbnikov), #72 (dokumentacija D12), #73 (izvor uporabniškega klica, vsebina dostave), #74 (sklic, seed, izvoz) |
| Stanje po združitvi kode | `main` = `1f31aea` (s poročiloma) |
| Izvedel | Claude (Anthropic), model Claude Opus 5.5, po navodilih pobudnika |
| Odgovorni človek | Mitja Pirih; sprejem tega zapisa še ni potrjen |

## Primerjava poročil

Prevzema T ne priporoča nobeden od pregledovalcev. DeepSeek jedro P0 priporoča pogojno. Oba sta s 275 testi in brez preskokov potrdila, da so popravki prejšnjih krogov odpravljeni, tudi S-01 do S-04, R-09 in R-10.

Oba sta neodvisno našla:
- isto zasebno ugotovitev: odjemalec API ob preusmeritvi prenese poverilnice (OA Z-01, DS T-01);
- isti lažno zeleni test zamrznitve;
- obhodljivo preverjanje meje modulov;
- zastarelo dokumentacijo o D12.

Samo Codex je našel:
- tuj dogodek v izvozu (Z-03);
- napačen izvor uporabniškega klica (T-02);
- nepopoln trajni zapis dostave (T-01).

Samo DeepSeek je našel:
- tekmo pri sklicu na obseg;
- orodja za zajezitev, ki jih ni bilo;
- `SEED_PASSWORD`;
- nepopoln izvoz;
- neskladje seznama vzdrževalcev.

Oznake T-xx se med poročiloma ne ujemajo, zato imajo v tabeli predpono OA oziroma DS. Zasebne ugotovitve (Z-xx) so opisane le toliko, kolikor so objavljene v nasvetih oziroma v javnem poročilu DeepSeek. Vsako ugotovitev je avtor popravkov pred popravkom ponovil v kodi.

## Tabela odprave

| Ugotovitev | Resnost (pregled) | Stanje | Dokaz |
| --- | --- | --- | --- |
| OA Z-01, DS T-01: preusmeritev prenese sejo, CSRF in žeton | srednja | odpravljeno; nasvet T3-Z01 | `UrllibTransportTests`: dva lokalna strežnika; cilj preusmeritve ne prejme ničesar; odgovor 3xx je `Unavailable` tudi z veljavnim JSON |
| OA Z-03: izvoz in zaslon osebe z dogodkom druge osebe | srednja | odpravljeno; nasvet T3-Z03 | `test_enak_kljuc_druge_vrste_ni_v_sledi_osebe`: dejansko tuje upravičenje s ključem lastne povezave; filter po paru (vrsta, ID) |
| OA Z-04, DS T-03: neveljavna glava ali skrajšan odgovor povzroči 500 | nizka | odpravljeno (`11f749c`) | `test_neveljavna_glava_je_nedosegljivost`, `test_skrajsan_odgovor_je_nedosegljivost` (pravi prenos) |
| OA Z-02, DS T-04: seznam oseb in admin brez sledi; admin lahko spreminja sledi in briše | srednja | odpravljeno (PR #69) | `AccessAuditTests`, `AdminAuditTests`: zapis za vsako prikazano osebo, brez iskalnega niza; admin zapiše seznam, obrazec, brisanje in zgodovino; `ChangeAudit` samo za branje; osebe, povezave, upravičenja in potrditve se ne brišejo |
| DS T-05: orodja za zajezitev iz SECURITY.md niso obstajala | srednja | odpravljeno (PR #69) | `deactivate_service_client`, `rotate_service_client`, `purge_all_sessions --yes`; `test_zajezitev` |
| OA T-03, DS T-06: test zamrznitve uspe po prepisu hasha 1.0.0 | srednja / nizka | odpravljeno (PR #70) | CI `zamrznitev-pogodbe`: samo dodajanje vrstic glede na osnovno vejo, ujemanje z oznakami `v*`, nova različica ob spremembi; 8 scenarijev v začasnem repozitoriju Git |
| OA T-04, DS T-07: meja modulov z regularnim izrazom | nizka | odpravljeno v obsegu učnega okolja (PR #70) | AST: vsa imena, relativni uvozi, `importlib`, `__import__`, `apps.get_model`, prepovedan `stubs`; vsi primeri pregledovalcev vstavljeni v `m1/views.py` test podrejo. Zapisano, da to ni varnostna meja |
| DS T-11: vzdrževalec pred sprejemom vloge | nizka | odpravljeno (PR #71) | Odločitev naročnika: Aleksandar je samo mentor, pravica na GitHubu Triage; pobudnik je edini vzdrževalec; sistemi AI so orodja |
| OA T-05, DS T-08: dokumentacija trdi, da je D12 osnutek | nizka / srednja | odpravljeno (PR #72) | 15 dokumentov usklajenih; zgodovinski deli označeni; D15, obseg izvoza, register prispevkov, Trivy |
| OA T-02: uporabniški POST iz modula vrne 403 | srednja | odpravljeno (PR #73) | `LiveUserSessionTests`: pravi strežnik in prenos; izvor brskalnika `localhost` in HTTPS proti `127.0.0.1`. Mutacija s starim izvorom vrne `403 csrf_failed`; CSRF ostane obvezen |
| OA T-01: prevzeta dostava izgubi `params` in `target` | srednja | odpravljeno (PR #73) | `test_zahteva_se_obnovi_iz_baze`: celotna zahteva se sestavi iz ponovno prebranega zapisa |
| DS T-02: tekma pri `issue_scope_ref` povzroči 500 | nizka | odpravljeno (PR #74) | `ConcurrentScopeRefTests`: dve niti z ločenima povezavama in bariera pred zapisom → isti sklic, en zapis |
| DS T-09: `SEED_PASSWORD` ne nastavi gesla obstoječim računom | nizka | odpravljeno (PR #74) | `SeedPasswordTests` (z gesli in brez njih) |
| DS T-10: izvoz brez `applied_by` in ključev učenca; ozko varovalo | nizka | odpravljeno (PR #74) | `uveljavljeni_uvozi`, `izvorni_kljuci_ucenca`; varovalo pregleda vsa polja v vseh aplikacijah, ki kažejo na osebo ali učenca |
| DS R-07 (iz drugega kroga): setuptools v razvojni sliki | nizka | opomba, ni napaka | nespremenjeno ([odvisnosti](../projekt/odvisnosti-in-licence.md)) |

## Izvedeni ukazi in rezultati

```text
docker compose down -v; up --build -d --wait   vse storitve zdrave
seed_test_data                                  naključni SEED_PASSWORD
python manage.py test                           Ran 299 tests. OK (brez preskokov)   [main = 1f31aea]
ruff check / format --check                     čisto (91 datotek)
makemigrations --check --dry-run                No changes detected
scripts/check_contract_freeze.py origin/main    skladno
python3 -m unittest scripts/test_check_contract_freeze.py   OK
scripts/check_docs_links.py                     veljavno
```

Vsak popravek ima mutacijo, ki pokaže, da test zazna napako: ob odstranitvi popravka vsaj en test pade. Zasebni popravki imajo 6 mutacij, PR #69 jih ima 8, PR #70 5 za skript in 5 vstavljenih obhodov meje, PR #73 3 in PR #74 5.

Med delom so se pokazale tri stvari:
- Prvi test preusmeritve brez telesa ni zaznal odstranjenega preverjanja 3xx, zato je okrepljen z odgovorom JSON.
- Prvi test trka ključev ni našel trka v testnem naboru (ključi povezav in upravičenj se tam ujemajo po družinah), zato zdaj ustvari dejanski trk.
- Ena mutacija na zaslonu osebe je po pomoti razveljavila popravek, ki je bil nato ponovno uveljavljen in preverjen.

Ni izvedeno, z razlogom:
- `pip-audit` in Trivy, ker zaklepi in slike niso spremenjeni; Trivy je s svežo bazo ponovil OpenAI, rezultat je v odvisnostih.
- Ročni pregled z bralnikom zaslona, ker je potreben človek.
- Nov model v `m1` za preizkus varovala izvoza ni bil dodan.

## Devet točk

| # | Točka | Stanje |
| --- | --- | --- |
| 1 | Lastni otroci, tuja družina zavrnjena | izpolnjeno |
| 2 | Skupen kontakt, ločena računa | izpolnjeno |
| 3 | Odvzem povezave ali upravičenja | izpolnjeno, tudi sočasno; admin ne obide več `authz` |
| 4 | CSV brez delnega prepisa, ponovitev, sled | izpolnjeno |
| 5 | Kontakt vezan na zahtevo in prejemnika | izpolnjeno za C07 |
| 6 | Pregled kode | trikrat pregledano s sistemi AI; človeški pregled ni izveden |
| 7 | Pogodbeni testi po ponastavitvi | izpolnjeno; zamrznitev zdaj preverja tudi CI |
| 8 | Izpad P0, varno zadržanje | delno: ogrodji modulov zavrneta ob nedosegljivosti; prava M1/M2 ne obstajata |
| 9 | Tipkovnica, fokus, napake, bralnik | ni izpolnjeno: bralnik zaslona ni uporabljen |

## Dvajset skupin

Ocena avtorja popravkov:

| Ocena | Skupine |
| --- | --- |
| Pokrite | 5, 6, 7, 8, 10 |
| Delne | 1, 2, 3, 17, 18, 19, 20 |
| Nepokrite | / |
| Zunaj obsega T | 4, 9, 11–16 |

Skupaj **5 / 7 / 0 / 8**, enako kot Codex. Skupina 10 je zdaj pokrita tudi pri dejanskem uporabniškem klicu modula (T-02). Pri skupini 17 je trajni zapis dostave zdaj popoln (T-01); izgubljeni odgovor 202 in prava M1/M2 manjkata, zato ostaja delna.

## Preostale naloge in odločitve

| Naloga | Kdo |
| --- | --- |
| Ročni pregled z NVDA ali Orca po [pregledu dostopnosti](../projekt/pregled-dostopnosti-P0.md) | človek, ki ga imenuje pobudnik |
| D08: pravni pregled obrazca in izjave mladoletnih avtorjev pred prvim PR dijaka | šola, mentor |
| Prava M1/M2: izpad, trajnost, SMTP (točka 8, skupine 17–19) | ekipi |
| Drugi človeški skrbnik in namestnik D14 | pred produkcijskim pilotom ([vloge skrbnikov](../projekt/odlocitve.md#vloge-skrbnikov-13-novembra-2026)) |
| Razporejevalnik čiščenja, HTTPS/HSTS v produkciji | namestitev (D04) |
| SBOM, vgrajene knjižnice `psycopg-binary`, pravni pregled licenc | pred prvo distribucijo slike |
| Človeški sprejem poročil in tega zapisa | pobudnik |

Znane omejitve:
- **Skrbniški vmesnik:** skrbnik brez osebe v evidenci je v sledi brez imena. Vpogled se zapiše tudi ob zavrnjenem poskusu brisanja.
- **Manjkajoča sled:** vpogledi v seznam oseb in admin pred PR #69 v sledi manjkajo.
- **Meja modulov:** imena, sestavljena med izvajanjem, in surovi SQL ostanejo na človeškem pregledu.
- **Zamrznitev v CI:** preverjanje `zamrznitev-pogodbe` je obvezno le, če pravilo »Zascita main« zahteva preverjanja CI. Trenutno jih ne zahteva.
