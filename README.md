This tool was created to make the Urbana School District financial data more readily accessible to community members. It parses budget .pdf files that are publically available on the USD 116 website (https://usd116.org/financial/). 

# Installation

Developed with Python 3.8 and PyPDF2 version 2.10.5.

```
conda install -n pypdf2 python=3.8 pypdf2
conda activate pypdf2
```

# Run

This tool was tested on a handful of pdf files from the USD 116 website. Users should double check the grand totals.

```
python parse_budget_pdf.py --pdf "pdf/FY23-Tentative-Budget-Expenditures.pdf" --n_columns 5
```

```
python parse_budget_pdf.py --pdf "pdf/FY23-Tentative-Budget-Revenues.pdf" --n_columns 5
```