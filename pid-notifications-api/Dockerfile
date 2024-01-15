FROM python:3.10.5 as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.1.15 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base as builder-base

RUN apt update \
    && apt upgrade -y \
    && apt install --no-install-recommends -y \
    curl \
    vim \
    nano \
    #netcat \
    gcc \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install poetry

WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./
COPY ./tests ./tests
COPY ./app ./app
RUN poetry install --no-dev --no-root

WORKDIR $PYSETUP_PATH
EXPOSE 8080

# Launch main python script
CMD ["poetry", "run", "start"]
