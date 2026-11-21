"""Pre-commit check: block referral data, exports, logs and output from any commit."""

from pathlib import PurePosixPath
import subprocess
import sys

BLOCKED_DIRS = {"data", "output", "logs"}
BLOCKED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".tsv", ".accdb", ".mdb", ".db"}


def blocked(paths) -> list:
    bad = []
    for path in paths:
        p = PurePosixPath(path.replace("\\", "/"))
        if p.suffix.lower() in BLOCKED_EXTENSIONS or BLOCKED_DIRS & {part.lower() for part in p.parts[:-1]}:
            bad.append(path)
    return bad


def main():
    staged = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
                            capture_output=True, text=True, check=True).stdout.splitlines()
    bad = blocked(staged)
    if bad:
        print("Commit blocked: these files look like referral data, exports, logs or output:")
        print("\n".join("  " + p for p in bad))
        print("Unstage them with: git restore --staged <file>")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
