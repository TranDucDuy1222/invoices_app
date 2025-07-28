import tkinter as tk
from tkinter import ttk
from tkinter import messagebox # Import messagebox để hiện thông báo



# Thay thế dữ liệu từ database
sample_data = [
    (1, "Đá bụi", "Xe", 1200000),
    (2, "Đá mi sàn", "Xe", 350000),
    (3, "Xà bần", "Xe", 2800000),
    (4, "Cát san lấp", "Xe", 80000),
]
class MatHangView(tk.Frame):
    def __init__(self, parent, root_window):
        super().__init__(parent, bg="white")
        
        self.root_window = root_window # Lưu lại cửa sổ gốc để dùng cho Toplevel
        
        # Gọi phương thức để tạo tất cả các widget
        self.create_widgets()

    def create_widgets(self):
        #------ Bảng mặt hàng ------
        left_frame = tk.Frame(self, bg="white")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(left_frame, text="Danh sách mặt hàng", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=(0, 10), anchor="w")

        columns = ("id", "ten_mat_hang", "don_vi", "gia")
        self.tree_mh = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse")

        self.tree_mh.heading("id", text="ID")
        self.tree_mh.heading("ten_mat_hang", text="Tên mặt hàng")
        self.tree_mh.heading("don_vi", text="Đơn vị")
        self.tree_mh.heading("gia", text="Giá")

        self.tree_mh.column("id", width=50, anchor="center")
        self.tree_mh.column("ten_mat_hang", width=250)
        self.tree_mh.column("don_vi", width=100, anchor="center")
        self.tree_mh.column("gia", width=120, anchor="e")

        for item in sample_data:
            self.tree_mh.insert("", "end", values=item)
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
            "Giá:": tk.StringVar()
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
        add_btn = tk.Button(button_frame, text="Thêm", command=self.add_item, bg="#2ecc71", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", width=10)
        add_btn.pack(side="left", expand=True)

        update_btn = tk.Button(button_frame, text="Sửa", command=self.update_item, bg="#f39c12", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", width=10)
        update_btn.pack(side="left", expand=True, padx=10)
        
        delete_btn = tk.Button(button_frame, text="Xóa", bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", width=10)
        delete_btn.pack(side="left", expand=True)
    
    def on_item_select(self, event):
        # Lấy dòng được chọn từ Treeview của class (self.tree_mh)
        selected_items = self.tree_mh.selection()
        
        # Nếu không có dòng nào được chọn (ví dụ: khi xóa dòng cuối), thì thoát
        if not selected_items:
            return

        # selected_items là một tuple, lấy phần tử đầu tiên
        item_id_in_tree = selected_items[0]
        
        # Lấy dữ liệu từ dòng được chọn
        values = self.tree_mh.item(item_id_in_tree, "values")
        
        # Cập nhật dữ liệu lên các ô Entry thông qua dictionary của class (self.form_fields_mh)
        # values[0] là ID, values[1] là tên, v.v.
        self.form_fields_mh["ID:"].set(values[0])
        self.form_fields_mh["Tên mặt hàng:"].set(values[1])
        self.form_fields_mh["Đơn vị:"].set(values[2])
        self.formatted_price = f"{int(values[3]):,}".replace(",", ".")
        self.form_fields_mh["Giá:"].set(self.formatted_price)
    def add_item(self):
        # Tạo cửa sổ thêm mặt hàng
        add_window = tk.Toplevel(self.root_window)
        add_window.title("Thêm mặt hàng mới")
        add_window.geometry("400x250")
        add_window.resizable(False, False) # Không cho phép thay đổi kích thước
        add_window.configure(bg="#f7f9fc")

        # Cửa sổ luôn ở trên cùng
        add_window.transient(self.root_window)
        add_window.grab_set()

        # Frame chứa form 
        form_add = tk.Frame(add_window, bg="#f7f9fc", padx=20, pady=20)
        form_add.pack(expand=True, fill="both")

        # Tạo trường nhập liệu
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
            
        # Nút lưu và hủy
        button_frame_add = tk.Frame(form_add, bg="#f7f9fc")
        button_frame_add.pack(fill="x", pady=(20, 0))

        add_btn = tk.Button(button_frame_add, text="Lưu", bg="#2ecc71", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", width=10)
        add_btn.pack(side="right", padx=5)

        cancel_btn = tk.Button(button_frame_add, text="Hủy", command=add_window.destroy, bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", width=10)
        cancel_btn.pack(side="right")

    def update_item(self):
        # Kiểm tra và lấy thông tin mặt hàng
        selected_id = self.form_fields_mh["ID:"].get()
        if not selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một mặt hàng để sửa!")
            return

        # Lấy thông tin hiện tại từ các ô Entry của form chính
        current_name = self.form_fields_mh["Tên mặt hàng:"].get()
        current_unit = self.form_fields_mh["Đơn vị:"].get()
        current_price_str = self.form_fields_mh["Giá:"].get().replace(".", "") # Loại bỏ dấu chấm
        
        # Tạo cửa sổ chức năng sửa mặt hàng
        edit_window = tk.Toplevel(self.root_window)
        edit_window.title(f"Sửa mặt hàng - ID: {selected_id}")
        edit_window.geometry("400x250")
        edit_window.resizable(False, False)
        edit_window.configure(bg="#f7f9fc")
        
        edit_window.transient(self.root_window)
        edit_window.grab_set()

        # Tạo form trong cửa sổ
        form_edit = tk.Frame(edit_window, bg="#f7f9fc", padx=20, pady=20)
        form_edit.pack(expand=True, fill="both")
        
        # Tạo các biến và widget cho form sửa
        name_var = tk.StringVar(value=current_name)
        unit_var = tk.StringVar(value=current_unit)
        price_var = tk.StringVar(value=current_price_str)

        fields_to_edit = {
            "Tên mặt hàng:": name_var,
            "Đơn vị:": unit_var,
            "Giá:": price_var
        }
        
        for label_text, var in fields_to_edit.items():
            row = tk.Frame(form_edit, bg="#f7f9fc")
            row.pack(fill="x", pady=8)
            label = tk.Label(row, text=label_text, width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10))
            label.pack(side="left")
            entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 10))
            entry.pack(side="left", expand=True, fill="x")
        # Tạo nút lưu và nút hủy
        button_frame_edit = tk.Frame(form_edit, bg="#f7f9fc")
        button_frame_edit.pack(fill="x", pady=(20, 0))

        edit_btn = tk.Button(button_frame_edit, text="Lưu", bg="#f39c12", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", width=12)
        edit_btn.pack(side="right", padx=5)

        cancel_btn = tk.Button(button_frame_edit, text="Hủy", command=edit_window.destroy, bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", width=10)
        cancel_btn.pack(side="right")