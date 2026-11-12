# Pregled dostopnosti P0 (točka 9)

Status: osnutek, 12. november 2026. Točka 9 [kontrolnega seznama](pregled-P0-kontrolni-seznam.md) ostaja **odprta**, dokler človek ne opravi ročnega pregleda spodaj. Dogovorjeni zasloni za osnovna opravila obstajajo (glej spodaj). Avtomatski preizkusi in pregled HTML ročnega preizkusa ne nadomestijo.

## Kaj je narejeno

Prijava in odjava imata lastni predlogi (`p0/templates/allauth/layouts/base.html`, `p0/templates/account/login.html`): `lang="sl"`, naslov strani, preskok na vsebino, ena glavna regija in en naslov `h1`, oznaka za vsako polje, viden fokus (`:focus-visible`), povzetek napak z `role="alert"`, na katerega se ob napaki premakne fokus, povezave iz povzetka v polja, napaka pri polju povezana z `aria-describedby` in označena z `aria-invalid`, besedilo »Napaka:« poleg barve. Prijava ne kaže povezave na zaprto samoregistracijo; sporočilo ne razlikuje med neznanim uporabnikom in napačnim geslom.

Avtomatski dokaz: `registry/tests/test_dostopnost.py` (8 testov; na prejšnji predlogi jih 6 pade).

## Zasloni evidence

Pod `/p0/evidenca/` (samo vloga tajništvo ali skrbnik, sicer 403; neprijavljen uporabnik gre na prijavo): seznam oseb z iskanjem in strani, podrobnosti osebe (vloge, povezave, upravičenja z dejanskim stanjem, zadnje spremembe), odvzem povezave ali upravičenja s potrditveno stranjo, popravek kontakta in uvoz CSV (predogled, pregled težav in sprememb, uveljavitev ali zavrženje). Vsi uporabljajo isto postavitev in vzorec napak kot prijava; tabele imajo glave s `scope` in se na ozkem zaslonu drsijo znotraj regije, ki jo doseže tipkovnica.

Avtomatski dokaz: `registry/tests/test_zasloni.py` (25 testov: dostop po vlogah, CSRF, delovanje, sled, ubežanje izpisa, struktura strani).

Omejen preizkus z AI v vgrajenem brskalniku (Chromium, `docker compose` iz repozitorija, slika zgrajena brez predpomnilnika, izmišljeni računi), **ne s bralnikom zaslona**:

| Preverjeno | Rezultat |
| --- | --- |
| Vrstni red fokusa s tipko Tab | preskok, Prijava, uporabniško ime, geslo, zapomni si me, gumb |
| Viden fokus na vsakem elementu | da (obroba 3 px) |
| Oddaja s tipko Enter, napačno geslo | povzetek »Prijava ni uspela«, fokus na povzetku |
| Oddaja praznega obrazca | povzetek z dvema povezavama; Enter na povezavi premakne fokus v polje; polji `aria-invalid`, opis napake povezan |
| Širina 375 px | prijava, začetek, osebe, podrobnosti, kontakt, uvoz: brez vodoravnega drsenja strani (popravljeno med preizkusom: navigacija se ni prelamljala, skrito besedilo v tabeli je širilo stran) |
| Osebe in podrobnosti s tipko Tab | preskok, navigacija, nazaj, popravi kontakt, regija tabele, odvzem z opisnim imenom (»Odvzemi povezavo z …«) |
| Odvzem povezave s tipkovnico | potrditvena stran, Enter na »Odvzemi«, vrnitev s sporočilom (`role="status"`); upravičenje na zaključeni povezavi je prikazano kot »ne velja« (popravljeno med preizkusom) |
| Kontakt z neveljavnim naslovom | povzetek napak s fokusom, polje `aria-invalid`, opisano s pomočjo in napako |
| Uvoz CSV v brskalniku | **ni preizkušeno** (izbira datotek v vgrajenem brskalniku); pokrito samo z avtomatskimi testi |

Ni preverjeno: bralnik zaslona, povečava 200 % in 400 %, kontrast z orodjem, visok kontrast operacijskega sistema, glasovno upravljanje, razumljivost besedil z uporabniki.

## Ročni pregled za človeka

Izvede ga oseba, ki kode ni pisala. Zapišite datum, brskalnik, operacijski sistem, bralnik zaslona z različico in rezultat vsake vrstice (uspešno, ne, opomba).

Priprava: `docker compose up --build -d --wait`, `seed_test_data` z lastnim `SEED_PASSWORD`, odprite `http://localhost:8000/accounts/login/`. Priporočeni par: NVDA s Firefoxom (Windows) ali Orca s Firefoxom (Linux); po možnosti še VoiceOver s Safarijem.

| # | Korak | Pričakovano |
| --- | --- | --- |
| 1 | Samo s tipkovnico: Tab od začetka strani | Prvi je »Preskoči na vsebino« in je viden; vrstni red je logičen; fokus je vedno viden |
| 2 | Bralnik: naslov strani, jezik, glavne regije | Prebere »Prijava – Odprta šola«, slovenski izgovor, regijo navigacije in glavno vsebino |
| 3 | Bralnik: polja | Vsako polje prebere z oznako; pri geslu tudi pomoč |
| 4 | Oddaja praznega obrazca s tipko Enter | Bralnik prebere povzetek napak; povezava v povzetku premakne v polje; pri polju prebere napako |
| 5 | Napačno geslo | Razumljivo sporočilo, brez razkritja, ali račun obstaja |
| 6 | Uspešna prijava in odjava samo s tipkovnico | Prijava uspe; odjava je gumb, potrditev je dosegljiva s tipkovnico |
| 6a | Tajništvo: iskanje osebe, podrobnosti, odvzem s potrditvijo, popravek kontakta | Vse s tipkovnico; bralnik prebere naslove tabel, stanje in namen povezav |
| 6b | Tajništvo: uvoz (izbira datotek, predogled, težave, uveljavitev, zavrženje) | Izbira datotek in gumbi dosegljivi s tipkovnico; težave prebrane v povzetku |
| 7 | Povečava 200 % in 400 % | Vsebina ostane berljiva, brez vodoravnega drsenja pri 320 px širine |
| 8 | Kontrast | Besedilo in obrobe polj ustrezajo WCAG 2.2 AA |
| 9 | Razumljivost | Testni uporabnik (npr. starš) razume navodilo in napake |

## Obseg zaslonov za T

Točka 9 zahteva »prijavo in osnovna opravila«. Obseg je osebno sprejel pobudnik 12. 11. 2026 ([register odločitev](odlocitve.md#osebni-sprejemi-pobudnika-12-novembra-2026)):

1. Prijava in odjava (narejeno).
2. Uvoz CSV za tajništvo: izbira datotek, predogled s težavami in spremembami, uveljavitev ali zavrnitev (narejeno).
3. Seznam oseb z iskanjem in podrobnosti osebe (vloge, povezave, upravičenja) za tajništvo, z odvzemom povezave ali upravičenja in potrditvijo (narejeno).
4. Popravek kontakta osebe s sledjo spremembe (narejeno).

Ni v obsegu T: celoten administrativni portal, izvoz, zasloni za starše zunaj M1/M2 (ti so v modulih). Vsak zaslon dobi enake avtomatske preizkuse in vrstico v ročnem pregledu.
