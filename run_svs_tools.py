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
from io import BytesIO

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
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False
    except:
        return False

def download_content(url, is_text=True):
    """Download content from GitHub and return content or save to file"""
    try:
        if "github.com" in url and "/blob/" in url:
            url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        
        print(f"Downloading from: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        if is_text:
            return response.text
        else:
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
        return access_code.strip()
    return None

def verify_access_code(correct_code):
    """Display dialog requesting access code and validate with custom interface"""
    login_window = tk.Tk()
    login_window.title("Authentication for SUT")
    login_window.geometry("440x300")
    login_window.resizable(False, False)
    login_window.configure(bg="#F2F2F2")
    login_window.overrideredirect(True)
    
    login_window.update_idletasks()
    width = login_window.winfo_width()
    height = login_window.winfo_height()
    x = (login_window.winfo_screenwidth() // 2) - (width // 2)
    y = (login_window.winfo_screenheight() // 2) - (height // 2)
    login_window.geometry(f'{width}x{height}+{x}+{y}')
    
    attempts = [0]
    max_attempts = 3
    result = [False]
    
    title_bar = tk.Frame(login_window, bg="#F2F2F2", height=30)
    title_bar.pack(fill=tk.X)
    
    title_text = tk.Label(title_bar, text="Authentication for SUT", bg="#F2F2F2", fg="#202124", font=("Segoe UI", 11))
    title_text.pack(side=tk.LEFT, padx=10)
    
    close_button = tk.Button(title_bar, text="✕", bg="#E34234", fg="white", font=("Segoe UI", 11, "bold"), width=3, height=1, bd=0, relief=tk.FLAT, command=login_window.destroy)
    close_button.pack(side=tk.RIGHT, padx=0, pady=0)
    
    content_frame = tk.Frame(login_window, bg="#F2F2F2")
    content_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=(5, 20))
    
    top_frame = tk.Frame(content_frame, bg="#F2F2F2")
    top_frame.pack(pady=(5, 25))
    
    icon_url = "https://github.com/alfienguyenn/SVS/blob/main/authen_icon.png"
    icon_data = download_content(icon_url, is_text=False)
    
    try:
        from PIL import Image, ImageTk
        if icon_data:
            img = Image.open(BytesIO(icon_data))
            img = img.resize((48, 48))
            icon_img = ImageTk.PhotoImage(img)
            icon_label = tk.Label(top_frame, image=icon_img, bg="#F2F2F2")
            icon_label.image = icon_img
            icon_label.pack(side=tk.LEFT, padx=(0, 15))
        else:
            shield_icon = tk.Canvas(top_frame, width=48, height=48, bg="#F2F2F2", highlightthickness=0)
            shield_icon.pack(side=tk.LEFT, padx=(0, 15))
            shield_icon.create_oval(8, 8, 40, 40, fill="#4285F4", outline="#4285F4")
            shield_icon.create_line(16, 24, 24, 32, width=3, fill="white")
            shield_icon.create_line(24, 32, 34, 18, width=3, fill="white")
    except ImportError:
        shield_icon = tk.Canvas(top_frame, width=48, height=48, bg="#F2F2F2", highlightthickness=0)
        shield_icon.pack(side=tk.LEFT, padx=(0, 15))
        shield_icon.create_oval(8, 8, 40, 40, fill="#4285F4", outline="#4285F4")
        shield_icon.create_line(16, 24, 24, 32, width=3, fill="white")
        shield_icon.create_line(24, 32, 34, 18, width=3, fill="white")
    
    title_label = tk.Label(top_frame, text="Authentication for SUT", font=("Segoe UI", 18, "bold"), fg="#202124", bg="#F2F2F2")
    title_label.pack(side=tk.LEFT)
    
    message_label = tk.Label(content_frame, text=f"Enter access code to continue.\nYou have {max_attempts} attempts remaining:", font=("Segoe UI", 11), fg="#5F6368", bg="#F2F2F2", justify=tk.LEFT)
    message_label.pack(anchor=tk.W, pady=(0, 15))
    
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
    
    entry_frame = tk.Frame(content_frame, bg="#F2F2F2")
    entry_frame.pack(fill=tk.X, pady=(0, 25))
    
    entry = PasswordEntry(entry_frame, font=("Segoe UI", 11), bg="white", relief=tk.FLAT, highlightbackground="#DADCE0", highlightthickness=1, bd=0)
    entry.pack(fill=tk.X, ipady=5)
    entry.focus()
    
    def on_key_event(event):
        if event.keysym == 'BackSpace':
            entry.remove_char()
        elif event.keysym == 'Return':
            check_password()
        elif len(event.char) == 1 and event.char.isprintable():
            entry.add_char(event.char)
        return "break"
    
    entry.bind("<Key>", on_key_event)
    
    button_frame = tk.Frame(content_frame, bg="#F2F2F2")
    button_frame.pack(fill=tk.X, pady=(0, 10))
    
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
                message_label.config(text=f"Enter access code to continue.\nYou have {remaining} attempts remaining:")
                entry.password = ""
                entry.delete(0, tk.END)
                entry.focus()
            else:
                messagebox.showerror("Error", "Too many incorrect attempts. The program will exit.")
                login_window.destroy()
    
    ok_button = tk.Button(button_frame, text="OK", command=check_password, font=("Segoe UI", 11), bg="#4285F4", fg="white", relief=tk.FLAT, bd=0, padx=15, pady=8, width=8)
    ok_button.pack(side=tk.LEFT)
    
    cancel_button = tk.Button(button_frame, text="Cancel", command=login_window.destroy, font=("Segoe UI", 11), bg="white", fg="#3C4043", relief=tk.FLAT, bd=0, highlightbackground="#DADCE0", highlightthickness=1, padx=15, pady=8, width=8)
    cancel_button.pack(side=tk.RIGHT)
    
    login_window.bind("<Return>", lambda event: check_password())
    
    def start_move(event):
        login_window.x = event.x
        login_window.y = event.y

    def do_move(event):
        dx = event.x - login_window.x
        dy = event.y - login_window.y
        x = login_window.winfo_x() + dx
        y = login_window.winfo_y() + dy
        login_window.geometry(f"+{x}+{y}")

    title_bar.bind("<ButtonPress-1>", start_move)
    title_bar.bind("<B1-Motion>", do_move)
    title_text.bind("<ButtonPress-1>", start_move)
    title_text.bind("<B1-Motion>", do_move)
    
    login_window.mainloop()
    
    return result[0]

def check_required_modules():
    """Check and install required modules if needed"""
    required_modules = ['requests', 'tkinter', 'PIL']
    
    for module in required_modules:
        try:
            if module == 'tkinter':
                __import__(module)
            elif module == 'PIL':
                try:
                    __import__(module)
                except ImportError:
                    module = 'pillow'
                    raise ImportError
            else:
                subprocess.run([sys.executable, '-c', f'import {module}'], check=True, capture_output=True)
            print(f"✓ Module {module} is installed")
        except (ImportError, subprocess.CalledProcessError):
            print(f"Module {module} is not installed. Installing...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', module], check=True)
                print(f"✓ Module {module} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"Error installing {module}: {e}")
                return False
    return True

def run_script(script_path):
    """Run Python script with admin rights on Windows and pass --no-loop parameter"""
    try:
        if sys.platform == 'win32':
            print("Requesting administrator privileges...")
            try:
                import ctypes
                if not ctypes.windll.shell32.IsUserAnAdmin():
                    print("Script requires administrator privileges. Requesting...")
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script_path}" --no-loop', None, 1)
                    time.sleep(2)
                    return True
                else:
                    subprocess.run([sys.executable, script_path, "--no-loop"], check=True)
                    return True
            except Exception as e:
                print(f"Error requesting admin privileges: {e}")
                try:
                    subprocess.run([sys.executable, script_path, "--no-loop"], check=True)
                    return True
                except Exception as sub_e:
                    print(f"Error running script: {sub_e}")
                    return False
        else:
            print("Running script...")
            subprocess.run([sys.executable, script_path, "--no-loop"], check=True)
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error running script: {e}")
        return False
    except Exception as e:
        print(f"Undefined error: {e}")
        return False

def main():
    """Main function to authenticate, download and run SVS Tools script"""
    print("SVS Tools - Secure Version")
    print("=" * 50)
    
    atexit.register(cleanup)
    
    # Check if --no-loop is passed (indicating this is the main script execution)
    if "--no-loop" in sys.argv:
        print("Running main SVS Tools functionality...")
        messagebox.showinfo("SVS Tools", "Welcome to SVS Tools! Main functionality would run here.")
        return
    
    print("Checking internet connection...")
    if not check_internet_connection():
        print("No internet connection detected.")
        messagebox.showerror("Connection Error", "No internet connection detected.\nPlease connect to the internet and try again.")
        return
    
    print("Internet connection confirmed.")
    
    if not check_required_modules():
        print("Unable to install required modules. Exiting.")
        return
    
    access_code_url = "https://github.com/alfienguyenn/SVS/blob/main/AccessCode.txt"
    script_url = "https://github.com/alfienguyenn/SVS/blob/main/SVS_Tools.py"
    
    print("Downloading access code...")
    access_code = get_access_code(access_code_url)
    
    if not access_code:
        print("Unable to download access code. Exiting.")
        return
    
    if not verify_access_code(access_code):
        print("Authentication failed. Exiting.")
        return
        
    print("Authentication successful! Downloading script...")
    script_content = download_content(script_url)
    
    if not script_content:
        print("Unable to download script. Exiting.")
        return
    
    temp_dir = tempfile.gettempdir()
    script_path = os.path.join(temp_dir, f"SVS_Tools_{int(time.time())}.py")
    
    if save_to_file(script_content, script_path):
        print(f"Script saved to {script_path}")
        
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
        cleanup()
