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
from tkinter import simpledialog, messagebox, ttk, filedialog
from io import BytesIO
import threading

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
    login_window.title("Authentication for SUT")
    login_window.geometry("440x300")  # Reduced to 2/3 of original size
    login_window.resizable(False, False)
    login_window.configure(bg="#F2F2F2")
    login_window.overrideredirect(True)  # Remove default window decorations
    
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
    
    # Create custom title bar
    title_bar = tk.Frame(login_window, bg="#F2F2F2", height=30)
    title_bar.pack(fill=tk.X)
    
    # Add title text to title bar
    title_text = tk.Label(
        title_bar, 
        text="Authentication for SUT", 
        bg="#F2F2F2", 
        fg="#202124",
        font=("Segoe UI", 11)
    )
    title_text.pack(side=tk.LEFT, padx=10)
    
    # Create custom close button (X) in top-right corner
    close_button = tk.Button(
        title_bar, 
        text="✕", 
        bg="#E34234", 
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=3,
        height=1,
        bd=0,
        relief=tk.FLAT,
        command=login_window.destroy
    )
    close_button.pack(side=tk.RIGHT, padx=0, pady=0)
    
    # Create the main content frame
    content_frame = tk.Frame(login_window, bg="#F2F2F2")
    content_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=(5, 20))
    
    # Create top section with icon and title
    top_frame = tk.Frame(content_frame, bg="#F2F2F2")
    top_frame.pack(pady=(5, 25))
    
    # Try to load the icon from URL
    icon_url = "https://github.com/alfienguyenn/SVS/blob/main/authen_icon.png"
    icon_data = download_content(icon_url, is_text=False)
    
    try:
        # Try to use PIL/Pillow if available
        from PIL import Image, ImageTk
        
        if icon_data:
            img = Image.open(BytesIO(icon_data))
            img = img.resize((48, 48))  # Reduced size
            icon_img = ImageTk.PhotoImage(img)
            
            icon_label = tk.Label(top_frame, image=icon_img, bg="#F2F2F2")
            icon_label.image = icon_img  # Keep a reference to prevent garbage collection
            icon_label.pack(side=tk.LEFT, padx=(0, 15))
        else:
            # Create a shield icon with checkmark as fallback
            shield_icon = tk.Canvas(top_frame, width=48, height=48, bg="#F2F2F2", highlightthickness=0)
            shield_icon.pack(side=tk.LEFT, padx=(0, 15))
            
            # Draw a shield shape
            shield_icon.create_oval(8, 8, 40, 40, fill="#4285F4", outline="#4285F4")
            # Draw a checkmark
            shield_icon.create_line(16, 24, 24, 32, width=3, fill="white")
            shield_icon.create_line(24, 32, 34, 18, width=3, fill="white")
            
    except ImportError:
        # If PIL is not available, create a simple shield icon
        shield_icon = tk.Canvas(top_frame, width=48, height=48, bg="#F2F2F2", highlightthickness=0)
        shield_icon.pack(side=tk.LEFT, padx=(0, 15))
        
        # Draw a shield shape
        shield_icon.create_oval(8, 8, 40, 40, fill="#4285F4", outline="#4285F4")
        # Draw a checkmark
        shield_icon.create_line(16, 24, 24, 32, width=3, fill="white")
        shield_icon.create_line(24, 32, 34, 18, width=3, fill="white")
    
    # Add title text - improved font rendering
    title_label = tk.Label(
        top_frame,
        text="Authentication for SUT",
        font=("Segoe UI", 18, "bold"),  # Changed font family for better rendering
        fg="#202124",
        bg="#F2F2F2"
    )
    title_label.pack(side=tk.LEFT)
    
    # Create message text with improved font
    message_label = tk.Label(
        content_frame,
        text=f"Enter access code to continue.\nYou have {max_attempts} attempts remaining:",
        font=("Segoe UI", 11),  # Reduced font size with better font family
        fg="#5F6368",
        bg="#F2F2F2",
        justify=tk.LEFT
    )
    message_label.pack(anchor=tk.W, pady=(0, 15))
    
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
    
    # Create a frame for the entry to control its width
    entry_frame = tk.Frame(content_frame, bg="#F2F2F2")
    entry_frame.pack(fill=tk.X, pady=(0, 25))
    
    # Create password entry field with reduced width
    entry = PasswordEntry(
        entry_frame,
        font=("Segoe UI", 11),  # Smaller font with better rendering
        bg="white",
        relief=tk.FLAT,
        highlightbackground="#DADCE0",
        highlightthickness=1,
        bd=0
    )
    entry.pack(fill=tk.X, ipady=5)  # Reduced padding
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
    
    # Create button frame
    button_frame = tk.Frame(content_frame, bg="#F2F2F2")
    button_frame.pack(fill=tk.X, pady=(0, 10))
    
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
                message_label.config(text=f"Enter access code to continue.\nYou have {remaining} attempts remaining:")
                # Clear old password
                entry.password = ""
                entry.delete(0, tk.END)
                entry.focus()
            else:
                messagebox.showerror("Error", "Too many incorrect attempts. The program will exit.")
                login_window.destroy()
    
    # OK button - left aligned
    ok_button = tk.Button(
        button_frame, 
        text="OK", 
        command=check_password,
        font=("Segoe UI", 11),  # Better font rendering
        bg="#4285F4",
        fg="white",
        relief=tk.FLAT,
        bd=0,
        padx=15,
        pady=8,
        width=8
    )
    ok_button.pack(side=tk.LEFT)
    
    # Cancel button - right aligned
    cancel_button = tk.Button(
        button_frame, 
        text="Cancel", 
        command=login_window.destroy,
        font=("Segoe UI", 11),  # Better font rendering
        bg="white",
        fg="#3C4043",
        relief=tk.FLAT,
        bd=0,
        highlightbackground="#DADCE0",
        highlightthickness=1,
        padx=15,
        pady=8,
        width=8
    )
    cancel_button.pack(side=tk.RIGHT)
    
    # Make the OK button the default
    login_window.bind("<Return>", lambda event: check_password())
    
    # Make window draggable
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
    
    # Mainloop
    login_window.mainloop()
    
    # Return authentication result
    return result[0]

def check_required_modules():
    """Check and install required modules if needed"""
    required_modules = ['requests', 'tkinter', 'PIL']
    
    for module in required_modules:
        try:
            if module == 'tkinter':
                # Try to import tkinter
                __import__(module)
            elif module == 'PIL':
                # Try to import PIL (Pillow)
                try:
                    __import__(module)
                except ImportError:
                    # PIL failed, try to install pillow
                    module = 'pillow'  # For pip install
                    raise ImportError
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

#---------- SVS_Tool.py components start here ----------#

class ToggleButton(tk.Canvas):
    def __init__(self, parent, width=80, height=30, bg="#f5f5f7", fg="#ffffff", 
                 activecolor="#4a86e8", inactivecolor="#cccccc", command=None):
        super().__init__(parent, width=width, height=height, bg=bg, 
                         highlightthickness=0, relief='ridge')
        
        self.activecolor = activecolor
        self.inactivecolor = inactivecolor
        self.command = command
        self.state = False
        self.width = width
        self.height = height
        
        # Đảm bảo kích thước cụ thể
        self.config(width=width, height=height)
        
        # Bind cho sự kiện cấu hình lại để vẽ lại khi widget hiển thị
        self.bind("<Configure>", self.on_configure)
        
        # Bind click event
        self.bind("<Button-1>", self.toggle)
        
        # Vẽ ngay sau khi tạo
        self.after(10, self.draw)  # Delay nhỏ để đảm bảo widget đã được tạo
    
    def on_configure(self, event):
        """Gọi khi widget thay đổi kích thước"""
        self.draw()
    
    def draw(self):
        # Xóa hết nội dung trước đó
        self.delete("all")
        
        # Lấy kích thước thực tế của widget
        w = self.winfo_width() or self.width
        h = self.winfo_height() or self.height
        
        # Vẽ với kích thước đúng
        if self.state:
            color = self.activecolor
            circle_x = w - 20
            text = "ON"
            text_x = 15
            text_color = "white"
        else:
            color = self.inactivecolor
            circle_x = 20
            text = "OFF"
            text_x = w - 25
            text_color = "#666666"
        
        # Vẽ rounded rectangle (track)
        self.create_rounded_rect(5, 5, w-5, h-5, 
                               15, fill=color, outline="")
        
        # Vẽ circle (thumb)
        self.create_oval(circle_x-10, 5, circle_x+10, h-5, 
                       fill="white", outline="")
        
        # Vẽ text
        self.create_text(text_x, h/2, text=text, 
                       fill=text_color, font=("Helvetica", 9, "bold"))
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        # Tạo rounded rectangle
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)
    
    def toggle(self, event=None):
        self.state = not self.state
        self.draw()
        if self.command:
            self.command(self.state)
    
    def set(self, state):
        if self.state != state:
            self.state = state
            self.draw()

class WindowsUtilityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SV Utility Tool")
        self.root.geometry("600x550")  # Increased height for more content
        self.root.resizable(True, True)
        
        # Set application theme colors
        self.bg_color = "#f5f5f7"  # Light grey background
        self.accent_color = "#4a86e8"  # Blue accent
        self.btn_color = "#ffffff"  # White buttons
        self.enabled_color = "#009900"  # Green for enabled status
        self.disabled_color = "#990000"  # Red for disabled status
        
        # Apply base theme to root window
        self.root.configure(bg=self.bg_color)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLabel", background=self.bg_color)
        self.style.configure("TButton", font=("Helvetica", 10))
        
        # Center the main window
        self.center_window(self.root)
        
        # Main container setup
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Setup content frames for each function
        self.frames = {}
        self.current_frame = None
        
        # Create frames
        self.create_main_menu()
        self.create_activation_frame()
        self.create_windows_update_frame()
        self.create_advanced_functions_frame()
        
        # Show main menu
        self.show_frame("main_menu")
        
        # Download activation script at startup
        threading.Thread(target=self.download_activation_script, daemon=True).start()
        
        # Setup global keyboard shortcuts (these will work regardless of focus)
        self.root.bind_all("<Key-1>", lambda event: self.handle_key_press(1))
        self.root.bind_all("<Key-2>", lambda event: self.handle_key_press(2))
        self.root.bind_all("<Key-3>", lambda event: self.handle_key_press(3))
        self.root.bind_all("<Escape>", lambda event: self.handle_escape_key())
    
    def run_batch_file(self, batch_file_path, description, show_window=False):
        """Chạy file batch trong thread riêng - có thể chọn hiển thị hoặc ẩn cửa sổ cmd"""
        def execute():
            try:
                self.log_result(f"Starting {description}...")
                
                if sys.platform == 'win32':
                    if show_window:
                        # Hiển thị cửa sổ CMD khi thực thi
                        os.startfile(batch_file_path)
                    else:
                        # Ẩn cửa sổ CMD khi thực thi
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        startupinfo.wShowWindow = subprocess.SW_HIDE
                        
                        # Sử dụng /c để cmd tự đóng sau khi thực thi xong
                        subprocess.Popen(
                            ['cmd', '/c', batch_file_path], 
                            shell=False,
                            startupinfo=startupinfo,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                    
                    self.log_result(f"{description} process started successfully.")
                else:
                    # Fallback cho các hệ điều hành khác
                    if show_window:
                        subprocess.Popen(['bash', batch_file_path], shell=False)
                    else:
                        subprocess.Popen(['bash', batch_file_path], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Kiểm tra trạng thái sau khi hoàn thành
                self.root.after(10000, self.check_activation_status)
                
            except Exception as e:
                self.log_result(f"Error executing {description}: {str(e)}")
        
        # Chạy trong thread riêng
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
    
    def download_activation_script(self):
        """Download the Microsoft Activation Script and extract it properly"""
        try:
            # Tạo thư mục để lưu và giải nén script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            mas_dir = os.path.join(current_dir, "MAS")
            
            # Tạo thư mục MAS nếu chưa tồn tại
            if not os.path.exists(mas_dir):
                os.makedirs(mas_dir)
                self.log_result(f"Created directory: {mas_dir}")
            
            # URL tải script MAS (dùng URL archive để tải file zip)
            url = "https://github.com/massgravel/Microsoft-Activation-Scripts/releases/download/1.5/MAS_1.5_Password_1234.zip"
            zip_path = os.path.join(mas_dir, "MAS.zip")
            
            # Tải file zip về
            self.log_result("Downloading MAS Archive...")
            response = requests.get(url)
            
            if response.status_code == 200:
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                self.log_result("Archive downloaded successfully.")
                
                # Giải nén với mật khẩu
                try:
                    import zipfile
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        # Mật khẩu chuẩn cho file zip này là '1234'
                        zip_ref.extractall(path=mas_dir, pwd=b'1234')
                    self.log_result("Archive extracted successfully.")
                    
                    # Xóa file zip sau khi giải nén
                    os.remove(zip_path)
                    
                    # Tìm đường dẫn đến file MAS_AIO.cmd trong thư mục đã giải nén
                    for root, dirs, files in os.walk(mas_dir):
                        for file in files:
                            if file == "MAS_AIO.cmd":
                                script_path = os.path.join(root, file)
                                self.log_result(f"Found activation script at: {script_path}")
                                return script_path
                    
                    self.log_result("Could not find MAS_AIO.cmd in extracted files.")
                    return False
                    
                except Exception as extract_error:
                    self.log_result(f"Error extracting archive: {str(extract_error)}")
                    return False
            else:
                self.log_result(f"Failed to download archive: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result(f"Error in download process: {str(e)}")
            return False    
    def center_window(self, window):
        """Center the given window on the screen"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def create_modern_button(self, parent, text, command, width=None, bg=None, fg="black", font=None):
        """Create a modern-looking button with elevation effect"""
        if bg is None:
            bg = self.btn_color
        
        if font is None:
            font = ("Helvetica", 10)
            
        frame = tk.Frame(parent, bg=self.bg_color)
        
        # Button with raised effect and rounded corners
        button = tk.Button(
            frame, text=text, command=command,
            bg=bg, fg=fg, font=font,
            relief=tk.RAISED, 
            borderwidth=1,
            padx=10, pady=6
        )
        
        # Apply rounded corners
        button.config(highlightthickness=0, bd=0)
        
        if width:
            button.config(width=width)
            
        button.pack(fill=tk.X, expand=True)
        
        # Hover effect
        def on_enter(e):
            button['bg'] = self.lighten_color(bg)
            
        def on_leave(e):
            button['bg'] = bg
            
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return frame
    
    def lighten_color(self, hex_color, factor=0.1):
        """Lighten a hex color by a factor"""
        # Convert to RGB
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # Lighten
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def create_main_menu(self):
        frame = tk.Frame(self.main_frame, bg=self.bg_color, padx=20, pady=20)
        self.frames["main_menu"] = frame
        
        # Title
        title = tk.Label(frame, text="SV Utility Tool", 
                        font=("Helvetica", 16, "bold"),
                        bg=self.bg_color)
        title.pack(pady=(0, 20))
        
        # Function buttons
        options = [
            ("1", "Activate Windows & Office", lambda: self.show_frame("activation")),
            ("2", "Manage Windows Update", lambda: self.show_frame("windows_update")),
            ("3", "Advanced Functions", lambda: self.show_frame("advanced_functions"))
        ]
        
        for key, text, command in options:
            button_frame = tk.Frame(frame, bg=self.bg_color)
            button_frame.pack(fill=tk.X, pady=8)
            
            key_label = tk.Label(button_frame, text=key, width=3, 
                               bg=self.accent_color, fg="white", 
                               font=("Helvetica", 10, "bold"),
                               relief=tk.RAISED)
            key_label.pack(side=tk.LEFT, padx=(0, 10))
            
            # Create modern button with rounded corners
            btn = self.create_modern_button(
                button_frame, text=text, command=command,
                bg=self.btn_color, font=("Helvetica", 11)
            )
            btn.pack(fill=tk.X, expand=True)
        
        # Keyboard shortcut instructions
        footer = tk.Label(frame, text="Use number keys (1-3) to select a function | ESC to go back",
                        font=("Helvetica", 9), fg="gray", bg=self.bg_color)
        footer.pack(side=tk.BOTTOM, pady=(20, 0))
    
    def create_activation_frame(self):
        frame = tk.Frame(self.main_frame, bg=self.bg_color, padx=20, pady=20)
        self.frames["activation"] = frame
        
        # Header with back button
        header_frame = tk.Frame(frame, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        back_btn = self.create_modern_button(
            header_frame, text="← Back", 
            command=lambda: self.show_frame("main_menu"),
            bg=self.btn_color
        )
        back_btn.pack(side=tk.LEFT)
        
        title = tk.Label(header_frame, text="Activate Windows & Office", 
                        font=("Helvetica", 14, "bold"),
                        bg=self.bg_color)
        title.pack(side=tk.LEFT, padx=10)
        
        # Status frame - NEW - cải tiến theo yêu cầu
        status_frame = tk.LabelFrame(frame, text="Current Status", 
                                    bg=self.bg_color, padx=10, pady=10)
        status_frame.pack(fill=tk.X, pady=10)
        
        # Windows status - đơn giản hóa thành một dòng
        self.windows_status_label = tk.Label(
            status_frame, 
            text="Windows Version: Checking...", 
            anchor="w", 
            bg=self.bg_color,
            font=("Helvetica", 10, "bold")
        )
        self.windows_status_label.pack(fill=tk.X, padx=10, pady=10)
        
        # Office status - đơn giản hóa thành một dòng
        self.office_status_label = tk.Label(
            status_frame, 
            text="Office Version: Checking...", 
            anchor="w", 
            bg=self.bg_color,
            font=("Helvetica", 10, "bold")
        )
        self.office_status_label.pack(fill=tk.X, padx=10, pady=10)
        
        # Actions frame - CHANGED
        actions_frame = tk.LabelFrame(frame, text="Actions", 
                                     bg=self.bg_color, padx=10, pady=10)
        actions_frame.pack(fill=tk.X, expand=False, pady=10)
        
        # Button frame for action buttons
        button_frame = tk.Frame(actions_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Activation buttons
        win_btn = self.create_modern_button(
            button_frame, text="Activate Windows", 
            command=self.activate_windows,
            bg=self.accent_color, fg="white",
            font=("Helvetica", 10, "bold")
        )
        win_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        office_btn = self.create_modern_button(
            button_frame, text="Activate Office", 
            command=self.activate_office,
            bg=self.accent_color, fg="white",
            font=("Helvetica", 10, "bold")
        )
        office_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        both_btn = self.create_modern_button(
            button_frame, text="Activate Windows & Office", 
            command=self.activate_both,
            bg=self.accent_color, fg="white",
            font=("Helvetica", 10, "bold")
        )
        both_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Check status when frame is shown
        frame.bind("<Visibility>", lambda event: self.check_activation_status())
    
    def activate_windows(self):
        """Activate Windows using the MAS_AIO.cmd script with HWID parameter"""
        # Hiển thị hộp thoại xác nhận
        if messagebox.askyesno("Confirm", "Do you want to activate Windows?"):
            try:
                # Kiểm tra xem script đã được tải về và giải nén chưa
                current_dir = os.path.dirname(os.path.abspath(__file__))
                mas_dir = os.path.join(current_dir, "MAS")
                
                # Tìm script MAS_AIO.cmd
                script_path = None
                if os.path.exists(mas_dir):
                    for root, dirs, files in os.walk(mas_dir):
                        for file in files:
                            if file == "MAS_AIO.cmd":
                                script_path = os.path.join(root, file)
                                break
                        if script_path:
                            break
                
                # Nếu không tìm thấy, tải về và giải nén
                if not script_path:
                    self.log_result("Activation script not found. Downloading and extracting...")
                    script_path = self.download_activation_script()
                    if not script_path:
                        messagebox.showerror("Error", "Failed to download activation script. Please check your internet connection and try again.")
                        return
                
                # Đường dẫn đến thư mục chứa script
                script_dir = os.path.dirname(script_path)
                
                # Tạo file batch tạm thời để chạy lệnh
                temp_bat = os.path.join(current_dir, "activate_windows.bat")
                with open(temp_bat, 'w') as f:
                    f.write('@echo off\n')
                    # Chuyển đến thư mục chứa script
                    f.write(f'cd /d "{script_dir}"\n')
                    # Chạy script với tham số
                    f.write(f'call "{script_path}" /HWID\n')
                    f.write('echo.\n')
                    f.write('echo Activation completed. This window will close in 5 seconds...\n')
                    f.write('timeout /t 5\n')
                    f.write('exit\n')
                
                # Hiển thị thông báo đang kích hoạt
                self.log_result(f"Starting Windows activation process using script at: {script_path}")
                
                # Sử dụng helper method để chạy file batch - HIỆN cửa sổ CMD
                self.run_batch_file(temp_bat, "Windows activation", show_window=True)
                
                # Hiển thị thông báo
                messagebox.showinfo("Activation", "Windows activation process has started.\nPlease wait for the process to complete.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start activation process: {str(e)}")
                self.log_result(f"Activation error: {str(e)}")
    
    def activate_office(self):
        """Activate Office using the MAS_AIO.cmd script with Ohook parameter"""
        # Hiển thị hộp thoại xác nhận
        if messagebox.askyesno("Confirm", "Do you want to activate Microsoft Office?"):
            try:
                # Kiểm tra xem script đã được tải về và giải nén chưa
                current_dir = os.path.dirname(os.path.abspath(__file__))
                mas_dir = os.path.join(current_dir, "MAS")
                
                # Tìm script MAS_AIO.cmd
                script_path = None
                if os.path.exists(mas_dir):
                    for root, dirs, files in os.walk(mas_dir):
                        for file in files:
                            if file == "MAS_AIO.cmd":
                                script_path = os.path.join(root, file)
                                break
                        if script_path:
                            break
                
                # Nếu không tìm thấy, tải về và giải nén
                if not script_path:
                    self.log_result("Activation script not found. Downloading and extracting...")
                    script_path = self.download_activation_script()
                    if not script_path:
                        messagebox.showerror("Error", "Failed to download activation script. Please check your internet connection and try again.")
                        return
                
                # Đường dẫn đến thư mục chứa script
                script_dir = os.path.dirname(script_path)
                
                # Tạo file batch tạm thời để chạy lệnh
                temp_bat = os.path.join(current_dir, "activate_office.bat")
                with open(temp_bat, 'w') as f:
                    f.write('@echo off\n')
                    # Chuyển đến thư mục chứa script
                    f.write(f'cd /d "{script_dir}"\n')
                    # Chạy script với tham số
                    f.write(f'call "{script_path}" /Ohook\n')
                    f.write('echo.\n')
                    f.write('echo Activation completed. This window will close in 5 seconds...\n')
                    f.write('timeout /t 5\n')
                    f.write('exit\n')
                
                # Hiển thị thông báo đang kích hoạt
                self.log_result(f"Starting Office activation process using script at: {script_path}")
                
                # Sử dụng helper method để chạy file batch - HIỆN cửa sổ CMD
                self.run_batch_file(temp_bat, "Office activation", show_window=True)
                
                # Hiển thị thông báo
                messagebox.showinfo("Activation", "Office activation process has started.\nPlease wait for the process to complete.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start activation process: {str(e)}")
                self.log_result(f"Activation error: {str(e)}")
    
    def activate_both(self):
        """Activate both Windows and Office using the MAS_AIO.cmd script with HWID and Ohook parameters"""
        # Hiển thị hộp thoại xác nhận
        if messagebox.askyesno("Confirm", "Do you want to activate both Windows and Office?"):
            try:
                # Kiểm tra xem script đã được tải về và giải nén chưa
                current_dir = os.path.dirname(os.path.abspath(__file__))
                mas_dir = os.path.join(current_dir, "MAS")
                
                # Tìm script MAS_AIO.cmd
                script_path = None
                if os.path.exists(mas_dir):
                    for root, dirs, files in os.walk(mas_dir):
                        for file in files:
                            if file == "MAS_AIO.cmd":
                                script_path = os.path.join(root, file)
                                break
                        if script_path:
                            break
                
                # Nếu không tìm thấy, tải về và giải nén
                if not script_path:
                    self.log_result("Activation script not found. Downloading and extracting...")
                    script_path = self.download_activation_script()
                    if not script_path:
                        messagebox.showerror("Error", "Failed to download activation script. Please check your internet connection and try again.")
                        return
                
                # Đường dẫn đến thư mục chứa script
                script_dir = os.path.dirname(script_path)
                
                # Tạo file batch tạm thời để chạy lệnh
                temp_bat = os.path.join(current_dir, "activate_both.bat")
                with open(temp_bat, 'w') as f:
                    f.write('@echo off\n')
                    # Chuyển đến thư mục chứa script
                    f.write(f'cd /d "{script_dir}"\n')
                    # Chạy script với tham số
                    f.write(f'call "{script_path}" /HWID /Ohook\n')
                    f.write('echo.\n')
                    f.write('echo Activation completed. This window will close in 5 seconds...\n')
                    f.write('timeout /t 5\n')
                    f.write('exit\n')
                
                # Hiển thị thông báo đang kích hoạt
                self.log_result(f"Starting Windows and Office activation process using script at: {script_path}")
                
                # Sử dụng helper method để chạy file batch - HIỆN cửa sổ CMD
                self.run_batch_file(temp_bat, "Windows and Office activation", show_window=True)
                
                # Hiển thị thông báo
                messagebox.showinfo("Activation", "Windows and Office activation process has started.\nPlease wait for the process to complete.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start activation process: {str(e)}")
                self.log_result(f"Activation error: {str(e)}")
    
    def check_activation_status(self):
        """Kiểm tra trạng thái kích hoạt của Windows và Office"""
        def check():
            # Kiểm tra phiên bản Windows và trạng thái kích hoạt (gộp lại thành một dòng)
            try:
                # Lấy phiên bản Windows - sử dụng hàm chung run_powershell_command
                returncode, stdout, stderr = run_powershell_command(
                    "(Get-WmiObject -Class Win32_OperatingSystem).Caption"
                )
                version = stdout.strip()
                
                # Kiểm tra trạng thái kích hoạt - sử dụng hàm chung run_powershell_command
                returncode, stdout, stderr = run_powershell_command(
                    "Get-CimInstance -ClassName SoftwareLicensingProduct | " +
                    "Where-Object {$_.Name -like 'Windows*' -and $_.LicenseStatus -eq 1} | " +
                    "Select-Object -First 1 | Select-Object -ExpandProperty LicenseStatus"
                )
                
                # Hiển thị kết quả gộp
                if stdout.strip() == "1":
                    status = "Activated"
                    color = self.enabled_color
                else:
                    status = "Not Activated"
                    color = self.disabled_color
                
                # Cập nhật UI từ main thread
                self.root.after(0, lambda: self.windows_status_label.config(
                    text=f"Windows Version: {version} ({status})",
                    fg=color
                ))
            except Exception as e:
                self.root.after(0, lambda: self.windows_status_label.config(
                    text="Windows Version: Error checking status",
                    fg=self.disabled_color
                ))
            
            # Kiểm tra phiên bản Office và trạng thái kích hoạt (gộp lại thành một dòng) 
            # Đã cải thiện cách kiểm tra Office
            try:
                # Phương pháp 1: Kiểm tra qua registry - nhiều cách để tìm phiên bản Office
                office_version = ""
                office_cmds = [
                    # Kiểm tra Office 365/Microsoft 365
                    "Get-ItemProperty HKLM:\\SOFTWARE\\Microsoft\\Office\\ClickToRun\\Configuration -ErrorAction SilentlyContinue | Select-Object -ExpandProperty ProductReleaseIds",
                    
                    # Kiểm tra các phiên bản Office cài đặt thông thường
                    "(Get-ItemProperty HKLM:\\SOFTWARE\\Microsoft\\Office\\*\\Common\\InstalledPackages\\* -ErrorAction SilentlyContinue).DisplayName",
                    
                    # Kiểm tra Office mới hơn thông qua cách khác
                    "Get-ItemProperty HKLM:\\SOFTWARE\\Microsoft\\Office\\ClickToRun\\Configuration -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Platform",
                ]
                
                for cmd in office_cmds:
                    if not office_version:
                        returncode, stdout, stderr = run_powershell_command(cmd)
                        if stdout.strip():
                            output = stdout.strip()
                            
                            # Xử lý output để lấy phiên bản
                            if "365" in output or "2021" in output or "2019" in output or "2016" in output:
                                if "365" in output:
                                    office_version = "Microsoft 365"
                                elif "2021" in output:
                                    office_version = "Office 2021"
                                elif "2019" in output:
                                    office_version = "Office 2019"
                                elif "2016" in output:
                                    office_version = "Office 2016"
                            elif "x64" in output or "x86" in output:
                                # Nếu phát hiện được nền tảng nhưng không rõ phiên bản
                                office_version = "Microsoft Office"
                
                # Nếu vẫn không tìm thấy, thử một cách cuối cùng
                if not office_version:
                    # Kiểm tra thông qua các thư mục cài đặt
                    returncode, stdout, stderr = run_powershell_command("Test-Path 'C:\\Program Files\\Microsoft Office'")
                    if stdout.strip() == "True":
                        office_version = "Microsoft Office"
                
                # Kiểm tra trạng thái kích hoạt
                returncode, activate_stdout, stderr = run_powershell_command(
                    "Get-CimInstance -ClassName SoftwareLicensingProduct | " +
                    "Where-Object {$_.Name -like '*Office*' -and $_.ApplicationID -like '*Office*' -and $_.LicenseStatus -eq 1} | " +
                    "Select-Object -First 1 | Select-Object -ExpandProperty LicenseStatus"
                )
                
                # Hiển thị kết quả gộp
                if office_version:
                    if activate_stdout.strip() == "1":
                        status = "Activated"
                        color = self.enabled_color
                    else:
                        status = "Not Activated"
                        color = self.disabled_color
                    
                    # Cập nhật UI từ main thread
                    self.root.after(0, lambda: self.office_status_label.config(
                        text=f"Office Version: {office_version} ({status})",
                        fg=color
                    ))
                else:
                    self.root.after(0, lambda: self.office_status_label.config(
                        text="Office Version: Not Detected",
                        fg=self.disabled_color
                    ))
            except Exception as e:
                self.root.after(0, lambda: self.office_status_label.config(
                    text="Office Version: Error checking status",
                    fg=self.disabled_color
                ))
        
        # Chạy trong thread riêng
        thread = threading.Thread(target=check)
        thread.daemon = True
        thread.start()
    
    def create_windows_update_frame(self):
        frame = tk.Frame(self.main_frame, bg=self.bg_color, padx=20, pady=20)
        self.frames["windows_update"] = frame
        
        # Title and Back button
        header_frame = tk.Frame(frame, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        back_btn = self.create_modern_button(
            header_frame, text="← Back", 
            command=lambda: self.show_frame("main_menu"),
            bg=self.btn_color
        )
        back_btn.pack(side=tk.LEFT)
        
        title = tk.Label(header_frame, text="Windows Update Manager", 
                        font=("Helvetica", 14, "bold"),
                        bg=self.bg_color)
        title.pack(side=tk.LEFT, padx=10)
        
        # Status frame
        status_frame = tk.LabelFrame(frame, text="Current Status", 
                                    bg=self.bg_color, padx=10, pady=10)
        status_frame.pack(fill=tk.X, pady=10)
        
        self.update_status_label = tk.Label(
            status_frame, 
            text="Windows Update: Checking...", 
            anchor="w", 
            bg=self.bg_color,
            font=("Helvetica", 10)
        )
        self.update_status_label.pack(fill=tk.X, padx=10, pady=5)
        
        self.driver_status_label = tk.Label(
            status_frame, 
            text="Driver Updates: Checking...", 
            anchor="w", 
            bg=self.bg_color,
            font=("Helvetica", 10)
        )
        self.driver_status_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Actions frame
        actions_frame = tk.LabelFrame(frame, text="Actions", 
                                     bg=self.bg_color, padx=10, pady=10)
        actions_frame.pack(fill=tk.X, expand=False, pady=10)
        
        # Create toggle buttons with explicit dimensions
        self.create_toggles_in_frame(actions_frame)
        
        # Results frame
        results_frame = tk.LabelFrame(frame, text="Results", 
                                     bg=self.bg_color, padx=10, pady=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollable text area with minimum 5 lines
        self.results_text = tk.Text(
            results_frame, 
            height=8,  # Increased height for more visibility
            width=50,
            bg="white",
            fg="black",
            font=("Consolas", 10),
            relief=tk.SUNKEN,
            borderwidth=1
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar to the text area
        scrollbar = tk.Scrollbar(self.results_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.results_text.yview)
        
        # Check current status when frame is shown
        frame.bind("<Visibility>", lambda event: self.check_update_status())
    
    def create_advanced_functions_frame(self):
        frame = tk.Frame(self.main_frame, bg=self.bg_color, padx=20, pady=20)
        self.frames["advanced_functions"] = frame
        
        # Title and Back button
        header_frame = tk.Frame(frame, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        back_btn = self.create_modern_button(
            header_frame, text="← Back", 
            command=lambda: self.show_frame("main_menu"),
            bg=self.btn_color
        )
        back_btn.pack(side=tk.LEFT)
        
        title = tk.Label(header_frame, text="Advanced System Functions", 
                        font=("Helvetica", 14, "bold"),
                        bg=self.bg_color)
        title.pack(side=tk.LEFT, padx=10)
        
        # Button colors (gradient-like colors as in the image)
        button_colors = [
            "#f8c156", # Gradient orange-reddish
            "#5dc698", # Gradient green-teal
            "#b35dbe", # Gradient purple
            "#13bdce"  # Gradient cyan-blue
        ]
        
        # Button texts
        button_texts = [
            "Install chipset driver",
            "B&R driver",
            "???",
            "???"
        ]
        
        # Functions for each button
        button_functions = [
            self.install_chipset_driver,
            self.backup_restore_driver,
            self.install_all_drivers,
            self.install_and_activate_all
        ]
        
        # Container frame for buttons
        buttons_container = tk.Frame(frame, bg=self.bg_color)
        buttons_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Tạo các nút một cách trực tiếp
        for i, (text, color, func) in enumerate(zip(button_texts, button_colors, button_functions)):
            # Tạo frame cho mỗi nút để điều khiển khoảng cách
            btn_frame = tk.Frame(buttons_container, bg=self.bg_color)
            btn_frame.pack(fill=tk.X, pady=10)
            
            # Tạo nút với màu nền và kiểu dáng tương tự như trong ảnh
            btn = tk.Button(
                btn_frame,
                text=text,
                command=func,
                bg=color,
                fg="white",
                font=("Helvetica", 12, "bold"),
                relief=tk.FLAT,
                borderwidth=0,
                padx=20,
                pady=15,
                activebackground=self.lighten_color(color),
                activeforeground="white"
            )
            
            # Hiển thị nút với kích thước đầy đủ
            btn.pack(fill=tk.X, expand=True)
            
            # Hiệu ứng hover
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=self.lighten_color(c)))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))
    
    # Functions for advanced actions
    def install_chipset_driver(self):
        """Install chipset drivers"""
        messagebox.showinfo("Install Chipset Driver", 
                         "This will install the chipset drivers for your system.\n\nThis functionality is not yet implemented.")
    
    def backup_restore_driver(self):
        """Backup or restore drivers"""
        messagebox.showinfo("Backup & Restore Driver", 
                         "This will allow you to backup or restore drivers.\n\nThis functionality is not yet implemented.")
    
    def install_all_drivers(self):
        """Install all drivers"""
        messagebox.showinfo("Install All Drivers", 
                         "This function is under development, we will update it soon in the next version.")
    
    def install_and_activate_all(self):
        """Install all drivers and activate Windows & Office"""
        messagebox.showinfo("Complete Setup", 
                         "This function is under development, we will update it soon in the next version.")
    
    def create_toggles_in_frame(self, actions_frame):
        """Tạo các nút gạt trong frame Windows Update Manager"""
        # Toggle buttons for Windows Update and Driver Updates
        update_toggle_frame = tk.Frame(actions_frame, bg=self.bg_color)
        update_toggle_frame.pack(fill=tk.X, pady=10)
        
        update_label = tk.Label(update_toggle_frame, text="Enable Windows Update", 
                              bg=self.bg_color, anchor="w", font=("Helvetica", 10))
        update_label.pack(side=tk.LEFT, padx=10)
        
        # Tạo toggle button với kích thước cụ thể
        self.update_toggle = ToggleButton(
            update_toggle_frame, 
            activecolor="#00aa00",  # Green for ON
            inactivecolor="#cccccc",  # Grey for OFF
            command=self.toggle_update_status,
            width=80,   # Kích thước cụ thể
            height=30
        )
        self.update_toggle.pack(side=tk.RIGHT, padx=10)
        
        # Driver updates toggle
        driver_toggle_frame = tk.Frame(actions_frame, bg=self.bg_color)
        driver_toggle_frame.pack(fill=tk.X, pady=10)
        
        driver_label = tk.Label(driver_toggle_frame, text="Allow Driver Updates", 
                              bg=self.bg_color, anchor="w", font=("Helvetica", 10))
        driver_label.pack(side=tk.LEFT, padx=10)
        
        # Tạo toggle button với kích thước cụ thể
        self.driver_toggle = ToggleButton(
            driver_toggle_frame, 
            activecolor="#00aa00",  # Green for ON
            inactivecolor="#cccccc",  # Grey for OFF
            command=self.toggle_driver_status,
            width=80,   # Kích thước cụ thể
            height=30
        )
        self.driver_toggle.pack(side=tk.RIGHT, padx=10)
        
        # Thực hiện update sau khi tạo để đảm bảo nút hiển thị đúng
        self.update_toggle.update()
        self.driver_toggle.update()
    
    def check_update_status(self):
        def check():
            # Check Windows Update service status
            try:
                returncode, stdout, stderr = run_powershell_command("Get-Service -Name wuauserv | Select-Object -ExpandProperty Status")
                status = stdout.strip()
                
                # Sử dụng after() để cập nhật GUI từ main thread
                self.root.after(0, lambda: self.update_ui_status(status))
                    
            except Exception as e:
                # Sử dụng after() để cập nhật lỗi từ main thread
                self.root.after(0, lambda: self.update_status_label.config(text=f"Error checking status: {str(e)}"))
        
        # Vẫn chạy kiểm tra trong thread riêng, nhưng cập nhật UI qua after()
        thread = threading.Thread(target=check)
        thread.daemon = True
        thread.start()
    
    def update_ui_status(self, status):
        """Cập nhật UI dựa trên trạng thái nhận được - gọi từ main thread"""
        if status.lower() == "running":
            self.update_status_label.config(
                text="Windows Update: Enabled (Running)",
                fg=self.enabled_color
            )
            self.update_toggle.set(True)
        else:
            self.update_status_label.config(
                text="Windows Update: Disabled (Stopped)",
                fg=self.disabled_color
            )
            self.update_toggle.set(False)
        
        # Kiểm tra driver update policy
        try:
            returncode, stdout, stderr = run_powershell_command("Get-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate' -Name 'ExcludeWUDriversInQualityUpdate' -ErrorAction SilentlyContinue")
            
            if "ExcludeWUDriversInQualityUpdate : 1" in stdout:
                self.driver_status_label.config(
                    text="Driver Updates: Blocked",
                    fg=self.disabled_color
                )
                self.driver_toggle.set(False)
            else:
                self.driver_status_label.config(
                    text="Driver Updates: Allowed",
                    fg=self.enabled_color
                )
                self.driver_toggle.set(True)
        except Exception as e:
            self.log_result(f"Error checking driver policy: {str(e)}")
    
    def toggle_update_status(self, enable):
        def execute():
            try:
                if enable:
                    # Enable Windows Update
                    self.root.after(0, lambda: self.log_result("Enabling Windows Update..."))
                    returncode, stdout, stderr = run_powershell_command(
                        "Set-Service -Name wuauserv -StartupType Automatic; Start-Service -Name wuauserv"
                    )
                    
                    # Cập nhật UI từ main thread
                    self.root.after(0, lambda: self.update_after_toggle(True))
                else:
                    # Disable Windows Update
                    self.root.after(0, lambda: self.log_result("Disabling Windows Update..."))
                    returncode, stdout, stderr = run_powershell_command(
                        "Stop-Service -Name wuauserv -Force; Set-Service -Name wuauserv -StartupType Disabled"
                    )
                    
                    # Cập nhật UI từ main thread
                    self.root.after(0, lambda: self.update_after_toggle(False))
            
            except Exception as e:
                # Báo lỗi qua main thread
                self.root.after(0, lambda: self.log_result(f"Error: {str(e)}"))
        
        # Chạy trong thread riêng
        thread = threading.Thread(target=execute)
        thread.daemon = True
        thread.start()
    
    def update_after_toggle(self, enabled):
        """Cập nhật UI sau khi toggle - gọi từ main thread"""
        if enabled:
            self.log_result("Windows Update has been enabled.")
            self.update_status_label.config(
                text="Windows Update: Enabled (Running)",
                fg=self.enabled_color
            )
        else:
            self.log_result("Windows Update has been disabled.")
            self.update_status_label.config(
                text="Windows Update: Disabled (Stopped)",
                fg=self.disabled_color
            )
    
    def toggle_driver_status(self, allow):
        def execute():
            try:
                if allow:
                    # Allow driver updates
                    self.root.after(0, lambda: self.log_result("Allowing driver updates..."))
                    returncode, stdout, stderr = run_powershell_command(
                        "Remove-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate' -Name 'ExcludeWUDriversInQualityUpdate' -ErrorAction SilentlyContinue"
                    )
                    
                    # Cập nhật UI từ main thread
                    self.root.after(0, lambda: self.update_driver_toggle(True))
                else:
                    # Block driver updates
                    self.root.after(0, lambda: self.log_result("Blocking driver updates..."))
                    returncode, stdout, stderr = run_powershell_command(
                        "New-Item -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate' -Force -ErrorAction SilentlyContinue | Out-Null; " +
                        "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate' -Name 'ExcludeWUDriversInQualityUpdate' -Value 1 -Type DWord -Force"
                    )
                    
                    # Cập nhật UI từ main thread
                    self.root.after(0, lambda: self.update_driver_toggle(False))
            
            except Exception as e:
                # Báo lỗi qua main thread
                self.root.after(0, lambda: self.log_result(f"Error: {str(e)}"))
        
        # Chạy trong thread riêng
        thread = threading.Thread(target=execute)
        thread.daemon = True
        thread.start()
    
    def update_driver_toggle(self, allowed):
        """Cập nhật UI sau khi toggle driver - gọi từ main thread"""
        if allowed:
            self.log_result("Driver updates through Windows Update have been allowed.")
            self.driver_status_label.config(
                text="Driver Updates: Allowed",
                fg=self.enabled_color
            )
        else:
            self.log_result("Driver updates through Windows Update have been blocked.")
            self.driver_status_label.config(
                text="Driver Updates: Blocked",
                fg=self.disabled_color
            )
    
    def log_result(self, message):
        def do_log():
            if hasattr(self, 'results_text'):
                self.results_text.config(state=tk.NORMAL)
                self.results_text.insert(tk.END, message + "\n")
                self.results_text.see(tk.END)
                self.results_text.config(state=tk.DISABLED)
        
        # Nếu được gọi từ thread khác, sử dụng after() để đảm bảo thread-safe
        if threading.current_thread() is not threading.main_thread():
            self.root.after(0, do_log)
        else:
            do_log()
    
    def show_frame(self, frame_id):
        # Hide current frame if any
        if self.current_frame:
            self.frames[self.current_frame].pack_forget()
        
        # Show new frame
        self.frames[frame_id].pack(fill=tk.BOTH, expand=True)
        self.current_frame = frame_id
        
        # Kích hoạt các chức năng đặc biệt sau khi hiển thị frame
        if frame_id == "windows_update":
            # Kiểm tra trạng thái Windows Update khi hiển thị frame
            self.check_update_status()
        elif frame_id == "activation":
            # Kiểm tra trạng thái kích hoạt khi hiển thị frame
            self.check_activation_status()
    
    def handle_key_press(self, key):
        if self.current_frame == "main_menu":
            if key == 1:
                self.show_frame("activation")
            elif key == 2:
                self.show_frame("windows_update")
            elif key == 3:
                self.show_frame("advanced_functions")
    
    def handle_escape_key(self):
        # If we're in a sub-frame, return to main menu
        if self.current_frame != "main_menu":
            self.show_frame("main_menu")
    
    def dummy_function(self):
        """Placeholder function for buttons not yet implemented"""
        messagebox.showinfo("Info", "This functionality is not yet implemented.")

def run_powershell_command(command):
    """Run a simple PowerShell command with hidden window"""
    try:
        # Tạo startupinfo object để ẩn cửa sổ PowerShell
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
        result = subprocess.run(
            ["powershell", "-WindowStyle", "Hidden", "-Command", command], 
            capture_output=True, 
            text=True,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def run_as_admin():
    """Restart script with admin privileges"""
    script = os.path.abspath(sys.argv[0])
    args = ' '.join(sys.argv[1:])
    
    try:
        if sys.platform == 'win32':
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("Requesting Administrator privileges...")
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, f'"{script}" {args}', None, 1)
                sys.exit()
    except Exception as e:
        print(f"Error requesting Admin privileges: {e}")

def main():
    """Main function to authenticate, and run SVS Tools directly instead of downloading it"""
    print("SVS Tools - Secure Version")
    print("=" * 50)
    
    # Register cleanup function to run when exiting program
    atexit.register(cleanup)
    
    # Request admin privileges FIRST, before doing anything else
    # This will restart the script with admin rights if needed
    run_as_admin()
    
    # Check internet connection
    print("Checking internet connection...")
    if not check_internet_connection():
        print("No internet connection detected.")
        messagebox.showerror("Connection Error", 
                            "No internet connection detected.\nPlease connect to the internet and try again.")
        return
    
    print("Internet connection confirmed.")
    
    # Check required modules
    if not check_required_modules():
        print("Unable to install required modules. Exiting.")
        return
    
    # URL for access code
    access_code_url = "https://github.com/alfienguyenn/SVS/blob/main/AccessCode.txt"
    
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
        
    # After successful authentication, run the app directly
    print("Authentication successful! Starting SVS Tools...")
    
    # Create and run the application
    root = tk.Tk()
    app = WindowsUtilityApp(root)
    root.mainloop()

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
