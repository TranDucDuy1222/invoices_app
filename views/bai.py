import tkinter as tk
from tkinter import ttk
from tkinter import messagebox # Import messagebox để hiện thông báo
import sqlite3
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

        self.tree_y.heading("id", text="Id")
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
        add_btn = tk.Button(button_frame, text="Thêm", command=self.add_item_window, bg="#2ecc71", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", width=10)
        add_btn.pack(side="left", expand=True)

        update_btn = tk.Button(button_frame, text="Sửa", command=self.update_item_window, bg="#f39c12", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", width=10)
        update_btn.pack(side="left", expand=True, padx=10)
        
        delete_btn = tk.Button(button_frame, text="Xóa", command=self.delete_item, bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", width=10)
        delete_btn.pack(side="left", expand=True)    

    # Hiển thị sản phẩm
    def set_products_list(self, data):
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
        self.form_fields_y["Tên mặt hàng:"].set(values[1])
        self.form_fields_y["Đơn vị:"].set(values[2])
        self.form_fields_y["Giá:"].set(values[3])
        self.form_fields_y["Bãi:"].set(values[4] or '')
    
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
            add_window.destroy()

        # Nút lưu và hủy
        button_frame_add = tk.Frame(form_add, bg="#f7f9fc")
        button_frame_add.pack(fill="x", pady=(20, 0))

        add_btn = tk.Button(button_frame_add, text="Lưu", command=save_new_item, bg="#2ecc71", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", width=10)
        add_btn.pack(side="right", padx=5)

        cancel_btn = tk.Button(button_frame_add, text="Hủy", command=add_window.destroy, bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", width=10)
        cancel_btn.pack(side="right")

    # Hàm này sẽ được gọi từ Controller để lấy danh sách bãi
    def set_yard_list(self, load_yards):
        self.display_yard_info = []
        self.display_yard_info = load_yards
        print (load_yards)
    
    # Hàm này bạn cần tự định nghĩa để load lại danh sách mặt hàng từ database
    def reload_products_list(self):
        try:
            conn = sqlite3.connect("database/CSP_0708.db")
            cursor = conn.cursor()
            cursor.execute("""SELECT p.id_sp, p.ten_sp, p.don_vi_tinh, p.gia_ban, 
                   IFNULL(y.ten_bai, 'Không có bãi')
            FROM products p
            LEFT JOIN yards y ON p.id_bai = y.id_bai""")
            data = cursor.fetchall()
            conn.close()
            self.set_products_list(data)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách mặt hàng: {e}")
    
    # Phương thức để cập nhật mặt hàng đã chọn
    def update_item_window(self):
        # Kiểm tra và lấy thông tin mặt hàng
        selected_id = self.form_fields_y["ID:"].get()
        if not selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một mặt hàng để sửa!")
            return

        # Lấy thông tin hiện tại từ các ô Entry của form chính
        current_name = self.form_fields_y["Tên mặt hàng:"].get()
        current_unit = self.form_fields_y["Đơn vị:"].get()
        current_price_str = self.form_fields_y["Giá:"].get().replace(".", "") # Loại bỏ dấu chấm
        current_yard = self.form_fields_y["Bãi:"].get() 
        
        
        # Tạo cửa sổ chức năng sửa mặt hàng
        edit_window = tk.Toplevel(self.root_window)
        edit_window.title(f"Sửa mặt hàng")
        edit_window.geometry("400x300")
        edit_window.resizable(False, False)
        edit_window.configure(bg="#f7f9fc")
        
        edit_window.transient(self.root_window)
        edit_window.grab_set()

        # Tạo form trong cửa sổ
        form_edit = tk.Frame(edit_window, bg="#f7f9fc", padx=20, pady=20)
        form_edit.pack(expand=True, fill="both")
        
        # Tạo các biến và widget cho form sửa
        # name_var = tk.StringVar(value=current_name)
        # unit_var = tk.StringVar(value=current_unit)
        # price_var = tk.StringVar(value=current_price_str)

        fields_to_edit = {
            "Tên mặt hàng:": tk.StringVar(value=current_name),
            "Đơn vị:": tk.StringVar(value=current_unit),
            "Giá:": tk.StringVar(value=current_price_str),
        } 
        
        for label_text, var in fields_to_edit.items():
            row = tk.Frame(form_edit, bg="#f7f9fc")
            row.pack(fill="x", pady=8)
            label = tk.Label(row, text=label_text, width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10))
            label.pack(side="left")
            entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 10))
            entry.pack(side="left", expand=True, fill="x")

        # Tạo trường chọn bãi
        yard_names = [yard[1] for yard in self.display_yard_info]

        # 2. Tạo các widget cho dòng chọn bãi
        yard_row = tk.Frame(form_edit, bg="#f7f9fc")
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
        if current_yard and current_yard in yard_options:
            yard_combo.set(current_yard)
        else:
            yard_combo.set("Không có bãi")
        # print("current_yard:", repr(current_yard))
        # print("current_yard in yard_options:", current_yard in yard_options)
        
        # Tạo nút lưu và nút hủy
        button_frame_edit = tk.Frame(form_edit, bg="#f7f9fc")
        button_frame_edit.pack(fill="x", pady=(20, 0))

        edit_btn = tk.Button(button_frame_edit, text="Lưu", bg="#f39c12", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", width=12)
        edit_btn.pack(side="right", padx=5)

        cancel_btn = tk.Button(button_frame_edit, text="Hủy", command=edit_window.destroy, bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", width=10)
        cancel_btn.pack(side="right")
    
    def delete_item(self):
        selected_id = self.form_fields_y["ID:"].get()
        if not selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một mặt hàng để xóa!")
            return
        
        confirm = messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa mặt hàng này !")
        if not confirm:
            return
        # Gọi phương thức delete_item từ controller
        self.controller.delete_item(selected_id)
        