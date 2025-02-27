import os
import sys
import argparse
import subprocess

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
    default_module = "mod_app"

    output_dir = os.path.abspath(output_dir)
    print(f">>> Creating project structure in: {parts[0]} <<<")
    project_root_path = os.path.join(output_dir, parts[0])  # env/dev/<projectname>/
    project_path = os.path.join(project_root_path, project_name)  # env/dev/<projectname>/project_<projectname>
    app_base_path = os.path.join(project_root_path, "apps")  # env/dev/<projectname>/apps
    app_path = os.path.join(app_base_path, app_name) if app_name else None
    module_path = os.path.join(app_path, module_name) if module_name else None
    default_module_path = os.path.join(app_path, default_module) if app_name else None

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(project_root_path, exist_ok=True)
    os.makedirs(project_path, exist_ok=True)

    if not os.path.exists(os.path.join(project_root_path, "manage.py")):
        print(f">>> Creating Django project: {project_name} <<<")
        execute_command(f"django-admin startproject {project_name} \"{project_root_path}\"")
    else:
        print(f"✅ Project '{project_name}' already exists, skipping creation.")

    if app_name:
        os.makedirs(app_base_path, exist_ok=True)
        os.makedirs(app_path, exist_ok=True)

        if not os.path.exists(os.path.join(app_path, "apps.py")):
            print(f">>> Creating Django app: {app_name} <<<")
            execute_command(f"django-admin startapp {app_name} \"{app_path}\"")
        else:
            print(f"✅ App '{app_name}' already exists, skipping creation.")

        if module_name:
            os.makedirs(module_path, exist_ok=True)
            os.makedirs(default_module_path, exist_ok=True)

            for path in [module_path, default_module_path]:
                init_file = os.path.join(path, "__init__.py")
                if not os.path.exists(init_file):
                    open(init_file, "w").close()
                    print(f">>> Module '{os.path.basename(path)}' created <<<")
                else:
                    print(f"✅ Module '{os.path.basename(path)}' already exists, skipping creation.")

            create_module_urls(default_module_path, module_path, app_name, module_name)
            create_app_urls(app_path, app_name)
            create_project_urls(project_path, app_name)

        update_settings(project_path, project_name, app_name)


def update_settings(project_root_path, project_name, app_name):
    """Update Django settings.py to include the new app."""
    settings_file = os.path.join(project_root_path,  "settings.py")

    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            content = f.readlines()

        # Ensure app_name is valid
        if not app_name:
            print("⚠️ No app specified, skipping settings update.")
            return

        app_entry = f"    'apps.{app_name}',\n"

        # Check if app is already listed in INSTALLED_APPS
        if any(app_entry.strip() in line.strip() for line in content):
            print(f"✅ '{app_name}' is already in settings.py, skipping update.")
            return

        # Insert app into INSTALLED_APPS
        for i, line in enumerate(content):
            if "INSTALLED_APPS = [" in line:
                content.insert(i + 1, app_entry)
                break

        with open(settings_file, "w") as f:
            f.writelines(content)

        print(f">>> Updated settings.py to include '{app_name}' <<<")
    else:
        print(f"⚠️ settings.py not found in {settings_file}, skipping update.")


def create_project_urls(project_path, app_name):
    """Update `urls.py` in the Django project to include the app URLs."""
    project_urls_file = os.path.join(project_path,  "urls.py")
    app_import_path = f"apps.{app_name}.urls"

    if os.path.exists(project_urls_file):
        with open(project_urls_file, "r") as f:
            content = f.readlines()

        app_import_line = f"    path('{app_name}/', include('{app_import_path}')),\n"

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

    module_import_path = f"apps.{app_name}.mod_{module_name}.urls_{module_name}"

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
