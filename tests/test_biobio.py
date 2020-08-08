from unittest.mock import Mock

from biobionews import biobio


def test_last_news_uses_given_limit(mock_requests_get: Mock) -> None:
    biobio.last_news(limit=15)
    args, _ = mock_requests_get.call_args
    assert "limit=15" in args[0]
