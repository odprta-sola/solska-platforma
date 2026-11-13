# Navodilo za ponovni neodvisni pregled P0

Status: izvedeno (drugi krog, 12. november 2026); za naslednji krog velja [navodilo za tretji pregled](navodilo-za-tretji-pregled.md). Navodilo je za oba pregledovalca prvega pregleda (Codex/OpenAI in DeepSeek). Besedilo spodaj pobudnik prilepi vsakemu posebej; razlikujeta se le oznaka sistema v imenu veje in poročila. Pregled z AI je osebna odločitev pobudnika ([register](odlocitve.md)); ni potrjen kot enakovreden človeškemu prevzemu.

Opomba o neodvisnosti: kodo faz 0 do 6 je napisal Claude Sonnet 5.5, popravke po prvem pregledu Claude Opus 5.5 (oba Anthropic) po navodilih pobudnika. Pregledovalca sta v prvem krogu sama poročala ugotovitve, katerih odpravo zdaj preverjata. To mora pregledovalec razkriti v poročilu.

---

## Besedilo navodila (prilepi pregledovalcu)

Si neodvisni pregledovalec odprtokodnega projekta »Odprta šola« (šolska platforma za obvestila in soglasja, Django 5.2, PostgreSQL 16). Kode nisi napisal ti. V prvem krogu si pregledal commit `e854f60`; zdaj preverjaš, ali so ugotovitve prvega pregleda res odpravljene in ali popravki niso uvedli novih težav. Kode ne popravljaj.

**Repozitorij:** https://github.com/odprta-sola/solska-platforma, veja `main`, commit `184c8f9` ali novejši, če ga pobudnik izrecno določi. Na začetku zapiši SHA, ki ga pregleduješ.

**Tvoja oznaka** (uporabi jo v imenu veje in poročila): `openai` za Codex/OpenAI, `deepseek` za DeepSeek.

### Pravila

1. **Ne spreminjaj `main`.** Če imaš pisalni dostop, ustvari vejo `pregled-p0-ponovni-<oznaka>`; sicer poročilo izročiš pobudniku v pogovoru.
2. **Ne popravljaj kode.** Edina sprememba v veji je tvoje poročilo. Registra prispevkov tokrat ne spreminjaj; vpis iz prvega kroga ostane, pobudnik ga dopolni sam.
3. **Samo izmišljeni podatki.** Testno geslo in servisne žetone ustvari naključno; ne zapisuj jih v poročilo ali repozitorij.
4. **Nove varnostno občutljive ugotovitve ne gredo v javni pull request ali issue.** Opiši jih pobudniku v pogovoru oziroma jih prijavi zasebno po [SECURITY.md](../../SECURITY.md). V javno poročilo zapiši le število in resnost. Štiri ugotovitve prvega kroga (S-01 do S-04) so že javno objavljene kot varnostni nasveti; njihovo preverjanje smeš opisati javno.
5. **Poročaj dejansko.** Kar nisi izvedel, označi »ni izvedeno« z razlogom. Če test pade, zapiši izpis. Ne prepisuj ocen iz zapisa o odpravi brez lastnega preverjanja.
6. **Ne ugibaj o sebi.** Ime sistema in ponudnik; verzije modela ne ugibaj.

### Branje

- Svoje poročilo prvega kroga in poročilo drugega pregledovalca: `docs/pregledi/2026-11-prvi-pregled-P0-openai.md`, `…-deepseek.md`
- [Zapis o odpravi](../pregledi/2026-11-odprava-prvega-pregleda-P0.md): kaj avtor popravkov trdi, da je odpravljeno, delno ali odprto
- Objavljeni varnostni nasveti S-01 do S-04: https://github.com/odprta-sola/solska-platforma/security/advisories
- [Kontrolni seznam](pregled-P0-kontrolni-seznam.md), [stanje T](stanje-prevzema-T.md), [register odločitev](odlocitve.md) (odločitve pobudnika 12. 11. 2026)
- [Pregled dostopnosti](pregled-dostopnosti-P0.md), [odvisnosti in licence](odvisnosti-in-licence.md)
- `DEVELOPER.md`, `SECURITY.md`, `api/openapi.yaml`

### Zagon

Kot v kontrolnem seznamu: `docker compose up --build -d`, `seed_test_data` z lastnim `SEED_PASSWORD`, `manage.py test`. Dodatno: gradnja `docker compose build --no-cache p0`, po koncu `docker compose down -v` in ponovni zagon pogodbenih testov. Zapiši okolje, različice in število testov (pričakovano 173, od tega 2 izrecno preskočena; preveri razlog preskoka).

### Pregled

1. **Preverjanje odprave.** Za vsako svojo ugotovitev iz prvega kroga in vsako ugotovitev drugega pregledovalca: ponovi prvotno reprodukcijo na novem commitu in zapiši rezultat (odpravljeno / delno / ni odpravljeno / ne velja več), z ukazom ali testom. Posebej:
   - S-01: klic `delivery-contacts/resolve` ne sme vrniti kontakta za noben vhod (začasna zapora do D12); preveri, da odgovor ne razlikuje tujih, neobstoječih in odvzetih sklicev.
   - S-02: ročni odvzem povezave ali upravičenja ostane učinkovit pri uvozu s spremenjenim začetkom veljavnosti, vrsto povezave ali obojim; preveri vse štiri poti (`/me/relationships`, `audiences/resolve`, `authorizations/check`, `delivery-contacts/resolve`).
   - S-03: nobena pot pod `/accounts/password/reset/` ne izda povezave ali spremeni gesla, tudi prej izdan ključ ne.
   - S-04: tajništvo z uvozom ne dodeli vloge `admin` ali `office` na novo; ponovni uvoz obstoječe vloge ostane dovoljen.
   - P0-01 do P0-11 iz poročila OpenAI in P0-01 do P0-06 iz poročila DeepSeek.
2. **Nova koda.** Popravki so dodali precej kode; preglej jo enako strogo kot v prvem krogu:
   - `p0/core/middleware.py`, `p0/core/views.py` (pretvorba napak, CSRF): ali kakšna napaka razkrije podrobnosti ali prikrije zavrnitev kot uspeh?
   - `p0/registry/contract_schemas.py`: ali se sheme ujemajo s `api/openapi.yaml` in ali preverjevalnik pravilno zavrne neveljavne vhode?
   - `p0/registry/importer.py`: vezava na načrt predogleda, zaklep serije, varovalo ročnega odvzema, pravilo vlog.
   - `p0/registry/ui.py`, `forms.py`, predloge v `p0/templates/`: zasloni evidence. Preveri dostop po vlogah, ugibanje ID oseb, povezav in upravičenj druge osebe, CSRF, ubežanje izpisa (XSS), nalaganje datotek (velikost, ime, vsebina), hrambo `ImportUpload` (osebni podatki, brisanje po 24 urah), sporočila in sled.
   - `p0/Dockerfile`, `requirements*.lock`, `.github/workflows/p0.yml`, `.github/dependabot.yml`: ali je zaklep s hashi res uveljavljen, ali so reference pripete, ali CI preveri, kar trdi.
3. **Testi.** Ali novi testi (`test_varovala.py`, `test_robni.py`, `test_zasloni.py`, `test_dostopnost.py`, `contract_check.py`) res padejo, če popravek odstraniš? Izberi vsaj tri popravke, jih začasno razveljavi v lastni kopiji in zapiši rezultat. Iščemo lažno zelene teste.
4. **Devet točk in dvajset skupin.** Ponovno oceni vseh 9 točk kontrolnega seznama in 20 skupin preizkusov kratke specifikacije (pokrit / delno / nepokrit / ni v obsegu T). Primerjaj z oceno v zapisu o odpravi in pojasni vsako razliko.
5. **Dostopnost (točka 9).** Ponovi, kar lahko preveriš brez bralnika zaslona (struktura, oznake, fokus, napake, širina 320 px). Ročni pregled z bralnikom zaslona opravi človek; ne trdi, da je izveden.
6. **Odvisnosti.** Ponovi `pip-audit` za vse tri zaklepe in, če lahko, skeniranje slike. Primerjaj z zapisom v [odvisnostih in licencah](odvisnosti-in-licence.md).
7. **Dokumentacija.** Trditve, ki jih koda ali izvedeni ukazi ne podpirajo.

### Poročilo

Ustvari datoteko `docs/pregledi/2026-11-ponovni-pregled-P0-<oznaka>.md` z razdelki:

1. Podatki: datum, commit SHA, okolje, sistem in ponudnik, razkritje neodvisnosti (glej opombo zgoraj), odgovorni človek (Mitja Pirih; sprejem še ni potrjen).
2. Povzetek: ali bi prevzem T zdaj priporočal (da / ne / pogojno, s pogoji); kaj ostaja.
3. Tabela odprave: ID iz prvega kroga (obeh poročil), prejšnja resnost, novo stanje, dokaz.
4. Nove ugotovitve: ID (`R-01` …), resnost, kje, opis, ponovljiv korak, predlog. Varnostno občutljive samo štetje (pravilo 4).
5. Rezultat preizkusa testov (točka 3).
6. Devet točk in dvajset skupin, z razlikami do zapisa o odpravi.
7. Odvisnosti.
8. Omejitve pregleda.
9. Izjava: pregled ni človeški prevzem, ni pravno mnenje in ni potrditev D12.

Commit s sporočilom `docs: ponovni neodvisni pregled P0 (<sistem>)`, pull request z veje `pregled-p0-ponovni-<oznaka>` proti `main`; opis naj vsebuje samo povzetek in pot do poročila. Če pull requesta ne moreš odpreti, izroči poročilo pobudniku v pogovoru.

---

## Po pregledu (pobudnik)

1. Poročili prebere človek in zabeleži sprejem ali zavrnitev v [registru](odlocitve.md).
2. Nove zasebne ugotovitve se obravnavajo po [SECURITY.md](../../SECURITY.md).
3. Sprejem prevzema T ostaja odločitev pobudnika; poleg pregleda so pogoji še ročni pregled dostopnosti (točka 9), točka 8 in potrditev D12.
