ARG BUILD_FROM=ghcr.io/hassio-addons/base-python:latest
FROM $BUILD_FROM

COPY run.sh /run.sh
RUN chmod a+x /run.sh

COPY src /app

CMD [ "/run.sh" ]
