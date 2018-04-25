import os, sys
import csv
import pandas as pd

__author__ = 'jihyunp'

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("")
        print('** Usage: python ./deidentify_merged_data.py <Mapping File> <Merged Data> ')
        print('** Example: python  ./deidentify_merged_data.py  ./master_keys.csv  ./identifiable_data/MATH-Merged Data.csv')
        print("")
        exit()

    mapping_file = sys.argv[1]
    merged_data_file = sys.argv[2]

    ucid2nsrc = {}
    if os.path.exists(mapping_file):
        print("Reading mapping file " + mapping_file)
        with open(mapping_file, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            header = reader.next()
            for row in reader:
                name = row[0]
                stid = row[1]  # kept as string due to alphabets in student ids
                ucid = row[2]
                rid = int(row[3])
                cid = int(row[4])
                ucid2nsrc[ucid] = [name, stid, rid, cid]

    if os.path.exists(merged_data_file):
        if merged_data_file.endswith('dta'):
            fname_wo_ext = merged_data_file.split(".dta")[0]
            csv_file = fname_wo_ext + ".csv"
            data = pd.io.stata.read_stata(merged_data_file)
            print("Converting .dta file to .csv file")
            data.to_csv(csv_file, index=False)

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
                if (col in col_in_data) or (col_in_data == 'name') or (col_in_data == 'id'):
                    print("Deleting column "+ col_in_data)
                    new_data.drop(col_in_data, axis=1, inplace=True)


        cols = new_data.columns.tolist()
        cols = ['roster_randomid'] + cols
        new_data = new_data.assign(roster_randomid=ridlist)
        new_data = new_data[cols]
        deiden_merged_data_file = fname_wo_ext + "-deidentified.csv"
        new_data.to_csv(deiden_merged_data_file, index=False)
        print("Deidentified merged data has been saved to " + deiden_merged_data_file)



