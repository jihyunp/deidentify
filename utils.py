import os
import csv

def convert_csv_to_unicode(data_dir):
    os.chdir(data_dir)
    for fname in os.listdir('.'):
        if fname.endswith('.csv'):
            fname_unicode = fname.split('.csv')[0] + '_unicode.csv'
            with open(fname, 'r', encoding='utf-8', errors='ignore') as infile, \
                    open(fname_unicode, 'w', newline='') as outfile:
                inputs = csv.reader(infile)
                output = csv.writer(outfile)
                for row in inputs:
                    output.writerow(row)
            os.remove(fname)
            os.rename(fname_unicode, fname)
            print("File %s converted to Unicode!" % fname)