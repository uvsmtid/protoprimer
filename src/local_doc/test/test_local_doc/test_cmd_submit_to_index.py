import io
import json
import urllib.error
from unittest.mock import (
    MagicMock,
    patch,
)

import pytest
from local_doc import cmd_submit_to_index

_base_url = "https://example.com/latest/"

_credentials_default = "gconf/some_key.json"

_sitemap_xml = (
    #
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    "<url><loc>https://example.com/latest/index.html</loc></url>\n"
    "<url><loc>https://example.com/latest/intro.html</loc></url>\n"
    "<url><loc>https://example.com/latest/use_case/UC_01.html</loc></url>\n"
    "</urlset>\n"
)


def _mock_response(
    status: int,
    body: str,
) -> MagicMock:
    mock_response = MagicMock()
    mock_response.status = status
    mock_response.read.return_value = body.encode("utf-8")
    # Support `with urlopen(...) as response`:
    mock_response.__enter__.return_value = mock_response
    return mock_response


def _http_error(
    status: int,
    body: str,
) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        url=_base_url,
        code=status,
        msg="some error",
        hdrs=None,
        fp=io.BytesIO(body.encode("utf-8")),
    )


def _parse_args(arg_list: list):
    return cmd_submit_to_index.init_arg_parser(
        credentials_file_default_rel=_credentials_default,
    ).parse_args(arg_list)


# --- arg parser ---


def test_arg_parser_requires_destination(capsys) -> None:
    # given:
    arg_list: list = []

    # when:
    with pytest.raises(SystemExit) as exc_info:
        _parse_args(arg_list)

    # then:
    assert exc_info.value.code != 0
    assert "destination" in capsys.readouterr().err


def test_arg_parser_google_defaults() -> None:
    # given:
    arg_list = ["google"]

    # when:
    parsed_args = _parse_args(arg_list)

    # then:
    assert parsed_args.destination == "google"
    assert parsed_args.base_url == cmd_submit_to_index._default_base_url
    assert parsed_args.dry_run is False
    assert parsed_args.credentials_file == _credentials_default


def test_arg_parser_indexnow_defaults() -> None:
    # given:
    arg_list = ["indexnow"]

    # when:
    parsed_args = _parse_args(arg_list)

    # then:
    assert parsed_args.destination == "indexnow"
    assert parsed_args.indexnow_key == cmd_submit_to_index._default_indexnow_key


def test_arg_parser_shared_options_go_before_destination() -> None:
    # given:
    arg_list = [
        "--base_url",
        _base_url,
        "--dry_run",
        "indexnow",
        "--indexnow_key",
        "some_key",
    ]

    # when:
    parsed_args = _parse_args(arg_list)

    # then:
    assert parsed_args.base_url == _base_url
    assert parsed_args.dry_run is True
    assert parsed_args.indexnow_key == "some_key"


def test_arg_parser_rejects_indexnow_option_for_google() -> None:
    # given:
    arg_list = [
        "google",
        "--indexnow_key",
        "some_key",
    ]

    # when:
    with pytest.raises(SystemExit) as exc_info:
        _parse_args(arg_list)

    # then:
    assert exc_info.value.code != 0


def test_arg_parser_rejects_google_option_for_indexnow() -> None:
    # given:
    arg_list = [
        "indexnow",
        "--credentials_file",
        "some_file.json",
    ]

    # when:
    with pytest.raises(SystemExit) as exc_info:
        _parse_args(arg_list)

    # then:
    assert exc_info.value.code != 0


# --- URL discovery ---


@patch("urllib.request.urlopen")
def test_discover_urls_skips_index_page(mock_urlopen: MagicMock) -> None:
    # given:
    mock_urlopen.return_value = _mock_response(200, _sitemap_xml)

    # when:
    discovered_urls = cmd_submit_to_index._discover_urls(_base_url)

    # then:
    assert discovered_urls == [
        "https://example.com/latest/intro.html",
        "https://example.com/latest/use_case/UC_01.html",
    ]


# --- credentials ---


def test_resolve_credentials_file_relative_to_ref_root() -> None:
    # given:
    credentials_file = "gconf/some_key.json"

    # when:
    effective_file = cmd_submit_to_index._resolve_credentials_file(
        credentials_file=credentials_file,
        ref_root_abs_path="/fake_repo",
    )

    # then:
    assert effective_file == "/fake_repo/gconf/some_key.json"


@patch.dict("os.environ", {"GOOGLE_APPLICATION_CREDENTIALS": "/abs/from_env.json"})
def test_resolve_credentials_file_env_var_overrides_arg() -> None:
    # when:
    effective_file = cmd_submit_to_index._resolve_credentials_file(
        credentials_file="gconf/some_key.json",
        ref_root_abs_path="/fake_repo",
    )

    # then:
    assert effective_file == "/abs/from_env.json"


# --- IndexNow code path ---


@patch("urllib.request.urlopen")
def test_submit_to_indexnow_sends_one_batch_request(mock_urlopen: MagicMock) -> None:
    # given:
    mock_urlopen.return_value = _mock_response(200, "")
    page_urls = [
        "https://example.com/latest/a.html",
        "https://example.com/latest/b.html",
    ]

    # when:
    failure_count = cmd_submit_to_index._submit_to_indexnow(
        base_url=_base_url,
        indexnow_key="some_key",
        page_urls=page_urls,
    )

    # then:
    assert failure_count == 0
    mock_urlopen.assert_called_once()
    sent_req = mock_urlopen.call_args[0][0]
    assert sent_req.full_url == cmd_submit_to_index._indexnow_endpoint
    assert json.loads(sent_req.data) == {
        "host": "example.com",
        "key": "some_key",
        "keyLocation": "https://example.com/latest/some_key.txt",
        "urlList": page_urls,
    }


@patch("urllib.request.urlopen")
def test_submit_to_indexnow_accepts_202(mock_urlopen: MagicMock) -> None:
    # given:
    mock_urlopen.return_value = _mock_response(202, "")

    # when:
    failure_count = cmd_submit_to_index._submit_to_indexnow(
        base_url=_base_url,
        indexnow_key="some_key",
        page_urls=["https://example.com/latest/a.html"],
    )

    # then:
    assert failure_count == 0


@patch("urllib.request.urlopen")
def test_submit_to_indexnow_reports_http_error(mock_urlopen: MagicMock) -> None:
    # given:
    mock_urlopen.side_effect = _http_error(403, "invalid key")

    # when:
    failure_count = cmd_submit_to_index._submit_to_indexnow(
        base_url=_base_url,
        indexnow_key="some_key",
        page_urls=["https://example.com/latest/a.html"],
    )

    # then:
    assert failure_count == 1


# --- Google code path ---


@patch(f"{cmd_submit_to_index.__name__}._submit_url_to_google")
@patch(f"{cmd_submit_to_index.__name__}._build_credentials")
def test_submit_to_google_sends_request_per_url(
    mock_build_credentials: MagicMock,
    mock_submit_url: MagicMock,
) -> None:
    # given:
    mock_submit_url.return_value = {
        "url": "some_url",
        "status": 200,
        "body": "",
    }
    page_urls = [
        "https://example.com/latest/a.html",
        "https://example.com/latest/b.html",
    ]

    # when:
    failure_count = cmd_submit_to_index._submit_to_google(
        page_urls=page_urls,
        credentials_file="some_file.json",
    )

    # then:
    assert failure_count == 0
    mock_build_credentials.assert_called_once_with("some_file.json")
    assert mock_submit_url.call_count == len(page_urls)


@patch(f"{cmd_submit_to_index.__name__}._submit_url_to_google")
@patch(f"{cmd_submit_to_index.__name__}._build_credentials")
def test_submit_to_google_counts_failures(
    mock_build_credentials: MagicMock,
    mock_submit_url: MagicMock,
) -> None:
    # given:
    mock_submit_url.side_effect = [
        {
            "url": "url_a",
            "status": 200,
            "body": "",
        },
        {
            "url": "url_b",
            "status": 403,
            "body": "denied",
        },
    ]

    # when:
    failure_count = cmd_submit_to_index._submit_to_google(
        page_urls=[
            "url_a",
            "url_b",
        ],
        credentials_file="some_file.json",
    )

    # then:
    assert failure_count == 1


# --- dispatch ---

_derived_data = {
    "state_ref_root_dir_abs_path_inited": "/fake_repo",
    "state_global_conf_dir_abs_path_inited": "/fake_repo/gconf",
}


@patch("sys.argv", ["submit_to_index", "indexnow"])
@patch(f"{cmd_submit_to_index.__name__}._submit_to_google")
@patch(f"{cmd_submit_to_index.__name__}._submit_to_indexnow")
@patch(f"{cmd_submit_to_index.__name__}._discover_urls")
@patch(f"{cmd_submit_to_index.__name__}.configure_script")
def test_custom_main_indexnow_follows_indexnow_path_only(
    mock_configure_script: MagicMock,
    mock_discover_urls: MagicMock,
    mock_submit_to_indexnow: MagicMock,
    mock_submit_to_google: MagicMock,
) -> None:
    # given:
    mock_configure_script.return_value = _derived_data
    mock_discover_urls.return_value = ["some_url"]
    mock_submit_to_indexnow.return_value = 0

    # when:
    cmd_submit_to_index.custom_main()

    # then:
    mock_submit_to_indexnow.assert_called_once()
    mock_submit_to_google.assert_not_called()


@patch("sys.argv", ["submit_to_index", "google"])
@patch(f"{cmd_submit_to_index.__name__}._submit_to_google")
@patch(f"{cmd_submit_to_index.__name__}._submit_to_indexnow")
@patch(f"{cmd_submit_to_index.__name__}._discover_urls")
@patch(f"{cmd_submit_to_index.__name__}.configure_script")
def test_custom_main_google_follows_google_path_only(
    mock_configure_script: MagicMock,
    mock_discover_urls: MagicMock,
    mock_submit_to_indexnow: MagicMock,
    mock_submit_to_google: MagicMock,
) -> None:
    # given:
    mock_configure_script.return_value = _derived_data
    mock_discover_urls.return_value = ["some_url"]
    mock_submit_to_google.return_value = 0

    # when:
    cmd_submit_to_index.custom_main()

    # then:
    mock_submit_to_google.assert_called_once()
    mock_submit_to_indexnow.assert_not_called()


@patch("sys.argv", ["submit_to_index", "--dry_run", "indexnow"])
@patch(f"{cmd_submit_to_index.__name__}._submit_to_google")
@patch(f"{cmd_submit_to_index.__name__}._submit_to_indexnow")
@patch(f"{cmd_submit_to_index.__name__}._discover_urls")
@patch(f"{cmd_submit_to_index.__name__}.configure_script")
def test_custom_main_dry_run_skips_submission(
    mock_configure_script: MagicMock,
    mock_discover_urls: MagicMock,
    mock_submit_to_indexnow: MagicMock,
    mock_submit_to_google: MagicMock,
) -> None:
    # given:
    mock_configure_script.return_value = _derived_data
    mock_discover_urls.return_value = ["some_url"]

    # when:
    cmd_submit_to_index.custom_main()

    # then:
    mock_submit_to_indexnow.assert_not_called()
    mock_submit_to_google.assert_not_called()


@patch("sys.argv", ["submit_to_index", "indexnow"])
@patch(f"{cmd_submit_to_index.__name__}._submit_to_indexnow")
@patch(f"{cmd_submit_to_index.__name__}._discover_urls")
@patch(f"{cmd_submit_to_index.__name__}.configure_script")
def test_custom_main_exits_non_zero_on_failure(
    mock_configure_script: MagicMock,
    mock_discover_urls: MagicMock,
    mock_submit_to_indexnow: MagicMock,
) -> None:
    # given:
    mock_configure_script.return_value = _derived_data
    mock_discover_urls.return_value = ["some_url"]
    mock_submit_to_indexnow.return_value = 1

    # when:
    with pytest.raises(SystemExit) as exc_info:
        cmd_submit_to_index.custom_main()

    # then:
    assert exc_info.value.code == 1
