import tkinter as tk
from tkinter import ttk
from tkinter import messagebox # Import messagebox để hiện thông báo
import sqlite3
import customtkinter as ctk
from datetime import datetime
from views.config import db_path

cong_no_data = [
    (1, 'Nguyễn Thành Công', 5000000, 2000000, '25/10/2023'),
    (2, 'Nguyễn Ngọc Hưng', 0, 0, '20/10/2023'),
    (3, 'Trần Đức Duy', 1250000, 1250000, '22/10/2023'),
    (4, 'Công ty Xây dựng ABC', 15000000, 7000000, '26/10/2023'),
]

class CongNoView(tk.Frame):
    def __init__(self, parent, root_window):
        super().__init__(parent, bg="white")
        
        self.root_window = root_window # Lưu lại cửa sổ gốc để dùng cho Toplevel
        
        # Gọi phương thức để tạo tất cả các widget
        self.create_widgets()
        self.load_cong_no_data()

    # Phương thức để tạo các widget trong frame 
    def create_widgets(self):
        # --- Cấu hình layout chính: 2 cột ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3) # Cột trái (danh sách) chiếm nhiều không gian hơn
        self.grid_columnconfigure(1, weight=2) # Cột phải (cập nhật)

        # --- 1. Frame bên trái: Danh sách công nợ ---
        left_frame = tk.Frame(self, bg="white", padx=10, pady=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_rowconfigure(2, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # -- Thanh tìm kiếm --
        search_frame = tk.Frame(left_frame, bg="white")
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 11))
        # Placeholder text
        self.placeholder = "Tìm kiếm khách hàng..."
        search_entry.insert(0, self.placeholder)
        search_entry.bind("<FocusIn>", self.on_search_focus_in)
        search_entry.bind("<FocusOut>", self.on_search_focus_out)
        search_entry.bind("<KeyRelease>", self.filter_data)
        search_entry.grid(row=0, column=0, sticky="ew", ipady=4)

        # -- Label danh sách --
        tk.Label(left_frame, text="Danh sách công nợ", font=("Segoe UI", 14, "bold"), bg="white").grid(row=1, column=0, sticky="w", pady=(5, 5))

        # -- Bảng danh sách công nợ --
        tree_container = tk.Frame(left_frame)
        tree_container.grid(row=2, column=0, sticky="nsew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        cols = ("ten_kh", "no_cu", "da_thanh_toan", "tong_no", "ngay_cap_nhat")
        self.tree_cn = ttk.Treeview(tree_container, columns=cols, show="headings", selectmode="browse")
        self.tree_cn.heading("ten_kh", text="Tên khách hàng")
        self.tree_cn.heading("no_cu", text="Nợ cũ")
        self.tree_cn.heading("da_thanh_toan", text="Đã thanh toán")
        self.tree_cn.heading("tong_no", text="Tổng nợ")
        self.tree_cn.heading("ngay_cap_nhat", text="Ngày cập nhật")

        # Định dạng cột
        for col in cols:
            if col != "ten_kh":
                self.tree_cn.column(col, width=120, anchor="e") # Căn phải cho các cột số
        
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree_cn.yview)
        self.tree_cn.configure(yscrollcommand=scrollbar.set)
        self.tree_cn.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.tree_cn.bind("<<TreeviewSelect>>", self.on_cong_no_select)
        
        # --- 2. Frame bên phải: Thông tin cập nhật ---
        right_frame = tk.Frame(self, bg="#f7f9fc", padx=20, pady=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(right_frame, text="Thông tin cập nhật", font=("Segoe UI", 14, "bold"), bg="#f7f9fc").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # -- Các trường thông tin --
        self.update_fields_vars = {
            "Tên khách hàng:": tk.StringVar(),
            "Công nợ hiện tại:": tk.StringVar(),
            "Đã thanh toán:": tk.StringVar(),
            "Cập nhật lần cuối:": tk.StringVar()
        }
        
        # Tên khách hàng (chỉ đọc)
        tk.Label(right_frame, text="Tên khách hàng:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(right_frame, textvariable=self.update_fields_vars["Tên khách hàng:"], state="readonly", font=("Segoe UI", 10)).grid(row=1, column=1, sticky="ew", pady=5)
        
        # Công nợ hiện tại (chỉ đọc, được tính toán)
        tk.Label(right_frame, text="Công nợ hiện tại:", font=("Segoe UI", 10, "bold"), bg="#f7f9fc").grid(row=2, column=0, sticky="w", pady=5)
        tk.Label(right_frame, textvariable=self.update_fields_vars["Công nợ hiện tại:"], font=("Segoe UI", 11, "bold"), bg="#f7f9fc").grid(row=2, column=1, sticky="w", pady=5)
        
        # Nhập số tiền đã thanh toán (đây là ô người dùng nhập)
        tk.Label(right_frame, text="Đã thanh toán:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=3, column=0, sticky="w", pady=5)
        self.thanh_toan_entry = tk.Entry(right_frame, textvariable=self.update_fields_vars["Đã thanh toán:"], font=("Segoe UI", 10))
        self.thanh_toan_entry.grid(row=3, column=1, sticky="ew", pady=5)

        # Cập nhật lần cuối (chỉ đọc)
        tk.Label(right_frame, text="Cập nhật lần cuối:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=4, column=0, sticky="w", pady=5)
        tk.Entry(right_frame, textvariable=self.update_fields_vars["Cập nhật lần cuối:"], state="readonly", font=("Segoe UI", 10)).grid(row=4, column=1, sticky="ew", pady=5)

        # -- Frame nút bấm --
        # Tạo một frame cho các button
        button_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        button_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=20)

        # Button "Cập nhật" với bo góc
        ctk.CTkButton(
            button_frame,
            text="Cập nhật",
            command=self.update_cong_no,
            font=("Segoe UI", 11, "bold"),
            fg_color="#3DB581",
            corner_radius=10,  # Thêm bo góc
            height=30,         # Chiều cao nút
            width=100          # Chiều rộng nút
        ).pack(side="left", padx=5)

        # Button "Chuyển tiếp" với bo góc
        ctk.CTkButton(
            button_frame,
            text="Chuyển tiếp",
            font=("Segoe UI", 11),
            fg_color="#ecf0f1",
            text_color="black", # Đổi màu chữ để dễ nhìn
            corner_radius=10,  # Thêm bo góc
            height=30,
            width=100
        ).pack(side="left", padx=5)

    # --- Các phương thức xử lý sự kiện ---
    
    def on_search_focus_in(self, event):
        if self.search_var.get() == self.placeholder:
            event.widget.delete(0, "end")
            event.widget.config(fg='black')

    def on_search_focus_out(self, event):
        if not self.search_var.get():
            event.widget.config(fg='grey')
            event.widget.insert(0, self.placeholder)

    def filter_data(self, event=None):
        """Lọc dữ liệu trong Treeview dựa trên nội dung ô tìm kiếm."""
        search_term = self.search_var.get().lower()
        
        # Xóa hết các dòng hiện tại
        for i in self.tree_cn.get_children():
            self.tree_cn.delete(i)
            
        # Nạp lại dữ liệu phù hợp
        for item in cong_no_data:
            if search_term == self.placeholder.lower() or search_term in item[1].lower():
                self.insert_cong_no_item(item)
    
    def load_cong_no_data(self):
        """Tải toàn bộ dữ liệu công nợ vào Treeview."""
        for i in self.tree_cn.get_children():
            self.tree_cn.delete(i)
            
        for item in cong_no_data:
            self.insert_cong_no_item(item)
            
        # Tự động chọn dòng đầu tiên
        children = self.tree_cn.get_children()
        if children:
            self.tree_cn.selection_set(children[0])
            self.tree_cn.focus(children[0])
            
    def insert_cong_no_item(self, item_data):
        """Hàm trợ giúp để chèn một dòng vào Treeview Công nợ."""
        kh_id, ten_kh, no_cu, da_thanh_toan, ngay_cap_nhat = item_data
        tong_no = no_cu - da_thanh_toan
        
        # Định dạng số cho đẹp
        no_cu_f = f"{no_cu:,}".replace(",", ".")
        da_thanh_toan_f = f"{da_thanh_toan:,}".replace(",", ".")
        tong_no_f = f"{tong_no:,}".replace(",", ".")
        
        self.tree_cn.insert("", "end", values=(ten_kh, no_cu_f, da_thanh_toan_f, tong_no_f, ngay_cap_nhat), iid=kh_id)
        
    def on_cong_no_select(self, event):
        """Hiển thị thông tin chi tiết khi một dòng được chọn."""
        selected_items = self.tree_cn.selection()
        if not selected_items:
            return
            
        kh_id = int(selected_items[0])
        
        # Tìm dữ liệu trong danh sách gốc
        # (Trong ứng dụng thực tế, bạn sẽ query DB với kh_id)
        item_data = next((item for item in cong_no_data if item[0] == kh_id), None)
        
        if item_data:
            _, ten_kh, no_cu, da_thanh_toan, ngay_cap_nhat = item_data
            tong_no = no_cu - da_thanh_toan
            
            # Cập nhật các ô thông tin
            self.update_fields_vars["Tên khách hàng:"].set(ten_kh)
            self.update_fields_vars["Công nợ hiện tại:"].set(f"{tong_no:,}".replace(",", "."))
            self.update_fields_vars["Đã thanh toán:"].set(f"{da_thanh_toan:,}".replace(",", "."))
            self.update_fields_vars["Cập nhật lần cuối:"].set(ngay_cap_nhat)
            
    def update_cong_no(self):
        """Lưu lại thông tin công nợ đã cập nhật."""
        selected_items = self.tree_cn.selection()
        if not selected_items:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một khách hàng để cập nhật.")
            return
            
        kh_id = int(selected_items[0])
        
        try:
            # Lấy số tiền thanh toán mới từ ô Entry
            thanh_toan_moi_str = self.update_fields_vars["Đã thanh toán:"].get().replace(".", "")
            thanh_toan_moi = int(thanh_toan_moi_str) if thanh_toan_moi_str else 0
        except ValueError:
            messagebox.showerror("Lỗi", "Số tiền thanh toán không hợp lệ.")
            return

        # ---- Tại đây, bạn sẽ thực hiện logic UPDATE database ----
        # 1. Tìm bản ghi công nợ của khách hàng có id là kh_id.
        # 2. Cập nhật cột da_thanh_toan = thanh_toan_moi.
        # 3. Cập nhật cột ngay_cap_nhat = ngày hiện tại.
        # Ví dụ:
        print(f"--- Sẵn sàng UPDATE vào DB ---")
        print(f"ID Khách hàng: {kh_id}")
        print(f"Số tiền đã thanh toán mới: {thanh_toan_moi}")
        print(f"Ngày cập nhật: {datetime.now().strftime('%d/%m/%Y')}")
        print("---------------------------")
        # --------------------------------------------------------

        # Sau khi update DB thành công, làm mới lại giao diện
        messagebox.showinfo("Thành công", "Đã cập nhật công nợ thành công!")
        # (Trong ứng dụng thực tế, bạn sẽ tải lại dữ liệu từ DB)
        # Tạm thời cập nhật dữ liệu giả lập để demo:
        for i, item in enumerate(cong_no_data):
            if item[0] == kh_id:
                cong_no_data[i] = (item[0], item[1], item[2], thanh_toan_moi, datetime.now().strftime('%d/%m/%Y'))
                break
        self.load_cong_no_data() # Tải lại toàn bộ bảng