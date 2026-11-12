# Osnovna slika je pripeta na digest (python 3.12.16, Debian 13). Posodobitev: DEVELOPER.md.
FROM python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
ARG INSTALL_DEV=0
# Varnostni popravek Debiana, ki ga pripeta osnovna slika še nima (CVE-2026-76844,
# CVE-2026-85091, CVE-2026-27171). Ob novejšem digestu osnovne slike ta korak odstranimo.
RUN apt-get update \
 && apt-get install -y --no-install-recommends --only-upgrade "zlib1g=1:1.3.dfsg+really1.3.1-1+deb13u1" \
 && rm -rf /var/lib/apt/lists/*
COPY requirements-build.lock requirements.lock requirements-dev.lock ./
# Samo zaklenjene različice s preverjenimi hashi; najprej posodobljen pip iz zaklepa.
# Produkcijska slika pip po namestitvi odstrani (med delovanjem ga ne potrebuje).
RUN python -m pip install --no-cache-dir --require-hashes -r requirements-build.lock \
 && if [ "$INSTALL_DEV" = "1" ]; then \
      python -m pip install --no-cache-dir --require-hashes --no-deps -r requirements-dev.lock \
      && python -m pip check; \
    else \
      python -m pip install --no-cache-dir --require-hashes --no-deps -r requirements.lock \
      && python -m pip check \
      && python -m pip uninstall -y pip; \
    fi
COPY . .
RUN useradd --no-create-home appuser
USER appuser
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
