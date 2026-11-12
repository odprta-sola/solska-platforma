# Odprava ugotovitev ponovnega neodvisnega pregleda P0

Status: osnutek, 12. november 2026. Ta zapis ne spreminja poročil pregledovalcev ([Codex/OpenAI](2026-11-ponovni-pregled-P0-openai.md), PR #51; [DeepSeek](2026-11-ponovni-pregled-P0-deepseek.md), PR #52), ki ostaneta dokaz za commit `184c8f9`. Nadaljuje [odpravo prvega pregleda](2026-11-odprava-prvega-pregleda-P0.md). **Ni človeški prevzem, ni potrditev D12 in ne zapira paketa T.**

## Podatki

| Podatek | Vrednost |
| --- | --- |
| Pregledano | `184c8f9` (koda P0 enaka `127f1d5`) |
| Zasebni popravki | `1b71c22` (R-09, R-10; objavljena varnostna nasveta) |
| Javni popravki | PR #53 (uvoz in zasloni), PR #54 (API, format časa, preverjevalnik, testi), ta PR (dokumentacija) |
| Stanje po združitvi kode | `main` = `898ff1a` |
| Izvedel | Claude (Anthropic), model Claude Opus 5.5, po navodilih pobudnika |
| Odgovorni človek | Mitja Pirih; sprejem tega zapisa še ni potrjen |

## Primerjava poročil

Oba pregledovalca prevzema T ne priporočata (DeepSeek jedro P0 pogojno). Oba potrjujeta odpravo S-01 do S-04 in večine ugotovitev prvega kroga. Codex je našel resno tekmo med uvozom in odvzemom (R-09) in več uporabniških ter pogodbenih neskladij; DeepSeek je našel lažno zelen test, napačen prikaz prihodnjih zapisov in opombo o razvojni sliki. Oznake R-xx se med poročiloma ne ujemajo; spodaj so označene s predpono OA oziroma DS. Vsako ugotovitev je avtor popravkov neodvisno ponovil pred popravkom.

## Tabela odprave

| Ugotovitev | Resnost (pregled) | Stanje | Dokaz |
| --- | --- | --- | --- |
| OA R-09 sočasni uvoz in ročni odvzem | visoka | odpravljeno; [nasvet](https://github.com/odprta-sola/solska-platforma/security/advisories/GHSA-mhxg-gwxv-32xw) | `test_varovala_uvoza.ConcurrentRevocationTests` (10, ločene povezave PostgreSQL, oba vrstna reda, zastarel zaslon, vse štiri poti); na izhodišču 10/10 pade |
| OA R-10, DS R-01 rok začasnih datotek | srednja / nizka | odpravljeno; [nasvet](https://github.com/odprta-sola/solska-platforma/security/advisories/GHSA-99hv-w9pg-2mwj) | `UploadExpiryTests`, `UploadPurgeTests` (8, nadzorovana ura, meja ±1 µs); storitev `cleanup` |
| OA R-01 `expires_at` zunaj RFC 3339 | srednja | odpravljeno | `test_ponovni_api.DateTimeFormatTests` (13 zapisov, enakost z validatorjem pogodbe) |
| OA R-02, DS R-03 preveliko telo HTML; `class_id="²"` 500 | srednja / nizka | odpravljeno | `ApiErrorEdgeTests` (DEBUG vklopljen in izklopljen; 8 neveljavnih `class_id`) |
| OA R-03, DS R-02 CSV 500 pri dolgem polju | srednja / nizka | odpravljeno | `test_uvoz_zasloni.CsvLimitTests`, `ScreenErrorTests`; najdena in odpravljena še napaka pri branju glave |
| OA R-04 predogled le 500 postavk | srednja | odpravljeno | `PreviewPagingTests` (501 postavka, sprememba za 500 nespremenjenimi, stabilen vrstni red) |
| OA R-05, DS R-05 320 px | nizka | odpravljeno | brskalnik (Chromium) pri 320 px: prijava, osebe, podrobnosti z 72-znakovnim e-naslovom, kontakt, uvoz brez vodoravnega drsenja strani |
| OA R-06 preverjevalnik pri neznani poti | nizka | odpravljeno | `CheckerUnknownPathTests` |
| OA R-07 dokumentacija | nizka | odpravljeno v tem PR | DEVELOPER, stanje T, kontrolni seznam, odvisnosti, prvi zapis o odpravi |
| OA R-08 lažno sporočilo zavrženja | nizka | odpravljeno | `DiscardOutcomeTests` (dve seji, že zavržena serija) |
| DS R-04 lažno zelen test granta | nizka | odpravljeno | test zdaj preverja varovalo granta; mutacija (onemogočeno varovalo) ga podre |
| DS R-06 prihodnji zapis prikazan kot zaključen | nizka | odpravljeno | `FutureValidityTests` (»še ne velja«, odvzem prihodnjega zapisa) |
| DS R-07 setuptools v razvojni sliki | nizka | opomba, ni napaka | vgrajeni `pkg_resources` v pip; zadeva samo razvojno sliko ([odvisnosti](../projekt/odvisnosti-in-licence.md)) |
| OA opomba: test S-03 z napačnim generatorjem ključa | opomba | odpravljeno | test uporablja generator allauth, preveri veljavnost ključa in odsotnost pošte |
| OA opomba: `seed` pred migracijami | opomba | odpravljeno | healthcheck `p0`; postopek `docker compose up --wait` |
| DS: trditve v DEVELOPER (napake vedno JSON, predogled »samo imena polj«), popis Actions | nizka | odpravljeno v tem PR | |

## Izvedeni ukazi in rezultati

```text
docker compose up --build -d --wait      vse storitve zdrave (p0 po migracijah)
seed_test_data                           naključni SEED_PASSWORD
python manage.py test                    Ran 214 tests. OK (skipped=2)   [main = 898ff1a]
ruff check / format --check              čisto
makemigrations --check --dry-run         No changes detected
scripts/check_docs_links.py              veljavno
```

Preskočena sta podtesta meje modulov M1 in M2 (mapi še ne obstajata). Mutacije (odstranjeno varovalo → test pade): ključavnica uvoza, odvzem le ene vrstice, rok v transakciji, iztek ob ogledu, varovalo granta. Prvi poskus mutacije roka v transakciji je razkril napačno zasnovan test (zamenjal je globalno uro); test je popravljen in mutacijo zdaj zazna.

Ni izvedeno, z razlogom: pip-audit in Trivy (odvisnosti in slike niso spremenjene od prejšnjega skeniranja); ročni pregled z bralnikom zaslona (potreben človek); uvoz z izbiro datotek v brskalniku (izbira datotek v uporabljenem brskalniku ni mogoča; pokrito s testi).

## Devet točk

| # | Točka | Stanje |
| --- | --- | --- |
| 1 | Lastni otroci, tuja družina zavrnjena | izpolnjeno (testi; ročna ponovitev pregledovalcev) |
| 2 | Skupen kontakt, ločena računa | izpolnjeno (testi; ročna ponovitev pregledovalcev) |
| 3 | Odvzem povezave ali upravičenja | izpolnjeno za neposredni odvzem, zaslon in uvoz, tudi sočasni |
| 4 | CSV brez delnega prepisa, ponovitev, sled | izpolnjeno za preizkušene primere; predogled celoten |
| 5 | Omejen servisni kontaktni klic | ni izpolnjeno: klic zaprt (503) do D12 |
| 6 | Pregled kode | dvakrat pregledala sistema AI; človeški pregled ni izveden |
| 7 | Pogodbeni testi po ponastavitvi | izpolnjeno v okviru nadomestkov |
| 8 | Izpad P0, varno zadržanje | ni izpolnjeno: prava M1/M2 ne obstajata |
| 9 | Tipkovnica, fokus, napake, bralnik | ni izpolnjeno: bralnik zaslona ni uporabljen |

## Dvajset skupin

Ocena avtorja popravkov, z razliko do pregledovalcev: pokrite **5, 6, 7, 8** (6 po odpravi R-09, 7 po odpravi R-03); delne **1, 2, 3, 10, 17, 18, 20** (10 ostane delna, ker delegiranje avtorja čaka D12; DeepSeek jo ocenjuje kot pokrito); nepokrita **19**; zunaj obsega T **4, 9, 11–16**. Skupaj **4 / 7 / 1 / 8**. Codex je ocenil 2/9/1/8, DeepSeek 5/6/1/8; razliki pri 6 in 7 izhajata iz popravkov po njunem pregledu in nista potrjeni s tretjim pregledom.

## Preostale naloge in odločitve

| Naloga | Kdo |
| --- | --- |
| Ročni pregled z NVDA ali Orca po [pregledu dostopnosti](../projekt/pregled-dostopnosti-P0.md) | človek, ki ga imenuje pobudnik |
| D12: vezava kontakta na dostavo, delegiranje avtorja, identiteta postavke, več obsegov iste osebe, namensko dovoljenje kontakta, hramba ključev idempotence ([paket](../projekt/d12-paket-za-odlocitev.md)) | tehnični nosilec in mentorji |
| Prava M1/M2: izpad, trajnost, SMTP (točka 8, skupini 17–19) | ekipi po D12 |
| Razporejevalnik čiščenja, HTTPS/HSTS v produkciji | namestitev (D04) |
| SBOM, vgrajene knjižnice `psycopg-binary`, pravni pregled licenc | pred prvo distribucijo slike |
| Individualna aktivacija/obnova, izvoz | pred B |
| Tretji neodvisni pregled po teh popravkih | pobudnik |

Znane omejitve popravkov: odvzem zapisa, ki šele začne veljati, ga zaključi 1 µs po začetku (zahteva ograde veljavnosti); sprememba veljavnosti neposredno v Django adminu ne gre skozi `authz` in ključavnice; dve sočasni različni seriji lahko PostgreSQL zaradi zastoja prekine (serija `failed`, brez delnega vpisa).
