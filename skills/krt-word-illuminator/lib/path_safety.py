"""Output-path guards for document tools."""

from __future__ import annotations

import os
import stat
import tempfile
from pathlib import Path
from typing import Iterable


def resolve_output_path(path: Path, *, label: str) -> Path:
    """Resolve an output path while rejecting existing symlink components."""
    lexical = path if path.is_absolute() else Path.cwd() / path
    lexical = lexical.absolute()
    components = [*reversed(lexical.parents), lexical]
    for component in components:
        if component.is_symlink():
            raise ValueError(f"{label} contains a symbolic-link component")
    return lexical.resolve()


def atomic_write_text(
    path: Path,
    text: str,
    *,
    overwrite: bool,
    label: str,
) -> Path:
    """Write UTF-8 text without clobbering unless overwrite is authorized."""
    output = resolve_output_path(path, label=label)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing {label}: {output}")
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=output.parent,
        prefix=f".{output.name}.",
        suffix=".tmp",
        delete=False,
    ) as temporary:
        temporary.write(text)
        temporary.flush()
        os.fsync(temporary.fileno())
        temporary_path = Path(temporary.name)
    return atomic_publish_file(
        temporary_path,
        output,
        overwrite=overwrite,
        label=label,
    )


def atomic_publish_file(
    prepared: Path,
    path: Path,
    *,
    overwrite: bool,
    label: str,
) -> Path:
    """Publish a prepared regular file through one no-follow parent descriptor."""
    output = resolve_output_path(path, label=label)
    output.parent.mkdir(parents=True, exist_ok=True)
    prepared = prepared.absolute()
    if prepared.parent.resolve() != output.parent:
        raise ValueError(f"Prepared {label} must be in the output directory")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(
        os, "O_NOFOLLOW", 0
    )
    parent_descriptor = os.open(output.parent, flags)
    try:
        metadata = os.stat(
            prepared.name,
            dir_fd=parent_descriptor,
            follow_symlinks=False,
        )
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError(f"Prepared {label} is not a regular file")
        if overwrite:
            os.replace(
                prepared.name,
                output.name,
                src_dir_fd=parent_descriptor,
                dst_dir_fd=parent_descriptor,
            )
        else:
            os.link(
                prepared.name,
                output.name,
                src_dir_fd=parent_descriptor,
                dst_dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
            os.unlink(prepared.name, dir_fd=parent_descriptor)
    except FileExistsError as error:
        raise FileExistsError(
            f"Refusing to overwrite existing {label}: {output}"
        ) from error
    finally:
        try:
            os.unlink(prepared.name, dir_fd=parent_descriptor)
        except FileNotFoundError:
            pass
        os.close(parent_descriptor)
    return output


def atomic_publish_files(
    entries: Iterable[tuple[Path, Path, str]],
    *,
    overwrite: bool,
) -> list[Path]:
    """Publish a small artifact set and restore prior files if any publish fails."""
    resolved = [
        (prepared, resolve_output_path(output, label=label), label)
        for prepared, output, label in entries
    ]
    targets = [output for _prepared, output, _label in resolved]
    if len(set(targets)) != len(targets):
        raise ValueError("Artifact transaction contains duplicate output paths")
    for _prepared, output, label in resolved:
        if output.exists() and not overwrite:
            raise FileExistsError(
                f"Refusing to overwrite existing {label}: {output}"
            )

    backups: dict[Path, Path] = {}
    published: list[Path] = []
    try:
        if overwrite:
            for _prepared, output, label in resolved:
                if not output.exists():
                    continue
                with tempfile.NamedTemporaryFile(
                    dir=output.parent,
                    prefix=f".{output.name}.backup.",
                    delete=False,
                ) as temporary:
                    backup = Path(temporary.name)
                backup.unlink()
                try:
                    os.link(output, backup, follow_symlinks=False)
                except OSError as error:
                    raise OSError(f"Could not preserve existing {label}") from error
                backups[output] = backup

        for prepared, output, label in resolved:
            atomic_publish_file(
                prepared,
                output,
                overwrite=overwrite,
                label=label,
            )
            published.append(output)
    except Exception:
        for output in reversed(published):
            backup = backups.pop(output, None)
            if backup is not None:
                backup.replace(output)
            else:
                try:
                    output.unlink()
                except FileNotFoundError:
                    pass
        raise
    finally:
        for prepared, _output, _label in resolved:
            try:
                prepared.unlink()
            except FileNotFoundError:
                pass
        for backup in backups.values():
            try:
                backup.unlink()
            except FileNotFoundError:
                pass
    return targets
