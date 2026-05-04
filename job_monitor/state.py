from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from .scraper import JobPosting

_DDL = """
CREATE TABLE IF NOT EXISTS seen_jobs (
    job_id      TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    company     TEXT,
    location    TEXT,
    date_posted TEXT,
    job_url     TEXT NOT NULL,
    site        TEXT,
    first_seen  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_first_seen ON seen_jobs(first_seen);
CREATE INDEX IF NOT EXISTS idx_site ON seen_jobs(site);
"""


def init_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.executescript(_DDL)
    conn.commit()
    return conn


def filter_new_jobs(conn: sqlite3.Connection, jobs: list[JobPosting]) -> list[JobPosting]:
    if not jobs:
        return []

    placeholders = ",".join("?" * len(jobs))
    ids = [j.job_id for j in jobs]
    rows = conn.execute(
        f"SELECT job_id FROM seen_jobs WHERE job_id IN ({placeholders})", ids
    ).fetchall()
    seen = {r[0] for r in rows}
    return [j for j in jobs if j.job_id not in seen]


def record_jobs(conn: sqlite3.Connection, jobs: list[JobPosting]) -> None:
    if not jobs:
        return

    now = datetime.now(timezone.utc).isoformat()
    conn.executemany(
        """
        INSERT OR IGNORE INTO seen_jobs
            (job_id, title, company, location, date_posted, job_url, site, first_seen)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (j.job_id, j.title, j.company, j.location, j.date_posted, j.job_url, j.site, now)
            for j in jobs
        ],
    )
    conn.commit()
