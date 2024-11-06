import pdfplumber
from tabulate import tabulate
import re

class AssetsLiabilitiesExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        # Simplified and more specific rows to match the actual PDFs
        self.rows_to_extract = {
            'assets': [
                'total non-current assets', 'total non current assets',
                'total current assets',
                'total assets'
            ],
            'liabilities': [
                'total non-current liabilities', 'total non current liabilities',
                'total current liabilities',
                'total liabilities'
            ],
            'equity': [
                'total equity'
            ]
        }
        self.headers = []
        # Modified number pattern to better match the format in the PDFs
        self.number_pattern = re.compile(r'-?\d{1,3}(?:,\d{3})*(?:\.\d{2})?')
        
    def extract_numbers(self, text):
        """Extract numbers from text, handling the specific format in the PDFs."""
        matches = self.number_pattern.findall(text)
        return [float(num.replace(',', '')) for num in matches if num]

    def find_table_start(self, lines):
        """Find where the actual table starts in the PDF."""
        for i, line in enumerate(lines):
            # Look for key identifiers that appear in the provided PDFs
            if any(identifier in line.lower() for identifier in [
                'as at', 'assets', 'non-current assets', 'particulars'
            ]):
                return i
        return 0

    def extract_headers(self, lines, start_idx):
        """Extract headers from the table."""
        headers = ['Particulars']
        # Look for date patterns in nearby lines
        for i in range(start_idx, min(start_idx + 5, len(lines))):
            line = lines[i]
            if 'march' in line.lower() or 'june' in line.lower():
                # Extract years using regex
                years = re.findall(r'\b20\d{2}\b', line)
                headers.extend([f'March {year}' for year in years])
                if headers:
                    return headers
        return headers

    def extract_assets_liabilities(self):
        table_data = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                lines = text.splitlines()
                table_start = self.find_table_start(lines)
                
                if not self.headers:
                    self.headers = self.extract_headers(lines, table_start)
                
                # Process each line after table start
                for line in lines[table_start:]:
                    line_lower = line.lower().strip()
                    
                    # Match any of our target rows
                    for section, patterns in self.rows_to_extract.items():
                        for pattern in patterns:
                            if pattern in line_lower:
                                numbers = self.extract_numbers(line)
                                if numbers:
                                    row_data = [pattern.title()]
                                    row_data.extend(numbers)
                                    if not any(r[0] == row_data[0] for r in table_data):
                                        table_data.append(row_data)
                                break

        # Calculate DOE if we have the necessary data
        if table_data:
            self.add_doe_calculation(table_data)

        # Format and return the table
        if table_data and self.headers:
            return tabulate(table_data, headers=self.headers, tablefmt="grid", floatfmt=".2f")
        return "Could not identify the required table or data in the PDF."

    def add_doe_calculation(self, table_data):
        """Calculate and add Debt over Equity ratio."""
        total_liabilities = None
        total_equity = None
        
        for row in table_data:
            if 'Total Liabilities' in row[0]:
                total_liabilities = row[1:]
            elif 'Total Equity' in row[0]:
                total_equity = row[1:]
        
        if total_liabilities and total_equity:
            doe_row = ["DOE (Debt/Equity Ratio)"]
            for liab, eq in zip(total_liabilities, total_equity):
                try:
                    doe = float(liab) / float(eq) if float(eq) != 0 else 0
                    doe_row.append(doe)
                except (ValueError, ZeroDivisionError):
                    doe_row.append(0)
            table_data.append(doe_row)

def extract_assets_liabilities(pdf_path):
    """Main function to extract assets and liabilities from PDF."""
    extractor = AssetsLiabilitiesExtractor(pdf_path)
    return extractor.extract_assets_liabilities()