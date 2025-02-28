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
CURRENT_DIR = os.path.abspath(".")
PROJECT_BASE_DIR = config.get("paths", "PROJECT_BASE_DIR", fallback="env/dev")  # Default to "env/dev" if missing
PROJECT_PREFIX = config.get("project", "project_prefix", fallback="project")  # Default to "app_" if missing
APP_PREFIX = config.get("apps", "app_prefix", fallback="app")  # Default to "app_" if missing
APP_FILES = config.get("apps", "app_files", fallback="no")  # Default to "no" if missing
MOD_PREFIX = config.get("modules", "mod_prefix", fallback="mod")  # Default to "mod_" if missing
abs_project_base_dir = os.path.join(CURRENT_DIR, PROJECT_BASE_DIR)

########################################### PROJECT RELATED ########################################################
def create_django_project(project_name, base_dir):
    """Create a new Django project if it doesn't already exist."""
    project_path = os.path.join(abs_project_base_dir, project_name)
    std_project_name = f"{PROJECT_PREFIX}_{project_name}" if not project_name.startswith(f"{PROJECT_PREFIX}_") else project_name
    check_abs_django_project_path = os.path.join(project_path, std_project_name)
    if os.path.exists(project_path):
        print(f"Django project {project_name} exists.")
        return  
    os.makedirs(project_path, exist_ok=True)    
    if os.path.exists(check_abs_django_project_path):
        return
    subprocess.run(["django-admin", "startproject", f"project_{project_name}", project_path])
    
    print(f"Django project '{project_name}' created successfully.")
########################################### APP RELATED ########################################################
def create_django_app(project_name, app_name, base_dir):    
    """Create a new Django app in an existing project."""
    project_path = os.path.join(abs_project_base_dir, project_name)
    std_app_name = f"{APP_PREFIX}_{app_name}" if not app_name.startswith(f"{APP_PREFIX}_") else app_name
    check_abs_app_path = os.path.join(project_path, std_app_name)
    if not os.path.exists(project_path):
        create_django_project(project_name, base_dir)
    if os.path.exists(check_abs_app_path):
        return
    subprocess.run(["python", "manage.py", "startapp", std_app_name], cwd=project_path, check=True)
    if APP_FILES == "no":
            app_files = ["models.py", "tests.py", "views.py"]            
            for file in app_files:
                to_be_removed = os.path.join(check_abs_app_path, file)             
                if os.path.exists(to_be_removed):
                    os.remove(to_be_removed)

    def_mod_name = f"{MOD_PREFIX}_app"
    check_abs_def_mod_path = os.path.join(check_abs_app_path, def_mod_name)
    if not os.path.exists(check_abs_def_mod_path):
        create_custom_module(project_name, app_name, def_mod_name, base_dir)

    app_mod_name = f"{MOD_PREFIX}_{app_name}"
    check_abs_app_mod_path = os.path.join(check_abs_app_path, def_mod_name)
    if not os.path.exists(check_abs_app_mod_path):
        create_custom_module(project_name, app_name, app_mod_name, base_dir)

    generate_app_urls(std_app_name, app_name, project_path)
    print(f"Django app '{std_app_name}' created successfully.")
########################################### MODULE RELATED ########################################################
def create_custom_module(project_name, app_name, mod_name, base_dir):
    """Create a new module in an existing Django app."""
    project_path = os.path.join(abs_project_base_dir, project_name)
    std_app_name = f"{APP_PREFIX}_{app_name}" if not app_name.startswith(f"{APP_PREFIX}_") else app_name
    check_abs_app_path = os.path.join(project_path, std_app_name)
    if not os.path.exists(check_abs_app_path):
        create_django_app(project_name, app_name, base_dir)
    if mod_name == None:
        print(f"CREATE_CUSTOM_MODULE: Error: mod_name None")
        sys.exit(1)
    std_mod_name = f"{MOD_PREFIX}_{mod_name}" if not mod_name.startswith(f"{MOD_PREFIX}_") else mod_name
    # Create template directories: templates/app_name/mod_name
    template_dir = os.path.join(check_abs_app_path, "templates", std_app_name)
    create_directory(template_dir)
    template_mod_name = os.path.join(template_dir, f"{std_mod_name}")
    create_directory(template_mod_name)
    def_mod_name = f"{MOD_PREFIX}_app"
    check_abs_def_mod_path = os.path.join(check_abs_app_path, def_mod_name)
    # create placeholder files for now or copy from existing     
    # create the module directory
    if not os.path.exists(check_abs_def_mod_path):
        create_directory(check_abs_def_mod_path)        
        create_empty_file(os.path.join(check_abs_def_mod_path, "__init__.py"))
        create_empty_file(os.path.join(check_abs_def_mod_path, f"urls_app.py")) 
        create_empty_file(os.path.join(check_abs_def_mod_path, f"all_model_imports.py"))
        create_empty_file(os.path.join(check_abs_def_mod_path, f"all_view_imports.py"))
        create_empty_file(os.path.join(check_abs_def_mod_path, f"all_form_imports.py"))
        # update the urls_app.py of the app based on the modules
        generate_urls(check_abs_app_path, "urls_app")
        print(f"Django module '{std_mod_name}' created successfully.")
    app_mod_name = f"{MOD_PREFIX}_{app_name}"
    check_abs_app_mod_path = os.path.join(check_abs_app_path, app_mod_name)
    if not os.path.exists(check_abs_app_mod_path):
        create_directory(check_abs_app_mod_path)        
        create_empty_file(os.path.join(check_abs_app_mod_path, "__init__.py"))
        create_empty_file(os.path.join(check_abs_app_mod_path, f"urls_{app_name}.py")) 
        create_empty_file(os.path.join(check_abs_app_mod_path, f"models_{mod_name}.py"))
        create_empty_file(os.path.join(check_abs_app_mod_path, f"views_{mod_name}.py"))
        create_empty_file(os.path.join(check_abs_app_mod_path, f"forms_{mod_name}.py"))
        # update the urls_app.py of the app based on the modules
        generate_urls(check_abs_app_path, "urls_app")
        print(f"Django module '{app_mod_name}' created successfully.")

    check_abs_new_mod_path = os.path.join(check_abs_app_path, std_mod_name)
    if not os.path.exists(check_abs_new_mod_path):
        create_directory(check_abs_new_mod_path)        
        create_empty_file(os.path.join(check_abs_new_mod_path, "__init__.py"))
        create_empty_file(os.path.join(check_abs_new_mod_path, f"urls_{mod_name}.py")) 
        create_empty_file(os.path.join(check_abs_new_mod_path, f"models_{mod_name}.py"))
        create_empty_file(os.path.join(check_abs_new_mod_path, f"views_{mod_name}.py"))
        create_empty_file(os.path.join(check_abs_new_mod_path, f"forms_{mod_name}.py"))
        # update the urls_app.py of the app based on the modules
        generate_urls(check_abs_app_path, "urls_app")
        print(f"Django module '{std_mod_name}' created successfully.")
    

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
            
            create_custom_module(project_name, app_name, mod_name, PROJECT_BASE_DIR)

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
