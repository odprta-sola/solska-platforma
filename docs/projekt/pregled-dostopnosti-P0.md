# Pregled dostopnosti P0 (točka 9)

Status: osnutek, 12. november 2026. Točka 9 [kontrolnega seznama](pregled-P0-kontrolni-seznam.md) ostaja **odprta**, dokler človek ne opravi ročnega pregleda spodaj in dokler ne obstajajo dogovorjeni zasloni za osnovna opravila. Avtomatski preizkusi in pregled HTML ročnega preizkusa ne nadomestijo.

## Kaj je narejeno

Prijava in odjava imata lastni predlogi (`p0/templates/allauth/layouts/base.html`, `p0/templates/account/login.html`): `lang="sl"`, naslov strani, preskok na vsebino, ena glavna regija in en naslov `h1`, oznaka za vsako polje, viden fokus (`:focus-visible`), povzetek napak z `role="alert"`, na katerega se ob napaki premakne fokus, povezave iz povzetka v polja, napaka pri polju povezana z `aria-describedby` in označena z `aria-invalid`, besedilo »Napaka:« poleg barve. Prijava ne kaže povezave na zaprto samoregistracijo; sporočilo ne razlikuje med neznanim uporabnikom in napačnim geslom.

Avtomatski dokaz: `registry/tests/test_dostopnost.py` (8 testov; na prejšnji predlogi jih 6 pade).

Omejen preizkus z AI v vgrajenem brskalniku (Chromium, lokalni strežnik, izmišljeni računi), **ne s bralnikom zaslona**:

| Preverjeno | Rezultat |
| --- | --- |
| Vrstni red fokusa s tipko Tab | preskok, Prijava, uporabniško ime, geslo, zapomni si me, gumb |
| Viden fokus na vsakem elementu | da (obroba 3 px) |
| Oddaja s tipko Enter, napačno geslo | povzetek »Prijava ni uspela«, fokus na povzetku |
| Oddaja praznega obrazca | povzetek z dvema povezavama; Enter na povezavi premakne fokus v polje; polji `aria-invalid`, opis napake povezan |
| Širina 375 px | brez vodoravnega drsenja |

Ni preverjeno: bralnik zaslona, povečava 200 % in 400 %, kontrast z orodjem, visok kontrast operacijskega sistema, glasovno upravljanje, razumljivost besedil z uporabniki.

## Ročni pregled za človeka

Izvede ga oseba, ki kode ni pisala. Zapišite datum, brskalnik, operacijski sistem, bralnik zaslona z različico in rezultat vsake vrstice (uspešno, ne, opomba).

Priprava: `docker compose up --build -d`, `seed_test_data` z lastnim `SEED_PASSWORD`, odprite `http://localhost:8000/accounts/login/`. Priporočeni par: NVDA s Firefoxom (Windows) ali Orca s Firefoxom (Linux); po možnosti še VoiceOver s Safarijem.

| # | Korak | Pričakovano |
| --- | --- | --- |
| 1 | Samo s tipkovnico: Tab od začetka strani | Prvi je »Preskoči na vsebino« in je viden; vrstni red je logičen; fokus je vedno viden |
| 2 | Bralnik: naslov strani, jezik, glavne regije | Prebere »Prijava – Odprta šola«, slovenski izgovor, regijo navigacije in glavno vsebino |
| 3 | Bralnik: polja | Vsako polje prebere z oznako; pri geslu tudi pomoč |
| 4 | Oddaja praznega obrazca s tipko Enter | Bralnik prebere povzetek napak; povezava v povzetku premakne v polje; pri polju prebere napako |
| 5 | Napačno geslo | Razumljivo sporočilo, brez razkritja, ali račun obstaja |
| 6 | Uspešna prijava in odjava samo s tipkovnico | Prijava uspe; odjava je gumb, potrditev je dosegljiva s tipkovnico |
| 7 | Povečava 200 % in 400 % | Vsebina ostane berljiva, brez vodoravnega drsenja pri 320 px širine |
| 8 | Kontrast | Besedilo in obrobe polj ustrezajo WCAG 2.2 AA |
| 9 | Razumljivost | Testni uporabnik (npr. starš) razume navodilo in napake |

## Obseg zaslonov za T

Točka 9 zahteva »prijavo in osnovna opravila«. Obseg je osebno sprejel pobudnik 12. 11. 2026 ([register odločitev](odlocitve.md#osebni-sprejemi-pobudnika-12-novembra-2026)):

1. Prijava in odjava (narejeno).
2. Uvoz CSV za tajništvo: izbira datotek, predogled s težavami in spremembami, uveljavitev ali zavrnitev.
3. Seznam oseb z iskanjem in podrobnosti osebe (vloge, povezave, upravičenja) za tajništvo, z odvzemom povezave ali upravičenja in potrditvijo.
4. Popravek kontakta osebe s sledjo spremembe.

Ni v obsegu T: celoten administrativni portal, izvoz, zasloni za starše zunaj M1/M2 (ti so v modulih). Vsak zaslon dobi enake avtomatske preizkuse in vrstico v ročnem pregledu.
