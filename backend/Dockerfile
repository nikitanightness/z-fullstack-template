FROM debian:trixie-slim AS base

FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Configure 'uv'
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1
ENV UV_PYTHON_PREFERENCE=only-managed
ENV UV_PYTHON_INSTALL_DIR=/python

# Install python
RUN --mount=type=bind,source=.python-version,target=.python-version \
    uv python install

# Copy project to 'builder'
WORKDIR /app
COPY . .

# Create virtual environment with required dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

FROM base AS runtime

# Copy python from 'builder'
COPY --from=builder --chown=python:python /python /python

# Copy project from 'builder'
COPY --from=builder --chown=app:app /app /app

# Add .venv binaries (including 'python3') to $PATH
ENV PATH="/app/.venv/bin:$PATH"

# Go to app directory
WORKDIR /app

# Create startup script
COPY <<EOF start.sh
#!/bin/bash
alembic upgrade head && python -m app $*
EOF
RUN chmod +x start.sh

# Run app
ENTRYPOINT ["./start.sh"]
CMD [""]
