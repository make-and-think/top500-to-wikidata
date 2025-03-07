#!/usr/bin/env python3
import os
import textwrap
import csv
import xlrd
from datetime import datetime
import mechanize as mech
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Credentials from .env ---
TOP500_USERNAME = os.environ.get("TOP500_USERNAME")
TOP500_PASSWORD = os.environ.get("TOP500_PASSWORD")
# --- End Credentials ---

# Check if credentials are set
if not TOP500_USERNAME or not TOP500_PASSWORD:
    raise EnvironmentError(
        "Please set TOP500_USERNAME and TOP500_PASSWORD environment variables, "
        "preferably in a .env file in the same directory as the script."
    )


def login_to_top500():
    """Logs into top500.org using credentials from environment variables."""
    print("Logging into top500.org ...")
    br = mech.Browser()
    br.open('https://www.top500.org/accounts/login?next=/')
    login_form = [f for f in br.forms() if 'login' in f.action][0]
    br.form = login_form
    br['login'] = TOP500_USERNAME
    br['password'] = TOP500_PASSWORD
    br.submit()
    if 'login' in br.geturl():
        raise RuntimeError('Login failed')
    print("Success.")
    return br


def download_xls_files(browser):
    """Downloads missing TOP500 XLS files from top500.org."""
    print("Downloading TOP500 XLS files...")
    now = datetime.now()
    xls_files = []
    url_template = 'https://www.top500.org/lists/top500/{0:04d}/{1:02d}/download/TOP500_{0:04d}{1:02d}.{2:s}'

    for year in range(1993, now.year + 1):
        for month in (6, 11):
            if (year, month) > (now.year, now.month):
                break
            ext = 'xlsx' if year >= 2020 else 'xls'
            url = url_template.format(year, month, ext)
            filename = os.path.basename(url)

            if os.path.exists(filename):
                print(f"{filename} exists, skipping.")
                xls_files.append((year, month, filename))
            else:
                print(f"Fetching {filename}...")
                try:
                    browser.retrieve(url, filename)
                    xls_files.append((year, month, filename))
                except mech.HTTPError as e:
                    print(f"Error downloading {filename}: {e}")
    print("Download process finished.")
    return xls_files


def reconcile_headers(xls_files):
    """Reconciles headers from all downloaded XLS files, identifying changes."""
    print("Reconciling headers from XLS files...")
    all_headers = ['Year', 'Month', 'Day']
    last_headers = []
    headers_to_rename = {  # Typos and inconsistencies in header names
        'Rmax': 'RMax',
        'Rpeak': 'RPeak',
        'Effeciency (%)': 'Efficiency (%)',
        'Proc. Frequency': 'Processor Speed (MHz)',
        'Cores': 'Total Cores',
        'Power Effeciency [GFlops/Watts]': 'Power Efficiency [GFlops/Watts]',
    }

    for year, month, filename in xls_files:
        try:
            workbook = xlrd.open_workbook(filename, logfile=open(os.devnull, 'w'))
            sheet = workbook.sheets()[0]
            for row_index in range(sheet.nrows):
                row = sheet.row_values(row_index)
                if any(row):  # Skip blank rows
                    renamed_headers = {}
                    headers = [
                        renamed_headers.setdefault(h, headers_to_rename[h]) if h in headers_to_rename else h
                        for h in row
                    ]
                    new_headers = [h for h in headers if h not in all_headers]
                    drop_headers = [h for h in last_headers if h not in headers]

                    if new_headers or drop_headers or renamed_headers:
                        print(f"{year}/{month}:")
                        if renamed_headers:
                            print(textwrap.fill(
                                "Renamed headers: " + ', '.join('%s to %s' % kv for kv in renamed_headers.items()),
                                initial_indent='  ', subsequent_indent='    '))
                        if new_headers:
                            print(textwrap.fill(
                                "New headers: " + ', '.join(new_headers),
                                initial_indent='  ', subsequent_indent='    '))
                        if drop_headers:
                            print(textwrap.fill(
                                "Dropped headers: " + ', '.join(drop_headers),
                                initial_indent='  ', subsequent_indent='    '))

                    all_headers.extend(new_headers)
                    last_headers = headers
                    break  # Headers are usually in the first non-empty row
            workbook.release_resources()
            del workbook, sheet
        except xlrd.XLRDError as e:
            print(f"Error processing {filename}: {e}")

    print("Header reconciliation complete.")
    return all_headers, headers_to_rename


def build_csv_table(xls_files, all_headers, headers_to_rename):
    """Builds a complete CSV table from XLS files using reconciled headers."""
    print("Building complete TOP500_history.csv...")

    with open("TOP500_history.csv", "w", newline='') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=all_headers)
        csv_writer.writeheader()

        for year, month, filename in xls_files:
            try:
                workbook = xlrd.open_workbook(filename, logfile=open(os.devnull, 'w'))
                sheet = workbook.sheets()[0]
                headers = None
                for row_index in range(sheet.nrows):
                    row = sheet.row_values(row_index)
                    if any(row):  # Skip blank lines
                        if headers is None:
                            headers = [headers_to_rename.get(h, h) for h in row]
                        else:
                            row_data = dict(zip(headers, row))
                            row_data.update({'Year': year, 'Month': month, 'Day': 1})
                            csv_writer.writerow(row_data)
                workbook.release_resources()
                del workbook, sheet
            except xlrd.XLRDError as e:
                print(f"Error processing {filename}: {e}")

    print("CSV table building complete: TOP500_history.csv")


def main():
    """Main function to download TOP500 data and create a CSV history file."""
    try:
        browser = login_to_top500()
        xls_files = download_xls_files(browser)
        all_headers, headers_to_rename = reconcile_headers(xls_files)
        build_csv_table(xls_files, all_headers, headers_to_rename)
        print("Done.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
