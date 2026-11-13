# Ekipa M1 – eSporočanje

Status: osnutek za mentorski pregled. Obseg je v [razvojnem naročilu](../projekt/razvojno-narocilo-P0-M1-M2.md) (razdelek »Obvezni izdelek M1«), poslovna pravila v [specifikaciji M1](../moduli/M1-eSporocanje.md). Splošna pravila: [README](README.md).

## Naloga

Celoten potek šolskega organizacijskega obvestila: učitelj objavi, upravičeni starš se prijavi, vidi samo svoje, potrdi seznanitev; šola vidi odzive.

## Kaj M1 dobi in kaj ponudi

| Smer | Pot | Namen |
| --- | --- | --- |
| M1 → P0 | `POST /p0/api/v1/audiences/resolve` | Predogled prejemnikov oddelka z uporabnikovo sejo (CSRF); vrne `audience_ref` in `scope_ref`, brez kontaktov |
| M1 → P0 | `POST /p0/api/v1/authorizations/check` | Pravica pred vpogledom, potrditvijo in dostavo |
| M1 → P0 | `POST /p0/api/v1/delivery-contacts/resolve` | Kontakt tik pred pošiljanjem za prejemnika iz posnetka (`audience_ref`); samo M1 |
| M1 → M2 | `POST /m2/api/v1/reminders/check` | Ali je opomnik še potreben (`REQUIRED` / `NO_LONGER_REQUIRED`) |
| M2 → M1 | `POST /m1/api/v1/delivery-requests` | Prevzem zahteve za dostavo; 202 šele po trajnem zapisu |
| M2 → M1 | `GET .../{id}`, `POST .../{id}/cancel` | Stanje in selektivni preklic po postavkah (`item_id` = oseba in obseg) |

M1 mora izvajati strežniško stran `/m1/api/v1/` po shemi; nadomestek (`p0/stubs/m1.py`) je referenca obnašanja. Servisni žeton M1 potrebuje: `p0.authorizations.check`, `p0.contacts.resolve`, `m2.reminders.check`. Predogled občinstva gre prek seje prijavljenega avtorja, ne prek žetona.

## Predlog razreza po dijakih (mentor potrdi)

1. **Objava in seznanitev:** osnutek, izbira skupine, predogled prejemnikov, objava, informativno in zahtevano obvestilo, različice, ponovna seznanitev, umik, zaščiten prikaz.
2. **Dostava in papir:** strežniška stran pogodbe `delivery-requests` (idempotenca, stanja, selektivni preklic), e-poštna vrsta, tihi čas, omejeni ponovni poskusi, iztek, opomniki, papirna izročitev in potrditev kot ločena dogodka.

Vsak razrez vključuje svoje teste, dostopnost in navodila.

## Pravila, ki jih ekipa najlažje zgreši

- Odprtje obvestila **ne** ustvari potrditve; ustvari jo izrecno dejanje za konkretno različico in jasno prikazan obseg otrok.
- Pri več otrocih je nova potrditev za vse dovoljene obsege ali za nobenega.
- Potrditev starša ne nadomesti potrditve drugega starša.
- E-pošta vsebuje samo splošno opozorilo in zaščiteno povezavo; brez imen otrok in vsebine.
- `handed_off` pomeni predajo strežniku, ne prejema. Negotov izid ostane viden (`held`, `HANDOFF_UNCERTAIN`), brez samodejne ponovne predaje; ponovitev je ročna odločitev (D12, C13).
- 202 samo po zapisu, ki preživi izpad. Isti `idempotency_key` in vsebina vrneta isti rezultat; drugačna vsebina 409.
- Pred pošiljanjem preverite pravico, kontakt, potrebo (M2), preklic, urnik in iztek. Preklic enega prejemnika ne ustavi drugih.
- Nov član oddelka ne dobi starih obvestil.

## Dokaz uspeha

Mejnik A: učitelj objavi → pravi starš se prijavi → vidi samo svoje → potrdi; druga družina nima dostopa; dostopnost s tipkovnico. Mejnik I: M1 prevzame zahtevo M2 po pogodbi; ob izpadu M1 odločitev M2 ostane, dostava se nadaljuje; dvojna zahteva se ne podvoji. Poleg teh sodijo v pregled specifikacijski preizkusi 11, 12, 17, 18 in 19 iz [kratke specifikacije](../arhitektura/kratka-specifikacija-P0-M1-M2.md).

## Odprto (ne rešujte po svoje)

D12 je sprejet (pogodba `1.0.0`): tihi čas (osnutek delavniki 7–20), negotova predaja, okno ključev 30 dni, vir jezika in oznak ter postavke po otrocih so določeni v [pogodbi](../arhitektura/vmesnik-P0-M1-M2.md). Odprti ostajajo prazniki in urnik šole, največje zadržanje in nadomestni jezik (D05); predloge oddajte v issueju.
