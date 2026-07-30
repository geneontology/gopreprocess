"""Module that processes the settings for the application."""

import json
import logging
import urllib.error
import urllib.request
from os import path

import yaml

CONFIG = path.join(path.dirname(path.abspath(__file__)), "../config/download_config.yaml")
logger = logging.getLogger(__name__)

# The Alliance rejects requests without one.
USER_AGENT = "gopreprocess (https://github.com/geneontology/gopreprocess)"


iso_eco_code = "ECO:0000266"

taxon_to_provider = {"NCBITaxon:10116": "RGD", "NCBITaxon:10090": "MGI", "NCBITaxon:9606": "HUMAN"}


def get_url(key: str) -> str:
    """
    Retrieves the URL corresponding to the given key from the configuration file.

    :param key: The key to retrieve the URL for.
    :type key: str
    :return: The URL corresponding to the given key.
    :rtype: str
    """
    with open(CONFIG, "r") as f:
        config = yaml.safe_load(f)
    return config[key]["url"]


def get_config(key: str) -> dict:
    """
    Retrieves the whole configuration block for the given key.

    :param key: The key to retrieve the configuration for.
    :type key: str
    :return: The configuration block.
    :rtype: dict
    """
    with open(CONFIG, "r") as f:
        config = yaml.safe_load(f)
    return config[key]


def _open_url(url: str, timeout: int = 60, method: str = None):
    """
    Opens an http(s) URL.

    URLs here come from remote manifests and remote metadata, so the scheme is
    checked rather than assumed: without this, a manifest could hand us a
    ``file:`` URL and we would read a local path.

    :param url: The URL to open.
    :type url: str
    :param timeout: Request timeout in seconds.
    :type timeout: int
    :param method: Optional HTTP method, e.g. "HEAD".
    :type method: str
    :raises ValueError: if the URL is not http or https.
    :return: The open response, as a context manager.
    """
    if not str(url).lower().startswith(("http://", "https://")):
        raise ValueError(f"Refusing to open non-http(s) URL: {url}")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method=method)  # noqa: S310
    return urllib.request.urlopen(request, timeout=timeout)  # noqa: S310


def _url_serves(url: str, timeout: int = 60) -> bool:
    """Report whether a URL currently answers a HEAD request with 200."""
    try:
        with _open_url(url, timeout=timeout, method="HEAD") as response:
            return response.status == 200
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as e:
        logger.debug("HEAD %s failed: %s", url, e)
        return False


def _resolve_from_go_site(config: dict, timeout: int = 60):
    """
    Resolves a URL from go-site dataset metadata, which owns what is authoritative.

    go-site is a canonical GO git repository, so reading it at run time is a
    legitimate input source; reading a GO *serving site* (snapshot, current) is
    not, since this pipeline ultimately feeds those.

    :param config: The config block, holding ``go_site_metadata`` and ``dataset_id``.
    :type config: dict
    :param timeout: Request timeout in seconds.
    :type timeout: int
    :return: The resolved URL, or None.
    """
    metadata_url = config.get("go_site_metadata")
    dataset_id = config.get("dataset_id")
    if not (metadata_url and dataset_id):
        return None

    try:
        with _open_url(metadata_url, timeout=timeout) as response:
            metadata = yaml.safe_load(response.read())
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, yaml.YAMLError) as e:
        logger.warning("Could not read go-site metadata %s: %s", metadata_url, e)
        return None

    for dataset in metadata.get("datasets") or []:
        if dataset.get("id") == dataset_id and dataset.get("source"):
            return dataset["source"]

    logger.warning("go-site metadata %s has no source for dataset id %s", metadata_url, dataset_id)
    return None


def _resolve_from_manifest(config: dict, timeout: int = 60):
    """
    Resolves a URL from the provider's own downloads manifest.

    Used for the Alliance orthology file, whose published "stable" URL has moved
    between releases and, at time of writing, 404s on the production instance
    while the release-versioned URL works. Resolving at run time means a URL move
    or a release bump is picked up without a code change; a *format* change is
    still a code change, and is caught by OrthoProcessor's schema check.

    :param config: The config block, holding ``manifests``, ``data_type``, ``file_extension``.
    :type config: dict
    :param timeout: Per-request timeout in seconds.
    :type timeout: int
    :return: A URL that answered 200, or None.
    """
    manifests = config.get("manifests") or []
    data_type = config.get("data_type")
    file_extension = config.get("file_extension")
    if not (manifests and data_type and file_extension):
        return None

    for manifest_url in manifests:
        try:
            with _open_url(manifest_url, timeout=timeout) as response:
                manifest = json.load(response)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as e:
            logger.warning("Could not read Alliance manifest %s: %s", manifest_url, e)
            continue

        entries = manifest if isinstance(manifest, list) else (manifest.get("results") or manifest.get("data") or [])
        for entry in entries:
            if entry.get("dataType") != data_type or entry.get("fileExtension") != file_extension:
                continue
            # stableURL is the one the Alliance advertises; s3Url is the
            # release-versioned path it currently redirects to in practice.
            for candidate_key in ("stableURL", "s3Url"):
                candidate = entry.get(candidate_key)
                if candidate and _url_serves(candidate, timeout=timeout):
                    logger.info("Resolved via %s %s: %s", manifest_url, candidate_key, candidate)
                    return candidate

    return None


def resolve_url(key: str, timeout: int = 60) -> str:
    """
    Resolves the download URL for a config key, preferring an authoritative source.

    Two strategies, chosen by what the config block declares:

    - ``go_site_metadata`` + ``dataset_id``: ask go-site which upstream is
      authoritative for that dataset.
    - ``manifests`` + ``data_type`` + ``file_extension``: ask the provider's own
      downloads manifest.

    Either way, the pinned ``url`` is the fallback if resolution fails, so a
    transient outage degrades to the last known-good URL rather than an error.
    A pinned URL that has gone stale in *format* is still caught downstream by
    the consuming processor's schema check.

    :param key: The config key.
    :type key: str
    :param timeout: Per-request timeout in seconds.
    :type timeout: int
    :return: The resolved URL, or the pinned fallback.
    :rtype: str
    """
    config = get_config(key)
    fallback = config["url"]

    # Most keys pin a canonical upstream directly and declare no resolution
    # strategy; that is normal and not worth warning about.
    if not (config.get("go_site_metadata") or config.get("manifests")):
        return fallback

    resolved = _resolve_from_go_site(config, timeout=timeout) or _resolve_from_manifest(config, timeout=timeout)
    if resolved:
        logger.info("Resolved %s to %s", key, resolved)
        return resolved

    logger.warning("Could not resolve %s; falling back to pinned %s", key, fallback)
    return fallback
