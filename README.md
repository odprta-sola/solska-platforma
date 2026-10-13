# Odprta šola

Modularna odprtokodna rešitev za elektronsko poslovanje šol.

Projekt nastaja iz pobude za preprostejšo komunikacijo med šolo in starši ter sodelovanje šol, mentorjev in dijakov pri razvoju uporabnih odprtokodnih rešitev.

## Dokumentacija

Začnite s [predstavitvijo za mentorja in šolo](docs/mentorji/predstavitev-projekta.md). P0 zagotavlja prijavo in pravice, M1 obvestila ter izrecno seznanitev, M2 odločitve po namenih. Možnost obveščanja učencev in dijakov je predlog za šolsko in mentorsko presojo.

[Razvojno naročilo](docs/projekt/razvojno-narocilo-P0-M1-M2.md) določa obseg in faze, [kratka tehnična specifikacija](docs/arhitektura/kratka-specifikacija-P0-M1-M2.md) pa model, poti API in 20 skupin prihodnjih preizkusov. [Kazalo](docs/README.md) loči delovno dokumentacijo od podrobnega podpornega gradiva in arhiva.

Pobudnik osebno pripravlja skupno osnovo ob pomoči AI; dijaki po dogovoru z mentorjem razvijajo predvsem obvestila in obrazce. Delujoči P0, pogodba OpenAPI in aplikacija še niso izdelani. [Register odločitev](docs/projekt/odlocitve.md) loči sprejete osebne dogovore od preostalih institucionalnih potrditev.

## Trenutno stanje

Po potrditvi pobudnika z dne 5. oktobra 2026 sta se OŠ Vojke Šmuc Izola in GEPŠ Piran odločili za sodelovanje v projektu. Pisna potrditev vodstev v repozitoriju ni evidentirana. Obseg pilota, odgovornosti, viri in pogoji uvedbe se še usklajujejo. Potekajo priprava dokumentacije, usklajevanje obsega prvega modula in organizacija razvoja. Aplikacija še ni na voljo za produkcijsko uporabo.

Dokumentacija v repozitoriju je delovna, razen kadar je izrecno označena kot potrjena. Objava spremembe sama po sebi ne pomeni potrditve sodelujočih šol.

## Namen

Razviti module, ki jih lahko šole uvajajo postopoma in uporabljajo samostojno ali povezano prek skupnih vmesnikov.

Prednost imajo preprosta uporaba, varstvo osebnih podatkov, dostopnost, prenosljivost podatkov in dolgoročno vzdrževanje.

## Prvi modul M1 eSporočanje

Prvi načrtovani modul je namenjen:

- objavi obvestil staršem in oddelkom;
- varnemu dostopu do vsebine in prilog;
- ločenemu beleženju odprtja obvestila in potrditve seznanitve;
- opomnikom in pregledu odzivov;
- podpori papirni poti.

Potrditev seznanitve ni soglasje ali privolitev. Obravnava soglasij je predvidena v ločenem modulu.

Natančen obseg prvega pilota bo določen v specifikaciji M1.

## Načela razvoja

- Razvoj in testiranje potekata na izmišljenih testnih podatkih.
- Osebni podatki, gesla, ključi in produkcijski izvozi ne sodijo v repozitorij.
- Elektronska uporaba naj bo za starše brezplačna, ohranjena naj bo papirna možnost.
- Moduli se povezujejo prek dokumentiranih vmesnikov.
- Produkcijska uvedba zahteva strokovni pregled in določenega vzdrževalca.
- Dokumentacija in pomembne odločitve se vodijo skupaj z zgodovino sprememb.

## Sodelovanje

Predloge, vprašanja in napake lahko odprete v zavihku Issues.

Spremembe dokumentacije in kode predlagajte prek pull requestov. Večje spremembe obsega ali arhitekture naj bodo najprej obravnavane v ustreznem issueju.

V javne razprave ne vključujte osebnih podatkov učencev, staršev ali zaposlenih.

## Naslednji koraki

1. Predstavitev projekta in prva mentorska ter šolska ocena.
2. Uskladitev učnega obsega, vključno s predlogom računov učencev/dijakov, individualnih izdelkov in virov.
3. Ločeni dogovori o predaji, skrbništvu, pregledih in varnostnem nadomeščanju; izpolnitev pogojev pred prvo kodo.
4. Potrditev razvojne pogodbe in priprava ter prevzem skupne osnove.
5. Razvoj in demonstracije na testnih podatkih. Uporaba na šoli ima ločen prevzem.

CSV ostane osnovna pot uvoza. Vsaka šola ima svojo namestitev in v izvedbenem dogovoru določi skrbnike ter vzdrževanje; centralna večšolska namestitev ni predvidena. Integracija eAsistent, ArnesAAI in SI-PASS so poznejše možnosti, brez potrjenih dostopov ali rokov.

## Licenca

Predvidena licenca za programsko kodo je EUPL 1.2. Besedilo licence in pogoji za prispevke bodo dodani pred vključevanjem kode.
