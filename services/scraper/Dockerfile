FROM python:3.13-slim

WORKDIR /app

# Preserve the repo's relative layout inside the image: requirements.txt's
# `-e ../../packages/py-utils` line and py_utils' own runtime lookup of
# packages/common/topics.json both depend on packages/ and services/scraper/
# sitting in the same relative positions they occupy in the real repo.
COPY packages/py-utils ./packages/py-utils
COPY packages/common ./packages/common
COPY services/scraper ./services/scraper

# pip resolves the `-e ../../packages/py-utils` editable path against the
# working directory at install time, so this must run from services/scraper.
WORKDIR /app/services/scraper
RUN pip install --no-cache-dir -r requirements.txt

# config.toml lives next to main.py; run from src/ so load_config()'s
# cwd-relative default ("config.toml") resolves without extra copying.
WORKDIR /app/services/scraper/src
CMD ["python", "main.py"]
