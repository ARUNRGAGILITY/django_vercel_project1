import os
import sys
import subprocess
import shutil

def create_django_project(project_name):
    """Create a new Django project."""
    project_path = os.path.join("env", "dev", project_name)
    
    # Create directories if they don't exist
    os.makedirs(project_path, exist_ok=True)

    # Run Django startproject without nesting
    subprocess.run(["django-admin", "startproject", f"project_{project_name}", project_path])    

    print(f"Django project '{project_name}' created successfully in '{project_path}'")

def delete_django_project(project_name):
    """Delete an existing Django project."""
    project_path = os.path.join("env", "dev", project_name)

    if os.path.exists(project_path):
        shutil.rmtree(project_path)
        print(f"Django project '{project_name}' deleted successfully.")
    else:
        print(f"Error: Django project '{project_name}' does not exist.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("AUTOMATED DPM Usage: python django_project_mgmt.py <create|delete|run> <project_name>")
        sys.exit(1)

    command = sys.argv[1]
    project_name = sys.argv[2]

    if command == "create":
        create_django_project(project_name)
    elif command == "delete":
        delete_django_project(project_name)
    
    else:
        print("Invalid command. Use: create, delete, or run.")
        sys.exit(1)
