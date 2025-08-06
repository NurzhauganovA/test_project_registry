from pathlib import Path


def read_version() -> str:
    for base in (Path(__file__).parent, Path(__file__).parent.parent, Path(__file__).parent.parent.parent):
        file = base / "VERSION"
        if file.exists():
            return file.read_text().strip()

    return "0.0.1"
