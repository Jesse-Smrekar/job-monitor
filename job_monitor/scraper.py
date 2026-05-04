from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd

from .config import SearchConfig, SearchQuery

logger = logging.getLogger(__name__)


@dataclass
class JobPosting:
    job_id: str
    title: str
    company: str
    location: str
    date_posted: str
    job_url: str
    site: str


def scrape_jobs(config: SearchConfig) -> list[JobPosting]:
    from jobspy import scrape_jobs as _scrape  # imported here to keep startup fast

    all_jobs: dict[str, JobPosting] = {}

    for query in config.queries:
        params = dict(
            site_name=config.site_names,
            search_term=query.job_title,
            location=query.location,
            results_wanted=config.results_wanted,
            hours_old=config.hours_old,
            job_type=config.job_type,
            is_remote=query.is_remote,
        )
        logger.debug("jobspy params: %s", params)
        try:
            df = _scrape(**params, verbose=2)
            postings = _normalize(df)
            for p in postings:
                all_jobs.setdefault(p.job_id, p)
            logger.info("Scraped %d jobs for '%s' in '%s'", len(postings), query.job_title, query.location)
        except Exception:
            logger.exception("Failed to scrape '%s' in '%s'", query.job_title, query.location)

    return list(all_jobs.values())


def _normalize(df: pd.DataFrame) -> list[JobPosting]:
    if df is None or df.empty:
        return []

    df = df.where(pd.notna(df), None)
    postings = []

    for _, row in df.iterrows():
        raw_id = row.get("id") or row.get("job_id")
        url = row.get("job_url") or row.get("job_url_direct")
        site = str(row.get("site") or "unknown").lower()

        if not raw_id or not url:
            continue

        job_id = f"{site}::{raw_id}"

        postings.append(JobPosting(
            job_id=job_id,
            title=str(row.get("title") or ""),
            company=str(row.get("company") or ""),
            location=str(row.get("location") or ""),
            date_posted=_format_date(row.get("date_posted")),
            job_url=str(url),
            site=site,
        ))

    return postings


def _format_date(value) -> str:
    if value is None:
        return ""
    try:
        if hasattr(value, "strftime"):
            return value.strftime("%Y-%m-%d")
        return str(value)[:10]
    except Exception:
        return ""
