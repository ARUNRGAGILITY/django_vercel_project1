import os
import sys
import configparser
import argparse
import subprocess

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read("config.ini")

# Read configurable paths
APPS_CREATED_DIR = config.get("paths", "apps_created", fallback="apps_created")
APPS_GENERAL_DIR = config.get("paths", "apps_general", fallback="apps_general")
APPS_COMMON_DIR = config.get("paths", "apps_common", fallback="apps_common")
APPS_BUILTIN_DIR = config.get("paths", "apps_builtin", fallback="apps_builtin")
DEFAULT_MODULE = config.get("paths", "default_module", fallback="mod_app")

VALID_APP_LOCATIONS = [APPS_GENERAL_DIR, APPS_COMMON_DIR, APPS_BUILTIN_DIR]


def execute_command(command):
    """Execute a shell command and display output."""
    subprocess.run(command, shell=True, check=True)
def create_project_structure(output_dir, input_string):
    """Create Django project, app, and module inside env/dev/<projectname>/."""
    parts = input_string.split(".")

    if len(parts) > 3 or len(parts) < 1:
        print("❌ Error: Invalid format. Use <project_name>[.<app_name>[.<module_name>]]")
        sys.exit(1)

    project_prefix = "project_"
    project_name = project_prefix + parts[0]  # Correctly prefixed
    app_name = f"app_{parts[1]}" if len(parts) > 1 else None
    module_name = f"mod_{parts[2]}" if len(parts) > 2 else None

    output_dir = os.path.abspath(output_dir)
    project_root_path = os.path.join(output_dir)
    project_path = os.path.join(project_root_path, project_name)

    print(f">>> Creating project structure in: {parts[0]} <<<")

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(project_root_path, exist_ok=True)

    if not os.path.exists(os.path.join(project_root_path, "manage.py")):
        print(f">>> Creating Django project: {project_name} <<<")
        execute_command(f"django-admin startproject {project_name} \"{project_root_path}\"")
    else:
        print(f"✅ Project '{project_name}' already exists, skipping creation.")

    if app_name:
        create_django_app(app_name, project_root_path, module_name)
        update_settings(project_root_path, project_name, app_name)
        create_project_urls(project_path, app_name)

    


def update_settings(project_root_path, project_name, app_name):
    """Update Django settings.py to include the new app."""
    settings_file = os.path.join(project_root_path, "settings.py")

    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            content = f.readlines()

        if not app_name:
            print("⚠️ No app specified, skipping settings update.")
            return

        app_entry = f"    'apps.{app_name}',\n"

        if any(app_entry.strip() in line.strip() for line in content):
            print(f"✅ '{app_name}' is already in settings.py, skipping update.")
            return

        for i, line in enumerate(content):
            if "INSTALLED_APPS = [" in line:
                content.insert(i + 1, app_entry)
                break

        with open(settings_file, "w") as f:
            f.writelines(content)

        print(f">>> Updated settings.py to include '{app_name}' <<<")


def create_project_urls(project_path, app_name):
    """Update `urls.py` in the Django project to include the app URLs."""
    project_urls_file = os.path.join(project_path, "urls.py")
    app_import_path = f"apps.{app_name}.urls"
    print(f">>> === {project_urls_file} === <<<")
    if os.path.exists(project_urls_file):
        with open(project_urls_file, "r") as f:
            content = f.readlines()

        # Ensure `include` is imported
        if "from django.urls import include, path\n" not in content:
            content.insert(0, "from django.urls import include, path\n")

        app_import_line = f"    path('{app_name}/', include('{app_import_path}')),\n"

        # Ensure the app's URLs are included only once
        if app_import_line not in content:
            for i, line in enumerate(content):
                if "urlpatterns = [" in line:
                    content.insert(i + 1, app_import_line)
                    break

            with open(project_urls_file, "w") as f:
                f.writelines(content)

            print(f">>> Updated project URLs to include '{app_name}' <<<")

def create_app_urls(app_path, app_name):
    """Create `urls.py` inside app_<appname> and include mod_app.urls."""
    app_urls_file = os.path.join(app_path, "urls.py")
    mod_app_import_path = f"apps.{app_name}.mod_app.urls"

    if not os.path.exists(app_urls_file):
        with open(app_urls_file, "w") as f:
            f.write(f"""from django.urls import path, include

urlpatterns = [
    path('mod_app/', include('{mod_app_import_path}')),
]
""")
        print(f">>> Created URLs file for app: {app_name} <<<")

def create_module_urls(default_module_path, module_path, app_name, module_name):
    """Create `urls_<modname>.py` inside mod_<modname> and include it in mod_app/urls.py."""
    module_urls_file = os.path.join(module_path, f"urls_{module_name}.py")
    mod_app_urls_file = os.path.join(default_module_path, "urls.py")

    module_import_path = f"apps.{app_name}.{module_name}.urls_{module_name}"

    if not os.path.exists(module_urls_file):
        with open(module_urls_file, "w") as f:
            f.write(f"""from django.urls import path
from . import views

urlpatterns = [
    # Define module-level URLs here
]
""")
        print(f">>> Created URLs file for module: {module_name} <<<")

    if not os.path.exists(mod_app_urls_file):
        with open(mod_app_urls_file, "w") as f:
            f.write(f"""from django.urls import path, include

urlpatterns = [
    path('{module_name}/', include('{module_import_path}')),
]
""")
        print(f">>> Created mod_app/urls.py <<<")

def update_apps_py(app_path, app_dir):
    """ Update the name field inside apps.py dynamically """
    apps_py_path = os.path.join(app_path, "apps.py")

    if not os.path.exists(apps_py_path):
        print(f"❌ Error: {apps_py_path} not found. Skipping update.")
        return

    app_name = os.path.basename(app_path)
    correct_name = f"{app_dir}.{app_name}"

    with open(apps_py_path, "r") as file:
        lines = file.readlines()

    with open(apps_py_path, "w") as file:
        for line in lines:
            if line.strip().startswith("name ="):
                file.write(f"    name = '{correct_name}'\n")
            else:
                file.write(line)

    print(f"✅ Updated apps.py: Set name = '{correct_name}' in {apps_py_path}")



def get_correct_app_location(base_dir, app_name):
    """Determine where the app should be created based on existing directories."""
    for app_dir in VALID_APP_LOCATIONS:
        app_path = os.path.join(base_dir, app_dir, app_name)
        if os.path.exists(app_path):  # If app exists, return correct path
            return app_dir
    return APPS_CREATED_DIR  # Default to APPS_GENERAL_DIR




def create_django_app(app_name, base_dir, module_name=None):
    """
    Create or update a Django app inside the appropriate configured directory.
    If a module is specified, ensure it exists inside the correct app structure.
    """
    app_location = get_correct_app_location(base_dir, app_name)
    app_path = os.path.join(base_dir, app_location, app_name)
    module_path = os.path.join(app_path, DEFAULT_MODULE) if module_name else None

    os.makedirs(os.path.join(base_dir, app_location), exist_ok=True)

    if not os.path.exists(app_path):
        os.makedirs(app_path)
        execute_command(f"django-admin startapp {app_name} \"{app_path}\"")
        print(f"✅ Django app '{app_name}' created inside '{app_location}/'.")
    else:
        print(f"✅ Django app '{app_name}' already exists in '{app_location}', updating...")

    for path in [os.path.join(base_dir, app_location), app_path]:
        init_file = os.path.join(path, "__init__.py")
        if not os.path.exists(init_file):
            open(init_file, "w").close()

    if module_name:
        os.makedirs(module_path, exist_ok=True)
        module_init = os.path.join(module_path, "__init__.py")
        if not os.path.exists(module_init):
            open(module_init, "w").close()
            print(f"✅ Created module '{module_name}' inside '{app_name}'.")

        models_auth_path = os.path.join(module_path, "models_auth.py")
        if not os.path.exists(models_auth_path):
            with open(models_auth_path, "w") as f:
                f.write("# models_auth.py - Module-level models\n")
            print(f"✅ Created 'models_auth.py' inside '{module_name}'.")

    update_apps_py(app_path, app_location)
    create_app_urls(app_path, app_name)
    print(f"✅ Django app '{app_name}' successfully updated in '{app_location}/'.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Django Project and App Creator")
    parser.add_argument("command", help="Command to run (e.g., create)")
    parser.add_argument("input_string", help="Format: <project_name>[.<app_name>[.<module_name>]]")
    parser.add_argument("--output-dir", help="Specify output directory for project", required=True)

    args = parser.parse_args()

    if args.command != "create":
        print("❌ Error: Only the 'create' command is supported.")
        sys.exit(1)

    create_project_structure(args.output_dir, args.input_string)







