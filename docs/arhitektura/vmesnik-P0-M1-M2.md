# Pogodba vmesnikov P0–M1–M2

Datum: 9. oktober 2026
Status: delovni predlog D12 za potrditev; ni dokončna implementacijska pogodba

## Vloga pogodbe v naročilu

Ta pogodba je skupni tehnični predlog v [razvojnem naročilu pobudnika](../projekt/razvojno-narocilo-P0-M1-M2.md). Dopolnitev shem in testov je naloga mejnika T. Pobudnik s pomočjo AI pripravi izhodiščno rešitev; mentorji in skupni tehnični nosilec preverijo izvedljivost in varnost ter potrdijo različico pogodbe v D12 pred odvisno implementacijo. Vmesniki niso prosta izbira posamezne ekipe. Zapisane odprte vrzeli niso s tem zaključene.

## Obseg in odprte odločitve

Ta dokument je stalno mesto osnutka pogodbe. Nadomešča načrtovani naslov vmesnik-M1-M2.md in vključuje skupni vir identitet ter upravičenj, ki je že del D12. [Vodnik za mentorje](../mentorji/razvojni-paket-P0-M1-M2.md) in [P0](../moduli/P0-uporabniki.md) pojasnita uporabo.

Pred odvisno implementacijo mentorji in skupni tehnični nosilec potrdijo topologijo, prijavno rešitev, delegiranje identitete, sheme, šifrante, meje velikosti, roke hrambe ključev in izvajalce testnega nadomestka. OpenAPI in delujoči nadomestek še nista izdelana. Besedilni primeri niso nadomestilo za pogodbeno testiranje.

P0 sam ne določi povezav M2 → M1 in M1 → M2. Paket T mora zagotoviti njuni shemi, nadomestka in pogodbene teste. Pred D12 je treba izrecno določiti vir jezika in prikaznih oznak vsakega prejemnika, slovar poslovnih ID, semantiko `scope_ref` pri več otrocih in `grants.scope_key`, ravnanje ob odsotnem kontaktu, pravilo tihega časa ter zgodovinski dostop. Seznam vprašanj ni dokončana pogodba.

## Topologija in prijava

Predlog za prvi pilot je ena namestitev šole za skupnim HTTPS vhodom. Zunanje osnovne poti so /p0/api/v1, /m1/api/v1 in /m2/api/v1. Fizična razporeditev procesov je odprta; ni zahteve po treh strežnikih. M1 samostojno pomeni paket P0+M1; M2 potrebuje P0+M1.

Predlog je skupen vzdrževan ponudnik prijave P0. Ob odprtju M2 iz e-pošte M2 preveri svojo sejo, po potrebi preusmeri na prijavo in nato vrne uporabnika na dovoljeni cilj. Seje oziroma preverjanje identitete uredimo z izbrano vzdrževano integracijo. Deljenje piškotkov ali sprejem poljubnega person_id ni dogovorjena prijavna rešitev. Končni protokol, zaščita sej, CSRF, potek in odjava so pogoj potrditve D12.

Dva načina klica:
- Uporabniški: preverjena seja oziroma delegirana identiteta; dejanska oseba izhaja iz preverjenega konteksta.
- Servisni: ločena identiteta modula z omejenimi dovoljenji. Zahteva z ID prejemnika ne pomeni prijave v njegovem imenu. Storitev sme preverjati in pošiljati samo v odobrenem obsegu in za evidentirano zahtevo.

Pri prvem pilotu za zaščitene vpoglede, oddajo, potrditev in dejansko pošiljanje ne uporabljamo pozitivnega predpomnilnika upravičenj. Ob nedosegljivem preverjanju dejanje zavrnemo oziroma dostavo zadržimo. Morebitni poznejši predpomnilnik potrebuje politiko veljavnosti in odvzema.

Prvi predlog ne zahteva potiskanja dogodkov iz P0: pravice se preverjajo ob dostopu in pred dostavo, odprta opravila pa ob naslednji obdelavi. To ne izpolni samodejno ponovne presoje vseh odprtih postopkov M2: izvajalec mora pred pilotom določiti periodično uskladitev ali dogodke, njihov interval in ponovne poskuse. Dogodki so razvojna možnost iz arhitekturnih izhodišč, ne že zagotovljen sistem.

## Skupna pravila

JSON, različica v1, stabilni ID, UTC ISO 8601; prikaz in tihi čas Europe/Ljubljana. Prijavne skrivnosti se ne zapisujejo v zahteve za dostavo. Moduli ne berejo tujih tabel.

idempotency_key določi klicatelj in zagotavlja ponovljivost mutacije; obseg je šola, klicoči modul in operacija. Enaka vsebina z istim ključem vrne prvotni logični rezultat; drugačna vsebina vrne 409. Hranimo ključ oziroma zaščiten zapis deduplikacije vsaj do konca dovoljenega okna ponavljanja; njegova konkretna dolžina in hramba sta obvezna odločitev pred potrditvijo pogodbe. Po tem oknu ponavljanje stare operacije ni dovoljeno; tudi nova oznaka ne sme podvojiti istega poslovnega dogodka.

trace_id ustvari strežnik za sledenje obdelavi. Napaka vsebuje code, message in trace_id. Sporočilo ne razkriva tujih virov ali skrivnosti. Predlog HTTP: 400 napačna shema, 401 neveljavna identiteta, 403 nedovoljeno dejanje, 404 vir ni dostopen/ne obstaja po potrjeni politiki, 409 konflikt, 503 začasna nedosegljivost. Seznamski klici uporabljajo omejen page_size in neprosojen next_cursor; konkretne meje se potrdijo pred implementacijo.

## P0 in upravičenci

| Pot v P0 | Kdo in zakaj | Minimalni rezultat |
| --- | --- | --- |
| GET /me | Prijavljen uporabnik | person_id, vloge |
| GET /me/relationships | Uporabnik, lastne povezave | student_id, dovoljeni obsegi in veljavnost |
| GET /me/classes | Zaposleni, lastne dodelitve | class_id in dovoljeni obsegi |
| POST /audiences/resolve | Modul z delegiranim zaposlenim | Predogled dovoljenih prejemnikov in obsegov |
| POST /authorizations/check | Uporabniški ali servisni klic v omejenem obsegu | allowed, reason_code, checked_at |
| POST /delivery-contacts/resolve | Samo pooblaščena dostavna storitev M1 | Veljavni kontakt za točno določenega prejemnika in zahtevo |

Razreševanje občinstva prejme class_id oziroma odobren group_id, namen, pooblaščenega avtorja iz preverjenega konteksta ter predlagani obseg. Preveri dodelitve avtorja in vrne person_id z dovoljenimi scope_ref, brez kontaktov ali občutljivih utemeljitev. Rezultat ima audience_ref, različico in čas predogleda. Ob objavi se shrani izbrani nabor; novi člani oddelka ne pridobijo samodejnega dostopa do starih objav. Pravice izbranih prejemnikov se ob uporabi ponovno preverjajo.

scope_ref je neprosojen sklic na potrjeni obseg (šola, subjekt/otrok, vir ali postopek, dovoljena dejanja in veljavnost). Izdajo in razrešitev sklica izvajata P0 ter lastnik vira po potrjeni pogodbi; klicateljev poljuben niz ni dokaz pravice. Konkretna shema izdaje sklica je odprta zahteva OpenAPI. Vir ostane odgovornost modula: P0 dovoli obseg, M1 preveri naslovljenost in različico, M2 veljavnost obrazca in pravila odločanja.

Povezava, na kateri temelji dovoljenje, se preveri ob vsakem zaščitenem dejanju; njen odvzem ima prednost pred še veljavnim zapisom dovoljenja. Semantika izdaje `scope_ref` in vezave na `grants.scope_key` ostaja za shemo D12.

Primer preverjanja:
```json
{"subject_id":"parent-01","scope_ref":"scope-demo-01","permission":"m1.confirm"}
```
```json
{"allowed":true,"reason_code":"ALLOWED","checked_at":"2026-10-08T10:00:00Z"}
```
P0 uporablja dogovorjen šifrant dovoljenj modulov; ne presoja njihove poslovne logike. Dovoljeni razlogi so ALLOWED, NOT_ALLOWED, SCOPE_INACTIVE; nedosegljivost je 503, ne NOT_ALLOWED. Odgovor ne razkriva razloga skrbniške omejitve.

Servisni kontaktni klic vsebuje recipient_id, scope_ref in delivery_request_id. M1 preveri lastništvo zahteve, P0 pa servisno dovoljenje in veljavni obseg prejemnika. Stikov ni mogoče množično brati zgolj s seznamom ugibanih ID. Kontakt se uporablja tik pred pošiljanjem; ne kopira se v splošno evidenco M1/M2. M2 kontaktov za dostavo ne potrebuje.

## Zahteve M2 za dostavo v M1

| Pot v M1 | Namen | Odgovor |
| --- | --- | --- |
| POST /delivery-requests | Prevzem veljavne zahteve | 202 z delivery_request_id, state=queued |
| GET /delivery-requests/{id} | Stanje lastne zahteve | 200 s stanji po prejemnikih |
| POST /delivery-requests/{id}/cancel | Ponovljiv preklic | 200 s stanji in rezultatom preklica po prejemniku |

Klicoči modul vidi le svoje zahteve. Vsak prejemnik ima svoj scope_ref. Število prejemnikov je omejeno s potrjeno shemo.

Selektivni preklic je del D12 pred začetkom odvisnega razvoja I: zahteva mora omogočiti izbiro konkretnega prejemnika oziroma njegove dostave, ne avtomatskega preklica drugih prejemnikov iste zahteve. Identifikator, shema in odgovor za posameznega prejemnika se določijo v OpenAPI in pogodbenem testu.

kind je notification, reminder, receipt ali change_notice. Besedilo izbere pregledana večjezična predloga template_id in locale. params dopušča le polja iz potrjene sheme predloge. Splošna predloga nima imen otrok ali vsebine odločitev. Vnos poljubnega besedila ni del tega predloga API. Manjkajoč prevod se obravnava po D05, nadomestni jezik je izrecen, ne tih.

```json
{
  "idempotency_key":"demo-reminder-001",
  "kind":"reminder",
  "recipients":[{"person_id":"parent-01","scope_ref":"scope-demo-01"}],
  "template_id":"m2.pending-response.v1",
  "locale":"sl",
  "params":{},
  "target":{"module":"M2","resource_id":"form-demo-01"},
  "need_ref":"need-demo-001",
  "expires_at":"2026-10-09T16:00:00Z"
}
```

M1 sestavi povezavo iz dovoljenega modula in vira. Poljubni zunanji URL ali callback niso dovoljeni. Ciljni modul ob kliku ponovno preveri pravice.

M2 načrtuje opomnik in odda zahtevo šele, ko dospe. Zato send_not_before v prvem dogovoru ni potreben. M1 zahtevo po prevzemu obdeluje ob upoštevanju tihega časa, ponovnih poskusov in izteka. Če pred iztekom ni dovoljenega časa dostave, se ne pošlje; iztek ima vidno kodo DELIVERY_WINDOW_EXPIRED. Nujno pošiljanje ni samodejna pravica servisnega klicatelja.

Stanja posamezne dostave: queued, held, handed_off, failed, cancelled, expired. handed_off pomeni predajo strežniku, ne prejema. Ponovitev obdela le neobdelane prejemnike. Agregat naj vrne število po stanju; ne skriva delnih napak.

Odgovor 202 sme slediti šele trajnemu zapisu zahteve, potrebnemu za obnovitev po izpadu. Pri negotovem izidu poštne predaje mora potrjena politika določiti, kdaj je ponovitev dopustna, kako se zabeleži negotovost in kaj lahko dokazujemo; logična deduplikacija ne zagotavlja enkratnega fizičnega prejema.

Rezultat preklica je ločen od stanja: cancelled_now, already_cancelled, too_late ali already_terminal. Pri too_late ostane state=handed_off; pri expired/failed vrnemo already_terminal z dejanskim stanjem. failed je končno stanje po izčrpanju poskusov; začasna napaka ostane queued ali held. Neveljavna/nepooblaščena zahteva vrne običajno napako, ne uspešnega preklica.

## Preverjanje potrebe in veljavnost opomnikov

M1 tik pred dostavo ločeno preveri pravico prejemnika in potrebo v M2.

POST /m2/api/v1/reminders/check:
```json
{"need_ref":"need-demo-001","recipient_id":"parent-01","scope_ref":"scope-demo-01"}
```
```json
{"needed":false,"reason_code":"NO_LONGER_REQUIRED"}
```

M2 preveri identiteto M1, da sklic pripada naročeni zahtevi in prejemniku, ter vrne samo REQUIRED ali NO_LONGER_REQUIRED z ustreznim needed. Ne razkrije privolitve, zavrnitve ali preklica. Napaka ni odgovor »nepotreben«. Že predane e-pošte ni mogoče priklicati; preverjanje ne zagotavlja atomarnosti z odzivom, povezava pa pokaže aktualno stanje.

Vsaka zahteva za opomnik vsebuje najpoznejši dovoljeni čas pošiljanja (polje `expires_at`); šola s skupnim tehničnim nosilcem pred pilotom določi največji čas zadržanja. Brez tega podatka M1 zahtevo zavrne. Po izteku M1 opomnik označi kot potekel in ga ne pošlje, tudi po obnovitvi povezave; razlog je viden skrbniku in klicočemu modulu. Ponovni poskusi ne podaljšujejo veljavnosti. Preverjanje potrebe vrne samo potreben/nepotreben in dogovorjeno kodo razloga, brez vsebine ali podrobnosti odločitve. Napaka oziroma nedosegljivost je ločena od odgovora nepotreben.

## Preizkusi in zamrznitev prve pogodbe

Skupni preizkusi morajo pokriti: pravico avtorja do oddelka, servisni klic brez seje, podtaknjen ID/obseg, nepooblaščen kontaktni klic, dvojno zahtevo, konflikt ključa, delno dostavo, ponovljen preklic, odziv med čakanjem, izpad P0/M2, iztek v tihem času in manjkajoč prevod.

Predlog shem in dovoljenj se lahko izdela pred potrditvijo D12. Odvisni razvoj A/I začne šele po celotnem človeškem prevzemu T z v D12 potrjeno različico pogodbe; nadomestka M1/M2 uporabita iste sheme, vendar ne nadomestita pravega P0. Pobudnik s pomočjo AI pripravi paket T, neodvisen človeški pregledovalec preveri kodo in pogodbo. Odgovorni nosilci še niso imenovani. Sprememba pogodbe zahteva uskladitev prizadetih ekip; nezdružljiva sprememba novo različico ali potrjen prehod.
