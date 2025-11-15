FROM ghcr.io/hassio-addons/base-python:17.0.0

RUN pip install ---no-cache-dir requests==2.32.3

# Copia la rootfs
COPY rootfs /

# Permessi eseguibili
RUN chmod a+x /usr/bin/logger.py && \
    chmod a+x /etc/services.d/hdf5_datalogger/run && \
    chmod a+x /etc/services.d/hdf5_datalogger/finish
