# Pinned by tag. Pin the digest yourself after your first pull:
#   docker inspect --format='{{index .RepoDigests 0}}' python:3.11.10-slim
# This file ships without a digest on purpose: a digest that was never
# actually pulled and checked is worse than no digest at all.
FROM python:3.11.10-slim

WORKDIR /work
COPY pyproject.toml ./
COPY src ./src
COPY configs ./configs
COPY fixtures ./fixtures
COPY tests ./tests
COPY scripts ./scripts

# The exact tokeniser is an extra; fall back to the core package when the
# build has no network, exactly as the native path does.
RUN pip install --no-cache-dir -e ".[exact]" || pip install --no-cache-dir -e .

ENTRYPOINT ["apr"]
CMD ["doctor"]
