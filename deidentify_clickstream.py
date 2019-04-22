from update_keys import *
import re

__author__ = 'jihyunp'

def print_usage_deidentify():
    print('')
    print('----------------------------------------------------------------------------------------------')
    print('** Usage: python ./deidentify_clickstream.py <Mapping File> <Clickstream Data Directories> ')
    print('** Example: python  ./deidentify_clickstream.py  ./master_keys.csv  ./clickstream_folders.txt ')
    print('----------------------------------------------------------------------------------------------')
    print('')
    print('   <Mapping File> : Should be a .csv file that has')
    print('       <Name_firstlast>,<studentid>,<ucinetid>,<randomid>,<canvasid> as the first five columns.')
    print('       To run this program, there should be a mapping between the <randomid> and the <canvasid>.')
    print('')
    print('   <Clickstream Data Directories> :  A list of paths to the data directories where all the clickstream ')
    print('        data are stored, each path for one course.')
    print('')
    print('')
    exit()


class DeidentifyClickstream():

    def __init__(self, mapping_file, data_dirs):
        """
        Parameters
        ----------
        mapping_file : str
            Should be a .csv file that has
            <Name_firstlast>,<studentid>,<ucinetid>,<randomid>,<canvasid> as the first five columns.
        data_dir : str
            Data directory where all the clickstream .csv files are in.
        """
        if not os.path.exists(mapping_file):
            print("ERROR! No such mapping file exists! Exiting.")
            exit()
        self.keys = StudentKeys(mapping_file, new_student_files=None)  # no new student file. Just load the data

        dirs = []
        with open(data_dirs, 'r') as f:
            for data_dir in f:
                data_dir_path = data_dir.splitlines()[0]
                if not os.path.exists(data_dir_path):
                    print('Directory %s does not exist!' % data_dir_path)
                    exit()
                dirs.append(data_dir_path)

        for data_dir in dirs:
            self.process_clickstream_data(data_dir)

        self.keys.write_mapping_file()



    def process_clickstream_data(self, data_dir):
        print('Processing the Clickstream Data')

        no_rid = []
        deidentified_dir = os.path.join(data_dir, 'deidentified')
        processed_dir =  os.path.join(data_dir, 'processed')
        make_dir(deidentified_dir)
        make_dir(processed_dir)

        for fname in os.listdir(data_dir):
            if re.search(r'[a-zA-Z0-9]+-[0-9]+.csv', fname):
                namesplit = fname[:-4].split('-')
                cid = int(namesplit[-1])
                ucid = ""
                if len(namesplit) == 2:
                    ucid = namesplit[0]
                    if cid not in self.keys.cid2ucid.keys():
                        if self.keys.ucid2nsrc.get(ucid, None) is None:
                            no_rid.append(ucid)
                            continue
                        else:
                            self.keys.update_canvas_ID(ucid, cid, "")

                elif len(namesplit) == 1:
                    if cid in self.keys.cid2ucid.keys():
                        ucid = self.keys.cid2ucid[cid]
                if ucid == "":
                    print('[ERROR]: Cannot find UCINetID for the student with CanvasID: %d' % cid)
                    return

                rid = self.keys.ucid2nsrc[ucid][2]
                src = os.path.join(data_dir, fname)
                new = os.path.join(deidentified_dir, str(rid)+'.csv' )
                dest = os.path.join(processed_dir, fname)

                print(src +' -> '+ new + '\n')
                # Remove the first two columns
                self.write_deidentified_csv(src, new, rid)
                # Move the original file
                os.rename(src, dest)

        if len(no_rid) > 0:
            print("\n----------------------------------------------------------------------")
            print("     The following UCINetIDs did not have UCINetID-RandomID mapping.")
            print("         Please update the master mapping file (%s) and try again.\n" % self.keys.mapping_file)
            print("   ".join(no_rid))
            print("\n----------------------------------------------------------------------\n")


    def write_deidentified_csv(self, src_file, dst_file, newid, debug=False):

        if debug:
            print('--> Loading ', src_file, ' and removing the first two columns and saving it to ', dst_file)
            sys.stdout.flush()

        with open(src_file, 'r') as fp:
            reader = csv.reader(fp)
            data = [[str(newid)] + row[2:] for row in reader]
        data[0][0] = 'roster_randomid'

        with open(dst_file, 'w', newline='') as fp:
            cwriter = csv.writer(fp)
            cwriter.writerows(data)



if __name__ == "__main__":

    if len(sys.argv) < 3:
        print_usage_deidentify()

    mapping_file = sys.argv[1]
    data_dirs = sys.argv[2]
    print(mapping_file)

    deiden = DeidentifyClickstream(mapping_file, data_dirs)

