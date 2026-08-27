#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Yayınlanacak (temiz) kopyayı üretir — kişisel veri olmadan.

Ne yapar: kod ağacını hedef klasöre kopyalar, `workspace/`, `.git/`,
`__pycache__/` ve yedekleri DIŞARIDA bırakır. Yani repoyu klonlayan birinin
göreceği şeyin birebir aynısı. Kendi verilerine dokunmaz.

    python make_release.py                    # ../MarketingHub-release
    python make_release.py ../deneme          # başka bir hedef
    python make_release.py --zip              # ayrıca .zip üretir
    python make_release.py --run              # kopyaladıktan sonra 8138'de açar

Kendi çalışmanı görmek için buna gerek yok: her zamanki gibi start.bat /
start.command yeter (8137, workspace/ ile).
"""
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = Path(__file__).resolve().parent
EXCLUDE_DIRS = {"workspace", ".git", "__pycache__", ".idea", ".vscode", "node_modules"}
EXCLUDE_FILES = {".DS_Store", "Thumbs.db", "desktop.ini"}
RELEASE_PORT = 8138          # kendi panelin 8137'de kalsın, çakışmasın


def copy_tree(dst: Path):
    if dst.exists():
        shutil.rmtree(dst)
    n = 0
    for src in BASE.rglob("*"):
        rel = src.relative_to(BASE)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if src.name in EXCLUDE_FILES:
            continue
        if src.is_dir():
            continue
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        n += 1
    return n


def audit(dst: Path):
    """Kopyada kişisel veri kalmadığını doğrula — sessiz sızıntıya karşı."""
    import re
    needles = re.compile(
        r"workspace/(config|data|advisor|playbook)\.json|"
        r"\.secrets|AuthKey|BEGIN [A-Z ]*PRIVATE KEY", re.I)
    hits = []
    for f in dst.rglob("*"):
        if not f.is_file() or f.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".zip"}:
            continue
        if f.name == Path(__file__).name:
            continue        # tarayıcının kendi deseni eşleşmesin
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for m in needles.finditer(txt):
            # kod içinde workspace/... yoluna atıf normaldir; dosyanın kendisi olmamalı
            if m.group(0).startswith("workspace/"):
                continue
            hits.append(f"{f.relative_to(dst)}: {m.group(0)[:40]}")
    leaked = [p for p in ("workspace", ".git") if (dst / p).exists()]
    return hits, leaked


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    dst = Path(args[0]).resolve() if args else BASE.parent / (BASE.name + "-release")

    print(f"Kaynak : {BASE}")
    print(f"Hedef  : {dst}")
    if dst == BASE or BASE in dst.parents:
        sys.exit("Hedef, projenin kendisi ya da içi olamaz — dışarıda bir klasör seç.")

    n = copy_tree(dst)
    print(f"\n✓ {n} dosya kopyalandı (workspace/, .git/, __pycache__/ hariç)")

    hits, leaked = audit(dst)
    if leaked:
        sys.exit(f"✗ Kopyada olmaması gereken klasör var: {', '.join(leaked)}")
    if hits:
        print("\n✗ Kişisel veri şüphesi:")
        for h in hits[:10]:
            print("   ·", h)
        sys.exit(1)
    print("✓ Kişisel veri denetimi temiz")

    if "--zip" in flags:
        zip_path = shutil.make_archive(str(dst), "zip", root_dir=dst)
        size = Path(zip_path).stat().st_size / 1024
        print(f"✓ Arşiv: {zip_path} ({size:.0f} KB)")

    print("\nYayın kopyasını yeni kullanıcı gibi denemek için:")
    print(f"   cd {dst}")
    print("   python setup.py          → workspace'i şablondan kurar, eksikleri söyler")
    print(f"   python -m http.server {RELEASE_PORT}   → panel: http://localhost:{RELEASE_PORT}")
    print("\n(Kendi çalışman etkilenmedi: bu klasörde start.bat 8137'de açılmaya devam eder.)")

    if "--run" in flags:
        print(f"\nKurulum çalıştırılıyor ve panel {RELEASE_PORT} portunda açılıyor…")
        subprocess.run([sys.executable, "setup.py"], cwd=dst)
        webbrowser.open(f"http://localhost:{RELEASE_PORT}")
        subprocess.run([sys.executable, "-m", "http.server", str(RELEASE_PORT)], cwd=dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
