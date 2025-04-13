import tkinter as tk
from tkinter import messagebox

class SimpleCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Máy Tính Đơn Giản")
        self.root.geometry("300x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        # Biến lưu giá trị hiển thị
        self.current_value = ""
        
        # Tạo khung hiển thị kết quả
        self.display_frame = tk.Frame(root, bg="#f0f0f0")
        self.display_frame.pack(pady=10)
        
        # Tạo ô hiển thị kết quả
        self.display = tk.Entry(self.display_frame, font=("Arial", 24), width=15, 
                                bd=5, justify=tk.RIGHT)
        self.display.pack()
        
        # Tạo khung chứa các nút
        self.buttons_frame = tk.Frame(root, bg="#f0f0f0")
        self.buttons_frame.pack()
        
        # Danh sách các nút
        self.button_list = [
            "7", "8", "9", "/",
            "4", "5", "6", "*",
            "1", "2", "3", "-",
            "0", ".", "=", "+"
        ]
        
        # Tạo nút Clear
        self.clear_button = tk.Button(self.buttons_frame, text="C", font=("Arial", 18),
                                     width=4, height=1, command=self.clear_display)
        self.clear_button.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="we")
        
        # Tạo các nút số và phép tính
        self.create_buttons()
    
    def create_buttons(self):
        row_val = 1
        col_val = 0
        
        for button_text in self.button_list:
            button = tk.Button(self.buttons_frame, text=button_text, font=("Arial", 18),
                              width=4, height=1, command=lambda x=button_text: self.button_click(x))
            button.grid(row=row_val, column=col_val, padx=5, pady=5)
            
            col_val += 1
            if col_val > 3:
                col_val = 0
                row_val += 1
    
    def button_click(self, value):
        if value == "=":
            try:
                # Tính toán kết quả
                result = eval(self.current_value)
                self.current_value = str(result)
                self.display.delete(0, tk.END)
                self.display.insert(0, self.current_value)
            except Exception as e:
                messagebox.showerror("Lỗi", "Biểu thức không hợp lệ")
                self.current_value = ""
                self.display.delete(0, tk.END)
        else:
            # Thêm giá trị vào biến hiện tại
            self.current_value += value
            self.display.delete(0, tk.END)
            self.display.insert(0, self.current_value)
    
    def clear_display(self):
        # Xóa hết giá trị
        self.current_value = ""
        self.display.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleCalculator(root)
    root.mainloop()
