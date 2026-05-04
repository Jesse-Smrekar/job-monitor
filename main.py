#!/usr/bin/env python3
"""Job monitor — scrapes Glassdoor/LinkedIn/Indeed for new job postings."""

import argparse
import logging
import sys

logging.basicConfig(
    level=logging.INFO, # change this to logging.DEBUG if having issues
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Monitor job boards for new postings and send notifications.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--once",
        action="store_true",
        help="Run a single check and exit (default behavior)",
    )
    mode.add_argument(
        "--schedule",
        action="store_true",
        help="Run repeatedly on the interval defined in config.yaml",
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        metavar="PATH",
        help="Path to config file (default: config.yaml)",
    )
    args = parser.parse_args()

    from job_monitor.config import load_config
    from job_monitor.scheduler import run_check, start_scheduler

    try:
        config = load_config(args.config)
    except (FileNotFoundError, ValueError) as e:
        print(f"[!] Config error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.schedule:
        start_scheduler(config)
    else:
        run_check(config)


if __name__ == "__main__":
    main()
