from biobionews import biobio


def test_last_news_uses_given_limit(mock_requests_get):
    biobio.last_news(limit=15)
    args, _ = mock_requests_get.call_args
    assert "limit=15" in args[0]
