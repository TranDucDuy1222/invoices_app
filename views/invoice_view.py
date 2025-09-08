import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import date
from tkcalendar import DateEntry
import customtkinter as ctk

# Dữ liệu giả lập (bạn sẽ thay thế bằng cách truy vấn từ database)
# Dữ liệu khách hàng: (id, ten, dia_chi, sdt, loai_kh)
khach_hang_data = [
    (1, 'Nguyễn Thành Công', '123 Đường ABC, Quận 1, TP.HCM', '0708662504', 'Vựa'),
    (2, 'Nguyễn Ngọc Hưng', '456 Đường XYZ, Quận 2, TP.HCM', '0708662704', 'Khách lẻ'),
    (3, 'Trần Đức Duy', '789 Đường KLM, Quận 3, TP.HCM', '0708552454', 'Khách lẻ')
]

# Dữ liệu mặt hàng: (id, ten, don_vi, gia)
mat_hang_data = [
    (1, "Đá bụi", "Xe", 1200000),
    (2, "Đá mi sàn", "Xe", 350000),
    (3, "Xà bần", "Xe", 2800000),
    (4, "Cát san lấp", "Xe", 80000),
]

class TaoHoaDonView(tk.Frame):
    def __init__(self, parent, root_window):
        super().__init__(parent, bg="white")
        
        self.root_window = root_window
        
        # --- Biến lưu trữ dữ liệu ---
        self.khach_hang_lookup = {kh[1]: kh for kh in khach_hang_data}
        self.mat_hang_lookup = {mh[1]: mh for mh in mat_hang_data}
        
        self.current_order_items = []
        self.current_customer_id = None
        
        # --- Đăng ký hàm kiểm tra nhập liệu ---
        self.vcmd = (self.register(self.validate_integer_input), '%P')
        
        self.create_widgets()

    def validate_integer_input(self, P):
        """Kiểm tra xem giá trị mới có phải là số nguyên hay không."""
        if P == "" or P.isdigit():
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
        tk.Label(left_frame, text="Ngày mua:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=1, column=0, sticky="w", pady=5)
        self.ngay_tao_entry = DateEntry(left_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy', font=("Segoe UI", 10))
        self.ngay_tao_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        tk.Label(left_frame, text="Khách hàng:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=2, column=0, sticky="w", pady=5)
        self.khach_hang_var = tk.StringVar()
        kh_names = [kh[1] for kh in khach_hang_data]
        self.khach_hang_dropdown = ttk.Combobox(left_frame, textvariable=self.khach_hang_var, values=kh_names, state="readonly", font=("Segoe UI", 10))
        self.khach_hang_dropdown.grid(row=2, column=1, sticky="ew", pady=5)
        self.khach_hang_dropdown.bind("<<ComboboxSelected>>", self.on_customer_select)
        
        tk.Label(left_frame, text="Mặt hàng:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=3, column=0, sticky="w", pady=5)
        self.mat_hang_var = tk.StringVar()
        mh_names = [mh[1] for mh in mat_hang_data]
        self.mat_hang_dropdown = ttk.Combobox(left_frame, textvariable=self.mat_hang_var, values=mh_names, state="readonly", font=("Segoe UI", 10))
        self.mat_hang_dropdown.grid(row=3, column=1, sticky="ew", pady=5)
        self.mat_hang_dropdown.bind("<<ComboboxSelected>>", self.on_item_select)

        tk.Label(left_frame, text="Đơn vị:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=4, column=0, sticky="w", pady=5)
        self.don_vi_var = tk.StringVar(value="Xe")
        tk.Entry(left_frame, textvariable=self.don_vi_var, state="readonly", font=("Segoe UI", 10)).grid(row=4, column=1, sticky="ew", pady=5)

        tk.Label(left_frame, text="Số lượng:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=5, column=0, sticky="w", pady=5)
        self.so_luong_var = tk.IntVar(value=1)
        self.so_luong_entry = tk.Entry(left_frame, textvariable=self.so_luong_var, font=("Segoe UI", 10), validate="key", validatecommand=self.vcmd)
        self.so_luong_entry.grid(row=5, column=1, sticky="ew", pady=5)
        self.so_luong_entry.bind("<KeyRelease>", self.calculate_subtotal)

        tk.Label(left_frame, text="Phí vận chuyển:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=6, column=0, sticky="w", pady=5)
        phi_vc_container = tk.Frame(left_frame, bg="#f7f9fc")
        phi_vc_container.grid(row=6, column=1, sticky="ew", pady=5)
        phi_vc_container.grid_columnconfigure(0, weight=1)
        self.phi_vc_var = tk.StringVar(value="")
        self.phi_vc_entry = tk.Entry(phi_vc_container, textvariable=self.phi_vc_var, font=("Segoe UI", 10), validate="key", validatecommand=self.vcmd, justify="right")
        self.phi_vc_entry.grid(row=0, column=0, sticky="ew")
        self.phi_vc_entry.bind("<KeyRelease>", self.calculate_subtotal)
        tk.Label(phi_vc_container, text=" 000 VNĐ", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=0, column=1, sticky="w")
        
        tk.Label(left_frame, text="Nơi giao:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=7, column=0, sticky="w", pady=5)
        self.noi_giao_var = tk.StringVar()
        tk.Entry(left_frame, textvariable=self.noi_giao_var, font=("Segoe UI", 10)).grid(row=7, column=1, sticky="ew", pady=5)

        tk.Label(left_frame, text="Thành tiền:", font=("Segoe UI", 10, "bold"), bg="#f7f9fc").grid(row=8, column=0, sticky="w", pady=5)
        self.thanh_tien_var = tk.StringVar(value="0 VNĐ")
        tk.Label(left_frame, textvariable=self.thanh_tien_var, font=("Segoe UI", 12, "bold"), bg="#f7f9fc").grid(row=8, column=1, sticky="w", pady=5)

        add_button = ctk.CTkButton(left_frame, text=" Thêm vào đơn hàng", command=self.add_item_to_order, 
                               font=("Segoe UI", 12, "bold"), fg_color="#27ae60",
                               compound="left")
        add_button.grid(row=9, column=0, columnspan=2, pady=20)

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

        cols = ("ten_sp", "don_vi", "so_luong", "don_gia", "thanh_tien")
        self.order_tree = ttk.Treeview(order_list_container, columns=cols, show="headings")
        self.order_tree.heading("ten_sp", text="Tên mặt hàng")
        self.order_tree.heading("don_vi", text="Đơn vị")
        self.order_tree.heading("so_luong", text="Số lượng")
        self.order_tree.heading("don_gia", text="Đơn giá")
        self.order_tree.heading("thanh_tien", text="Thành tiền")

        self.order_tree.column("so_luong", width=80, anchor="center")
        self.order_tree.column("don_gia", width=120, anchor="e")
        self.order_tree.column("thanh_tien", width=120, anchor="e")
        
        order_scrollbar = ttk.Scrollbar(order_list_container, orient="vertical", command=self.order_tree.yview)
        self.order_tree.configure(yscrollcommand=order_scrollbar.set)
        
        self.order_tree.grid(row=0, column=0, sticky="nsew")
        order_scrollbar.grid(row=0, column=1, sticky="ns")

        summary_frame = tk.Frame(right_frame, bg="white", pady=10)
        summary_frame.grid(row=3, column=0, sticky="ew")
        summary_frame.grid_columnconfigure(1, weight=1)

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

    def on_item_select(self, event):
        self.calculate_subtotal()

    def calculate_subtotal(self, event=None):
        try:
            so_luong = self.so_luong_var.get()
            phi_vc_text = self.phi_vc_var.get()
            phi_vc = int(phi_vc_text) * 1000 if phi_vc_text else 0
            selected_item_name = self.mat_hang_var.get()
            
            if selected_item_name in self.mat_hang_lookup:
                don_gia = self.mat_hang_lookup[selected_item_name][3]
                thanh_tien = (don_gia * so_luong) + phi_vc
                self.thanh_tien_var.set(f"{thanh_tien:,.0f} VNĐ".replace(",", "."))
            else:
                self.thanh_tien_var.set("0 VNĐ")
        except (ValueError, tk.TclError):
            self.thanh_tien_var.set("0 VNĐ")
    
    def add_item_to_order(self):
        if not self.current_customer_id:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn khách hàng trước.")
            return
            
        selected_item_name = self.mat_hang_var.get()
        if not selected_item_name:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn một mặt hàng.")
            return

        try:
            so_luong = self.so_luong_var.get()
            if so_luong <= 0:
                raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showwarning("Lỗi nhập liệu", "Số lượng phải là một số nguyên dương.")
            return

        phi_vc_text = self.phi_vc_var.get()
        phi_vc = int(phi_vc_text) * 1000 if phi_vc_text else 0
        
        item_data = self.mat_hang_lookup[selected_item_name]
        item_id, don_vi, don_gia = item_data[0], item_data[2], item_data[3]
        noi_giao = self.noi_giao_var.get()
        thanh_tien = (don_gia * so_luong) + phi_vc

        order_item = {
            "id": item_id, "ten_sp": selected_item_name, "don_vi": don_vi,
            "so_luong": so_luong, "don_gia": don_gia, "phi_vc": phi_vc,
            "noi_giao": noi_giao, "thanh_tien": thanh_tien
        }
        
        self.current_order_items.append(order_item)
        
        self.order_tree.insert("", "end", values=(
            selected_item_name, don_vi, so_luong, 
            f"{don_gia:,.0f}", f"{thanh_tien:,.0f}"
        ))
        
        self.update_total_amount()
        self.reset_left_form()

    def update_total_amount(self):
        total = sum(item['thanh_tien'] for item in self.current_order_items)
        self.tong_cong_var.set(f"{total:,.0f} VNĐ".replace(",", "."))
        
    def reset_left_form(self):
        self.mat_hang_var.set("")
        self.so_luong_var.set(1)
        self.phi_vc_var.set("")
        self.thanh_tien_var.set("0 VNĐ")

    def cancel_order(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn hủy đơn hàng này?"):
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
            self.reset_left_form()
            
    def complete_order(self):
        if not self.current_customer_id:
            messagebox.showerror("Lỗi", "Chưa có thông tin khách hàng.")
            return
        if not self.current_order_items:
            messagebox.showerror("Lỗi", "Chưa có mặt hàng nào trong đơn.")
            return
            
        messagebox.showinfo("Thành công", "Đã tạo hóa đơn thành công! (logic lưu DB sẽ ở đây)")
        self.cancel_order()