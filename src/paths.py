from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    root: Path

    @property
    def data_dir(self) -> Path:
        return self.root / "data"

    @property
    def notebooks_dir(self) -> Path:
        return self.root / "notebooks"

    @property
    def cleaned_pattern(self) -> str:
        return "*_clean.csv"


def get_project_root() -> Path:
    # This file lives under src/, so project root is one parent up.
    return Path(__file__).resolve().parents[1]


def paths() -> ProjectPaths:
    return ProjectPaths(root=get_project_root())

