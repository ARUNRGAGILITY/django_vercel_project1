import os
import sys
import subprocess
import shutil
import configparser
import time 

from generate_urls import *
from utils import *

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read("../../config.ini")
PROJECT_BASE_DIR = config.get("paths", "PROJECT_BASE_DIR", fallback="env/dev")  # Default to "env/dev" if missing
PROJECT_PREFIX = config.get("project", "project_prefix", fallback="project")  # Default to "app_" if missing
APP_PREFIX = config.get("apps", "app_prefix", fallback="app")  # Default to "app_" if missing
APP_FILES = config.get("apps", "app_files", fallback="no")  # Default to "no" if missing
MOD_PREFIX = config.get("modules", "mod_prefix", fallback="mod")  # Default to "mod_" if missing
########################################### PROJECT RELATED ########################################################
def create_django_project(project_name, base_dir):
    """Create a new Django project if it doesn't already exist."""
    project_path = os.path.join(base_dir, project_name)

    if os.path.exists(project_path):
        print(f"Django project {project_name} exists.")
        return  # Do not exit, just return

    os.makedirs(project_path, exist_ok=True)
    subprocess.run(["django-admin", "startproject", f"project_{project_name}", project_path])
    #print(f"Django project '{project_name}' created successfully in '{project_path}'")
    print(f"Django project '{project_name}' created successfully.")
########################################### APP RELATED ########################################################
def create_django_app(project_name, app_name, base_dir):    
    """Create a new Django app in an existing project."""
    app_info = get_app_naming(project_name, app_name, base_dir)
    THIS_CODE_DIR = "."
    absolute_base_dir = os.path.abspath(THIS_CODE_DIR)
    absolute_project_path = os.path.join(absolute_base_dir)
    absolute_django_project_path = app_info["absolute_django_project_path"]
    absolute_app_path = app_info["absolute_app_path"]
    std_app_name = app_info["std_app_name"]
    app_exists = app_info["app_exists"]
    def_mod_name = app_info["def_mod_name"]
    this_mod_name = app_info["this_mod_name"]
    absolute_def_mod_path = app_info["absolute_def_mod_path"]
    absolute_this_mod_path = app_info["absolute_this_mod_path"]
    def_mod_exists = app_info["def_mod_exists"]
    this_mod_exists = app_info["this_mod_exists"]
    project_exists = app_info["project_exists"]

    if not project_exists:
        create_django_project(project_name, base_dir)

    if app_exists :
        if def_mod_exists and this_mod_exists:
            return
    if not app_exists:
        os.chdir(absolute_project_path)
        print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {absolute_project_path}")
        subprocess.run(["python", "manage.py", "startapp", std_app_name])
        print(f"Django app '{std_app_name}' created successfully.")
        if APP_FILES == "no":
            app_files = ["models.py", "tests.py", "views.py"]            
            for file in app_files:
                to_be_removed = os.path.join(std_app_name, file)                
                if os.path.exists(to_be_removed):
                    os.remove(to_be_removed)
        # create mod_app and mod_<app_name>
        if not def_mod_exists:
            create_mod(project_name, app_name, def_mod_name, base_dir)           
        if not this_mod_exists:
            create_mod(project_name, app_name, this_mod_name, base_dir)

    
########################################### MODULE RELATED ########################################################
def create_mod(project_name, app_name, mod_name, base_dir):
    """Create a new module in an existing Django app."""
    app_info = get_mod_naming(project_name, app_name, mod_name, base_dir)
    absolute_base_dir = app_info["absolute_base_dir"]
    absolute_project_path = app_info["absolute_project_path"]
    absolute_django_project_path = app_info["absolute_django_project_path"]
    absolute_app_path = app_info["absolute_app_path"]
    std_app_name = app_info["std_app_name"]
    app_exists = app_info["app_exists"]
    def_mod_name = app_info["def_mod_name"]
    this_mod_name = app_info["this_mod_name"]
    absolute_def_mod_path = app_info["absolute_def_mod_path"]
    absolute_this_mod_path = app_info["absolute_this_mod_path"]
    def_mod_exists = app_info["def_mod_exists"]
    this_mod_exists = app_info["this_mod_exists"]
    project_exists = app_info["project_exists"]
    absolute_new_mod_path = app_info["absolute_new_mod_path"]
    new_mod_exists = app_info["new_mod_exists"]
    #print(f">>> === APP PATH {absolute_app_path} === <<<")
    # absolute_base_dir = os.path.abspath(base_dir)
    print(f">>> === absolute_base_dir {absolute_base_dir} === <<<")
    absolute_project_path = os.path.join(absolute_base_dir, project_name)
    absolute_app_path = os.path.join(absolute_project_path, std_app_name)
    #print(f">>> === CORRECTED MOD PATH {absolute_app_path} === <<<")
    
    
    print(f"Django module '{mod_name}' created successfully.")

######################################################################################################################
def delete_django_project(project_name):
    """Delete an existing Django project."""
    project_path = os.path.join("env", "dev", project_name)

    if os.path.exists(project_path):
        shutil.rmtree(project_path)
        print(f"Django project '{project_name}' deleted successfully.")
    else:
        print(f"Error: Django project '{project_name}' does not exist.")


######################################################################################################################
def get_app_naming(project_name, app_name, base_dir):
    """Return standardized app names, paths, and existence checks as a dictionary."""
    #print(f">>> === NAMING APP base_dir {base_dir} === <<<")   

    # Standardized project name
    std_project_name = f"{PROJECT_PREFIX}_{project_name}" if not project_name.startswith(f"{PROJECT_PREFIX}_") else project_name
    THIS_CODE_DIR = "."
    absolute_base_dir = os.path.abspath(THIS_CODE_DIR)
    absolute_project_path = os.path.join(absolute_base_dir)
    #print(f">>> === NAMING APP absolute_base_dir {absolute_base_dir} === <<<")
    #print(f">>> === NAMING APP absolute_project_path {absolute_project_path} === <<<")
    absolute_django_project_path = os.path.join(absolute_base_dir, std_project_name)
    # Standardized app name
    std_app_name = f"{APP_PREFIX}_{app_name}" if not app_name.startswith(f"{APP_PREFIX}_") else app_name
    absolute_app_path = os.path.join(absolute_project_path, std_app_name)
    
    # Existence checks
    project_exists = os.path.exists(absolute_project_path)
    app_exists = os.path.exists(absolute_app_path)

    # Module names
    def_mod_name = f"{MOD_PREFIX}_app"
    this_mod_name = f"{MOD_PREFIX}_{app_name}"

    # Module paths
    absolute_def_mod_path = os.path.join(absolute_app_path, def_mod_name)
    absolute_this_mod_path = os.path.join(absolute_app_path, this_mod_name)

    # Check if modules exist
    def_mod_exists = os.path.exists(absolute_def_mod_path)
    this_mod_exists = os.path.exists(absolute_this_mod_path)
    #print(f">>> === NAMING APP PATH {absolute_app_path} === <<<")
    # Return as a dictionary
    return {
        "absolute_base_dir": absolute_base_dir,
        "absolute_project_path": absolute_project_path,
        "absolute_django_project_path": absolute_django_project_path,
        "absolute_app_path": absolute_app_path,
        "std_app_name": std_app_name,
        "project_exists": project_exists,
        "app_exists": app_exists,
        "def_mod_name": def_mod_name,
        "this_mod_name": this_mod_name,
        "absolute_def_mod_path": absolute_def_mod_path,
        "absolute_this_mod_path": absolute_this_mod_path,
        "def_mod_exists": def_mod_exists,
        "this_mod_exists": this_mod_exists,
    }

######################################################################################################################
def get_mod_naming(project_name, app_name, mod_name, base_dir):
    """Return the standard app name and the app directory name."""
    THIS_CODE_DIR = "."
    absolute_base_dir = os.path.abspath(THIS_CODE_DIR)
    absolute_project_path = os.path.join(absolute_base_dir)
    app_info = get_app_naming(project_name, app_name, base_dir)
    absolute_base_dir = app_info["absolute_base_dir"]
    absolute_project_path = app_info["absolute_project_path"]
    absolute_django_project_path = app_info["absolute_django_project_path"]
    absolute_app_path = app_info["absolute_app_path"]
    std_app_name = app_info["std_app_name"]
    app_exists = app_info["app_exists"]
    def_mod_name = app_info["def_mod_name"]
    this_mod_name = app_info["this_mod_name"]
    absolute_def_mod_path = app_info["absolute_def_mod_path"]
    absolute_this_mod_path = app_info["absolute_this_mod_path"]
    def_mod_exists = app_info["def_mod_exists"]
    this_mod_exists = app_info["this_mod_exists"]
    project_exists = app_info["project_exists"]

    # There are two apps we are mainly looking for: mod_app and mod_<mod_name>
    new_mod_name = mod_name
    absolute_new_mod_path = None
    new_mod_exists = False
    

    if not mod_name.startswith(f"{MOD_PREFIX}_"):
        new_mod_name = f"{MOD_PREFIX}_{mod_name}"
        absolute_new_mod_path = os.path.join(absolute_app_path, new_mod_name)
        new_mod_exists = os.path.exists(absolute_new_mod_path)
    # Return as a dictionary
    return {
        "absolute_base_dir": absolute_base_dir,
        "absolute_project_path": absolute_project_path,
        "absolute_app_path": absolute_app_path,
        "absolute_django_project_path": absolute_django_project_path,
        "std_app_name": std_app_name,
        "project_exists": project_exists,
        "app_exists": app_exists,
        "def_mod_name": def_mod_name,
        "this_mod_name": this_mod_name,
        "absolute_def_mod_path": absolute_def_mod_path,
        "absolute_this_mod_path": absolute_this_mod_path,
        "def_mod_exists": def_mod_exists,
        "this_mod_exists": this_mod_exists,
        "absolute_new_mod_path": absolute_new_mod_path,
        "new_mod_exists": new_mod_exists,        
    }
  
#######################################################################################################################
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python django_project_mgmt.py <create|delete> <project_name>[.app_name[.mod_name]]")
        sys.exit(1)

    command = sys.argv[1]
    project_input = sys.argv[2]
    input_parts = project_input.split(".")
    length_input_parts = len(input_parts)

  
    # Initialize variables
    project_name = None
    app_name = None
    mod_name = None

    # Determine the type of entity (project, app, or module)
    if length_input_parts == 1:
        project_name = project_input
    elif length_input_parts == 2:
        project_name, app_name = input_parts
    elif length_input_parts == 3:
        project_name, app_name, mod_name = input_parts
    else:
        print("Error: Invalid input format. Use 'project', 'project.app', or 'project.app.module'.", file=sys.stderr)
        sys.exit(1)

    # Execute based on the detected type
    if command == "create":
        if length_input_parts == 1:
            #print(f"Creating Django project '{project_name}'")
            create_django_project(project_name, PROJECT_BASE_DIR)
        elif length_input_parts == 2:
            #print(f"Creating Django app '{app_name}' inside project '{project_name}'")
            create_django_app(project_name, app_name, PROJECT_BASE_DIR)
        elif length_input_parts == 3:
            #print(f"Creating module '{mod_name}' inside app '{app_name}' in project '{project_name}'")
            std_app_name = f"{APP_PREFIX}_{app_name}"
            std_mod_name = f"{MOD_PREFIX}_{mod_name}"
            def_mod_name = f"{MOD_PREFIX}_app"
            if os.path.exists(os.path.join(PROJECT_BASE_DIR, project_name, std_app_name, std_mod_name)):
                print(f"Warning: Module '{mod_name}' already exists in app '{app_name}' in project '{project_name}'.", file=sys.stderr)
                sys.exit(1)
            
            create_mod(project_name, app_name, mod_name, PROJECT_BASE_DIR)

    elif command == "delete":
        if length_input_parts == 1:
            print(f"Deleting Django project '{project_name}'")
            delete_django_project(project_name)
        else:
            print("Error: Deletion is only supported for full projects, not apps or modules.", file=sys.stderr)
            sys.exit(1)
    else:
        print("Invalid command. Use: create, delete.", file=sys.stderr)
        sys.exit(1)


############################################################ DEBUG ##################################################
# def create_mod(project_name, app_name, mod_name, base_dir):
#     """Create a new module in an existing Django app."""
#     app_info = get_mod_naming(project_name, app_name, mod_name, base_dir)
#     absolute_base_dir = app_info["absolute_base_dir"]
#     absolute_project_path = app_info["absolute_project_path"]
#     absolute_django_project_path = app_info["absolute_django_project_path"]
#     absolute_app_path = app_info["absolute_app_path"]
#     std_app_name = app_info["std_app_name"]
#     app_exists = app_info["app_exists"]
#     def_mod_name = app_info["def_mod_name"]
#     this_mod_name = app_info["this_mod_name"]
#     absolute_def_mod_path = app_info["absolute_def_mod_path"]
#     absolute_this_mod_path = app_info["absolute_this_mod_path"]
#     def_mod_exists = app_info["def_mod_exists"]
#     this_mod_exists = app_info["this_mod_exists"]
#     project_exists = app_info["project_exists"]
#     absolute_new_mod_path = app_info["absolute_new_mod_path"]
#     new_mod_exists = app_info["new_mod_exists"]
#     print(f">>> === APP PATH {absolute_app_path} === <<<")


#     if not os.path.exists(absolute_project_path):
#         create_django_project(project_name, base_dir)
#     if not app_exists:
#         create_django_app(project_name, app_name, base_dir)


#     # Create template directories: templates/app_name/mod_name
#     template_dir = os.path.join(absolute_app_path, "templates", std_app_name)
#     create_directory(template_dir)
#     template_mod_name = os.path.join(template_dir, f"{this_mod_name}")
#     create_directory(template_mod_name)
    
#     # create placeholder files for now or copy from existing     
#     # create the module directory
#     if not os.path.exists(absolute_def_mod_path):
#         create_directory(absolute_def_mod_path)
#         create_empty_file(os.path.join(absolute_def_mod_path, f"urls_app.py")) 
#         create_empty_file(os.path.join(absolute_def_mod_path, "__init__.py"))
#         create_empty_file(os.path.join(absolute_def_mod_path, f"urls_{mod_name}.py"))
#         create_empty_file(os.path.join(absolute_def_mod_path, f"models_{mod_name}.py"))
#         create_empty_file(os.path.join(absolute_def_mod_path, f"views_{mod_name}.py"))
#         create_empty_file(os.path.join(absolute_def_mod_path, f"forms_{mod_name}.py"))
#         # update the urls_app.py of the app based on the modules
#         generate_urls(absolute_def_mod_path, "urls_app")
#     if not os.path.exists(absolute_this_mod_path):
#         create_directory(absolute_this_mod_path)    
#         create_empty_file(os.path.join(absolute_this_mod_path, "__init__.py"))
#         create_empty_file(os.path.join(absolute_this_mod_path, f"urls_{mod_name}.py"))
#         create_empty_file(os.path.join(absolute_this_mod_path, f"models_{mod_name}.py"))
#         create_empty_file(os.path.join(absolute_this_mod_path, f"views_{mod_name}.py"))
#         create_empty_file(os.path.join(absolute_this_mod_path, f"forms_{mod_name}.py"))

#     if absolute_new_mod_path != None and not os.path.exists(absolute_new_mod_path):
#         create_directory(absolute_new_mod_path)    
#         create_empty_file(os.path.join(absolute_new_mod_path, "__init__.py"))
#         create_empty_file(os.path.join(absolute_new_mod_path, f"urls_{mod_name}.py"))
#         create_empty_file(os.path.join(absolute_new_mod_path, f"models_{mod_name}.py"))
#         create_empty_file(os.path.join(absolute_new_mod_path, f"views_{mod_name}.py"))
#         create_empty_file(os.path.join(absolute_new_mod_path, f"forms_{mod_name}.py"))
    
#     print(f"Django module '{mod_name}' created successfully.")
