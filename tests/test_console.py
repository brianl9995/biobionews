import pytest
import requests

from biobionews import console
from click.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


def test_main_succeeds(runner, mock_requests_get):
    result = runner.invoke(console.main)
    assert mock_requests_get.called
    assert "10:20 foo\nbar\n\n" in result.output
    assert result.exit_code == 0


def test_main_uses_biobio_cl(runner, mock_requests_get):
    runner.invoke(console.main)
    args, _ = mock_requests_get.call_args
    assert "biobiochile.cl" in args[0]


def test_main_fails_on_request_error(runner, mock_requests_get):
    mock_requests_get.side_effect = Exception("Boom")
    result = runner.invoke(console.main)
    assert result.exit_code == 1


def test_main_prints_message_on_request_error(runner, mock_requests_get):
    mock_requests_get.side_effect = requests.RequestException("Error")
    result = runner.invoke(console.main)
    assert "Error" in str(result.output)


@pytest.fixture
def mock_biobio_last_news(mocker):
    return mocker.patch("biobionews.biobio.last_news")


def test_main_uses_specified_limit(runner, mock_biobio_last_news):
    runner.invoke(console.main, ["--limit=5"])
    mock_biobio_last_news.assert_called_with(limit=5)


@pytest.mark.e2e
def test_main_succeeds_in_production_env(runner):
    result = runner.invoke(console.main)
    assert result.exit_code == 0
