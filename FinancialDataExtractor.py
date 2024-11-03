import pdfplumber
import re
from tabulate import tabulate

class FinancialDataExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        # Define specific rows to extract with display labels
        self.rows_to_extract = {
            "Total income": "Total income",
            "Total expenses": "Total expenses",
            "Total comprehensive loss for the period/year, net of tax": "Total comprehensive loss",
            "Total comprehensive profit for the period/year, net of tax": "Total comprehensive profit",
            "Loss per equity share - Basic and Diluted": "Loss per equity share"
        }
        # Define a pattern to match large numbers with commas and decimals correctly
        self.number_pattern = re.compile(r"\b\d{1,3}(?:,\d{3})*\.\d{2}\b")
        self.headers = ["Column-0", "Column-1", "Column-2", "Column-3", "Column-4", "Column-5"]

    def is_table_start(self, line):
        """Check if this line indicates the start of the actual financial table."""
        # You might need to adjust these conditions based on your PDF structure
        return (
            "Particulars" in line 
            and any(word in line.lower() for word in ["year", "period", "ended", "month"])
        )

    def is_numeric_row(self, line):
        """Check if the line contains numeric data."""
        return bool(self.number_pattern.search(line))

    def extract_financial_data(self):
        table_data = []
        found_header = False
        processing_table = False

        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                lines = text.splitlines()
                
                for line in lines:
                    # Look for the section header
                    if "Restated Consolidated Statement of Profit and Loss" in line:
                        found_header = True
                        continue

                    # If we found the header, look for the table start
                    if found_header and not processing_table:
                        if self.is_table_start(line):
                            processing_table = True
                            continue

                    # If we're processing the table, look for our target rows
                    if processing_table:
                        for row_label, display_label in self.rows_to_extract.items():
                            if row_label in line and self.is_numeric_row(line):
                                # Extract values starting after the row label
                                label_end = line.find(row_label) + len(row_label)
                                data_part = line[label_end:].strip()

                                # Extract all numeric values matching the pattern, removing commas
                                values = [float(num.replace(',', '')) for num in self.number_pattern.findall(data_part)]
                                
                                # Prepare row data with label and extracted values
                                row_data = [display_label] + values
                                
                                # Ensure row has exactly 6 columns; pad with empty strings if fewer values
                                while len(row_data) < 6:
                                    row_data.append("")

                                table_data.append(row_data)
                                break

                # If we've found and processed the table, we can stop
                if processing_table and table_data:
                    break

        # Return data in a formatted table or an error message
        if table_data:
            return tabulate(table_data, headers=self.headers, tablefmt="grid")
        else:
            return "The required rows were not found in the specified table."

# Usage example
def extract_financial_data(pdf_path):
    extractor = FinancialDataExtractor(pdf_path)
    return extractor.extract_financial_data()