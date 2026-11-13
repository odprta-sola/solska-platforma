# Ekipa M2 – eSoglasja

Status: navodila za izvajalca (mentor in ekipa M2), pogodba `1.0.0`. Obseg je v [razvojnem naročilu](../projekt/razvojno-narocilo-P0-M1-M2.md) (razdelek »Obvezni izdelek M2«), poslovna pravila v [specifikaciji M2](../moduli/M2-eSoglasja.md). Splošna pravila: [README](README.md). M2 za obveščanje potrebuje M1; do takrat dela proti nadomestku.

## Naloga

Potek pregledanega obrazca od osnutka do odločitve in dovoljene spremembe: priprava, vsebinski pregled, objava, izrecna odločitev po namenih, potrdilo, zgodovina, preklic.

## Kaj M2 dobi in kaj ponudi

| Smer | Pot | Namen |
| --- | --- | --- |
| M2 → P0 | `GET /p0/api/v1/me/relationships` | Lastne povezave in `scope_ref` za odločanje |
| M2 → P0 | `POST /p0/api/v1/authorizations/check` | Pravica za dejanje (`m2.decide`) pred prikazom in oddajo |
| M2 → P0 | `POST /p0/api/v1/audiences/resolve` | Ob objavi obrazca: posnetek občinstva z avtorjevo sejo; `audience_ref` se pošlje v dostavno zahtevo |
| M2 → M1 | `POST /m1/api/v1/delivery-requests` | Obvestila in opomniki z `audience_ref`; M2 kontaktov ne vidi |
| M2 → M1 | `POST .../{id}/cancel` | Selektivni preklic nepotrebnih opomnikov po `item_id` |
| M1 → M2 | `POST /m2/api/v1/reminders/check` | Strežniška stran, ki jo mora izdelati M2: samo `REQUIRED` ali `NO_LONGER_REQUIRED` |

Servisni žeton M2 potrebuje `m1.delivery` in `p0.authorizations.check`. Nadomestek (`p0/stubs/m2.py`) je referenca obnašanja `reminders/check`; strežniško stran izdelate v `p0/m2/api_urls.py`, klici v P0 in M1 so pripravljeni v `p0/m2/p0_client.py`.

Zahteva za dostavo (pogodba `1.0.0`): `event_key` je poslovni ključ dogodka (npr. `obrazec-1:v1:opomnik:2`; naslednji opomnik ima novo številko), pri opomniku ima vsaka postavka svoj `need_ref` za eno potrebo (oseba, otrok, obrazec, različica), skupnega `locale` ni.

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

Besedilo obrazca in pravila odločanja (D11), polnoletni dijaki (D16), politika opomnikov po odvzemu pravice in interval periodične ponovne presoje odprtih postopkov (C14). Več otrok je več postavk (ena na `scope_ref`), vstop uporabnika je skupna seja P0 (glej [README](README.md#povezava-z-drugimi-deli)). Predlagajte v issueju; šolske in pravne odločitve niso tehnične.
