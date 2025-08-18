import tkinter as tk
from tkinter import ttk
from tkinter import messagebox # Import messagebox để hiện thông báo

hoa_don_kh_data = [
    (102, '25/10/2023', 'Nguyễn Thành Công', '123 ABC, Q1, HCM', '0708662504', 3500000, 'Đã thanh toán', 'khach_hang'),
    (101, '24/10/2023', 'Trần Đức Duy', '789 KLM, Q3, HCM', '0708552454', 1280000, 'Chưa thanh toán', 'khach_hang'),
]
hoa_don_cty_data = [
    (201, '23/10/2023', 'Công ty Xây dựng ABC', 'Khu Công nghệ cao, Q9, HCM', '02837338888', 15000000, 'Công nợ', 'cong_ty'),
]

# Chi tiết hóa đơn (id_hoa_don, ngay_dat, ten_mh, so_luong, gia, noi_giao)
chi_tiet_hd_data = {
    102: [
        ('25/10/2023', 'Xà bần', 1, 2800000, 'Công trình A'),
        ('25/10/2023', 'Đá mi sàn', 2, 350000, 'Công trình B'),
    ],
    101: [
        ('24/10/2023', 'Đá bụi', 1, 1200000, 'Nhà riêng'),
        ('24/10/2023', 'Cát san lấp', 1, 80000, 'Nhà riêng'),
    ],
    201: [
        ('23/10/2023', 'Đá bụi', 10, 1200000, 'Dự án Thủ Thiêm'),
        ('23/10/2023', 'Cát san lấp', 50, 80000, 'Dự án Thủ Thiêm'),
    ]
}

class LsHoaDonView(tk.Frame):
    def __init__(self, parent, root_window):
        super().__init__(parent, bg="white")
        
        self.root_window = root_window
        
        # Biến để kiểm tra xem dữ liệu đã được nạp lần đầu chưa
        self._data_loaded_once = False 

        self.create_widgets()
        
        # Khi Frame này được hiển thị (tkraise), hàm self.refresh_on_map sẽ được gọi
        self.bind("<Map>", self.refresh_on_map)

    def refresh_on_map(self, event):
        """
        Hàm được gọi khi Frame này được hiển thị.
        Chỉ nạp lại dữ liệu nếu đây là lần đầu tiên, hoặc nếu bạn muốn nó luôn làm mới.
        """
        # Để tránh việc nạp lại dữ liệu không cần thiết mỗi khi focus lại cửa sổ,
        # chúng ta có thể chỉ nạp dữ liệu ở lần hiển thị đầu tiên.
        # Nếu muốn nó luôn làm mới mỗi khi chuyển tab, hãy bỏ điều kiện if.
        if not self._data_loaded_once:
            print("Tab Lịch sử được hiển thị lần đầu, đang nạp dữ liệu...") # Dòng debug
            self.load_hoa_don_data('khach_hang')
            self._data_loaded_once = True

    def create_widgets(self):
        # --- Cấu hình layout chính: 2 cột (trái-phải) ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=3)

        # --- 1. Frame bên trái: Danh sách hóa đơn ---
        left_frame = tk.Frame(self, bg="white", padx=10, pady=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_rowconfigure(2, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        top_controls_frame = tk.Frame(left_frame, bg="white")
        top_controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_controls_frame.grid_columnconfigure(2, weight=1)

        self.btn_hd_kh = tk.Button(top_controls_frame, text="Hóa đơn khách hàng", font=("Segoe UI", 10, "bold"), relief="flat", padx=10, pady=5,
                                command=lambda: self.load_hoa_don_data('khach_hang'))
        self.btn_hd_kh.grid(row=0, column=0, sticky="w")
        
        self.btn_hd_cty = tk.Button(top_controls_frame, text="Hóa đơn công ty", font=("Segoe UI", 10, "bold"), relief="flat", padx=10, pady=5,
                                    command=lambda: self.load_hoa_don_data('cong_ty'))
        self.btn_hd_cty.grid(row=0, column=1, sticky="w", padx=5)

        search_entry = ttk.Entry(top_controls_frame, font=("Segoe UI", 10))
        search_entry.grid(row=0, column=2, sticky="ew", padx=(20, 0))

        tk.Label(left_frame, text="Danh sách hóa đơn", font=("Segoe UI", 14, "bold"), bg="white").grid(row=1, column=0, sticky="w", pady=(5, 5))

        tree_container = tk.Frame(left_frame)
        tree_container.grid(row=2, column=0, sticky="nsew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        cols = ("id", "ngay_lap", "ten_kh", "tong_tien", "tinh_trang")
        self.tree_hd = ttk.Treeview(tree_container, columns=cols, show="headings", selectmode="browse")
        self.tree_hd.heading("id", text="ID")
        self.tree_hd.heading("ngay_lap", text="Ngày lập")
        self.tree_hd.heading("ten_kh", text="Khách hàng")
        self.tree_hd.heading("tong_tien", text="Tổng tiền")
        self.tree_hd.heading("tinh_trang", text="Tình trạng")
        self.tree_hd.column("tinh_trang", width=120, anchor="center")

        self.tree_hd.column("id", width=60, anchor="center")
        self.tree_hd.column("ngay_lap", width=100, anchor="center")
        self.tree_hd.column("ten_kh", width=200)
        self.tree_hd.column("tong_tien", width=120, anchor="e")
        self.tree_hd.column("tinh_trang", width=120, anchor="center")

        # for item in hoa_don_kh_data:
        #     self.tree_kh.insert("", "end", values=item)

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree_hd.yview)
        self.tree_hd.configure(yscrollcommand=scrollbar.set)
        self.tree_hd.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.tree_hd.bind("<<TreeviewSelect>>", self.on_hoa_don_select)


        # --- 2. Frame bên phải: Chi tiết hóa đơn ---
        right_frame = tk.Frame(self, bg="#f7f9fc", padx=20, pady=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Cấu hình grid cho right_frame để cho phép các widget con co giãn
        right_frame.grid_columnconfigure(0, weight=1) # Cho phép cột 0 co giãn hết chiều rộng
        right_frame.grid_rowconfigure(3, weight=1) # <-- CHO PHÉP HÀNG 3 (chứa bảng chi tiết) CO GIÃN THEO CHIỀU DỌC

        tk.Label(right_frame, text="Chi tiết hóa đơn", font=("Segoe UI", 14, "bold"), bg="#f7f9fc").grid(row=0, column=0, sticky="w", pady=(0, 10))

        # -- Frame thông tin chung --
        info_frame = tk.Frame(right_frame, bg="#f7f9fc")
        info_frame.grid(row=1, column=0, sticky="ew", pady=(0,10))
        info_frame.grid_columnconfigure(1, weight=1)
        
        self.info_vars = {
            "Ngày lập:": tk.StringVar(), "Tên khách hàng:": tk.StringVar(),
            "Địa chỉ:": tk.StringVar(), "Số điện thoại:": tk.StringVar(),
            "Tình trạng:": tk.StringVar()
        }
        
        for i, (label_text, var) in enumerate(self.info_vars.items()):
            tk.Label(info_frame, text=label_text, font=("Segoe UI", 10, "bold"), bg="#f7f9fc").grid(row=i, column=0, sticky="nw", padx=(0,10))
            tk.Label(info_frame, textvariable=var, font=("Segoe UI", 10), bg="#f7f9fc", wraplength=250, justify="left").grid(row=i, column=1, sticky="w")
        
        tk.Label(right_frame, text="Chi tiết mặt hàng", font=("Segoe UI", 12, "bold"), bg="#f7f9fc").grid(row=2, column=0, sticky="w", pady=(10,5))
        
        # -- Bảng chi tiết mặt hàng --
        detail_tree_container = tk.Frame(right_frame)
        detail_tree_container.grid(row=3, column=0, sticky="nsew") # <-- Đặt vào hàng 3
        detail_tree_container.grid_rowconfigure(0, weight=1)
        detail_tree_container.grid_columnconfigure(0, weight=1)
        
        detail_cols = ("ngay_dat", "mat_hang", "so_luong", "gia", "noi_giao")
        self.tree_detail = ttk.Treeview(detail_tree_container, columns=detail_cols, show="headings")
        self.tree_detail.heading("ngay_dat", text="Ngày đặt")
        self.tree_detail.heading("mat_hang", text="Mặt hàng")
        self.tree_detail.heading("so_luong", text="SL")
        self.tree_detail.heading("gia", text="Giá")
        self.tree_detail.heading("noi_giao", text="Nơi giao")

        self.tree_detail.column("ngay_dat", width=80, anchor="center")
        self.tree_detail.column("so_luong", width=40, anchor="center")
        self.tree_detail.column("gia", width=100, anchor="e")
        
        detail_scrollbar = ttk.Scrollbar(detail_tree_container, orient="vertical", command=self.tree_detail.yview)
        self.tree_detail.configure(yscrollcommand=detail_scrollbar.set)
        self.tree_detail.grid(row=0, column=0, sticky="nsew")
        detail_scrollbar.grid(row=0, column=1, sticky="ns")

        # -- Frame tổng kết --
        summary_frame = tk.Frame(right_frame, bg="#f7f9fc", pady=10)
        summary_frame.grid(row=4, column=0, sticky="ew") # <-- Đặt vào hàng 4
        summary_frame.grid_columnconfigure(1, weight=1)

        self.summary_vars = { "Tổng tiền:": tk.StringVar(), "Nợ cũ:": tk.StringVar(), "TỔNG NỢ:": tk.StringVar() }
        
        for i, (label_text, var) in enumerate(self.summary_vars.items()):
            font_style = ("Segoe UI", 10, "bold") if "TỔNG" not in label_text else ("Segoe UI", 12, "bold")
            fg_color = "black" if "TỔNG" not in label_text else "#e74c3c"
            tk.Label(summary_frame, text=label_text, font=font_style, bg="#f7f9fc").grid(row=i, column=0, sticky="e", padx=(0,10))
            tk.Label(summary_frame, textvariable=var, font=font_style, bg="#f7f9fc", fg=fg_color).grid(row=i, column=1, sticky="e")

        # -- Frame nút bấm cuối trang --
        final_button_frame = tk.Frame(right_frame, bg="#f7f9fc", pady=10)
        final_button_frame.grid(row=5, column=0, sticky="ew") # <-- Đặt vào hàng 5

        final_button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1) # Chia đều không gian cho 4 nút

        buttons = ["Chốt hóa đơn", "Thanh toán", "In lại", "Xóa hóa đơn"]
        for i, btn_text in enumerate(buttons):
            tk.Button(final_button_frame, text=btn_text, font=("Segoe UI", 10), relief="groove").grid(row=0, column=i, sticky="ew", padx=2)

    # --- Các phương thức xử lý sự kiện ---
    
    def load_hoa_don_data(self, loai_hd):
        """Tải dữ liệu hóa đơn vào bảng bên trái."""
        # Xóa dữ liệu cũ
        for i in self.tree_hd.get_children():
            self.tree_hd.delete(i)
        
        # Cập nhật style nút
        if loai_hd == 'khach_hang':
            data_to_load = hoa_don_kh_data
        else: # cong_ty
            data_to_load = hoa_don_cty_data
            
        # Nạp dữ liệu mới
        for hd in data_to_load:
            # Chỉ lấy các cột cần thiết cho bảng chính
            display_values = (hd[0], hd[1], hd[2], f"{hd[5]:,}".replace(",", "."), hd[6])
            # Lưu toàn bộ dữ liệu vào item để dùng sau
            self.tree_hd.insert("", "end", values=display_values, iid=hd[0])

        # Tự động chọn dòng đầu tiên nếu có
        children = self.tree_hd.get_children()
        if children:
            self.tree_hd.selection_set(children[0])
            self.tree_hd.focus(children[0])

    def on_hoa_don_select(self, event):
        """Hiển thị chi tiết hóa đơn khi một dòng được chọn."""
        selected_items = self.tree_hd.selection()
        if not selected_items:
            return
        
        hoa_don_id = int(selected_items[0])
        
        # Tìm dữ liệu đầy đủ của hóa đơn đã chọn
        # Lấy dữ liệu từ db ở đây
        hoa_don_info = None
        for hd in hoa_don_kh_data + hoa_don_cty_data:
            if hd[0] == hoa_don_id:
                hoa_don_info = hd
                break
        
        if hoa_don_info:
            # Cập nhật thông tin chung
            self.info_vars["Ngày lập:"].set(hoa_don_info[1])
            self.info_vars["Tên khách hàng:"].set(hoa_don_info[2])
            self.info_vars["Địa chỉ:"].set(hoa_don_info[3])
            self.info_vars["Số điện thoại:"].set(hoa_don_info[4])
            self.info_vars["Tình trạng:"].set(hoa_don_info[6])

            # Cập nhật bảng chi tiết mặt hàng
            for i in self.tree_detail.get_children():
                self.tree_detail.delete(i)
                
            if hoa_don_id in chi_tiet_hd_data:
                for detail in chi_tiet_hd_data[hoa_don_id]:
                    # Định dạng giá
                    detail_values = list(detail)
                    detail_values[3] = f"{detail[3]:,}".replace(",", ".")
                    self.tree_detail.insert("", "end", values=tuple(detail_values))
            
            # Cập nhật phần tổng kết (ví dụ giả lập)
            tong_tien = hoa_don_info[5]
            no_cu = 150000 if hoa_don_id == 101 else 0 # Giả lập nợ cũ
            tong_no = tong_tien + no_cu
            self.summary_vars["Tổng tiền:"].set(f"{tong_tien:,.0f} VNĐ".replace(",", "."))
            self.summary_vars["Nợ cũ:"].set(f"{no_cu:,.0f} VNĐ".replace(",", "."))
            self.summary_vars["TỔNG NỢ:"].set(f"{tong_no:,.0f} VNĐ".replace(",", "."))  