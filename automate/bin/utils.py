import os
import shutil
import re
import glob

# Functions in this utils.py file:
# copy_files_with_prefix(src_directory, dest_directory, prefix)
# read_all_files(directory)
# format_title_re(title)
# copy_files(src_dir, dst_dir, files)
# process_word(word)
# copy_directory_contents(source_dir, destination_dir)
# read_files_replace_variables(root_directory, variable_dict)
# replace_placeholders_in_files(root_directory, variable_dict)
# copy_file(source_file, destination_dir)
# copy_files_by_pattern(source_pattern, destination_dir)
# delete_specific_file_or_dir(path)
# create_directory(path)
# create_empty_file(file_path)

def create_empty_file(file_path):
    #print(f">>> === FILEPATH: {file_path} === <<<")
    """
    Creates an empty file at the specified file path.
    
    Parameters:
    file_path (str): The path where the empty file will be created.
    """
    # Check if the file already exists
    if not os.path.exists(file_path):
        # Create an empty file
        with open(file_path, 'w') as file:
            pass
        #print(f"Empty file created at: {file_path}")
    else:
        print(f"File already exists at: {file_path}")

# # Example usage
# create_empty_file("empty_file.txt")



def create_directory(path):
    """
    Creates a directory at the specified path. If the directory already exists,
    no action is taken. Intermediate directories are also created if they do not exist.
    
    :param path: Path where the directory will be created.
    :type path: str
    """
    try:
        os.makedirs(path, exist_ok=True)  # 'exist_ok=True' prevents error if directory already exists
        #print(f"Directory '{path}' created successfully.")
    except Exception as e:
        print(f"Error: Failed to create directory '{path}'. Reason: {str(e)}")

# # Example usage:
# create_directory('/one/two/three')  # Specify the full path to create


def delete_specific_file_or_dir(path):
    """
    Deletes a file or directory at a specified path.
    
    :param path: Path to the file or directory to be deleted.
    :type path: str
    """
    if not os.path.exists(path):
        print(f"Warning: The item '{path}' does not exist and cannot be deleted.")
        return

    try:
        if os.path.isdir(path):
            # If the path is a directory, remove it along with all its contents
            shutil.rmtree(path)
            print(f"Directory '{path}' has been deleted successfully.")
        else:
            # If the path is a file, remove it directly
            os.remove(path)
            print(f"File '{path}' has been deleted successfully.")
    except Exception as e:
        print(f"Error: Failed to delete '{path}'. Reason: {str(e)}")

# # Example usage:
# delete_specific_item('/one/two/file.txt')  # Specify the full path to the file or directory


def copy_files_by_pattern(source_pattern, destination_dir):
    try:
        # Create destination directory if it doesn't exist
        os.makedirs(destination_dir, exist_ok=True)
        
        # Find all files matching the source pattern
        files_to_copy = glob.glob(source_pattern)
        
        for source_file in files_to_copy:
            # Extract the filename from the source path
            filename = os.path.basename(source_file)
            
            # Construct the destination path
            destination_file = os.path.join(destination_dir, filename)
            
            # Copy the file
            shutil.copy2(source_file, destination_file)
            
            print(f"File '{source_file}' copied to '{destination_file}' successfully.")
    
    except IOError as e:
        print(f"Error: {e}")

# # Example usage:
# source_pattern = '/path/to/source/*.txt'  # Example: all .txt files in /path/to/source/
# destination_directory = '/path/to/destination/directory'

# copy_files_by_pattern(source_pattern, destination_directory)


def copy_file(source_file, destination_dir):
    try:
        # Create destination directory if it doesn't exist
        os.makedirs(destination_dir, exist_ok=True)
        
        # Extract the filename from the source path
        filename = os.path.basename(source_file)
        
        # Construct the destination path
        destination_file = os.path.join(destination_dir, filename)
        
        # Copy the file
        shutil.copy2(source_file, destination_file)
        
        #print(f"File '{source_file}' copied to '{destination_file}' successfully.")
    except IOError as e:
        print(f"Error: {e}")

# # Example usage:
# source_file_path = '/path/to/source/file.txt'
# destination_directory = '/path/to/destination/directory'

# copy_file(source_file_path, destination_directory)


def replace_placeholders_in_files(root_directory, variable_dict):
    # Walk through all files and directories starting from root_directory
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            # Construct the full path to the file
            file_path = os.path.join(dirpath, filename)
            
            # Read the file contents
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Replace placeholders (__var__) with corresponding values from variable_dict
            for key, value in variable_dict.items():
                placeholder = f'{key}'
                content = re.sub(placeholder, str(value), content)
            
            # Write the modified content back to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            #print(f"Modified '{file_path}' successfully.")

# # Example usage:
# root_dir = '/path/to/your/root/directory'
# variables = {
#     'var1': 'replacement1',
#     'var2': 123,
#     'var3': 'another replacement'
# }

# replace_placeholders_in_files(root_dir, variables)



def read_files_replace_variables(root_directory, variable_dict):
    file_contents = {}

    # Walk through all files and directories starting from root_directory
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            # Construct the full path to the file
            file_path = os.path.join(dirpath, filename)
            
            # Read the file contents
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Replace placeholders (__var__) with corresponding values from variable_dict
            for key, value in variable_dict.items():
                placeholder = f'{key}'
                #print(f"Replacing '{placeholder}' with '{value}' in '{file_path}'")
                content = re.sub(placeholder, str(value), content)
            
            # Store content in dictionary with file path as key
            file_contents[file_path] = content
    
    return file_contents

# # Example usage:
# root_dir = '/path/to/your/root/directory'
# variables = {
#     'var1': 'replacement1',
#     'var2': 123,
#     'var3': 'another replacement'
# }

# files_content = read_files_replace_variables(root_dir, variables)

# # Example to print the content of each file
# for file_path, content in files_content.items():
#     print(f"Content of '{file_path}':")
#     print(content)
#     print('-' * 50)


def copy_directory_contents(source_dir, destination_dir):
    try:
        # Create destination directory if it doesn't exist
        os.makedirs(destination_dir, exist_ok=True)
        
        # Iterate over files and subdirectories in the source directory
        for item in os.listdir(source_dir):
            source_item = os.path.join(source_dir, item)
            destination_item = os.path.join(destination_dir, item)
            
            # Copy if it's a file
            if os.path.isfile(source_item):
                shutil.copy2(source_item, destination_item)
            # Recursively copy if it's a directory
            elif os.path.isdir(source_item):
                shutil.copytree(source_item, destination_item, symlinks=True)
        
        print(f"Contents of '{source_dir}' copied to '{destination_dir}' successfully.")
    except OSError as e:
        print(f"Error: {e}")

# # Usage example:
# source_directory = '/path/to/source_directory'
# destination_directory = '/path/to/destination_directory'
# copy_directory_contents(source_directory, destination_directory)


def copy_files_with_prefix(src_directory, dest_directory, prefix):
    # Create the destination directory if it doesn't exist
    if not os.path.exists(dest_directory):
        os.makedirs(dest_directory)

    # Use glob to get a list of all files in the source directory
    files = glob.glob(os.path.join(src_directory, '*'))
    
    # Iterate through the files and copy those that start with the given prefix
    for file in files:
        if os.path.basename(file).startswith(prefix):
            shutil.copy(file, dest_directory)
            print(f"Copied: {file} to {dest_directory}")

# # Example usage
# src_directory = 'path/to/source/directory'
# dest_directory = 'path/to/destination/directory'
# prefix = 'your_prefix'

# copy_files_with_prefix(src_directory, dest_directory, prefix)


def read_all_files(directory):
    # Use glob to get a list of all files in the directory
    files = glob.glob(os.path.join(directory, '*'))
    return files

# # Example usage
# directory = 'path/to/your/directory'
# file_list = read_all_files(directory)

# print("Files in directory:")
# for file in file_list:
#     print(file)


def format_title_re(title):
    # Insert an underscore before all caps, then convert to lowercase
    formatted_title = re.sub(r'(?<!^)(?=[A-Z])', '_', title).lower()
    return formatted_title


def copy_files(src_dir, dst_dir, files):
    # Check if the source directory exists
    if not os.path.exists(src_dir):
        print(f"Source directory '{src_dir}' does not exist.")
        return

    # Ensure the destination directory exists
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
        print(f"Destination directory '{dst_dir}' created.")

    # Copy each file from the source to destination directory
    for file_name in files:
        src_file_path = os.path.join(src_dir, file_name)
        dst_file_path = os.path.join(dst_dir, file_name)

        # Check if the file exists before copying
        if os.path.exists(src_file_path):
            shutil.copy2(src_file_path, dst_file_path)
            print(f"Copied {file_name} to {dst_dir}.")
        else:
            print(f"File {file_name} does not exist in the source directory.")

# Example usage
# source_directory = "/path/to/source"
# destination_directory = "/path/to/destination"
# files_to_copy = ["file1.txt", "file2.txt", "file3.txt"]

# copy_files(source_directory, destination_directory, files_to_copy)


def process_word(word):
    # Define the padding sequence
    padding_sequence = "abcde"
    
    # Check the length of the word
    if len(word) > 3:
        # If more than 4 characters, extract the first four
        return word[:3]
    elif len(word) < 3:
        # If less than 4 characters, pad with the sequence
        return word + padding_sequence[:3-len(word)]
    else:
        # If exactly 4 characters, return the word as is
        return word

# # Example usage
# words = ["hello", "test", "hi", "word"]
# processed_words = [process_word(word) for word in words]
# print(processed_words)  # Output will be ['hell', 'test', 'hiab', 'word']
