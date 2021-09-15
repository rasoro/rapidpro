FROM python:3.6-slim as build-poetry

WORKDIR /app

COPY ./pyproject.toml .
COPY ./poetry.lock .

RUN python -m pip install -U poetry
RUN poetry export --without-hashes --output requirements.txt

FROM python:3.6-slim

ARG APP_UID=1000
ARG APP_GID=1000

ARG COMPRESS_ENABLED
ARG BRANDING_ENABLED
 
ARG FLOWEDITOR_VERSION
ARG FLOWEDITOR_REPO
ARG FLOWEDITOR_BRANCH


ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND  noninteractive

ENV PROJECT           rapidpro
ENV PROJECT_PATH      /app
ENV PROJECT_CONF      ${PROJECT_PATH}-conf
ENV NPM_CONFIG_PREFIX /opt/npm-globals
ENV PATH              "${NPM_CONFIG_PREFIX}/bin:${PATH}"
ENV FLOWEDITOR_TGZ "nyaruka-flow-editor-${FLOWEDITOR_VERSION}.tgz"

ENV APP_UID=${APP_UID} 
ENV APP_GID=${APP_GID} 

RUN addgroup --gid "${APP_GID}" app_group \
  && useradd --system -m -d ${PROJECT_PATH} -u "${APP_UID}" -g "${APP_GID}" app_user

# set work directory
WORKDIR ${PROJECT_PATH}

RUN apt-get update \
 && apt-get install --no-install-recommends --no-install-suggests -y apt-utils \
 && apt-get install --no-install-recommends --no-install-suggests -y gcc bzip2 git curl libpq-dev gettext \
    libgdal-dev python3-cffi python3-gdal vim

RUN curl -sL https://deb.nodesource.com/setup_12.x | bash - \
 && apt-get install --no-install-recommends --no-install-suggests -y nodejs

RUN rm -rf /var/lib/apt/lists/*

COPY --from=build-poetry /app/requirements.txt /tmp/dep/
RUN pip install --no-cache-dir -r /tmp/dep/requirements.txt 

COPY --chown=app_user:app_group . .

RUN npm install --global \
  coffeescript \
  less \
  yarn

RUN npm install

RUN git clone --branch ${FLOWEDITOR_BRANCH} ${FLOWEDITOR_REPO} && \
    cd floweditor && \
    yarn install && \
    yarn run build && \
    npm pack && \
    cd .. && \
    npm install ./floweditor/${FLOWEDITOR_TGZ} && \
    npm prune --production

RUN ln -s $PROJECT_PATH/temba/settings.py.prod $PROJECT_PATH/temba/settings.py

EXPOSE 8000
EXPOSE 8001
ENTRYPOINT ["sh", "./docker/start"]
