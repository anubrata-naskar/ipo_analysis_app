import pdfplumber
from tabulate import tabulate
import re

class AssetsLiabilitiesExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.rows_to_extract = [
            "Total non-current assets",
            "Total current assets",
            "Total assets",
            "Total liabilities"
        ]
        self.headers = []
        # Enhanced number pattern to match different number formats
        self.number_pattern = re.compile(r"-?\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b")
        # Different possible table identifiers
        self.table_identifiers = [
            "Restated Consolidated Statement of Assets and Liabilities",
            "Statement of Assets and Liabilities",
            "ASSETS AND LIABILITIES"
        ]

    def is_table_header(self, line):
        """Check if line contains table headers with date information."""
        date_patterns = [
            r"(?:As at|as at|As of|as of).*(?:March|September|June|December).*\d{4}",
            r"\d{2}(?:th|st|nd|rd)?\s+(?:March|September|June|December).*\d{4}"
        ]
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in date_patterns)

    def is_table_identifier(self, line):
        """Check if line contains any of the table identifiers."""
        return any(identifier.lower() in line.lower() for identifier in self.table_identifiers)

    def extract_numbers(self, text):
        """Extract numbers from text, handling commas and decimals."""
        numbers = self.number_pattern.findall(text)
        return [float(num.replace(',', '')) for num in numbers]

    def clean_header(self, header):
        """Clean and standardize header text."""
        return re.sub(r'\s+', ' ', header).strip()

    def extract_date_headers(self, text):
        """Extract date-based headers from text."""
        headers = ["Particulars"]
        # Match patterns like "As at 31st March, 2024" or "31 March 2023"
        date_pattern = r"(?:As at|as at|As of|as of)?\s*\d{2}(?:th|st|nd|rd)?\s+(?:March|September|June|December)[,\s]+\d{4}"
        matches = re.finditer(date_pattern, text, re.IGNORECASE)
        for match in matches:
            headers.append(self.clean_header(match.group()))
        return headers

    def calculate_doe(self, total_assets_row, total_liabilities_row):
        """Calculate DOE for each column (Total Liabilities / Total Assets)."""
        doe_row = ["DOE"]
        
        # Start from index 1 to skip the "Particulars" column
        for i in range(1, len(self.headers)):
            try:
                assets = float(total_assets_row[i]) if total_assets_row[i] != "" else 0
                liabilities = float(total_liabilities_row[i]) if total_liabilities_row[i] != "" else 0
                
                if assets != 0:  # Avoid division by zero
                    doe = liabilities / assets
                    doe_row.append(f"{doe:.2f}")
                else:
                    doe_row.append("")
            except (ValueError, IndexError):
                doe_row.append("")
        
        return doe_row

    def extract_assets_liabilities(self):
        table_data = []
        found_table = False
        current_section = None

        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                lines = text.splitlines()
                
                for line_num, line in enumerate(lines):
                    # Look for table identifier
                    if not found_table and self.is_table_identifier(line):
                        found_table = True
                        # Look for headers in next few lines
                        for i in range(line_num, min(line_num + 5, len(lines))):
                            if self.is_table_header(lines[i]):
                                self.headers = self.extract_date_headers(lines[i])
                                break
                        continue

                    if found_table:
                        # Track current section
                        if "ASSETS" in line or "Assets" in line:
                            current_section = "ASSETS"
                        elif "LIABILITIES" in line or "Liabilities" in line:
                            current_section = "LIABILITIES"

                        # Look for target rows
                        for target_row in self.rows_to_extract:
                            if target_row.lower() in line.lower():
                                numbers = self.extract_numbers(line)
                                if numbers:  # Only process if we found numbers
                                    row_data = [target_row] + numbers
                                    # Pad row to match header length
                                    while len(row_data) < len(self.headers):
                                        row_data.append("")
                                    table_data.append(row_data)

                # Calculate DOE if we have both total assets and total liabilities
                total_assets_row = None
                total_liabilities_row = None
                
                for row in table_data:
                    if "Total assets" in row[0]:
                        total_assets_row = row
                    elif "Total liabilities" in row[0]:
                        total_liabilities_row = row
                
                if total_assets_row and total_liabilities_row:
                    doe_row = self.calculate_doe(total_assets_row, total_liabilities_row)
                    # Only add DOE row if it's not already in table_data
                    if not any("DOE" in row[0] for row in table_data):
                        table_data.append(doe_row)
                    break

        # Return formatted table or error message
        if table_data and self.headers:
            return tabulate(table_data, headers=self.headers, tablefmt="grid")
        else:
            return "The required rows were not found in the specified table."

# Usage example
def extract_assets_liabilities(pdf_path):
    extractor = AssetsLiabilitiesExtractor(pdf_path)
    return extractor.extract_assets_liabilities()