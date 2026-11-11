"""Import the database and write private runtime settings on the EC2 instance."""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import subprocess
from pathlib import Path

import pymysql


def env_value(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-secret", type=Path, required=True)
    parser.add_argument("--app-secret", type=Path, required=True)
    parser.add_argument("--dump", type=Path, required=True)
    parser.add_argument("--ca", type=Path, required=True)
    parser.add_argument("--db-host", required=True)
    parser.add_argument("--env-output", type=Path, required=True)
    args = parser.parse_args()

    db_secret = json.loads(args.db_secret.read_text(encoding="utf-8"))
    app_secret = json.loads(args.app_secret.read_text(encoding="utf-8"))

    mysql_env = os.environ.copy()
    mysql_env["MYSQL_PWD"] = db_secret["password"]
    with args.dump.open("rb") as dump_file:
        result = subprocess.run(
            [
                "mysql",
                "--host", args.db_host,
                "--port", str(db_secret.get("port", 3306)),
                "--user", db_secret["username"],
                "--ssl",
                "--ssl-ca", str(args.ca),
                "--ssl-verify-server-cert",
                "--default-character-set=utf8mb4",
            ],
            stdin=dump_file,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            env=mysql_env,
            check=False,
        )
    mysql_env.pop("MYSQL_PWD", None)
    if result.returncode:
        message = result.stderr.decode("utf-8", errors="replace")
        match = re.search(r"ERROR\s+(\d+)\s+\(([A-Z0-9]+)\)\s+at line\s+(\d+)", message)
        if match:
            details = f"MySQL import failed: error {match.group(1)} ({match.group(2)}) at dump line {match.group(3)}"
        else:
            details = f"MySQL import failed with exit code {result.returncode}; see local bootstrap logs"
        raise SystemExit(details)

    username = app_secret["DB_USERNAME"]
    password = app_secret["DB_PASSWORD"]
    connection = pymysql.connect(
        host=args.db_host,
        port=3306,
        user=db_secret["username"],
        password=db_secret["password"],
        database="mysql",
        connect_timeout=15,
        ssl_ca=str(args.ca),
        ssl_verify_cert=True,
        ssl_verify_identity=True,
        autocommit=True,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute("CREATE USER IF NOT EXISTS %s@'%%' IDENTIFIED BY %s", (username, password))
            cursor.execute("ALTER USER %s@'%%' IDENTIFIED BY %s", (username, password))
            cursor.execute(
                "GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES "
                "ON ciudad_conectada.* TO %s@'%%'",
                (username,),
            )
    finally:
        connection.close()

    environment = {
        "DATABASE_URL": app_secret["DATABASE_URL"],
        "SECRET_KEY": secrets.token_urlsafe(64),
        "ALGORITHM": app_secret.get("ALGORITHM", "HS256"),
        "ACCESS_TOKEN_EXPIRE_MINUTES": app_secret.get("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"),
    }
    if app_secret.get("GEMINI_API_KEY"):
        environment["GEMINI_API_KEY"] = app_secret["GEMINI_API_KEY"]

    args.env_output.write_text(
        "".join(f"{key}={env_value(value)}\n" for key, value in environment.items()),
        encoding="utf-8",
    )
    os.chmod(args.env_output, 0o640)
    print(f"Imported database and configured {len(environment)} runtime variables.")


if __name__ == "__main__":
    main()
