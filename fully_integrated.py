import os
import sys
import tkinter as tk
from tkinter import messagebox
import tempfile
import time

# File khóa để đảm bảo chỉ chạy một instance
LOCK_FILE = os.path.join(tempfile.gettempdir(), "svs_utility_launcher.lock")

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

def clean_up():
    """Xử lý khi ứng dụng thoát"""
    # Xóa file khóa khi thoát
    try:
        os.remove(LOCK_FILE)
    except:
        pass

def find_utility_tool():
    """Tìm file công cụ SVS_Utility_Tool.py"""
    # Thứ tự tìm kiếm:
    # 1. Trong resource đã nhúng khi đóng gói thành .exe
    # 2. Trong cùng thư mục với file launcher
    # 3. Trong thư mục hiện tại
    
    # Kiểm tra xem đang chạy từ file .exe không
    if getattr(sys, 'frozen', False):
        # Nếu đang chạy từ .exe, tìm trong resource
        embedded_path = os.path.join(getattr(sys, '_MEIPASS', ''), "calculator.py")
        if os.path.exists(embedded_path):
            return embedded_path
    
    # Tìm trong cùng thư mục với file launcher
    launcher_dir = os.path.dirname(os.path.abspath(__file__))
    local_path = os.path.join(launcher_dir, "SVS_Utility_Tool.py")
    if os.path.exists(local_path):
        return local_path
    
    # Tìm trong thư mục hiện tại
    current_path = os.path.join(os.getcwd(), "SVS_Utility_Tool.py")
    if os.path.exists(current_path):
        return current_path
    
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
    
    # Đối với Windows, thêm cờ CREATE_NO_WINDOW vào các lệnh subprocess
    if sys.platform == 'win32':
        # Định nghĩa hằng số
        CREATE_NO_WINDOW = 0x08000000
        
        # Tìm và thay thế các lệnh subprocess.Popen
        modified_code = modified_code.replace(
            "subprocess.Popen(", 
            "subprocess.Popen("
        )
        
        # Tìm và thay thế các lệnh subprocess.run
        modified_code = modified_code.replace(
            "subprocess.run(", 
            "subprocess.run("
        )
    
    return modified_code

def run_utility_directly():
    """Chạy công cụ trực tiếp từ mã nguồn"""
    try:
        # Tìm file công cụ
        tool_path = find_utility_tool()
        
        if not tool_path:
            show_message(
                "Không tìm thấy file SVS_Utility_Tool.py. Vui lòng đảm bảo file này nằm trong cùng thư mục.", 
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
        
        # Thực thi mã nguồn đã sửa đổi
        exec(modified_code, globals())
        return True
        
    except Exception as e:
        error_msg = f"Lỗi khi chạy công cụ: {str(e)}"
        show_message(error_msg, "Lỗi khởi chạy", True)
        return False

def main():
    """Hàm chính của launcher"""
    # Đăng ký hàm dọn dẹp khi thoát
    import atexit
    atexit.register(clean_up)
    
    try:
    
        
        # Tạo file khóa
        create_lock_file()
        
        # Chạy công cụ trực tiếp từ mã nguồn
        run_utility_directly()
        
    except Exception as e:
        error_msg = f"Lỗi không xác định: {str(e)}"
        show_message(error_msg, "Lỗi", True)
        sys.exit(1)

if __name__ == "__main__":
    main()
