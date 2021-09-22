ARG NODE_VERSION=10
FROM node:${NODE_VERSION}-buster as build-floweditor
 
ARG FLOWEDITOR_REPO
ARG FLOWEDITOR_BRANCH

WORKDIR /app

RUN mkdir /dist && \
    git clone --branch ${FLOWEDITOR_BRANCH} ${FLOWEDITOR_REPO} . && \
    yarn install && \
    yarn build  && \
    yarn pack -f /dist/floweditor.tgz
  

FROM python:3.6-slim-buster AS base

ARG APP_UID=1000
ARG APP_GID=1000

ARG COMPRESS_ENABLED
ARG BRANDING_ENABLED
ARG NODE_VERSION

ENV APP_UID=${APP_UID} \
  APP_GID=${APP_GID} \
  COMPRESS_ENABLED=${COMPRESS_ENABLED} \
  BRANDING_ENABLED=${BRANDING_ENABLED} \
  PYTHONUNBUFFERED=1 \
  DEBIAN_FRONTEND=noninteractive \
  PROJECT="rapidpro" \
  PROJECT_PATH="/app" \
  PROJECT_CONF=${PROJECT_PATH}-conf \
  NPM_CONFIG_PREFIX="/opt/npm-globals" \
  PATH="${NPM_CONFIG_PREFIX}/bin:${PATH}" \
  NODE_VERSION=${NODE_VERSION}

RUN addgroup --gid "${APP_GID}" app_group \
  && useradd --system -m -d ${PROJECT_PATH} -u "${APP_UID}" -g "${APP_GID}" app_user

# set work directory
WORKDIR ${PROJECT_PATH}

RUN apt-get update \
 && apt-get install --no-install-recommends --no-install-suggests -y apt-utils \
 && apt-get install --no-install-recommends --no-install-suggests -y gcc bzip2 git curl libpq-dev gettext \
    libgdal-dev python3-cffi python3-gdal vim \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sL https://deb.nodesource.com/setup_$NODE_VERSION.x | bash - \
 && apt-get install --no-install-recommends --no-install-suggests -y nodejs \
 && rm -rf /var/lib/apt/lists/*

FROM base as build-poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN python -m pip install -U pip  \
 && pip install poetry \
 && poetry add weni-rp-apps \
 && poetry export --without-hashes --output requirements.txt

FROM base

COPY --from=build-poetry /app/requirements.txt /tmp/dep/
RUN pip install --no-cache-dir -r /tmp/dep/requirements.txt

COPY --chown=app_user:app_group . ./

RUN npm install -g less

RUN npm install

COPY --from=build-floweditor /dist/floweditor.tgz /tmp/dep/
RUN npm install /tmp/dep/floweditor.tgz


RUN ln -s $PROJECT_PATH/temba/settings.py.prod $PROJECT_PATH/temba/settings.py

EXPOSE 8000
EXPOSE 8001
ENTRYPOINT ["sh", "./docker/start"]
