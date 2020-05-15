FROM python:3.6-alpine

ARG COMPRESS_ENABLED
ARG BRANDING_ENABLED

ENV NPM_CONFIG_PREFIX /opt/npm-globals
ENV PATH              "${NPM_CONFIG_PREFIX}/bin:${PATH}"
ENV PYTHONUNBUFFERED 1

RUN mkdir /$PROJECT \
 && mkdir $NPM_CONFIG_PREFIX

WORKDIR /app

RUN apk update \
  && apk add --virtual build-deps gcc python3-dev musl-dev \
  && apk add postgresql-client postgresql-dev libxml2-dev libxslt-dev gettext-dev \
  && apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
  && apk add libffi-dev py-cffi gettext nodejs npm git

RUN apk add --no-cache -X http://dl-cdn.alpinelinux.org/alpine/v3.11/community/ \
  gdal gdal-dev geos-dev py3-gdal \
  && rm -rf /var/cache/apk/*

RUN addgroup -S django \
  && adduser -S -G django django

RUN chown -R django:django $NPM_CONFIG_PREFIX

COPY ./pip-freeze.txt /app
RUN pip install --no-cache-dir -r pip-freeze.txt

COPY . .
RUN ln -s /app/temba/settings.py.prod /app/temba/settings.py

COPY ./docker/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
RUN chown django /start

RUN chown -R django /app
USER django

RUN npm install --global \
  coffeescript \
  less@2.7.1 \
  yarn

COPY ./package.json /app

RUN npm install

EXPOSE 8000
ENTRYPOINT ["/start"]
