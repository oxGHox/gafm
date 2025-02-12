from http import HTTPStatus
from pathlib import Path
from typing import Generator
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from gafm.gafm import RandomWordList, app, format_dir_listing_response_body, redis_connection


@pytest.fixture(scope="session")
def wordlist() -> list[str]:
    return ["these", "aren't", "the", "droids", "you're", "looking", "for"]


@pytest.fixture(scope="session")
def wordlist_path(tmp_path_factory: pytest.TempPathFactory, wordlist: list[str]) -> Path:
    wlp = tmp_path_factory.mktemp("wordlist_dir", numbered=True) / "wordlist.txt"
    with open(wlp, "wt") as f:
        f.write("\n".join(wordlist))

    return wlp


def test_random_wordlist(
    wordlist_path: Path,
    wordlist: list[str],
):
    collected_words_1 = []
    collected_words_2 = []
    random_words = RandomWordList(wordlist_path)

    for _ in range(0, len(wordlist)):
        collected_words_1.append(next(random_words))

    for _ in range(0, len(wordlist)):
        collected_words_2.append(next(random_words))

    assert len(collected_words_1) == len(collected_words_2)
    assert collected_words_1 != collected_words_2
    assert set(collected_words_1) == set(collected_words_2)
    assert sorted(collected_words_1) == sorted(collected_words_2)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[redis_connection] = lambda: AsyncMock()
    yield TestClient(app, follow_redirects=False)
    app.dependency_overrides.clear()


@pytest.mark.parametrize("file_name", ["robots.txt", "favicon.ico"])
def test_gafm__404_files(client: TestClient, file_name: str):
    response = client.get(file_name)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_gafm__directory_redirect(client: TestClient):
    response = client.get("/test_dir")

    assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
    assert response.headers["location"] == "/test_dir/"


def test_gafm__directory_listing(client: TestClient, wordlist: list[str]):
    response = client.get("/test_dir/")

    assert response.status_code == HTTPStatus.OK
    assert any((word in response.text for word in wordlist))
    assert "<html>" in response.text
    assert "Directory listing for /test_dir/" in response.text


def test_gafm__directory_listing_multiple_slashes(client: TestClient, wordlist: list[str]):
    response = client.get("/test_dir////")

    assert response.status_code == HTTPStatus.OK
    assert any((word in response.text for word in wordlist))
    assert "<html>" in response.text
    assert "Directory listing for /test_dir/" in response.text


def test_format_dir_listing_response_body__current_dir():
    response = format_dir_listing_response_body("test_dir/", ["file1", "file2"])

    assert response.count("Directory listing for test_dir/") == 2


def test_format_dir_listing_response_body__dir_with_spaces():
    response = format_dir_listing_response_body("test_dir/", ["dir 1/"])

    assert '<li><a href="dir%201/">dir 1/</a></li>' in response


def test_format_dir_listing_response_body__dir_with_multiple_spaces():
    response = format_dir_listing_response_body("test_dir/", ["dir 1 2/"])

    assert '<li><a href="dir%201%202/">dir 1 2/</a></li>' in response
