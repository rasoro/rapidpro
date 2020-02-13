ARG DOCKER_REGISTRY_IMAGE

FROM $DOCKER_REGISTRY_IMAGE

COPY . .
RUN ln -s /app/temba/settings.py.prod /app/temba/settings.py

COPY ./docker/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
RUN chown django /start

RUN chown -R django /app
USER django

EXPOSE 8000
ENTRYPOINT ["/start"]

