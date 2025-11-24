import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys
import shutil
import win32api
import win32gui
import win32con

# Import Controller
from controllers.products_controller import ProductController
from controllers.yard_controller import YardController
from controllers.customer_controller import CustomerController
from controllers.debt_controller import DebtController
from controllers.invoice_controller import InvoiceController
from controllers.invoiceHistorys_controller import InvoiceHistoryController
from controllers.setting_controller import SettingController


# Import class view từ file đã tách
from views.products_view import MatHangView
from views.khach_hang import KhachHangView
from views.invoice_view import TaoHoaDonView
from views.invoiceHistorys_view import LsHoaDonView
from views.bai import YardVehicleManagementView
from views.debt_view import CongNoView
from views.setting_view import CaiDatView

def resource_path(relative_path):
    """ Lấy đường dẫn tuyệt đối đến tài nguyên, hoạt động cho cả chế độ dev và PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- HÀM MỚI ĐỂ XỬ LÝ DATABASE BỀN VỮNG ---
def get_persistent_db_path():
    """
    Tạo và trả về đường dẫn đến file database trong thư mục AppData của người dùng.
    Dữ liệu sẽ được lưu trữ bền vững tại đây.
    """
    # Tạo một thư mục riêng cho ứng dụng của bạn trong %APPDATA%
    # Ví dụ: C:\Users\TenNguoiDung\AppData\Roaming\TinhKhangPhucApp
    app_data_dir = os.path.join(os.getenv('APPDATA'), 'TinhKhangPhucApp')
    os.makedirs(app_data_dir, exist_ok=True)
    
    # Đường dẫn đến file database sẽ được sử dụng
    persistent_path = os.path.join(app_data_dir, 'CSP_0708.db')
    return persistent_path

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.geometry("1730x800")
        self.title("Quản Lý Hóa Đơn Công Ty TNHH TM DV Tính Khang Phúc")
        try:
            icon_path = resource_path('icons/logo.ico') 
            self.iconbitmap(icon_path)
            # print(f"Đã tải icon ứng dụng từ: {icon_path}")
        except Exception as e:
            # Không làm crash chương trình nếu không tải được icon
            print(f"Lỗi khi tải icon ứng dụng: {e}")

        # --- THAY ĐỔI LOGIC XỬ LÝ DATABASE TẠI ĐÂY ---
        # 1. Lấy đường dẫn đến file DB bền vững trong AppData
        persistent_db_path = get_persistent_db_path()

        # 2. Kiểm tra xem file DB đã tồn tại ở đó chưa. Nếu chưa (lần chạy đầu tiên),
        #    sao chép file DB "mẫu" từ gói ứng dụng ra đó.
        if not os.path.exists(persistent_db_path):
            print(f"Database chưa tồn tại. Bắt đầu sao chép từ mẫu...")
            try:
                # Lấy đường dẫn đến file DB "mẫu" được đóng gói bên trong .exe
                template_db_path = resource_path("database/CSP_0708.db")
                # Sao chép file DB mẫu ra thư mục AppData
                shutil.copy2(template_db_path, persistent_db_path)
                print(f"Sao chép database thành công tới: {persistent_db_path}")
            except Exception as e:
                messagebox.showerror("Lỗi nghiêm trọng", f"Không thể tạo file database! Dữ liệu sẽ không được lưu.\nLỗi: {e}")
                self.destroy() # Đóng ứng dụng nếu không tạo được db

        # 3. LUÔN LUÔN sử dụng đường dẫn bền vững này cho mọi hoạt động của ứng dụng
        self.db_path = persistent_db_path
        # -----------------------------------------------
    
        self.configure(bg="#f0f0f0")

        self.frames = {} # Dictionary để lưu các frame trang

        self._create_header()
        self._create_content_area()
        self._create_pages()
        
        self.show_tab("Mặt hàng")

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
            "Bãi & Xe": "truck.png",
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
                icon_path = resource_path(f"icons/{icon_file}")
                img = Image.open(icon_path)
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
                # print(f"Lỗi: không tìm thấy file icon 'icons/{icon_file}'")
                # Tạo nút không có icon nếu file không tồn tại
                btn = tk.Button(tab_frame, text=name, command=lambda n=name: self.show_tab(n))
                btn.pack(side="left", padx=5)

        # --- Frame chứa nút setting
        settings_frame = tk.Frame(header, bg="#34495e")
        settings_frame.grid(row=0, column=1, sticky="e", padx=20, pady=10)

        try:
            # Load icon setting
            settings_icon_path = resource_path("icons/setting.png")
            settings_img = Image.open(settings_icon_path)
            settings_img_resized = settings_img.resize((30, 30), Image.LANCZOS)
            self.settings_icon = ImageTk.PhotoImage(settings_img_resized)

            # Nút setting chỉ có icon
            settings_btn = tk.Button(
                settings_frame,
                image=self.settings_icon,
                bg="#34495e",
                relief="flat",
                activebackground="#4a627a",
                command=lambda: self.show_tab("Cài đặt")
            )
            settings_btn.pack()
        except FileNotFoundError:
            # print("Lỗi: không tìm thấy file icon 'icons/setting.png'")
            # Tạo nút text nếu không có icon
            settings_btn = tk.Button(settings_frame, text="Cài đặt", command=lambda: self.show_tab("Cài đặt"))
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
        self.customer_controller = CustomerController(view=khach_hang_page, db_path=self.db_path)
        self.frames["Khách hàng"] = khach_hang_page
 
        tao_hoa_don_page = TaoHoaDonView(self.main_content_frame, self)
        tao_hoa_don_page.grid(row=0, column=0, sticky='nsew')
        self.frames["Tạo hóa đơn"] = tao_hoa_don_page
        self.invoice_controller = InvoiceController(view=tao_hoa_don_page, db_path=self.db_path)
        
        ls_hoa_don_page = LsHoaDonView(self.main_content_frame, self)
        ls_hoa_don_page.grid(row=0, column=0, sticky='nsew')
        self.frames["Lịch sử hóa đơn"] = ls_hoa_don_page
        self.invoice_history_controller = InvoiceHistoryController(view=ls_hoa_don_page, db_path=self.db_path)

        # Trang "Bãi"
        yard_page = YardVehicleManagementView(self.main_content_frame, self)
        yard_page.grid(row=0, column=0, sticky="nsew")
        self.yard_controller = YardController(view=yard_page, db_path=self.db_path)
        self.frames["Bãi & Xe"] = yard_page
        
        # Trang "Công nợ"
        cong_no_page = CongNoView(self.main_content_frame, self)
        cong_no_page.grid(row=0, column=0, sticky="nsew")
        self.frames["Công nợ"] = cong_no_page
        self.debt_controller = DebtController(view=cong_no_page, db_path=self.db_path)

        # Trang " Cài đặt "
        cai_dat_page = CaiDatView(self.main_content_frame, self)
        cai_dat_page.grid(row=0, column=0, sticky="nsew")   
        self.frames["Cài đặt"] = cai_dat_page
        self.setting_controller = SettingController(view=cai_dat_page, db_path=self.db_path)

    def show_tab(self, tab_name):
        frame_to_show = self.frames[tab_name]
        frame_to_show.tkraise()

    def refresh_product_page_data(self):
        """Yêu cầu ProductController tải lại dữ liệu (sản phẩm và bãi)."""
        if hasattr(self, 'products_controller'):
            self.products_controller.refresh_data()

    def refresh_invoice_creation_data(self):
        """Yêu cầu InvoiceController tải lại dữ liệu (sản phẩm, khách hàng, xe)."""
        if hasattr(self, 'invoice_controller'):
            self.invoice_controller.refresh_data()

    def refresh_debt_data(self):
        """Yêu cầu DebtController tải lại dữ liệu công nợ."""
        if self.debt_controller:
            self.debt_controller.load_debts()

    def refresh_invoice_history(self):
        """Yêu cầu LsHoaDonView tải lại dữ liệu lịch sử hóa đơn."""
        history_view = self.frames.get("Lịch sử hóa đơn")
        if history_view:
            history_view.refresh_data()
        # --- Chạy ứng dụng ---
if __name__ == "__main__":
    app = App()
    app.mainloop()