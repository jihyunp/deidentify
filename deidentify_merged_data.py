import os, sys
import csv
import pandas as pd

__author__ = 'jihyunp'

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("")
        print('** Usage: python ./deidentify_merged_data.py <Mapping File> <Merged Data Files> ')
        print('** Example: python  ./deidentify_merged_data.py  ./master_keys.csv  ./merged_data_list.txt')
        print('')
        print('   <Mapping File> : A .csv file that has')
        print('       <Name_firstlast>,<studentid>,<ucinetid>,<randomid>,<canvasid> as the first five columns.')
        print('       If there is no file with this name, a new mapping file will be created with this name.')
        print('')
        print('   <Merged Data Files> :  A .txt file that lists .csv or .dta files of merged student data. ')
        print('       The .csv or .dta files are like ../Year1/Physics3A_Merged_data.csv ')
        print('       In each .csv or .dta file, the first row should be the name of each column, and it should have ')
        print('       at least "studentid", "ucinetid", "name_firstlast" ')
        print('')
        exit()

    mapping_file = sys.argv[1]
    merged_data_files = sys.argv[2]

    ucid2nsrc = {}
    if os.path.exists(mapping_file):
        print("Reading mapping file " + mapping_file)
        with open(mapping_file, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            header = next(reader)
            for row in reader:
                name = row[0]
                stid = row[1]  # kept as string due to alphabets in student ids
                ucid = row[2]
                rid = int(row[3])
                cid = int(row[4])
                ucid2nsrc[ucid] = [name, stid, rid, cid]

    files = []
    with open(merged_data_files, 'r') as f:
        for file in f:
            file_path = file.splitlines()[0]
            if not os.path.exists(file_path):
                print('File %s does not exist!' % file_path)
                exit()
            files.append(file_path)

    for merged_data_file in files:
        if merged_data_file.endswith('dta'):
            fname_wo_ext = merged_data_file.split(".dta")[0]
            print("Loading dta file " + merged_data_file)
            data = pd.read_stata(merged_data_file)
            data_reader = pd.read_stata(merged_data_file, iterator=True)

        elif merged_data_file.endswith('csv'):
            fname_wo_ext = merged_data_file.split(".csv")[0]
            print("Loading csv file "+ merged_data_file)
            data = pd.read_csv(merged_data_file)

        else:
            print("Merged data file should be either .dta or .csv file! Exiting..")
            exit()

        ridlist = []
        for uci in data['ucinetid']:
            ucinetid = uci.lower()
            ridlist.append(ucid2nsrc[ucinetid][2])

        # Drop the columns
        new_data = data
        col_list = ['name', 'studentid', 'ucinetid', 'canvasid', 'loginid', 'email', 'middle_last']

        for col in col_list:
            for col_in_data in data.columns:
                if (col in col_in_data) or (col_in_data == 'id'):
                    print("Deleting column "+ col_in_data)
                    new_data.drop(col_in_data, axis=1, inplace=True)


        cols = new_data.columns.tolist()
        cols = ['roster_randomid'] + cols
        new_data = new_data.assign(roster_randomid=ridlist)
        new_data = new_data[cols]

        if merged_data_file.endswith('dta'):
            deiden_merged_data_file = fname_wo_ext + " DEID.dta"
            new_data.to_stata(deiden_merged_data_file, write_index=False,
                              variable_labels=data_reader.variable_labels(), version=117)

        elif merged_data_file.endswith('csv'):
            deiden_merged_data_file = fname_wo_ext + " DEID.csv"
            new_data.to_csv(deiden_merged_data_file, index=False)

        print("Deidentified merged data has been saved to " + deiden_merged_data_file)



