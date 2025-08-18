import tkinter as tk
from tkinter import ttk
from tkinter import messagebox # Import messagebox để hiện thông báo

# Thay thế dữ liệu từ database
khach_hang_data = [
    (1, 'Nguyễn Thành Công', 'Thành Phố Hồ Chí Minh', '0708662504'),
    (2, 'Nguyễn Ngọc Hưng', 'Thành Phố Hồ Chí Minh', '0708662704'),
    (3, 'Trần Đức Duy', 'Thành Phố Hồ Chí Minh', '0708552454')
]
class KhachHangView(tk.Frame):
    def __init__(self, parent, root_window):
        super().__init__(parent, bg="white")
        
        self.root_window = root_window
        self.create_widgets()

    def create_widgets(self):
        #------ Bảng danh sách khách hàng ------
        left_frame = tk.Frame(self, bg='white')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(left_frame, text="Danh sách khách hàng", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=(0, 10), anchor="w")

        # Thêm cột 'loai_kh' vào columns
        columns = ("id", "ten_khach_hang", "dia_chi", "sdt")
        self.tree_kh = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse")

        self.tree_kh.heading("id", text="ID")
        self.tree_kh.heading("ten_khach_hang", text="Tên khách hàng")
        self.tree_kh.heading("dia_chi", text="Địa chỉ")
        self.tree_kh.heading("sdt", text="Số điện thoại")

        self.tree_kh.column("id", width=50, anchor="center")
        self.tree_kh.column("ten_khach_hang", width=200)
        self.tree_kh.column("dia_chi", width=200)
        self.tree_kh.column("sdt", width=120, anchor="w")

        for item in khach_hang_data:
            self.tree_kh.insert("", "end", values=item)

        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree_kh.yview)
        self.tree_kh.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree_kh.pack(expand=True, fill="both")
        
        # Gán sự kiện chọn dòng
        self.tree_kh.bind("<<TreeviewSelect>>", self.on_customer_select)

        #------ Form thông tin chi tiết ------
        right_frame = tk.Frame(self, bg="#f7f9fc", width=350)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)

        tk.Label(right_frame, text="Thông tin khách hàng", font=("Segoe UI", 16, "bold"), bg="#f7f9fc").pack(pady=20, anchor="w", padx=20)

        # Lưu các biến thành thuộc tính của self
        self.form_fields_kh = {
            "ID:": tk.StringVar(),
            "Khách hàng:": tk.StringVar(),
            "Địa chỉ:": tk.StringVar(),
            "Số điện thoại:": tk.StringVar()
        }
        self.loai_kh_var = tk.StringVar(value="Khách lẻ") # Đặt giá trị mặc định

        form_frame = tk.Frame(right_frame, bg="#f7f9fc")
        form_frame.pack(fill="x", padx=20)

        for label_text, var in self.form_fields_kh.items():
            row = tk.Frame(form_frame, bg="#f7f9fc")
            row.pack(fill="x", pady=5)
            
            label = tk.Label(row, text=label_text, width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10))
            label.pack(side="left")
            
            entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 10))
            if label_text == "ID:":
                entry.config(state="readonly", relief="flat", bg="#e9ecef")
            entry.pack(side="left", expand=True, fill="x")

        # --- Phần chọn Loại khách hàng ---
        loai_kh_frame = tk.Frame(form_frame, bg="#f7f9fc")
        loai_kh_frame.pack(fill="x", pady=5)

        loai_kh_label = tk.Label(loai_kh_frame, text="Loại KH:", width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10))
        loai_kh_label.pack(side="left")

        radio_container = tk.Frame(loai_kh_frame, bg="#f7f9fc")
        radio_container.pack(side="left")

        tk.Radiobutton(radio_container, text="Vựa", variable=self.loai_kh_var, value="Vựa", bg="#f7f9fc", font=("Segoe UI", 10), activebackground="#f7f9fc").pack(side="left", padx=5)
        tk.Radiobutton(radio_container, text="Khách lẻ", variable=self.loai_kh_var, value="Khách lẻ", bg="#f7f9fc", font=("Segoe UI", 10), activebackground="#f7f9fc").pack(side="left", padx=5)

        #------ Frame chứa các nút bấm ------
        button_frame = tk.Frame(right_frame, bg="#f7f9fc")
        button_frame.pack(pady=30, padx=20, fill="x")
        
        tk.Button(button_frame, text="Thêm", bg="#2ecc71", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", width=10).pack(side="left", expand=True, pady=5)
        tk.Button(button_frame, text="Sửa", bg="#f39c12", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", width=10).pack(side="left", expand=True, pady=5, padx=10)
        tk.Button(button_frame, text="Xóa", bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", width=10).pack(side="left", expand=True, pady=5)

    def on_customer_select(self, event):
        # Lấy dòng được chọn
        selected_customer = self.tree_kh.selection()
        if not selected_customer:
            return

        item_id = selected_customer[0]
        # Lấy dữ liệu từ dòng được chọn
        values = self.tree_kh.item(item_id, "values")
        
        # Cập nhật dữ liệu lên các ô Entry
        self.form_fields_kh["ID:"].set(values[0])
        self.form_fields_kh["Khách hàng:"].set(values[1])
        self.form_fields_kh["Địa chỉ:"].set(values[2])
        self.form_fields_kh["Số điện thoại:"].set(values[3])