import re, csv
import PyPDF2
import openpyxl


def main():
    # PDF_PATH = 'data/FY23-Tentative-Budget-Expenditures.pdf'
    PDF_PATH = 'data/budget_2018_2019.pdf'
    # PDF's may be given with different numbers of budget (dollar) columns
    N_BUDGET_COLS = 5
    # 5 account number columns + 1 account description + N budget columns
    MAX_BUDGET_ENTRY_COLS = 5 + 1 + N_BUDGET_COLS

    # output_file_type = 'csv'
    # # the relevant data starts on this line (each pdf page has a header)
    # data_start_line = 7

    # if output_file_type == 'xlsx':
    #     # create output file object
    #     wb = openpyxl.Workbook()
    #     outfile = wb.active
    #     # define function to add line to output file
    #     add_line = lambda worksheet, line_item: worksheet.append(line_item)
    # elif output_file_type == 'csv':
    #     # create output file object
    #     csvfile = open('budget.csv', 'w', newline='')
    #     outfile = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    #     outfile.writerow(['ftdloc', 'func', 'obj', 'sj', 'acct', 'description',
    #                       'budget_1819', 'budget_1718', 'actual_1718'])
    #     # define function to add line to output file
    #     add_line = lambda csvwriter, line_item: csvwriter.writerow(line_item)

    # read pdf file into list
    raw_pages = []
    with open(PDF_PATH, 'rb') as f:
        pdf = PyPDF2.PdfFileReader(f)
        for page in pdf.pages:
            raw_pages.append(page.extract_text())
        n_pages =  pdf.getNumPages()

    clean_lines = []
    for page in raw_pages:
        this_page = page.splitlines(keepends=True)
        for line in this_page:
            clean_line = line.replace('\xa0', ' ')
            clean_line = clean_line.strip()
            clean_lines.append(clean_line)

    # first line of new page = any chars + Urbana,IL + date + Page:# + end of line
    new_page_pattern = '.*Urbana, IL \d\d/\d\d/\d\d Page:\d{1,3}$'

    # save to these output variables
    output_lines = []
    funds = {}
    accounts = {}

    # iterate over all extracted lines of the pdf
    i = 0
    while i < len(clean_lines):
        current_line = clean_lines[i]
        if re.match(new_page_pattern, current_line):
            i += 1
            print(f'HEADER: {current_line}')
        # line 2 of header = start of string + 10 digits separated by decimals
        elif re.match('^\d\d\.\d\d\.\d\d\.\d\d\.\d\d', current_line):
            i += 1
            print(f'HEADER: {current_line}')
        # line 3 of header = begins with "Account Level"
        elif re.match('^Account Level', current_line):
            i += 1
            print(f'HEADER: {current_line}')
        # line 4 of header = begins with "FDTLOC"
        elif re.match('^FDTLOC', current_line):
            i += 1
            print(f'HEADER: {current_line}')
        # line 5 of header = begins with "Description"
        elif re.match('^Description', current_line):
            i += 1
            print(f'HEADER: {current_line}')
        # fund number = start of string + two digit number + end of string
        elif re.match('^\d{2}$', current_line):
            # this line is the fund number, next line is the fund name
            funds[current_line] = clean_lines[i+1]
            i += 2
            print(f'FUND number:{current_line} name:{funds[current_line]}')
        # account number = start of string + six digit number + end of string
        elif re.match('^\d{6}$', current_line):
            # this line is the account number, next line is the account name
            accounts[current_line] = clean_lines[i+1]
            i += 2
            print(f'ACCOUNT number:{current_line} name:{accounts[current_line]}')
        # budget line item - ##E### ####
        elif re.match('^\d{2}E\d{3} \d{4}', current_line):
            # account numbers
            budget_line = current_line.split()
            # if the next line is empty or numeric, the account description is blank in the PDF
            if not clean_lines[i+1] or clean_lines[i+1].isnumeric():
                budget_line.append('BLANK')
            # continue adding budget line entries until we reach either
            #    1) the next budget line item
            #    2) the next page
            #    3) the maximum number of columns (helps with edge cases with subtotals)
            while not (re.match('^\d{2}E\d{3} \d{4}', clean_lines[i+1]) or 
                       re.match(new_page_pattern, clean_lines[i+1])):
                i += 1
                budget_line.append(clean_lines[i].replace(',',''))
                if len(budget_line) == MAX_BUDGET_ENTRY_COLS:
                    break
            i += 1
            print('ENTRY:', budget_line)
            output_lines.append(budget_line)
        else:
            i += 1
            print(f'SKIPPING: {current_line}')


    with open('budget.csv', 'w',  newline='') as f:
        csvwriter = csv.writer(f)
        for line in output_lines:
            csvwriter.writerow(line)

    # write fund types separate csv file
    with open('funds.csv', 'w',  newline='') as f:
        csvwriter = csv.writer(f)
        for key, val in funds.items():
            csvwriter.writerow([key, val])

    # write account types to separate csv file
    with open('accounts.csv', 'w',  newline='') as f:
        csvwriter = csv.writer(f)
        for key, val in accounts.items():
            csvwriter.writerow([key, val])

    print(funds)
    print(accounts)

if __name__ == '__main__':
    main()