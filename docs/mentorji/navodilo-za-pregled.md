# Navodilo za neodvisni pregled dokumentacije

Preglejte dejanski diff PR #29 in nove dokumente v celoti. Primerjajte z M1, M2, arhitekturo, povzetkom, odgovornostmi in registrom na osnovni veji.

Preverite razumljivost za mentorja, razmejitev evidenc/prijave/upravičenj, uvoz in aktivacijo, mejnike ter individualne izdelke. Pri API preverite prejemnike, servisno avtorizacijo, minimalne podatke, podvojitve, preklic, iztek, topologijo in prijavo. Vključite varstvo podatkov, dostopnost in večjezičnost.

Ocenite ločeno: primernost za mentorjev pregled; pripravljenost pogodbe za implementacijo; pripravljenost za produkcijo. Odprtih odločitev ne štejte kot že potrjene izvedbe.

Za vsako ugotovitev navedite datoteko, razdelek, konkreten problem in predlagani popravek. Ločite blokirajoče napake, pomembne dopolnitve in uredniške predloge. Preverite tudi odprte točke iz spodnjega odziva na prvi pregled.

Naloga je pregled in poročilo v pogovoru. Brez posebnega naročila ne spreminjajte, komentirajte na GitHubu ali združujte PR. Če do repozitorija nimate dostopa, to povejte.

## Odziv na prvi pregled

| Pripombe | Obravnava |
| --- | --- |
| B1, B4 | Dodani oddelki, občinstvo, kontakti, obseg in servisni način. Konkretna shema izdaje scope_ref ter prijavni protokol ostajata pogoj potrditve API. |
| B2 | idempotency_key ločen od trace_id; rezultati cancel ločeni od stanj. Konkretno okno hrambe ključa še zahteva odločitev. |
| B3 | Ohranjen dogovor: M2 načrtuje in odda ob dospelosti. send_not_before zato ni dodan; dodan iztek v tihem času. |
| B5 | Predlagani skupni vhod, ločene osnovne poti in SSO potek; konkretna rešitev odprta. Enaka API predpona sama ne bi bila napaka pri različnih gostiteljih. |
| B6 | Pogodba prestavljena na stalno mesto; sklici in D12 usklajeni. D12 ostaja odprt. |
| P1, P3 | Ločeni mejniki A/I/B/C, dodan minimalni sprejem M1, oznake zaslonov, celoten M2 prototip in dodatni preizkusi. |
| P2 | Nadomestek omogoča vzporednost; P0 ostaja dijaški razvoj. Izvajalca imenuje mentor, ne predpostavljamo razpoložljivega tehničnega nosilca. |
| P4 | Predloge, locale, omejeni parametri in štiri vrste dostave. |
| P5 | CSV polja, šifranti in lastništvo P0. Manjkajoče vrstice ne ukinjajo pravic samodejno; politiko potrdita šola in tehnični nosilec. |
| P6, P7 | Aktivacijska pošta neodvisna od M1; dodana tabela blokad in rokov. |
| U1–U9 | Ločeni dodatki in navodilo, oznake primerov, primerjalna tabela, pojmovnik, izvor, ID, vloge, predlagana šola in dopolnjeni testni podatki. |

OpenAPI, testni strežnik in produkcijska rešitev še niso izdelani; dokumentacija tega ne predstavlja kot zaključeno delo.
