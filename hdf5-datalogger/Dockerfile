FROM ghcr.io/hassio-addons/base-python:17.0.0

# Installa le dipendenze Python dell'add-on
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copia la rootfs
COPY rootfs /

# Permessi eseguibili
RUN chmod a+x /usr/bin/logger.py && \
    chmod a+x /etc/services.d/hdf5_datalogger/run && \
    chmod a+x /etc/services.d/hdf5_datalogger/finish
