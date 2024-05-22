from phenoplier.config import settings
from phenoplier.cache import cache_dir_exists, get_cache_dir
from pathlib import Path


def _cleanup_cache_dir():
    if cache_dir_exists():
        Path(settings.CACHE_DIR).rmdir()


def test_cache_dir_exists():
    _cleanup_cache_dir()
    assert not cache_dir_exists()


def test_get_cache_dir():
    _cleanup_cache_dir()
    assert get_cache_dir() == settings.CACHE_DIR
    assert cache_dir_exists()
    _cleanup_cache_dir()
