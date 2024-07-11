# Hi, i'm Vitor Lamoya and this is my resolution for your task ;;
# I decided to comment on every step of the process, so that the code is better understandable and easier to maintenance.
#
# I would like to thank you for the opportunity and say that it was of great importance in my professional career, 
# as in carrying out this task I was able to put into practice all the concepts I learned in courses I took and it also led me
# to research various libraries, functions and methodologies of code that had not yet had contact.
#
# Command to run: python sync_folders.py "C:\Users\{Computer name}\Desktop\myFolderTest\source" "C:\Users\{Computer name}\Desktop\myFolderTest\replica" 60 "C:\Users\{Computer name}\Desktop\myFolderTest\sync.log"
#

# The first step is the import of the libraries:

import os #Used for file and directory manipulation
import shutil #Used to copy and move files and directories
import time #Used to obtain time-related functions
import hashlib #Used to calculate MD5 hashes of files to compare contents.
import argparse #Used to parse arguments passed through the command line
import logging #Used to record and track events that occur during the execution of a program

# The second step is the creation of the "calc_md5" function to check the integrity of the files, 
# detect changes, minimize unnecessary copies and remove files of the "replica" foulder that are no longer in the "source" foulder

def calc_md5(file_path):
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logging.error(f"Failed to calculate MD5 for {file_path}: {e}")
        return None
    
# The third step is the creation of the "sync_foulders" function.

def sync_folders(source, replica):
    logging.info(f'Starting synchronization from {source} to {replica}')

    if not os.path.exists(source): #Check if the "source" folder exists!
        logging.error(f'Source folder {source} does not exist') #If it does not exist, we record this error in the log
        return
    if not os.path.exists(replica): #Check if the "replica" folder exists!
        try:
            logging.info(f'Replica folder {replica} does not exist, creating it') #If it does not exist, we record this error in the log
            os.makedirs(replica) #And we create the folder using the following function from the "os" library
        except Exception as e:
            logging.error(f'Failed to create replica folder {replica}: {e}')
            return
    
    source_files = {} #Initialize the "source_files" dictionary!
    replica_files = {} #Initialize the "replica_files" dictionary!

    for root, dirs, files in os.walk(source): #We traverse all directories and files in the "source" directory
        # "root" is the current directory.
        # "files" Is a list of files inside "root".
        for file in files:
            source_path = os.path.join(root, file) # Construct the full path of the file
            relative_path = os.path.relpath(source_path, source) # Calculates the relative path of the file in relation to the "source" directory
            source_files[relative_path] = calc_md5(source_path) # Calculate the MD5 hash of the file and store it in the "source_files" dictionary
        
    for root, dirs, files in os.walk(replica): #We traverse all directories and files in the "replica" directory
        # "root" is the current directory.
        # "files" Is a list of files inside "root".
        for file in files:
            replica_path = os.path.join(root, file) # Construct the full path of the file
            relative_path = os.path.relpath(replica_path, replica) # Calculates the relative path of the file in relation to the "replica" directory
            replica_files[relative_path] = calc_md5(replica_path) # Calculate the MD5 hash of the file and store it in the "replica_files" dictionary
    
    # The Fourth step is responsible for synchronizing files from the "source" folder to the "replica" folder

    for relative_path, md5 in source_files.items(): # Used to loop through each item in the "source_files" dictionary
        # "relative_path" is the relative path of the file.
        # "md5" is the MD5 hash of the file.
        source_path = os.path.join(source, relative_path) # Builds the full path of the file in the "source" folder
        replica_path = os.path.join(replica, relative_path) # Builds the full path of the file in the "replica" folder
        # Checks if the file exists in the "replica" folder, or whether the MD5 hash of the file in the "source" folder is different from the MD5 hash of 
        # the corresponding file in the "replica" folder
        if relative_path not in replica_files or source_files[relative_path] != replica_files[relative_path]:
            try:
                # Create directories in the "replica" folder
                os.makedirs(os.path.dirname(replica_path), exist_ok=True)
                # Copy the file from "source" to "replica"
                shutil.copy2(source_path, replica_path)
                # Log the copy operation in the log and print a message to the console
                logging.info(f'Copied: {source_path} to {replica_path}')
                print(f'Copied: {source_path} to {replica_path}')
            except Exception as e:
                # If an error occurs, log the error message to the log
                logging.error(f'Failed to copy {source_path} to {replica_path}: {e}')
    
    # The Fifth step is remove files from the "replica" folder that do not exist in the "source" folder!
    # Cycle through all files in the "replica_files" dictionary, where "relative_path" is the relative path of the file in the "replica" folder
    for relative_path in replica_files.keys():
        # Checks if the file does not exist in the "source_files" dictionary, which means it has been removed from the "source" folder 
        # and should therefore be removed from the "replica" folder
        if relative_path not in source_files:
            try:
                os.remove(os.path.join(replica, relative_path)) # Remove the file from the "replica" folder
                # Records the remove operation in the log and prints a message to the console
                logging.info(f'Removed: {os.path.join(replica, relative_path)}')
                print(f'Removed: {os.path.join(replica, relative_path)}')
            except Exception as e:
                # If an error occurs while removing the file, an error message is recorded in the log.
                logging.error(f'Failed to remove {os.path.join(replica, relative_path)}: {e}')
    
def main():
    # We created an argument parser, which contains all the information necessary for the code to function.
    parser = argparse.ArgumentParser(description='Folder Synchronization Script')
    parser.add_argument('source', type=str, help='Source folder path')
    parser.add_argument('replica', type=str, help='Replica folder path')
    parser.add_argument('interval', type=int, help='Synchronization interval in seconds')
    parser.add_argument('log_file', type=str, help='Log file path')

    # We assign to the variable "args", the arguments informed in the parser
    args = parser.parse_args()

    # Configures logging to record messages in a log file informed in "args.log_file"
    logging.basicConfig(filename=args.log_file, level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Add the log to the console as well
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)

    while True:
        sync_folders(args.source, args.replica)
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
