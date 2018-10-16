import re
import PyPDF2
import openpyxl


def main():
    pdf_path = 'data/budget_2018_2019.pdf'
    # create excel workbook object
    wb = openpyxl.Workbook()
    # get the active worksheet
    ws = wb.active

    # cleaned up list of entries
    with open(pdf_path, 'rb') as f:
        pdf = PyPDF2.PdfFileReader(f)
        # n_pages =  pdf.getNumPages()
        for i in range(15, 18):
            page = pdf.getPage(i)
            # get text from page, line by line
            for line in page.extractText().splitlines():
                line = line.strip()
                print(line)
                # text matching this pattern is a budget line item
                if re.match('[0-9][0-9]E[0-9][0-9][0-9] [0-9][0-9][0-9][0-9]', line):
                    print('matching line:', line)
                    ws.append(line.split())

        # print(page.extractText().splitlines())
    # save the file
    wb.save('output.xlsx')

if __name__ == '__main__':
    main()