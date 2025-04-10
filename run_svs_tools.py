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

# Biến toàn cục để theo dõi các tệp cần xóa
temp_files = []

def cleanup():
    """Xóa toàn bộ dữ liệu tạm đã tải xuống"""
    global temp_files
    
    print("\nDọn dẹp dữ liệu tạm...")
    for file_path in temp_files:
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"✓ Đã xóa file: {file_path}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                print(f"✓ Đã xóa thư mục: {file_path}")
        except Exception as e:
            print(f"! Lỗi khi xóa {file_path}: {e}")

def download_content(url, is_text=True):
    """Tải nội dung từ GitHub và trả về nội dung hoặc lưu vào tệp"""
    try:
        # Chuyển đổi URL GitHub thành URL raw nếu cần
        if "github.com" in url and "/blob/" in url:
            url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        
        print(f"Đang tải từ: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        if is_text:
            return response.text
        else:
            # Nếu không phải text, trả về nội dung nhị phân
            return response.content
    except Exception as e:
        print(f"Lỗi khi tải nội dung: {e}")
        return None

def save_to_file(content, destination):
    """Lưu nội dung vào tệp"""
    try:
        if isinstance(content, str):
            with open(destination, 'w', encoding='utf-8') as file:
                file.write(content)
        else:
            with open(destination, 'wb') as file:
                file.write(content)
        
        # Thêm file vào danh sách cần xóa
        global temp_files
        temp_files.append(destination)
        
        print(f"✓ Đã lưu thành công vào {destination}")
        return True
    except Exception as e:
        print(f"Lỗi khi lưu tệp: {e}")
        return False

def get_access_code(url):
    """Tải và đọc mã truy cập từ URL"""
    access_code = download_content(url)
    if access_code:
        # Làm sạch mã (loại bỏ khoảng trắng, dòng mới)
        return access_code.strip()
    return None

def verify_access_code(correct_code):
    """Hiển thị hộp thoại yêu cầu mã truy cập và xác thực với giao diện tùy chỉnh"""
    # Tạo cửa sổ đăng nhập tùy chỉnh
    login_window = tk.Tk()
    login_window.title("Xác thực")
    login_window.geometry("400x200")  # Tăng kích thước cửa sổ
    login_window.resizable(False, False)
    login_window.configure(bg="#f0f0f0")
    
    # Center the window
    login_window.update_idletasks()
    width = login_window.winfo_width()
    height = login_window.winfo_height()
    x = (login_window.winfo_screenwidth() // 2) - (width // 2)
    y = (login_window.winfo_screenheight() // 2) - (height // 2)
    login_window.geometry(f'{width}x{height}+{x}+{y}')
    
    # Biến để kiểm soát số lần thử
    attempts = [0]  # Sử dụng list để có thể thay đổi giá trị trong hàm con
    max_attempts = 3
    
    # Biến kết quả
    result = [False]  # Sử dụng list để có thể thay đổi giá trị trong hàm con
    
    # Tạo label hướng dẫn
    label = tk.Label(
        login_window, 
        text=f"Nhập mã truy cập để tiếp tục.\nBạn còn {max_attempts} lần thử:",
        font=("Arial", 12),
        bg="#f0f0f0",
        pady=10
    )
    label.pack(pady=10)
    
    # Tạo frame chứa entry
    entry_frame = tk.Frame(login_window, bg="#f0f0f0")
    entry_frame.pack(pady=5, fill="x", padx=30)
    
    # Tạo biến chuỗi để lưu password thực
    password_var = tk.StringVar()
    
    # Tạo custom Entry tự xử lý việc hiển thị dấu sao
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
    
    # Tạo entry tùy chỉnh
    entry = PasswordEntry(
        entry_frame,
        font=("Arial", 12),
        width=30,
        justify="center"
    )
    entry.pack(fill="x", ipady=5)
    entry.focus()
    
    # Hàm xử lý khi nhập ký tự
    def on_key_event(event):
        # Nếu là phím xóa (Backspace)
        if event.keysym == 'BackSpace':
            entry.remove_char()
        # Nếu là Enter
        elif event.keysym == 'Return':
            check_password()
        # Nếu là ký tự thông thường
        elif len(event.char) == 1 and event.char.isprintable():
            entry.add_char(event.char)
        # Ngăn chặn sự kiện mặc định để không hiển thị ký tự thực
        return "break"
    
    # Gán sự kiện nhấn phím cho entry
    entry.bind("<Key>", on_key_event)
    
    # Frame chứa các nút
    button_frame = tk.Frame(login_window, bg="#f0f0f0")
    button_frame.pack(pady=20)
    
    # Hàm kiểm tra mật khẩu
    def check_password():
        entered_password = entry.get_password()
        attempts[0] += 1
        remaining = max_attempts - attempts[0]
        
        if entered_password.strip() == correct_code:
            result[0] = True
            messagebox.showinfo("Thành công", "Mã truy cập chính xác!")
            login_window.destroy()
        else:
            if remaining > 0:
                messagebox.showerror("Lỗi", f"Mã truy cập không đúng. Còn {remaining} lần thử.")
                label.config(text=f"Nhập mã truy cập để tiếp tục.\nBạn còn {remaining} lần thử:")
                # Xóa mật khẩu cũ
                entry.password = ""
                entry.delete(0, tk.END)
                entry.focus()
            else:
                messagebox.showerror("Lỗi", "Quá nhiều lần thử sai. Chương trình sẽ thoát.")
                login_window.destroy()
    
    # Nút OK
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
    
    # Nút Cancel
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
    
    # Trả về kết quả xác thực
    return result[0]

def check_required_modules():
    """Kiểm tra và cài đặt các module cần thiết nếu cần"""
    required_modules = ['requests', 'tkinter']
    
    for module in required_modules:
        try:
            if module == 'tkinter':
                # Thử import tkinter
                __import__(module)
            else:
                # Kiểm tra xem module đã được cài đặt chưa
                subprocess.run([sys.executable, '-c', f'import {module}'], 
                              check=True, capture_output=True)
            print(f"✓ Module {module} đã được cài đặt")
        except (ImportError, subprocess.CalledProcessError):
            print(f"Module {module} chưa được cài đặt. Đang cài đặt...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', module], 
                              check=True)
                print(f"✓ Module {module} đã cài đặt thành công")
            except subprocess.CalledProcessError as e:
                print(f"Lỗi khi cài đặt {module}: {e}")
                return False
    return True

def run_script(script_path):
    """Chạy script Python với quyền admin trên Windows"""
    try:
        if sys.platform == 'win32':
            # Trên Windows, thử chạy với quyền admin
            print("Đang yêu cầu quyền quản trị viên...")
            try:
                import ctypes
                if not ctypes.windll.shell32.IsUserAnAdmin():
                    print("Script cần quyền quản trị viên. Đang yêu cầu...")
                    # Nếu không phải admin, chạy lại với quyền admin
                    ctypes.windll.shell32.ShellExecuteW(
                        None, "runas", sys.executable, f'"{script_path}"', None, 1)
                    # Đợi một chút để có thời gian khởi động
                    time.sleep(2)
                    return True
                else:
                    # Đã là admin, chạy bình thường
                    subprocess.run([sys.executable, script_path], check=True)
                    return True
            except Exception as e:
                print(f"Lỗi khi yêu cầu quyền admin: {e}")
                # Thử chạy bình thường nếu có lỗi
                try:
                    subprocess.run([sys.executable, script_path], check=True)
                    return True
                except Exception as sub_e:
                    print(f"Lỗi khi chạy script: {sub_e}")
                    return False
        else:
            # Trên các nền tảng khác
            print("Đang chạy script...")
            subprocess.run([sys.executable, script_path], check=True)
            return True
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi chạy script: {e}")
        return False
    except Exception as e:
        print(f"Lỗi không xác định: {e}")
        return False

def main():
    """Hàm chính để xác thực, tải về và chạy SVS Tools script"""
    print("SVS Tools Launcher - Phiên bản bảo mật")
    print("=" * 50)
    
    # Đăng ký hàm dọn dẹp để chạy khi thoát chương trình
    atexit.register(cleanup)
    
    # Kiểm tra các module cần thiết
    if not check_required_modules():
        print("Không thể cài đặt các module cần thiết. Đang thoát.")
        return
    
    # URL cho mã truy cập và script
    access_code_url = "https://github.com/alfienguyenn/SVS/blob/main/AccessCode.txt"
    script_url = "https://github.com/alfienguyenn/SVS/blob/main/SVS_Tools.py"
    
    # Tải mã truy cập trước
    print("Đang tải mã truy cập...")
    access_code = get_access_code(access_code_url)
    
    if not access_code:
        print("Không thể tải mã truy cập. Đang thoát.")
        return
    
    # Yêu cầu người dùng nhập mã truy cập
    if not verify_access_code(access_code):
        print("Xác thực thất bại. Đang thoát.")
        return
        
    # Sau khi xác thực thành công, tải script
    print("Xác thực thành công! Đang tải script...")
    script_content = download_content(script_url)
    
    if not script_content:
        print("Không thể tải script. Đang thoát.")
        return
    
    # Tạo thư mục tạm để lưu script
    temp_dir = tempfile.gettempdir()
    script_path = os.path.join(temp_dir, f"SVS_Tools_{int(time.time())}.py")
    
    # Lưu script vào file tạm
    if save_to_file(script_content, script_path):
        print(f"Script đã được lưu vào {script_path}")
        
        # Chạy script
        print("Đang chạy SVS Tools...")
        if run_script(script_path):
            print("SVS Tools đã chạy thành công!")
        else:
            print("Có lỗi xảy ra khi chạy SVS Tools.")
    else:
        print("Không thể lưu script. Đang thoát.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nChương trình bị dừng bởi người dùng.")
    except Exception as e:
        print(f"\nLỗi không mong muốn: {e}")
    finally:
        # Đảm bảo dọn dẹp được gọi ngay cả khi có lỗi
        cleanup()
