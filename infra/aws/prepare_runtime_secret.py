"""Prepare a private JSON payload for the AWS Secrets Manager app config."""

from __future__ import annotations

import argparse
import json
import secrets
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy.engine import URL


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--db-host", required=True)
    parser.add_argument("--db-name", default="ciudad_conectada")
    args = parser.parse_args()

    values = dotenv_values(args.env_file)
    app_password = secrets.token_urlsafe(36)
    database_url = URL.create(
        "mysql+pymysql",
        username="ciudad_app",
        password=app_password,
        host=args.db_host,
        port=3306,
        database=args.db_name,
        query={"charset": "utf8mb4"},
    ).render_as_string(hide_password=False)

    payload = {
        "DATABASE_URL": database_url,
        "DB_USERNAME": "ciudad_app",
        "DB_PASSWORD": app_password,
        "ALGORITHM": values.get("ALGORITHM") or "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": values.get("ACCESS_TOKEN_EXPIRE_MINUTES") or "1440",
    }
    if values.get("GEMINI_API_KEY"):
        payload["GEMINI_API_KEY"] = values["GEMINI_API_KEY"]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload), encoding="utf-8")
    print(f"Prepared {len(payload)} runtime settings without displaying their values.")


if __name__ == "__main__":
    main()
