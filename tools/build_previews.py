"""Capture simulator first screens with Chrome from local, network-isolated sites."""
from contextlib import contextmanager
from functools import partial
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import quote
import io
import json
import os
import re
import shutil

from PIL import Image
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
output = Path(os.environ.get("PREVIEW_OUTPUT", "preview-output")).resolve()
output.mkdir(exist_ok=True, parents=True)
public_host = "https://mananin42.github.io/"
private = re.compile(r"[\w.+%-]+@[\w.-]+\.[A-Za-z]{2,}|01[016789][- ]?\d{3,4}[- ]?\d{4}|\d{6}-[1-4]\d{6}|-----BEGIN .*PRIVATE KEY|(?:ghp_|github_pat_|sk-proj-)[\w-]{12,}|(?:학번|성명|학생명)\s*[:：]\s*\S+", re.I)

@contextmanager
def local_site(folder):
    with ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(folder))) as server:
        Thread(target=server.serve_forever, daemon=True).start()
        try:
            yield f"http://127.0.0.1:{server.server_port}/"
        finally:
            server.shutdown()

def capture(browser, origin, relative):
    context = browser.new_context(viewport={"width": 1136, "height": 710}, locale="ko-KR",
                                  reduced_motion="reduce", service_workers="block")
    try:
        def restrict(route):
            if route.request.url.startswith(origin) and "/.git/" not in route.request.url:
                route.continue_()
            else:
                route.abort()
        context.route("**/*", restrict)
        context.route_web_socket("**/*", lambda sock: sock.close())
        page = context.new_page()
        response = page.goto(origin + quote(relative), wait_until="networkidle", timeout=20000)
        if not response.ok or page.locator("input[type=password]").count() or private.search(page.locator("body").inner_text()):
            return None
        page.evaluate("() => document.fonts.ready")
        if relative == "cox2-drug-action/index.html":
            page.wait_for_function("() => typeof ready !== 'undefined' && ready", timeout=60000)
        image = Image.open(io.BytesIO(page.screenshot(animations="disabled"))).convert("RGB")
        image.thumbnail((864, 540), Image.Resampling.LANCZOS)
        blob = io.BytesIO()
        image.save(blob, format="WEBP", quality=80)
        payload = blob.getvalue()
        key = sha256(payload).hexdigest() + ".webp"
        (output / key).write_bytes(payload)
        return key
    finally:
        context.close()

def site_inputs():
    docs = root / "docs"
    pages = []
    for file in sorted(docs.rglob("*.html")):
        name = file.relative_to(docs).as_posix()
        if file.is_symlink() or name == "index.html" or name.startswith("preview-renderer/"):
            continue
        if not re.search(r'<meta\s+http-equiv=["\']refresh["\']', file.read_text("utf-8"), re.I):
            pages.append(name)
    yield "science-simulators", docs, pages
    if "PREVIEW_PEERS" in os.environ:
        peers = Path(os.environ["PREVIEW_PEERS"])
        for slug, folder in [("aspirin-process-simulator", "."), ("mxene-cosmetic-dispersion-simulator", "."),
                             ("ring-strain-newman-projection-visualizer", "docs")]:
            site = peers / slug / folder
            if not (site / "index.html").is_file():
                raise FileNotFoundError(site / "index.html")
            yield slug, site, ["index.html"]

manifest = {}
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path=os.environ.get("CHROME_BIN") or shutil.which("google-chrome"),
                                 args=["--disable-dev-shm-usage", "--use-angle=swiftshader",
                                       "--enable-unsafe-swiftshader"])
    # Missing glyphs draw the same box. Check the browser's pixels before publishing any screenshots.
    probe = browser.new_page(locale="ko-KR")
    readable = probe.evaluate("""() => {
      const canvas = document.createElement('canvas');
      canvas.width = canvas.height = 50;
      const ctx = canvas.getContext('2d');
      ctx.font = '32px sans-serif';
      const glyphs = Array.from('한글열', glyph => {
        ctx.clearRect(0, 0, 50, 50);
        ctx.fillText(glyph, 4, 38);
        return canvas.toDataURL();
      });
      return new Set(glyphs).size === glyphs.length;
    }""")
    probe.close()
    if not readable:
        raise RuntimeError("Chrome cannot render distinct Korean glyphs")
    for slug, folder, pages in site_inputs():
        with local_site(folder) as origin:
            for relative in pages:
                key = capture(browser, origin, relative)
                if key:
                    url = public_host + slug + "/" + quote(relative)
                    manifest[url] = key
                    if relative == "index.html" or relative.endswith("/index.html"):
                        manifest[url.removesuffix("index.html")] = key
    browser.close()
if not manifest:
    raise SystemExit("No preview images built.")
(output / "manifest.json").write_text(json.dumps(manifest, indent=2), "utf-8")
