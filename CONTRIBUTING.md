# Sodelovanje pri Odprti šoli

## Predlogi in spremembe

Vprašanje ali večji predlog odprite v issueju. Navedite problem, predlagano rešitev in vpliv na uporabnike ali obseg.

Spremembe pripravite v ločeni veji in odprite pull request. Opišite namen in preverjanje. Glavna veja je zaščitena; ne prepisujte njene zgodovine.

Dokumenti imajo status osnutek, za pregled ali potrjeno. Potrjen dokument vsebuje datum in odgovorno osebo. Merge sam ne pomeni odobritve šol.

## Javna vsebina

Uporabljajte izmišljene testne podatke. Ne vključujte osebnih kontaktnih seznamov, produkcijskih izvozov, gesel, ključev ali internih zapisov brez ustrezne priprave za objavo.

Varnostne težave, ki bi razkrile podatke ali omogočile zlorabo, se najprej obravnavajo zasebno z vzdrževalcem. Zasebna prijava ranljivosti v GitHubu je omogočena (glej [SECURITY.md](SECURITY.md)); nosilec obravnave in roki odziva se določijo pred prvo kodo oziroma vključitvijo zunanjih ekip; ne objavljajte skrivnosti ali resničnih podatkov v issueju.

## Dokumentacija

Aktivna dokumentacija je v docs/ v obliki Markdown. PDF in Word sta obliki za posredovanje ob mejnikih. Pomembne odločitve povežite z registrom odločitev. Pri navedbah ločite izmerjene podatke, interpretacijo in predlog.

## Licenciranje prispevkov

Programska koda je pod licenco **EUPL 1.2** ([LICENSE](LICENSE)), dokumentacija pod **CC BY-SA 4.0** ([LICENSE-dokumentacija.md](LICENSE-dokumentacija.md)). Z oddajo prispevka (pull requesta) soglašate, da je prispevek licenciran pod isto licenco kot del projekta, v katerega spada (koda pod EUPL 1.2, besedila pod CC BY-SA 4.0). Odločitvi D08 in D15 sta zapisani v [registru odločitev](docs/projekt/odlocitve.md).

### Pogoji za združitev prispevka

1. **Izvor in podpis (DCO).** Vsak commit vsebuje vrstico `Signed-off-by: Ime <e-naslov>` (`git commit -s`). S podpisom potrjujete [Developer Certificate of Origin 1.1](https://developercertificate.org/): prispevek ste napisali sami ali ga smete objaviti pod licenco projekta. Podpis preveri CI.
2. **Ime in vzdevek.** Ime v podpisu je lahko vzdevek, če je vaša identiteta znana projektu prek šolske izjave. Mladoletnim priporočamo vzdevek in GitHubov skriti e-naslov (`…@users.noreply.github.com`), ker je git zgodovina javna in trajna.
3. **Mladoletni avtorji.** Za združitev prispevka avtorja, mlajšega od 18 let, potrebujemo enkratno pisno izjavo avtorja in soglasje staršev oziroma zakonitih zastopnikov. Izjave ni treba urejati vnaprej: ob prvem pull requestu vam mentor posreduje obrazec. Izjavo hrani šola; v repozitoriju je ni. Ko je urejena, mentor ali vzdrževalec pull requestu doda oznako `avtor-urejen`, ki velja tudi za vse vaše poznejše prispevke. Praga »majhnih« prispevkov brez izjave ni.
4. **Polnoletni avtorji** zadostijo z DCO; mentor ali vzdrževalec doda oznako `avtor-urejen` po preverjeni polnoletnosti.
5. **Uporaba orodij AI.** V opisu pull requesta navedite, ali in kako ste uporabili orodja AI. Za prispevek odgovarjate vi, tudi za del, ki ga je predlagalo orodje.
6. **Prostovoljnost.** Ocena pri pouku ali v krožku ne sme biti odvisna od soglasja z javno licenco. Dijak brez izjave lahko dela v svoji veji ali kopiji in je ocenjen enako; njegov prispevek se le ne združi v projekt.

Dijaki prispevajo prek lastnega forka. Oznake `avtor-urejen` ne potrebujejo samo vzdrževalci, navedeni v [`.github/vzdrzevalci.txt`](.github/vzdrzevalci.txt); seznam se spremeni samo prek pull requesta.

Pred sprejemom kode se preverijo tudi licence odvisnosti. Skupnih varnostnih funkcij ne razvijajte na novo brez dogovora s tehničnim nosilcem.

## Pregled

Dokumentacijo preverite glede na izvor, številke, povezave in jasno označen status. Kodo preverite s smiselnimi testi ter namestitvijo na testnih podatkih. Produkcijski prevzem sledi ločenim merilom in ni posledica samega merge.
