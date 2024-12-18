FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /app/

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV PATH="/app/.venv/bin:$PATH"
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONPATH=/app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

COPY ./pyproject.toml ./uv.lock ./alembic.ini /app/
COPY ./app /app/app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

CMD ["fastapi", "run", "--workers", "4", "app/main.py"]