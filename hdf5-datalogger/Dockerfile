FROM ghcr.io/hassio-addons/base-python:17.0.0

COPY requirements.txt /requirements.txt

RUN pip install -r requirements.txt

# Copia la rootfs
COPY rootfs /

# Permessi eseguibili
RUN chmod a+x /usr/bin/logger.py && \
    chmod a+x /etc/services.d/hdf5_datalogger/run && \
    chmod a+x /etc/services.d/hdf5_datalogger/finish
