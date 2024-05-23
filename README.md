# Automated headless authentication to OpenShift Cluster Manager

## Usage

Supports logging in with a standard username/password combination

```bash
$ python main.py --user <username> --pass <password> [--url <ocm backend api URL>]
```

Also supports logging in to OCM with a redirect to an SSO endpoint

```bash
$ python main.py --user <ocm_username> --second-user <sso_username> --pass <sso_password>
```
