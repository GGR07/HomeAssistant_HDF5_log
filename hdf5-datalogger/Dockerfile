FROM ghcr.io/hassio-addons/base-python:12.2.0


COPY rootfs /

# Assicurati che i file eseguibili abbiano i permessi corretti
RUN chmod a+x /usr/bin/logger.py && \
    chmod a+x /etc/services.d/hdf5_datalogger/run && \
    chmod a+x /etc/services.d/hdf5_datalogger/finish
