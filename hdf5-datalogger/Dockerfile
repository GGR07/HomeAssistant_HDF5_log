FROM ghcr.io/hassio-addons/base-python:17.0.0

# Installa Python 3 + pip + requests (Alpine)
RUN apk add --no-cache python3 py3-pip py3-requests

# Copia la rootfs
COPY rootfs /

# Permessi eseguibili
RUN chmod a+x /usr/bin/logger.py && \
    chmod a+x /etc/services.d/hdf5_datalogger/run && \
    chmod a+x /etc/services.d/hdf5_datalogger/finish
