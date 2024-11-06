import tkinter as tk
from tkinter import Label, Toplevel
from PIL import Image, ImageTk
import pdfplumber
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

import pandas as pd

def analysis_total_income(pdf_path):
    # Get financial data using the existing extract_financial_data function
    data = extract_financial_data(pdf_path)
    
    # Split the data into lines
    lines = data.split('\n')
    
    # Find the Total income line
    total_income_values = None
    for line in lines:
        if 'Total income' in line:
            # Split the line into parts
            parts = line.split('|')
            # Extract only the numeric values, skipping any text
            values = []
            for part in parts[1:-1]:  # Skip first and last empty parts from split
                try:
                    # Try to convert to float, skip if fails
                    cleaned_val = part.strip()
                    if cleaned_val and not cleaned_val.isalpha():  # Check if it's not purely alphabetic
                        values.append(float(cleaned_val))
                except ValueError:
                    continue
            total_income_values = values
            break
    
    if not total_income_values:
        return "Could not find Total income data in the document."
    
    # Calculate percentage changes
    changes = []
    for i in range(len(total_income_values)-1):
        current_value = total_income_values[i]
        previous_value = total_income_values[i+1]
        
        # Calculate percentage change
        pct_change = ((current_value - previous_value) / previous_value) * 100
        
        changes.append({
            'Current Period Value': current_value,
            'Previous Period Value': previous_value,
            'Percentage Change': round(pct_change, 2)
        })
    
    # Create formatted output string
    result = "Total Income Analysis:\n\n"
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

def analyze_expenses(pdf_path):
    # Get financial data
    data = extract_financial_data(pdf_path)
    
    # Split the data into lines
    lines = data.split('\n')
    
    # Find the Total expenses line
    expense_values = None
    for line in lines:
        if 'Total expenses' in line:
            # Split the line into parts
            parts = line.split('|')
            # Extract only the numeric values, skipping any text
            values = []
            for part in parts[1:-1]:
                try:
                    cleaned_val = part.strip()
                    if cleaned_val and not cleaned_val.isalpha():
                        values.append(float(cleaned_val))
                except ValueError:
                    continue
            expense_values = values
            break
    
    if not expense_values:
        return "Could not find Total expenses data in the document."
    
    # Calculate percentage changes
    changes = []
    for i in range(len(expense_values)-1):
        current_value = expense_values[i]
        previous_value = expense_values[i+1]
        
        # Calculate percentage change
        pct_change = ((current_value - previous_value) / previous_value) * 100
        
        changes.append({
            'Current Period Value': current_value,
            'Previous Period Value': previous_value,
            'Percentage Change': round(pct_change, 2)
        })
    
    # Create formatted output string
    result = "Total Expenses Analysis:\n\n"
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

def analyze_comprehensive_loss(pdf_path):
    # Get financial data
    data = extract_financial_data(pdf_path)
    
    # Split the data into lines
    lines = data.split('\n')
    
    # Find the Total comprehensive loss line
    loss_values = None
    for line in lines:
        if 'Total comprehensive loss' in line:
            parts = line.split('|')
            values = []
            for part in parts[1:-1]:
                try:
                    cleaned_val = part.strip()
                    if cleaned_val and not cleaned_val.isalpha():
                        values.append(float(cleaned_val))
                except ValueError:
                    continue
            loss_values = values
            break
    
    if not loss_values:
        return "Could not find Total comprehensive loss data in the document."
    
    # Calculate percentage changes
    changes = []
    for i in range(len(loss_values)-1):
        current_value = loss_values[i]
        previous_value = loss_values[i+1]
        
        pct_change = ((current_value - previous_value) / previous_value) * 100
        
        changes.append({
            'Current Period Value': current_value,
            'Previous Period Value': previous_value,
            'Percentage Change': round(pct_change, 2)
        })
    
    # Create formatted output string
    result = "Total Comprehensive Loss Analysis:\n\n"
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

def analyze_loss_per_share(pdf_path):
    # Get financial data
    data = extract_financial_data(pdf_path)
    
    # Split the data into lines
    lines = data.split('\n')
    
    # Find the Loss per equity share line
    eps_values = None
    for line in lines:
        if 'Loss per equity share' in line:
            parts = line.split('|')
            values = []
            for part in parts[1:-1]:
                try:
                    cleaned_val = part.strip()
                    if cleaned_val and not cleaned_val.isalpha():
                        values.append(float(cleaned_val))
                except ValueError:
                    continue
            eps_values = values
            break
    
    if not eps_values:
        return "Could not find Loss per equity share data in the document."
    
    # Calculate percentage changes
    changes = []
    for i in range(len(eps_values)-1):
        current_value = eps_values[i]
        previous_value = eps_values[i+1]
        
        pct_change = ((current_value - previous_value) / previous_value) * 100
        
        changes.append({
            'Current Period Value': current_value,
            'Previous Period Value': previous_value,
            'Percentage Change': round(pct_change, 2)
        })
    
    # Create formatted output string
    result = "Loss per Equity Share Analysis:\n\n"
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

def analyze_all_metrics(pdf_path):
    """Analyze all financial metrics and return combined results"""
    expenses_analysis = analyze_expenses(pdf_path)
    comprehensive_loss_analysis = analyze_comprehensive_loss(pdf_path)
    eps_analysis = analyze_loss_per_share(pdf_path)
    total_income = analysis_total_income(pdf_path)
    
    combined_analysis = "\n".join([
        "=== COMPREHENSIVE FINANCIAL ANALYSIS ===\n",
        total_income,
        "\n" + "="*40 + "\n",
        expenses_analysis,
        "\n" + "="*40 + "\n",
        comprehensive_loss_analysis,
        "\n" + "="*40 + "\n",
        eps_analysis
    ])
    
    return combined_analysis

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

def analyze_all_balance_sheet_metrics(pdf_path):
    """Analyze all balance sheet metrics and return combined results"""
    assets_analysis = analyze_assets(pdf_path)
    liabilities_analysis = analyze_liabilities(pdf_path)
    ratio_analysis = analyze_assets_liabilities_ratio(pdf_path)
    
    combined_analysis = "\n".join([
        "=== COMPREHENSIVE BALANCE SHEET ANALYSIS ===\n",
        assets_analysis,
        "\n" + "="*40 + "\n",
        liabilities_analysis,
        "\n" + "="*40 + "\n",
        ratio_analysis
    ])
    
    return combined_analysis

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
        pdf_path = 'C:/Users/anubrata/Downloads/project_python/1727955078450_537AL.pdf'
        
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
