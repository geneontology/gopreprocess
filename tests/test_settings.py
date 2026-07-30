"""Test the settings module."""

from unittest.mock import patch

import yaml

from src.utils.settings import CONFIG, get_url, resolve_url


def test_get_url():
    """Test that get_url returns the pinned fallback URL from the config."""
    actual_url = get_url("MGI_GPI")
    assert actual_url == "https://www.informatics.jax.org/downloads/reports/mgi.gpi.gz"


def test_no_snapshot_inputs():
    """
    No input may be pinned to snapshot.geneontology.org.

    snapshot is a rolling endpoint that this pipeline ultimately feeds, so reading
    an input from it is both circular and silently stale: the MGI GPI was read
    from there until its copy was found to be generated 2026-05-20 against MGI's
    own 2026-07-27.

    Deliberately narrow. Dated release.geneontology.org URLs are immutable and
    therefore reproducible, so they are fine; current.geneontology.org is rolling
    and arguably circular too, but nothing here reads it and that call has not
    been made.
    """
    with open(CONFIG, "r") as f:
        config = yaml.safe_load(f)

    for key, block in config.items():
        assert "snapshot.geneontology.org" not in block["url"], f"{key} reads from snapshot.geneontology.org"


def test_resolve_url_falls_back_to_pin_when_resolution_fails():
    """If the authoritative source cannot be reached, fall back to the pinned URL."""
    with patch("src.utils.settings._resolve_from_go_site", return_value=None), patch("src.utils.settings._resolve_from_manifest", return_value=None):
        assert resolve_url("MGI_GPI") == get_url("MGI_GPI")


def test_resolve_url_prefers_resolved_over_pin():
    """A successfully resolved URL wins over the pinned fallback."""
    with patch("src.utils.settings._resolve_from_go_site", return_value="https://example.org/resolved.gpi.gz"):
        assert resolve_url("MGI_GPI") == "https://example.org/resolved.gpi.gz"
