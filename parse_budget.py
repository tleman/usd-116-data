import re
import PyPDF2
import openpyxl


def main():
    pdf_path = 'data/budget_2018_2019.pdf'
    # the relevant data starts on this line (each pdf page has a header)
    data_start_line = 7

    # create excel workbook object
    wb = openpyxl.Workbook()
    # get the active worksheet
    ws = wb.active


    # cleaned up list of entries
    with open(pdf_path, 'rb') as f:
        pdf = PyPDF2.PdfFileReader(f)
        # n_pages =  pdf.getNumPages()
        for i_page in range(15, 18):
            # read text off of this page into a list
            page = pdf.getPage(i_page)
            all_lines_on_page = [line.strip() for line in page.extractText().splitlines()[data_start_line:]]
            # iterate over all lines on this page
            i_line = 0
            while i_line < len(all_lines_on_page):
                line = all_lines_on_page[i_line]
                # print(line)
                # text matching this pattern is a budget line item
                if re.match('\d{2}E\d{3} \d{4}', line):
                    budget_line_item = line.split()
                    for line_increment in range(1, 7):
                        try:
                            budget_line_item.append(float(all_lines_on_page[i_line+line_increment].replace(',','')))
                        except:
                            budget_line_item.append(all_lines_on_page[i_line+line_increment])
                    ws.append(budget_line_item)
                    i_line += line_increment
                    print('budget line item:', budget_line_item)
                # text matching this pattern is a summation line
                elif re.match('\d+ -+ -+ -+', line):
                    summation_line = ['']*6
                    summation_line[0] = 'Subtotal'
                    i_line += 1 # skip blank line
                    for line_increment in range(1, 6):
                        try:
                            summation_line.append(float(all_lines_on_page[i_line+line_increment].replace(',','')))
                        except:
                            summation_line.append(all_lines_on_page[i_line+line_increment])
                    ws.append(summation_line)
                    i_line += line_increment
                    print('summation line:', summation_line)
                i_line += 1

    # print(all_lines_on_page)
    # save the file
    wb.save('output.xlsx')

if __name__ == '__main__':
    main()