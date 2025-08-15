from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any
import os

try:
    import ruamel.yaml as ryaml  # type: ignore
except Exception:
    ryaml = None  # runtime will require installation via requirements.txt


@dataclass
class Profile:
    services: List[str] = field(default_factory=list)
    options: List[str] = field(default_factory=lambda: ["*"])


@dataclass
class Descriptor:
    version: int = 1
    profiles: Dict[str, Profile] = field(default_factory=dict)
    source: Dict[str, Any] = field(default_factory=dict)
    prepare: Dict[str, Any] = field(default_factory=dict)
    deploy: Dict[str, Any] = field(default_factory=dict)
    post_deploy: Dict[str, Any] = field(default_factory=dict)
    destroy: Dict[str, Any] = field(default_factory=dict)


def load(path: str) -> Descriptor:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    if ryaml is None:
        # Fallback very minimal parser for JSON-like YAML (dev only)
        import json
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        try:
            data = json.loads(text)
        except Exception as e:
            raise RuntimeError("ruamel.yaml not installed; cannot parse YAML") from e
    else:
        yaml = ryaml.YAML(typ="rt")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.load(f)
    return _coerce_descriptor(data)


def _coerce_descriptor(data: Dict[str, Any]) -> Descriptor:
    profiles: Dict[str, Profile] = {}
    for name, p in (data.get("profiles") or {}).items():
        profiles[name] = Profile(services=p.get("services", []), options=p.get("options", ["*"]))
    return Descriptor(
        version=int(data.get("version", 1)),
        profiles=profiles,
        source=data.get("source") or {},
        prepare=data.get("prepare") or {},
        deploy=data.get("deploy") or {},
        post_deploy=data.get("post_deploy") or {},
        destroy=data.get("destroy") or {},
    )


def validate(d: Descriptor) -> None:
    if d.version != 1:
        raise ValueError(f"Unsupported descriptor version: {d.version}")
    # Minimal structural checks
    if not isinstance(d.profiles, dict):
        raise ValueError("profiles must be a map")
