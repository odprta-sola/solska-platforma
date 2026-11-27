# Testno okolje za oddaljeni pregled

Namen: oseba na daljavo pregleda P0 (npr. [ročni pregled dostopnosti](../../docs/projekt/pregled-dostopnosti-P0.md) z bralnikom zaslona) na **izmišljenih podatkih**. To ni namestitev za šolo (D04) in ne sme vsebovati resničnih podatkov.

Kaj je drugače kot pri razvoju (`docker-compose.yml` v korenu):

- produkcijski način: `DJANGO_DEBUG=0`, gunicorn s tremi delavci, slika brez razvojnih paketov, brez nadomestkov M1/M2 (`STUBS` prazen);
- vsebnik posluša samo na `127.0.0.1:${PORT}`; zunaj ga objavi posrednik HTTPS ([primer nginx](nginx.conf.primer)) z dodatnim geslom (Basic Auth) in `noindex`;
- piškotki seje in CSRF samo prek HTTPS; Django zaupa glavi `X-Forwarded-Proto`, ki jo nastavi posrednik;
- pošte ni (obnova gesla je v P0 izklopljena); storitev `cleanup` vsako uro počisti začasne datoteke.

## Namestitev

```bash
git clone https://github.com/odprta-sola/solska-platforma.git odprta-sola-test
cd odprta-sola-test/deploy/testno-okolje
cp env.primer .env && chmod 600 .env   # vpišite PUBLIC_HOST in naključni skrivnosti
docker compose up --build -d --wait
docker compose exec -e SEED_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(18))')" p0 python manage.py seed_test_data
```

Geslo testnih računov pred zagonom shranite (npr. v `.env` kot komentar ali v upravljalnik gesel) in ga pregledovalcu predajte po ločeni poti, ne v repozitoriju ali javnem kanalu.

Posrednik: DNS zapis za `PUBLIC_HOST` na strežnik, certifikat (npr. `certbot certonly --webroot`), datoteka `htpasswd` in vhost po primeru; pred ponovnim nalaganjem `nginx -t`.

## Posodobitev in odstranitev

```bash
git pull && docker compose up --build -d --wait     # nova različica, podatki ostanejo
docker compose down -v                              # odstrani vsebnike in bazo
```

Ob odstranitvi izbrišite tudi vhost, `htpasswd` in certifikat (`certbot delete --cert-name <ime>`).
