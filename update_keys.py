import sys
import os
import csv
from random import sample
import numpy as np
import pandas as pd
from shutil import copyfile


__author__ = 'jihyunp'
__author__ = 'renzhey'

def make_dir(dir_path):
    if not os.path.exists(dir_path):
        print('making ', dir_path)
        os.makedirs(dir_path)

def print_usage():
    print('')
    print('----------------------------------------------------------------------------------------------')
    print('** Usage: python ./update_keys.py <Mapping File> <New Student Files> ')
    print('** Example: python  ./update_keys.py  ./master_keys.csv  ./new_merged_files.txt ')
    print('----------------------------------------------------------------------------------------------')
    print('')
    print('   <Mapping File> : A .csv file that has')
    print('       <Name_firstlast>,<studentid>,<ucinetid>,<randomid>,<canvasid> as the first five columns.')
    print('       If there is no file with this name, a new mapping file will be created with this name.')
    print('')
    print('   <New Student Files> :  A .txt file that lists .csv or .dta files (with path) of new student data. ')
    print('       The .csv or .dta files are like ../Year1/Physics3A_Merged_data.csv ')
    print('       In each .csv file, the first row should be the name of each column, and it should have at least ')
    print('       "studentid", "ucinetid", "name_firstlast" ')
    print('       Once a random ID is assigned to a student, that random ID will not be updated.')
    print('')
    exit()


class StudentKeys():

    def __init__(self, mapping_file, new_student_files=None):
        self.mapping_file = mapping_file
        self.old_mapping_file = mapping_file.split(".csv")[0] + "_old.csv"

        self.ucid2nsrc = {} # UCINetID to [Name, StudentID, RandomID, CanvasID]
        self.ucid2coursearr = {} # UCINetID to array of course indicator (1 if the student has taken the course)
        self.cid2ucid = {} # CanvasID to UCINetID
        self.cid2rid = {}
        # self.name2ucid = {}
        self.course_headers = []
        self.load_mapping_file()

        if new_student_files is not None:

            self.new_student_files = []
            with open(new_student_files, 'r') as f:
                for file in f:
                    file_path = file.splitlines()[0]
                    if not os.path.exists(file_path):
                        print('File %s does not exist!' % file_path)
                        exit()
                    self.new_student_files.append(file_path)

            for file in self.new_student_files:
                new_course_name = self.get_course_name_from_st_file(file)
                if new_course_name not in self.course_headers:
                    self.course_headers.append(new_course_name)
                self.load_new_info_and_update_map(file)
                self.write_mapping_file()


    def get_course_name_from_st_file(self, students_fpath):
        import re
        students_fname = students_fpath.split("/")[-1]
        return re.match(r"[A-Za-z ]+[0-9]+[A-Za-z]?\s\d{1,4}[A-Za-z]+\s?\d?", students_fname).group(0).strip()


    def load_mapping_file(self):
        mapping_file = self.mapping_file
        # Check the file type

        if not mapping_file.endswith('.csv'):
            print('[ERROR]: Mapping file should be a csv file')
            print_usage()

        if os.path.exists(mapping_file):
            print('\n*** Loading mapping file "' + mapping_file + '"')
            with open(mapping_file, 'r') as f:
                reader = csv.reader(f, delimiter=',')
                header = next(reader)
                self.course_headers = header[5:]
                for row in reader:
                    name = row[0]
                    stid = row[1]  # Student ID is string due to the extension students
                    ucid = row[2].lower()
                    rid = int(row[3])
                    cid = int(row[4])
                    self.ucid2nsrc[ucid] = [name, stid, rid, cid]
                    self.cid2ucid[cid] = ucid
                    self.cid2rid[cid] = rid
                    self.ucid2coursearr[ucid] = row[5:]
        else:
            print('\n*** No mapping file found. New mapping file will be created "' + mapping_file + '"')


    def load_new_info_and_update_map(self, new_student_file):

        def get_indices_from_header(header):
            indices = [-1,-1,-1,-1,-1]  # Name, Stid, UCINetid, Randomid, CanvasId
            for i, h in enumerate(header):
                h = h.lower()
                if "name_firstlast" == h:
                    indices[0] = i
                elif (indices[0] == -1) and ("name_lastfirst" == h):
                    indices[0] = i
                elif (indices[0] == -1) and ("name" == h):
                    indices[0] = i
                elif "studentid" in h:
                    indices[1] = i
                elif "ucinetid" == h:
                    indices[2] = i
                elif (indices[2] == -1) and ("sisloginid" == h):
                    indices[2] = i
                elif "roster_randomid" in h:
                    indices[3] = i
                elif "canvasid" in h:
                    indices[4] = i
                elif (indices[4] == -1) and ("id" == h):
                    indices[4] = i
            return indices

        if os.path.exists(new_student_file):

            print('\n*** Reading new student info and assigning random Ids')

            if not (new_student_file.endswith('.csv') or new_student_file.endswith('.dta')):
                print('[ERROR]: new_students_file should be either .csv or .dta ')
                print_usage()
                exit()

            print('\n*** Loading the new students file "' + new_student_file +'"')

            if new_student_file.endswith('dta'):
                data = pd.read_stata(new_student_file)
            else:
                data = pd.read_csv(new_student_file)

            header = data.columns
            name_idx, sid_idx, ucid_idx, rid_idx, cid_idx = get_indices_from_header(header)

            if ucid_idx == -1:
                print('[ERROR] There is no column called "ucinetid" in file ' + new_student_file)
                print('        Stopping the process..')
                exit()

            # Default values
            name = ''
            stid = ''  # Student ID is kept as string since the extension students had alphabets
            cid = 0

            for i, row in data.iterrows():
                ucid = row[ucid_idx].lower()

                if ucid.isalnum():
                    if name_idx > -1:
                        name = row[name_idx]
                        if len(name.split(",")) > 1:
                            namesplit = name.split(",")
                            name = namesplit[1].strip() + " " + namesplit[0].strip()
                    if sid_idx > -1:
                        stid = str(row[sid_idx])
                        if stid == 'nan':
                            stid = ''
                    if cid_idx > -1:
                        cid = str(row[cid_idx])
                        if cid == 'nan':
                            cid = 0
                        else:
                            cid = int(float(row[cid_idx]))

                    # If UCID-RandomID pair is new
                    if ucid not in self.ucid2nsrc.keys():
                        # If new UCINEtID is found
                        if rid_idx > -1:
                            # Has RandomID column
                            if row[rid_idx].isdigit():
                                # Read the existing random ID
                                rid = int(row[rid_idx])
                            else:
                                # Assign new if empty
                                rid = self.get_new_random_id(ucid)
                        else:
                            # Does not have random id column. create new one.
                            rid = self.get_new_random_id(ucid)


                        self.ucid2nsrc[ucid] = [name, stid, rid, cid]
                        self.ucid2coursearr[ucid] = list(np.zeros(len(self.course_headers)-1, dtype=np.int8))
                        self.ucid2coursearr[ucid].append(1)
                        if cid > 0:
                            self.cid2ucid[cid] = ucid
                    else:
                        # Already have UCID-RandomID pair. Check if Canvas ID also matches.
                        # If not, just update to the newer info
                        # Also check if the name was empty, and update the name to the current name
                        if cid > 0 and cid != self.ucid2nsrc[ucid][3]:
                            self.update_canvas_ID(ucid, cid, new_student_file)

                        if name_idx > -1 and len(name) > 3 and name != self.ucid2nsrc[ucid][0]:
                            # print warning if already had a different student name before.
                            # otherwise just update it
                            if len(self.ucid2nsrc[ucid][0]) > 2: # has a differnt name
                                print('[WARNING]: UCINetID <'+ucid+'> has two different names. ')
                                print('           Updating the student name for <'+ucid+'> to the one in '+new_student_file)
                            else:
                                print(' Student name for <'+ucid+'> has been updated.')
                            self.ucid2nsrc[ucid][0] = name

                        if sid_idx > -1 and len(stid.strip()) > 3 and stid != self.ucid2nsrc[ucid][1]:
                            # print warning if already had a different student id before.
                            # otherwise just update it
                            if len(self.ucid2nsrc[ucid][1]) > 2:
                                print('[WARNING]: UCINetID <'+ucid+'> has two different student IDs. ')
                                print('           Updating the student ID for <'+ucid+'> to the one in '+new_student_file)
                            else:
                                print(' Student ID for <'+ucid+'> has been updated.')
                            self.ucid2nsrc[ucid][1] = stid

                        if len(self.ucid2coursearr[ucid]) < len(self.course_headers):
                            self.ucid2coursearr[ucid].append(1)


    def update_canvas_ID(self, ucid, cid, new_student_file):
        # print warning if already had a different canvasid before. otherwise just update it
        if self.ucid2nsrc[ucid][3] > 0:  # has a canvas id before
            print('[WARNING]: UCINetID <' + ucid + '> has two different canvas IDs. ')
            print('           Updating canvas Id for <' + ucid + '> to the one in ' + new_student_file)
        else:
            print(' Canvas ID for <' + ucid + '> has been updated.')
        self.ucid2nsrc[ucid][3] = cid
        self.cid2ucid[cid] = ucid


    def get_new_random_id(self, ucid=None):
        # ucid argument is used for debugging (printing) purpose
        if ucid is not None:
            print('Assigning a new random Id for UCINetID :' + ucid)
        # Avoid random IDs that are already assigned
        rids_assigned = [rcn[2] for rcn in self.ucid2nsrc.values()]
        rid = sample(range(100000, 900000), 1)[0]
        while rid in rids_assigned:
            rid = sample(range(100000, 900000), 1)[0]
        return rid


    def write_mapping_file(self):
        mapping_file = self.mapping_file
        print('\n*** Updating mapping file "' + mapping_file +'"')
        print('  Old mapping file copied to ' + self.old_mapping_file)
        copyfile(mapping_file, self.old_mapping_file)

        header = ['name_firstlast', 'studentid', 'ucinetid', 'randomid', 'canvasid'] + self.course_headers
        with open(mapping_file, 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(header)
            for ucid in sorted(self.ucid2nsrc.keys()):
                coursearr = self.ucid2coursearr.get(ucid, [])
                while len(coursearr) < len(self.course_headers):
                    coursearr.append(0)
                writer.writerow(self.ucid2nsrc[ucid][:2] + [ucid] +
                                self.ucid2nsrc[ucid][2:] + coursearr)




if __name__ == "__main__":

    if len(sys.argv) < 3:
        print_usage()

    mapping_file = sys.argv[1]
    new_student_files = sys.argv[2]

    stkeys = StudentKeys(mapping_file, new_student_files)

