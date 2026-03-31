import pdfplumber

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    print("------ RAW EXTRACTED TEXT ------")
    print(text)
    print("------ END OF TEXT ------")
    return text

if __name__ == "__main__":
    sample_path = "../uploads/Resume_Jagtap.pdf"  # adjust path
    extract_text_from_pdf(sample_path)