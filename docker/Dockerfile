FROM python:3.11.9-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.0.1 \
    LANG=ru_RU.UTF-8 \
    LANGUAGE=ru_RU:ru \
    LC_ALL=ru_RU.UTF-8



RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Poetry installing
RUN pip install --no-cache-dir pipx && pipx ensurepath
RUN pipx install poetry==$POETRY_VERSION
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Poetry dependencies installing
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

COPY . .

COPY docker/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
