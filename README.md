# De-identifying Scripts

Jihyun Park (`jihyunp@uci.edu`)  
Aug 24, 2017

Renzhe Yu (`renzhey@uci.edu`)  
Apr 6, 2019

To deidentify clickstream data, you need to first run 'update_keys.py' which updates the 'master_keys.csv' file.


### `update_keys.py`
Reads the data files of a list of courses and updates the mapping file that keeps student identifiers. 

* Usage: `python ./update_keys.py <Mapping File> <New Student Files>`
* Example: `python  ./update_keys.py  ./master_keys.csv  ./new_merged_files.txt`


### `deidentify_clickstream.py`
Based on the mapping file, de-identifies the clickstream data of a list of courses. Running this file will 
create two folders inside each clickstream directory of a course: `processed/` and `deidentified/`

* Usage: `python ./deidentify_clickstream.py <Mapping File> <Clickstream Data Directories>`
* Example: `python  ./deidentify_clickstream.py  ./master_keys.csv  ./clickstream_folders.txt `


### `deidentify_merged_data.py`
Based on the mapping file, de-identifies a list of student-level merged data files, each for a single course. It will 
create another file with the same name with 'DEID' at the end which has the random id column at the first column but 
does not have any identifiable columns. Make sure that you have already updated/created the mapping file using the 
merged file that you are about to deidentify.


### `deidentify_quiz_data.py`
Reads the mapping file (e.g. 'master_keys.csv') and then de-identifies <br>
quiz submission data in the folder. (This script is only for MathXX-FaXX). <br>
It will create two folders inside the existing data directory : processed/ and deidentified/


### `master_keys.csv`
Mapping file where the first five columns correspond to <br>
`[Name_firstlast],[studentid],[ucinetid],[randomid],[canvasid],` 
and the columns after that indicate whether the student had taken a specific course or not.

