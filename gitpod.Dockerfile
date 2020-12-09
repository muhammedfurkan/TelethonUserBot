FROM gitpod/workspace-full

RUN mkdir /tmp/kite && \
    curl -fsSL https://linux.kite.com/dls/linux/current > /tmp/kite/kite-installer.sh && \
    cd /tmp/kite && \
    chmod +x ./kite-installer.sh && \
    ./kite-installer.sh --download && \
    ./kite-installer.sh --install && \
    rm -rf /tmp/kite
