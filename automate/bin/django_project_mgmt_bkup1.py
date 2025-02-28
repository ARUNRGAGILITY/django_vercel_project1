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
APP_PREFIX = config.get("apps", "app_prefix", fallback="app")  # Default to "app_" if missing
APP_FILES = config.get("apps", "app_files", fallback="no")  # Default to "no" if missing
MOD_PREFIX = config.get("modules", "mod_prefix", fallback="mod")  # Default to "mod_" if missing
########################################### PROJECT RELATED ########################################################
def create_django_project(project_name, base_dir):
    """Create a new Django project if it doesn't already exist."""
    project_path = os.path.join(base_dir, project_name)

    if os.path.exists(project_path):
        #print(f"Warning: Django project '{project_name}' already exists at '{project_path}'. Skipping project creation.")
        print(f"Django project {project_name} exists.")
        return  # Do not exit, just return

    os.makedirs(project_path, exist_ok=True)
    subprocess.run(["django-admin", "startproject", f"project_{project_name}", project_path])
    #print(f"Django project '{project_name}' created successfully in '{project_path}'")
    print(f"Django project '{project_name}' created successfully.")
########################################### APP RELATED ########################################################
def create_django_app(project_name, app_name, base_dir):
    absolute_base_dir = os.path.abspath(base_dir)
    #print(f"DJANGO_APP: Full path of base_dir: {absolute_base_dir}")
    """Create a new Django app inside an existing project."""
    in_app_name = app_name
    app_name = app_name.lower()
    # Add prefix to app name
    # Ensure "app_" is only added once
    if not app_name.startswith(f"{APP_PREFIX}_"):
        app_name = f"{APP_PREFIX}_{app_name}"

    project_path = os.path.join(base_dir, project_name)
    app_path = os.path.join(project_path, app_name)

    # Ensure project exists first
    if not os.path.exists(project_path):
        #print(f"Warning: Django project '{project_name}' does not exist. Creating project first.")
        create_django_project(project_name, base_dir)

    if os.path.exists(app_path):
        #print(f"Warning: Django app '{app_name}' already exists inside project '{project_name}'. Skipping app creation.")
        return  # Do not exit, just return
    

    os.chdir(project_path)
    subprocess.run(["python", "manage.py", "startapp", app_name])
    
    # ✅ Ensure the app folder has been created
    if not os.path.exists(app_name):
        print(f"Error: The app directory '{app_path}' was not created.")
        sys.exit(1)

    # ✅ List the contents of the app directory for debugging
    #print(f">>> === CHECKING FILES IN APP DIRECTORY '{app_name}' === <<<")
    app_contents = os.listdir(app_name)
    #print(f"Contents: {app_contents}")

    if APP_FILES == "no":
        #print(f">>> === REMOVE THE DEFAULT FILES CREATED IN APP FOLDER === <<<")
        app_files = ["models.py", "tests.py", "views.py"]
        
        for file in app_files:
            to_be_removed = os.path.join(app_name, file)
            
            if os.path.exists(to_be_removed):
                os.remove(to_be_removed)
                #print(f">>> === FILE EXISTS: {to_be_removed} === <<<")
            else:
                print(f">>> === FILE NOT FOUND: {to_be_removed} === <<<")

    
    # first time the module is created, we clear the default files
    # create the module directory
    # create mod_app for general purpose and create mod_app_name for its purpose
    default_mod_name = f"{MOD_PREFIX}_app"
    this_mod_app = f"{MOD_PREFIX}_{in_app_name}"
    default_mod_path = os.path.join(app_path, default_mod_name)
    this_mod_app_path = os.path.join(app_path, this_mod_app)
    if not os.path.exists(default_mod_path):
        #print(f">>> === Creating module {default_mod_path} '{default_mod_name}' inside app '{app_name}' in project '{project_name}' === <<<")
        create_mod(project_name, app_name, default_mod_name, base_dir)
    if not os.path.exists(this_mod_app_path):
        #print(f">>> === Creating module {this_mod_app_path} '{this_mod_app}' inside app '{app_name}' in project '{project_name}' === <<<")
        create_mod(project_name, app_name, this_mod_app, base_dir)

    #print(f"Django app '{app_name}' created successfully inside '{project_name}'.")
    print(f"Django app '{app_name}' created successfully.")
########################################### MODULE RELATED ########################################################
def create_mod(project_name, app_name, mod_name, base_dir):
    #print(f">>> === **** CHECK: {project_name}:{app_name}:{mod_name} === <<<")
    # Ensure base_dir is absolute
    absolute_base_dir = os.path.abspath(base_dir)
    #print(f">>> === INCOMING MODULE BASE DIR : {absolute_base_dir} === <<<")

    # Construct project and app paths
    project_path = os.path.join(absolute_base_dir, project_name)
    
    def_mod_name = f"{MOD_PREFIX}_app"
    std_mod_name = f"{MOD_PREFIX}_{mod_name}"
    if not app_name.startswith(f"{APP_PREFIX}_"):
        app_name = f"{APP_PREFIX}_{app_name}"
    if not mod_name.startswith(f"{MOD_PREFIX}_"):
        std_app_name = f"{MOD_PREFIX}_app"
        std_mod_name = f"{MOD_PREFIX}_{mod_name}"
    
    app_path = os.path.join(project_path, app_name)
    # Ensure project exists first
    if not os.path.exists(project_path):
        #print(f"Warning: Django project '{project_name}' does not exist. Creating project first.")
        create_django_project(project_name, absolute_base_dir)  # Pass absolute_base_dir

    # Ensure app exists first
    if not os.path.exists(app_path):
        #print(f"Warning: Django app '{app_name}' does not exist. Creating app first.")
        create_django_app(project_name, app_name, absolute_base_dir)  # Pass absolute_base_dir
   
    # Ensure module does not already exist
    if os.path.exists(os.path.join(app_path, def_mod_name)):
        #print(f"Warning: Module '{mod_name}' already exists in app '{app_name}' in project '{project_name}'.")
        return  # Do not exit, just return
    if os.path.exists(os.path.join(app_path, std_mod_name)):
        #print(f"Warning: Module '{mod_name}' already exists in app '{app_name}' in project '{project_name}'.")
        return
   
    """Create a new module inside an existing app."""
    
    app_dir = app_path
    mod_dir = os.path.join(app_dir, mod_name)
    #print(f">>> === MODULECREATION: ***** Creating module {mod_dir} '{mod_name}' inside app '{app_name}' in project '{project_name}' === <<<")
    std_app_name = app_name
    std_mod_name = mod_name
    # Create template directories: templates/app_name/mod_name
    template_dir = os.path.join(app_dir, "templates", std_app_name)
    create_directory(template_dir)
    template_mod_name = os.path.join(template_dir, f"{std_mod_name}")
    create_directory(template_mod_name)
    
    # create placeholder files for now or copy from existing     
    # create the module directory
    create_directory(mod_dir)
    
    create_empty_file(os.path.join(mod_dir, "__init__.py"))
    create_empty_file(os.path.join(mod_dir, f"urls_{mod_name}.py"))
    create_empty_file(os.path.join(mod_dir, f"models_{mod_name}.py"))
    create_empty_file(os.path.join(mod_dir, f"views_{mod_name}.py"))
    create_empty_file(os.path.join(mod_dir, f"forms_{mod_name}.py"))
    if mod_name == "mod_app":
        create_empty_file(os.path.join(mod_dir, f"urls_app.py")) 
    
    # update the urls_app.py of the app based on the modules
    generate_urls(app_dir, "urls_app")

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
            def_mod_anme = f"{MOD_PREFIX}_app"
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
