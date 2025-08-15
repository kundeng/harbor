# Harbor v2 Project Brief

## Overview
Harbor v2 evolves Harbor into a descriptor-driven, runner-based orchestration system. It preserves Harbor’s strengths (smart compose selection, single-network multi-service stack, ephemeral routines) while adding:

- Descriptor-defined workflows and stages (kstack-style)
- Config interpolation (pre-rendered configs, not entrypoint hacks)
- Layered environment model (sys.env → site.env → service.env)
- Secure, pluggable secret handling (dynamic injection at deploy; SOPS optional later)
- Optional, on-demand Cloudflare tunneling
- Traefik routing driven by compose file naming/overlays

This brief codifies requirements, architecture, milestones, and deliverables.

## Goals
- Maintain Harbor’s compose overlay “genius” and ephemeral routines
- Introduce a clear workflow/stage/action model via a descriptor
- Add a flexible config interpolation pipeline
- Support layered env resolution and dynamic secret injection at deploy time
- Keep tunneling as an optional action; support quick tunnels now, named tunnels later
- Keep Traefik via naming/overlays; allow parameterization via env/interpolation
- Non-breaking transition; existing CLI continues to work

## Non-Goals (v2)
- Replace Docker Compose
- Remove ephemeral container execution
- Mandate named Cloudflare tunnels (optional after v2)

## Current State (Summary)
- Entry point: `harbor2/harbor.sh`
  - Compose selection and layering via `compose_with_options()`/`resolve_compose_files()`
  - Many `run_*` CLI commands (up/down/build/logs/exec/…)
  - Quick Cloudflare tunnels via `establish_tunnel()`; `compose.cfd.yml`
- Routines: TypeScript (Deno) executed in ephemeral containers
- Env: plaintext `.env` via `envManager.ts`; no secret backend
- Traefik: routing via compose overlays with labels

## Key Decisions (confirmed)
- Ephemeral routines are “runners” (keep)
- Compose selection defined as rules in the source stage
- Tunneling is optional/on-demand actions
- Traefik “through naming” (labels/overlays), parameterized by env
- `harbor.yaml` NOT at repo root
  - System-level descriptor lives under an etc-style directory (per-deployment)
  - Per-stack `harbor.yaml` overrides allowed but system-level will usually suffice
- `harbor deploy` auto-runs `prepare` then `up`
- Add flexible config interpolation supporting arbitrary file types
- Secrets: decide concrete backend later; support dynamic injection at deploy; SOPS optional

## Architecture

### Descriptor and Location
- System descriptor: `harbor2/etc/harbor.yaml` (per deployment)
- Optional overrides: `harbor2/stacks/<stack>/harbor.yaml`
- Descriptor defines stages and actions; actions adapt to Harbor’s existing engine

### Stage Model
- source: select and order compose files and options based on declarative rules
- prepare: merge env (sys/site/service), resolve secrets, interpolate configs, stage run artifacts in `var/run/`
- deploy: compose up (with auto prepare if not already run), optional tunnel actions
- post_deploy: open URLs, health checks, tail logs
- destroy: compose down, stop tunnels, cleanup `var/run/` if configured

### Runners
- All routines (descriptor loading, env/secrets merge, interpolation, verification) run in ephemeral containers via `run_routine()`

## Compose Selection as Rules (source stage)
Rules preserve Harbor semantics:
- Auto capability detection: `nvidia`, `cdi`, `rocm`, `mdc`
- Always include `compose.yml`
- Include service overlays: `compose.<service>.yml`
- Include capability overlays: e.g., `*.nvidia.*`, `*.mdc.*`
- Cross-files: `compose.x.<a>.<b>.yml` included if all tokens match options/services
- Wildcard profile: `*` includes all non-capability overlays for the selected services
- Output: ordered `-f` files + resolved `services` and `options` for downstream stages

## Environment and Secrets Model

### Layering
- sys.env → site.env → service.env (merge order top→bottom)
  - sys.env: system-level defaults for a deployment
  - site.env: per-site (or per-environment) overrides
  - service.env: per-service overrides

Proposed file mapping (examples; not strict):
- System: `harbor2/etc/sys.env`
- Site: `harbor2/etc/site.env` (or `harbor2/etc/sites/<name>.env`)
- Service: `harbor2/stacks/<service>/service.env`
- Developer overrides: `.env.local` (ignored by VCS)

### Secrets
- Dynamic injection at deploy time (baseline)
- Supported sources (optional, merge in this order after non-secret env):
  - `override.secrets.env` (plaintext if needed)
  - `*.sops.env` (Age-encrypted; decrypt in runner using `AGE_PRIVATE_KEY` or key file)
- In-memory merge by default; do not persist unless explicitly requested
- If compose requires `--env-file`, generate `var/run/.env.run` with strict perms; remove on destroy unless configured otherwise

#### SOPS/Age key management

- SOPS encrypts sensitive values in-place inside files (YAML/JSON/ENV), keeping structure readable in diffs. We will support SOPS with Age recipients.
- Age identities (private keys) must live outside the repo, typically at `~/.config/sops/age/keys.txt` (0600) or via `AGE_PRIVATE_KEY` env. Back them up securely (password manager, Keychain, or an encrypted backup).
- Team workflow: encrypt to multiple Age recipients (each developer + service account). Decryption happens inside a runner container so the host remains clean.
- Never commit private keys. We will provide a short guide and a linter to verify keys are not accidentally included in the repo.

## Config Interpolation
- Motivation: avoid runtime entrypoint hacks; produce deterministic config files before startup
- Inputs:
  - Templates per service: `harbor2/stacks/<service>/templates/**`
  - Values: merged env (sys/site/service + secrets) + descriptor-provided extra values
- Output:
  - `var/run/<service>/config/**` (mounted via volumes)
- Engine:
  - Start with a small, safe templating engine (e.g., Handlebars/Eta) and/or `envsubst` mode for `${VAR}`
  - Requirements:
    - Works with YAML/JSON/text
    - Deterministic, no arbitrary code execution, no network
    - Simple helpers (upper/lower, default, join), opt-in

## Hooks

- Purpose: allow custom logic before/after stages and reuse existing stack scripts without forking the engine.
- Hook points (global): `pre_source`, `post_source`, `pre_prepare`, `post_prepare`, `pre_deploy`, `post_deploy`, `pre_destroy`, `post_destroy`.
- Hook points (per-service, optional): `pre_service_prepare`, `post_service_prepare`, `pre_service_up`, `post_service_up`.
- Hook types:
  - shell: run `harbor2/stacks/<service>/hooks/*.sh` or a specified path. Default execution inside a runner container; explicit opt-in needed for host execution.
  - ts_routine: execute a TypeScript routine via `run_routine()`.
  - container: run an arbitrary container image/command.
- Execution environment:
  - Runner container with merged env and selected services/options injected.
  - Read-only repo and descriptor; writable `harbor2/var/run/` for artifacts.
  - Timeouts and logging; non-zero exit fails the stage unless `continueOnError: true`.
- Autodiscovery (optional): if enabled, automatically run `hooks/<stage>.sh` when present under a stack directory.

## Tunneling
- Quick tunnels (baseline): `establish_tunnel()` using `cloudflare/cloudflared` to yield `*.trycloudflare.com` URLs
- Actions: `net.tunnel.quick { service }` (in deploy/post_deploy or on demand)
- Named tunnels (optional later): token/credentials via secrets (SOPS recommended), ingress YAML rendered in `prepare`, actions `net.tunnel.named.up|down`

## Traefik
- Keep routing via compose overlays and naming; parameterize with env from prepare
- Optional: generate a small overlay at `var/run/overlays/compose.traefik.gen.yml` for fully dynamic labels when needed

## CLI Integration
- Non-breaking: existing `harbor up/down/...` continue to work
- New high-level commands:
  - `harbor deploy` → auto-runs `prepare` then `up` when descriptor present
  - `harbor run <stage>` → run a specific stage via descriptor
- Action adapters cover compose/env/tunnel/open/service interactions

### Utility actions

- Provide parity for important CLI utilities:
  - `doctor`: environment and dependency diagnostics; can run inside runner and optionally on host, reporting versions (docker/compose/yq/deno), network status, and key files.
  - `history` and `size`: existing helpers can be wrapped as actions for consistency.
  - `tools/dev`: expose via an action group for advanced workflows.
  - `svc.cmd`: generic adapter to call service-specific helpers implemented in `harbor.sh` (avoids enumerating every helper separately).

## Text-based UI (future)

- Explore a Textual-based TUI to browse merged env, decrypted secrets (when permitted), and interpolated configs. TUI runs against runner-exposed APIs/state to avoid leaking secrets to disk. Access is opt-in and can be gated by role.

## Language strategy

- Core and CLI will be implemented in Python for Harbor v2 (unifying runtime and future TUI language).
- The legacy TypeScript skeletons will be retired; parity will be rebuilt in Python modules.
- Execution will occur inside runner containers. Use a standard Python virtual environment (venv) inside the container for isolation; this is sufficient. We may adopt `uv` later for faster installs and lockfiles, but it is optional.
- The Textual-based TUI will be a Python client using the same core modules (or a thin local API), ensuring a single source of truth.

## File/Directory Layout (proposal)
```
harbor2/
  harbor.sh
  lib/                    # all Python modules and CLI entry
    __init__.py
    cli.py                # Typer CLI entrypoint (python -m lib.cli)
    descriptor.py         # load/validate harbor.yaml
    source.py             # compose rules executor
    prepare.py            # env layering + interpolation
    actions.py            # compose/tunnel/open/svc adapters (future)
    secrets.py            # SOPS/Age helpers (future)
    hooks.py              # hooks execution (future)
  etc/
    stacks/               # consolidated service compose files (base + overlays)
    harbor.yaml           # system-level descriptor (per deployment)
    sys.env               # system env defaults (optional)
    site.env              # site env overrides (optional)
    sites/                # optional per-site envs (e.g., etc/sites/prod.env)
  stacks/
    <service>/
      service.env         # per-service env (optional)
      templates/          # config templates to interpolate
      hooks/              # optional shell hooks per service
  docs/
    projectBrief.md
    Harbor-Descriptor.md
    Harbor-Secrets.md
    Harbor-Prepare-Deploy.md
    Harbor-Tunnels.md
  var/
    run/<service>/config/**
    overlays/compose.traefik.gen.yml
  requirements.txt        # Python dependencies (pinned)
  Dockerfile.runner       # Runner image (python + venv)
  Justfile                # cross-platform entry; runs Python core in ephemeral container
```

## Milestones
- M1: Descriptor loader + workflow runner; adapters for `compose.up/down`, `open`, `logs`, `env.merge` (non-breaking)
- M2: Prepare stage with env layering (sys/site/service), dynamic secret injection (plaintext now), and config interpolation → `var/run/`
- M3: Tunneling action (quick), UX improvements (list/stop/copy URL/QR)
- M4: Traefik parameterization via env; optional generated overlay
- M5: Optional SOPS-age provider and named tunnels
- M6: Documentation and examples; migration notes; tests

## Deliverables
- Source rules executor (preserves Harbor compose semantics)
- Env/secrets pipeline and interpolation engine (runner-executed)
- Action adapters for compose/env/tunnel/open/service
- System/per-stack descriptors and templates (examples)
- Comprehensive docs and example workflows

## Risks and Mitigations
- Complexity: keep adapters thin; reuse Harbor’s selection logic; ship examples
- Secrets leakage: default to in-memory; strict `var/run` usage; clear docs and linting
- Backward compatibility: descriptor is additive; classic CLI remains

## Open Items
- Interpolation engine choice (start with envsubst + minimal handlebars-like?)
- Exact sys/site/service env file naming and precedence (outlined above; confirm details during M2)
- Named tunnels scope: schedule after v2 or include a minimal alpha?
- Hook autodiscovery default (on/off) and per-service hook surface area (finalize in M2)
- TUI scope and permissions model

## Example: System Descriptor (sketch)
```yaml
version: 1
profiles:
  default:
    services: ["litellm","webui"]
    options: ["*"]
source:
  rules:
    autoCapabilities: true
    base: ["compose.yml"]
    include:
      - "compose.${service}.yml"
      - "compose.*.${option}.yml"
      - "compose.x.${service}.${option}.yml"
prepare:
  env:
    sources:
      - { type: "sys", file: "harbor2/etc/sys.env", optional: true }
      - { type: "site", file: "harbor2/etc/site.env", optional: true }
      - { type: "service", dir: "harbor2/stacks", pattern: "service.env", optional: true }
      - { type: "dotenv", file: ".env.local", optional: true }
      - { type: "secrets", file: "override.secrets.env", optional: true }
      # - { type: "sops", file: "secrets.sops.env", optional: true }
  templates:
    - { from: "harbor2/stacks/${service}/templates/**", to: "harbor2/var/run/${service}/config/" }
  interpolation:
    engine: "handlebars"
    values:
      fromEnv: true
      extra: { TRAEFIK_TLS: "true" }
deploy:
  steps:
    - { action: "compose.up" }
    - { action: "net.tunnel.quick", service: "litellm", when: "${ENABLE_TUNNEL}" }
post_deploy:
  steps:
    - { action: "open", target: ["litellm","webui"] }
destroy:
  steps:
    - { action: "compose.down" }
    - { action: "net.tunnel.stop" }
```

---

Prepared: 2025-08-12
