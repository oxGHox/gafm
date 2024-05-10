FROM oraclelinux:8.9

# Download packages to prep container
RUN    chmod +t /tmp /var/tmp && \
    update-ca-trust && \
    update-ca-trust force-enable && \
    dnf install -y openssl curl python3.11 git && \
    dnf clean all && \
    rm -rf /var/cache/dnf/ /var/tmp/* /tmp/* /var/tmp/.???* /tmp/.???*

# Disable ChaCha20 Algorithms
RUN set -eux; \
    disabledAlgorithms=' \
       TLS_CHACHA20_POLY1305_SHA256, \
       TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256, \
       TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256, \
       TLS_DHE_RSA_WITH_CHACHA20_POLY1305_SHA256, \
    '; \
    disabledAlgorithms="${disabledAlgorithms//[[:space:]]/}"; \
    sed -i "s/^jdk\.tls\.disabledAlgorithms=/jdk.tls.disabledAlgorithms=$disabledAlgorithms/" \
       /usr/share/crypto-policies/FIPS/java.txt;

# Set environment variables to ensure Python output is not buffered
ENV PYTHONUNBUFFERED=1

# Install Poetry by downloading the installation script and executing it
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to the system path
ENV PATH="/root/.local/bin:${PATH}"

# Change dir to pull gafm 
WORKDIR /usr/share

# Pull GAFM
RUN git clone https://github.com/mssalvatore/gafm.git 

# Change to gafm work dir
WORKDIR /usr/share/gafm

# Generate PEM and key
RUN openssl req -x509 -subj "/C=US/ST=Pennsylvania/L=Harrisburg/O=GAFM/CN=localdomain" \
        -nodes -days 365 -newkey rsa:2048 -keyout ./key.pem \
        -out cert.pem

# modify source python to statically assign for docker
RUN sed -i s/'Redis(host="127.0.0.1'/'Redis(host="gafm-redis'/g /usr/share/gafm/gafm/gafm.py
RUN sed -i s/'127.0.0.1'/'gafm-srv'/g /usr/share/gafm/gafm/gafm.py
RUN sed -i s/'localhost'/'gafm-redis'/g /usr/share/gafm/gafm/metrics.py

# Install project dependencies 
RUN poetry install

# Verify ENV set
ENV container oci
ENV PATH /root/.local/bin/:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

CMD ["poetry", "run", "python", "-m", "gafm"]

