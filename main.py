import tkinter as tk
from tkinter import Label, Toplevel
from PIL import Image, ImageTk
import pdfplumber
import pandas as pd
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from FinancialDataExtractor import *
from AssetsLiabilitiesExtractor import *
from SectionImageExtractor import *

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Initialize caches
financial_data_cache = {}
assets_liabilities_cache = {}
ratios_cache = {}
section_images_cache = {}
first_page_cache = None

def extract_financial_data(pdf_path):
    if pdf_path in financial_data_cache:
        return financial_data_cache[pdf_path]
    
    extractor = FinancialDataExtractor(pdf_path)
    data = extractor.extract_financial_data()
    financial_data_cache[pdf_path] = data  # Cache the data
    return data

def extract_assets_liabilities(pdf_path):
    if pdf_path in assets_liabilities_cache:
        return assets_liabilities_cache[pdf_path]
    
    extractor = AssetsLiabilitiesExtractor(pdf_path)
    data = extractor.extract_assets_liabilities()
    assets_liabilities_cache[pdf_path] = data  # Cache the data
    return data

def extract_and_calculate_ratios(pdf_path):
    if pdf_path in ratios_cache:
        return ratios_cache[pdf_path]
    
    # Assuming you perform calculations based on the PDF content
    # Replace with actual calculations
    result = "Debt-to-equity ratio calculated successfully from the PDF."
    ratios_cache[pdf_path] = result  # Cache the result
    return result

def display_images_from_section(pdf_path):
    if pdf_path in section_images_cache:
        return section_images_cache[pdf_path]
    
    extractor = SectionImageExtractor(pdf_path)
    images = extractor.display_images_from_section()
    section_images_cache[pdf_path] = images  # Cache the images
    return images

def display_first_page(pdf_path):
    global first_page_cache
    if first_page_cache is not None:
        return [first_page_cache]  # Return cached image
    
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        image = first_page.to_image()
        image_path = "first_page.png"  # Save the image temporarily
        image.save(image_path)
        first_page_cache = image_path  # Cache the image path
    return [image_path]  # Return as a list to maintain consistent handling





def calculate_percentage_change(current, previous):
    """Calculate percentage change between two values"""
    if previous == 0:
        return 0
    return ((current - previous) / abs(previous)) * 100

def format_analysis_section(metric_name, values, include_negative=False):
    """Format the analysis for a single metric"""
    if not values or len(values) < 2:
        return f"Insufficient data for {metric_name} analysis.\n"
        
    result = f"{metric_name} Analysis:\n\n"
    
    for i in range(len(values)-1):
        current_value = values[i]
        previous_value = values[i+1]
        
        pct_change = calculate_percentage_change(current_value, previous_value)
        
        result += f"Period {i+1}:\n"
        result += f"Current Value: ₹{current_value:,.2f}\n"
        result += f"Previous Value: ₹{previous_value:,.2f}\n"
        
        if include_negative:
            result += f"Change: {pct_change:+.2f}%\n"
        else:
            if pct_change > 0:
                result += f"Percentage Increase: {abs(pct_change):.2f}%\n"
            else:
                result += f"Percentage Decrease: {abs(pct_change):.2f}%\n"
        
        result += "\n"
        
    return result



def analyze_total_income(pdf_path):
    """Analyze only total income metrics"""
    extractor = FinancialDataExtractor(pdf_path)
    table_data = extractor.extract_financial_data()
    parsed_data = parse_tabulated_data(table_data)
    
    if not parsed_data or 'total income' not in parsed_data:
        return "No total income data found in the document."
        
    return format_analysis_section('Total Income', parsed_data['total income'])

def analyze_expenses(pdf_path):
    """Analyze only expenses metrics"""
    extractor = FinancialDataExtractor(pdf_path)
    table_data = extractor.extract_financial_data()
    parsed_data = parse_tabulated_data(table_data)
    
    if not parsed_data or 'total expenses' not in parsed_data:
        return "No expenses data found in the document."
        
    return format_analysis_section('Total Expenses', parsed_data['total expenses'])

def analyze_comprehensive_loss(pdf_path):
    """Analyze only comprehensive loss metrics"""
    extractor = FinancialDataExtractor(pdf_path)
    table_data = extractor.extract_financial_data()
    parsed_data = parse_tabulated_data(table_data)
    
    if not parsed_data or 'comprehensive loss' not in parsed_data:
        return "No comprehensive loss data found in the document."
        
    return format_analysis_section('Comprehensive Loss', parsed_data['comprehensive loss'])

def analyze_loss_per_share(pdf_path):
    """Analyze only loss per share metrics"""
    extractor = FinancialDataExtractor(pdf_path)
    table_data = extractor.extract_financial_data()
    parsed_data = parse_tabulated_data(table_data)
    
    if not parsed_data or 'loss per equity share' not in parsed_data:
        return "No loss per share data found in the document."
        
    return format_analysis_section('Loss per Share', parsed_data['loss per equity share'])



def analyze_assets(pdf_path):
    # Get assets and liabilities data
    data = extract_assets_liabilities(pdf_path)
    
    # Split the data into lines
    lines = data.split('\n')
    
    # Find the Total Assets line
    assets_values = None
    for line in lines:
        if 'Total   | assets' in line and 'current' not in line:
            parts = line.split('|')
            values = []
            for part in parts[3:]:  # Skip the first 3 columns which are headers
                try:
                    cleaned_val = part.strip().replace(',', '')  # Remove commas
                    if cleaned_val and not cleaned_val.isalpha():
                        values.append(float(cleaned_val))
                except ValueError:
                    continue
            assets_values = values
            break
    
    if not assets_values:
        return "Could not find Total Assets data in the document."
    
    # Calculate percentage changes
    changes = []
    for i in range(len(assets_values)-1):
        current_value = assets_values[i]
        previous_value = assets_values[i+1]
        
        # Calculate percentage change
        pct_change = ((current_value - previous_value) / previous_value) * 100
        
        changes.append({
            'Current Period Value': current_value,
            'Previous Period Value': previous_value,
            'Percentage Change': round(pct_change, 2)
        })
    
    # Create formatted output string
    result = "Total Assets Analysis:\n\n"
    for i, change in enumerate(changes):
        result += f"Period {i+1}:\n"
        result += f"Current Value: ₹{change['Current Period Value']:,.2f}\n"
        result += f"Previous Value: ₹{change['Previous Period Value']:,.2f}\n"
        if change['Percentage Change'] > 0:
            result += f"Percentage Increase: {abs(change['Percentage Change'])}%\n"
        else:
            result += f"Percentage Decrease: {abs(change['Percentage Change'])}%\n"
        result += "\n"
    
    return result

def analyze_liabilities(pdf_path):
    # Get assets and liabilities data
    data = extract_assets_liabilities(pdf_path)
    
    # Split the data into lines
    lines = data.split('\n')
    
    # Find the Total Liabilities line
    liabilities_values = None
    for line in lines:
        if 'Total   | liabilities' in line:
            parts = line.split('|')
            values = []
            for part in parts[3:]:  # Skip the first 3 columns which are headers
                try:
                    cleaned_val = part.strip().replace(',', '')  # Remove commas
                    if cleaned_val and not cleaned_val.isalpha():
                        values.append(float(cleaned_val))
                except ValueError:
                    continue
            liabilities_values = values
            break
    
    if not liabilities_values:
        return "Could not find Total Liabilities data in the document."
    
    # Calculate percentage changes
    changes = []
    for i in range(len(liabilities_values)-1):
        current_value = liabilities_values[i]
        previous_value = liabilities_values[i+1]
        
        # Calculate percentage change
        pct_change = ((current_value - previous_value) / previous_value) * 100
        
        changes.append({
            'Current Period Value': current_value,
            'Previous Period Value': previous_value,
            'Percentage Change': round(pct_change, 2)
        })
    
    # Create formatted output string
    result = "Total Liabilities Analysis:\n\n"
    for i, change in enumerate(changes):
        result += f"Period {i+1}:\n"
        result += f"Current Value: ₹{change['Current Period Value']:,.2f}\n"
        result += f"Previous Value: ₹{change['Previous Period Value']:,.2f}\n"
        if change['Percentage Change'] > 0:
            result += f"Percentage Increase: {abs(change['Percentage Change'])}%\n"
        else:
            result += f"Percentage Decrease: {abs(change['Percentage Change'])}%\n"
        result += "\n"
    
    return result

def analyze_assets_liabilities_ratio(pdf_path):
    # Get assets and liabilities data
    data = extract_assets_liabilities(pdf_path)
    
    # Split the data into lines
    lines = data.split('\n')
    
    # Find both Total Assets and Total Liabilities
    assets_values = None
    liabilities_values = None
    
    for line in lines:
        if 'Total   | assets' in line and 'current' not in line:
            parts = line.split('|')
            assets_values = []
            for part in parts[3:]:  # Skip the first 3 columns which are headers
                try:
                    cleaned_val = part.strip().replace(',', '')  # Remove commas
                    if cleaned_val and not cleaned_val.isalpha():
                        assets_values.append(float(cleaned_val))
                except ValueError:
                    continue
        
        if 'Total   | liabilities' in line:
            parts = line.split('|')
            liabilities_values = []
            for part in parts[3:]:  # Skip the first 3 columns which are headers
                try:
                    cleaned_val = part.strip().replace(',', '')  # Remove commas
                    if cleaned_val and not cleaned_val.isalpha():
                        liabilities_values.append(float(cleaned_val))
                except ValueError:
                    continue
    
    if not assets_values or not liabilities_values:
        return "Could not find either Assets or Liabilities data in the document."
    
    # Calculate ratios and changes
    result = "Assets to Liabilities Ratio Analysis:\n\n"
    
    for i in range(len(assets_values)):
        ratio = assets_values[i] / liabilities_values[i]
        result += f"Period {i+1}:\n"
        result += f"Assets: ₹{assets_values[i]:,.2f}\n"
        result += f"Liabilities: ₹{liabilities_values[i]:,.2f}\n"
        result += f"Assets to Liabilities Ratio: {ratio:.2f}\n"
        
        # Calculate ratio change if not the first period
        if i > 0:
            previous_ratio = assets_values[i-1] / liabilities_values[i-1]
            ratio_change = ((ratio - previous_ratio) / previous_ratio) * 100
            if ratio_change > 0:
                result += f"Ratio Increased by: {abs(ratio_change):.2f}%\n"
            else:
                result += f"Ratio Decreased by: {abs(ratio_change):.2f}%\n"
        result += "\n"
    
    return result

def parse_tabulated_data(table_string):
    """Parse the tabulated string output into a structured dictionary"""
    if not isinstance(table_string, str):
        return None
        
    data = {}
    headers = []
    
    # Split the table into lines
    lines = table_string.split('\n')
    
    # Find headers first
    for line in lines:
        if '+-' in line:  # Skip grid lines
            continue
        if any(word in line.lower() for word in ['particulars', 'march', 'year']):
            # Extract headers
            headers = [h.strip() for h in line.split('|') if h.strip()]
            break
    
    for line in lines:
        # Skip grid lines and empty lines
        if '+-' in line or not line.strip():
            continue
            
        # Split the line by '|' and clean up the cells
        cells = [cell.strip() for cell in line.split('|') if cell.strip()]
        
        if cells and len(cells) >= 2:
            # First cell is typically the label/metric name
            metric = cells[0].lower()
            
            # Look for specific keywords in the metric name
            if any(keyword in metric for keyword in [
                'total income', 'total expenses', 'comprehensive loss', 
                'comprehensive profit', 'loss per equity', 'total assets',
                'total liabilities', 'total equity'
            ]):
                # Convert string values to floats, handling commas and parentheses
                values = []
                for cell in cells[1:]:
                    try:
                        # Remove commas and handle negative numbers in parentheses
                        clean_cell = cell.replace(',', '').replace('(', '-').replace(')', '')
                        if clean_cell.strip() and not clean_cell.isalpha():
                            value = float(clean_cell)
                            values.append(value)
                    except ValueError:
                        continue
                        
                if values:  # Only add if we found numeric values
                    data[metric] = {
                        'values': values,
                        'headers': headers[1:len(values)+1] if headers else None
                    }
                
    return data

def format_currency(value):
    """Format number as currency with appropriate scaling"""
    abs_value = abs(value)
    if abs_value >= 10000000:  # Crores
        return f"₹{value/10000000:.2f} Cr"
    elif abs_value >= 100000:  # Lakhs
        return f"₹{value/100000:.2f} L"
    else:
        return f"₹{value:,.2f}"

def analyze_metric(metric_name, metric_data, include_headers=True):
    """Analyze a single metric and format the results"""
    if not metric_data or 'values' not in metric_data or not metric_data['values']:
        return f"No data available for {metric_name}\n"
    
    values = metric_data['values']
    headers = metric_data.get('headers', [])
    
    result = f"\n{metric_name.upper()} ANALYSIS:\n"
    result += "=" * (len(metric_name) + 9) + "\n\n"
    
    for i in range(len(values)-1):
        current_value = values[i]
        previous_value = values[i+1]
        
        period_header = f"Period: {headers[i]} vs {headers[i+1]}" if headers and include_headers else f"Period {i+1}"
        result += f"{period_header}\n"
        result += f"Current Value: {format_currency(current_value)}\n"
        result += f"Previous Value: {format_currency(previous_value)}\n"
        
        if previous_value != 0:
            pct_change = ((current_value - previous_value) / abs(previous_value)) * 100
            if pct_change > 0:
                result += f"Increase: {abs(pct_change):.2f}%\n"
            else:
                result += f"Decrease: {abs(pct_change):.2f}%\n"
        
        result += "\n"
    
    # Add latest absolute value
    result += f"Latest Value: {format_currency(values[0])}\n"
    return result

def analyze_all_metrics(pdf_path):
    """Comprehensive analysis of all financial metrics"""
    # Get both financial and balance sheet data
    financial_extractor = FinancialDataExtractor(pdf_path)
    balance_sheet_extractor = AssetsLiabilitiesExtractor(pdf_path)
    
    financial_data = financial_extractor.extract_financial_data()
    balance_sheet_data = balance_sheet_extractor.extract_assets_liabilities()
    
    # Parse both datasets
    financial_metrics = parse_tabulated_data(financial_data)
    balance_sheet_metrics = parse_tabulated_data(balance_sheet_data)
    
    if not financial_metrics and not balance_sheet_metrics:
        return "No financial data could be extracted from the document."
    
    analysis = "COMPREHENSIVE FINANCIAL ANALYSIS\n"
    analysis += "==============================\n\n"
    
    # Analyze Income Statement Metrics
    if financial_metrics:
        analysis += "INCOME STATEMENT METRICS\n"
        analysis += "-----------------------\n"
        for metric_name, data in financial_metrics.items():
            if metric_name in ['total income', 'total expenses', 'comprehensive loss', 'loss per equity']:
                analysis += analyze_metric(metric_name, data)
        analysis += "\n"
    
    # Analyze Balance Sheet Metrics
    if balance_sheet_metrics:
        analysis += "BALANCE SHEET METRICS\n"
        analysis += "--------------------\n"
        for metric_name, data in balance_sheet_metrics.items():
            if metric_name in ['total assets', 'total liabilities', 'total equity']:
                analysis += analyze_metric(metric_name, data)
                
        # Calculate and add ratio analysis if we have the necessary data
        if 'total assets' in balance_sheet_metrics and 'total liabilities' in balance_sheet_metrics:
            analysis += "\nKEY RATIOS\n"
            analysis += "----------\n"
            
            assets = balance_sheet_metrics['total assets']['values']
            liabilities = balance_sheet_metrics['total liabilities']['values']
            
            for i in range(len(assets)):
                if liabilities[i] != 0:
                    ratio = assets[i] / liabilities[i]
                    analysis += f"Assets to Liabilities Ratio (Period {i+1}): {ratio:.2f}\n"
    
    return analysis

def analyze_all_balance_sheet_metrics(pdf_path):
    """Focused analysis of balance sheet metrics"""
    extractor = AssetsLiabilitiesExtractor(pdf_path)
    data = extractor.extract_assets_liabilities()
    
    metrics = parse_tabulated_data(data)
    if not metrics:
        return "No balance sheet data could be extracted from the document."
    
    analysis = "BALANCE SHEET ANALYSIS\n"
    analysis += "=====================\n\n"
    
    # Analyze core balance sheet metrics
    for metric_name in ['total assets', 'total liabilities', 'total equity']:
        if metric_name in metrics:
            analysis += analyze_metric(metric_name, metrics[metric_name])
            analysis += "\n"
    
    # Add ratio analysis
    if 'total assets' in metrics and 'total liabilities' in metrics:
        analysis += "FINANCIAL RATIOS\n"
        analysis += "===============\n\n"
        
        assets = metrics['total assets']['values']
        liabilities = metrics['total liabilities']['values']
        
        for i in range(len(assets)):
            if liabilities[i] != 0:
                current_ratio = assets[i] / liabilities[i]
                analysis += f"Assets to Liabilities Ratio (Period {i+1}): {current_ratio:.2f}\n"
                
                if i > 0 and liabilities[i-1] != 0:
                    prev_ratio = assets[i-1] / liabilities[i-1]
                    pct_change = ((current_ratio - prev_ratio) / prev_ratio) * 100
                    if pct_change > 0:
                        analysis += f"Ratio Increased by: {abs(pct_change):.2f}%\n"
                    else:
                        analysis += f"Ratio Decreased by: {abs(pct_change):.2f}%\n"
                analysis += "\n"
    
    return analysis

# Mapping intents to functions
intents = {
    "profit": extract_financial_data,
    "loss": extract_financial_data,
    "expenses": extract_financial_data,
    "assets": extract_assets_liabilities,
    "asset": extract_assets_liabilities,
    "liabilities": extract_assets_liabilities,
    "debt_to_equity": extract_and_calculate_ratios,
    "growth": display_images_from_section,
    "about": display_first_page,
    "analysis": analyze_all_metrics,
    "balance" : analyze_all_balance_sheet_metrics
}

# Function to identify user intent
def identify_intent(user_question):
    question_vector = vectorizer.transform([user_question])
    similarities = cosine_similarity(question_vector, intent_vectors).flatten()
    best_match_index = similarities.argmax()
    
    if similarities[best_match_index] > 0.2:  # Threshold for similarity
        return list(intents.keys())[best_match_index]
    return None

# Preprocess intents for vectorization
vectorizer = TfidfVectorizer()
intent_phrases = list(intents.keys())
intent_vectors = vectorizer.fit_transform(intent_phrases)

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Financial Query Chatbot")

        self.root.geometry("800x600")
        self.root.minsize(400, 300)

        self.chat_frame = tk.Frame(self.root)
        self.chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.chat_canvas = tk.Canvas(self.chat_frame)
        self.chat_scrollbar = tk.Scrollbar(self.chat_frame, command=self.chat_canvas.yview)
        self.chat_scrollable_frame = tk.Frame(self.chat_canvas)

        self.chat_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )

        self.chat_canvas.create_window((0, 0), window=self.chat_scrollable_frame, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=self.chat_scrollbar.set)

        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.user_input = tk.Entry(self.root, width=50)
        self.user_input.pack(pady=5)
        self.user_input.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack()

    def send_message(self, event=None):
        user_question = self.user_input.get()
        if user_question:
            self.add_message("You: " + user_question, is_user=True)
            self.user_input.delete(0, tk.END)

            self.disable_input()
            self.add_message("Anubrata : Processing...\n")

            self.root.after(100, self.generate_response, user_question)

    def generate_response(self, user_question):
        intent = identify_intent(user_question)
        pdf_path = 'C:/Users/anubrata/Downloads/project_python/284.pdf'
        
        if intent:
            output = intents[intent](pdf_path)
            if isinstance(output, list):  # If the output is a list of images
                self.add_images_to_chat(output)
            else:
                self.add_message("Anubrata: " + output)
        else:
            self.add_message("Anubrata: I'm sorry, I couldn't understand your question.")

        self.enable_input()

    def add_message(self, message, is_user=False):
        if message:
            label = Label(self.chat_scrollable_frame, text=message, justify=tk.LEFT, anchor="w")
            label.pack(fill=tk.X, padx=10, pady=2)

    def add_images_to_chat(self, images):
        for img in images:  # Assuming images are PIL Image objects
            img.thumbnail((200, 200), Image.LANCZOS)  # Resize the image for chat display
            photo = ImageTk.PhotoImage(img)

            img_label = Label(self.chat_scrollable_frame, image=photo)
            img_label.image = photo  # Keep a reference to avoid garbage collection
            img_label.pack(pady=2)

            # Add click event to open full-size image
            img_label.bind("<Button-1>", lambda e, image=img: self.open_full_image(image))

    def open_full_image(self, img):
        # Open a new window with the full-size image
        full_image_window = Toplevel(self.root)
        full_image_window.title("Full Image")
        photo = ImageTk.PhotoImage(img)
        img_label = Label(full_image_window, image=photo)
        img_label.image = photo  # Keep reference to avoid garbage collection
        img_label.pack()

        # Close button for the full image window
        close_button = tk.Button(full_image_window, text="Close", command=full_image_window.destroy)
        close_button.pack(pady=10)

    def disable_input(self):
        self.user_input.config(state='disabled')
        self.send_button.config(state='disabled')

    def enable_input(self):
        self.user_input.config(state='normal')
        self.send_button.config(state='normal')

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
