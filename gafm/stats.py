"""A utility script for gathering stats about requests to the server."""

import tabulate
from redis import Redis

THRESHOLD = 10

r = Redis(host="localhost", port=6379, decode_responses=True)

request_count = {k: int(r.get(k)) for k in r.keys()}  # type: ignore [arg-type]

all_keys = list(request_count.keys())
all_keys.sort(key=request_count.get, reverse=True)  # type: ignore [arg-type]

data: list[tuple[str, str, int]] = []
for k, _v in request_count.items():
    if "-redirect" in k:
        continue

    _, __, ip, date = k.split(":")
    if request_count[k] <= THRESHOLD:
        continue

    data.append((date, ip, request_count[k]))

data.sort(key=lambda x: (x[0], x[2], x[1]), reverse=True)

table = [(x[0], x[1], f"{x[2]:,}") for x in data]

print()
print(f"\033[33mNOTE: ONLY SHOWING ROWS WHERE REQUESTS > {THRESHOLD}\033[0m")
print()
print(tabulate.tabulate(table, headers=["Date", "IP", "# requests"]))
print()
