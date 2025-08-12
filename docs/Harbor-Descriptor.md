# Harbor Descriptor (harbor.yaml)

## Purpose
Descriptor-driven orchestration that defines stages and actions executed in runner containers. Keeps Harbor's compose strengths while adding env layering, secrets, and config interpolation.

## Stages
- source: resolve compose files, services, options.
- prepare: env layering + secrets, config interpolation to `var/run/`.
- deploy: compose up; may imply prepare.
- post_deploy: open/health/logs.
- destroy: compose down/cleanup.

## Hooks
Global: pre_/post_ for each stage.
Per-service: pre/post prepare and up.
Types: shell (runner default), ts_routine, container. Optional autodiscovery `hooks/<stage>.sh`.

## Actions (examples)
- compose.up|down|build|pull|ps|logs
- service.exec|shell|run|stats
- env.merge|get|set|list
- net.tunnel.quick|stop (named later)
- open
- doctor|history|size|tools.dev
- routine.run
- svc.cmd (generic wrapper for service-specific helpers)

## Env and Secrets
Layering: sys.env → site.env → service.env → .env.local → secrets (override.secrets.env, optional SOPS `*.sops.env`). In-memory by default. Write `var/run/.env.run` only if needed.

## Interpolation
Templates: `harbor2/stacks/<service>/templates/**`
Output: `harbor2/var/run/<service>/config/**`
Engine: envsubst + minimal handlebars-like (safe helpers).

