import argparse
import re
import sys
from getpass import getpass

import sh
from playwright.sync_api import sync_playwright


def ocm_login():
    process = sh.ocm("login", "--use-device-code", "--url", args.ocm_url, _out=login_sso, _bg=True)
    process.wait()
    print(f"Logged in as: {sh.jq("-r", ".username", _in=sh.ocm("whoami", _piped=True))}")


def login_sso(output):
    device_code = re.search(r"([A-Z-]{9})", output).group(1)

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=True,
        args=[
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-gpu",
            "--disable-gl-drawing-for-tests",
        ],
    )
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://sso.redhat.com/device")
    page.get_by_label("Code").fill(device_code)
    page.get_by_role("button", name="Submit").click()
    page.wait_for_url("https://sso.redhat.com/auth/realms/redhat-external/login-actions/authenticate**")
    page.locator("#username-verification").fill(args.user)
    page.get_by_role("button", name="Next").click()

    # Prompt for password if not provided on command line
    if not args.password:
        args.password = getpass()

    if args.sso_url:
        page.wait_for_url(re.compile(rf"(https://)?{args.sso_url}.*"), wait_until="domcontentloaded")
        # These locators may not be the same for all SSO endpoints, PR's welcome
        page.get_by_placeholder("KERBEROS ID").fill(args.sso_user)
        page.get_by_role("textbox", name="password").fill(args.password)
        page.get_by_role("button", name="Log in").click()

    else:
        page.wait_for_url("https://sso.redhat.com/auth/realms/redhat-external/login-actions/authenticate**")
        password = page.get_by_role("textbox", name="password")
        password.wait_for()
        password.fill(args.password)
        page.get_by_role("button", name="Log in").click()

    # Assume authentication was successful, and grant access
    page.wait_for_url("https://sso.redhat.com/auth/realms/redhat-external/login-actions/required-action**")
    page.get_by_role("button", name="Grant access").click()
    browser.close()
    playwright.stop()

    # Stop processing callbacks
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated headless authentication to OpenShift Cluster Manager (OCM)")
    parser.add_argument("--user", "-u", help="OCM username", required=True)
    sso_user = parser.add_argument("--sso-user", help="SSO username (optional)")
    sso_url = parser.add_argument("--sso-url", help="SSO URL (optional), e.g., https://sso.redhat.com")
    parser.add_argument(
        "--password",
        "-p",
        "--pass",
        help="OCM password, or SSO password if --sso-user is specified. Interactively prompts for password if not supplied",
    )
    parser.add_argument("--ocm-url", "--url", default="prod", help="OCM URL, default: prod (https://api.openshift.com)")
    args = parser.parse_args()

    sso_args = [args.sso_user, args.sso_url]
    if any(sso_args) and not all(sso_args):
        parser.print_usage(sys.stderr)
        print()
        if not args.sso_user:
            raise SystemExit(argparse.ArgumentError(sso_user, "also requires --sso-url"))
        elif not args.sso_url:
            raise SystemExit(argparse.ArgumentError(sso_url, "also requires --sso-user"))

    ocm_login()
