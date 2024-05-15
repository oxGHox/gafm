# GAFM - Go Ahead, Fuzz me

## How tos
### How to run GAFM
1. `sudo docker run -d -v redis-data:/data -p 127.0.0.1:6379:6379 --name redis-server redis --save 60 1 --loglevel warning`
1. `sudo capsh --keep=1 --user=$USER --inh=cap_net_bind_service --addamb=cap_net_bind_service -- -c "ulimit -Sn 524288 && poetry run python -m gafm"`

### How to access redis
`sudo docker run -it --network host --rm redis redis-cli -h 127.0.0.1`


NOTE: Run `ulimit -Hn` to see what the hard limit is.

### How to get metrics

`poetry run python -m gafm.metrics`

## Configuration options

GAFM can be configured by setting environment variables to the desired values.
For convenience, GAFM will search the current directory for a `.env` file.
Settings defined in the `.env` file will be read and used by GAFM. Note that
values set in environment variables take precedence over those in the `.env`
file.

### `GAFM_BIND_ADDRESS`

*Optional*, default value: `127.0.0.1`

The interface that GAFM will listen on

### `GAFM_HOT_RELOAD`

*Optional*, default value: `False`

Whether or not to reload GAFM automatically when code changes

### `GAFM_MAX_CACHE_SIZE`

*Optional*, default value: `65536`

The maximum number of randomly generated responses to cache

### `GAFM_MAX_SUBDIRS`

*Optional*, default value: `24`

The maximum number of subdirectories to include in a response

### `GAFM_MIN_SUBDIRS`

*Optional*, default value: `3`

The maximum number of subdirectories to include in a response

### `GAFM_PORT`

*Optional*, default value: `8080`

The port that GAFM will listen on

### `GAFM_REDIS_HOST`

*Optional*, default value: `127.0.0.1`

The IP address or hostname for the Redis server

### `GAFM_REDIS_PORT`

*Optional*, default value: `6379`

The port Redis is listening on

### `GAFM_SSL_CERTFILE`

*Optional*, default value: `None`

The path to an SSL certificate file; if this is not set, HTTP will be used.

### `GAFM_SSL_KEYFILE`

*Optional*, default value: `None`

The path to an SSL certificate file; if this is not set, HTTP will be used.
