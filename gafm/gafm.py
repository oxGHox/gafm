import random
from datetime import datetime
from functools import lru_cache
from http import HTTPStatus
from itertools import islice
from pathlib import Path
from string import Template
from typing import Annotated, Final, Iterable

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from redis.asyncio import Redis

from .config import load_config

DIRECTORY_RESPONSE_TEMPLATE: Final = Template(
    """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Directory listing for $current_dir</title>
</head>
<body>
<h1>Directory listing for $current_dir</h1>
<hr>
<ul>
$formatted_links
</ul>
<hr>
</body>
</html>"""
)

CONFIG = load_config(env_file=Path.cwd() / ".env")
# TODO: Log config


class RandomWordList:
    """
    An infinitely long iterable of random words based on a word list
    """

    def __init__(self, wordlist_path: Path):
        self._words = self._load_wordlist(wordlist_path)
        random.shuffle(self._words)  # noqa: DUO102

        self.index = 0
        self.max_index = len(self._words) - 1

    @staticmethod
    def _load_wordlist(wordlist_path: Path):
        with open(wordlist_path, "r") as f:
            return [line.rstrip() for line in f.readlines()]

    def __iter__(self):
        return self

    def __next__(self):
        retval = self._words[self.index]
        self.index += 1

        if self.index > self.max_index:
            self.index = 0
            random.shuffle(self._words)  # noqa: DUO102

        return retval


@lru_cache
def redis_connection() -> Redis:
    print("CONNECTING TO REDIS")
    return Redis(host=str(CONFIG.redis.host), port=CONFIG.redis.port, decode_responses=True)


wordlist_path = Path(__file__).parent.resolve() / "wordlist.txt"
random_words = RandomWordList(wordlist_path)
app = FastAPI()


@app.get("{full_path:path}")
async def gafm(
    request: Request, full_path: str, redis: Annotated[Redis, Depends(redis_connection)]
) -> HTMLResponse:
    await redis.incr(
        f"gafm:requests:{request.client.host}:{datetime.utcnow().strftime('%Y-%m-%d')}"
    )

    if full_path == "/robots.txt" or full_path == "/favicon.ico":
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    content = get_dir_html_response_content(full_path)

    if not full_path[-1] == "/":
        # Ferroxbuster will start to ignore our redirect responses if they
        # don't include content of varying length, lines, words, etc.
        # Therefore, we use an HTML response instead of a RedirectResponse.
        return HTMLResponse(
            headers={"Location": full_path.rstrip("/") + "/"},
            status_code=HTTPStatus.MOVED_PERMANENTLY,
            content=content,
        )

    return HTMLResponse(content=content)


def get_dir_html_response_content(path: str) -> str:
    # Normalize path so that caching works properly
    normalized_path = normalize_path(path)
    return generate_response_content(normalized_path)


def normalize_path(path: str) -> str:
    return path.rstrip("/") + "/"


# Caching this means we give a consisent view of a resource across multiple
# requests, at least for a little while
@lru_cache(maxsize=CONFIG.max_cache_size)
def generate_response_content(path: str) -> str:
    dir_names = generate_random_dir_names()
    return format_dir_listing_response_body(path, dir_names)


def generate_random_dir_names():
    num_dirs = random.randint(CONFIG.min_subdirs, CONFIG.max_subdirs)  # noqa: DUO102
    return [dir_name + "/" for dir_name in islice(random_words, num_dirs)]


def format_dir_listing_response_body(current_dir: str, dirs: Iterable[str]) -> str:
    formatted_links = "\n".join(
        [f"<li><a href=\"{dirname.replace(' ', '%20')}\">{dirname}</a></li>" for dirname in dirs]
    )
    return DIRECTORY_RESPONSE_TEMPLATE.substitute(
        current_dir=current_dir, formatted_links=formatted_links
    )


def main():
    uvicorn.run(
        "gafm.gafm:app",
        host=str(CONFIG.bind_address),
        port=CONFIG.port,
        reload=CONFIG.hot_reload,
        ssl_certfile=CONFIG.ssl_certfile,
        ssl_keyfile=CONFIG.ssl_keyfile,
        proxy_headers=False,
        forwarded_allow_ips=None
    )


if __name__ == "__main__":
    main()
