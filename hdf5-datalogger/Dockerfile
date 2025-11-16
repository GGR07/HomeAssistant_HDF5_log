FROM ghcr.io/hassio-addons/base-python:17.0.0

# Per trovare il package Python in /usr/lib
ENV PYTHONPATH="/usr/lib"

# Installa le dipendenze Python dell'add-on
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copia la rootfs nello stage finale
COPY rootfs /

# Permessi eseguibili
RUN chmod a+x /usr/bin/logger.py \
    && chmod a+x /usr/bin/compresser.py \
    && chmod a+x /etc/services.d/hdf5_datalogger/run \
    && chmod a+x /etc/services.d/hdf5_datalogger/finish \
    && chmod a+x /etc/services.d/hdf5_compresser/run \
    && chmod a+x /etc/services.d/hdf5_compresser/finish
