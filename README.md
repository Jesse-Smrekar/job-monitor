# Job Monitor

A tool to periodically query the top job boards for new posting that
match given criteria. Leverages [jobspy](https://pypi.org/project/python-jobspy/) (via chromium) to scrape data from the sites and bypass bot detection. It stores unique results into a local sqlite db and will send email and desktop (Windows only so far) notifications for new postings.

---

## Setup

```sh
# Install dependencies
pip install -r requirements.txt

# Install Chromium for Glassdoor scraping
playwright install chromium

# Set up your secrets
cp .env.example .env
# Edit .env — fill in your email smtp server and credential details.

```

---

# Run

```sh
# run a manual check once
python main.py
python main.py --once

# Run on a schedule (every <interval_minutes> from config.yaml)
python main.py --schedule

# Use a different config file
python main.py --config my_other_search.yaml
```

<img src=./docs/email_notification.jpg>

---

## Notes

Currently it looks like there is a bug in the Glassdoor request logic. Was able to get it working by manually making the changes in these two PRs: [JobSpy PR#350](https://github.com/speedyapply/JobSpy/pull/350/changes) & [JobSpy PR#347](https://github.com/speedyapply/JobSpy/pull/347)