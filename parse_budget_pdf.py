import argparse, csv, re
import PyPDF2


def main(args):
    # 5 account number columns + 1 account description + N budget columns
    max_budget_entry_columns = 5 + 1 + args.n_columns

    # read pdf file into list
    raw_pages = []
    with open(args.pdf, 'rb') as f:
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
    # budget line item = ##E### ####
    budget_entry_pattern = '^\d{2}E\d{3} \d{4}'
    # subtotal line item = ## ---
    subtotal_line_pattern = '^\d{2} ---'

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
            # edge case where the account does not have a corresponding description
            # and the next line is a budget entry
            if re.match(budget_entry_pattern, clean_lines[i+1]):
                accounts[current_line] = 'BLANK'
            # this line is the account number, next line is the account name            
            else:
                accounts[current_line] = clean_lines[i+1]
            i += 1
            print(f'ACCOUNT number:{current_line} name:{accounts[current_line]}')
        # budget line item = ##E### ####
        elif re.match(budget_entry_pattern, current_line):
            # account numbers
            budget_line = current_line.split()
            # account description
            if clean_lines[i+1]:
                try:
                    float(clean_lines[i+1].replace(',',''))
                    budget_line.append('BLANK')
                except ValueError:
                    pass
            else:
                budget_line.append('BLANK')
            # continue adding budget line entries until we reach either
            #    1) the next budget line item
            #    2) the next page
            #    3) the maximum number of columns (helps with edge cases with subtotals)
            while not (re.match(budget_entry_pattern, clean_lines[i+1]) or 
                       re.match(new_page_pattern, clean_lines[i+1])):
                i += 1
                budget_line.append(clean_lines[i].replace(',',''))
                if len(budget_line) == max_budget_entry_columns:
                    break
            i += 1
            print('ENTRY:', budget_line)
            output_lines.append(budget_line)
        # subtotal = ## --- ---- ----
        elif re.match(subtotal_line_pattern, current_line):
            subtotal_line = current_line.split()
            subtotal_line.append('SUBTOTAL')
            # continue adding budget line entries until we reach the maximum number of columns
            while True:
                i += 1
                subtotal_line.append(clean_lines[i].replace(',',''))
                if len(subtotal_line) == max_budget_entry_columns:
                    break

            i += 1
            print('SUBTOAL:', subtotal_line)
            # output_lines.append(subtotal_line)
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

    print('FUNDS:\n', funds)
    print('ACCOUNTS:\n', accounts)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf', type=str, required=True, help='Path to the Budget PDF')
    parser.add_argument('--n_columns', type=int, required=True, help='Number of columns containing budget dollars')
    args = parser.parse_args()
    main(args)