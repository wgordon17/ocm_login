import argparse
import re

import sh
from playwright.sync_api import sync_playwright


def ocm_login():
    process = sh.ocm("login", "--use-device-code", "--url", args.url, _out=login_sso, _bg=True)
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

    if args.second_user:
        page.wait_for_url("https://auth.redhat.com/auth/realms/EmployeeIDP/login-actions/authenticate**")
        page.get_by_placeholder("KERBEROS ID").fill(args.second_user)
        page.get_by_role("textbox", name="password").fill(args.password)
        page.get_by_role("button", name="Log in").click()

    else:
        password = page.get_by_role("textbox", name="password")
        password.wait_for()
        password.fill(args.password)
        page.get_by_role("button", name="Log in").click()

    page.wait_for_url("https://sso.redhat.com/auth/realms/redhat-external/login-actions/required-action**")
    page.get_by_role("button", name="Grant access").click()
    browser.close()
    playwright.stop()

    # Stop processing callbacks
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user")
    parser.add_argument("--second-user")
    parser.add_argument("--password")
    parser.add_argument("--url", default="prod")
    args = parser.parse_args()

    ocm_login()
