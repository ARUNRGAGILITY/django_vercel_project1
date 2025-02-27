import os
import sys
import subprocess
import shutil
import configparser
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
        print(f"Warning: Django project '{project_name}' already exists at '{project_path}'. Skipping project creation.")
        return  # Do not exit, just return

    os.makedirs(project_path, exist_ok=True)
    subprocess.run(["django-admin", "startproject", f"project_{project_name}", project_path])
    print(f"Django project '{project_name}' created successfully in '{project_path}'")

def create_django_app(project_name, app_name, base_dir):
    """Create a new Django app inside an existing project."""
    app_name = app_name.lower()
    app_name = f"{APP_PREFIX}_{app_name}"  # Add prefix to app name
    project_path = os.path.join(base_dir, project_name)
    app_path = os.path.join(project_path, app_name)

    # Ensure project exists first
    if not os.path.exists(project_path):
        print(f"Warning: Django project '{project_name}' does not exist. Creating project first.")
        create_django_project(project_name, base_dir)

    if os.path.exists(app_path):
        print(f"Warning: Django app '{app_name}' already exists inside project '{project_name}'. Skipping app creation.")
        return  # Do not exit, just return

    os.chdir(project_path)
    subprocess.run(["python", "manage.py", "startapp", app_name])
    print(f"Django app '{app_name}' created successfully inside '{project_name}'.")

def create_module(project_name, app_name, mod_name, base_dir):
    """Ensure project and app exist before creating a module inside an app."""
    app_name = app_name.lower()
    app_name = f"{APP_PREFIX}_{app_name}"  # Add prefix to app
    # print(f">>> === CHECKING THE APP NAME {app_name} === <<<")
    mod_name = mod_name.lower()
    mod_name = f"{MOD_PREFIX}_{mod_name}"  # Add prefix to module name
    project_path = os.path.join(base_dir, project_name)
    app_path = os.path.join(project_path, app_name)
    mod_path = os.path.join(app_path, mod_name)
    # print(f">>> === CHECKING THE project_path PATH {project_path} === <<<")
    # print(f">>> === CHECKING THE app_path PATH {app_path} === <<<")
    # print(f">>> === CHECKING THE mod_path PATH {mod_path} === <<<")

    # Ensure project exists first
    if not os.path.exists(project_path):
        print(f"Warning: Django project '{project_name}' does not exist. Creating project first.")
        create_django_project(project_name, base_dir)

    # Ensure app exists first
    if not os.path.exists(app_path):
        print(f"Warning: Django app '{app_name}' does not exist. Creating app first.")
        create_django_app(project_name, app_name, base_dir)

    # Ensure module does not already exist
    if os.path.exists(mod_path):
        print(f"Error: Module '{mod_name}' already exists inside app '{app_name}' in project '{project_name}'.", file=sys.stderr)
        sys.exit(1)
    print(f">>> === CHECKING THE MOD PATH {mod_path} === <<<")
    os.makedirs(mod_path, exist_ok=True)
    open(os.path.join(mod_path, "__init__.py"), "w").close()
    print(f"Module '{mod_name}' created successfully inside app '{app_name}' in project '{project_name}'.")

####################    DELETE FUNCTIONS    ####################
def delete_django_project(project_name):
    """Delete an existing Django project."""
    project_path = os.path.join("env", "dev", project_name)

    if os.path.exists(project_path):
        shutil.rmtree(project_path)
        print(f"Django project '{project_name}' deleted successfully.")
    else:
        print(f"Error: Django project '{project_name}' does not exist.")

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
            print(f"Creating Django project '{project_name}'")
            create_django_project(project_name, PROJECT_BASE_DIR)
        elif length_input_parts == 2:
            print(f"Creating Django app '{app_name}' inside project '{project_name}'")
            create_django_app(project_name, app_name, PROJECT_BASE_DIR)
        elif length_input_parts == 3:
            print(f"Creating module '{mod_name}' inside app '{app_name}' in project '{project_name}'")
            create_module(project_name, app_name, mod_name, PROJECT_BASE_DIR)

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
