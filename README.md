# Job Monitor

A tool to periodically query the top job boards for new posting that
match given criteria. Leverages [jobspy](https://pypi.org/project/python-jobspy/) (via chromium) to scrape data from the sites and bypass bot detection. It stores unique results into a local sqlite db and will send email and desktop (Windows only so far) notifications for new postings.

---

## Setup

#### Step 1
```sh
# Install dependencies
# will require the VS C++ build tools
pip install -r requirements.txt

# Install Chromium for Glassdoor scraping
# You may need to add the python scripts dir to your path
playwright install chromium

# Set up your secrets
cp .env.example .env
# Edit .env — fill in your email smtp server and credential details.

```

#### Step 2
Configure your search criteria in [config.yaml](./config.yaml).\
You'll want to look through all of the properties listed here and tweak them as you wish. The file comments should hopefully make the meaning of each property clear.

Each separate entry under `search.queries` will result in a different search to each of job boards.

**PLEASE** change the `notifications.notify_email` property so I don't get spammed :)





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

<img src=./docs/email_notification.JPG>

---

## Notes

Currently it looks like there is a bug in the Glassdoor request logic. Was able to get it working by manually making the changes in these two PRs: [JobSpy PR#350](https://github.com/speedyapply/JobSpy/pull/350/changes) & [JobSpy PR#347](https://github.com/speedyapply/JobSpy/pull/347)
