"""Build first-screen images from this repository's published simulator HTML."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import quote, urlsplit
from hashlib import sha256
import io, json, os, re, shutil
from PIL import Image
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
docs = root / "docs"
output = Path(os.environ.get("PREVIEW_OUTPUT","preview-output")).resolve()
output.mkdir(exist_ok=True, parents=True)
prefix = "https://mananin42.github.io/science-simulators/"
server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(docs)))
Thread(target=server.serve_forever, daemon=True).start()
origin = f"http://127.0.0.1:{server.server_port}"
private = re.compile(r"[\w.+%-]+@[\w.-]+\.[A-Za-z]{2,}|01[016789][- ]?\d{3,4}[- ]?\d{4}|\d{6}-[1-4]\d{6}|-----BEGIN .*PRIVATE KEY|(?:ghp_|github_pat_|sk-proj-)[\w-]{12,}|(?:학번|성명|학생명)\s*[:：]\s*\S+",re.I)
manifest = {}
try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get("CHROME_BIN") or shutil.which("google-chrome"), args=["--disable-dev-shm-usage"])
        for file in sorted(docs.rglob("*.html")):
            relative = file.relative_to(docs).as_posix()
            if file.is_symlink() or relative == "index.html" or relative.startswith("preview-renderer/"):
                continue
            context = browser.new_context(viewport={"width":1136,"height":710}, reduced_motion="reduce", service_workers="block")
            try:
                def restrict(route):
                    if route.request.url.startswith(origin + "/"):
                        route.continue_()
                    else:
                        route.abort()
                context.route("**/*", restrict)
                context.route_web_socket("**/*", lambda sock: sock.close())
                page=context.new_page()
                response=page.goto(origin+"/"+quote(relative),wait_until="networkidle",timeout=20000)
                if not response.ok or page.locator("input[type=password]").count() or private.search(page.locator("body").inner_text()):
                    continue
                page.evaluate("() => document.fonts.ready")
                image=Image.open(io.BytesIO(page.screenshot(animations="disabled"))).convert("RGB")
                image.thumbnail((864,540),Image.Resampling.LANCZOS)
                blob=io.BytesIO(); image.save(blob,format="WEBP",quality=80)
                payload=blob.getvalue()
                key=sha256(payload).hexdigest()+".webp"
                (output/key).write_bytes(payload)
                manifest[prefix+quote(relative)]=key
                if relative.endswith("/index.html"):
                    manifest[prefix+quote(relative.removesuffix("index.html"))]=key
            finally:
                context.close()
        browser.close()
finally:
    server.shutdown();server.server_close()
if not manifest:
    raise SystemExit("No preview images built.")
(output/"manifest.json").write_text(json.dumps(manifest,indent=2),"utf-8")
