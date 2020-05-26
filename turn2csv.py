""" turn2csv.py

Turn a xls report in a lot of csvs

Example:
python turn2csv.py ${directory_with_xls_reports}
"""

import os
import sys

import xlrd


def main(directory):
    for file in os.listdir(directory):
        if os.path.isfile(file) and file.endswith("xls"):
            basename, extension = file.split(".")
            book = xlrd.open_workbook(file)
    
            for sheet_name in book.sheet_names():     
                sheet = book.sheet_by_name(sheet_name)
                out_csv = "{}_{}.csv".format(basename, sheet_name)
                
                with open(out_csv, "w") as f:
                    for nb_row in range(sheet.nrows):
                        row = [str(ele) for ele in sheet.row_values(nb_row)]
                        csved_row = ",".join(row)
                        f.write("{}\n".format(csved_row))



if __name__ == "__main__":
    directory = sys.argv[1]
    main(directory)