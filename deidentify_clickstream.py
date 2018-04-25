from update_keys import *

__author__ = 'jihyunp'

def print_usage_deidentify():
    print('')
    print('----------------------------------------------------------------------------------------------')
    print('** Usage: python ./deidentify_clickstream.py <Mapping File> <Clickstream Data Directory> ')
    print('** Example: python  ./deidentify_clickstream.py  ./master_keys.csv  ./identifiable_data/MATH-Clickstream ')
    print('----------------------------------------------------------------------------------------------')
    print('')
    print('   <Mapping File> : Should be a .csv file that has')
    print('       <Name_firstlast>,<studentid>,<ucinetid>,<randomid>,<canvasid> as the first five columns.')
    print('       To run this program, there should be a mapping between the <randomid> and the <canvasid>.')
    print('')
    print('   <Clickstream Data Directory> :  Path to the data directory where all the clickstream ')
    print('        data are in..')
    print('')
    print('')
    exit()


class DeidentifyClickstream():

    def __init__(self, mapping_file, data_dir):
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

        self.keys = StudentKeys(mapping_file, new_students_file=None)  # no new student file. Just load the data
        self.data_dir = data_dir
        self.process_clickstream_data()
        self.keys.write_mapping_file()


    def process_clickstream_data(self):
        print('\nStep 2: Processing the Clickstream Data')
        data_dir = self.data_dir
        if not os.path.isdir(data_dir):
            print('[ERROR]: Data directory '+data_dir+' does not exist!')
            exit()

        no_rid = []
        deidentified_dir = os.path.join(data_dir, 'deidentified')
        processed_dir =  os.path.join(data_dir, 'processed')
        make_dir(deidentified_dir)
        make_dir(processed_dir)

        for fname in os.listdir(data_dir):
            if fname.endswith('.csv') and fname[-8:-4].isdigit():
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
            print '--> Loading ', src_file, ' and removing the first two columns and saving it to ', dst_file,
            sys.stdout.flush()

        with open(src_file, 'r') as fp:
            reader = csv.reader(fp)
            data = [[str(newid)] + row[2:] for row in reader]
        data[0][0] = 'roster_randomid'

        with open(dst_file, 'w') as fp:
            cwriter = csv.writer(fp)
            cwriter.writerows(data)



if __name__ == "__main__":

    if len(sys.argv) < 3:
        print_usage_deidentify()

    mapping_file = sys.argv[1]
    data_dir = sys.argv[2]

    deiden = DeidentifyClickstream(mapping_file, data_dir)

