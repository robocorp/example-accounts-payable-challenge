import convert
import extract
import logging
import os
import sys
from RPA.Archive import Archive
from RPA.Browser.Selenium import Selenium
from RPA.Cloud.AWS import AWS
from RPA.FileSystem import FileSystem
from RPA.HTTP import HTTP

browser_lib = Selenium()

INVOICING_WEB_APP_URL = "https://developer.automationanywhere.com/challenges/automationanywherelabs-invoiceentry.html"
OUTPUT_DIR = f"{os.getcwd()}/output"
INVOICES_ZIP_PATH = f"{OUTPUT_DIR}/invoices.zip"


def complete_accounts_payable_challenge():
    open_integrated_invoicing_solution(INVOICING_WEB_APP_URL)
    download_invoices(get_invoices_zip_url(), INVOICES_ZIP_PATH)
    invoice_files = extract_invoice_files(INVOICES_ZIP_PATH, OUTPUT_DIR)
    invoice_files = convert.to_jpeg(invoice_files, OUTPUT_DIR)
    submit_invoices(invoice_files)
    take_screenshot_of_results()


def open_integrated_invoicing_solution(url):
    browser_lib.open_chrome_browser("about:blank")
    override_user_agent("Chrome/92.0.4515.159")
    browser_lib.go_to(url)


def override_user_agent(user_agent):
    parameters = {"userAgent": user_agent}
    browser_lib.execute_cdp("Network.setUserAgentOverride", parameters)


def get_invoices_zip_url():
    locator = "css:p.lead a"
    browser_lib.wait_until_element_is_visible(locator)
    return browser_lib.get_element_attribute(locator, "href")


def download_invoices(url, target_file):
    HTTP().download(url, target_file, overwrite=True)


def extract_invoice_files(path, output_dir):
    Archive().extract_archive(path, output_dir)
    return FileSystem().find_files(f"{output_dir}/*.tiff")


def submit_invoices(invoice_files):
    aws_lib = AWS(region="us-east-1", robocloud_vault_name="aws")
    aws_lib.init_textract_client(use_robocloud_vault=True)
    for invoice_file in invoice_files:
        invoice_data = extract.extract_invoice_data(aws_lib, invoice_file)
        fill_in_invoice_details(invoice_data)
        upload_invoice_file(invoice_file)
        agree_to_terms()
        submit_invoice()


def fill_in_invoice_details(invoice_data):
    fields = invoice_data["fields"]
    invoice_number = get_field("Invoice no.", fields)
    invoice_date = get_field("Invoice Date", fields)
    invoice_total = get_field("Invoice Amount", fields)
    browser_lib.click_button("css:.btn-reset")
    browser_lib.input_text("id:invoiceNumber", invoice_number)
    browser_lib.input_text("id:invoiceDate", invoice_date)
    browser_lib.input_text("id:invoiceTotal", invoice_total)
    fill_in_invoice_rows(invoice_data)


def get_field(key, fields):
    for field in fields:
        if field.key.text == key:
            return strip_value(field.value.text)
    return None


def strip_value(value):
    return value.strip().replace("$ ", "").replace(",", "")


def fill_in_invoice_rows(invoice_data):
    for table in invoice_data["tables"]:
        for index, row in enumerate(table.rows):
            if len(row.cells) < 3 or not row.cells[0].text or index < 1:
                continue
            add_invoice_row(index)
            quantity = strip_value(row.cells[0].text)
            description = strip_value(row.cells[2].text)
            total_price = strip_value(row.cells[-1].text)
            browser_lib.input_text(f"id:quantity_row_{index}", quantity)
            browser_lib.input_text(f"id:description_row_{index}", description)
            browser_lib.input_text(f"id:price_row_{index}", total_price)


def add_invoice_row(index):
    if index != 1:
        browser_lib.click_button("css:#myDIV button")


def upload_invoice_file(file):
    browser_lib.choose_file("id:fileupload", file.path.replace("jpeg", "tiff"))


def agree_to_terms():
    browser_lib.select_radio_button("termsRadios", "option1")


def submit_invoice():
    browser_lib.click_button("id:submit_button")


def take_screenshot_of_results():
    browser_lib.wait_until_element_is_visible("css:.modal-confirm")
    browser_lib.screenshot(filename="output/result.png")


def initialize_logging():
    stdout = logging.StreamHandler(sys.stdout)

    logging.basicConfig(
        level=logging.ERROR,
        format="{%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        handlers=[stdout]
    )


if __name__ == "__main__":
    initialize_logging()
    complete_accounts_payable_challenge()
