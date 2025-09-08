import tkinter as tk
from tkinter import ttk
from tkinter import messagebox # Import messagebox để hiện thông báo
import customtkinter as ctk

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
        # self.loai_kh_var = tk.StringVar(value="Khách lẻ") # Đặt giá trị mặc định

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
        # loai_kh_frame = tk.Frame(form_frame, bg="#f7f9fc")
        # loai_kh_frame.pack(fill="x", pady=5)

        # loai_kh_label = tk.Label(loai_kh_frame, text="Loại KH:", width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10))
        # loai_kh_label.pack(side="left")

        # radio_container = tk.Frame(loai_kh_frame, bg="#f7f9fc")
        # radio_container.pack(side="left")

        # tk.Radiobutton(radio_container, text="Vựa", variable=self.loai_kh_var, value="Vựa", bg="#f7f9fc", font=("Segoe UI", 10), activebackground="#f7f9fc").pack(side="left", padx=5)
        # tk.Radiobutton(radio_container, text="Khách lẻ", variable=self.loai_kh_var, value="Khách lẻ", bg="#f7f9fc", font=("Segoe UI", 10), activebackground="#f7f9fc").pack(side="left", padx=5)

        #------ Frame chứa các nút bấm ------
        button_frame = tk.Frame(right_frame, bg="#f7f9fc")
        button_frame.pack(pady=30, padx=20, fill="x")
        
        ctk.CTkButton(button_frame, text="Thêm", command=self.add_customer_window, corner_radius=10, fg_color="#27ae60", font=("Segoe UI", 11), width=100).pack(side="left", expand=True, pady=5)
        ctk.CTkButton(button_frame, text="Sửa", command=self.update_customer_window, corner_radius=10, fg_color="#f39c12", font=("Segoe UI", 11), width=100).pack(side="left", expand=True, pady=5, padx=10)
        ctk.CTkButton(button_frame, text="Xóa", command=self.delete_customer, corner_radius=10, fg_color="#e74c3c", font=("Segoe UI", 11), width=100).pack(side="left", expand=True, pady=5)

    def set_customer_list(self, data):
        """
        Xóa dữ liệu cũ trong bảng và hiển thị dữ liệu mới.
        Phương thức này sẽ được gọi bởi Controller.
        """
        for item in self.tree_kh.get_children():
            self.tree_kh.delete(item)
        for item in data:
            self.tree_kh.insert("", "end", values=item)

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

    def add_customer_window(self):
        # Tạo cửa sổ thêm mặt hàng
        add_window = tk.Toplevel(self.root_window)
        add_window.title("Thêm khách hàng mới")
        add_window.geometry("400x250")
        add_window.resizable(False, False) # Không cho phép thay đổi kích thước
        add_window.configure(bg="#f7f9fc")
        add_window.transient(self.root_window)# Cửa sổ luôn ở trên cùng
        add_window.grab_set()

        # Frame chứa form 
        form_add = tk.Frame(add_window, bg="#f7f9fc", padx=20, pady=20)
        form_add.pack(expand=True, fill="both")

        add_fields = {
        "Khách hàng:": tk.StringVar(),
        "Địa chỉ:": tk.StringVar(),
        "Số điện thoại:": tk.StringVar(),
        }

        for label_text, var in add_fields.items():
            row = tk.Frame(form_add, bg="#f7f9fc")
            row.pack(fill="x", pady=8)

            label = tk.Label(row, text=label_text, width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10))
            label.pack(side="left")

            entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 10))
            entry.pack(side="left", expand=True, fill="x") 
            
        # Hàm lưu khách hàng mới
        def save_new_customer():
            ten_kh = add_fields["Khách hàng:"].get().strip()
            dia_chi = add_fields["Địa chỉ:"].get().strip()
            so_dien_thoai = add_fields["Số điện thoại:"].get().strip()

            # Gọi phương thức add_item từ controller
            self.controller.add_customer(ten_kh, dia_chi, so_dien_thoai)
            add_window.destroy()

        # Nút lưu và hủy
        button_frame_add = tk.Frame(form_add, bg="#f7f9fc")
        button_frame_add.pack(fill="x", pady=(20, 0))

        add_btn = ctk.CTkButton(button_frame_add, text="Lưu", command=save_new_customer, fg_color="#2ecc71", font=("Segoe UI", 10, "bold"), width=100)
        add_btn.pack(side="right", padx=5)

        cancel_btn = ctk.CTkButton(button_frame_add, text="Hủy", command=add_window.destroy, fg_color="#e74c3c", font=("Segoe UI", 10, "bold"), width=100)
        cancel_btn.pack(side="right")
    
    def update_customer_window(self):
        # Kiểm tra và lấy thông tin mặt hàng
        selected_id = self.form_fields_kh["ID:"].get()
        if not selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một bãi để sửa!")
            return

        # Lấy thông tin hiện tại từ các ô Entry của form chính
        current_name = self.form_fields_kh["Khách hàng:"].get()
        current_address = self.form_fields_kh["Địa chỉ:"].get()
        current_sdt = self.form_fields_kh["Số điện thoại:"].get()
        
        # Tạo cửa sổ chức năng sửa mặt hàng
        edit_window = tk.Toplevel(self.root_window)
        edit_window.title(f"Sửa thông tin khách hàng")
        edit_window.geometry("400x250")
        edit_window.resizable(False, False)
        edit_window.configure(bg="#f7f9fc")
        
        edit_window.transient(self.root_window)
        edit_window.grab_set()

        # Tạo form trong cửa sổ
        form_edit = tk.Frame(edit_window, bg="#f7f9fc", padx=20, pady=20)
        form_edit.pack(expand=True, fill="both")

        fields_to_edit = {
            "Khách hàng:": tk.StringVar(value=current_name),
            "Địa chỉ:": tk.StringVar(value=current_address),
            "Số điện thoại:": tk.StringVar(value=current_sdt),
        } 
        
        for label_text, var in fields_to_edit.items():
            row = tk.Frame(form_edit, bg="#f7f9fc")
            row.pack(fill="x", pady=8)
            label = tk.Label(row, text=label_text, width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10))
            label.pack(side="left")
            entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 10))
            entry.pack(side="left", expand=True, fill="x")
        
        def save_customer_change():
            # selected_id = self.form_fields_y["ID:"].get()
            ten_kh = fields_to_edit["Khách hàng:"].get().strip()
            dia_chi = fields_to_edit["Địa chỉ:"].get().strip()
            so_dien_thoai = fields_to_edit["Số điện thoại:"].get().strip()

            # Gọi phương thức add_item từ controller
            self.controller.update_customer(selected_id, ten_kh, dia_chi, so_dien_thoai)
            edit_window.destroy()

            for item in self.tree_kh.get_children():
                if self.tree_kh.item(item, "values")[0] == selected_id:
                    self.tree_kh.selection_set(item)
                    self.tree_kh.focus(item)
                    self.tree_kh.see(item)
                    self.on_item_select(None)  # Gọi lại hàm cập nhật chi tiết
                    break

        # Tạo nút lưu và nút hủy
        button_frame_edit = tk.Frame(form_edit, bg="#f7f9fc")
        button_frame_edit.pack(fill="x", pady=(20, 0))

        edit_btn = ctk.CTkButton(button_frame_edit, text="Lưu", command=save_customer_change, fg_color="#f39c12", font=("Segoe UI", 10, "bold"), width=100)
        edit_btn.pack(side="right", padx=5)

        cancel_btn = ctk.CTkButton(button_frame_edit, text="Hủy", command=edit_window.destroy, fg_color="#e74c3c", font=("Segoe UI", 10, "bold"), width=100)
        cancel_btn.pack(side="right")
    
    def delete_customer(self):
        selected_id = self.form_fields_kh["ID:"].get()
        selected_tree_item = self.tree_kh.selection()
        if not selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một khách hàng để xóa!")
            return
        
        confirm = messagebox.askyesno("Xác nhận xóa", "Bạn có chắc chắn muốn xóa khách hàng này?")
        if confirm:
            # Gọi phương thức delete_item từ controller
            self.controller.delete_customer(selected_id)
            # Xóa thông tin trong form
            self.tree_kh.delete(selected_tree_item)
            self.clear_details_form()

    def clear_details_form(self):
        """Xóa toàn bộ nội dung trong các ô Entry của form chi tiết."""
        for var in self.form_fields_kh.values():
            var.set("")