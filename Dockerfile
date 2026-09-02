# Runs the iam-shrink CLI in a slim Python image. Multi-stage keeps the final
# image free of build tooling.

# --- build stage ---
FROM python:3.14-slim@sha256:ce40764625a4ff50df3548277632e7f96c4e77fe75fa848aae9885476e7df5a4 AS build
WORKDIR /src
COPY . .
RUN pip install --no-cache-dir build && python -m build --wheel --outdir /dist

# --- runtime stage ---
FROM python:3.14-slim@sha256:ce40764625a4ff50df3548277632e7f96c4e77fe75fa848aae9885476e7df5a4
RUN adduser --disabled-password --uid 10001 app
COPY --from=build /dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl
USER app
# hardener: run this image with `docker run --read-only` for a read-only rootfs
ENTRYPOINT ["iam-shrink"]
