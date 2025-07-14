"""
CLI for compiling translations (.po → .mo) for 'ru' and 'kk' locales.
Runs as poetry-script module.
"""

from pathlib import Path

from pythongettext.msgfmt import Msgfmt


def compile_translations(locale_code: str = "ru"):
    """
    Compiles .po files into .mo files for the specified language.
    """
    base_dir = Path(__file__).resolve().parent.parent.parent
    po_file = base_dir / "locale" / locale_code / "LC_MESSAGES" / "messages.po"
    mo_file = po_file.with_suffix(".mo")

    if not po_file.exists():
        print(f"Translation file .po was not found in this path: {po_file}")
        return

    with po_file.open("rb") as po:
        mo_content = Msgfmt(po).get()
        with mo_file.open("wb") as mo:
            mo.write(mo_content)

    print(f"Translation file is compiled: {mo_file}")


def main():
    locales = ["ru", "kk"]
    for loc in locales:
        print(f"→ Compiling locale...: {loc}")
        compile_translations(loc)
    print("All locales are compiled.")


if __name__ == "__main__":
    main()
