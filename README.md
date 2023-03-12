# <h1 align="center">tableau-datasource-refresher</h1>

**This python code uses a headless Selenium browser to request a data refresh on a Tableau Public dashboard.**

[![Tests](https://github.com/gibz104/tableau-datasource-refresher/actions/workflows/tests.yaml/badge.svg)](https://github.com/gibz104/tableau-datasource-refresher/actions/workflows/tests.yaml)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/gibz104/465cb74d7d8ba19a655fba50d0ce3665/raw/covbadge-tableau-datasource-refresher.json)](https://github.com/gibz104/tableau-datasource-refresher/actions/workflows/tests.yaml)
[![Py Versions](https://img.shields.io/badge/python-3.8_|_3.9_|_3.10-blue.svg)](https://www.python.org/downloads/)
[![Test OS](https://img.shields.io/badge/tested_on-ubuntu_|_mac_os_|_windows-blue.svg)](https://github.com/gibz104/google-sheets-writer/actions/workflows/tests.yaml)

# Background

Tableau Public allows you to create and publish dashboards for free that can be accessed by anyone online.  There is no authetication (or cost) for the number of users that view your dashboard, nor the resources to host and maintain the dashboard.  The catch is that Tableau Public only allows you to connect to a very limited subset of data sources and they cannot be setup to be refreshed on a schedule.  

However, there is a button on the Tableau Public UI that allows you to manually trigger a refresh for the data source the workbook is connected to.  The purpose of this repository was to create a program that uses a headless Selenium browser to login as the owner of a dashboard and click this UI button that will trigger a data source refresh.  The idea is you can schedule this program to run on a set schedule (say every hour) to trigger a refresh to the dashboard without requiring any orchestration/scheduling on the Tableau Public side.

# Usage

#### Instantiate the TableauPublic class

- `username` parameter should be the __username__ of the dashboard owner

- `password` parameter should be the __password__ of the dashboard owner

```python
tableau = TableauPublic(
    username='username',
    password='password',
    headless=True,
)
```

#### Next call the `refresh_datasource` method by passing the url endpoint of the dashboard you want refreshed.  When this method is called, Selenium will log you into Tableau Public with the provided username/password and then refresh the dashboard's data source.

```python
tableau.refresh_datasource('/app/profile/user/viz/dashboardname')
```

# Tests
Basic unittests are in place in the `/tests` directory which can be run locally using `pytest`.  There is also a github workflow associated with this repo that will run the tests and report the code coverage on every push (https://github.com/gibz104/tableau-datasource-refresher/actions/workflows/tests.yaml).

Tests have been run on python versions 3.8, 3.9, and 3.10 on Ubuntu, Mac OS, and Windows.  Testing status and coverage are reported as badges at the top of this readme.

# Disclaimer
Run this code at your own risk.
