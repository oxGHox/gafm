# GAFM - Go Ahead, Fuzz me

## How tos
### How to run GAFM
1. `sudo docker run -d -v redis-data:/data -p 127.0.0.1:6379:6379 --name redis-server redis --save 60 1 --loglevel warning`
1. `sudo capsh --keep=1 --user=$USER --inh=cap_net_bind_service --addamb=cap_net_bind_service -- -c "ulimit -Hn 524288 && poetry run python -m gafm"`

### How to access redis
`sudo docker run -it --network host --rm redis redis-cli -h 127.0.0.1`


NOTE: Run `ulimit -Hn` to see what the hard limit is.
