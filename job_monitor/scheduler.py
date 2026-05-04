from __future__ import annotations

import logging

from .config import AppConfig
from .notifier import notify
from .scraper import scrape_jobs
from .state import filter_new_jobs, init_db, record_jobs

logger = logging.getLogger(__name__)


def run_check(config: AppConfig) -> None:
    logger.info("Starting job check...")
    jobs = scrape_jobs(config.search)
    logger.info("Found %d total postings", len(jobs))

    # Open a fresh connection per invocation so scheduler threads don't share one
    conn = init_db(config.db_path)
    try:
        new_jobs = filter_new_jobs(conn, jobs)
        logger.info("%d new posting(s) since last check", len(new_jobs))

        if new_jobs:
            notify(config, new_jobs)
            record_jobs(conn, new_jobs)
            print(f"[+] {len(new_jobs)} new job(s) found:")
            for j in new_jobs:
                print(f"    {j.title} @ {j.company} ({j.location}) — {j.job_url}")
        else:
            print("[-] No new jobs found.")
    finally:
        conn.close()


def start_scheduler(config: AppConfig) -> None:
    import signal
    import sys
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.interval import IntervalTrigger

    scheduler = BlockingScheduler()

    def _shutdown(signum, frame):
        print("\n[*] Shutting down...")
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    minutes = config.search.interval_minutes
    scheduler.add_job(
        run_check,
        trigger=IntervalTrigger(minutes=minutes),
        args=[config],
        next_run_time=__import__("datetime").datetime.now(),
    )
    print(f"[*] Scheduler started — checking every {minutes} minute(s). Press Ctrl+C to stop.")
    scheduler.start()
