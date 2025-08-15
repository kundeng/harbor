from __future__ import annotations
from typing import Dict, List
import os

LAYER_ORDER = ["sys", "site", "service", "dotenv", "secrets"]


def _parse_env_file(path: str) -> Dict[str, str]:
    env: Dict[str, str] = {}
    if not os.path.exists(path):
        return env
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def merge_env(sources: List[Dict]) -> Dict[str, str]:
    merged: Dict[str, str] = {}
    # simple layering: later sources override earlier ones
    for src in sources:
        typ = src.get("type")
        if typ in ("sys", "site", "dotenv", "secrets"):
            file = src.get("file")
            if file:
                merged.update(_parse_env_file(file))
        elif typ == "service":
            # scan dir for service.env
            base = src.get("dir") or "."
            pattern = src.get("pattern") or "service.env"
            for root, _dirs, files in os.walk(base):
                for fn in files:
                    if fn == pattern:
                        merged.update(_parse_env_file(os.path.join(root, fn)))
        # SOPS support to be added later via secrets.py helpers
    return merged


def envsubst(text: str, vars: Dict[str, str]) -> str:
    # very small ${VAR} replacement
    import re
    def repl(m):
        key = m.group(1)
        return vars.get(key, m.group(0))
    return re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", repl, text)


def render_templates(src_dir: str, dst_dir: str, vars: Dict[str, str]) -> None:
    import shutil
    from pathlib import Path
    src = Path(src_dir)
    dst = Path(dst_dir)
    if not src.exists():
        return
    dst.mkdir(parents=True, exist_ok=True)
    for p in src.rglob("*"):
        rel = p.relative_to(src)
        outp = dst / rel
        if p.is_dir():
            outp.mkdir(parents=True, exist_ok=True)
        else:
            text = p.read_text(encoding="utf-8")
            outp.write_text(envsubst(text, vars), encoding="utf-8")
