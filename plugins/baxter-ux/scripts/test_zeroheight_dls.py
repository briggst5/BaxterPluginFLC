#!/usr/bin/env python3
"""Unit tests for Zero Height URL parsing and page snapshot formatting."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from zeroheight_dls import (
    apply_snapshots,
    canonical_page_url,
    colors_from_text,
    is_styleguide_page,
    page_markdown,
    parse_page_url,
    slug_from_tail,
)


class ParseUrlTests(unittest.TestCase):
    def test_parse_start_page(self) -> None:
        parsed = parse_page_url(
            "https://zeroheight.com/67cfae98e/v/latest/p/69b547-nexus-design-system?foo=1"
        )
        assert parsed is not None
        self.assertEqual(parsed.styleguide_id, "67cfae98e")
        self.assertEqual(parsed.page_id, "69b547")
        self.assertEqual(parsed.slug, "nexus-design-system")
        self.assertEqual(
            parsed.canonical_url,
            "https://zeroheight.com/67cfae98e/v/latest/p/69b547-nexus-design-system",
        )

    def test_double_hyphen_slug(self) -> None:
        parsed = parse_page_url(
            "https://zeroheight.com/67cfae98e/v/latest/p/34aae0-heuristics--clinical-ui"
        )
        assert parsed is not None
        self.assertEqual(parsed.slug, "heuristics-clinical-ui")

    def test_rejects_other_hosts(self) -> None:
        self.assertIsNone(parse_page_url("https://example.com/67cfae98e/v/latest/p/69b547-x"))

    def test_styleguide_boundary(self) -> None:
        url = "https://zeroheight.com/67cfae98e/v/latest/p/343940-standard-button"
        self.assertTrue(is_styleguide_page(url, "67cfae98e"))
        self.assertFalse(is_styleguide_page(url, "deadbeef"))


class ColorAndMarkdownTests(unittest.TestCase):
    def test_colors_dedupe_and_skip_chrome(self) -> None:
        text = "Primary #2265c9 then #2265C9 and rgb(21, 72, 152) plus #ffffff and #3b82f6"
        colors = colors_from_text(text)
        self.assertIn("#2265c9", colors)
        self.assertIn("rgb(21,72,152)", colors)
        self.assertEqual(len([c for c in colors if c.lower() == "#2265c9"]), 1)
        self.assertNotIn("#3b82f6", [c.lower() for c in colors])

    def test_page_markdown_shape(self) -> None:
        md = page_markdown(
            title="Standard Button",
            url="https://zeroheight.com/67cfae98e/v/latest/p/343940-standard-button",
            colors=["#2265c9"],
            body="### Anatomy\nLabel",
        )
        self.assertTrue(md.startswith("# Standard Button\n"))
        self.assertIn("Source: https://zeroheight.com/", md)
        self.assertIn("- `#2265c9`", md)
        self.assertIn("## Sections", md)

    def test_slug_from_tail(self) -> None:
        self.assertEqual(slug_from_tail("alarm-notification-banner-smmd-screens"), "alarm-notification-banner-smmd-screens")
        self.assertEqual(slug_from_tail("heuristics--clinical-ui"), "heuristics-clinical-ui")


class ApplyTests(unittest.TestCase):
    def test_apply_writes_pages_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = Path(tmp)
            crawl_dir = plugin / "design-system" / ".crawl"
            crawl_dir.mkdir(parents=True)
            record = {
                "slug": "standard-button",
                "url": "https://zeroheight.com/67cfae98e/v/latest/p/343940-standard-button",
                "title": "Standard Button",
                "colors": ["#2265c9"],
                "text": "Button label",
                "headings": ["Standard Button"],
            }
            (crawl_dir / "manifest.json").write_text(
                json.dumps({"pages": [record], "start_url": record["url"]}),
                encoding="utf-8",
            )
            report = apply_snapshots(plugin_root=plugin, prune=False)
            page = plugin / "design-system" / "pages" / "standard-button.md"
            nav = json.loads((plugin / "design-system" / "nav-manifest.json").read_text(encoding="utf-8"))
            self.assertTrue(page.exists())
            self.assertEqual(nav[0]["slug"], "standard-button")
            self.assertEqual(report["written"], ["standard-button"])
            self.assertEqual(canonical_page_url(record["url"]), record["url"])


if __name__ == "__main__":
    unittest.main()
