def extract_invoice_data(aws_lib, invoice_file):
    model = aws_lib.analyze_document(
        invoice_file, f"{invoice_file}.json", model=True)
    for page in model.pages:
        fields = page.form.fields
        tables = page.tables
    return {"fields": fields, "tables": tables}
