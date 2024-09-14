import pandas as pd
import pdfplumber
import re

def process_details(details_column):
    # Split the details string into individual transactions
    transactions = re.split(r'\n(?=(?:\d{1,2}/\d{1,2}/\d{4}|\d+\.?\d*(?:\.\d+)?[A-Z]{3}|[A-Z0-9]+\.[A-Z0-9.]+))', details_column)
    
    # Clean up transactions and replace \n with space
    cleaned_transactions = []
    for transaction in transactions:
        # Remove leading/trailing whitespace and replace internal newlines with spaces
        cleaned = re.sub(r'\s+', ' ', transaction.strip())
        if cleaned:
            cleaned_transactions.append(cleaned)
    
    return cleaned_transactions

def process_pdf_table(data):
    # Extract the columns
    date_column = data[1][0]
    debit_column = data[1][1]
    credit_column = data[1][2]
    balance_column = data[1][3]
    details_column = data[1][4]

    # Split the columns into rows
    date_rows = re.split(r'\n(?=\d{2}/\d{2}/\d{4})', date_column)
    debit_rows = debit_column.split('\n') if debit_column else [''] * len(date_rows)
    credit_rows = credit_column.split('\n')
    balance_rows = balance_column.split('\n') if balance_column else [''] * len(date_rows)
    
    # Process the details column
    details_rows = process_details(details_column)
    
    # Ensure all lists have the same length
    max_length = max(len(date_rows), len(debit_rows), len(credit_rows), len(balance_rows), len(details_rows))
    date_rows += [''] * (max_length - len(date_rows))
    debit_rows += [''] * (max_length - len(debit_rows))
    credit_rows += [''] * (max_length - len(credit_rows))
    balance_rows += [''] * (max_length - len(balance_rows))
    details_rows += [''] * (max_length - len(details_rows))

    # Process each row
    processed_rows = []
    current_transaction = None

    for date_row, debit, credit, balance, details in zip(date_rows, debit_rows, credit_rows, balance_rows, details_rows):
        # Split date and document number
        date_match = re.search(r'(\d{2}/\d{2}/\d{4})\n?(.*)', date_row)
        
        if date_match:
            # If we have a current transaction, add it to processed_rows
            if current_transaction:
                processed_rows.append(current_transaction)

            # Start a new transaction
            date = date_match.group(1)
            doc_no = date_match.group(2)
            current_transaction = {
                'Date': date,
                'Doc No': doc_no,
                'Debit': debit.strip(),
                'Credit': credit.strip(),
                'Balance': balance.strip(),
                'Details': details.strip()
            }
        elif current_transaction:
            # Append additional details to the current transaction
            current_transaction['Details'] += ' ' + details.strip()

    # Add the last transaction if it exists
    if current_transaction:
        processed_rows.append(current_transaction)

    return processed_rows

def extract_and_process_pdf(pdf_path):
    all_processed_data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:  # Check if a table was extracted
                processed_data = process_pdf_table(table)
                all_processed_data.extend(processed_data)
    
    return all_processed_data


# Usage
pdf_path = 'Preview.pdf'
processed_tables = extract_and_process_pdf(pdf_path)

# Create DataFrame and save to CSV
data = pd.DataFrame(data=processed_tables)
data['Credit'] = data['Credit'].str.replace('.', '', regex=False)
data['Credit'] = pd.to_numeric(data['Credit'], errors='coerce')
data['Debit'] = data['Debit'].str.replace('.', '', regex=False)
data['Debit'] = pd.to_numeric(data['Debit'], errors='coerce')
data['Balance'] = data['Balance'].str.replace('.', '', regex=False)
data['Balance'] = pd.to_numeric(data['Balance'], errors='coerce')
data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%Y', errors='coerce')
print('Data has been created')
data.to_csv("bankstatement.csv", index=False)
