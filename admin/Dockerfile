FROM python:3.11-slim

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_HOME="/etc/poetry" \
    POETRY_CACHE_DIR="/tmp/poetry_cache" \
    POETRY_VERSION=1.7.0

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" \
    && poetry install --without bot --without dev --no-root \
    && pip uninstall -y poetry \
    && rm -rf /root/.cache \
    && rm -rf $POETRY_CACHE_DIR

CMD ["gunicorn", "-c", "admin/gunicorn_conf.py"]
