import re, csv
import PyPDF2
import openpyxl


def main():
    pdf_path = 'data/budget_2018_2019.pdf'
    output_file_type = 'csv'
    # the relevant data starts on this line (each pdf page has a header)
    data_start_line = 7

    if output_file_type == 'xlsx':
        # create output file object
        wb = openpyxl.Workbook()
        outfile = wb.active
        # define function to add line to output file
        add_line = lambda worksheet, line_item: worksheet.append(line_item)
    elif output_file_type == 'csv':
        # create output file object
        csvfile = open('budget.csv', 'w', newline='')
        outfile = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        outfile.writerow(['ftdloc', 'func', 'obj', 'sj', 'acct', 'description',
                          'budget_1819', 'budget_1718', 'actual_1718'])
        # define function to add line to output file
        add_line = lambda csvwriter, line_item: csvwriter.writerow(line_item)

    fund_types = {}
    account_types = {}
    with open(pdf_path, 'rb') as f:
        # read pdf file
        pdf = PyPDF2.PdfFileReader(f)
        n_pages =  pdf.getNumPages()
        
        # iterate over pages in pdf
        for i_page in range(n_pages):
            
            # read text from this page into a list
            page = pdf.getPage(i_page)
            all_lines_on_page = [line.strip() for line in page.extractText().splitlines()[data_start_line:]]
            
            # iterate over all lines on this page
            i_line = 0
            while i_line < len(all_lines_on_page):
                line = all_lines_on_page[i_line]
                # line matching two digit number is a fund type
                if re.match('^\d{2}$', line):
                    i_line += 1
                    fund_types[line] = all_lines_on_page[i_line]
                    print('fund type:', line, fund_types[line])
                # line matching six digit number is an account type
                elif re.match('^\d{6}$', line):
                    i_line += 1
                    account_types[line] = all_lines_on_page[i_line]
                    print('account type:', line, account_types[line])
                # line matching this pattern is a budget line item
                elif re.match('\d{2}E\d{3} \d{4}', line):
                    line_item = line.split()
                    for line_increment in range(1, 5):
                        try:
                            line_item.append(float(all_lines_on_page[i_line+line_increment].replace(',','')))
                        except:
                            line_item.append(all_lines_on_page[i_line+line_increment])
                    add_line(outfile, line_item)
                    i_line += line_increment
                    print('budget entry:', line_item)
                # line matching this pattern is a subtotal
                elif re.match('\d+ -+ -+ -+', line) and output_file_type == 'xlsx':
                    line_item = ['']*6
                    line_item[0] = 'Subtotal'
                    i_line += 1 # skip blank line
                    for line_increment in range(1, 4):
                        try:
                            line_item.append(float(all_lines_on_page[i_line+line_increment].replace(',','')))
                        except:
                            line_item.append(all_lines_on_page[i_line+line_increment])
                    add_line(outfile, line_item)
                    i_line += line_increment                
                    print('subtotal:', line_item)
                i_line += 1

    # save the file
    if output_file_type == 'xlsx':
        wb.save('output.xlsx')
    elif output_file_type == 'csv':
        csvfile.close()

    # write fund types separate csv file
    with open('funds.csv', 'w',  newline='') as f:
        csvwriter = csv.writer(f)
        for key, val in fund_types.items():
            csvwriter.writerow([key, val])

    # write account types to separate csv file
    with open('accounts.csv', 'w',  newline='') as f:
        csvwriter = csv.writer(f)
        for key, val in account_types.items():
            csvwriter.writerow([key, val])

    print(fund_types)
    print(account_types)

if __name__ == '__main__':
    main()