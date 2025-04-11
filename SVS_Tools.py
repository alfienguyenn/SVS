import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import sys
import threading
import requests  # Added for downloading files

# Windows-specific subprocess flags
if sys.platform == 'win32':
    CREATE_NEW_CONSOLE = 0x00000010
    DETACHED_PROCESS = 0x00000008
    CREATE_NO_WINDOW = 0x08000000
else:
    # Placeholders for non-Windows platforms
    CREATE_NEW_CONSOLE = 0
    DETACHED_PROCESS = 0
    CREATE_NO_WINDOW = 0

class ToggleButton(tk.Canvas):
    # [ToggleButton class remains unchanged]
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
        self.root.title("Windows Utility")
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
    
    def download_activation_script(self):
        """Download the Microsoft Activation Script at startup"""
        try:
            # URL to the raw content of the file (using raw content URL)
            url = "https://raw.githubusercontent.com/massgravel/Microsoft-Activation-Scripts/master/MAS/All-In-One-Version-KL/MAS_AIO.cmd"
            
            # Path to save the file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(current_dir, "MAS_AIO.cmd")
            
            # Download the file
            self.log_result("Downloading activation script...")
            response = requests.get(url)
            
            if response.status_code == 200:
                with open(script_path, 'wb') as f:
                    f.write(response.content)
                self.log_result("Activation script downloaded successfully.")
            else:
                self.log_result(f"Failed to download script: HTTP {response.status_code}")
        except Exception as e:
            self.log_result(f"Error downloading script: {str(e)}")
    
    # [Other existing methods remain unchanged]
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
        title = tk.Label(frame, text="Windows Utility Tool", 
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
    
    # Updated activation methods to use the downloaded script
    def activate_windows(self):
        """Activate Windows using the MAS_AIO.cmd script with HWID parameter"""
        # Hiển thị hộp thoại xác nhận
        if messagebox.askyesno("Confirm", "Do you want to activate Windows?"):
            try:
                # Lấy đường dẫn của thư mục hiện tại
                current_dir = os.path.dirname(os.path.abspath(__file__))
                script_path = os.path.join(current_dir, "MAS_AIO.cmd")
                
                # Kiểm tra xem file đã được tải về chưa
                if not os.path.exists(script_path):
                    messagebox.showerror("Error", "Activation script not found. Please restart the application.")
                    return
                
                # Tạo file batch tạm thời để chạy lệnh
                temp_bat = os.path.join(current_dir, "activate_windows.bat")
                with open(temp_bat, 'w') as f:
                    f.write('@echo off\n')
                    f.write(f'call "%~dp0MAS_AIO.cmd" /HWID\n')
                    f.write('cd \\\n')
                    f.write('(goto) 2>nul & (if "%~dp0"=="%SystemRoot%\\Setup\\Scripts\\" rd /s /q "%~dp0")\n')
                    f.write('exit\n')
                
                # Hiển thị thông báo đang kích hoạt
                self.log_result("Starting Windows activation process...")
                
                # Tạo startupinfo để chạy batch trong cửa sổ tách biệt
                if sys.platform == 'win32':
                    # Chạy file batch với quyền admin trong cửa sổ riêng biệt
                    process = subprocess.Popen(
                        temp_bat, 
                        shell=True,
                        creationflags=CREATE_NEW_CONSOLE,  # Tạo cửa sổ mới tách biệt
                    )
                else:
                    # Cho các hệ điều hành khác
                    process = subprocess.Popen(temp_bat, shell=True)
                
                # Hiển thị thông báo
                messagebox.showinfo("Activation", "Windows activation process has started.\nPlease wait for the process to complete.")
                
                # Làm mới trạng thái sau khi quá trình kích hoạt hoàn tất
                self.root.after(10000, self.check_activation_status)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start activation process: {str(e)}")
                self.log_result(f"Activation error: {str(e)}")
    
    def activate_office(self):
        """Activate Office using the MAS_AIO.cmd script with Ohook parameter"""
        # Hiển thị hộp thoại xác nhận
        if messagebox.askyesno("Confirm", "Do you want to activate Microsoft Office?"):
            try:
                # Lấy đường dẫn của thư mục hiện tại
                current_dir = os.path.dirname(os.path.abspath(__file__))
                script_path = os.path.join(current_dir, "MAS_AIO.cmd")
                
                # Kiểm tra xem file đã được tải về chưa
                if not os.path.exists(script_path):
                    messagebox.showerror("Error", "Activation script not found. Please restart the application.")
                    return
                
                # Tạo file batch tạm thời để chạy lệnh
                temp_bat = os.path.join(current_dir, "activate_office.bat")
                with open(temp_bat, 'w') as f:
                    f.write('@echo off\n')
                    f.write(f'call "%~dp0MAS_AIO.cmd" /Ohook\n')
                    f.write('cd \\\n')
                    f.write('(goto) 2>nul & (if "%~dp0"=="%SystemRoot%\\Setup\\Scripts\\" rd /s /q "%~dp0")\n')
                    f.write('exit\n')
                
                # Hiển thị thông báo đang kích hoạt
                self.log_result("Starting Office activation process...")
                
                # Tạo startupinfo để chạy batch trong cửa sổ tách biệt
                if sys.platform == 'win32':
                    # Chạy file batch với quyền admin trong cửa sổ riêng biệt
                    process = subprocess.Popen(
                        temp_bat, 
                        shell=True,
                        creationflags=CREATE_NEW_CONSOLE,  # Tạo cửa sổ mới tách biệt
                    )
                else:
                    # Cho các hệ điều hành khác
                    process = subprocess.Popen(temp_bat, shell=True)
                
                # Hiển thị thông báo
                messagebox.showinfo("Activation", "Office activation process has started.\nPlease wait for the process to complete.")
                
                # Làm mới trạng thái sau khi quá trình kích hoạt hoàn tất
                self.root.after(10000, self.check_activation_status)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start activation process: {str(e)}")
                self.log_result(f"Activation error: {str(e)}")
    
    def activate_both(self):
        """Activate both Windows and Office using the MAS_AIO.cmd script with HWID and Ohook parameters"""
        # Hiển thị hộp thoại xác nhận
        if messagebox.askyesno("Confirm", "Do you want to activate both Windows and Office?"):
            try:
                # Lấy đường dẫn của thư mục hiện tại
                current_dir = os.path.dirname(os.path.abspath(__file__))
                script_path = os.path.join(current_dir, "MAS_AIO.cmd")
                
                # Kiểm tra xem file đã được tải về chưa
                if not os.path.exists(script_path):
                    messagebox.showerror("Error", "Activation script not found. Please restart the application.")
                    return
                
                # Tạo file batch tạm thời để chạy lệnh
                temp_bat = os.path.join(current_dir, "activate_both.bat")
                with open(temp_bat, 'w') as f:
                    f.write('@echo off\n')
                    f.write(f'call "%~dp0MAS_AIO.cmd" /HWID /Ohook\n')
                    f.write('cd \\\n')
                    f.write('(goto) 2>nul & (if "%~dp0"=="%SystemRoot%\\Setup\\Scripts\\" rd /s /q "%~dp0")\n')
                    f.write('exit\n')
                
                # Hiển thị thông báo đang kích hoạt
                self.log_result("Starting Windows and Office activation process...")
                
                # Tạo startupinfo để chạy batch trong cửa sổ tách biệt
                if sys.platform == 'win32':
                    # Chạy file batch với quyền admin trong cửa sổ riêng biệt
                    process = subprocess.Popen(
                        temp_bat, 
                        shell=True,
                        creationflags=CREATE_NEW_CONSOLE,  # Tạo cửa sổ mới tách biệt
                    )
                else:
                    # Cho các hệ điều hành khác
                    process = subprocess.Popen(temp_bat, shell=True)
                
                # Hiển thị thông báo
                messagebox.showinfo("Activation", "Windows and Office activation process has started.\nPlease wait for the process to complete.")
                
                # Làm mới trạng thái sau khi quá trình kích hoạt hoàn tất
                self.root.after(10000, self.check_activation_status)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start activation process: {str(e)}")
                self.log_result(f"Activation error: {str(e)}")
    
    # [Other methods remain the same]
    def check_activation_status(self):
        """Kiểm tra trạng thái kích hoạt của Windows và Office"""
        def check():
            # Kiểm tra phiên bản Windows và trạng thái kích hoạt (gộp lại thành một dòng)
            try:
                # Lấy phiên bản Windows
                result_version = subprocess.run(["powershell", "-Command", 
                                      "(Get-WmiObject -Class Win32_OperatingSystem).Caption"], 
                                     capture_output=True, text=True)
                version = result_version.stdout.strip()
                
                # Kiểm tra trạng thái kích hoạt
                result_activation = subprocess.run(["powershell", "-Command", 
                                      "Get-CimInstance -ClassName SoftwareLicensingProduct | " +
                                      "Where-Object {$_.Name -like 'Windows*' -and $_.LicenseStatus -eq 1} | " +
                                      "Select-Object -First 1 | Select-Object -ExpandProperty LicenseStatus"], 
                                     capture_output=True, text=True)
                
                # Hiển thị kết quả gộp
                if result_activation.stdout.strip() == "1":
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
                        result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
                        if result.stdout.strip():
                            output = result.stdout.strip()
                            
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
                    result = subprocess.run(["powershell", "-Command", 
                                          "Test-Path 'C:\\Program Files\\Microsoft Office'"], 
                                         capture_output=True, text=True)
                    if result.stdout.strip() == "True":
                        office_version = "Microsoft Office"
                
                # Kiểm tra trạng thái kích hoạt
                result_activation = subprocess.run(["powershell", "-Command", 
                                                "Get-CimInstance -ClassName SoftwareLicensingProduct | " +
                                                "Where-Object {$_.Name -like '*Office*' -and $_.ApplicationID -like '*Office*' -and $_.LicenseStatus -eq 1} | " +
                                                "Select-Object -First 1 | Select-Object -ExpandProperty LicenseStatus"], 
                                               capture_output=True, text=True)
                
                # Hiển thị kết quả gộp
                if office_version:
                    if result_activation.stdout.strip() == "1":
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
                result = subprocess.run(["powershell", "-Command", "Get-Service -Name wuauserv | Select-Object -ExpandProperty Status"], 
                                      capture_output=True, text=True)
                status = result.stdout.strip()
                
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
            result = subprocess.run(["powershell", "-Command", "Get-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate' -Name 'ExcludeWUDriversInQualityUpdate' -ErrorAction SilentlyContinue"], 
                                  capture_output=True, text=True)
            
            if "ExcludeWUDriversInQualityUpdate : 1" in result.stdout:
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
                    result = subprocess.run(["powershell", "-Command", 
                                          "Set-Service -Name wuauserv -StartupType Automatic; Start-Service -Name wuauserv"],
                                         capture_output=True, text=True)
                    
                    # Cập nhật UI từ main thread
                    self.root.after(0, lambda: self.update_after_toggle(True))
                else:
                    # Disable Windows Update
                    self.root.after(0, lambda: self.log_result("Disabling Windows Update..."))
                    result = subprocess.run(["powershell", "-Command", 
                                          "Stop-Service -Name wuauserv -Force; Set-Service -Name wuauserv -StartupType Disabled"],
                                         capture_output=True, text=True)
                    
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
                    result = subprocess.run(["powershell", "-Command", 
                                          "Remove-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate' -Name 'ExcludeWUDriversInQualityUpdate' -ErrorAction SilentlyContinue"],
                                         capture_output=True, text=True)
                    
                    # Cập nhật UI từ main thread
                    self.root.after(0, lambda: self.update_driver_toggle(True))
                else:
                    # Block driver updates
                    self.root.after(0, lambda: self.log_result("Blocking driver updates..."))
                    result = subprocess.run(["powershell", "-Command", 
                                          "New-Item -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate' -Force -ErrorAction SilentlyContinue | Out-Null; " +
                                          "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate' -Name 'ExcludeWUDriversInQualityUpdate' -Value 1 -Type DWord -Force"],
                                         capture_output=True, text=True)
                    
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
    """Run a simple PowerShell command"""
    try:
        result = subprocess.run(["powershell", "-Command", command], 
                              capture_output=True, text=True)
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

if __name__ == "__main__":
    run_as_admin()  # Request Admin privileges
    
    root = tk.Tk()
    app = WindowsUtilityApp(root)
    root.mainloop()
