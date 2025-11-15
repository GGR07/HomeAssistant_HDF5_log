FROM ghcr.io/hassio-addons/base-python:17.0.0

# Per trovare il package Python in /usr/lib
ENV PYTHONPATH="/usr/lib"

# Dipendenze Python
RUN pip install --no-cache-dir requests

# Copia rootfs nello stage finale
COPY rootfs /

# Permessi eseguibili
RUN chmod a+x /usr/bin/logger.py \
    && chmod a+x /etc/services.d/hdf5_datalogger/run \
    && chmod a+x /etc/services.d/hdf5_datalogger/finish
