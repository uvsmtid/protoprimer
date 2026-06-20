# Submit published doc URLs to Google Indexing API.
# It is expected to be run under activated `venv`.
# It must be run from the repo root:
# ./cmd/submit_to_index -h
# Requires a Google service account with Indexing API access
# added as Owner in Google Search Console for the property.
# Set GOOGLE_APPLICATION_CREDENTIALS to the service account JSON key path.

import argparse
import logging
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET

logger: logging.Logger = logging.getLogger()

_default_base_url = "https://protoprimer.readthedocs.io/latest/"

_indexing_api_endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"

_indexing_api_scope = "https://www.googleapis.com/auth/indexing"


def custom_main():

    parsed_args = init_arg_parser().parse_args()

    _submit_to_index(
        base_url=parsed_args.base_url,
        credentials_file=parsed_args.credentials_file,
        dry_run=parsed_args.dry_run,
    )


def init_arg_parser():

    arg_parser = argparse.ArgumentParser(
        description="Submit published doc URLs to Google Indexing API.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    arg_parser.add_argument(
        "--base_url",
        type=str,
        default=_default_base_url,
        help="Base URL of the published documentation (must end with /).",
    )
    arg_parser.add_argument(
        "--credentials_file",
        type=str,
        default=None,
        help=("Path to the Google service account JSON key file." " Falls back to GOOGLE_APPLICATION_CREDENTIALS env var."),
    )
    arg_parser.add_argument(
        "--dry_run",
        action="store_true",
        default=False,
        help="Discover and print URLs but skip API submission.",
    )
    return arg_parser


def _discover_urls(base_url: str) -> list:

    sitemap_url = base_url + "sitemap.xml"
    logger.info(f"fetching sitemap: {sitemap_url}")

    with urllib.request.urlopen(sitemap_url) as response:
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


def _build_credentials(credentials_file):

    credentials_path = credentials_file or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        raise RuntimeError("no credentials: provide --credentials_file or set GOOGLE_APPLICATION_CREDENTIALS")

    logger.info(f"credentials_path: {credentials_path}")

    from google.oauth2 import service_account

    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=[_indexing_api_scope],
    )
    return credentials


def _submit_url(
    credentials,
    page_url: str,
) -> dict:

    import json

    import google.auth.transport.requests

    auth_request = google.auth.transport.requests.Request()
    credentials.refresh(auth_request)

    request_body = json.dumps(
        {
            "url": page_url,
            "type": "URL_UPDATED",
        }
    ).encode("utf-8")

    import urllib.error

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


def _submit_to_index(
    base_url: str,
    credentials_file,
    dry_run: bool,
):
    logger.info(f"base_url: {base_url}")

    discovered_urls = _discover_urls(base_url)

    for page_url in discovered_urls:
        logger.info(f"url: {page_url}")

    if dry_run:
        logger.info(f"dry_run: skipping submission of {len(discovered_urls)} URLs")
        return

    credentials = _build_credentials(credentials_file)

    success_count = 0
    failure_count = 0

    for page_url in discovered_urls:
        result = _submit_url(
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

    if failure_count > 0:
        sys.exit(1)
