# Submit published doc URLs to a search engine index (one sub-command per destination):
# - `google`: Google Indexing API
# - `indexnow`: IndexNow (Bing etc.)
# It is expected to be run under activated `venv`.
# It must be run from the repo root:
# ./cmd/submit_to_index -h
# ./cmd/submit_to_index google -h
# ./cmd/submit_to_index indexnow -h
# Shared options go before the sub-command:
# ./cmd/submit_to_index --dry_run google
# `google` requires a Google service account with Indexing API access
# added as Owner in Google Search Console for the property.
# Set GOOGLE_APPLICATION_CREDENTIALS to override --credentials_file.

import argparse
import json
import logging
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

import google.auth.transport.requests
from google.oauth2 import service_account
from metaprimer.script_lib import (
    configure_script,
)
from protoprimer.primer_kernel import _EnvState

logger: logging.Logger = logging.getLogger()

_dest_google = "google"

_dest_indexnow = "indexnow"

_credentials_basename = "google_indexer_key.json"

_default_base_url = "https://protoprimer.readthedocs.io/latest/"

_indexing_api_endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"

_indexing_api_scope = "https://www.googleapis.com/auth/indexing"

_indexnow_endpoint = "https://api.indexnow.org/indexnow"

# IndexNow: 200 = submitted, 202 = accepted (key validation pending):
_indexnow_success_statuses = (
    200,
    202,
)

# Public by design (served as `<key>.txt` next to the docs, see `html_extra_path` in `doc/conf.py`):
_default_indexnow_key = "7944aac309c3411cba99b6f76c03857a"  # gitleaks:allow


def custom_main():

    derived_data = configure_script(script_basename=os.path.basename(sys.argv[0]))

    ref_root_abs_path: str = derived_data[_EnvState.state_ref_root_dir_abs_path_inited.name]
    global_conf_dir_abs_path: str = derived_data[_EnvState.state_global_conf_dir_abs_path_inited.name]

    # Relative to ref root — shown as default in help:
    credentials_file_rel_display = os.path.relpath(
        os.path.join(
            global_conf_dir_abs_path,
            _credentials_basename,
        ),
        ref_root_abs_path,
    )

    parsed_args = init_arg_parser(
        credentials_file_default_rel=credentials_file_rel_display,
    ).parse_args()

    logger.info(f"base_url: {parsed_args.base_url}")

    discovered_urls = _discover_urls(parsed_args.base_url)

    for page_url in discovered_urls:
        logger.info(f"url: {page_url}")

    if parsed_args.dry_run:
        logger.info(f"dry_run: skipping submission of {len(discovered_urls)} URLs to {parsed_args.destination}")
        return

    if parsed_args.destination == _dest_google:
        failure_count = _submit_to_google(
            page_urls=discovered_urls,
            credentials_file=_resolve_credentials_file(
                credentials_file=parsed_args.credentials_file,
                ref_root_abs_path=ref_root_abs_path,
            ),
        )
    elif parsed_args.destination == _dest_indexnow:
        failure_count = _submit_to_indexnow(
            base_url=parsed_args.base_url,
            indexnow_key=parsed_args.indexnow_key,
            page_urls=discovered_urls,
        )
    else:
        raise AssertionError(f"unsupported destination: {parsed_args.destination}")

    if failure_count > 0:
        sys.exit(1)


def init_arg_parser(
    credentials_file_default_rel: str,
):

    arg_parser = argparse.ArgumentParser(
        description="Submit published doc URLs to a search engine index.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Shared options (must be specified before the sub-command):
    arg_parser.add_argument(
        "--base_url",
        type=str,
        default=_default_base_url,
        help="Base URL of the published documentation (must end with /).",
    )
    arg_parser.add_argument(
        "-d",
        "--dry_run",
        action="store_true",
        default=False,
        help="Discover and print URLs but skip API submission.",
    )

    sub_parsers = arg_parser.add_subparsers(
        dest="destination",
        metavar="destination",
        required=True,
        help="Where to submit URLs.",
    )

    google_parser = sub_parsers.add_parser(
        _dest_google,
        help="Submit each URL to Google Indexing API.",
        description="Submit each URL to Google Indexing API.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    google_parser.add_argument(
        "--credentials_file",
        type=str,
        default=credentials_file_default_rel,
        help=("Path to the Google service account JSON key file." " Override-able by GOOGLE_APPLICATION_CREDENTIALS env var."),
    )

    indexnow_parser = sub_parsers.add_parser(
        _dest_indexnow,
        help="Submit all URLs in one batch to IndexNow (Bing etc.).",
        description="Submit all URLs in one batch to IndexNow (Bing etc.).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    indexnow_parser.add_argument(
        "--indexnow_key",
        type=str,
        default=_default_indexnow_key,
        help="IndexNow key. It must be served as `<INDEXNOW_KEY>.txt` under --base_url and contain only the key.",
    )

    return arg_parser


def _discover_urls(base_url: str) -> list:

    sitemap_url = base_url + "sitemap.xml"
    logger.info(f"fetching sitemap: {sitemap_url}")

    sitemap_req = urllib.request.Request(
        sitemap_url,
        # Cloudflare blocks the default `Python-urllib` `User-Agent` with 403:
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(sitemap_req) as response:
        sitemap_bytes = response.read()

    root_elem = ET.fromstring(sitemap_bytes)

    # Sitemap XML uses a namespace:
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    all_urls = [loc_elem.text.strip() for loc_elem in root_elem.findall("sm:url/sm:loc", ns) if loc_elem.text]

    # Skip the redirect index page (has noindex meta):
    skip_suffixes = (
        "/index.html",
        "/index",
    )
    discovered_urls = [url for url in all_urls if not any(url.endswith(suffix) for suffix in skip_suffixes)]

    logger.info(f"discovered {len(discovered_urls)} URLs from sitemap")
    return discovered_urls


def _resolve_credentials_file(
    credentials_file: str,
    ref_root_abs_path: str,
) -> str:

    # GOOGLE_APPLICATION_CREDENTIALS overrides --credentials_file:
    effective_credentials_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or credentials_file
    # Resolve relative path against ref root:
    if not os.path.isabs(effective_credentials_file):
        effective_credentials_file = os.path.join(
            ref_root_abs_path,
            effective_credentials_file,
        )
    return effective_credentials_file


def _build_credentials(credentials_file: str):

    logger.info(f"credentials_file: {credentials_file}")

    credentials = service_account.Credentials.from_service_account_file(
        credentials_file,
        scopes=[_indexing_api_scope],
    )
    return credentials


def _submit_url_to_google(
    credentials,
    page_url: str,
) -> dict:

    auth_request = google.auth.transport.requests.Request()
    credentials.refresh(auth_request)

    request_body = json.dumps(
        {
            "url": page_url,
            "type": "URL_UPDATED",
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        url=_indexing_api_endpoint,
        data=request_body,
        headers={
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode("utf-8")
        return {
            "url": page_url,
            "status": response.status,
            "body": response_body,
        }
    except urllib.error.HTTPError as http_error:
        error_body = http_error.read().decode("utf-8")
        return {
            "url": page_url,
            "status": http_error.code,
            "body": error_body,
        }


# Google: one API call per URL. Returns the number of failures:
def _submit_to_google(
    page_urls: list,
    credentials_file: str,
) -> int:

    credentials = _build_credentials(credentials_file)

    success_count = 0
    failure_count = 0

    for page_url in page_urls:
        result = _submit_url_to_google(
            credentials=credentials,
            page_url=page_url,
        )
        if result["status"] == 200:
            logger.info(f"submitted: {result['url']}")
            success_count += 1
        else:
            logger.error(f"failed [{result['status']}]: {result['url']} — {result['body']}")
            failure_count += 1

    logger.info(f"done: {success_count} submitted, {failure_count} failed")

    return failure_count


# IndexNow: one API call for all URLs. Returns the number of failures (0 or 1):
def _submit_to_indexnow(
    base_url: str,
    indexnow_key: str,
    page_urls: list,
) -> int:

    request_body = json.dumps(
        {
            "host": urllib.parse.urlparse(base_url).netloc,
            "key": indexnow_key,
            "keyLocation": f"{base_url}{indexnow_key}.txt",
            "urlList": page_urls,
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        url=_indexnow_endpoint,
        data=request_body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as response:
            response_status = response.status
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as http_error:
        response_status = http_error.code
        response_body = http_error.read().decode("utf-8")

    if response_status in _indexnow_success_statuses:
        logger.info(f"indexnow: submitted {len(page_urls)} URLs [{response_status}]")
        return 0
    else:
        logger.error(f"indexnow: failed [{response_status}] — {response_body}")
        return 1
