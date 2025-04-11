import os
import sys
import subprocess
import tempfile
import requests
import atexit
import shutil
import time
import getpass
import tkinter as tk
from tkinter import simpledialog, messagebox

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

def get_access_code(url):
    """Download and read access code from URL"""
    access_code = download_content(url)
    if access_code:
        # Clean the code (remove whitespace, newlines)
        return access_code.strip()
    return None

def verify_access_code(correct_code):
    """Display dialog requesting access code and validate with custom interface"""
    # Create custom login window
    login_window = tk.Tk()
    login_window.title("Authentication")
    login_window.geometry("400x200")  # Increase window size
    login_window.resizable(False, False)
    login_window.configure(bg="#f0f0f0")
    
    # Center the window
    login_window.update_idletasks()
    width = login_window.winfo_width()
    height = login_window.winfo_height()
    x = (login_window.winfo_screenwidth() // 2) - (width // 2)
    y = (login_window.winfo_screenheight() // 2) - (height // 2)
    login_window.geometry(f'{width}x{height}+{x}+{y}')
    
    # Variable to control number of attempts
    attempts = [0]  # Use list to be able to change value in inner function
    max_attempts = 3
    
    # Result variable
    result = [False]  # Use list to be able to change value in inner function
    
    # Create guide label
    label = tk.Label(
        login_window, 
        text=f"Enter access code to continue.\nYou have {max_attempts} attempts remaining:",
        font=("Arial", 12),
        bg="#f0f0f0",
        pady=10
    )
    label.pack(pady=10)
    
    # Create frame containing entry
    entry_frame = tk.Frame(login_window, bg="#f0f0f0")
    entry_frame.pack(pady=5, fill="x", padx=30)
    
    # Create string variable to store actual password
    password_var = tk.StringVar()
    
    # Create custom Entry to handle displaying asterisks
    class PasswordEntry(tk.Entry):
        def __init__(self, master=None, **kwargs):
            self.password = ""
            super().__init__(master, **kwargs)
            
        def add_char(self, char):
            self.password += char
            self.delete(0, tk.END)
            self.insert(0, "*" * len(self.password))
            
        def remove_char(self):
            if self.password:
                self.password = self.password[:-1]
                self.delete(0, tk.END)
                self.insert(0, "*" * len(self.password))
                
        def get_password(self):
            return self.password
    
    # Create custom entry
    entry = PasswordEntry(
        entry_frame,
        font=("Arial", 12),
        width=30,
        justify="center"
    )
    entry.pack(fill="x", ipady=5)
    entry.focus()
    
    # Function to handle key input
    def on_key_event(event):
        # If Backspace key
        if event.keysym == 'BackSpace':
            entry.remove_char()
        # If Enter key
        elif event.keysym == 'Return':
            check_password()
        # If normal character
        elif len(event.char) == 1 and event.char.isprintable():
            entry.add_char(event.char)
        # Prevent default event to not display actual character
        return "break"
    
    # Assign key event to entry
    entry.bind("<Key>", on_key_event)
    
    # Frame containing buttons
    button_frame = tk.Frame(login_window, bg="#f0f0f0")
    button_frame.pack(pady=20)
    
    # Function to check password
    def check_password():
        entered_password = entry.get_password()
        attempts[0] += 1
        remaining = max_attempts - attempts[0]
        
        if entered_password.strip() == correct_code:
            result[0] = True
            messagebox.showinfo("Success", "Correct access code!")
            login_window.destroy()
        else:
            if remaining > 0:
                messagebox.showerror("Error", f"Incorrect access code. {remaining} attempts remaining.")
                label.config(text=f"Enter access code to continue.\nYou have {remaining} attempts remaining:")
                # Clear old password
                entry.password = ""
                entry.delete(0, tk.END)
                entry.focus()
            else:
                messagebox.showerror("Error", "Too many incorrect attempts. The program will exit.")
                login_window.destroy()
    
    # OK button
    ok_button = tk.Button(
        button_frame, 
        text="OK", 
        command=check_password,
        width=10,
        font=("Arial", 11),
        bg="#4a86e8",
        fg="white",
        relief=tk.RAISED
    )
    ok_button.pack(side=tk.LEFT, padx=10)
    
    # Cancel button
    cancel_button = tk.Button(
        button_frame, 
        text="Cancel", 
        command=login_window.destroy,
        width=10,
        font=("Arial", 11)
    )
    cancel_button.pack(side=tk.LEFT, padx=10)
    
    # Mainloop
    login_window.mainloop()
    
    # Return authentication result
    return result[0]

def check_required_modules():
    """Check and install required modules if needed"""
    required_modules = ['requests', 'tkinter']
    
    for module in required_modules:
        try:
            if module == 'tkinter':
                # Try to import tkinter
                __import__(module)
            else:
                # Check if module is installed
                subprocess.run([sys.executable, '-c', f'import {module}'], 
                              check=True, capture_output=True)
            print(f"✓ Module {module} is installed")
        except (ImportError, subprocess.CalledProcessError):
            print(f"Module {module} is not installed. Installing...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', module], 
                              check=True)
                print(f"✓ Module {module} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"Error installing {module}: {e}")
                return False
    return True

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
    """Main function to authenticate, download and run SVS Tools script"""
    print("SVS Tools Launcher - Secure Version")
    print("=" * 50)
    
    # Register cleanup function to run when exiting program
    atexit.register(cleanup)
    
    # Check required modules
    if not check_required_modules():
        print("Unable to install required modules. Exiting.")
        return
    
    # URLs for access code and script
    access_code_url = "https://github.com/alfienguyenn/SVS/blob/main/AccessCode.txt"
    script_url = "https://github.com/alfienguyenn/SVS/blob/main/SVS_Tools.py"
    
    # Download access code first
    print("Downloading access code...")
    access_code = get_access_code(access_code_url)
    
    if not access_code:
        print("Unable to download access code. Exiting.")
        return
    
    # Ask user to enter access code
    if not verify_access_code(access_code):
        print("Authentication failed. Exiting.")
        return
        
    # After successful authentication, download script
    print("Authentication successful! Downloading script...")
    script_content = download_content(script_url)
    
    if not script_content:
        print("Unable to download script. Exiting.")
        return
    
    # Create temp directory to save script
    temp_dir = tempfile.gettempdir()
    script_path = os.path.join(temp_dir, f"SVS_Tools_{int(time.time())}.py")
    
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
