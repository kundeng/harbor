# Cross-platform entry via `just` to run Python core in ephemeral container

# Variables
runner_image := "harbor2-runner:local"
workspace := "$(pwd)"

# Default help
default:
	@just --list

# Build the runner image
build-runner:
	docker build -f etc/runner/Dockerfile -t {{runner_image}} .

# Internal: ensure runner image exists
_ensure-runner:
	@if ! docker image inspect {{runner_image}} >/dev/null 2>&1; then \
		echo "[harbor2] Building runner image {{runner_image}}..."; \
		docker build -f etc/runner/Dockerfile -t {{runner_image}} .; \
	fi

# Run arbitrary CLI inside runner (pass args after --)
py *args:
	@just _ensure-runner
	docker run --rm \
		-v {{workspace}}:/workspace \
		-w /workspace/harbor2 \
		--network host \
		-e AGE_PRIVATE_KEY \
		{{runner_image}} \
		python -m etc.lib.cli {{args}}

# Convenience targets
source profile="default":
	@just py run source --profile {{profile}}

prepare profile="default":
	@just py run prepare --profile {{profile}}

deploy profile="default":
	@just py deploy --profile {{profile}}
