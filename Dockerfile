# Runs the iam-shrink CLI in a slim Python image. Multi-stage keeps the final
# image free of build tooling.

# --- build stage ---
FROM python:3.12-slim AS build
WORKDIR /src
COPY . .
RUN pip install --no-cache-dir build && python -m build --wheel --outdir /dist

# --- runtime stage ---
FROM python:3.12-slim
RUN adduser --disabled-password --uid 10001 app
COPY --from=build /dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl
USER app
ENTRYPOINT ["iam-shrink"]
