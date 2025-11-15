# Usa direttamente l'immagine base Python ufficiale degli add-on
FROM ghcr.io/home-assistant/base:3.15

# Copia la rootfs nel container
COPY rootfs /

# Assicurati che i file eseguibili abbiano i permessi corretti
RUN chmod a+x /usr/bin/my_program && \
    chmod a+x /etc/services.d/hdf5_datalogger/run && \
    chmod a+x /etc/services.d/hdf5_datalogger/finish

# Fine: l'avvio viene gestito da S6, nessun CMD necessario
