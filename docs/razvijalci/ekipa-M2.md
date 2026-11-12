# Ekipa M2 – eSoglasja

Status: osnutek za mentorski pregled. Obseg je v [razvojnem naročilu](../projekt/razvojno-narocilo-P0-M1-M2.md) (razdelek »Obvezni izdelek M2«), poslovna pravila v [specifikaciji M2](../moduli/M2-eSoglasja.md). Splošna pravila: [README](README.md). M2 za obveščanje potrebuje M1; do takrat dela proti nadomestku.

## Naloga

Potek pregledanega obrazca od osnutka do odločitve in dovoljene spremembe: priprava, vsebinski pregled, objava, izrecna odločitev po namenih, potrdilo, zgodovina, preklic.

## Kaj M2 dobi in kaj ponudi

| Smer | Pot | Namen |
| --- | --- | --- |
| M2 → P0 | `GET /p0/api/v1/me/relationships` | Lastne povezave in `scope_ref` za odločanje |
| M2 → P0 | `POST /p0/api/v1/authorizations/check` | Pravica za dejanje (`m2.decide`) pred prikazom in oddajo |
| M2 → M1 | `POST /m1/api/v1/delivery-requests` | Obvestila in opomniki; M2 kontaktov ne vidi |
| M2 → M1 | `POST .../{id}/cancel` | Selektivni preklic nepotrebnih opomnikov |
| M1 → M2 | `POST /m2/api/v1/reminders/check` | Strežniška stran, ki jo mora izdelati M2: samo `REQUIRED` ali `NO_LONGER_REQUIRED` |

Servisni žeton M2 potrebuje `m1.delivery` in `p0.authorizations.check`. Nadomestek (`p0/stubs/m2.py`) je referenca obnašanja `reminders/check`.

## Predlog razreza po dijakih (mentor potrdi)

1. **Priprava in pregled obrazcev:** predloga z omejenimi polji, različice, predogled, vsebinska odobritev, ločeni nameni, dva izmišljena učna postopka.
2. **Odločitve, zgodovina in preklic:** izbire brez vnaprej izbranih odgovorov, odločitev kot dogodek, skupno stanje, potrdilo, sprememba, preklic, ročna obravnava nasprotij, papirni vnos, opomniki prek M1.

## Pravila, ki jih ekipa najlažje zgreši

- Brez odziva in potek roka **ne** pomenita Da ali Ne. Sistem ne izmisli izjave uporabnika.
- Odločitev, dokazni dogodek, skupno stanje in dostava so **ločeni podatki**. Nobeno e-poštno stanje ne nadomesti odločitve.
- Odločitev in trajna namera za obveščanje se shranita skupaj; ob izpadu M1 odločitev ostane.
- Obrazec se pred objavo vsebinsko pregleda; nova različica zahteva nov pregled.
- Prva različica: en otrok naenkrat, izbire po namenih. Odgovor ene osebe ne ustvari odziva druge.
- Nasprotujoči odzivi → ročna obravnava, ne tiha razrešitev.
- Zgodovina se ne prepiše: sprememba ali preklic doda dogodek. Veljavno privolitev je mogoče preklicati tudi po zaključku zbiranja.
- `reminders/check` ne razkrije privolitve ali zavrnitve; napaka ni odgovor »nepotreben«.
- M2 ne zahteva predhodnega klika v M1 (»Seznanjen/-a sem«).

## Dokaz uspeha

Mejnik I: odločitev se shrani, zahteva za dostavo gre v M1 po pogodbi; ob izpadu M1 odločitev ostane; dvojna zahteva se ne podvoji; preklic ene od dveh dostav ustavi samo izbranega prejemnika. Mejnik B: več namenov in več odločevalcev, preklic pri zaključenem obrazcu. Poleg teh sodijo v pregled specifikacijski preizkusi 13 do 18 iz [kratke specifikacije](../arhitektura/kratka-specifikacija-P0-M1-M2.md).

## Odprto (ne rešujte po svoje)

Besedilo obrazca in pravila odločanja (D11), polnoletni dijaki (D16), predstavitev več otrok v eni zahtevi, vstop uporabnika v modul, politika opomnikov po odvzemu pravice. Predlagajte v issueju; odločitve so šolske in pravne, ne tehnične.
