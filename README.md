# A robot that completes the accounts payable challenge

This example robot completes the accounts payable challenge at https://developer.automationanywhere.com/challenges/automationanywherelabs-invoiceentry.html.

The challenge involves reading invoice images programmatically and entering the data into a web application.

This robot is written in Python. It uses Python standard libraries and some [RPA Framework](https://rpaframework.org/) libraries.

[Amazon Textract](https://aws.amazon.com/textract/) is used for extracting data from the invoice images.

Here is the main "task" definition:

```py
def complete_accounts_payable_challenge():
    open_integrated_invoicing_solution(INVOICING_WEB_APP_URL)
    download_invoices(get_invoices_zip_url(), INVOICES_ZIP_PATH)
    invoice_files = extract_invoice_files(INVOICES_ZIP_PATH, OUTPUT_DIR)
    invoice_files = convert.to_jpeg(invoice_files, OUTPUT_DIR)
    submit_invoices(invoice_files)
    take_screenshot_of_results()
```

> See the full code for implementation details!
