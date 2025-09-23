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
        
        # Biến theo dõi view hiện tại
        self.current_view = "yards"

        # Biến lưu trữ ID đang được chọn cho mỗi view
        self.selected_yard_id = None
        self.selected_vehicle_id = None
        
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
        self.button_frame = button_frame

        self.add_btn = ctk.CTkButton(self.button_frame, text="Thêm", command=self.add_yard_window, corner_radius=10, fg_color="#27ae60", font=("Segoe UI", 11), width=100)
        self.update_btn = ctk.CTkButton(self.button_frame, text="Sửa", command=self.update_yard, corner_radius=10, fg_color="#f39c12", font=("Segoe UI", 11), width=100)
        self.cancel_btn = ctk.CTkButton(self.button_frame, text="Hủy", command=self.clear_selection_and_form, corner_radius=10, fg_color="#7f8c8d", font=("Segoe UI", 11), width=100)
        self.delete_btn = ctk.CTkButton(self.button_frame, text="Xóa", command=self.delete_yard, corner_radius=10, fg_color="#e74c3c", font=("Segoe UI", 11), width=100)

        self._show_initial_buttons()

    def _show_initial_buttons(self):
        """Chỉ hiển thị nút Thêm."""
        self.update_btn.pack_forget()
        self.cancel_btn.pack_forget()
        self.delete_btn.pack_forget()
        self.add_btn.pack(side="left", expand=True, pady=5)

    def _show_edit_buttons(self):
        """Hiển thị các nút Sửa, Hủy, Xóa."""
        self.add_btn.pack_forget()
        self.update_btn.pack(side="left", expand=True, pady=5)
        self.cancel_btn.pack(side="left", expand=True, pady=5, padx=10)
        self.delete_btn.pack(side="left", expand=True, pady=5)

    def clear_selection_and_form(self):
        """Xóa lựa chọn trên Treeview, xóa form và đặt lại các nút."""
        if self.tree_y.selection():
            self.tree_y.selection_remove(self.tree_y.selection()[0])
        self.clear_details_form()
        self._show_initial_buttons()
        self.selected_customer_id = None
        
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

        self.selected_customer_id = values[0]
        self._show_edit_buttons()
    
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
    def update_yard(self):
        """
        Cập nhật thông tin khách hàng trực tiếp từ form chi tiết.
        """
        # 1. Kiểm tra xem có khách hàng nào được chọn trong form không
        selected_id = self.form_fields_y["ID:"].get()
        if not selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một bãi để sửa!")
            return

        # 2. Lấy dữ liệu đã được người dùng chỉnh sửa từ các ô Entry
        #    Hàm .strip() giúp loại bỏ các khoảng trắng thừa ở đầu và cuối
        ten_bai = self.form_fields_y["Tên bãi:"].get().strip()
        dia_chi = self.form_fields_y["Địa chỉ:"].get().strip()

        # 3. Kiểm tra dữ liệu đầu vào (ví dụ: tên không được để trống)
        if not ten_bai:
            messagebox.showerror("Lỗi", "Tên bãi không được để trống.")
            return

        # 4. Yêu cầu xác nhận từ người dùng
        confirm = messagebox.askyesno(
            "Xác nhận sửa", 
            f"Xác nhận thay đổi thông tin bãi"
        )
        
        if not confirm:
            return # Nếu người dùng chọn "No", không làm gì cả

        try:
            # 5. Gọi phương thức update_customer từ controller để lưu vào database
            self.controller.update_yard(selected_id, ten_bai, dia_chi)
            
            # 6. Cập nhật lại dòng tương ứng trong Treeview mà không cần tải lại toàn bộ danh sách
            selection = self.tree_y.selection()
            if selection:            
                selected_item = self.tree_y.selection()[0]  # Lấy item đang được chọn
                self.tree_y.item(selected_item, values=(selected_id, ten_bai, dia_chi))
            
            # 7. Thông báo thành công
            messagebox.showinfo("Thành công", "Cập nhật thông tin khách hàng thành công!")

        except Exception as e:
            # 8. Bắt lỗi nếu có sự cố xảy ra và thông báo cho người dùng
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi cập nhật: {e}")
    
    def delete_yard(self):
        selected_id = self.form_fields_y["ID:"].get()
        selected_tree_item = self.tree_y.selection()
        if not selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một bãi để xóa!")
            return
        
        confirm = messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa bãi này !")
        if not confirm:
            return
        # Gọi phương thức delete_item từ controller
        self.controller.delete_yard(selected_id)
        # Xóa thông tin trong form
        self.tree_y.delete(selected_tree_item)
        self.clear_details_form()

    def clear_details_form(self):
        """Xóa toàn bộ nội dung trong các ô Entry của form chi tiết."""
        for var in self.form_fields_y.values():
            var.set("")
        self.selected_customer_id = None
        