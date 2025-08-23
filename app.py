import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk

# Import Controller
from controllers.products_controller import ProductController
from controllers.debt_controller import DebtController

# Import Model
from models.base_model import BaseModel
from models.products_model import ProductModel

# Import class view từ file đã tách
from views.products_view import MatHangView
from views.khach_hang import KhachHangView
from views.hoa_don import TaoHoaDonView
from views.lich_su_hoa_don import LsHoaDonView
from views.bai import YardView
from views.debt_view import CongNoView

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.geometry("1100x700")
        self.title("Quản lý hóa đơn")

        # Kết nối với cơ sở dữ liệu
        self.db_path = "database/CSP_0708.db"
    
        self.configure(bg="#f0f0f0")

        self.frames = {} # Dictionary để lưu các frame trang

        self._create_header()
        self._create_content_area()
        self._create_pages()
        
        self.show_tab("Mặt hàng") # Hiển thị tab mặc định

    def _create_header(self):
        # Frame header chính, không thay đổi
        header = tk.Frame(self, bg="#34495e", height=60) # Có thể đặt chiều cao cố định
        header.pack(side="top", fill="x")
        # Ngăn header co lại
        header.pack_propagate(False) 

        # --- Frame chứa các nút tab, dồn về bên trái ---
        # Thay vì pack(), dùng grid() để kiểm soát layout tốt hơn
        header.grid_columnconfigure(0, weight=1) # Cho phép cột 0 (chứa tab) co giãn
        header.grid_columnconfigure(1, weight=0) # Cột 1 (chứa setting) không co giãn

        tab_frame = tk.Frame(header, bg="#34495e")
        # Đặt tab_frame vào cột 0, căn lề trái
        tab_frame.grid(row=0, column=0, sticky="w", padx=20, pady=10)

        # --- Dictionary chứa thông tin tab và icon tương ứng ---
        # Key là tên tab, value là tên file icon
        tab_info = {
            "Mặt hàng": "box.png",
            "Bãi": "truck.png",
            "Khách hàng": "customer.png",
            "Tạo hóa đơn": "invoice.png",
            "Lịch sử hóa đơn": "history.png",
            "Công nợ": "loan.png",
        }

        # Lưu trữ các đối tượng PhotoImage để tránh bị "garbage collected" (lỗi không hiện ảnh)
        self.tab_icons = {}

        for name, icon_file in tab_info.items():
            try:
                # Mở file ảnh và thay đổi kích thước
                img = Image.open(f"icons/{icon_file}")
                img_resized = img.resize((24, 24), Image.LANCZOS)
                self.tab_icons[name] = ImageTk.PhotoImage(img_resized)

                # --- Tạo nút với cả text và icon ---
                btn = tk.Button(
                    tab_frame, 
                    text=f" {name}",  # Thêm khoảng trắng để text không dính vào icon
                    image=self.tab_icons[name], # Gán icon
                    compound="left", # Đặt icon ở bên trái text
                    bg="white",
                    fg="#34495e",
                    font=("Segoe UI", 11, "bold"),
                    relief="solid",
                    bd=2,
                    highlightbackground="#34495e",
                    activebackground="#e0e0e0",
                    activeforeground="#34495e",
                    padx=15,
                    pady=5,
                    command=lambda n=name: self.show_tab(n)
                )
                btn.pack(side="left", padx=5)
            except FileNotFoundError:
                print(f"Lỗi: không tìm thấy file icon 'icons/{icon_file}'")
                # Tạo nút không có icon nếu file không tồn tại
                btn = tk.Button(tab_frame, text=name, command=lambda n=name: self.show_tab(n))
                btn.pack(side="left", padx=5)

        # --- Frame chứa nút setting
        settings_frame = tk.Frame(header, bg="#34495e")
        settings_frame.grid(row=0, column=1, sticky="e", padx=20, pady=10)

        try:
            # Load icon setting
            settings_img = Image.open("icons/setting.png")
            settings_img_resized = settings_img.resize((30, 30), Image.LANCZOS)
            self.settings_icon = ImageTk.PhotoImage(settings_img_resized)

            # Nút setting chỉ có icon
            settings_btn = tk.Button(
                settings_frame,
                image=self.settings_icon,
                bg="#34495e",
                relief="flat",
                activebackground="#4a627a",
                # command=self.open_settings # (Hàm mở cửa sổ cài đặt)
            )
            settings_btn.pack()
        except FileNotFoundError:
            print("Lỗi: không tìm thấy file icon 'icons/setting.png'")
            # Tạo nút text nếu không có icon
            settings_btn = tk.Button(settings_frame, text="Cài đặt")
            settings_btn.pack()

    def _create_content_area(self):
        self.main_content_frame = tk.Frame(self, bg="#ffffff")
        self.main_content_frame.pack(expand=True, fill="both", padx=20, pady=20)
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

    def _create_pages(self):
        # --- Tạo trang "Mặt hàng" từ class đã import ---
        mat_hang_page = MatHangView(self.main_content_frame, self)
        mat_hang_page.grid(row=0, column=0, sticky="nsew")
        self.frames["Mặt hàng"] = mat_hang_page
        self.products_controller = ProductController(view=mat_hang_page, db_path=self.db_path)

        khach_hang_page = KhachHangView(self.main_content_frame, self)
        khach_hang_page.grid(row=0, column=0, sticky='nsew')
        self.frames["Khách hàng"] = khach_hang_page
 
        tao_hoa_don_page = TaoHoaDonView(self.main_content_frame, self)
        tao_hoa_don_page.grid(row=0, column=0, sticky='nsew')
        self.frames["Tạo hóa đơn"] = tao_hoa_don_page
        
        ls_hoa_don_page = LsHoaDonView(self.main_content_frame, self)
        ls_hoa_don_page.grid(row=0, column=0, sticky='nsew')
        self.frames["Lịch sử hóa đơn"] = ls_hoa_don_page

        # Trang "Bãi"
        yard_page = YardView(self.main_content_frame, self)
        yard_page.grid(row=0, column=0, sticky="nsew")
        self.frames["Bãi"] = yard_page
        
        # Trang "Công nợ"
        cong_no_page = CongNoView(self.main_content_frame, self)
        cong_no_page.grid(row=0, column=0, sticky="nsew")
        self.frames["Công nợ"] = cong_no_page
        self.debt_controller = DebtController(view=cong_no_page, db_path=self.db_path)

    def show_tab(self, tab_name):
        frame_to_show = self.frames[tab_name]
        frame_to_show.tkraise()

        # --- Chạy ứng dụng ---
if __name__ == "__main__":
    app = App()
    app.mainloop()