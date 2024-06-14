FROM python:3.9-alpine

# Set environment variables to ensure Python output is not buffered
ENV PYTHONUNBUFFERED=1

# Install required packages
RUN apk add --no-cache openssl curl git poetry gcc python3-dev libffi-dev build-base


# Add GAFM Packages
ADD gafm /usr/share/gafm/gafm
ADD pyproject.toml /usr/share/gafm
ADD poetry.lock /usr/share/gafm

# Change to gafm work dir
WORKDIR /usr/share/gafm

# Generate PEM and key
RUN openssl req -x509 -subj "/C=US/ST=Pennsylvania/L=Harrisburg/O=GAFM/CN=localdomain" \
        -nodes -days 365 -newkey rsa:2048 -keyout key.pem \
        -out cert.pem

# Install project dependencies 
RUN poetry --no-dev install

# Verify ENV settings
ENV PATH /root/.local/bin/:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

CMD ["poetry", "run", "python", "-m", "gafm"]
