import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from tkinter import messagebox # Import messagebox để hiện thông báo
from datetime import datetime, timedelta
from tkcalendar import DateEntry

class LsHoaDonView(tk.Frame):
    def __init__(self, parent, root_window):
        super().__init__(parent, bg="white")
        
        self.root_window = root_window
        
        # Biến để kiểm tra xem dữ liệu đã được nạp lần đầu chưa
        self._data_loaded_once = False
        self.controller = None # Sẽ được gán từ controller
        self.current_invoice_data = {} # Lưu dữ liệu hóa đơn đang hiển thị
        self.current_invoice_type = 'unpaid' # Mặc định xem hóa đơn chưa thanh toán


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
            self.load_hoa_don_data(self.current_invoice_type)
            self._data_loaded_once = True

    def refresh_data(self):
        """Làm mới dữ liệu bằng cách tải lại danh sách hóa đơn khách hàng."""
        if self.controller:
            self.load_hoa_don_data(self.current_invoice_type)
        # Không cần set _data_loaded_once nữa vì nó chỉ dùng cho lần đầu
        self._data_loaded_once = True

    def create_widgets(self):
        # --- Cấu hình layout chính: 2 cột (trái-phải) ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=2) # Thu nhỏ frame trái
        self.grid_columnconfigure(1, weight=3) # Mở rộng frame phải

        # --- 1. Frame bên trái: Danh sách hóa đơn ---
        left_frame = tk.Frame(self, bg="white", padx=10, pady=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_rowconfigure(4, weight=1) # Bảng sẽ ở hàng 4
        left_frame.grid_columnconfigure(0, weight=1)

        tk.Label(left_frame, text="Danh sách hóa đơn", font=("Segoe UI", 14, "bold"), bg="white").grid(row=0, column=0, sticky="w", pady=(5, 5))

        # -- Thanh tìm kiếm --
        search_frame = ctk.CTkFrame(left_frame, fg_color="white")
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            fg_color="white",
            text_color="grey",
            font=("Arial", 11),  
            corner_radius=10,
            border_width=2,
            border_color="#474646"
        )
        self.placeholder = "Tìm kiếm khách hàng..."
        search_entry.insert(0, self.placeholder)        
        search_entry.bind("<FocusIn>", self.on_search_focus_in)
        search_entry.bind("<FocusOut>", self.on_search_focus_out)
        search_entry.bind("<KeyRelease>", self.filter_invoices) # Gán sự kiện tìm kiếm
        search_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        top_controls_frame = tk.Frame(left_frame, bg="white")
        top_controls_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        top_controls_frame.grid_columnconfigure((0,1,2), weight=1) # Thêm cột cho nút mới

        self.btn_hd_kh = tk.Button(top_controls_frame, text="Hóa đơn chưa thanh toán", font=("Segoe UI", 10, "bold"), relief="flat", padx=10, pady=5,
                                command=lambda: self.load_hoa_don_data('unpaid'))
        self.btn_hd_kh.grid(row=0, column=0, sticky="ew")
        
        self.btn_hd_cty = tk.Button(top_controls_frame, text="Hóa đơn đã thanh toán", font=("Segoe UI", 10, "bold"), relief="flat", padx=10, pady=5,
                                    command=lambda: self.load_hoa_don_data('paid'))
        self.btn_hd_cty.grid(row=0, column=1, sticky="ew")

        self.btn_hd_gop = tk.Button(top_controls_frame, text="Hoá đơn theo tuần", font=("Segoe UI", 10, "bold"), relief="flat", padx=10, pady=5,
                                    command=lambda: self.load_hoa_don_data('summary'))
        self.btn_hd_gop.grid(row=0, column=2, sticky="ew")

        # -- Frame chọn ngày cho gộp hóa đơn --
        self.date_range_frame = tk.Frame(left_frame, bg="white")
        self.date_range_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        self.date_range_frame.grid_columnconfigure((1, 3), weight=1)
        self.date_range_frame.grid(row=3, column=0, sticky="ew", pady=(5, 10))
        self.date_range_frame.grid_columnconfigure((1, 3), weight=1) # Cho phép ô ngày co giãn

        tk.Label(self.date_range_frame, text="Từ ngày:", bg="white", font=("Segoe UI", 10)).grid(row=0, column=0, padx=(0, 5))
        self.start_date_entry = DateEntry(self.date_range_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy', font=("Segoe UI", 10))
        self.start_date_entry.grid(row=0, column=1, sticky="ew")

        tk.Label(self.date_range_frame, text="Đến ngày:", bg="white", font=("Segoe UI", 10)).grid(row=0, column=2, padx=(10, 5))
        self.end_date_entry = DateEntry(self.date_range_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy', font=("Segoe UI", 10))
        self.end_date_entry.grid(row=0, column=3, sticky="ew")

        # Thêm nút truy vấn
        query_btn = ctk.CTkButton(self.date_range_frame, text="Truy vấn", command=lambda: self.load_hoa_don_data('summary'), height=25, font=("Segoe UI", 10, "bold"))
        query_btn.grid(row=0, column=4, padx=(10, 0))

        # Đặt ngày mặc định là tuần trước
        today = datetime.today()
        start_of_last_week = today - timedelta(days=today.weekday() + 7)
        end_of_last_week = start_of_last_week + timedelta(days=6)
        self.start_date_entry.set_date(start_of_last_week)
        self.end_date_entry.set_date(end_of_last_week)

        tree_container = tk.Frame(left_frame)
        tree_container.grid(row=4, column=0, sticky="nsew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        cols = ("id", "ngay_lap", "ten_kh", "tong_tien")
        self.tree_hd = ttk.Treeview(tree_container, columns=cols, show="headings", selectmode="browse")
        self.tree_hd.heading("id", text="ID")
        self.tree_hd.heading("ngay_lap", text="Ngày lập")
        self.tree_hd.heading("ten_kh", text="Khách hàng")
        self.tree_hd.heading("tong_tien", text="Tổng tiền")

        self.tree_hd.column("id", width=60, anchor="center")
        self.tree_hd.column("ngay_lap", width=100, anchor="center")
        self.tree_hd.column("ten_kh", width=200)
        self.tree_hd.column("tong_tien", width=120, anchor="e")

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
            "Địa chỉ khách hàng:": tk.StringVar(), "Số điện thoại:": tk.StringVar(),
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
        
        # THAY ĐỔI: Sắp xếp lại cột theo yêu cầu
        detail_cols = ("ngay_mua", "mat_hang", "noi_lay", "so_xe", "don_vi", "so_luong", "gia_tai_bai", "phi_vc", "thanh_tien", "noi_giao")
        self.tree_detail = ttk.Treeview(detail_tree_container, columns=detail_cols, show="headings")
        self.tree_detail.heading("ngay_mua", text="Ngày")
        self.tree_detail.heading("mat_hang", text="Tên mặt hàng")
        self.tree_detail.heading("noi_lay", text="Lấy tại bãi")
        self.tree_detail.heading("so_xe", text="Số xe")
        self.tree_detail.heading("don_vi", text="Số khối")
        self.tree_detail.heading("so_luong", text="Số chuyến")
        self.tree_detail.heading("gia_tai_bai", text="Giá tại bãi")
        self.tree_detail.heading("phi_vc", text="Phí VC")
        self.tree_detail.heading("thanh_tien", text="Thành tiền")
        self.tree_detail.heading("noi_giao", text="Nơi giao")

        self.tree_detail.column("ngay_mua", width=80, anchor="center")
        self.tree_detail.column("mat_hang", width=120, anchor="center")
        self.tree_detail.column("noi_lay", width=80, anchor="center")
        self.tree_detail.column("so_xe", width=80, anchor="center")
        self.tree_detail.column("don_vi", width=70, anchor="center")
        self.tree_detail.column("so_luong", width=80, anchor="center")
        self.tree_detail.column("gia_tai_bai", width=80, anchor="center")
        self.tree_detail.column("phi_vc", width=80, anchor="center")
        self.tree_detail.column("thanh_tien", width=100, anchor="center")
        self.tree_detail.column("noi_giao", width=120, anchor="center")
        
        detail_scrollbar = ttk.Scrollbar(detail_tree_container, orient="vertical", command=self.tree_detail.yview)
        self.tree_detail.configure(yscrollcommand=detail_scrollbar.set)
        self.tree_detail.grid(row=0, column=0, sticky="nsew")
        detail_scrollbar.grid(row=0, column=1, sticky="ns")

        # -- Frame tổng kết --
        summary_frame = tk.Frame(right_frame, bg="#f7f9fc", pady=10)
        summary_frame.grid(row=4, column=0, sticky="ew") # <-- Đặt vào hàng 4
        summary_frame.grid_columnconfigure(1, weight=1)

        self.summary_vars = {
            "Tổng tiền hóa đơn:": tk.StringVar(),
            "Công nợ kỳ trước:": tk.StringVar(),
            "Tổng phải thu hiện tại:": tk.StringVar()
        }
        
        for i, (label_text, var) in enumerate(self.summary_vars.items()):
            font_style = ("Segoe UI", 10, "bold") if "TỔNG" not in label_text else ("Segoe UI", 12, "bold")
            fg_color = "black" if "TỔNG" not in label_text else "#e74c3c"
            tk.Label(summary_frame, text=label_text, font=font_style, bg="#f7f9fc").grid(row=i, column=0, sticky="e", padx=(0,10))
            tk.Label(summary_frame, textvariable=var, font=font_style, bg="#f7f9fc", fg=fg_color).grid(row=i, column=1, sticky="e")

        # -- Frame nút bấm cuối trang --
        final_button_frame = tk.Frame(right_frame, bg="#f7f9fc", pady=10)
        final_button_frame.grid(row=5, column=0, sticky="ew") # <-- Đặt vào hàng 5

        # Cấu hình frame để các nút con được căn giữa
        final_button_frame.pack_propagate(0) # Ngăn frame co lại
        final_button_frame.configure(height=50) # Đặt chiều cao cố định cho frame

        button_group = tk.Frame(final_button_frame, bg="#f7f9fc")
        button_group.pack(anchor="center")

        # Nút Thanh toán (Màu xanh lá)
        ctk.CTkButton(button_group, text="Thanh toán", command=self.process_payment,
                      font=("Segoe UI", 15, "bold"), fg_color="#2ecc71", hover_color="#156336",
                      width=150, corner_radius=8
                      ).pack(side="left", padx=10, pady=2)

        # Nút In hóa đơn (Màu vàng)
        ctk.CTkButton(button_group, text="In hóa đơn", command=self.process_print_invoice,
                      font=("Segoe UI", 15, "bold"), fg_color="#f39c12", hover_color="#d35400",
                      width=150, corner_radius=8
                      ).pack(side="left", padx=10, pady=2)

        # Nút Xuất PDF (Màu trung tính)
        ctk.CTkButton(button_group, text="Xuất PDF", command=self.process_export_pdf,
                      font=("Segoe UI", 15, "bold"), width=150, corner_radius=8
                      ).pack(side="left", padx=10, pady=2)
        
        # Nút "Xem trước" - gán command cho nó
        # preview_btn = tk.Button(
        #     final_button_frame, 
        #     text="Xem trước", 
        #     font=("Segoe UI", 10), 
        #     relief="groove",
        #     command=self.show_invoice_preview # <-- GÁN LỆNH Ở ĐÂY
        # )
        # preview_btn.grid(row=0, column=4, sticky="ew", padx=2)
    # --- Các phương thức xử lý sự kiện ---

    def filter_invoices(self, event=None):
        """Lọc danh sách hóa đơn dựa trên tên khách hàng."""
        search_term = self.search_var.get().lower().strip()

        # Xóa các dòng hiện tại trong treeview
        for i in self.tree_hd.get_children():
            self.tree_hd.delete(i)

        # Lặp qua dữ liệu gốc đã lưu và chèn lại nếu khớp
        for invoice_id, invoice_data in self.current_invoice_data.items():
            customer_name = invoice_data[2].lower()
            if search_term in customer_name:
                ngay_lap = invoice_data[1].split(' ')[0] if invoice_data[1] else ''
                ten_kh = invoice_data[2]
                tong_tien = invoice_data[5]
                display_values = (invoice_id, ngay_lap, ten_kh, f"{tong_tien:,.0f}".replace(",", "."))
                self.tree_hd.insert("", "end", values=display_values, iid=invoice_id)

        # Tự động chọn lại dòng đầu tiên nếu có kết quả
        children = self.tree_hd.get_children()
        if children:
            self.tree_hd.selection_set(children[0])
            self.tree_hd.focus(children[0])

    def on_search_focus_in(self, event):
        """Xử lý sự kiện khi ô tìm kiếm được focus."""
        if self.search_var.get() == self.placeholder:
            event.widget.delete(0, "end")
            event.widget.configure(fg="black")

    def on_search_focus_out(self, event):
        """Xử lý sự kiện khi ô tìm kiếm mất focus."""
        if not self.search_var.get():
            event.widget.insert(0, self.placeholder)
            event.widget.configure(fg="grey")

    def update_tab_colors(self):
        """Cập nhật màu sắc cho các nút tab dựa trên tab hiện tại."""
        # Màu sắc
        active_bg = "#3498db"
        active_fg = "white"
        inactive_bg = "SystemButtonFace"
        inactive_fg = "black"

        # Hiển thị/ẩn frame chọn ngày
        if self.current_invoice_type == 'summary':
            self.date_range_frame.grid()
        else:
            self.date_range_frame.grid_remove()

        # Cập nhật màu cho từng nút dựa trên tab hiện tại
        self.btn_hd_kh.config(bg=active_bg if self.current_invoice_type == 'unpaid' else inactive_bg, fg=active_fg if self.current_invoice_type == 'unpaid' else inactive_fg)
        self.btn_hd_cty.config(bg=active_bg if self.current_invoice_type == 'paid' else inactive_bg, fg=active_fg if self.current_invoice_type == 'paid' else inactive_fg)
        self.btn_hd_gop.config(bg=active_bg if self.current_invoice_type == 'summary' else inactive_bg, fg=active_fg if self.current_invoice_type == 'summary' else inactive_fg)

    # def show_invoice_preview(self):
    #     selected_items = self.tree_hd.selection()
    #     if not selected_items:
    #         messagebox.showwarning("Chưa chọn hóa đơn", "Vui lòng chọn một hóa đơn để xem trước.")
    #         return
    #     customer_name = self.info_vars["Tên khách hàng:"].get()
    #     customer_phone = self.info_vars["Số điện thoại:"].get()

    #     preview_window = tk.Toplevel(self.root_window)
    #     preview_window.title(f"Xem trước hóa đơn - Khách hàng: {customer_name}")
    #     preview_window.geometry("900x650")
    #     preview_window.configure(bg="lightgrey")
    #     preview_window.transient(self.root_window)
    #     preview_window.grab_set()

    #     container = tk.Frame(preview_window)
    #     container.pack(fill="both", expand=True)
    #     canvas = tk.Canvas(container, bg="white")
    #     scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    #     canvas.configure(yscrollcommand=scrollbar.set)
    #     scrollbar.pack(side="right", fill="y")
    #     canvas.pack(side="left", fill="both", expand=True)
    #     scrollable_frame = tk.Frame(canvas, bg="white", padx=30, pady=30)
    #     canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # def on_frame_configure(event):
        #     canvas.configure(scrollregion=canvas.bbox("all"))
        # scrollable_frame.bind("<Configure>", on_frame_configure)
        # header_frame = tk.Frame(scrollable_frame, bg="white")
        # header_frame.pack(fill="x")
        # header_left = tk.Frame(header_frame, bg="white")
        # header_left.pack(side="left")
        # tk.Label(header_left, text="CỬA HÀNG VLXD VÀ SAN LẤP MẶT BẰNG NGUYỄN ĐẠT", font=("Arial", 12, "bold"), bg="white", justify="left").pack(anchor="w")
        # tk.Label(header_left, text="MST: 0314412607", font=("Arial", 10), bg="white").pack(anchor="w")
        # tk.Label(header_left, text="Địa chỉ: 149A, Lý Thế Kiệt, P. Linh Đông, Q. Thủ Đức, TP.HCM", font=("Arial", 10), bg="white").pack(anchor="w")
        # tk.Label(header_left, text="Liên hệ: 0977.209.709 (Đạt) - 0967.209.709 (Trinh)", font=("Arial", 10), bg="white").pack(anchor="w")
        # header_right = tk.Frame(header_frame, bg="white")
        # header_right.pack(side="right")
        # ngay_lap = self.info_vars["Ngày lập:"].get()
        # tk.Label(header_right, text=f"Ngày nhập: {ngay_lap}", font=("Arial", 10, "italic"), bg="white").pack(anchor="e")
        # tk.Label(header_right, text=f"Ngày in: {datetime.now().strftime('%d/%m/%Y %H:%M')}", font=("Arial", 10, "italic"), bg="white").pack(anchor="e")
        # tk.Label(scrollable_frame, text="HÓA ĐƠN BÁN HÀNG", font=("Arial", 20, "bold"), bg="white", pady=20).pack()
        # customer_frame = tk.Frame(scrollable_frame, bg="white")
        # customer_frame.pack(fill="x", pady=10)
        # tk.Label(customer_frame, text=f"Tên khách hàng: {customer_name}", font=("Arial", 10, "bold"), bg="white").pack(anchor="w")
        # tk.Label(customer_frame, text=f"Số điện thoại: {customer_phone}", font=("Arial", 10), bg="white").pack(anchor="w")
        # details_tree_frame = tk.Frame(scrollable_frame, bg="white")
        # details_tree_frame.pack(fill="x", pady=10)
        # detail_cols = ("ngay_mua", "mat_hang", "so_luong", "gia", "thanh_tien", "ghi_chu")
        # num_items = len(self.tree_detail.get_children())
        # preview_tree = ttk.Treeview(details_tree_frame, columns=detail_cols, show="headings", height=num_items)
        # preview_tree.heading("ngay_mua", text="Ngày mua")
        # preview_tree.heading("mat_hang", text="Mặt hàng")
        # preview_tree.heading("so_luong", text="Số lượng")
        # preview_tree.heading("gia", text="Đơn giá")
        # preview_tree.heading("thanh_tien", text="Thành tiền")
        # preview_tree.heading("ghi_chu", text="Ghi chú (Nơi giao)")
        # preview_tree.column("ngay_mua", width=100, anchor="center")
        # preview_tree.column("so_luong", width=80, anchor="center")
        # preview_tree.column("gia", width=120, anchor="e")
        # preview_tree.column("thanh_tien", width=120, anchor="e")
        # preview_tree.column("mat_hang", width=200)

        # # Vòng lặp for để chèn dữ liệu
        # for item_id in self.tree_detail.get_children():
        #     item_data = self.tree_detail.item(item_id, 'values')
        #     ngay_mua, mat_hang, so_luong, gia_str, noi_giao = item_data
        #     try:
        #         gia = int(gia_str.replace(".", ""))
        #         thanh_tien = gia * float(so_luong)
        #         thanh_tien_f = f"{thanh_tien:,.0f}".replace(",", ".")
        #     except:
        #         thanh_tien_f = "Lỗi"
        #     preview_tree.insert("", "end", values=(ngay_mua, mat_hang, so_luong, gia_str, thanh_tien_f, noi_giao))
        
        # # Dòng này phải nằm ngoài vòng lặp for, ở cùng cấp độ thụt lề
        # preview_tree.pack(fill="x")

        # footer_frame = tk.Frame(scrollable_frame, bg="white", pady=20)
        # footer_frame.pack(fill="x")
        # footer_frame.grid_columnconfigure((0, 1), weight=1)
        # footer_left = tk.Frame(footer_frame, bg="white")
        # footer_left.grid(row=0, column=0, sticky="n")
        # tk.Label(footer_left, text=f"Ngày {datetime.now().day} tháng {datetime.now().month} năm {datetime.now().year}", font=("Arial", 10, "italic"), bg="white").pack()
        # tk.Label(footer_left, text="Người lập phiếu", font=("Arial", 10, "bold"), bg="white").pack(pady=(10,0))
        # footer_right = tk.Frame(footer_frame, bg="white")
        # footer_right.grid(row=0, column=1, sticky="e")
        # # no_cu = self.summary_vars["Nợ cũ:"].get()
        # # tong_no = self.summary_vars["TỔNG NỢ:"].get()
        # # tk.Label(footer_right, text=f"Nợ cũ: {no_cu}", font=("Arial", 10), bg="white").pack(anchor="e")
        # # tk.Label(footer_right, text=f"Tổng nợ: {tong_no}", font=("Arial", 12, "bold"), bg="white").pack(anchor="e")
        
        # action_frame = tk.Frame(preview_window, bg="white", pady=10)
        # action_frame.pack(fill="x", side="bottom", padx=30)
        # tk.Button(action_frame, text="In Hóa Đơn", font=("Arial", 10, "bold")).pack(side="right", padx=5)
        # tk.Button(action_frame, text="Đóng", command=preview_window.destroy).pack(side="right")

    def get_date_range(self):
        """Lấy ngày bắt đầu và kết thúc từ DateEntry."""
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()
        return start_date, end_date

    def process_print_invoice(self):
        """Thu thập dữ liệu từ giao diện và yêu cầu controller thực hiện in."""
        selected_items = self.tree_hd.selection()
        if not selected_items:
            messagebox.showwarning("Chưa chọn hóa đơn", "Vui lòng chọn một hóa đơn để in.")
            return

        if not self.controller:
            messagebox.showerror("Lỗi", "Controller chưa được khởi tạo.")
            return

        # 1. Thu thập thông tin chung của hóa đơn
        invoice_data_for_print = {
            'customer_name': self.info_vars["Tên khách hàng:"].get(),
            'customer_phone': self.info_vars["Số điện thoại:"].get(),
            'customer_address': self.info_vars["Địa chỉ khách hàng:"].get(),
            'invoice_date': self.info_vars["Ngày lập:"].get(),
            'total_invoice': self.summary_vars["Tổng tiền hóa đơn:"].get(),
            'paid_amount': self.summary_vars["Công nợ kỳ trước:"].get(),
            'current_debt': self.summary_vars["Tổng phải thu hiện tại:"].get()
        }

        # 2. Thu thập danh sách các mặt hàng từ bảng chi tiết
        items_for_print = []
        for item_id in self.tree_detail.get_children():
            item_values = self.tree_detail.item(item_id, 'values') 
            # THAY ĐỔI: Lấy dữ liệu theo cấu trúc cột mới
            ngay_mua = item_values[0] 
            mat_hang = item_values[1] 
            noi_lay = item_values[2]
            so_xe = item_values[3] 
            don_vi = item_values[4] 
            so_luong = item_values[5] 
            don_gia = item_values[6].replace('.', '') # Giá tại bãi
            phi_vc = item_values[7].replace('.', '') # Phí VC
            thanh_tien = item_values[8].replace('.', '') # Thành tiền
            noi_giao = item_values[9].split('-')[0].strip()
            
            items_for_print.append((ngay_mua, mat_hang, so_xe, noi_lay, don_vi, so_luong, thanh_tien, noi_giao, don_gia, phi_vc))

        # 3. Gọi controller để xử lý
        self.controller.print_invoice(invoice_data_for_print, items_for_print)
    
    def process_export_pdf(self):
        """Thu thập dữ liệu và yêu cầu controller chỉ tạo file PDF mà không in."""
        selected_items = self.tree_hd.selection()
        if not selected_items:
            messagebox.showwarning("Chưa chọn hóa đơn", "Vui lòng chọn một hóa đơn để xuất PDF.")
            return

        if not self.controller:
            messagebox.showerror("Lỗi", "Controller chưa được khởi tạo.")
            return

        # 1. Thu thập thông tin chung của hóa đơn (giống hệt process_print_invoice)
        invoice_data_for_export = {
            'customer_name': self.info_vars["Tên khách hàng:"].get(),
            'customer_phone': self.info_vars["Số điện thoại:"].get(),
            'customer_address': self.info_vars["Địa chỉ khách hàng:"].get(),
            'invoice_date': self.info_vars["Ngày lập:"].get(),
            'total_invoice': self.summary_vars["Tổng tiền hóa đơn:"].get(),
            'paid_amount': self.summary_vars["Công nợ kỳ trước:"].get(),
            'current_debt': self.summary_vars["Tổng phải thu hiện tại:"].get()
        }

        # 2. Thu thập danh sách các mặt hàng từ bảng chi tiết
        items_for_export = []
        for item_id in self.tree_detail.get_children():
            item_values = self.tree_detail.item(item_id, 'values')
            # THAY ĐỔI: Lấy dữ liệu theo cấu trúc cột mới
            ngay_mua = item_values[0] 
            mat_hang = item_values[1] 
            noi_lay = item_values[2]
            so_xe = item_values[3] 
            don_vi = item_values[4] 
            so_luong = item_values[5] 
            don_gia = item_values[6].replace('.', '') # Giá tại bãi
            phi_vc = item_values[7].replace('.', '') # Phí VC
            thanh_tien = item_values[8].replace('.', '') # Thành tiền
            noi_giao = item_values[9].split('-')[0].strip()

            items_for_export.append((ngay_mua, mat_hang, so_xe, noi_lay, don_vi, so_luong, thanh_tien, noi_giao, don_gia, phi_vc))

        # 3. Gọi controller để xử lý việc xuất PDF
        self.controller.export_invoice_to_pdf(invoice_data_for_export, items_for_export)

    def process_payment(self):
        """Xử lý sự kiện nhấn nút Thanh toán."""
        selected_items = self.tree_hd.selection()
        if not selected_items:
            messagebox.showwarning("Chưa chọn hóa đơn", "Vui lòng chọn một hóa đơn để thanh toán.")
            return

        if self.current_invoice_type != 'unpaid' and self.current_invoice_type != 'summary':
            messagebox.showinfo("Thông báo", "Chỉ có thể thanh toán cho các hóa đơn 'Chưa thanh toán'.")
            return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn thanh toán cho hóa đơn này?"):
            invoice_id_str = selected_items[0]
            invoice_data = self.current_invoice_data.get(invoice_id_str)
            if invoice_data and self.controller:
                invoice_id = int(invoice_id_str)
                customer_id = invoice_data[7] # id_kh
                total_amount = invoice_data[5] # tong_tien
                self.controller.pay_invoice(invoice_id, customer_id, total_amount)

    def load_hoa_don_data(self, invoice_type):
        """Yêu cầu controller tải dữ liệu hóa đơn."""
        self.current_invoice_type = invoice_type
        if self.controller: # Luôn tải dữ liệu khi chuyển tab
            self.controller.load_invoices(invoice_type)

        # Cập nhật màu sắc của tab
        self.update_tab_colors()

    def display_invoices(self, invoices, invoice_type):
        """Hiển thị dữ liệu hóa đơn do controller cung cấp vào bảng bên trái."""
        # Xóa dữ liệu cũ
        for i in self.tree_hd.get_children():
            self.tree_hd.delete(i)
        self.current_invoice_data.clear()
        self.search_var.set(self.placeholder) # Reset ô tìm kiếm

        for hd in invoices:
            invoice_id = hd[0]
            # Xử lý ngày lập tùy theo loại hóa đơn
            if invoice_type == 'summary':
                ngay_lap = hd[1] # Giữ nguyên chuỗi khoảng ngày "dd/mm - dd/mm/yyyy"
            else:
                ngay_lap = hd[1].split(' ')[0] if hd[1] else '' # Chỉ lấy phần ngày cho hóa đơn đơn lẻ
            ten_kh = hd[2]
            tong_tien = hd[5] # tong_tien

            display_values = (invoice_id, ngay_lap, ten_kh, f"{tong_tien:,.0f}".replace(",", "."))
            self.tree_hd.insert("", "end", values=display_values, iid=invoice_id)
            self.current_invoice_data[str(invoice_id)] = hd # Lưu dữ liệu đầy đủ

        # Cập nhật màu sắc của tab
        # self.update_tab_colors() # Đã chuyển vào load_hoa_don_data

        # Tự động chọn dòng đầu tiên nếu có
        children = self.tree_hd.get_children()
        if children:
            self.tree_hd.selection_set(children[0])
            self.tree_hd.focus(children[0])
        else:
            # Nếu không có dữ liệu, xóa form chi tiết
            self.clear_details()

    def on_hoa_don_select(self, event):
        """Hiển thị chi tiết hóa đơn khi một dòng được chọn."""
        selected_items = self.tree_hd.selection()
        if not selected_items:
            return

        hoa_don_id_str = selected_items[0]
        hoa_don_info = self.current_invoice_data.get(hoa_don_id_str)

        if hoa_don_info:
            # Cập nhật thông tin chung
            if self.current_invoice_type == 'summary':
                self.info_vars["Ngày lập:"].set(hoa_don_info[1]) # Giữ nguyên chuỗi khoảng ngày
            else:
                self.info_vars["Ngày lập:"].set(hoa_don_info[1].split(' ')[0] if hoa_don_info[1] else '')

            self.info_vars["Tên khách hàng:"].set(hoa_don_info[2])
            self.info_vars["Địa chỉ khách hàng:"].set(hoa_don_info[3] or "N/A")
            self.info_vars["Số điện thoại:"].set(hoa_don_info[4] or "N/A")
            self.info_vars["Tình trạng:"].set(hoa_don_info[6] or "N/A")

            # Cập nhật bảng chi tiết mặt hàng
            for i in self.tree_detail.get_children():
                self.tree_detail.delete(i)

            if self.controller:
                if self.current_invoice_type == 'summary':
                    # Nếu là hóa đơn gộp, hoa_don_id_str thực chất là id_kh
                    customer_id = int(hoa_don_id_str)
                    start_date, end_date = self.get_date_range()
                    details = self.controller.get_summary_details(customer_id, start_date, end_date)
                else:
                    # Nếu là hóa đơn đơn lẻ, lấy chi tiết theo id_hd
                    details = self.controller.get_invoice_details(int(hoa_don_id_str))

                for detail in details:
                    # Cấu trúc tuple trả về từ cả 2 hàm là như nhau
                    # (ngay_mua, ten_sp, so_luong, thanh_tien, noi_giao, bien_so, ten_bai, don_vi_tinh, don_gia, phi_vc)
                    thanh_tien_formatted = f"{int(detail[3]):,.0f}".replace(",", ".") if detail[3] else "0"
                    don_gia_formatted = f"{int(detail[8]):,.0f}".replace(",", ".") if detail[8] else "0"
                    phi_vc_formatted = f"{int(detail[9]):,.0f}".replace(",", ".") if detail[9] else "0"
                    ngay_mua_formatted = detail[0].split(' ')[0] if detail[0] else ''
                    don_vi_tinh = detail[7] if len(detail) > 7 else '' # Lấy đơn vị tính từ vị trí index 7
                    
                    # THAY ĐỔI: Chèn dữ liệu vào bảng theo đúng thứ tự cột mới
                    self.tree_detail.insert("", "end", values=(ngay_mua_formatted, detail[1], detail[6] or '', detail[5] or '', don_vi_tinh, detail[2], don_gia_formatted, phi_vc_formatted, thanh_tien_formatted, detail[4]))

            # Cập nhật phần tổng kết
            tong_tien = hoa_don_info[5]
            self.summary_vars["Tổng tiền hóa đơn:"].set(f"{tong_tien:,.0f} VNĐ".replace(",", "."))

            # Lấy và hiển thị công nợ
            customer_id = hoa_don_info[7] # id_kh luôn ở cột thứ 8 (index 7)
            current_debt, old_debt = self.controller.get_customer_debt(customer_id)
            self.summary_vars["Tổng phải thu hiện tại:"].set(f"{current_debt:,.0f} VNĐ".replace(",", "."))
            self.summary_vars["Công nợ kỳ trước:"].set(f"{old_debt:,.0f} VNĐ".replace(",", "."))

    def clear_details(self):
        """Xóa thông tin ở khung chi tiết bên phải."""
        for var in self.info_vars.values():
            var.set("")
        for var in self.summary_vars.values():
            var.set("")
        self.summary_vars["Công nợ kỳ trước:"].set("") # Thêm dòng này
        for i in self.tree_detail.get_children():
            self.tree_detail.delete(i)