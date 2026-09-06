# Packages the HTTP API service only (docs/api/README.md). The CLI and the
# MCP server (packages/mcp-server) are not part of this image.
FROM python:3.12-slim AS build
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .

FROM python:3.12-slim
RUN useradd --create-home --shell /usr/sbin/nologin app
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin
USER app
EXPOSE 8000
CMD ["uvicorn", "whisper_street.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
