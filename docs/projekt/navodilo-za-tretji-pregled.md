# Navodilo za tretji neodvisni pregled P0

Status: pripravljeno 13. novembra 2026 za pregled commita `d261ace`. Navodilo je za oba pregledovalca prejšnjih krogov (Codex/OpenAI in DeepSeek). Pobudnik ga prilepi vsakemu posebej; razlikujeta se le v oznaki sistema v imenu veje in poročila. Pregled z AI je osebna odločitev pobudnika ([register](odlocitve.md)) in ni potrjen kot enakovreden človeškemu prevzemu. Prejšnje navodilo: [ponovni pregled](navodilo-za-ponovni-pregled.md).

Opomba o neodvisnosti, ki jo mora pregledovalec razkriti v poročilu:
- Kodo faz 0 do 6 je napisal Claude Sonnet 5.5, vse poznejše popravke in dopolnitve pa Claude Opus 5.5. Oba sta modela podjetja Anthropic; delala sta po navodilih pobudnika.
- Pregledovalca sta v prejšnjih krogih sama poročala ugotovitve, katerih odpravo zdaj preverjata.

---

## Besedilo navodila (prilepi pregledovalcu)

Si neodvisni pregledovalec odprtokodnega projekta »Odprta šola«. To je šolska platforma za obvestila in soglasja na Django 5.2 in PostgreSQL 16. Kode nisi napisal ti. V prejšnjih krogih si pregledal commita `e854f60` in `184c8f9`. Zdaj preverjaš dvoje: ali ugotovitve drugega kroga ostajajo odpravljene in ali je koda, dodana po drugem krogu, ustrezna. Kode ne popravljaj.

**Repozitorij:** https://github.com/odprta-sola/solska-platforma, veja `main`, commit `d261ace` ali novejši, če ga pobudnik izrecno določi. Na začetku zapiši SHA, ki ga pregleduješ. Pogodba je označena z `v1.0.0` (commit `68fea19`).

**Tvoja oznaka** (uporabi jo v imenu veje in poročila): `openai` za Codex/OpenAI, `deepseek` za DeepSeek.

### Kaj se je spremenilo od drugega kroga

| PR | Vsebina | Glavne datoteke |
| --- | --- | --- |
| #56 | D12, točke A: predogled občinstva z avtorjevo sejo, shranjen posnetek, kontakt samo za prejemnika iz posnetka, postavke dostave | `p0/registry/api.py`, `models.py`, `api/openapi.yaml` |
| #57, #58 | Licenciranje prispevkov (DCO, preverjanje avtorja), gradivo za varstvo podatkov | `CONTRIBUTING.md`, `.github/`, `docs/projekt/varstvo-podatkov-P0.md` |
| #59 | Brisanje poteklih posnetkov občinstva | `p0/registry/audiences.py`, ukaz `purge_audience_snapshots`, storitev `cleanup` |
| #60 | Sled vpogledov zaposlenih | `AccessAudit`, `p0/registry/ui.py` |
| #61 | Izvoz podatkov ene osebe | `p0/registry/export.py`, `ui.person_export` |
| #62 | Postopek ob kršitvi varstva podatkov | `SECURITY.md` |
| #63 | D12, točke B: nadomestka M1/M2 s trajnim zapisom, okno idempotence, poslovni ključ, `need_ref` na postavko, obdelava (odvzem, urnik, iztek, jezik, negotova predaja) | `p0/stubs/`, `api/openapi.yaml` |
| #64 | Vloge naročnik–izvajalec, sprejem D12, zamrznitev pogodbe `1.0.0` | `docs/projekt/odlocitve.md`, `api/zamrznitve.txt` |
| #65 | Ogrodje modulov M1 in M2, skupni odjemalec API, usmerjanje nadomestek ali pravi modul | `p0/core/api_client.py`, `p0/core/testing.py`, `p0/m1/`, `p0/m2/`, `p0/config/urls.py` |

### Pravila

1. **Ne spreminjaj `main`.** Če imaš pisalni dostop, ustvari vejo `pregled-p0-tretji-<oznaka>`. Sicer poročilo izročiš pobudniku v pogovoru.
2. **Ne popravljaj kode.** Edina sprememba v veji je tvoje poročilo. Registra prispevkov ne spreminjaj.
3. **Samo izmišljeni podatki.** Testno geslo in servisne žetone ustvari naključno in jih ne zapisuj v poročilo ali repozitorij.
4. **Nove varnostno občutljive ugotovitve ne gredo v javni pull request ali issue.** Prijavi jih zasebno po [SECURITY.md](../../SECURITY.md) ali jih opiši pobudniku v pogovoru. V javno poročilo zapiši le število in resnost. Šest že objavljenih nasvetov (S-01 do S-04, R-09, R-10) smeš opisati javno.
5. **Poročaj dejansko.** Kar nisi izvedel, označi »ni izvedeno« in navedi razlog. Če test pade, zapiši izpis. Ocen iz zapisov o odpravi ne prepisuj brez lastnega preverjanja.
6. **Ne ugibaj o sebi.** Navedi ime sistema in ponudnika, verzije modela ne ugibaj.

### Branje

- Poročila obeh prejšnjih krogov in zapisa o odpravi v `docs/pregledi/`.
- Objavljeni varnostni nasveti: https://github.com/odprta-sola/solska-platforma/security/advisories
- [Pogodba](../arhitektura/vmesnik-P0-M1-M2.md), [OpenAPI](../../api/openapi.yaml), [paket D12](d12-paket-za-odlocitev.md) (tabela B s stolpcem »Izvedba«).
- [Register odločitev](odlocitve.md), posebej razdelek »Vloge naročnik in izvajalec«.
- [Kontrolni seznam](pregled-P0-kontrolni-seznam.md), [stanje T](stanje-prevzema-T.md), [varstvo podatkov](varstvo-podatkov-P0.md), [pregled dostopnosti](pregled-dostopnosti-P0.md), [odvisnosti in licence](odvisnosti-in-licence.md).
- [Navodila za razvijalce](../razvijalci/README.md), `DEVELOPER.md`, `SECURITY.md`.

### Zagon

Zaženi po kontrolnem seznamu:
1. `docker compose up --build -d --wait`;
2. `seed_test_data` z lastnim `SEED_PASSWORD`;
3. `manage.py test`.

Dodatno izvedi `docker compose build --no-cache p0`, po koncu `docker compose down -v` in ponovni zagon testov. Zapiši okolje, različice in število testov. Pričakovano je **275 testov, 0 preskočenih**; meje modulov se zdaj preverjajo. Če dobiš drugačno število, ga zapiši in pojasni.

### Pregled

1. **Preverjanje odprave drugega kroga.** Za vsako ugotovitev drugega kroga (OA R-01 do R-10, DS R-01 do R-07) ponovi prvotno reprodukcijo na novem commitu. Zapiši rezultat (odpravljeno / delno / ni odpravljeno / ne velja več) z ukazom ali testom. Posebej preveri, da R-09 (sočasni uvoz in odvzem) in R-10 (rok začasnih datotek) ostajata odpravljena.

2. **Kontakt in posnetek občinstva (S-01, D12 C07).**
   - Kontakt se vrne samo za prejemnika s tem sklicem v neizteklem posnetku in ob aktualnem upravičenju za namen posnetka.
   - Tuj, neobstoječ, potekel, izbrisan (po `purge_audience_snapshots`) in odvzet vhod morajo dati enak 403.
   - Ali je mogoče z ugibanjem `audience_ref`, `scope_ref` ali `recipient_id` pridobiti kontakt ali ugotoviti obstoj?
   - Ali sme avtor ustvariti posnetek za oddelek, kjer nima veljavne dodelitve?

3. **Varstvo podatkov (PR #59 do #62).**
   - Sled vpogledov: ali vsak zaslon, ki prikaže podatke osebe, zapis ustvari *pred* prikazom? Ali kaj prikaže podatke brez zapisa (npr. napake, preusmeritve, `/admin/`)? Ali sled hrani vsebino, ki je ne bi smela?
   - Izvoz: dostop po vlogah, POST s CSRF, brez gesla in sej, brez tujih kontaktov in ID-jev drugih oseb. Ali varovalo `test_vsi_modeli_z_osebo_so_zajeti` res zazna nov model?
   - Brisanje posnetkov: meja roka in vpliv na dostave, ki se nanje sklicujejo.
   - `SECURITY.md`, razdelek o kršitvah: notranja skladnost in trditve, ki jih koda ne podpira (npr. orodja za zajezitev).

4. **Nadomestka po točkah B (PR #63).** Nadomestka sta referenca obnašanja za ekipi, zato sta pomembna kot pogodba.
   - Ali se ujemata z `api/openapi.yaml` in opisom v pogodbi?
   - Trajni zapis pred 202 in izpad.
   - Okno ponovitve 30 dni in poslovni ključ `event_key`, vključno s sočasnima zahtevama in potjo `IntegrityError`.
   - Vrstni red preverjanj v `_stub/process`.
   - Urnik (delavniki 7–20, Europe/Ljubljana, prehod poletnega časa) in iztek.
   - Negotova predaja in preklic.
   - `need_ref`: tuj ali potekel sklic ni »nepotreben«.
   - Ali so pomožne poti `/_stub/*` in tabele nadomestkov res nedosegljive v produkcijskem načinu (`STUBS` samo z `DJANGO_DEBUG=1`)?

5. **Ogrodje modulov in odjemalec API (PR #65).**
   - `core/api_client.py`: ali posredovanje seje in CSRF ustreza C04/C05? Preveri:
     - ali lahko vrednost piškotka ali glave povzroči vbrizg glave ali razkritje seje ali žetona;
     - ali so časovne omejitve in obravnava napak (5xx, odgovor brez JSON, omrežna napaka) pravilne;
     - ali je `P0_API_URL` mogoče zlorabiti.
   - Usmerjanje (`config/urls.py`): nadomestek ali pravi modul glede na `STUBS`.
   - Test meja modulov (`core/tests/test_boundaries.py`): ali ga je mogoče obiti, npr. z `importlib` ali relativnim uvozom? Oceni, ali je to za učno okolje pomembno.

6. **Zamrznitev pogodbe (PR #64).** Ali `test_pogodba_je_zamrznjena_razlicica` pade ob vsaki spremembi `api/openapi.yaml` brez nove različice? Ali so `api/zamrznitve.txt`, oznaka `v1.0.0` in dokumentacija skladni?

7. **Testi.** Ali novi testi res padejo, če popravek odstraniš? Izberi vsaj pet pravil iz točk 2 do 6, jih začasno razveljavi v lastni kopiji in zapiši rezultat. Iščemo lažno zelene teste.

8. **Devet točk in dvajset skupin.** Ponovno oceni vseh 9 točk kontrolnega seznama in 20 skupin preizkusov kratke specifikacije (pokrit / delno / nepokrit / ni v obsegu T). Primerjaj z zapisom o odpravi drugega kroga in s [stanjem T](stanje-prevzema-T.md) ter pojasni vsako razliko.

9. **Dostopnost (točka 9).** Ponovi, kar lahko preveriš brez bralnika zaslona: strukturo, oznake, fokus, napake in širino 320 px. Vključi novi gumb za izvoz in zaslona `/m1/`, `/m2/`. Ročni pregled z bralnikom zaslona opravi človek, zato ne trdi, da je izveden.

10. **Odvisnosti.** Ponovi `pip-audit` za vse tri zaklepe in, če lahko, skeniranje slike. Primerjaj z [odvisnostmi in licencami](odvisnosti-in-licence.md).

11. **Dokumentacija.** Poišči trditve, ki jih koda ali izvedeni ukazi ne podpirajo, posebej v navodilih za razvijalce in ekipi M1/M2. Po teh navodilih bodo delali dijaki.

### Poročilo

Ustvari datoteko `docs/pregledi/2026-11-tretji-pregled-P0-<oznaka>.md` z razdelki:

1. Podatki: datum, commit SHA, okolje, sistem in ponudnik, razkritje neodvisnosti (glej opombo zgoraj), odgovorni človek (Mitja Pirih; sprejem še ni potrjen).
2. Povzetek: ali bi prevzem T zdaj priporočal (da / ne / pogojno, s pogoji). Ali so navodila in ogrodje dovolj zanesljiva, da ekipi začneta delo? Kaj ostaja?
3. Tabela odprave: ID iz drugega kroga (obeh poročil), prejšnja resnost, novo stanje, dokaz.
4. Nove ugotovitve: ID (`T-01` …), resnost, kje, opis, ponovljiv korak, predlog. Varnostno občutljive ugotovitve samo prešteješ (pravilo 4).
5. Rezultat preizkusa testov (točka 7).
6. Devet točk in dvajset skupin, z razlikami.
7. Odvisnosti.
8. Omejitve pregleda.
9. Izjava: pregled ni človeški prevzem in ni pravno mnenje.

Commit naj ima sporočilo `docs: tretji neodvisni pregled P0 (<sistem>)` in podpis DCO (`git commit -s`), sicer ga CI zavrne. Pull request odpri z veje `pregled-p0-tretji-<oznaka>` proti `main`; opis naj vsebuje samo povzetek in pot do poročila. Če pull requesta ne moreš odpreti, izroči poročilo pobudniku v pogovoru.

---

## Po pregledu (pobudnik)

1. Poročili prebere človek in zabeleži sprejem ali zavrnitev v [registru](odlocitve.md).
2. Nove zasebne ugotovitve se obravnavajo po [SECURITY.md](../../SECURITY.md).
3. Sprejem prevzema T ostaja odločitev pobudnika. Poleg pregleda sta pogoja še ročni pregled dostopnosti (točka 9) in točka 8. D12 je sprejet (pogodba `1.0.0`). Za vključitev dijakov veljajo še D09/D14 (pisni sprejem namestnika) in pravni pregled obrazca D08.
