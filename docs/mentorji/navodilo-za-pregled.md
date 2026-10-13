# Navodilo za prvi mentorski in poznejši tehnični pregled

Datum: 13. oktober 2026

## Prvi mentorski pogovor

Najprej preberite [predstavitev](predstavitev-projekta.md). Ocenite primernost cilja, samostojne izdelke, izvedljiv obseg, potrebne informacije ter vključitev učencev/dijakov v prvo različico ali pozneje. Pojasnite predlagane spremembe in odvisnosti; začetna ocena ni sprejem skrbništva, varnostnih odzivov ali produkcijskega vzdrževanja.

Nato obravnavajte [naročilo](../projekt/razvojno-narocilo-P0-M1-M2.md) in [kratko specifikacijo](../arhitektura/kratka-specifikacija-P0-M1-M2.md). Dolga priloga K 0.6 in arhiv AI pregledov nista obvezno prvo branje. Naslednji vhod je človeška ocena, ne nov splošni krog AI pregleda.

## Poznejši tehnični pregled

Na dejanskem aktualnem diffu preverite model, pravice, podatkovne poti, uporabniške/servisne identitete, različice, trajnost in negotove dostavne izide, CSV, ločenost učencev/staršev ter 20 skupin preizkusov. Primerjajte s stalnim D12, načrtom T in registrom. Ločite pripravljenost za mentorski pogovor, implementacijo pogodbe in produkcijo.

Za ugotovitev navedite datoteko, razdelek, vpliv in konkreten popravek. Brez posebnega naročila je naloga pregled, ne pisanje na GitHub ali merge. Imenovanja in formalna potrditev pogodbe zahtevajo izrecen sprejem pristojnih. Sedanji neodvisni človeški prevzem T ostaja merilo do potrjene spremembe.

## Zgodovinski odziv na prvi pregled pri 487ff00

Spodnje vrstice beležijo odziv na prejšnjo različico. Ne opisujejo trenutnega HEAD; za sedanji obseg in razdelitev dela veljajo naročilo, načrt P0 in aktualni diff PR.

| Pripombe | Obravnava |
| --- | --- |
| B1, B4 | Dodani oddelki, občinstvo, kontakti, obseg in servisni način. Konkretna shema izdaje scope_ref ter prijavni protokol ostajata pogoj potrditve API. |
| B2 | idempotency_key ločen od trace_id; rezultati cancel ločeni od stanj. Konkretno okno hrambe ključa še zahteva odločitev. |
| B3 | Ohranjen dogovor: M2 načrtuje in odda ob dospelosti. send_not_before zato ni dodan; dodan iztek v tihem času. |
| B5 | Predlagani skupni vhod, ločene osnovne poti in SSO potek; konkretna rešitev odprta. Enaka API predpona sama ne bi bila napaka pri različnih gostiteljih. |
| B6 | Pogodba prestavljena na stalno mesto; sklici in D12 usklajeni. D12 ostaja odprt. |
| P1, P3 | Takrat so bili dodani mejniki A/I/B/C, minimalni sprejem M1 in dodatni preizkusi; poznejša razdelitev jih je spremenila. |
| P2 | Prejšnje stanje pri c3388ed: nadomestek je omogočal vzporednost in P0 je ostal dijaški razvoj. Nova usmeritev določa pobudnikov referenčni P0 in celoten človeški prevzem T pred A/I. |
| P4 | Predloge, locale, omejeni parametri in štiri vrste dostave. |
| P5 | CSV polja, šifranti in lastništvo P0. Manjkajoče vrstice ne ukinjajo pravic samodejno; politiko potrdita šola in tehnični nosilec. |
| P6, P7 | Aktivacijska pošta je bila ločena od M1; poznejši načrt P0 določa aktualne pogoje pred kodo in prevzemom. |
| U1–U9 | Ločeni dodatki in navodilo, oznake primerov, primerjalna tabela, pojmovnik, izvor, ID, vloge, predlagana šola in dopolnjeni testni podatki. |

OpenAPI, testni strežnik in produkcijska rešitev še niso izdelani; dokumentacija tega ne predstavlja kot zaključeno delo.
