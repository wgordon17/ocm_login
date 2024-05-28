# Automated headless authentication to OpenShift Cluster Manager

## Installation

Installation assumes that you already have Python3 on your machine.

* Install [PDM](https://pdm-project.org/latest/#installation)
* Install python dependencies
    ```bash
    $ pdm install
    ```
* Using `pdm` to run the rest of the commands:
    ```bash
    $ pdm run playwright install chromium
    $ pdm run src/ocm_login/main.py --user <username> ...
    ```

## Usage

Supports logging in with a standard username/password combination

```bash
$ pdm run src/ocm_login/main.py --user <username> --password <password> [--ocm-url https://api.openshift.com]
```

Also supports logging in to OCM with a redirect to an SSO endpoint

```bash
$ pdm run src/ocm_login/main.py -u <ocm_username> --sso-user <sso_username> --sso-url <sso-url-endpoint> -p <sso_password>
```

### Example

```bash
$ pdm run src/ocm_login/main.py --user admin.openshift --sso-user admin@redhat.com --sso-url auth.redhat.com
```

Excluding `--password` will interactively prompt the user for their password