"""Create a MySQL dump without printing local database credentials or rows."""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy.engine import make_url


def option_value(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "") + '"'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mysqldump", type=Path, required=True)
    args = parser.parse_args()

    values = dotenv_values(args.env_file)
    raw_url = values.get("DATABASE_URL")
    if not raw_url:
        raise SystemExit("DATABASE_URL is missing")
    url = make_url(raw_url)
    if not all((url.host, url.username, url.password, url.database)):
        raise SystemExit("DATABASE_URL is missing a required connection field")

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".cnf", delete=False) as f:
        option_file = Path(f.name)
        f.write("[client]\n")
        f.write(f"host={option_value(url.host)}\n")
        f.write(f"port={url.port or 3306}\n")
        f.write(f"user={option_value(url.username)}\n")
        f.write(f"password={option_value(url.password)}\n")

    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("wb") as dump_file:
            result = subprocess.run(
                [
                    str(args.mysqldump),
                    f"--defaults-extra-file={option_file}",
                    "--single-transaction",
                    "--quick",
                    "--routines",
                    "--triggers",
                    "--events",
                    "--no-tablespaces",
                    "--set-gtid-purged=OFF",
                    "--databases",
                    url.database,
                ],
                stdout=dump_file,
                stderr=subprocess.PIPE,
                check=False,
            )
        if result.returncode:
            args.output.unlink(missing_ok=True)
            raise SystemExit(f"mysqldump failed with exit code {result.returncode}")
    finally:
        option_file.unlink(missing_ok=True)

    print(f"Database dump created; size={args.output.stat().st_size} bytes.")


if __name__ == "__main__":
    main()
