import os
import argparse


def generate_app_urls(app_name, url_name, base_dir):
    """Automatically create `app_urls.py` inside each app."""
    app_path = os.path.join(base_dir, app_name)
    urls_file = os.path.join(app_path, "app_urls.py")

    if not os.path.exists(urls_file):  # Only create if it doesn't exist
        content = f"""from django.urls import include, path

urlpatterns = [
    path('{url_name}/', include('{app_name}.mod_app.urls_app')),
]
"""
        with open(urls_file, "w") as f:
            f.write(content)

        #print(f"✅ Created {urls_file}")
    else:
        print(f"⚠️ {urls_file} already exists, skipping.")


def generate_urls(app_directory, urls_app_filename):
    # Ensure the app directory path is absolute
    app_directory = os.path.abspath(app_directory)
    # Extract the app name from the absolute path
    app_name = os.path.basename(app_directory)
    # Path to the file that will include all module URLs
    urls_file_path = os.path.join(app_directory, 'mod_app' , f"{urls_app_filename}.py")
    
    with open(urls_file_path, 'w') as urls_file:
        urls_file.write("from django.urls import include, path\n\n")
        urls_file.write("urlpatterns = [\n")
        
        for entry in os.listdir(app_directory):
            entry_path = os.path.join(app_directory, entry)
            #print(f"Processing entry: {entry_path}")
            # Check if the entry is a directory and starts with 'mod_' but is not 'mod_app'
            if os.path.isdir(entry_path) and entry.startswith('mod_') and entry != 'mod_app':
                urls_module = f'urls_{entry[4:]}'
                urls_module_path = os.path.join(entry_path, f'{urls_module}.py')
                #print(f">>> === Found module: {urls_module_path} ===")
                if os.path.exists(urls_module_path):
                    urls_file.write(f"    path('{entry[4:]}/', include('{app_name}.{entry}.{urls_module}')),\n")
                else:
                    print(f"urls_module_path does not exist: {urls_module_path}")
        
        urls_file.write("]\n")

    #print(f"{urls_file_path} generated successfully.")
    ##print(f"URLs generated successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a Django URLs file that includes URLs from mod_<modname> directories.')
    parser.add_argument('app_directory', help='The directory of the Django app')
    parser.add_argument('urls_app_filename', help='The filename for the generated URLs file (e.g., urls_app.py)')
    
    args = parser.parse_args()
    
    generate_urls(args.app_directory, args.urls_app_filename)
