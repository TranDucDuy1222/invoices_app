import tkinter as tk
from tkinter import ttk
from tkinter import messagebox # Import messagebox để hiện thông báo
import sqlite3
import customtkinter as ctk
from views.config import db_path

class MatHangView(tk.Frame):
    def __init__(self, parent, root_window):
        super().__init__(parent, bg="white")
        
        self.root_window = root_window # Lưu lại cửa sổ gốc để dùng cho Toplevel
        
        # Gọi phương thức để tạo tất cả các widget
        self.create_widgets()

    # Phương thức để tạo các widget trong frame 
    def create_widgets(self):
        #------ Bảng mặt hàng ------
        left_frame = tk.Frame(self, bg="white")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(left_frame, text="Danh sách mặt hàng", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=(0, 10), anchor="w")
        style = ttk.Style()
        # Cấu hình style cho Treeview để mỗi hàng cao 40px, đủ cho 2 dòng text
        style.configure("Treeview", rowheight=40, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        columns = ("id", "ten_mat_hang", "don_vi", "gia", "ten_bai")
        self.tree_mh = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse")

        self.tree_mh.heading("id", text="ID")
        self.tree_mh.heading("ten_mat_hang", text="Tên mặt hàng")
        self.tree_mh.heading("don_vi", text="Đơn vị")
        self.tree_mh.heading("gia", text="Giá")

        self.tree_mh.column("id", width=50, anchor="center")
        self.tree_mh.column("ten_mat_hang", width=250)
        self.tree_mh.column("don_vi", width=100, anchor="center")
        self.tree_mh.column("gia", width=120, anchor="e")
        self.tree_mh.column("ten_bai", width=0, stretch=False)


        # for item in sample_data:
        #     self.tree_mh.insert("", "end", values=item)
        # Thanh cuộn
        scrollbar_mh = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree_mh.yview)
        self.tree_mh.configure(yscrollcommand=scrollbar_mh.set)
        scrollbar_mh.pack(side="right", fill="y")
        self.tree_mh.pack(expand=True, fill="both")
        
        # Gán sự kiện chọn dòng
        self.tree_mh.bind("<<TreeviewSelect>>", self.on_item_select)

        # Form thông tin chi tiết
        right_frame = tk.Frame(self, bg="#f7f9fc", width=350)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)

        tk.Label(right_frame, text="Thông tin chi tiết", font=("Segoe UI", 16, "bold"), bg="#f7f9fc").pack(pady=20, anchor="w", padx=20)

        self.form_fields_mh = {
            "ID:": tk.StringVar(),
            "Tên mặt hàng:": tk.StringVar(),
            "Đơn vị:": tk.StringVar(),
            "Giá:": tk.StringVar(),
            "Bãi:": tk.StringVar()
        }

        form_frame = tk.Frame(right_frame, bg="#f7f9fc")
        form_frame.pack(fill="x", padx=20)

        for label_text, var in self.form_fields_mh.items():
            row = tk.Frame(form_frame, bg="#f7f9fc")
            row.pack(fill="x", pady=5)
            
            label = tk.Label(row, text=label_text, width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10))
            label.pack(side="left")
            
            entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 10))
            if label_text == "ID:":
                entry.config(state="readonly", relief="flat", bg="#e9ecef")
            entry.pack(side="left", expand=True, fill="x")  

        #------ Frame chứa các nút bấm ------
        button_frame = tk.Frame(right_frame, bg="#f7f9fc")
        button_frame.pack(pady=30, padx=20, fill="x")
        
        # Thêm các nút bấm và liên kết với các phương thức của class
        add_btn = ctk.CTkButton(button_frame, text="Thêm", command=self.add_item_window, corner_radius=10, fg_color="#27ae60", font=("Segoe UI", 11), width=100)
        add_btn.pack(side="left", expand=True)

        update_btn = ctk.CTkButton(button_frame, text="Sửa", command=self.update_item_window, corner_radius=10, fg_color="#f39c12", font=("Segoe UI", 11), width=100)
        update_btn.pack(side="left", expand=True, padx=10)
        
        delete_btn = ctk.CTkButton(button_frame, text="Xóa", command=self.delete_item, corner_radius=10, fg_color="#e74c3c", font=("Segoe UI", 11), width=100)
        delete_btn.pack(side="left", expand=True)    

    # Hiển thị sản phẩm
    def set_products_list(self, data):
        """
        Xóa dữ liệu cũ trong bảng và hiển thị dữ liệu mới.
        Phương thức này sẽ được gọi bởi Controller.
        """
        for item in self.tree_mh.get_children():
            self.tree_mh.delete(item)
        for item in data:
            self.tree_mh.insert("", "end", values=item)
        # Tự động chọn dòng đầu tiên sau khi cập nhật
        # children = self.tree_mh.get_children()
        # if children:
        #     self.tree_mh.selection_set(children[0])
        #     self.tree_mh.focus(children[0])

    # Chọn một mặt hàng trong Treeview và cập nhật thông tin vào các ô Entry
    def on_item_select(self, event):
        selected_items = self.tree_mh.selection()
        if not selected_items:
            return
        
        item_id_in_tree = selected_items[0]
        values = self.tree_mh.item(item_id_in_tree, "values")
        
        # Cập nhật dữ liệu lên các ô Entry thông qua dictionary của class (self.form_fields_mh)
        # values[0] là ID, values[1] là tên, v.v.
        self.form_fields_mh["ID:"].set(values[0])
        self.form_fields_mh["Tên mặt hàng:"].set(values[1])
        self.form_fields_mh["Đơn vị:"].set(values[2])
        self.form_fields_mh["Giá:"].set(values[3])
        self.form_fields_mh["Bãi:"].set(values[4] or '')
    
    # Thêm mặt hàng mới
    def add_item_window(self):
        # Tạo cửa sổ thêm mặt hàng
        add_window = tk.Toplevel(self.root_window)
        add_window.title("Thêm mặt hàng mới")
        add_window.geometry("400x300")
        add_window.resizable(False, False) # Không cho phép thay đổi kích thước
        add_window.configure(bg="#f7f9fc")
        add_window.transient(self.root_window)# Cửa sổ luôn ở trên cùng
        add_window.grab_set()

        # Frame chứa form 
        form_add = tk.Frame(add_window, bg="#f7f9fc", padx=20, pady=20)
        form_add.pack(expand=True, fill="both")

        add_fields = {
        "Tên mặt hàng:": tk.StringVar(),
        "Đơn vị:": tk.StringVar(),
        "Giá:": tk.StringVar()
        }

        for label_text, var in add_fields.items():
            row = tk.Frame(form_add, bg="#f7f9fc")
            row.pack(fill="x", pady=8)

            label = tk.Label(row, text=label_text, width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10))
            label.pack(side="left")

            entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 10))
            entry.pack(side="left", expand=True, fill="x")

        # Tạo trường chọn bãi
        yard_names = [yard[1] for yard in self.display_yard_info]

        # 2. Tạo các widget cho dòng chọn bãi
        yard_row = tk.Frame(form_add, bg="#f7f9fc")
        yard_row.pack(fill="x", pady=8)
        
        yard_label = tk.Label(yard_row, text="Bãi:", width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10))
        yard_label.pack(side="left")

        yard_var = tk.StringVar()
        # Thêm lựa chọn "Không có bãi" vào đầu danh sách
        yard_options = ["Không có bãi"] + yard_names 
        
        yard_combo = ttk.Combobox(yard_row, 
                                textvariable=yard_var, 
                                values=yard_options, 
                                state="readonly", # Ngăn người dùng nhập tự do
                                font=("Segoe UI", 10))
        yard_combo.pack(side="left", expand=True, fill="x")
        yard_combo.set("Không có bãi") # Đặt giá trị mặc định được hiển thị       
            
        # Hàm lưu mặt hàng mới
        def save_new_item():
            ten = add_fields["Tên mặt hàng:"].get().strip()
            donvi = add_fields["Đơn vị:"].get().strip()
            gia = add_fields["Giá:"].get().replace(".", "").replace(",", "").strip()
            bai = yard_var.get()

            if not ten or not donvi or not gia:
                messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ thông tin!")
                return
            try:
                gia_int = int(gia)
            except ValueError:
                messagebox.showerror("Lỗi", "Giá phải là số nguyên!")
                return

            # Lấy id_bai nếu có chọn bãi
            id_bai = None
            if bai != "Không có bãi":
                for yard in self.display_yard_info:
                    if yard[1] == bai:
                        id_bai = yard[0]
                        break

            # Gọi phương thức add_item từ controller
            self.controller.add_item(id_bai, ten, gia_int, donvi)
            close_add_window()
        
        def close_add_window():
            add_window.destroy()

        # Nút lưu và hủy
        button_frame_add = tk.Frame(form_add, bg="#f7f9fc")
        button_frame_add.pack(fill="x", pady=(20, 0))

        add_btn = ctk.CTkButton(button_frame_add, text="Lưu", command=save_new_item, fg_color="#2ecc71", font=("Segoe UI", 10, "bold"), width=100)
        add_btn.pack(side="right", padx=5)

        cancel_btn = ctk.CTkButton(button_frame_add, text="Hủy", command=close_add_window, fg_color="#e74c3c", font=("Segoe UI", 10, "bold"), width=100)
        cancel_btn.pack(side="right")

    # Hàm này sẽ được gọi từ Controller để lấy danh sách bãi
    def set_yard_list(self, load_yards):
        self.display_yard_info = []
        self.display_yard_info = load_yards
    
    # Hàm này bạn cần tự định nghĩa để load lại danh sách mặt hàng từ database
    # def reload_products_list(self):
    #     try:
    #         conn = sqlite3.connect("database/CSP_0708.db")
    #         cursor = conn.cursor()
    #         cursor.execute("""SELECT p.id_sp, p.ten_sp, p.don_vi_tinh, p.gia_ban, 
    #                IFNULL(y.ten_bai, 'Không có bãi')
    #         FROM products p
    #         LEFT JOIN yards y ON p.id_bai = y.id_bai""")
    #         data = cursor.fetchall()
    #         conn.close()
    #         self.set_products_list(data)
    #     except Exception as e:
    #         messagebox.showerror("Lỗi", f"Không thể tải danh sách mặt hàng: {e}")
    
    def update_item_window(self):
        self.set_yard_list(load_yards=self.controller.model.get_yard_info())
        selected_id = self.form_fields_mh["ID:"].get()
        if not selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một mặt hàng để sửa!")
            return
        
        # Tạo cửa sổ sửa mặt hàng
        edit_window = tk.Toplevel(self.root_window)
        edit_window.title("Sửa mặt hàng")
        edit_window.geometry("400x300")
        edit_window.resizable(False, False)
        edit_window.configure(bg="#f7f9fc")
        edit_window.transient(self.root_window)

        form_edit = tk.Frame(edit_window, bg="#f7f9fc", padx=20, pady=20)
        form_edit.pack(expand=True, fill="both")

        field_to_edit = {
            "Tên mặt hàng:": tk.StringVar(value=self.form_fields_mh["Tên mặt hàng:"].get()),
            "Đơn vị:": tk.StringVar(value=self.form_fields_mh["Đơn vị:"].get()),
            "Giá:": tk.StringVar(value=self.form_fields_mh["Giá:"].get().replace(".", "").replace(",", "")) # Loại bỏ dấu chấm
        }

        for label_text, var in field_to_edit.items():
            row = tk.Frame(form_edit, bg="#f7f9fc")
            row.pack(fill="x", pady=8)
            label = tk.Label(row, text=label_text, width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10))
            label.pack(side="left")
            entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 10))
            entry.pack(side="left", expand=True, fill="x")

        yard_names = [yard[1] for yard in self.display_yard_info]
        yard_row = tk.Frame(form_edit, bg="#f7f9fc")
        yard_row.pack(fill="x", pady=8)
        yard_label = tk.Label(yard_row, text="Bãi:", width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10))
        yard_label.pack(side="left")
        yard_var = tk.StringVar()
        yard_options = ["Không có bãi"] + yard_names
        yard_combo = ttk.Combobox(yard_row, 
                                  textvariable=yard_var, 
                                  values=yard_options, 
                                  state="readonly", 
                                  font=("Segoe UI", 10))
        yard_combo.pack(side="left", expand=True, fill="x")
        current_yard = self.form_fields_mh["Bãi:"].get()
        if current_yard and current_yard in yard_options:
            yard_combo.set(current_yard)
        else:
            yard_combo.set("Không có bãi")
        # Hàm lưu mặt hàng đã sửa
        def save_edited_item():
            ten = field_to_edit["Tên mặt hàng:"].get().strip()
            donvi = field_to_edit["Đơn vị:"].get().strip()
            gia = field_to_edit["Giá:"].get().replace(".", "").replace(",", "").strip()
            bai = yard_var.get()

            if not ten or not donvi or not gia:
                messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ thông tin!")
                return
            try:
                gia_int = int(gia)
            except ValueError:
                messagebox.showerror("Lỗi", "Giá phải là số nguyên!")
                return

            # Lấy id_bai nếu có chọn bãi
            id_bai = None
            if bai != "Không có bãi":
                for yard in self.display_yard_info:
                    if yard[1] == bai:
                        id_bai = yard[0]
                        break

            # Gọi phương thức update_item từ controller
            self.controller.update_item(selected_id, id_bai, ten, gia_int, donvi)
            edit_window.destroy()
            # Chọn lại sản phẩm vừa sửa trong Treeview
            for item in self.tree_mh.get_children():
                if self.tree_mh.item(item, "values")[0] == selected_id:
                    self.tree_mh.selection_set(item)
                    self.tree_mh.focus(item)
                    self.tree_mh.see(item)
                    self.on_item_select(None)  # Gọi lại hàm cập nhật chi tiết
                    break
        def close_edit_window():
            edit_window.destroy()
        # Nút lưu và hủy
        button_frame_edit = tk.Frame(form_edit, bg="#f7f9fc")
        button_frame_edit.pack(fill="x", pady=(20, 0))
        
        edit_btn = ctk.CTkButton(button_frame_edit, text="Lưu", command=save_edited_item, fg_color="#f39c12", font=("Segoe UI", 10, "bold"), width=100)
        edit_btn.pack(side="right", padx=5)
        cancel_btn = ctk.CTkButton(button_frame_edit, text="Hủy", command=close_edit_window, fg_color="#e74c3c", font=("Segoe UI", 10, "bold"), width=100)
        cancel_btn.pack(side="right")

    
    def delete_item(self):
        selected_id = self.form_fields_mh["ID:"].get()
        selected_tree_item = self.tree_mh.selection()
        if not selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một mặt hàng để xóa!")
            return
        
        confirm = messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa mặt hàng này !")
        if not confirm:
            return
        # Gọi phương thức delete_item từ controller
        self.controller.delete_item(selected_id)
        self.tree_mh.delete(selected_tree_item)
        self.clear_details_form()
        
    def clear_details_form(self):
        """Xóa toàn bộ nội dung trong các ô Entry của form chi tiết."""
        for var in self.form_fields_mh.values():
            var.set("")