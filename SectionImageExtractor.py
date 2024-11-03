import pdfplumber
import re
from PIL import Image

class SectionImageExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def find_section_pages(self, section_title, occurrence=2):
        count = 0
        with pdfplumber.open(self.pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and re.search(section_title, text, re.IGNORECASE):
                    count += 1
                    if count == occurrence:
                        return i + 1  # Return the page number (1-indexed)
        return None

    def display_images_from_section(self, section_title="SECTION IV: ABOUT OUR COMPANY", occurrence=2, max_pages=5):
        images = []  # List to store extracted images
        with pdfplumber.open(self.pdf_path) as pdf:
            start_page = self.find_section_pages(section_title, occurrence)
            if start_page is None:
                print("Section not found.")
                return []

            end_page = min(start_page + max_pages - 1, len(pdf.pages))
            for i in range(start_page - 1, end_page):
                page = pdf.pages[i]
                for image in page.images:
                    # Extract the bounding box of the image
                    x0, top, x1, bottom = image['x0'], image['top'], image['x1'], image['bottom']
                    # Crop the image from the page
                    cropped_image = page.within_bbox((x0, top, x1, bottom)).to_image()
                    # Convert cropped image to PIL image and ensure it's in RGB format
                    pil_image = cropped_image.original.convert("RGB")
                    images.append(pil_image)  # Append PIL image to the list
        return images  # Return the list of images
