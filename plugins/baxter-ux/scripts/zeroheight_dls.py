#!/usr/bin/env python3
"""Crawl the Nexus Zero Height styleguide and snapshot pages into baxter-ux.

SSO: run `login` in a headed browser (or attach to Chrome via --cdp-url), then `crawl`
and `apply`. Cursor can then update tokens.md, components.md, web-mapping.md, and
nexus-dls-*.mdc from the snapshots — see skills/sync-dls/SKILL.md.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urljoin, urlparse, urlunparse

DEFAULT_START = (
    "https://zeroheight.com/67cfae98e/v/latest/p/69b547-nexus-design-system"
)
PAGE_URL_RE = re.compile(
    r"^https?://(?:www\.)?zeroheight\.com/([0-9a-f]+)/v/latest/p/([0-9a-f]+)-([^/?#]+)",
    re.IGNORECASE,
)
HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b")
RGB_RE = re.compile(r"rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)", re.I)
# Frequent Zero Height chrome / browser UI — keep DLS-looking values.
CHROME_COLOR_BLOCKLIST = frozenset(
    {
        "#0000ff",
        "#ffff00",
        "#ff0000",
        "#00ff00",
        "#1a1a1a",
        "#333333",
        "#cccccc",
        "#dddddd",
        "#eeeeee",
        "#fafafa",
        "#2563eb",
        "#3b82f6",
    }
)
PRESERVE_PAGE_NAMES = frozenset()  # pages/*.md not from ZH could be listed here
PRESERVE_DESIGN_FILES = frozenset(
    {
        "tokens.md",
        "components.md",
        "web-mapping.md",
        "gap-analysis.md",
        "nav-manifest.json",
    }
)

EXTRACT_JS = """() => {
  const origin = location.origin;
  const hrefs = [...document.querySelectorAll('a[href]')].map((a) => a.href);
  const sidebar = document.querySelector('nav, [class*="Sidebar"], [class*="sidebar"], [class*="Nav"]');
  if (sidebar) {
    sidebar.querySelectorAll('[aria-expanded="false"]').forEach((el) => {
      try { el.click(); } catch (e) {}
    });
  }
  const clone = document.body ? document.body.cloneNode(true) : document.documentElement.cloneNode(true);
  clone.querySelectorAll(
    'nav, header, footer, script, style, iframe, [class*="Sidebar"], [class*="sidebar"], [class*="TopBar"]'
  ).forEach((n) => n.remove());
  const title =
    document.querySelector('h1')?.innerText?.trim() ||
    document.title.replace(/\\s*\\|.*$/, '').trim() ||
    '';
  const headings = [...clone.querySelectorAll('h1, h2, h3, h4')].map((h) => h.innerText.trim()).filter(Boolean);
  return {
    title,
    text: (clone.innerText || '').trim(),
    headings,
    hrefs,
    url: location.href,
  };
}"""


@dataclass(frozen=True)
class ParsedPage:
    styleguide_id: str
    page_id: str
    slug: str
    canonical_url: str


def plugin_root_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def auth_dir() -> Path:
    override = os.environ.get("BAXTER_UX_AUTH_DIR")
    if override:
        return Path(override)
    return Path.home() / ".cache" / "baxter-ux"


def storage_state_path() -> Path:
    return auth_dir() / "zeroheight-storage.json"


def user_data_dir() -> Path:
    return auth_dir() / "zeroheight-profile"


def crawl_dir(plugin_root: Path) -> Path:
    return plugin_root / "design-system" / ".crawl"


def slug_from_tail(tail: str) -> str:
    return re.sub(r"-{2,}", "-", tail).strip("-").lower()


def canonical_page_url(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))


def parse_page_url(url: str) -> ParsedPage | None:
    match = PAGE_URL_RE.match(canonical_page_url(url.strip()))
    if not match:
        return None
    styleguide_id, page_id, tail = match.group(1), match.group(2), match.group(3)
    return ParsedPage(
        styleguide_id=styleguide_id.lower(),
        page_id=page_id.lower(),
        slug=slug_from_tail(tail),
        canonical_url=canonical_page_url(url),
    )


def is_styleguide_page(url: str, styleguide_id: str) -> bool:
    parsed = parse_page_url(url)
    return parsed is not None and parsed.styleguide_id == styleguide_id.lower()


def normalize_hex(value: str) -> str:
    raw = value if value.startswith("#") else f"#{value}"
    body = raw[1:]
    if len(body) == 3:
        body = "".join(ch * 2 for ch in body)
    if len(body) == 8 and body.endswith("ff"):
        body = body[:6]
    return f"#{body}"


def colors_from_text(text: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()

    def add(token: str) -> None:
        key = token.lower()
        if key in seen or key in CHROME_COLOR_BLOCKLIST:
            return
        seen.add(key)
        found.append(token)

    for match in HEX_RE.findall(text):
        add(normalize_hex(match))
    for match in RGB_RE.finditer(text):
        r, g, b = (int(match.group(i)) for i in range(1, 4))
        add(f"rgb({r},{g},{b})")
    return found


def page_markdown(*, title: str, url: str, colors: list[str], body: str) -> str:
    color_lines = "\n".join(f"- `{c}`" for c in colors) or "- (none extracted)"
    body = body.strip() or "(no text extracted)"
    return (
        f"# {title}\n\n"
        f"Source: {url}\n\n"
        f"## Colors found\n\n"
        f"{color_lines}\n\n"
        f"## Sections\n\n"
        f"{body}\n"
    )


def looks_logged_out(url: str, text: str) -> bool:
    lowered_url = url.lower()
    if any(part in lowered_url for part in ("/login", "/signin", "/sso", "auth0", "okta", "login.microsoftonline")):
        if parse_page_url(url) is None:
            return True
    snippet = text[:2000].lower()
    signs = ("sign in to continue", "log in to continue", "use sso", "single sign-on")
    return any(s in snippet for s in signs) and len(text) < 4000


def _require_playwright():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit(
            "Playwright is not installed. From plugins/baxter-ux run:\n"
            "  python3 -m pip install -r scripts/requirements-crawl.txt\n"
            "  python3 -m playwright install chromium"
        ) from exc
    return sync_playwright


def _new_page(playwright, *, headed: bool, cdp_url: str | None):
    if cdp_url:
        browser = playwright.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()
        return browser, context, page, "cdp"
    user_data_dir().mkdir(parents=True, exist_ok=True)
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=str(user_data_dir()),
        headless=not headed,
        viewport={"width": 1440, "height": 900},
        accept_downloads=False,
    )
    page = context.pages[0] if context.pages else context.new_page()
    return None, context, page, "persistent"


def cmd_login(args: argparse.Namespace) -> int:
    if not args.cdp_url and not os.environ.get("DISPLAY") and not args.headed_ok:
        print(
            "No DISPLAY found (typical on WSL without WSLg).\n"
            "Options:\n"
            "  1. Enable WSLg / a desktop and re-run login\n"
            "  2. Start Chrome with remote debugging and attach:\n"
            "       chrome --remote-debugging-port=9222\n"
            "       python3 scripts/zeroheight_dls.py login --cdp-url http://127.0.0.1:9222\n",
            file=sys.stderr,
        )
        return 1
    start = args.start
    timeout_s = args.login_timeout
    storage = storage_state_path()
    storage.parent.mkdir(parents=True, exist_ok=True)
    sync_playwright = _require_playwright()
    print(f"Opening {start}")
    print("Complete SSO in the browser window. Waiting until a styleguide page loads...")
    with sync_playwright() as playwright:
        browser, context, page, mode = _new_page(
            playwright, headed=True, cdp_url=args.cdp_url
        )
        page.goto(start, wait_until="domcontentloaded", timeout=120_000)
        deadline = time.time() + timeout_s
        logged_in = False
        while time.time() < deadline:
            current = page.url
            parsed = parse_page_url(current)
            text = ""
            try:
                text = page.inner_text("body")
            except Exception:
                pass
            if parsed and not looks_logged_out(current, text):
                logged_in = True
                break
            time.sleep(1)
        if mode != "cdp":
            context.storage_state(path=str(storage))
        if browser:
            pass  # leave CDP Chrome running
        else:
            context.close()
    if not logged_in:
        print("Timed out waiting for SSO. Re-run login after signing in.", file=sys.stderr)
        return 1
    print(f"Session saved to {storage}" if mode != "cdp" else "Using existing Chrome session (CDP)")
    return 0


def _collect_links(hrefs: Iterable[str], *, base: str, styleguide_id: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for href in hrefs:
        if not href:
            continue
        absolute = urljoin(base, href)
        parsed = parse_page_url(absolute)
        if parsed is None or parsed.styleguide_id != styleguide_id:
            continue
        if parsed.canonical_url in seen:
            continue
        seen.add(parsed.canonical_url)
        found.append(parsed.canonical_url)
    return found


def cmd_crawl(args: argparse.Namespace) -> int:
    plugin_root = Path(args.plugin_root)
    start_parsed = parse_page_url(args.start)
    if start_parsed is None:
        print(f"Not a Zero Height page URL: {args.start}", file=sys.stderr)
        return 1
    styleguide_id = start_parsed.styleguide_id
    out = crawl_dir(plugin_root)
    pages_dir = out / "raw"
    pages_dir.mkdir(parents=True, exist_ok=True)
    storage = storage_state_path()
    if not args.cdp_url and not storage.exists() and not user_data_dir().exists():
        print("No saved session. Run: python3 scripts/zeroheight_dls.py login", file=sys.stderr)
        return 1

    sync_playwright = _require_playwright()
    queue: list[str] = [start_parsed.canonical_url]
    queued = set(queue)
    crawled: dict[str, dict[str, Any]] = {}
    if args.resume:
        existing_manifest = out / "manifest.json"
        if existing_manifest.exists():
            data = json.loads(existing_manifest.read_text(encoding="utf-8"))
            for page in data.get("pages", []):
                crawled[page["url"]] = page

    print(f"Crawling styleguide {styleguide_id} from {start_parsed.canonical_url}")
    with sync_playwright() as playwright:
        browser, context, page, _mode = _new_page(
            playwright,
            headed=not args.headless,
            cdp_url=args.cdp_url,
        )
        try:
            while queue:
                if args.limit and len(crawled) >= args.limit:
                    break
                url = queue.pop(0)
                if url in crawled and args.resume:
                    for link in crawled[url].get("links", []):
                        if link not in queued:
                            queued.add(link)
                            queue.append(link)
                    continue
                print(f"  [{len(crawled) + 1}] {url}")
                page.goto(url, wait_until="domcontentloaded", timeout=120_000)
                page.wait_for_timeout(args.settle_ms)
                extracted = page.evaluate(EXTRACT_JS)
                text = extracted.get("text") or ""
                if looks_logged_out(page.url, text):
                    print("Session expired or SSO required. Re-run login.", file=sys.stderr)
                    return 1
                parsed = parse_page_url(page.url) or parse_page_url(url)
                assert parsed is not None
                links = _collect_links(
                    extracted.get("hrefs") or [],
                    base=page.url,
                    styleguide_id=styleguide_id,
                )
                record = {
                    "slug": parsed.slug,
                    "page_id": parsed.page_id,
                    "url": parsed.canonical_url,
                    "title": (extracted.get("title") or parsed.slug).strip(),
                    "colors": colors_from_text(text),
                    "headings": extracted.get("headings") or [],
                    "text": text,
                    "links": links,
                    "crawled_at": datetime.now(timezone.utc).isoformat(),
                }
                crawled[parsed.canonical_url] = record
                (pages_dir / f"{parsed.slug}.json").write_text(
                    json.dumps(record, indent=2), encoding="utf-8"
                )
                for link in links:
                    if link not in queued:
                        queued.add(link)
                        queue.append(link)
                time.sleep(args.delay)
        finally:
            if browser is None:
                context.close()

    pages = list(crawled.values())
    pages.sort(key=lambda item: item["slug"])
    manifest = {
        "start_url": start_parsed.canonical_url,
        "styleguide_id": styleguide_id,
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "page_count": len(pages),
        "pages": pages,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (out / "AGENT_APPLY.md").write_text(_agent_apply_prompt(plugin_root, manifest), encoding="utf-8")
    print(f"Wrote {len(pages)} pages to {out}")
    print("Next: python3 scripts/zeroheight_dls.py apply")
    print("Then ask Cursor to follow skills/sync-dls (AI apply step).")
    return 0


def apply_snapshots(*, plugin_root: Path, prune: bool) -> dict[str, Any]:
    manifest_path = crawl_dir(plugin_root) / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing crawl manifest at {manifest_path}. Run crawl first.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    pages_dir = plugin_root / "design-system" / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    nav: list[dict[str, Any]] = []
    written: list[str] = []
    for record in manifest.get("pages", []):
        slug = record["slug"]
        md = page_markdown(
            title=record.get("title") or slug,
            url=record["url"],
            colors=record.get("colors") or [],
            body=record.get("text") or "",
        )
        (pages_dir / f"{slug}.md").write_text(md, encoding="utf-8")
        nav.append(
            {
                "slug": slug,
                "url": record["url"],
                "title": record.get("title") or slug,
                "colors": record.get("colors") or [],
            }
        )
        written.append(slug)

    existing = {path.stem for path in pages_dir.glob("*.md")}
    crawled_slugs = set(written)
    extra = sorted(existing - crawled_slugs - PRESERVE_PAGE_NAMES)
    removed: list[str] = []
    if prune:
        for slug in extra:
            (pages_dir / f"{slug}.md").unlink()
            removed.append(slug)

    (plugin_root / "design-system" / "nav-manifest.json").write_text(
        json.dumps(nav, indent=2) + "\n", encoding="utf-8"
    )
    report = {
        "written": written,
        "unchanged_extras": extra if not prune else [],
        "removed": removed,
        "preserve": sorted(PRESERVE_DESIGN_FILES),
    }
    (crawl_dir(plugin_root) / "apply-report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


def _agent_apply_prompt(plugin_root: Path, manifest: dict[str, Any]) -> str:
    slugs = [p["slug"] for p in manifest.get("pages", [])]
    return f"""# AI apply — Nexus DLS from Zero Height crawl

Do **not** rewrite `design-system/pages/*.md` or `nav-manifest.json` (the crawl apply step owns those).
Do **not** edit `gap-analysis.md` unless the user asks (ConfigTool-specific).

## Inputs

- Crawl manifest: `design-system/.crawl/manifest.json`
- Page snapshots: `design-system/pages/*.md` ({len(slugs)} pages)
- Current catalogs: `design-system/tokens.md`, `components.md`, `web-mapping.md`
- Current rules: `rules/nexus-dls-*.mdc`

## Tasks

1. Read new/changed component pages. Update `tokens.md` with colors, type, spacing that appear in the DLS (keep CSS custom property names stable unless Zero Height renamed them).
2. Update `components.md` matrix: every snapshot slug that is a UI component should have a Bootstrap / Razor mapping. Mark unmapped embedded-only patterns.
3. Update `web-mapping.md` for web adaptations. Keep authority paths as `design-system/...` (not `docs/design-system/...`).
4. Refresh `rules/nexus-dls-foundations.mdc`, `nexus-dls-components.mdc`, `nexus-dls-layout.mdc`, `nexus-dls-accessibility.mdc` so hex values, do-not lists, and component mappings match tokens/components. Keep existing YAML frontmatter (`description`, `globs`, `alwaysApply`).
5. Leave `dls-authority.mdc` structure intact; only adjust source table if files moved.
6. Summarize: new pages, removed pages, token changes, rule changes. Do not invent Figma or Polarion updates.

Styleguide: {manifest.get("start_url")}
Crawled at: {manifest.get("crawled_at")}
"""


def cmd_apply(args: argparse.Namespace) -> int:
    plugin_root = Path(args.plugin_root)
    try:
        report = apply_snapshots(plugin_root=plugin_root, prune=args.prune)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Wrote {len(report['written'])} page snapshots and nav-manifest.json")
    if report["unchanged_extras"]:
        print("Pages not in crawl (kept; pass --prune to delete):")
        for slug in report["unchanged_extras"]:
            print(f"  {slug}")
    if report["removed"]:
        print("Pruned:")
        for slug in report["removed"]:
            print(f"  {slug}")
    print("Catalogs/rules are not auto-rewritten. In Cursor: use the sync-dls skill AI apply step.")
    print(f"Prompt: {crawl_dir(plugin_root) / 'AGENT_APPLY.md'}")
    return 0


def cmd_refresh(args: argparse.Namespace) -> int:
    crawl_rc = cmd_crawl(args)
    if crawl_rc != 0:
        return crawl_rc
    return cmd_apply(args)


def build_parser() -> argparse.ArgumentParser:
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument(
        "--plugin-root",
        default=str(plugin_root_from_script()),
        help="baxter-ux plugin root",
    )
    shared.add_argument("--start", default=DEFAULT_START, help="Zero Height start URL")
    shared.add_argument(
        "--cdp-url",
        default=os.environ.get("ZEROHEIGHT_CDP_URL"),
        help="Attach to Chrome remote debugging (best for corporate SSO)",
    )
    parser = argparse.ArgumentParser(description=__doc__, parents=[shared])
    sub = parser.add_subparsers(dest="command", required=True)

    login = sub.add_parser("login", parents=[shared], help="Open Zero Height and wait for SSO")
    login.add_argument("--login-timeout", type=int, default=600)
    login.add_argument(
        "--headed-ok",
        action="store_true",
        help="Skip DISPLAY check (use if headed Chrome works anyway)",
    )
    login.set_defaults(func=cmd_login)

    crawl = sub.add_parser(
        "crawl", parents=[shared], help="Spider styleguide pages into design-system/.crawl"
    )
    crawl.add_argument("--headless", action="store_true", default=True)
    crawl.add_argument("--headed", action="store_false", dest="headless")
    crawl.add_argument("--limit", type=int, default=0, help="Max pages (0 = all)")
    crawl.add_argument("--delay", type=float, default=0.4)
    crawl.add_argument("--settle-ms", type=int, default=1200)
    crawl.add_argument("--resume", action="store_true")
    crawl.set_defaults(func=cmd_crawl)

    apply_cmd = sub.add_parser(
        "apply", parents=[shared], help="Write pages/*.md and nav-manifest.json from crawl"
    )
    apply_cmd.add_argument("--prune", action="store_true", help="Delete page snapshots not in crawl")
    apply_cmd.set_defaults(func=cmd_apply)

    refresh = sub.add_parser("refresh", parents=[shared], help="crawl + apply")
    refresh.add_argument("--headless", action="store_true", default=True)
    refresh.add_argument("--headed", action="store_false", dest="headless")
    refresh.add_argument("--limit", type=int, default=0)
    refresh.add_argument("--delay", type=float, default=0.4)
    refresh.add_argument("--settle-ms", type=int, default=1200)
    refresh.add_argument("--resume", action="store_true")
    refresh.add_argument("--prune", action="store_true")
    refresh.set_defaults(func=cmd_refresh)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
