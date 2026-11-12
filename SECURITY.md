# Varnostne težave

Projekt ima referenčno kodo P0 za razvoj na izmišljenih podatkih; produkcijske namestitve in resničnih podatkov ni. Pravila veljajo že zdaj.

## Kako sporočiti varnostno težavo

Zasebna prijava ranljivosti v GitHubu je omogočena. V zavihku **Security** izberite **Report a vulnerability** oziroma uporabite [zasebno prijavo](https://github.com/odprta-sola/solska-platforma/security/advisories/new). Dostop do zasebnih prijav določajo pravice računov v GitHubu. Število upravičenih računov in nadomeščanje je treba preveriti; to besedilo ne potrjuje, da sta imenovana dva skrbnika.

- Tehničnih podrobnosti, načinov zlorabe ali skrivnosti ne objavljajte v javnih Issues.
- Za dokaz uporabite izmišljene oziroma zmanjšane podatke; ne prilagajte produkcijskih izvozov ali osebnih podatkov.
- Ob opaženi objavi skrivnosti ali osebnih podatkov navedite mesto težave brez ponovnega kopiranja vsebine.

Po D14 prijave obravnava pobudnik. Za namestnika je 12. 11. 2026 določen Aleksandar (`alexlandich`), ki ima kot admin repozitorija dostop do zasebnih prijav; njegov pisni sprejem vloge je še odprt. Roki potrditve prejema, ocene resnosti in odziva še niso potrjeni (predlog: 3 delovni dnevi, 7 dni, 30 dni).

## Obravnava

Vzdrževalec prijavo potrdi, oceni resnost in popravek objavi šele po odpravi težave. Roki odgovora so odprta naloga v [registru odločitev](docs/projekt/odlocitve.md) (D14).

## Kršitev varstva osebnih podatkov

Ranljivost v kodi še ni kršitev. Kršitev je dejanski dostop nepooblaščene osebe do osebnih podatkov, njihovo razkritje, sprememba, izguba ali uničenje (čl. 4(12) GDPR). Postopek je osnutek: dokončno ga potrdijo šola, njena pooblaščena oseba za varstvo podatkov (DPO) in odločitvi D07 ter D14.

### Kdo odloča

- **Upravljavec je šola**, ki ima namestitev. Šola se odloči, ali obvesti Informacijskega pooblaščenca (čl. 33) in posameznike (čl. 34). Šola tudi vodi evidenco kršitev.
- **Skrbnik namestitve** je tisti, ki namestitev upravlja, šola ali gostitelj po D04. Skrbnik kršitev zajezi in zavaruje sledi. Če je zunanji obdelovalec, šolo obvesti brez nepotrebnega odlašanja (čl. 33(2)).
- **Vzdrževalci projekta** (D14) nimajo dostopa do podatkov šol. Šoli pomagajo pri oceni, kadar je vzrok v kodi, in ranljivost obravnavajo po zgornjem postopku.

### Koraki

1. **Takoj sporočite.** Kdor opazi kršitev (zaposleni, dijak, skrbnik ali vzdrževalec), o njej takoj obvesti odgovorno osebo šole in DPO. Če je vzrok morda v kodi, pošlje tudi zasebno prijavo ranljivosti. Zapišite, kaj ste opazili in kdaj, ter kje se to vidi. Osebnih podatkov ne kopirajte v sporočila, Issues ali klepet.
2. **Rok teče od zavedanja.** Šola Informacijskega pooblaščenca obvesti brez nepotrebnega odlašanja, po možnosti najpozneje v **72 urah** od trenutka, ko se je kršitve zavedla. Obvestilo ni potrebno, če kršitev verjetno ne pomeni tveganja za posameznike. Če niso znana vsa dejstva, šola v roku pošlje delno obvestilo in ga pozneje dopolni (čl. 33(4)).
3. **Zajezitev.** Skrbnik namestitve ukrepa po potrebi:
   - onemogoči prizadete račune (`is_active`);
   - izbriše seje, s čimer odjavi vse uporabnike;
   - onemogoči ali zamenja servisne žetone M1/M2 (`ServiceClient.active` in nov žeton z `create_service_client`);
   - odvzame povezave ali upravičenja na zaslonih evidence;
   - zamenja `DJANGO_SECRET_KEY` in druge skrivnosti, če so izpostavljene.

   Dokazov ne briše: dnevnikov, sledi sprememb in sledi vpogledov.
4. **Ocena tveganja.** Šola z DPO oceni, katere vrste podatkov in koliko oseb je prizadetih ter kakšne so verjetne posledice. Ali gre za mladoletne, zviša tveganje. Pri tem si pomaga s sledjo vpogledov (`AccessAudit`: kdo je odprl katero osebo), sledjo sprememb (`ChangeAudit`) in izvozom podatkov posamezne osebe. Ti prikažejo, kateri zapisi so bili vidni, ne pa, kaj je bilo kopirano.
5. **Obvestilo posameznikom.** Ob verjetnem velikem tveganju šola brez nepotrebnega odlašanja obvesti prizadete starše, dijake oziroma zaposlene (čl. 34). Obvestilo v jasnem jeziku pove:
   - kaj se je zgodilo;
   - verjetne posledice;
   - sprejete ukrepe;
   - kaj lahko posameznik naredi sam, na primer zamenja geslo ali je pozoren na lažna sporočila;
   - kontakt DPO.
6. **Evidenca.** Šola zapiše vsako kršitev, tudi tisto, o kateri ni obvestila, z dejstvi, posledicami in ukrepi (čl. 33(5)).
7. **Odprava in poročilo.** Vzrok se odpravi. Če je vzrok v kodi, se popravek objavi kot varnostni nasvet. Vzdrževalci zapišejo poročilo brez osebnih podatkov in morebitne spremembe tega postopka.

### Osebni podatki v repozitoriju

V repozitoriju, Issues, PR-jih in prilogah so dovoljeni samo izmišljeni podatki. Kdor tam opazi resnične osebne podatke, o tem zasebno obvesti vzdrževalca (zasebna prijava). V obvestilu navede samo mesto in podatkov ne kopira. Vzdrževalec:

- vsebino takoj skrije ali odstrani (komentar, priloga, PR);
- obvesti šolo, katere podatki so izpostavljeni, ta pa oceni tveganje po zgornjih korakih.

Odstranitev iz že objavljene zgodovine Git in zahteva podpori GitHub za odstranitev predpomnjenih pogledov sta izjemi od pravila, da objavljene zgodovine ne prepisujemo. O njiju izrecno odloči nosilec.

Informacijski pooblaščenec: [www.ip-rs.si](https://www.ip-rs.si/) (obrazec in navodila za prijavo kršitve).
