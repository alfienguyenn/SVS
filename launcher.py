import os
import sys
import subprocess
import tempfile
import requests
import atexit
import shutil
import time
import tkinter as tk
from tkinter import messagebox

# Global variable to track files to be deleted
temp_files = []

def cleanup():
    """Delete all temporary downloaded data"""
    global temp_files
    
    print("\nCleaning up temporary data...")
    for file_path in temp_files:
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"✓ Deleted file: {file_path}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                print(f"✓ Deleted directory: {file_path}")
        except Exception as e:
            print(f"! Error when deleting {file_path}: {e}")

def check_internet_connection():
    """Check if the system has an active internet connection"""
    try:
        # Try to connect to Google's DNS server
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False
    except:
        return False

def download_content(url, is_text=True):
    """Download content from GitHub and return content or save to file"""
    try:
        # Convert GitHub URL to raw URL if needed
        if "github.com" in url and "/blob/" in url:
            url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        
        print(f"Downloading from: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        if is_text:
            return response.text
        else:
            # If not text, return binary content
            return response.content
    except Exception as e:
        print(f"Error when downloading content: {e}")
        return None

def save_to_file(content, destination):
    """Save content to file"""
    try:
        if isinstance(content, str):
            with open(destination, 'w', encoding='utf-8') as file:
                file.write(content)
        else:
            with open(destination, 'wb') as file:
                file.write(content)
        
        # Add file to the list to be deleted
        global temp_files
        temp_files.append(destination)
        
        print(f"✓ Successfully saved to {destination}")
        return True
    except Exception as e:
        print(f"Error when saving file: {e}")
        return False

def run_script(script_path):
    """Run Python script with admin rights on Windows"""
    try:
        if sys.platform == 'win32':
            # On Windows, try running with admin rights
            print("Requesting administrator privileges...")
            try:
                import ctypes
                if not ctypes.windll.shell32.IsUserAnAdmin():
                    print("Script requires administrator privileges. Requesting...")
                    # If not admin, run again with admin rights
                    ctypes.windll.shell32.ShellExecuteW(
                        None, "runas", sys.executable, f'"{script_path}"', None, 1)
                    # Wait a bit to give time to start up
                    time.sleep(2)
                    return True
                else:
                    # Already admin, run normally
                    subprocess.run([sys.executable, script_path], check=True)
                    return True
            except Exception as e:
                print(f"Error requesting admin privileges: {e}")
                # Try running normally if error occurs
                try:
                    subprocess.run([sys.executable, script_path], check=True)
                    return True
                except Exception as sub_e:
                    print(f"Error running script: {sub_e}")
                    return False
        else:
            # On other platforms
            print("Running script...")
            subprocess.run([sys.executable, script_path], check=True)
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error running script: {e}")
        return False
    except Exception as e:
        print(f"Undefined error: {e}")
        return False

def main():
    """Main function to check internet connection and run SVS Tools script"""
    print("SVS Tools Launcher")
    print("=" * 50)
    
    # Register cleanup function to run when exiting program
    atexit.register(cleanup)
    
    # Check internet connection
    print("Checking internet connection...")
    if not check_internet_connection():
        print("No internet connection detected.")
        messagebox.showerror("Connection Error", 
                            "No internet connection detected.\nPlease connect to the internet and try again.")
        return
    
    print("Internet connection confirmed.")
    
    # URL for the script
    script_url = "https://github.com/alfienguyenn/SVS/blob/main/run_svs_tools.py"
    
    # Download script
    print("Downloading script...")
    script_content = download_content(script_url)
    
    if not script_content:
        print("Unable to download script. Exiting.")
        return
    
    # Create temp directory to save script
    temp_dir = tempfile.gettempdir()
    script_path = os.path.join(temp_dir, f"run_svs_tools_{int(time.time())}.py")
    
    # Save script to temp file
    if save_to_file(script_content, script_path):
        print(f"Script saved to {script_path}")
        
        # Run script
        print("Running SVS Tools...")
        if run_script(script_path):
            print("SVS Tools ran successfully!")
        else:
            print("An error occurred when running SVS Tools.")
    else:
        print("Unable to save script. Exiting.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        # Ensure cleanup is called even if there is an error
        cleanup()
