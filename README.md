# Automated headless authentication to OpenShift Cluster Manager

## Installation

Installation assumes that you already have Python3 on your machine.

* Install [PDM](https://pdm-project.org/latest/#installation)
* Install python dependencies
    ```bash
    $ pdm install
    ```
* Enter the virutal environment to run the rest of the commands:
    ```bash
    $ source .venv/bin/activate
    [python3] $ playwright install chromium
    [python3] $ python3 src/ocm_login/main.py --user <username> ...
    ```

## Usage

Supports logging in with a standard username/password combination

```bash
$ python main.py --user <username> --pass <password> [--url <ocm backend api URL>]
```

Also supports logging in to OCM with a redirect to an SSO endpoint

```bash
$ python main.py --user <ocm_username> --second-user <sso_username> --pass <sso_password>
```
