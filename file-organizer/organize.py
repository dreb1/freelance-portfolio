"""Sort a messy folder into tidy subfolders by file type or by month.

Usage:
    python organize.py PATH              # sort by type (Images, Documents, ...)
    python organize.py PATH --by date    # sort into YYYY-MM folders
    python organize.py PATH --dry-run    # show what would move, change nothing
    python organize.py PATH --undo       # put everything back

Every run writes a log so it can be undone. Standard library only.
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

LOG_NAME = ".organize_log.json"

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".svg", ".bmp"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md"},
    "Spreadsheets": {".xls", ".xlsx", ".csv", ".ods"},
    "Presentations": {".ppt", ".pptx", ".key", ".odp"},
    "Audio": {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"},
    "Video": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Code": {".py", ".js", ".html", ".css", ".json", ".ts", ".sh"},
    "Installers": {".exe", ".msi", ".dmg", ".pkg"},
}


def category_for(path: Path) -> str:
    ext = path.suffix.lower()
    for name, exts in CATEGORIES.items():
        if ext in exts:
            return name
    return "Other"


def month_for(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m")


def unique_target(target: Path) -> Path:
    """Never overwrite: report.pdf -> report (1).pdf -> report (2).pdf"""
    if not target.exists():
        return target
    n = 1
    while True:
        candidate = target.with_name(f"{target.stem} ({n}){target.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def organize(folder: Path, by: str, dry_run: bool) -> int:
    files = [p for p in folder.iterdir() if p.is_file() and p.name != LOG_NAME]
    if not files:
        print("Nothing to organize.")
        return 0

    moves = []
    for f in sorted(files):
        group = category_for(f) if by == "type" else month_for(f)
        target = unique_target(folder / group / f.name)
        moves.append((f, target))

    for src, dst in moves:
        print(f"{'[dry run] ' if dry_run else ''}{src.name}  ->  {dst.relative_to(folder)}")
        if not dry_run:
            dst.parent.mkdir(exist_ok=True)
            shutil.move(str(src), str(dst))

    if not dry_run:
        # Append, so --undo can reverse several runs in a row
        log_path = folder / LOG_NAME
        log = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
        log += [{"from": str(s), "to": str(d)} for s, d in moves]
        log_path.write_text(json.dumps(log, indent=2), encoding="utf-8")

    summary = {}
    for _, dst in moves:
        summary[dst.parent.name] = summary.get(dst.parent.name, 0) + 1
    print(f"\n{'Would move' if dry_run else 'Moved'} {len(moves)} files:")
    for group, count in sorted(summary.items()):
        print(f"  {group:<14} {count}")
    return len(moves)


def undo(folder: Path) -> int:
    log_path = folder / LOG_NAME
    if not log_path.exists():
        print("No log found, nothing to undo.")
        return 0
    entries = json.loads(log_path.read_text(encoding="utf-8"))
    restored = 0
    for e in reversed(entries):
        src, dst = Path(e["to"]), Path(e["from"])
        if src.exists():
            shutil.move(str(src), str(unique_target(dst)))
            restored += 1
            if src.parent != folder and not any(src.parent.iterdir()):
                src.parent.rmdir()
    log_path.unlink()
    print(f"Restored {restored} files.")
    return restored


def main() -> None:
    ap = argparse.ArgumentParser(description="Sort a folder into subfolders.")
    ap.add_argument("folder", type=Path)
    ap.add_argument("--by", choices=["type", "date"], default="type")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--undo", action="store_true")
    args = ap.parse_args()

    if not args.folder.is_dir():
        sys.exit(f"Not a folder: {args.folder}")
    if args.undo:
        undo(args.folder)
    else:
        organize(args.folder, args.by, args.dry_run)


if __name__ == "__main__":
    main()
