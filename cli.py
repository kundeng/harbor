#!/usr/bin/env python3
from typing import Optional
import typer

app = typer.Typer(help="Harbor v2 CLI (Python)")

@app.command()
def run(stage: str = typer.Argument(..., help="Stage to run: source|prepare|deploy|post_deploy|destroy"),
        profile: str = typer.Option("default", help="Profile name")):
    """Dispatch to stage executors (skeleton)."""
    from core import descriptor, source, prepare
    d = descriptor.load("harbor2/etc/harbor.yaml")
    descriptor.validate(d)
    if stage == "source":
        out = source.execute(profile, d)
        typer.echo({"files": out.files, "services": out.services, "options": out.options})
    elif stage == "prepare":
        # Skeleton; will merge env and interpolate templates
        typer.echo({"status": "prepare-not-implemented"})
    else:
        raise typer.Exit(code=2)

@app.command()
def deploy(profile: str = typer.Option("default")):
    """Auto runs prepare then compose up (skeleton)."""
    typer.echo({"status": "deploy-not-implemented", "profile": profile})

if __name__ == "__main__":
    app()
