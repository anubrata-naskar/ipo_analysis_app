import pdfplumber
import re
from tabulate import tabulate

class FinancialDataExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        # Define keywords to identify relevant rows
        self.keywords = ["total income", "total expenses", "comprehensive loss", "comprehensive profit", "loss per equity share"]
        # Adjusted pattern for numeric values to detect numbers with optional commas and decimals
        self.number_pattern = re.compile(r"\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b")
        self.headers = ["Label", "Value-1", "Value-2", "Value-3", "Value-4", "Value-5"]

    def is_table_start(self, line):
        """Check if this line indicates the start of the profit and loss table."""
        return any(keyword in line.lower() for keyword in ["particulars", "income", "expenses", "profit", "loss", "ended"])

    def extract_financial_data(self):
        table_data = []
        found_header = False
        processing_table = False

        with pdfplumber.open(self.pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages):
                text = page.extract_text()
                lines = text.splitlines()

                for line in lines:
                    print(f"Processing line: {line}")

                    # Look for the main section header
                    if any(header in line.lower() for header in ["statement of profit and loss", "profit and loss statement", "comprehensive income"]):
                        found_header = True
                        print(f"Found header on page {page_number + 1}: {line}")
                        continue

                    # If we found the header, look for the table start
                    if found_header and not processing_table:
                        if self.is_table_start(line):
                            processing_table = True
                            print(f"Found table start on page {page_number + 1}: {line}")
                            continue

                    # If we're processing the table, look for keywords
                    if processing_table:
                        for keyword in self.keywords:
                            if keyword in line.lower():
                                print(f"Matching keyword '{keyword}' found in line: {line}")
                                
                                # Extract all numeric values matching the pattern
                                values = [float(num.replace(',', '')) for num in self.number_pattern.findall(line)]
                                
                                if values:
                                    # Prepare row data with label and extracted values
                                    row_data = [keyword.capitalize()] + values

                                    # Ensure row has exactly 6 columns; pad with empty strings if fewer values
                                    while len(row_data) < 6:
                                        row_data.append("")

                                    table_data.append(row_data)
                                    print(f"Added row for {keyword.capitalize()}: {row_data}")
                                    break
                                else:
                                    print(f"No numeric data found in line: {line}")

                # Stop after processing the table
                if processing_table and table_data:
                    break

        if table_data:
            return tabulate(table_data, headers=self.headers, tablefmt="grid")
        else:
            print("No matching rows were found after processing all pages.")
            return "The required rows were not found in the specified table."

# Usage example
def extract_financial_data(pdf_path):
    extractor = FinancialDataExtractor(pdf_path)
    return extractor.extract_financial_data()
