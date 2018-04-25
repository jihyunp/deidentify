import pandas as pd
from update_keys import *

__author__ = 'jihyunp'

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("")
        print('** Usage: python ./deidentify_quiz_data.py <Mapping File> <Quiz Data Folder> ')
        print('** Example: python  ./deidentify_quiz_data.py  ./master_keys.csv  ./identifiable_data/MATH/Quiz Data')
        print("")
        exit()

    mapping_file = sys.argv[1]
    quiz_data_dir = sys.argv[2]

    keys = StudentKeys(mapping_file, new_students_file=None)  # no new student file. Just load the data


    if not os.path.isdir(quiz_data_dir):
        print('[ERROR]: Data directory '+quiz_data_dir+' does not exist!')
        exit()

    deidentified_dir = os.path.join(quiz_data_dir, 'deidentified')
    processed_dir =  os.path.join(quiz_data_dir, 'processed')
    make_dir(deidentified_dir)
    make_dir(processed_dir)

    for fname in os.listdir(quiz_data_dir):
        if fname.endswith('.csv') and fname.startswith('Lesson'):
            src = os.path.join(quiz_data_dir, fname)
            new = os.path.join(deidentified_dir, fname )
            dest = os.path.join(processed_dir, fname)

            print(src +' -> '+ new)

            # Load data
            data = pd.read_csv(src)

            # Get the random id's in the same order
            ridlist = []
            for cid in data['id']:
                ridlist.append(keys.cid2rid[cid])

            # Remove the columns
            new_data = data
            col_list = ['name', 'id', 'sis_id']
            for col_in_data in data.columns:
                if col_in_data in col_list:
                    print(" - Deleting column " + col_in_data)
                    new_data.drop(col_in_data, axis=1, inplace=True)

            cols = new_data.columns.tolist()
            cols = ['roster_randomid'] + cols
            new_data = new_data.assign(roster_randomid=ridlist)
            new_data = new_data[cols]

            new_data.to_csv(new, index=False)
            # Move the original file
            os.rename(src, dest)

    print("\nDeidentified Quiz data has been saved to " + deidentified_dir + '\n')

