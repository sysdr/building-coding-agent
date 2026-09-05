# Pinned by tag. Run `docker pull python:3.11.10-slim && docker inspect --format='{{index .RepoDigests 0}}' python:3.11.10-slim`
# after your first pull and record the digest in VERIFY.md — see the note there on why
# this file ships without a fabricated digest.
FROM python:3.11.10-slim

WORKDIR /app
COPY pyproject.toml .
COPY src ./src
COPY tests ./tests
COPY fixtures ./fixtures
COPY scripts ./scripts

RUN pip install --no-cache-dir --upgrade pip==24.3.1 \
    && pip install --no-cache-dir -e .

ENTRYPOINT ["apr"]
CMD ["doctor"]
