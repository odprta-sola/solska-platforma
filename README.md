# Odprta šola

Modularna odprtokodna rešitev za elektronsko poslovanje šol.

Projekt nastaja iz pobude za preprostejšo komunikacijo med šolo in starši ter sodelovanje šol, mentorjev in dijakov pri razvoju uporabnih odprtokodnih rešitev.

## Dokumentacija

[Kazalo dokumentacije](docs/README.md) povezuje javni povzetek V6, poročilo ankete, predlog odgovornosti, arhitekturna izhodišča in register odločitev.

[Osnutek M1 eSporočanje](docs/moduli/M1-eSporocanje.md) opredeli obvestila in seznanitev. [Osnutek M2 eSoglasja](docs/moduli/M2-eSoglasja.md) opredeli obrazce, odločitve in preklic. Oba sta odprta za mentorjev pregled. [Navodila za sodelovanje](CONTRIBUTING.md) opisujejo pripravo in pregled prispevkov.

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

1. Uskladitev in potrditev obsega prvega pilota M1.
2. Določitev odgovornosti za razvoj, pregled in vzdrževanje.
3. Priprava arhitekture in pravil povezovanja modulov.
4. Potrditev licence kode in pogojev prispevkov.
5. Razvoj in preizkus na testnih podatkih.

## Licenca

Predvidena licenca za programsko kodo je EUPL 1.2. Besedilo licence in pogoji za prispevke bodo dodani pred vključevanjem kode.
