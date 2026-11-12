# Register prispevkov

Status: osnutek, 12. november 2026. Namen: sledljivost avtorstva in uporabe AI, kot zahteva [CONTRIBUTING.md](../../CONTRIBUTING.md) in pogoji D08. Register ne podeljuje pravic, ne nadomešča izjav avtorjev in ne pomeni institucionalne potrditve. AI sistem ne more sam podpisati pravne izjave; vpis sprejme in odgovarja zanj človek.

## Vpisi

| Prispevajoči | Vrsta | Vloga | Obseg | Datum | Odgovorni človek |
| --- | --- | --- | --- | --- | --- |
| Mitja Pirih | Človek | Pobudnik, koordinator, tehnični nosilec (osebni sprejem D03) | Cilj, obseg, odločitve, usmerjanje in sprejem dela | od 5. 10. 2026 | Mitja Pirih |
| Claude (Anthropic), model Claude Sonnet 5.5 | AI | Pisec kode in dokumentacije po navodilih pobudnika | Faze 0 do 6: ogrodje P0, model, prijava, API, uvoz CSV, osnutek pogodbe D12, nadomestka M1/M2, testi, navodila za razvijalce (PR #31 do #37) | 12. 11. 2026 | Mitja Pirih |
| Codex (OpenAI), različica modela: ni znano | AI | neodvisni pregledovalec | bral in zaganjal kodo, napisal poročilo; kode ni spreminjal | 12. 11. 2026 | Mitja Pirih |
| DeepSeek (DeepSeek), različica modela: ni znano | AI | neodvisni pregledovalec | bral in zaganjal kodo, napisal poročilo; kode ni spreminjal | 12. 11. 2026 | Mitja Pirih |
| Claude (Anthropic), model Claude Opus 5.5 | AI | Pisec popravkov po navodilih pobudnika | Preverjanje ugotovitev prvega pregleda, popravki kode in testov ter uskladitev dokumentacije ([zapis o odpravi](../pregledi/2026-11-odprava-prvega-pregleda-P0.md)); poročil pregledovalcev vsebinsko ni spreminjal (le preimenoval datoteki) | 12. 11. 2026 | Mitja Pirih |

Kodo, ki jo je napisal AI, sta prvič pregledala druga sistema AI (Codex/OpenAI in DeepSeek, PR #39 in #40) po [kontrolnem seznamu](pregled-P0-kontrolni-seznam.md); človeški pregled ni opravljen, ponovni pregled po popravkih ni izveden.

## Kako se vpiše nov prispevajoči

Vsak prispevajoči (človek ali AI) v svojem pull requestu doda vrstico v tabelo z: imenom ali oznako sistema in ponudnikom, vrsto, vlogo, obsegom (kaj je pisal, kaj samo bral), datumom in odgovornim človekom. Za AI navedite le, kar sistem zanesljivo ve o sebi; verzije ne ugibajte, zapišite »ni znano«. Odgovorni človek vpis prebere in ga z združitvijo pull requesta sprejme.

Glede pravic: prispevek kode je pod EUPL 1.2 ([LICENSE](../../LICENSE)); licenca dokumentacije in pravice dijaških prispevkov sta še odprti (D15, D08).
