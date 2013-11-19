#!/usr/bin/env python2
#
#       A simple script to automate folder creation, organization of files
#       and conversion to 3D NifTi using MRICRON
#       Created by Dr. Mithun , MMST, IIT Kharagpur
#
#                       For WINDOWS
#
import sys
import ConfigParser
import os, fnmatch
import glob
import shutil
import subprocess
import getpass

#ACTUAL SCRIPT MAKE MY LIFE EASIER
def makemylifeeasier():
        file_length = file_len('C:\Scripts\pairs.conf')
        number_of_pairs = (file_length-9)/7
        #Start reading pairs
        x = 1
        config = ConfigParser.ConfigParser()
        config.read('C:\Scripts\pairs.conf')
	PATH = config.get('path','path')
	JOB = config.get('job','job_folder')
	T_ONE_FOLDER = config.get('t1','t_one')
	T_ONE = config.get('t1','t_one_kind_of')
	print 'Creating folder '+T_ONE_FOLDER
	try:
                os.makedirs(T_ONE_FOLDER)
        except WindowsError:
                print 'Folder '+T_ONE_FOLDER+' exists. Skipping creation'
	#Create other files folder
	OTHER_FILES = config.get('other','other_files')
	print 'Creating folder '+OTHER_FILES
	#Clean up unwanted files first
	try:
                os.makedirs(OTHER_FILES)
        except WindowsError:
                print 'Folder '+OTHER_FILES+' exists. Skipping creation'
	#move FSL files
	print 'Moving FSL files to '+OTHER_FILES+'\n'
	for filename in glob.glob('*FSL*'):
                #move it!
                shutil.move(filename,OTHER_FILES)
                print 'Moved '+filename
	#move PAR files
        print 'Moving PAR files to '+OTHER_FILES+'\n'
	for filename in glob.glob('*.PAR'):
                #move it!
                shutil.move(filename,OTHER_FILES)
                print 'Moved '+filename
	#move REC files
        print 'Moving REC files to '+OTHER_FILES+'\n'
	for filename in glob.glob('*.REC'):
                #move it!
                shutil.move(filename,OTHER_FILES)
                print 'Moved '+filename
	#move the actual T1 file to T1 folder
	t1 = glob.glob('*'+T_ONE+'*.nii')
	if not t1:
                print 'No T1 file found'
                tone_not_found=1
        else:
                #move it!
                print 'Moving T1 NII file to '+T_ONE_FOLDER
                shutil.move(t1[0],T_ONE_FOLDER)
                tone_not_found=0
	#Start moving individual data files
	#Call dcm2nii and convert to 3D NifTi
	#Also create analysis folders
        while (number_of_pairs >= x):
                y=str(x)
                DATA = config.get(y,'data_folder')
                ANALYSIS = config.get(y,'analysis_folder')
                KIND_OF = config.get(y,'kind_of')
                DISCARD = config.get(y,'discard')
                MATLAB_PREPROCESS_SCRIPT = config.get(y,'matlab_preprocess_script')
		MATLAB_ANALYSIS_SCRIPT = config.get (y,'matlab_analysis_script')
                #check if kind of file exists
                data_file = glob.glob('*'+KIND_OF+'*.nii')
                if not data_file:
                        print 'No file with string '+KIND_OF+', related to the '+DATA+' folder found'
                else:
                        #create folders
                        print 'Creating Folder ' +DATA
                        try:
                                os.makedirs(DATA)
                        except WindowsError:
                                print 'Folder '+DATA+' exists. Skipping creation'
                        #Move the data file
                        print 'Moving '+data_file[0]
                        shutil.move(data_file[0],DATA)
                        #Covert to 3D NifTi by calling dcm2nii
                        print 'Executing MRICRON'
                        subprocess.call(PATH+'\dcm2nii.exe '+os.path.abspath('')+'\\'+DATA+'\\'+data_file[0])
                        #Discard user specified volumes
                        matches = []
                        for root, dirnames, filenames in os.walk(DATA):
                                for discard in DISCARD:
                                        discard = str(discard).zfill(3)
                                        for filename in fnmatch.filter(filenames, 'f*'+discard+'.nii'):
                                                matches.append(os.path.join(root, filename))
                        for discardvolume in matches:
                                print 'Deleting '+discardvolume
                                os.remove(discardvolume)
                        print 'Creating Folder ' +ANALYSIS
                        try:
                                os.makedirs(ANALYSIS)
                        except WindowsError:
                                print 'Folder '+ANALYSIS+' exists. Skipping creation'
                        if (MATLAB_PREPROCESS_SCRIPT == ''):
                                print 'Matlab preprocess batch file not specified. Skipping processing'
                        else:
                                try:
                                        #check if script file is present
                                        filetry=open('C:\Scripts\\'+MATLAB_PREPROCESS_SCRIPT+'.m')
                                except IOError:
                                        print 'Matlab preprocessing script file not found. '
                                        try:
                                                input = raw_input('Enter to continue. Press CTRL+C to quit')
                                        except NameError:
                                                pass
                                else:
                                        #Script file present. GAME ON!
                                        scan_folder = os.path.abspath('')+'\\'+DATA
                                        if (tone_not_found == 1):
                                                #T1 file was not present in subjec files
                                                #Prcocessing cannot continue. Get it from user!
                                                print 'T1 file was not found. Processing cannot continue!'
                                                print 'Press CTRL+C to quit.'
                                                t_one = raw_input('Or input the absolute path to T1 file :')
                                        else:
                                                t_one = os.path.abspath('')+'\\'+T_ONE_FOLDER+'\\'+t1[0]
                                                to_run = MATLAB_PREPROCESS_SCRIPT+'(\''+scan_folder+'\',\''+t_one+'\')'
                                                print 'Start Processing in Matlab. Go Go Go!'
                                                #Call matlab WITH GUI. Calling without GUI fails to print .ps file for preprocessing
                                                Command = 'matlab -wait -r "'+to_run+'",exit'
                                                os.system(Command)
                                                print 'Data Processing complete'
                        if (MATLAB_ANALYSIS_SCRIPT == ''):
                                print 'Matlab analysis batch file not specified. Skipping analysis'
                        else:
                                try:
                                        #check if script file is present
                                        filetry=open('C:\Scripts\\'+MATLAB_ANALYSIS_SCRIPT+'.m')
                                except IOError:
                                        print 'Matlab analysis script file not found. '
                                        try:
                                                input = raw_input('Enter to continue. Press CTRL+C to quit')
                                        except NameError:
                                                pass
                                else:
                                        #Script file present. GAME ON!
                                        scan_folder = os.path.abspath('')+'\\'+DATA
                                        analysis_folder = os.path.abspath('')+'\\'+ANALYSIS
                                        to_run = MATLAB_ANALYSIS_SCRIPT+'(\''+analysis_folder+'\',\''+scan_folder+'\')'
                                        print 'Start Analysis in Matlab. Go Go Go!'
                                        #Call matlab WITHOUT GUI. Printing .ps file for analysis works from command line
                                        Command = 'matlab -wait -nodesktop -nosplash -r "'+to_run+'",exit'
                                        os.system(Command)
                                        print 'Analysis complete!'
                x=x+1
        try:
                os.makedirs(JOB)
        except WindowsError:
                print 'Folder '+JOB+' exists. Skipping creation'
        print '\n\nThanks for using the script'
        print 'Your life has been made easier :P'
        try:
            input = raw_input('Press Enter to continue')
        except NameError:
                pass
        print 'Bye '+getpass.getuser()+' :)'
	sys.exit()

#GET FILE LENGTH       
def file_len(fname):
        with open(fname) as f:
                for i, l in enumerate(f):
                        pass
        return i + 1

#CREATE CONFIGURATION FILE IF NOT PRESENT
def makefile():
        try:
                pair_number = int(raw_input('Enter the number of data and analysis folder pairs :'))
        except ValueError:
                print('Not an integer! Please enter a integer')
                makefile()
        x = 0;
        while (pair_number > x):
                y = str(x+1) 
                print 'Enter details for pair number '+y
                data_folder = raw_input('Please enter the name of data folder (eg:-data_working_memory) :')
                analysis_folder = raw_input('Please enter the name of analysis folder (eg:-analysis_working_memory) :')
                kind_of = raw_input('Enter the kind of file that goes to the data folder :')
                discard = raw_input('Enter the volumes to be discarded, separated by commas (eg:- 1,2,45,46) :')
                matlab_preprocess_script = raw_input('Enter the absolute path to MATLAB preprocess batch file :')
                matlab_analysis_script = raw_input('Enter the absolute path to MATLAB analysis batch file :')
                #check whether file already exists
                if not os.path.isfile('C:\Scripts\pairs.conf'):
                        #file doesn't exist. Add first pair data to it
                        file = open('C:\Scripts\pairs.conf', 'w+')
                        file.write('['+y+']\n')
                        file.write('data_folder='+data_folder+'\n')
                        file.write('analysis_folder='+analysis_folder+'\n')
                        file.write('kind_of='+kind_of+'\n')
                        file.write('discard='+discard+'\n')
                        file.write('matlab_preprocess_script='+matlab_preprocess_script+'\n')
                        file.write('matlab_analysis_script='+matlab_analysis_script+'\n')
                        file.close()
                else:
                        #file exists! Append the pair data
                        file = open('C:\Scripts\pairs.conf', 'a')
                        file.write('['+y+']\n')
                        file.write('data_folder='+data_folder+'\n')
                        file.write('analysis_folder='+analysis_folder+'\n')
                        file.write('kind_of='+kind_of+'\n')
                        file.write('discard='+discard+'\n')
                        file.write('matlab_preprocess_script='+matlab_preprocess_script+'\n')
                        file.write('matlab_analysis_script='+matlab_analysis_script+'\n')
                        file.close()
                x = x + 1
        t_one = raw_input('Enter the T1 folder name :')
        t_one_kind_of = raw_input('Enter the kind of file that goes to T1 folder :')
        other_files = raw_input('Enter the folder for all other files :')
        job = raw_input('Enter the jobs folder name :')
        path = raw_input('Enter the folder where dcm2nii.exe is located. Your MRICRON folder :')
        file = open('C:\Scripts\pairs.conf', 'a')
        file.write('[path]\n')
        file.write('path='+path+'\n')
        file.write('[t1]\n')
        file.write('t_one='+t_one+'\n')
        file.write('t_one_kind_of='+t_one_kind_of+'\n')
        file.write('[other]\n')
        file.write('other_files='+other_files+'\n')
        file.write('[job]\n')
        file.write('job_folder='+job+'\n')
        file.close()
	print ('\n\nConfiguration file created. Run program again')
	try:
            input = raw_input('Press Enter to continue')
        except NameError:
                pass
        sys.exit()

#START
#Check whether configuration file is present
try:			
        filetry=open('C:\Scripts\pairs.conf')
#Create if not present
except IOError:
        print 'Hello '+getpass.getuser()+','
        print 'This is a simple script to automate folder creation, organization and 3D NifTi conversion'
        print 'Written in Python & Compiled using PyInstaller'
	print '\n\nConfiguration file does not exist'
	print 'First run? Lets configure your data and analysis folders'
	print 'This will create a configuration file(pairs.conf)\nin the C:\Scripts folder\n\n'
	makefile()
#File present. GAME ON!
else:
	makemylifeeasier()
