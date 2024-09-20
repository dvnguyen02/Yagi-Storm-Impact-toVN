import pdfplumber
import csv
import re
from collections import defaultdict

def process_page(page):
    transactions = []
    date = None
    start = False
    info = defaultdict(str)
    i = 0
    
    text_chunks = page.extract_text().split('\n')
    for text_chunk in text_chunks:
        if text_chunk == 'Postal address: Telex : (0805) 411504 VCB - VT':
            break
        if not start and text_chunk == 'Số CT/ Doc No':
            start = True
        elif start:
            match = re.fullmatch('[0-9]{2}\/09\/2024', text_chunk)
            if match:
                i = 0
                if info['transaction_code']:
                    info['date'] = date
                    transactions.append(info)
                    info = defaultdict(str)
                date = match.group(0)
            elif i == 0:
                amount, first_transaction_detail_line = text_chunk.split(' ', 1)
                info['amount'] = amount
                info['transaction_detail'] = first_transaction_detail_line
                match1 = re.match('(\d{1,3}(\.\d{3})*) ', first_transaction_detail_line)
                if match1:
                    print(match1.group(1))
                    info['transaction_detail'] = info['transaction_detail'].split(' ', 1)[1]
                i += 1
            elif i == 1:
                info['transaction_code'] = text_chunk
                i += 1
            else:
                info['transaction_detail'] += ' ' + text_chunk

    if info['transaction_code']:
        info['date'] = date
        transactions.append(info)
    
    return transactions

def main():
    pdf_path = "from1-09to10-09.pdf"
    
    # Get the total number of pages
    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)

    with open('mttq.csv', 'w', newline='') as csvfile:
        fieldnames = ['date', 'transaction_code', 'amount', 'transaction_detail']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for page_number in range(num_pages):
            with pdfplumber.open(pdf_path) as pdf:
                page = pdf.pages[page_number]
                transactions = process_page(page)
                for row in transactions:
                    writer.writerow(row)

if __name__ == "__main__":
    main()