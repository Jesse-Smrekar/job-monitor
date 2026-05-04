from __future__ import annotations

import os
from dataclasses import dataclass

import yaml
from dotenv import load_dotenv


@dataclass
class SearchQuery:
    job_title: str
    location: str
    is_remote: bool | None  # overrides the root-level default when set


@dataclass
class SearchConfig:
    queries: list[SearchQuery]
    site_names: list[str]
    results_wanted: int
    hours_old: int
    job_type: str | None
    is_remote: bool | None  # default; overridden per-query if the query sets it
    interval_minutes: int


@dataclass
class AppConfig:
    search: SearchConfig
    db_path: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    smtp_from: str
    notify_email: str
    desktop_notify: bool
    desktop_notify_url: str
    desktop_notify_sound: bool


def load_config(config_path: str = "config.yaml") -> AppConfig:
    load_dotenv()

    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    s = raw.get("search", {})
    default_is_remote = s.get("is_remote")

    queries = []
    for q in s.get("queries", []):
        # Accept both singular and plural key names
        title = q.get("job_title") or q.get("job_titles") or ""
        location = q.get("location") or q.get("locations") or ""
        # Use query-level is_remote if explicitly present, otherwise fall back to root default
        is_remote = q["is_remote"] if "is_remote" in q else default_is_remote
        if not title or not location:
            raise ValueError(f"config.yaml: each query must have job_title and location — got {q}")
        queries.append(SearchQuery(job_title=str(title), location=str(location), is_remote=is_remote))

    if not queries:
        raise ValueError("config.yaml: search.queries must not be empty")

    search = SearchConfig(
        queries=queries,
        site_names=s.get("site_names", ["glassdoor"]),
        results_wanted=int(s.get("results_wanted", 20)),
        hours_old=int(s.get("hours_old", 24)),
        job_type=s.get("job_type") or None,
        is_remote=default_is_remote,
        interval_minutes=int(s.get("interval_minutes", 60)),
    )

    n = raw.get("notifications", {})
    notify_email = (
        n.get("notify_email")
        or os.getenv("NOTIFY_EMAIL")
        or ""
    )

    db_path = raw.get("database", {}).get("db_path", "seen_jobs.db")

    return AppConfig(
        search=search,
        db_path=db_path,
        smtp_host=os.getenv("SMTP_HOST", ""),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        smtp_from=os.getenv("SMTP_FROM", ""),
        notify_email=notify_email,
        desktop_notify=bool(n.get("desktop_notify", True)),
        desktop_notify_url=n.get("desktop_notify_url", ""),
        desktop_notify_sound=n.get("desktop_notify_sound", "Default"),
    )
