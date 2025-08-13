from __future__ import annotations
from dataclasses import dataclass
from typing import List
from .descriptor import Descriptor, Profile

@dataclass
class SourceOutput:
    files: List[str]
    services: List[str]
    options: List[str]

def execute(profile_name: str, d: Descriptor) -> SourceOutput:
    # TODO: Detect capabilities (nvidia, cdi, rocm, mdc)
    prof: Profile = d.profiles.get(profile_name, Profile())
    files: List[str] = ["compose.yml"]
    # TODO: Include overlays per rules (service, option, cross-files)
    return SourceOutput(files=files, services=prof.services, options=prof.options)
