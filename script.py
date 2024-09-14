import pdfplumber
import pandas as pd

# Path to the PDF
pdf_path="from1-09to10-09.pdf"


# Function to extract tables from a range of PDF pages
def extract_tables_from_pdf(pdf_path, start_page, end_page):
    table_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num in range(start_page, end_page):
            page = pdf.pages[page_num]
            # Extract tables from the page
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    table_data.append(row)
    return table_data

# Function to save the extracted table data into a CSV file
def save_to_csv(table_data, csv_file):
    df = pd.DataFrame(table_data)
    df.to_csv(csv_file, index=False)
    print(f'Data saved to {csv_file}')

# Main function to extract tables from 200 pages and save to CSV
def extract_pdf_tables_to_csv(pdf_path, start_page, end_page, csv_file):
    # Extract tables from the first 200 pages
    table_data = extract_tables_from_pdf(pdf_path, start_page, end_page)
    
    # Save the table data into a CSV file
    save_to_csv(table_data, csv_file)

# Run the extraction for the first 200 pages
extract_pdf_tables_to_csv(pdf_path, start_page=0, end_page=200, csv_file='output_tables_200_pages.csv')
