import os
import sys
import tkinter as tk
from tkinter import messagebox
import tempfile
import time
import shutil
import atexit
import traceback

# URL của file GitHub
GITHUB_URL = "https://raw.githubusercontent.com/alfienguyenn/SVS/main/SVS_Utility_Tool.py"

# File khóa để đảm bảo chỉ chạy một instance
LOCK_FILE = os.path.join(tempfile.gettempdir(), "svs_utility_launcher.lock")

# Danh sách các file tạm cần xóa khi kết thúc
TEMP_FILES = []
TEMP_DIRS = []

def is_already_running():
    """Kiểm tra xem chương trình đã đang chạy chưa"""
    try:
        # Nếu file khóa tồn tại và chứa nội dung
        if os.path.exists(LOCK_FILE):
            # Kiểm tra xem tiến trình đó còn sống không
            with open(LOCK_FILE, 'r') as f:
                pid = f.read().strip()
                if pid and pid.isdigit():
                    # Kiểm tra PID theo cách phù hợp với hệ điều hành
                    try:
                        if sys.platform == "win32":
                            # Windows
                            import ctypes
                            kernel32 = ctypes.windll.kernel32
                            handle = kernel32.OpenProcess(1, 0, int(pid))
                            if handle:
                                kernel32.CloseHandle(handle)
                                return True
                        else:
                            # Unix/Linux/Mac
                            os.kill(int(pid), 0)  # Không gửi tín hiệu, chỉ kiểm tra
                            return True
                    except (OSError, ImportError):
                        # PID không tồn tại hoặc không thể import
                        pass
        return False
    except:
        return False

def create_lock_file():
    """Tạo file khóa để đánh dấu chương trình đang chạy"""
    try:
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))
        # Thêm file khóa vào danh sách để xóa khi kết thúc
        TEMP_FILES.append(LOCK_FILE)
    except:
        pass

def show_message(message, title="Thông báo", error=False):
    """Hiển thị thông báo"""
    root = tk.Tk()
    root.withdraw()
    if error:
        messagebox.showerror(title, message)
    else:
        messagebox.showinfo(title, message)
    root.destroy()

def create_temp_dir():
    """Tạo thư mục tạm thời và đảm bảo nó được xóa khi kết thúc"""
    temp_dir = tempfile.mkdtemp(prefix="svs_utility_")
    TEMP_DIRS.append(temp_dir)
    return temp_dir

def download_from_github(url):
    """Tải mã nguồn mới nhất từ GitHub"""
    try:
        # Tạo một thư mục tạm thời
        temp_dir = create_temp_dir()
        temp_file = os.path.join(temp_dir, "latest_utility.py")
        
        # Tạo cửa sổ loading
        root = tk.Tk()
        root.title("Đang tải...")
        root.geometry("300x80")
        root.resizable(False, False)
        
        label = tk.Label(root, text="Đang tải phiên bản mới nhất từ GitHub...", font=("Arial", 10))
        label.pack(pady=10)
        
        progress = tk.Label(root, text="Vui lòng chờ...", font=("Arial", 8))
        progress.pack(pady=5)
        
        root.update()
        
        # Tải file từ GitHub
        import requests
        response = requests.get(url, timeout=10)
        
        # Kiểm tra trạng thái phản hồi
        if response.status_code != 200:
            root.destroy()
            return None
        
        # Lưu nội dung vào file
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Thêm vào danh sách file tạm
        TEMP_FILES.append(temp_file)
        
        # Cập nhật thông báo và đóng cửa sổ
        progress.config(text="Đã tải xong!")
        root.after(1000, root.destroy)
        root.mainloop()
        
        return temp_file
    
    except Exception as e:
        print(f"Lỗi khi tải từ GitHub: {str(e)}")
        try:
            if 'root' in locals() and root:
                root.destroy()
        except:
            pass
        return None

def find_embedded_utility():
    """Tìm file công cụ được nhúng trong file .exe"""
    if getattr(sys, 'frozen', False):
        # Nếu đang chạy từ .exe, tìm trong resource
        embedded_path = os.path.join(getattr(sys, '_MEIPASS', ''), "calculator.py")
        if os.path.exists(embedded_path):
            # Sao chép vào thư mục tạm để có thể sửa đổi
            temp_dir = create_temp_dir()
            temp_file = os.path.join(temp_dir, "embedded_utility.py")
            
            # Sao chép file
            with open(embedded_path, 'r', encoding='utf-8') as src:
                with open(temp_file, 'w', encoding='utf-8') as dest:
                    dest.write(src.read())
            
            # Thêm vào danh sách file tạm
            TEMP_FILES.append(temp_file)
            return temp_file
    
    return None

def find_local_utility():
    """Tìm file công cụ trong thư mục cục bộ"""
    # Tìm trong cùng thư mục với file launcher
    launcher_dir = os.path.dirname(os.path.abspath(__file__))
    local_path = os.path.join(launcher_dir, "SVS_Utility_Tool.py")
    if os.path.exists(local_path):
        # Sao chép vào thư mục tạm để có thể sửa đổi
        temp_dir = create_temp_dir()
        temp_file = os.path.join(temp_dir, "local_utility.py")
        
        # Sao chép file
        with open(local_path, 'r', encoding='utf-8') as src:
            with open(temp_file, 'w', encoding='utf-8') as dest:
                dest.write(src.read())
        
        # Thêm vào danh sách file tạm
        TEMP_FILES.append(temp_file)
        return temp_file
    
    return None

def get_utility_code():
    """Lấy mã nguồn công cụ theo thứ tự ưu tiên:
    1. Tải từ GitHub (phiên bản mới nhất)
    2. Tìm bản cục bộ
    3. Tìm bản nhúng trong .exe
    """
    # Thử tải từ GitHub trước
    github_version = download_from_github(GITHUB_URL)
    if github_version:
        print("Sử dụng phiên bản từ GitHub")
        return github_version
    
    # Nếu không tải được, thử tìm bản cục bộ
    local_version = find_local_utility()
    if local_version:
        print("Sử dụng phiên bản cục bộ")
        return local_version
    
    # Nếu không có bản cục bộ, thử dùng bản nhúng
    embedded_version = find_embedded_utility()
    if embedded_version:
        print("Sử dụng phiên bản nhúng trong .exe")
        return embedded_version
    
    return None

def modify_powershell_commands(code):
    """Sửa đổi các lệnh PowerShell để ẩn cửa sổ"""
    # Thêm tùy chọn -WindowStyle Hidden vào lệnh PowerShell
    modified_code = code.replace(
        "subprocess.run(['powershell", 
        "subprocess.run(['powershell', '-WindowStyle', 'Hidden'"
    )
    modified_code = modified_code.replace(
        "subprocess.Popen(['powershell", 
        "subprocess.Popen(['powershell', '-WindowStyle', 'Hidden'"
    )
    
    return modified_code

def clean_up_resources():
    """Dọn dẹp tất cả tài nguyên tạm thời"""
    print("Đang dọn dẹp tài nguyên tạm thời...")
    
    # Xóa các file tạm
    for file_path in TEMP_FILES:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Đã xóa file: {file_path}")
        except Exception as e:
            print(f"Không thể xóa file {file_path}: {str(e)}")
    
    # Xóa các thư mục tạm
    for dir_path in TEMP_DIRS:
        try:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path, ignore_errors=True)
                print(f"Đã xóa thư mục: {dir_path}")
        except Exception as e:
            print(f"Không thể xóa thư mục {dir_path}: {str(e)}")
    
    # Xóa các file trong thư mục %TEMP% bắt đầu bằng "tmp" (do Python tạo ra)
    temp_dir = tempfile.gettempdir()
    try:
        for item in os.listdir(temp_dir):
            if item.startswith("tmp") and item.endswith(".py"):
                item_path = os.path.join(temp_dir, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        print(f"Đã xóa file tạm Python: {item_path}")
                except:
                    pass
    except:
        pass
    
    print("Đã hoàn tất dọn dẹp tài nguyên")

def run_utility_directly():
    """Chạy công cụ trực tiếp từ mã nguồn"""
    try:
        # Lấy mã nguồn công cụ mới nhất
        tool_path = get_utility_code()
        
        if not tool_path:
            show_message(
                "Không thể lấy mã nguồn công cụ. Vui lòng kiểm tra kết nối mạng hoặc đảm bảo file SVS_Utility_Tool.py nằm trong cùng thư mục.", 
                "Lỗi", 
                True
            )
            return False
        
        # Đọc mã nguồn từ file
        with open(tool_path, 'r', encoding='utf-8') as f:
            tool_code = f.read()
        
        # Sửa đổi mã nguồn để ẩn cửa sổ PowerShell
        modified_code = modify_powershell_commands(tool_code)
        
        # Thêm biến môi trường để ẩn cửa sổ PowerShell
        os.environ['PYTHONUNBUFFERED'] = '1'
        
        # Đăng ký hàm dọn dẹp
        atexit.register(clean_up_resources)
        
        # Thực thi mã nguồn đã sửa đổi
        exec(modified_code, globals())
        return True
        
    except Exception as e:
        error_msg = f"Lỗi khi chạy công cụ: {str(e)}\n{traceback.format_exc()}"
        show_message(error_msg, "Lỗi khởi chạy", True)
        return False

def main():
    """Hàm chính của launcher"""
    try:
        # Kiểm tra xem đã có instance đang chạy chưa
        if is_already_running():
            show_message("SVS Utility Tool đã đang chạy.", "Thông báo")
            sys.exit(0)
        
        # Tạo file khóa
        create_lock_file()
        
        # Chạy công cụ trực tiếp từ mã nguồn
        run_utility_directly()
        
        # Dọn dẹp tài nguyên
        clean_up_resources()
        
    except Exception as e:
        error_msg = f"Lỗi không xác định: {str(e)}\n{traceback.format_exc()}"
        show_message(error_msg, "Lỗi", True)
        
        # Dọn dẹp tài nguyên ngay cả khi có lỗi
        clean_up_resources()
        
        sys.exit(1)

if __name__ == "__main__":
    main()
