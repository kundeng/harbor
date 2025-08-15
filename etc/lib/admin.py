from __future__ import annotations
import subprocess
from pathlib import Path
import typer

app = typer.Typer(help="Harbor v2 admin utilities (stubs mapping legacy .scripts)")

ROOT = Path(__file__).resolve().parents[2]  # repo root (harbor2/)

@app.command()
def hello():
    """Quick sanity check."""
    typer.echo("harbor2 admin ready @ " + str(ROOT))

@app.group()
def repo():
    """Repo maintenance commands."""
    pass

@repo.command("move-folders")
def repo_move_folders(dry_run: bool = True):
    """Stub: previously .scripts/* moves. Implemented earlier via git mv.
    TODO: no-op for now.
    """
    typer.echo("[stub] repo move-folders (dry-run=%s)" % dry_run)

@repo.command("clean-empty-dirs")
def repo_clean_empty_dirs(path: Path = ROOT / "etc/stacks"):
    """Remove empty directories under etc/stacks."""
    removed = 0
    for p in sorted(path.rglob("*")):
        if p.is_dir() and not any(p.iterdir()):
            p.rmdir(); removed += 1
    typer.echo(f"Removed {removed} empty directories under {path}")

@app.group()
def runner():
    """Runner image and commands."""
    pass

@runner.command("build")
def runner_build(tag: str = "harbor2-runner:local"):
    """Build runner image from etc/runner/Dockerfile."""
    dockerfile = ROOT / "etc/runner/Dockerfile"
    subprocess.run(["docker", "build", "-f", str(dockerfile), "-t", tag, str(ROOT)], check=True)

@app.group()
def docs():
    """Docs and exports."""
    pass

@docs.command("export-conport")
def docs_export_conport(output: Path = ROOT.parent / "conport_export" / "manual" ):
    """Placeholder: export handled via MCP. This stub documents the intent."""
    output.mkdir(parents=True, exist_ok=True)
    typer.echo(f"[stub] ConPort export folder prepared at {output}")

if __name__ == "__main__":
    app()
