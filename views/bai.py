import tkinter as tk
from tkinter import ttk
from tkinter import messagebox # Import messagebox để hiện thông báo
import sqlite3
import customtkinter as ctk
from views.config import db_path

class YardView(tk.Frame):
    def __init__(self, parent, root_window):
        super().__init__(parent, bg="white")
        
        self.root_window = root_window # Lưu lại cửa sổ gốc để dùng cho Toplevel
        
        # Gọi phương thức để tạo tất cả các widget
        self.create_widgets()

    # Phương thức để tạo các widget trong frame 
    def create_widgets(self):
        # Danh sách bãi
        left_frame = tk.Frame(self, bg="white")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(left_frame, text="Danh sách bãi", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=(0, 10), anchor="w")
        style = ttk.Style()
        # Cấu hình style cho Treeview để mỗi hàng cao 40px, đủ cho 2 dòng text
        style.configure("Treeview", rowheight=40, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        columns = ("id", "ten_bai", "dia_chi")
        self.tree_y = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse")

        self.tree_y.heading("id", text="ID")
        self.tree_y.heading("ten_bai", text="Tên bãi")
        self.tree_y.heading("dia_chi", text="Địa chỉ")

        self.tree_y.column("id", width=50, anchor="center")
        self.tree_y.column("ten_bai", width=250)
        self.tree_y.column("dia_chi", width=100)

        # Thanh cuộn
        scrollbar_y = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree_y.yview)
        self.tree_y.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_y.pack(side="right", fill="y")
        self.tree_y.pack(expand=True, fill="both")
        
        # Gán sự kiện chọn dòng
        self.tree_y.bind("<<TreeviewSelect>>", self.on_item_select)

        # Form thông tin chi tiết
        right_frame = tk.Frame(self, bg="#f7f9fc", width=350)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)

        tk.Label(right_frame, text="Thông tin chi tiết", font=("Segoe UI", 16, "bold"), bg="#f7f9fc").pack(pady=20, anchor="w", padx=20)

        self.form_fields_y = {
            "ID:": tk.StringVar(),
            "Tên bãi:": tk.StringVar(),
            "Địa chỉ:": tk.StringVar(),
        }

        form_frame = tk.Frame(right_frame, bg="#f7f9fc")
        form_frame.pack(fill="x", padx=20)

        for label_text, var in self.form_fields_y.items():
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
        add_btn = ctk.CTkButton(button_frame, text="Thêm", command=self.add_yard_window, corner_radius=10, fg_color="#27ae60", font=("Segoe UI", 11), width=100)
        add_btn.pack(side="left", expand=True)

        update_btn = ctk.CTkButton(button_frame, text="Sửa", command=self.update_yard_window, corner_radius=10, fg_color="#f39c12", font=("Segoe UI", 11), width=100)
        update_btn.pack(side="left", expand=True, padx=10)
        
        delete_btn = ctk.CTkButton(button_frame, text="Xóa", command=self.delete_yard, corner_radius=10, fg_color="#e74c3c", font=("Segoe UI", 11), width=100)
        delete_btn.pack(side="left", expand=True) 

    # Hiển thị sản phẩm
    def set_yard_list(self, data):
        """
        Xóa dữ liệu cũ trong bảng và hiển thị dữ liệu mới.
        Phương thức này sẽ được gọi bởi Controller.
        """
        for item in self.tree_y.get_children():
            self.tree_y.delete(item)
        for item in data:
            self.tree_y.insert("", "end", values=item)

    # Chọn một mặt hàng trong Treeview và cập nhật thông tin vào các ô Entry
    def on_item_select(self, event):
        # Lấy dòng được chọn từ Treeview của class (self.tree_y)
        selected_items = self.tree_y.selection()
        
        # Nếu không có dòng nào được chọn (ví dụ: khi xóa dòng cuối), thì thoát
        if not selected_items:
            return

        # selected_items là một tuple, lấy phần tử đầu tiên
        item_id_in_tree = selected_items[0]
        
        # Lấy dữ liệu từ dòng được chọn
        values = self.tree_y.item(item_id_in_tree, "values")
        
        # Cập nhật dữ liệu lên các ô Entry thông qua dictionary của class (self.form_fields_y)
        # values[0] là ID, values[1] là tên, v.v.
        self.form_fields_y["ID:"].set(values[0])
        self.form_fields_y["Tên bãi:"].set(values[1])
        self.form_fields_y["Địa chỉ:"].set(values[2])
    
    # Thêm mặt hàng mới
    def add_yard_window(self):
        # Tạo cửa sổ thêm mặt hàng
        add_window = tk.Toplevel(self.root_window)
        add_window.title("Thêm bãi mới")
        add_window.geometry("400x200")
        add_window.resizable(False, False) # Không cho phép thay đổi kích thước
        add_window.configure(bg="#f7f9fc")
        add_window.transient(self.root_window)# Cửa sổ luôn ở trên cùng
        add_window.grab_set()

        # Frame chứa form 
        form_add = tk.Frame(add_window, bg="#f7f9fc", padx=20, pady=20)
        form_add.pack(expand=True, fill="both")

        add_fields = {
        "Tên bãi:": tk.StringVar(),
        "Địa chỉ:": tk.StringVar(),
        }

        for label_text, var in add_fields.items():
            row = tk.Frame(form_add, bg="#f7f9fc")
            row.pack(fill="x", pady=8)

            label = tk.Label(row, text=label_text, width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10))
            label.pack(side="left")

            entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 10))
            entry.pack(side="left", expand=True, fill="x") 
            
        # Hàm lưu mặt hàng mới
        def save_new_yard():
            ten = add_fields["Tên bãi:"].get().strip()
            dia_chi = add_fields["Địa chỉ:"].get().strip()

            # Gọi phương thức add_item từ controller
            self.controller.add_yard(ten, dia_chi)
            add_window.destroy()

        def close_add_window():
            add_window.destroy()

        # Nút lưu và hủy
        button_frame_add = tk.Frame(form_add, bg="#f7f9fc")
        button_frame_add.pack(fill="x", pady=(20, 0))

        add_btn = ctk.CTkButton(button_frame_add, text="Lưu", command=save_new_yard, fg_color="#2ecc71", font=("Segoe UI", 10, "bold"), width=100)
        add_btn.pack(side="right", padx=5)

        cancel_btn = ctk.CTkButton(button_frame_add, text="Hủy", command=close_add_window, fg_color="#e74c3c", font=("Segoe UI", 10, "bold"), width=100)
        cancel_btn.pack(side="right")
    
    # Phương thức để cập nhật mặt hàng đã chọn
    def update_yard_window(self):
        # Kiểm tra và lấy thông tin mặt hàng
        selected_id = self.form_fields_y["ID:"].get()
        if not selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một bãi để sửa!")
            return

        # Lấy thông tin hiện tại từ các ô Entry của form chính
        current_name = self.form_fields_y["Tên bãi:"].get()
        current_address = self.form_fields_y["Địa chỉ:"].get()
        
        # Tạo cửa sổ chức năng sửa mặt hàng
        edit_window = tk.Toplevel(self.root_window)
        edit_window.title(f"Sửa mặt hàng")
        edit_window.geometry("400x200")
        edit_window.resizable(False, False)
        edit_window.configure(bg="#f7f9fc")
        
        edit_window.transient(self.root_window)
        edit_window.grab_set()

        # Tạo form trong cửa sổ
        form_edit = tk.Frame(edit_window, bg="#f7f9fc", padx=20, pady=20)
        form_edit.pack(expand=True, fill="both")

        fields_to_edit = {
            "Tên bãi:": tk.StringVar(value=current_name),
            "Địa chỉ:": tk.StringVar(value=current_address),
        } 
        
        for label_text, var in fields_to_edit.items():
            row = tk.Frame(form_edit, bg="#f7f9fc")
            row.pack(fill="x", pady=8)
            label = tk.Label(row, text=label_text, width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10))
            label.pack(side="left")
            entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 10))
            entry.pack(side="left", expand=True, fill="x")
        
        def save_yard_change():
            # selected_id = self.form_fields_y["ID:"].get()
            ten = fields_to_edit["Tên bãi:"].get().strip()
            dia_chi = fields_to_edit["Địa chỉ:"].get().strip()

            # Gọi phương thức add_item từ controller
            self.controller.update_yard(selected_id,ten, dia_chi)
            edit_window.destroy()
            
            for item in self.tree_y.get_children():
                if self.tree_y.item(item, "values")[0] == selected_id:
                    self.tree_y.selection_set(item)
                    self.tree_y.focus(item)
                    self.tree_y.see(item)
                    self.on_item_select(None)  # Gọi lại hàm cập nhật chi tiết
                    break

        # Tạo nút lưu và nút hủy
        button_frame_edit = tk.Frame(form_edit, bg="#f7f9fc")
        button_frame_edit.pack(fill="x", pady=(20, 0))

        edit_btn = ctk.CTkButton(button_frame_edit, text="Lưu", command=save_yard_change, fg_color="#f39c12", font=("Segoe UI", 10, "bold"), width=100)
        edit_btn.pack(side="right", padx=5)

        cancel_btn = ctk.CTkButton(button_frame_edit, text="Hủy", command=edit_window.destroy, fg_color="#e74c3c", font=("Segoe UI", 10, "bold"), width=100)
        cancel_btn.pack(side="right")
    
    def delete_yard(self):
        selected_id = self.form_fields_y["ID:"].get()
        if not selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một bãi để xóa!")
            return
        
        confirm = messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa bãi này !")
        if not confirm:
            return
        # Gọi phương thức delete_item từ controller
        self.controller.delete_yard(selected_id)
        