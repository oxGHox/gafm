"""A utility script for gathering stats about requests to the server."""

import tabulate
from redis import Redis

r = Redis(host="localhost", port=6379, decode_responses=True)

request_count = {k: int(r.get(k)) for k in r.keys()}  # type: ignore [arg-type]

all_keys = list(request_count.keys())
all_keys.sort(key=request_count.get, reverse=True)  # type: ignore [arg-type]

table: list[tuple[str, str, int]] = []
for k, _v in request_count.items():
    _, __, ip, date = k.split(":")
    table.append((date, ip, request_count[k]))

table.sort(key=lambda x: (x[2], x[0], x[1]), reverse=True)

print()
print("\033[33mNOTE: ONLY SHOWING ROWS WHERE REQUESTS > 3\033[0m")
print()
print(tabulate.tabulate([row for row in table if row[2] > 3], headers=["Date", "IP", "# requests"]))
print()
