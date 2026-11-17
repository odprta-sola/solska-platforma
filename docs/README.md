# Dokumentacija Odprte šole

Datum usmeritve: 13. oktober 2026; kazalo usklajeno s stanjem 13. novembra 2026 (P0 v `main`, pogodba `1.0.0`). Dokumenti so delovni predlogi, razen izrecno evidentiranih sprejemov. Merge ni institucionalna potrditev.

## Delovna raven

| Za koga oziroma kdaj | Dokument |
| --- | --- |
| Prvi mentorski in šolski pogovor | [Predstavitev projekta](mentorji/predstavitev-projekta.md) in [spremni sporočili](mentorji/prvi-pogovor.md) |
| Ocena obsega, individualnih izdelkov in faz | [Razvojno naročilo](projekt/razvojno-narocilo-P0-M1-M2.md) |
| Model, API, pravila in 20 skupin preizkusov | [Kratka tehnična specifikacija](arhitektura/kratka-specifikacija-P0-M1-M2.md) |
| Pogodba P0–M1–M2 (D12, sprejeta, `1.0.0`) | [Razlaga pogodbe](arhitektura/vmesnik-P0-M1-M2.md), [OpenAPI](../api/openapi.yaml) in [paket odločitve](projekt/d12-paket-za-odlocitev.md) |
| Priprava in prevzem skupne osnove | [Načrt P0/T](projekt/priprava-referencnega-P0.md) |
| Zagon, razvojno okolje in struktura kode | [DEVELOPER.md](../DEVELOPER.md) |
| Razvijalci modulov M1 in M2 | [Navodila](razvijalci/README.md), [ekipa M1](razvijalci/ekipa-M1.md), [ekipa M2](razvijalci/ekipa-M2.md) |
| Pregled in stanje paketa T | [Stanje prevzema T](projekt/stanje-prevzema-T.md), [kontrolni seznam pregleda](projekt/pregled-P0-kontrolni-seznam.md) in [pregled dostopnosti](projekt/pregled-dostopnosti-P0.md) |
| Navodilo za prvi pregled z OpenAI in register prispevkov | [Navodilo](projekt/navodilo-za-pregled-OpenAI.md) in [prispevki](projekt/prispevki.md) |
| Poročila pregledov, odprava in ponovni pregled | [Pregledi](pregledi/), zapisi o odpravi ([prvi](pregledi/2026-11-odprava-prvega-pregleda-P0.md), [ponovni](pregledi/2026-11-odprava-ponovnega-pregleda-P0.md), [tretji](pregledi/2026-11-odprava-tretjega-pregleda-P0.md)), navodili za [ponovni](projekt/navodilo-za-ponovni-pregled.md) in [tretji pregled](projekt/navodilo-za-tretji-pregled.md) |
| Prijava ranljivosti in varnostni postopek | [SECURITY.md](../SECURITY.md) |
| Odvisnosti, slike in licence | [Odvisnosti in licence](projekt/odvisnosti-in-licence.md) |
| Potrditve in formalni pogoji | [Register odločitev](projekt/odlocitve.md) in [odgovornosti](projekt/odgovornosti.md) |
| Varstvo osebnih podatkov (za šolo in DPO) | [Stanje in vrzeli](projekt/varstvo-podatkov-P0.md) |

Najprej razumemo namen in primere. Mentor oceni primernost, obseg in individualne izdelke; šola preveri postopke in pravila. Šele nato se z ustreznimi ljudmi dogovorijo izvedba, skrbništvo in varnostno nadomeščanje, pri čemer so formalni pogoji veljali pred prvo kodo. Nov splošni krog AI pregledov dolge priloge ni naslednji korak.

Stanje 13. novembra 2026: referenčni P0 je izdelan in pogodba D12 zamrznjena kot `1.0.0`; človeški prevzem paketa T ni opravljen. Trenutno stanje in odprte točke vodi [stanje prevzema T](projekt/stanje-prevzema-T.md).

## Podporno gradivo in arhiv

[Arhiv in pravila branja](arhiv/README.md) pojasnita drugi nivo dokumentacije. Daljši opisi [P0](moduli/P0-uporabniki.md), [M1](moduli/M1-eSporocanje.md), [M2](moduli/M2-eSoglasja.md) in [priprava odločitev](projekt/priprava-odlocitev-D03-D09-D12-D14.md) niso obvezno prvo branje.

| Podporno gradivo | Namen |
| --- | --- |
| [Praktični primeri razvojnega paketa](mentorji/razvojni-paket-P0-M1-M2.md) | Podrobnejša pojasnila k naročilu |
| [Navodilo za pregled](mentorji/navodilo-za-pregled.md) | Prva človeška ocena in ločen tehnični pregled |
| [Povzetek projekta V6](projekt/povzetek.md) | Zgodovina pobude, anketa in širši okvir |
| [Anketa staršev](raziskave/anketa-starsi.md) | Preverjene potrebe in omejitve raziskave |
| [Arhitekturna izhodišča](arhitektura/izhodisca.md) | Meje modulov in podatkovnih poti |
| [Izvor gradiva](projekt/izvor-gradiva.md) | Sledljivost vhodov in uredniških popravkov |
| [Izdaje](izdaje/README.md) | Postopek potrjenih izdaj in PDF |
| [Sodelovanje](../CONTRIBUTING.md) | Prispevki, licence in pregledi |
