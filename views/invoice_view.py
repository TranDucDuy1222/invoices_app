import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import date
from tkcalendar import DateEntry
import customtkinter as ctk
from controllers.invoice_controller import InvoiceController

class TaoHoaDonView(tk.Frame):
    def __init__(self, parent, root_window):
        super().__init__(parent, bg="white")
        
        self.root_window = root_window
        
        # --- Dữ liệu mẫu ---
        self.khach_hang_lookup = {}
        self.mat_hang_lookup = {}
        self.car_lookup = {}
        self.current_customer_id = None
        self.current_order_items = []
        self.editing_item_iid = None # Biến để theo dõi item đang được chỉnh sửa
        self.trang_thai_var = tk.StringVar(value="Chưa thanh toán")

        # --- Đăng ký hàm kiểm tra nhập liệu ---
        self.vcmd = (self.register(self.validate_integer_input), '%P')
        
        # Phải tạo widget trước khi khởi tạo controller
        # để controller có thể truy cập các widget này
        self.create_widgets()

        # --- Biến lưu trữ dữ liệu ---
        self.invoice_controller = InvoiceController(view=self, db_path=getattr(root_window, "db_path", None))

    def update_customer_list(self, customers):
        """Cập nhật danh sách khách hàng từ controller."""
        kh_names = [kh[1] for kh in customers]
        self.khach_hang_dropdown['values'] = kh_names
        # Tạo một dictionary để tra cứu thông tin khách hàng bằng tên
        self.khach_hang_lookup = {kh[1]: kh for kh in customers}

    def update_car_list(self, cars):
        """Cập nhật danh sách xe từ controller."""
        car_plates = [car[1] for car in cars]
        self.car_dropdown['values'] = car_plates
        self.car_lookup = {car[1]: car for car in cars}

    def update_product_list(self, products):
        """Danh sách sản phẩm từ controller."""
        mh_display_names = []
        self.mat_hang_lookup = {}
        # products: (id_sp, ten_sp, don_vi_tinh, gia_ban, ten_bai)
        for product in products:
            ten_sp = product[1]
            ten_bai = product[4]
            # Tạo tên hiển thị: "Tên sản phẩm (Tên bãi)" nếu có bãi
            display_name = f"{ten_sp} ({ten_bai})" if ten_bai else ten_sp
            mh_display_names.append(display_name)
            # Lưu thông tin sản phẩm với key là tên hiển thị
            self.mat_hang_lookup[display_name] = product

        self.mat_hang_dropdown['values'] = mh_display_names

    def validate_integer_input(self, P):
        """Kiểm tra xem giá trị mới có phải là số nguyên hay không."""
        # Cho phép chuỗi rỗng hoặc chuỗi chỉ chứa số và dấu chấm
        if all(char.isdigit() or char == '.' for char in P) or P == "":
            return True 
        return False
    def create_widgets(self):
        # --- Cấu hình layout chính: 2 cột ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- 1. Frame bên trái: Tạo đơn hàng ---
        left_frame = tk.Frame(self, bg="#f7f9fc", padx=20, pady=20)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.grid_columnconfigure(1, weight=1)

        tk.Label(left_frame, text="Tạo đơn hàng", font=("Segoe UI", 16, "bold"), bg="#f7f9fc").grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        # --- Các trường nhập liệu ---
        # Ngày mua của khách hàng
        tk.Label(left_frame, text="Ngày mua:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=1, column=0, sticky="w", pady=5)
        self.ngay_tao_entry = DateEntry(left_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy', font=("Segoe UI", 10))
        self.ngay_tao_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Khách hàng (chỉ đọc)
        tk.Label(left_frame, text="Khách hàng:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=2, column=0, sticky="w", pady=5)
        self.khach_hang_var = tk.StringVar()
        self.khach_hang_dropdown = ttk.Combobox(left_frame, textvariable=self.khach_hang_var, values=[], state="readonly", font=("Segoe UI", 10))
        self.khach_hang_dropdown.grid(row=2, column=1, sticky="ew", pady=5)
        self.khach_hang_dropdown.bind("<<ComboboxSelected>>", self.on_customer_select)
        
        # Chọn xe
        tk.Label(left_frame, text="Chọn xe:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=3, column=0, sticky="w", pady=5)
        self.car_var = tk.StringVar()
        self.car_dropdown = ttk.Combobox(left_frame, textvariable=self.car_var, values=[], state="readonly", font=("Segoe UI", 10))
        self.car_dropdown.grid(row=3, column=1, sticky="ew", pady=5)

        # Mặt hàng (chỉ đọc)
        tk.Label(left_frame, text="Mặt hàng:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=4, column=0, sticky="w", pady=5)
        self.mat_hang_var = tk.StringVar()
        self.mat_hang_dropdown = ttk.Combobox(left_frame, textvariable=self.mat_hang_var, values=[], state="readonly", font=("Segoe UI", 10))
        self.mat_hang_dropdown.grid(row=4, column=1, sticky="ew", pady=5)
        self.mat_hang_dropdown.bind("<<ComboboxSelected>>", self.on_item_select)
        
        # Đơn vị và giá (tùy chọn) - Radio buttons
        tk.Label(left_frame, text="Tùy chọn giá:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=5, column=0, sticky="nw", pady=5)
        self.unit_price_options_frame = tk.Frame(left_frame, bg="#f7f9fc")
        self.unit_price_options_frame.grid(row=5, column=1, sticky="ew", pady=5)
        self.unit_price_var = tk.StringVar()

        # Đơn vị tính và Giá bán (tùy chỉnh) - Gộp thành 1 hàng
        tk.Label(left_frame, text="Đơn vị/Giá:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=6, column=0, sticky="w", pady=5)
        custom_price_frame = tk.Frame(left_frame, bg="#f7f9fc")
        custom_price_frame.grid(row=6, column=1, sticky="ew", pady=5)
        custom_price_frame.grid_columnconfigure(0, weight=1)
        custom_price_frame.grid_columnconfigure(2, weight=1)

        self.don_vi_var = tk.StringVar(value="")
        self.don_vi_entry = tk.Entry(custom_price_frame, textvariable=self.don_vi_var, font=("Segoe UI", 10), width=10)
        self.don_vi_entry.grid(row=0, column=0, sticky="ew")

        tk.Label(custom_price_frame, text=" : ", font=("Segoe UI", 10, "bold"), bg="#f7f9fc").grid(row=0, column=1, padx=5)

        self.don_gia_var = tk.StringVar()
        self.don_gia_entry = tk.Entry(custom_price_frame, textvariable=self.don_gia_var, font=("Segoe UI", 10), validate="key", validatecommand=self.vcmd, justify="right")
        self.don_gia_entry.grid(row=0, column=2, sticky="ew")
        self.don_gia_entry.bind("<KeyRelease>", self.on_don_gia_key_release)

        # Số chuyến
        tk.Label(left_frame, text="Số chuyến:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=7, column=0, sticky="w", pady=5)
        self.so_luong_var = tk.IntVar(value=1)
        self.so_luong_entry = tk.Entry(left_frame, textvariable=self.so_luong_var, font=("Segoe UI", 10), validate="key", validatecommand=self.vcmd)
        self.so_luong_entry.grid(row=7, column=1, sticky="ew", pady=5)
        self.so_luong_entry.bind("<KeyRelease>", self.calculate_subtotal)

        # Phí vận chuyển
        tk.Label(left_frame, text="Phí vận chuyển:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=8, column=0, sticky="w", pady=5)
        phi_vc_container = tk.Frame(left_frame, bg="#f7f9fc")
        phi_vc_container.grid(row=8, column=1, sticky="ew", pady=5)
        phi_vc_container.grid_columnconfigure(0, weight=1)
        self.phi_vc_var = tk.StringVar(value="")
        self.phi_vc_entry = tk.Entry(phi_vc_container, textvariable=self.phi_vc_var, font=("Segoe UI", 10), validate="key", validatecommand=self.vcmd, justify="right")
        self.phi_vc_entry.grid(row=0, column=0, sticky="ew")
        self.phi_vc_entry.bind("<KeyRelease>", self.calculate_subtotal)
        tk.Label(phi_vc_container, text=" 000 VNĐ", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=0, column=1, sticky="w")
        
        tk.Label(left_frame, text="Tên nơi giao:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=9, column=0, sticky="w", pady=5)
        self.noi_giao_var = tk.StringVar()
        tk.Entry(left_frame, textvariable=self.noi_giao_var, font=("Segoe UI", 10)).grid(row=9, column=1, sticky="ew", pady=5)

        tk.Label(left_frame, text="Địa chỉ chi tiết:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=10, column=0, sticky="w", pady=5)
        self.dia_chi_chi_tiet_var = tk.StringVar()
        tk.Entry(left_frame, textvariable=self.dia_chi_chi_tiet_var, font=("Segoe UI", 10)).grid(row=10, column=1, sticky="ew", pady=5)

        tk.Label(left_frame, text="Thành tiền + Ship:", font=("Segoe UI", 10, "bold"), bg="#f7f9fc").grid(row=11, column=0, sticky="w", pady=5)
        self.thanh_tien_var = tk.StringVar(value="0 VNĐ")
        tk.Label(left_frame, textvariable=self.thanh_tien_var, font=("Segoe UI", 12, "bold"), bg="#f7f9fc").grid(row=11, column=1, sticky="w", pady=5)

        # Frame cho các nút Thêm/Cập nhật
        add_update_frame = tk.Frame(left_frame, bg="#f7f9fc")
        add_update_frame.grid(row=12, column=0, columnspan=2, pady=20, sticky="ew")
        add_update_frame.grid_columnconfigure(0, weight=1)
        add_update_frame.grid_columnconfigure(1, weight=1)

        self.add_button = ctk.CTkButton(add_update_frame, text=" Thêm vào đơn hàng", command=self.add_item_to_order, 
                               font=("Segoe UI", 12, "bold"), fg_color="#27ae60",
                               compound="left")
        self.add_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.cancel_edit_button = ctk.CTkButton(add_update_frame, text="Hủy sửa", command=self.cancel_edit, fg_color="#e74c3c")
        # --- 2. Frame bên phải: Thông tin hóa đơn ---
        right_frame = tk.Frame(self, bg="white", padx=20, pady=20)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_rowconfigure(2, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        customer_info_frame = tk.LabelFrame(right_frame, text="Thông tin khách hàng", font=("Segoe UI", 12, "bold"), bg="white", padx=15, pady=10, relief="groove")
        customer_info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        customer_info_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(customer_info_frame, text="Khách hàng:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=0, column=0, sticky="w")
        self.ten_kh_label = tk.Label(customer_info_frame, text="...", font=("Segoe UI", 10), bg="white")
        self.ten_kh_label.grid(row=0, column=1, sticky="w", padx=5)

        tk.Label(customer_info_frame, text="Địa chỉ:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=1, column=0, sticky="w")
        self.dia_chi_label = tk.Label(customer_info_frame, text="...", font=("Segoe UI", 10), bg="white", wraplength=300, justify="left")
        self.dia_chi_label.grid(row=1, column=1, sticky="w", padx=5)
        
        tk.Label(customer_info_frame, text="SĐT:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=2, column=0, sticky="w")
        self.sdt_label = tk.Label(customer_info_frame, text="...", font=("Segoe UI", 10), bg="white")
        self.sdt_label.grid(row=2, column=1, sticky="w", padx=5)

        tk.Label(right_frame, text="Danh sách đặt hàng", font=("Segoe UI", 12, "bold"), bg="white").grid(row=1, column=0, sticky="w", pady=(0,10))
        
        order_list_container = tk.Frame(right_frame)
        order_list_container.grid(row=2, column=0, sticky="nsew")
        order_list_container.grid_rowconfigure(0, weight=1)
        order_list_container.grid_columnconfigure(0, weight=1)
        
        cols = ("ten_sp", "lay_tai_bai", "so_xe", "don_vi", "so_luong", "gia_tai_bai", "phi_vc", "thanh_tien", "noi_giao",)
        self.order_tree = ttk.Treeview(order_list_container, columns=cols, show="headings")
        self.order_tree.heading("ten_sp", text="Tên mặt hàng")
        self.order_tree.heading("lay_tai_bai", text="Lấy tại bãi")
        self.order_tree.heading("so_xe", text="Số xe")
        self.order_tree.heading("don_vi", text="Số khối")
        self.order_tree.heading("so_luong", text="Số chuyến")
        self.order_tree.heading("gia_tai_bai", text="Giá tại bãi")
        self.order_tree.heading("phi_vc", text="Phí vận chuyển")
        self.order_tree.heading("thanh_tien", text="Thành tiền")
        self.order_tree.heading("noi_giao", text="Nơi giao")

        self.order_tree.column("ten_sp", width=150)
        self.order_tree.column("lay_tai_bai", width=100)
        self.order_tree.column("so_xe", width=80, anchor="center")
        self.order_tree.column("don_vi", width=80, anchor="center")
        self.order_tree.column("so_luong", width=80, anchor="center")
        self.order_tree.column("gia_tai_bai", width=120, anchor="e")
        self.order_tree.column("phi_vc", width=120, anchor="e")
        self.order_tree.column("thanh_tien", width=120, anchor="e")
        self.order_tree.column("noi_giao", width=100)
        
        order_scrollbar = ttk.Scrollbar(order_list_container, orient="vertical", command=self.order_tree.yview)
        self.order_tree.configure(yscrollcommand=order_scrollbar.set)
        
        self.order_tree.grid(row=0, column=0, sticky="nsew")
        order_scrollbar.grid(row=0, column=1, sticky="ns")
        self.order_tree.bind("<<TreeviewSelect>>", self.on_order_item_select)
        self.order_tree.bind("<MouseWheel>", self._on_tree_scroll) # Thêm dòng này

        summary_frame = tk.Frame(right_frame, bg="white", pady=10)
        summary_frame.grid(row=3, column=0, sticky="ew")
        summary_frame.grid_columnconfigure(1, weight=1)

        # --- Phần trạng thái thanh toán ---
        tk.Label(summary_frame, text="Trạng thái:", font=("Segoe UI", 14, "bold"), bg="white").grid(row=1, column=0, sticky="w")

        # Tạo một frame riêng để chứa các Radiobutton và đặt nó ở hàng 1, cột 1
        radio_frame = tk.Frame(summary_frame, bg="white")
        radio_frame.grid(row=1, column=1, sticky="e", padx=10)

        style = ttk.Style()
        style.configure("T.TRadiobutton", font=("Segoe UI", 12))
        style.configure("T.TRadiobutton", background="white")
        style.map("T.TRadiobutton", background=[("active", "white")])

        # Sử dụng ttk.Radiobutton và tag style
        radio_chua_tt = ttk.Radiobutton(
            radio_frame,
            text="Chưa thanh toán",
            variable=self.trang_thai_var,
            value="Chưa thanh toán",
            style="T.TRadiobutton"
        )
        radio_chua_tt.pack(side="left")

        radio_da_tt = ttk.Radiobutton(
            radio_frame,
            text="Đã thanh toán",
            variable=self.trang_thai_var,
            value="Đã thanh toán",
            style="T.TRadiobutton"
        )
        radio_da_tt.pack(side="left", padx=(10, 0))

        # --- Phần tổng cộng ---
        tk.Label(summary_frame, text="Tổng cộng:", font=("Segoe UI", 14, "bold"), bg="white").grid(row=0, column=0, sticky="e")
        self.tong_cong_var = tk.StringVar(value="0 VNĐ")
        tk.Label(summary_frame, textvariable=self.tong_cong_var, font=("Segoe UI", 16, "bold"), bg="white").grid(row=0, column=1, sticky="e", padx=10)


        final_button_frame = tk.Frame(right_frame, bg="white", pady=10)
        final_button_frame.grid(row=4, column=0, sticky="ew")
        
        ctk.CTkButton(final_button_frame, text=" Hủy đơn hàng", command=self.cancel_order,
                  font=("Segoe UI", 12, "bold"), fg_color="#bdc3c7").pack(side="left", expand=True)
        ctk.CTkButton(final_button_frame, text=" Hoàn thành", command=self.complete_order,
                  font=("Segoe UI", 12, "bold"), fg_color="#007bff").pack(side="left", expand=True)

    def on_customer_select(self, event):
        selected_name = self.khach_hang_var.get()
        if selected_name in self.khach_hang_lookup:
            customer_data = self.khach_hang_lookup[selected_name]
            self.current_customer_id = customer_data[0]
            self.ten_kh_label.config(text=customer_data[1])
            self.dia_chi_label.config(text=customer_data[2])
            self.sdt_label.config(text=customer_data[3])
            self.noi_giao_var.set(customer_data[2])
            self.dia_chi_chi_tiet_var.set(customer_data[2])

    def on_item_select(self, event):
        """Xử lý khi một mặt hàng được chọn."""
        selected_display_name = self.mat_hang_var.get()
        
        # Xóa các radio button cũ
        for widget in self.unit_price_options_frame.winfo_children():
            widget.destroy()
        
        self.unit_price_var.set('')
        self.don_vi_var.set('')
        self.don_gia_var.set('')

        if selected_display_name in self.mat_hang_lookup:
            product_data = self.mat_hang_lookup[selected_display_name] # (id_sp, ten_sp, don_vi_tinh, gia_ban, ten_bai)
            units_str = product_data[2] # chuỗi "m3|xe"
            prices_str = product_data[3] # chuỗi "150000|2000000"

            if units_str and prices_str:
                units = units_str.split('|')
                prices = prices_str.split('|')
                
                # Tạo các radio button mới
                for i, (unit, price) in enumerate(zip(units, prices)):
                    formatted_price = f"{int(price):,}".replace(",", ".")
                    option_text = f"{unit} : {formatted_price}"
                    
                    rb = ttk.Radiobutton(self.unit_price_options_frame, text=option_text, variable=self.unit_price_var,
                                         value=option_text, command=self.on_unit_price_select)
                    rb.pack(anchor="w")

                    if i == 0: # Tự động chọn radio button đầu tiên
                        rb.invoke()

        self.calculate_subtotal()

    def on_unit_price_select(self, event=None):
        """Xử lý khi một cặp đơn vị/giá được chọn."""
        selected_pair = self.unit_price_var.get()
        if " : " in selected_pair:
            unit, price_str = selected_pair.split(' : ')
            self.don_vi_var.set(unit.strip())
            self.don_gia_var.set(price_str.strip())
            self.calculate_subtotal()

    def _on_tree_scroll(self, event):
        """
        Xử lý sự kiện cuộn chuột trên Treeview để tăng tốc độ cuộn.
        Bạn có thể thay đổi giá trị của 'scroll_speed' để nhanh hơn hoặc chậm hơn.
        """
        scroll_speed = 5  # Cuộn 5 dòng mỗi lần lăn chuột
        # event.delta < 0 là cuộn xuống, > 0 là cuộn lên (trên Windows)
        self.order_tree.yview_scroll(int(-1 * (event.delta / 120) * scroll_speed), "units")
        self.order_tree.xview_scroll(int(-1 * (event.delta / 120) * scroll_speed), "units")

    def on_order_item_select(self, event):
        """Xử lý khi một item trong đơn hàng được chọn để chỉnh sửa."""
        selected_items = self.order_tree.selection()
        if not selected_items:
            return

        self.editing_item_iid = selected_items[0]
        
        # Tìm item trong list dữ liệu gốc
        item_data = next((item for item in self.current_order_items if item["iid"] == self.editing_item_iid), None)
        if not item_data:
            return

        # Điền thông tin vào form bên trái
        # Tái tạo lại tên hiển thị đầy đủ (có bãi) để chọn đúng trong dropdown
        clean_name = item_data["ten_sp"]
        yard_name = item_data["lay_tai_bai"]
        display_name = f"{clean_name} ({yard_name})" if yard_name and yard_name != " " else clean_name
        self.mat_hang_var.set(display_name)
        self.on_item_select(None) # Tải lại các option đơn vị/giá

        # Tìm và set đúng option đơn vị/giá
        don_gia_formatted = f"{item_data['don_gia']:,}".replace(",", ".")
        unit_price_str = f"{item_data['don_vi']} : {don_gia_formatted}"
        self.unit_price_var.set(unit_price_str)

        # Định dạng giá khi điền vào form
        # Định dạng giá khi điền vào form
        self.don_gia_var.set(don_gia_formatted)
        self.don_vi_var.set(item_data["don_vi"])
        self.so_luong_var.set(item_data["so_luong"])
        self.phi_vc_var.set(str(item_data["phi_vc"] // 1000)) # Chuyển về dạng nghìn đồng
        # THAY ĐỔI: Tách chuỗi "noi_giao" đã gộp để điền vào 2 ô riêng biệt
        full_noi_giao = item_data.get("noi_giao", "")
        noi_giao_part, _, dia_chi_part = full_noi_giao.partition(' - ')
        self.noi_giao_var.set(noi_giao_part)
        self.dia_chi_chi_tiet_var.set(dia_chi_part)
        self.car_var.set(item_data["so_xe"])
        self.calculate_subtotal()

        self.enter_edit_mode()

    def on_don_gia_key_release(self, event=None):
        """Định dạng ô giá và tính lại tổng phụ."""
        self.format_don_gia_entry()
        self.calculate_subtotal()

    def format_don_gia_entry(self, event=None):
        """Định dạng số trong ô đơn giá với dấu chấm."""
        current_value = self.don_gia_var.get()
        # Bỏ các dấu chấm cũ để lấy số thuần
        value_no_dots = current_value.replace(".", "")
        if value_no_dots.isdigit():
            formatted_value = f"{int(value_no_dots):,}".replace(",", ".")
            self.don_gia_var.set(formatted_value)

    def calculate_subtotal(self, event=None):
        try:
            so_luong = self.so_luong_var.get()
            # Bỏ dấu chấm trước khi tính toán
            don_gia_text = self.don_gia_var.get().replace(".", "")
            don_gia = int(don_gia_text) if don_gia_text.isdigit() else 0
            phi_vc_text = self.phi_vc_var.get()
            phi_vc = int(phi_vc_text) * 1000 if phi_vc_text else 0
            
            thanh_tien = (don_gia * so_luong) + phi_vc
            self.thanh_tien_var.set(f"{thanh_tien:,.0f} VNĐ".replace(",", "."))

        except (ValueError, tk.TclError):
            self.thanh_tien_var.set("0 VNĐ")
    
    def add_item_to_order(self):
        # Nếu đang trong chế độ chỉnh sửa, gọi hàm cập nhật và thoát
        if self.editing_item_iid:
            self.update_order_item()
            return
        if not self.current_customer_id:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn khách hàng trước.")
            return
            
        selected_item_name = self.mat_hang_var.get()
        if not selected_item_name:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn một mặt hàng.")
            return
        
        selected_car_plate = self.car_var.get()
        if not selected_car_plate:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn xe.")
            return

        try:
            so_luong = self.so_luong_var.get()
            if so_luong <= 0:
                raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showwarning("Lỗi nhập liệu", "Số lượng phải là một số nguyên dương.")
            return
        
        try:
            # Bỏ dấu chấm trước khi chuyển sang số nguyên
            don_gia = int(self.don_gia_var.get().replace(".", ""))
        except (ValueError, tk.TclError):
            messagebox.showwarning("Lỗi nhập liệu", "Đơn giá không hợp lệ.")
            return

        phi_vc_text = self.phi_vc_var.get()
        phi_vc = int(phi_vc_text) * 1000 if phi_vc_text else 0

        item_data_lookup = self.mat_hang_lookup[selected_item_name]
        item_id, real_ten_sp, _, _, ten_bai, id_bai = item_data_lookup
        
        car_data_lookup = self.car_lookup.get(selected_car_plate)
        id_xe = car_data_lookup[0] if car_data_lookup else None

        don_vi = self.don_vi_var.get()
        noi_giao = self.noi_giao_var.get()
        dia_chi_chi_tiet = self.dia_chi_chi_tiet_var.get()
        thanh_tien = (don_gia * so_luong) + phi_vc
        full_noi_giao = f"{noi_giao} - {dia_chi_chi_tiet}"
        # --- Logic gộp sản phẩm ---
        # Tìm xem có sản phẩm nào cùng id, cùng giá và cùng nơi giao đã tồn tại không
        existing_item = next((item for item in self.current_order_items if 
                              item["id"] == item_id and item["don_gia"] == don_gia and 
                              item["noi_giao"] == noi_giao and item["so_xe"] == selected_car_plate), None)

        if existing_item:
            # Nếu có, cập nhật số lượng, phí vc và thành tiền
            # Lưu ý: không gộp các sản phẩm đi xe khác nhau hoặc giao đến nơi khác nhau
            existing_item["so_luong"] += so_luong
            existing_item["phi_vc"] += phi_vc
            existing_item["thanh_tien"] = (existing_item["don_gia"] * existing_item["so_luong"]) + existing_item["phi_vc"]
            
            # Cập nhật dòng tương ứng trong Treeview
            self.order_tree.item(existing_item["iid"], values=( # Sửa thứ tự
                existing_item["ten_sp"], # ten_sp
                existing_item["lay_tai_bai"], # lay_tai_bai
                existing_item["so_xe"], # so_xe
                existing_item["don_vi"], # don_vi
                existing_item["so_luong"], # so_luong
                f"{existing_item['don_gia']:,}".replace(",", "."), # gia_tai_bai
                f"{existing_item['phi_vc']:,}".replace(",", "."), # phi_vc
                f"{existing_item['thanh_tien']:,}".replace(",", "."), # thanh_tien
                existing_item["noi_giao"] # noi_giao
            ))
        else:
            # Nếu không, thêm như một sản phẩm mới
            iid = f"I{len(self.current_order_items):03d}" # Tạo IID duy nhất
            order_item = {
                "iid": iid, "id": item_id, 
                "ten_sp": real_ten_sp, 
                "so_xe": selected_car_plate,
                "id_xe": id_xe,
                "lay_tai_bai": ten_bai or " ",
                "id_bai": id_bai,
                "don_vi": don_vi,
                "so_luong": so_luong, 
                "don_gia": don_gia, 
                "phi_vc": phi_vc,
                "noi_giao": full_noi_giao, 
                "dia_chi_chi_tiet": dia_chi_chi_tiet,
                "thanh_tien": thanh_tien
            }
            self.current_order_items.append(order_item)
            
            self.order_tree.insert("", "end", iid=iid, values=( # Sửa thứ tự
                real_ten_sp, # ten_sp
                ten_bai or " ", # lay_tai_bai
                selected_car_plate, # so_xe
                don_vi, # don_vi
                so_luong, # so_luong
                f"{don_gia:,.0f}".replace(",", "."), # gia_tai_bai
                f"{phi_vc:,.0f}".replace(",", "."), # phi_vc
                f"{thanh_tien:,.0f}".replace(",", "."), # thanh_tien
                full_noi_giao # noi_giao
            ))
        
        self.update_total_amount()
        self.reset_left_form()

    def update_order_item(self):
        """Cập nhật một item đang có trong đơn hàng."""
        if not self.editing_item_iid:
            return

        # Tìm item trong list dữ liệu
        item_to_update = next((item for item in self.current_order_items if item["iid"] == self.editing_item_iid), None)
        if not item_to_update:
            return

        # Lấy dữ liệu mới từ form
        try:
            so_luong = self.so_luong_var.get()
            if so_luong <= 0: raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showwarning("Lỗi nhập liệu", "Số lượng phải là một số nguyên dương.")
            return
        
        try:
            # Bỏ dấu chấm trước khi chuyển sang số nguyên
            don_gia = int(self.don_gia_var.get().replace(".", ""))
        except (ValueError, tk.TclError):
            messagebox.showwarning("Lỗi nhập liệu", "Đơn giá không hợp lệ.")
            return

        phi_vc_text = self.phi_vc_var.get()
        phi_vc = int(phi_vc_text) * 1000 if phi_vc_text else 0
        noi_giao = self.noi_giao_var.get()
        dia_chi_chi_tiet = self.dia_chi_chi_tiet_var.get()
        full_noi_giao = f"{noi_giao} - {dia_chi_chi_tiet}"
        so_xe = self.car_var.get()
        id_xe = self.car_lookup.get(so_xe)[0] if self.car_lookup.get(so_xe) else None
        thanh_tien = (don_gia * so_luong) + phi_vc

        # Cập nhật dữ liệu trong list
        item_to_update.update({
            "don_gia": don_gia,
            "don_vi": self.don_vi_var.get(),
            "so_luong": so_luong, 
            "phi_vc": phi_vc, 
            "noi_giao": noi_giao, 
            "dia_chi_chi_tiet": dia_chi_chi_tiet,
            "so_xe": so_xe,
            "thanh_tien": thanh_tien
        })
        item_to_update['noi_giao'] = full_noi_giao

        # Cập nhật dòng trong Treeview
        self.order_tree.item(self.editing_item_iid, values=( # Sửa thứ tự
            item_to_update["ten_sp"], # ten_sp
            item_to_update["lay_tai_bai"], # lay_tai_bai
            item_to_update["so_xe"], # so_xe
            item_to_update["don_vi"], # don_vi
            so_luong, # so_luong
            f"{don_gia:,.0f}".replace(",", "."), # gia_tai_bai
            f"{phi_vc:,.0f}".replace(",", "."), # phi_vc
            f"{thanh_tien:,.0f}".replace(",", "."), # thanh_tien
            item_to_update["noi_giao"] # noi_giao
        ))
        
        self.update_total_amount()
        self.exit_edit_mode()

    def enter_edit_mode(self):
        """Chuyển giao diện sang chế độ chỉnh sửa."""
        self.add_button.configure(text="Cập nhật mặt hàng", fg_color="#f39c12")
        self.cancel_edit_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        self.mat_hang_dropdown.config(state="disabled") # Không cho đổi mặt hàng khi sửa

    def exit_edit_mode(self):
        """Thoát khỏi chế độ chỉnh sửa, quay về chế độ thêm mới."""
        self.editing_item_iid = None
        if self.order_tree.selection():
            self.order_tree.selection_remove(self.order_tree.selection()) # Bỏ chọn dòng
        self.add_button.configure(text=" Thêm vào đơn hàng", fg_color="#27ae60")
        self.cancel_edit_button.grid_forget()
        self.mat_hang_dropdown.config(state="readonly")
        self.reset_left_form()

    def cancel_edit(self):
        """Hủy thao tác chỉnh sửa."""
        self.exit_edit_mode()

    def update_total_amount(self):
        total = sum(item['thanh_tien'] for item in self.current_order_items)
        self.tong_cong_var.set(f"{total:,.0f} VNĐ".replace(",", "."))
        
    def reset_left_form(self):
        self.mat_hang_var.set("")
        self.on_item_select(None) # Gọi để xóa các radio button và reset các biến
        self.don_vi_var.set("")
        self.don_gia_var.set("")
        self.so_luong_var.set(1)
        self.phi_vc_var.set("")
        self.thanh_tien_var.set("0 VNĐ")
        self.car_var.set("")
        # Không reset nơi giao vì có thể khách hàng muốn giao nhiều món đến cùng một chỗ

    def cancel_order(self, show_confirmation=True):
        """Hủy đơn hàng. Có thể bỏ qua hộp thoại xác nhận."""
        # Nếu cần xác nhận, hỏi người dùng. Nếu không, mặc định là đồng ý hủy.
        should_proceed = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn hủy đơn hàng này?") if show_confirmation else True

        if should_proceed:
            self._clear_order_form()

    def _clear_order_form(self):
        """Xóa toàn bộ thông tin trên form đơn hàng một cách lặng lẽ."""
        self.current_order_items.clear()
        for i in self.order_tree.get_children():
            self.order_tree.delete(i)
        self.update_total_amount()
        self.khach_hang_var.set("")
        self.ten_kh_label.config(text="...")
        self.dia_chi_label.config(text="...")
        self.sdt_label.config(text="...")
        self.current_customer_id = None
        self.noi_giao_var.set("")
        self.dia_chi_chi_tiet_var.set("")
        self.trang_thai_var.set("Chưa thanh toán") # Reset trạng thái
        self.exit_edit_mode() # Đảm bảo thoát khỏi chế độ sửa
            
    def complete_order(self):
        if not self.current_customer_id:
            messagebox.showerror("Lỗi", "Chưa có thông tin khách hàng.")
            return
        if not self.current_order_items:
            messagebox.showerror("Lỗi", "Chưa có mặt hàng nào trong đơn.")
            return
        
        # Thu thập dữ liệu để gửi cho controller
        ngay_mua = self.ngay_tao_entry.get_date()
        tong_tien_str = self.tong_cong_var.get().replace(" VNĐ", "").replace(".", "")
        tong_tien = int(tong_tien_str)
        trang_thai = self.trang_thai_var.get()

        # Gọi controller để xử lý việc lưu hóa đơn
        success, message = self.invoice_controller.create_invoice(
            id_kh=self.current_customer_id,
            ngay_mua=ngay_mua,
            tong_tien=tong_tien,
            trang_thai=trang_thai,
            items=self.current_order_items
        )

        if success:
            # Gọi hàm xóa form mà không hiển thị thông báo xác nhận
            self._clear_order_form()
            # Thông báo cho người dùng biết đã hoàn thành