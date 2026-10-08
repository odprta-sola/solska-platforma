# Register odločitev

Status: začetni delovni register  
Datum: 5. oktober 2026

## Način vodenja

Predlog se odpre v issueju ali pull requestu. Sprejeta odločitev navede datum, odgovorno osebo, povezavo na gradivo, razlog in posledice. Tehnična združitev ni samodejna institucionalna potrditev.

| ID | Vprašanje | Status | Nosilec potrditve |
| --- | --- | --- | --- |
| D01 | Obseg učnega izdelka in prvega pilota M1 | Odprto | Mentor in pilotna šola |
| D02 | Mentor, dijaki in roki | Odprto | Razvojni zavod |
| D03 | Skupni tehnični nosilec in skupni gradniki | Odprto | Sodelujoči zavodi |
| D04 | Gostovanje, e-pošta in kopije | Odprto | Pilotna šola in skupni tehnični nosilec |
| D05 | Jeziki in dostopnost pilota (podatkovni model je večjezičen od začetka; zahtevani jeziki za namestitve po državi, npr. italijanščina in madžarščina, se pravno preverijo) | Odprto | Pilotna šola in nosilec projekta |
| D06 | Upravičeni prejemniki in pravila potrjevanja | Odprto | Pilotna šola |
| D07 | Hramba, dostopi in podatkovne poti | Odprto | Pilotna šola ob posvetu z DPO |
| D08 | Licenca EUPL 1.2 in pravice prispevkov | Predlog | Nosilec projekta in avtorji |
| D09 | Vzdrževanje, podpora in namestnik | Odprto | Sodelujoči zavodi |
| D10 | Merila produkcijskega prevzema M1 in M2 | Predlog v specifikacijah | Skupni tehnični nosilec in pilotna šola |
| D11 | Postopek pilota M2, besedilo obrazca in pravila odločanja | Odprto | Pilotna šola ob vsebinskem in pravnem pregledu |
| D12 | [Pogodba P0–M1–M2](../arhitektura/vmesnik-P0-M1-M2.md): minimalno obveščanje in skupni vir identitet ter upravičenj | Odprto | Skupni tehnični nosilec in mentorji ekip |
| D13 | Razdelitev ekip, nosilci modulov in ocena ur po fazah | Odprto | Sodelujoči zavodi in mentorji |
| D14 | Nosilec obravnave zasebnih prijav, namestnik in roki odziva | Kanal omogočen; obravnava odprta, pred prvo kodo oziroma vključitvijo zunanjih ekip | Nosilec projekta in skrbnik repozitorija |
| D15 | Licenca dokumentacije in pravice besedil; ločeno od licence kode | Predlog/Odprto | Nosilec projekta in avtorji |
| D16 | Prejemniki in odločevalci pri polnoletnih dijakih, prehod med letom in ustreznost privolitve za postopek | Odprto | Pilotna šola ob pravnem in podatkovnem pregledu |

Osnutek D12 z dne 8. oktobra 2026 konkretizira že predvidene skupne identitete in obveščanje. Sheme, prijavni protokol, nosilci, testni nadomestki in pogodbeni preizkusi še niso potrjeni; D12 ostaja odprt. Izhodišča za razdelitev dijaškega dela so v [vodniku za mentorje](../mentorji/razvojni-paket-P0-M1-M2.md).

## Roki in sledenje

D01–D03, D11–D14 in D16 blokirajo začetek odvisnega razvoja. D07, D09 in D10 se zaključijo pred produkcijskim pilotom; imenovanje drugega skrbnika iz D09 je izjema in je potrebno že pred prvo kodo oziroma vključitvijo zunanjih ekip. D04–D06 se rešijo pred razvojem odvisnih funkcij, D08 pred sprejemom kode in D15 pred potrditvijo pogojev ponovne uporabe besedil. Koledarske roke in GitHub dodelitve določijo potrjeni nosilci; vloge niso samodejno imenovanja oseb.

Odločitve se spremljajo v issueih #10–#25 (D01–D16). Dokaz izpolnitve posameznega merila in potrditev se zapišeta v ustrezni issue in register.

## Stanje sodelovanja

Po potrditvi pobudnika z dne 5. oktobra 2026 sta se OŠ Vojke Šmuc Izola in GEPŠ Piran odločili za sodelovanje v projektu. Pisna potrditev vodstev v repozitoriju ni evidentirana. Obseg pilota, odgovornosti, viri in pogoji uvedbe se še usklajujejo. Podatek je potrdil pobudnik Mitja Pirih. Datum prvotne odločitve in zapis dogovora tu nista določena. Ko bo pisna potrditev na voljo, se zabeležita datum in sklic na ustrezno gradivo; javna objava se omeji na podatke, primerne za objavo.

## Evidentirana dejstva

- 5. oktobra 2026 sta bila vzpostavljena javna organizacija GitHub in repozitorij.
- Specifikaciji M1 in M2 sta vključeni v main prek združenih PR #1 in #7; ostajata delovna osnutka za mentorjev pregled.
- Uporabnik je nastavil aktivno zaščito glavne veje z obveznim pull requestom, brez obveznih odobritev, z blokado brisanja in prisilnega prepisa.

- 5. oktobra 2026 je bila omogočena zasebna prijava ranljivosti; navodila so v SECURITY.md. Nosilec obravnave, namestnik in roki odziva ostajajo odprti v D14.
- Odprti so issuei #10–#25 za odločitve D01–D16.
- Omogočeno je samodejno brisanje vej po združitvi.

Ta dejstva ne pomenijo potrditve obsega ali produkcijske uvedbe.
