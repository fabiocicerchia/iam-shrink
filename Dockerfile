# Runs the iam-shrink CLI in a slim Python image. Multi-stage keeps the final
# image free of build tooling.

# --- build stage ---
FROM python:3.14-slim@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6 AS build
WORKDIR /src
COPY . .
# `pip wheel` drives the build backend directly, so the image needs no
# separately-installed (and separately-pinned) build frontend.
RUN pip wheel --no-cache-dir --no-deps -w /dist .

# --- runtime stage ---
FROM python:3.14-slim@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6
RUN adduser --disabled-password --uid 10001 app
COPY --from=build /dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl
USER app
# hardener: run this image with `docker run --read-only` for a read-only rootfs
ENTRYPOINT ["iam-shrink"]
