import hashlib
import re
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
MANIFEST = ROOT / "moe.sable.client.yml"


def test_manifest_tracks_sable_next_release_for_both_architectures():
    manifest = yaml.safe_load(MANIFEST.read_text())
    module = next(module for module in manifest["modules"] if module["name"] == "sable-next")
    archives = [source for source in module["sources"] if source["type"] == "archive"]

    assert {tuple(source["only-arches"]) for source in archives} == {("x86_64",), ("aarch64",)}
    for source in archives:
        arch = source["only-arches"][0]
        assert f"sable-next/releases/" in source["url"]
        assert source["url"].endswith(f"linux-{arch}.tar.gz")
        assert re.fullmatch(r"[0-9a-f]{64}", source["sha256"])
        checker = source["x-checker-data"]
        assert checker["url"].endswith("/SableClient/sable-next/releases/latest")
        assert f"\"sable-\" + $version + \"-linux-{arch}.tar.gz\"" in checker["url-query"]


def test_pinned_release_archive_hashes_match_published_assets():
    manifest = yaml.safe_load(MANIFEST.read_text())
    module = next(module for module in manifest["modules"] if module["name"] == "sable-next")
    archives = [source for source in module["sources"] if source["type"] == "archive"]
    for source in archives:
        with urllib.request.urlopen(source["url"]) as response:
            digest = hashlib.sha256(response.read()).hexdigest()
        assert digest == source["sha256"]
