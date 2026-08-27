#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Panel sunucusu — statik dosyalar + kurulum/tarama API'si.

`python -m http.server` yalnızca dosya SERVİS eder; panelin kurulum formunun
config.json'u YAZABİLMESİ ve taramayı başlatabilmesi için bu küçük sunucu var.

    python serve.py            # http://127.0.0.1:8137
    python serve.py 8139       # başka port

Yalnızca 127.0.0.1'e bağlanır: dosya yazan ve alt süreç çalıştıran bir uçtur,
ağa açılmaz.

Uçlar:
    GET  /api/status   → kurulum durumu + süren taramanın logu
    POST /api/config   → workspace/config.json'u yaz (doğrulayarak)
    POST /api/scan     → refresh.py'yi başlat, logu /api/status'tan akıt
"""
import json
import shutil
import subprocess
import sys
import threading
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = Path(__file__).resolve().parent
WS = BASE / "workspace"
TPL = BASE / "templates"

_scan = {"running": False, "lines": [], "done": False, "code": None}
_lock = threading.Lock()


# ---------------------------------------------------------------- yardımcılar
def read_config():
    try:
        return json.loads((WS / "config.json").read_text(encoding="utf-8"))
    except Exception:
        return None


def validate(app):
    """setup.py ile aynı kurallar — panel de aynı cevabı görsün."""
    p = []
    if not (app.get("name") or "").strip() or app.get("name") == "My App":
        p.append("Uygulama adı gerekli")
    if not app.get("iosId") and not (app.get("playId") or "").strip():
        p.append("App Store ID'si ya da Play paket adından en az biri gerekli")
    if app.get("playId") == "com.example.myapp":
        p.append("Play paket adı hâlâ örnek değerinde")
    if not [k for k in (app.get("keywords") or []) if str(k).strip()]:
        p.append("En az bir hedef kelime gerekli — radar ölçecek bir şey bulamaz")
    if not (app.get("competitors") or []):
        p.append("En az bir rakip gerekli — etiket matrisi rakiplerden çıkar")
    return p


def status_payload():
    cfg = read_config()
    app = ((cfg or {}).get("apps") or {}).get((cfg or {}).get("activeApp")) or {}
    with _lock:
        scan = dict(_scan)
        scan["lines"] = scan["lines"][-200:]
    return {
        "hasConfig": bool(app),
        "problems": validate(app) if app else ["config.json yok"],
        "hasData": (WS / "data.json").exists(),
        "hasAdvisor": bool((lambda a: a and (a.get("recommendations") or a.get("asoSuggestions")))(
            _safe_json(WS / "advisor.json"))),
        "activeApp": (cfg or {}).get("activeApp"),
        "lang": (cfg or {}).get("lang", "tr"),
        "scan": scan,
    }


def _safe_json(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def seed_workspace():
    """workspace/ yoksa şablonlardan kur — kullanıcı setup.py çalıştırmasa da panel açılsın."""
    WS.mkdir(exist_ok=True)
    lang = (read_config() or {}).get("lang", "en")
    for name, tpl in (("config.json", "config.json"),
                      ("advisor.json", "advisor.json"),
                      ("playbook.json", f"playbook.{lang}.json")):
        target = WS / name
        if target.exists():
            continue
        src = TPL / tpl
        if not src.exists() and name == "playbook.json":
            src = TPL / "playbook.en.json"
        if src.exists():
            shutil.copy(str(src), str(target))


def run_scan():
    with _lock:
        if _scan["running"]:
            return False
        _scan.update(running=True, lines=[], done=False, code=None)
    threading.Thread(target=_scan_worker, daemon=True).start()
    return True


def _scan_worker():
    try:
        proc = subprocess.Popen(
            [sys.executable, "-u", str(BASE / "refresh.py")],
            cwd=str(BASE), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace")
        for line in proc.stdout:
            with _lock:
                _scan["lines"].append(line.rstrip())
        code = proc.wait()
    except Exception as e:
        with _lock:
            _scan["lines"].append(f"HATA: {e}")
        code = -1
    with _lock:
        _scan.update(running=False, done=True, code=code)


# -------------------------------------------------------------------- handler
class Handler(SimpleHTTPRequestHandler):
    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split("?")[0] == "/api/status":
            return self._json(status_payload())
        return super().do_GET()

    def do_POST(self):
        path = self.path.split("?")[0]
        try:
            n = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(n) or b"{}") if n else {}
        except Exception as e:
            return self._json({"ok": False, "error": f"geçersiz JSON: {e}"}, 400)

        if path == "/api/config":
            return self._save_config(body)
        if path == "/api/scan":
            ok = run_scan()
            return self._json({"ok": ok, "error": None if ok else "tarama zaten sürüyor"})
        return self._json({"ok": False, "error": "bilinmeyen uç"}, 404)

    def _save_config(self, body):
        app = body.get("app") or {}
        key = (body.get("key") or app.get("name") or "app").strip().lower()
        key = "".join(c if c.isalnum() or c in "-_" else "-" for c in key).strip("-") or "app"
        seed_workspace()
        cfg = read_config() or {"activeApp": key, "apps": {}}
        cfg.setdefault("apps", {})
        # şablon bloğu duruyorsa ve dolduruluyorsa onun yerini al
        if "my-app" in cfg["apps"] and key != "my-app":
            cfg["apps"].pop("my-app", None)
        prev = cfg["apps"].get(key) or {}
        prev.update({k: v for k, v in app.items() if v not in (None, "")})
        for k in ("brandTerms", "keywords", "screenHeadings", "competitors", "countries"):
            if k in app:
                prev[k] = app[k]           # listeler daima değiştirilir, birleştirilmez
        cfg["apps"][key] = prev
        cfg["activeApp"] = key
        if body.get("lang"):
            cfg["lang"] = body["lang"]
        cfg.pop("_help", None) if body.get("stripHelp") else None
        (WS / "config.json").write_text(
            json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
        return self._json({"ok": True, "problems": validate(prev), "activeApp": key})

    def log_message(self, fmt, *args):
        if "/api/" in (args[0] if args else ""):
            return          # api gürültüsünü bastır, dosya isteklerini göster
        super().log_message(fmt, *args)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8137
    seed_workspace()
    handler = partial(Handler, directory=str(BASE))
    srv = ThreadingHTTPServer(("127.0.0.1", port), handler)
    url = f"http://127.0.0.1:{port}"
    print(f"MarketingHub paneli: {url}   (durdurmak için Ctrl+C)")
    print("Kurulum ve tarama panelin ⚙️ Kurulum sekmesinden yapılır.")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nkapatıldı")
    return 0


if __name__ == "__main__":
    sys.exit(main())
