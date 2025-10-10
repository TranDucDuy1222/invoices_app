import tkinter as tk
from tkinter import ttk
from tkinter import messagebox # Import messagebox để hiện thông báo
import customtkinter as ctk

class KhachHangView(tk.Frame):
    def __init__(self, parent, root_window):
        super().__init__(parent, bg="white")
        
        self.root_window = root_window
        self.selected_customer_id = None
        self.original_customer_data = None # Biến lưu dữ liệu gốc
        self.all_customers_data = [] # Lưu toàn bộ danh sách khách hàng
        self.create_widgets()

    def create_widgets(self):  
        #------ Bảng danh sách khách hàng ------
        left_frame = tk.Frame(self, bg='white')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(left_frame, text="Danh sách khách hàng", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=(0, 10), anchor="w")

        # -- Thanh tìm kiếm --
        search_frame = ctk.CTkFrame(left_frame, fg_color="white")
        search_frame.pack(fill="x", pady=(0, 10)) # Sửa từ grid() sang pack()
        
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            fg_color="white", 
            text_color="black",
            font=("Arial", 11),  
            corner_radius=10,
            border_width=2,
            border_color="#474646"
        )
        self.placeholder = "Tìm kiếm khách hàng..."
        search_entry.insert(0, self.placeholder)        
        search_entry.bind("<FocusIn>", self.on_search_focus_in)
        search_entry.bind("<FocusOut>", self.on_search_focus_out)
        search_entry.pack(expand=True, fill="x", padx=5, pady=5) # Sửa từ grid() sang pack()
        
        # Bind sự kiện KeyRelease thay vì dùng trace
        search_entry.bind("<KeyRelease>", self.filter_data)

        # Thêm cột 'loai_kh' vào columns
        columns = ("id", "ten_khach_hang", "dia_chi", "sdt")
        self.tree_kh = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse")

        self.tree_kh.heading("id", text="ID")
        self.tree_kh.heading("ten_khach_hang", text="Tên khách hàng")
        self.tree_kh.heading("dia_chi", text="Địa chỉ")
        self.tree_kh.heading("sdt", text="Số điện thoại")

        self.tree_kh.column("id", width=5, anchor="center")
        self.tree_kh.column("ten_khach_hang", width=100)
        self.tree_kh.column("dia_chi", width=100)
        self.tree_kh.column("sdt", width=20, anchor="w")

        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree_kh.yview)
        self.tree_kh.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree_kh.pack(expand=True, fill="both")
        
        # Gán sự kiện chọn dòng
        self.tree_kh.bind("<<TreeviewSelect>>", self.on_customer_select)

        #------ Form thông tin chi tiết ------
        right_frame = tk.Frame(self, bg="#f7f9fc", width=450)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)

        # --- Frame chứa nút Thêm chính, luôn hiển thị ---
        add_button_container = tk.Frame(right_frame, bg="#f7f9fc")
        add_button_container.pack(pady=20, padx=20, fill="x")
        self.add_btn = ctk.CTkButton(add_button_container, text="Thêm khách hàng mới", command=self.add_customer_window, corner_radius=10, fg_color="#27ae60", font=("Segoe UI", 15, "bold"), height=30)
        self.add_btn.pack(expand=True, fill="x")

        # --- Frame chứa toàn bộ form chi tiết, có thể ẩn/hiện ---
        self.details_container_kh = tk.Frame(right_frame, bg="#f7f9fc")
        self.details_container_kh.pack(fill="both", expand=True, padx=20)

        tk.Label(self.details_container_kh, text="Thông tin khách hàng", font=("Segoe UI", 16, "bold"), bg="#f7f9fc").pack(pady=(0, 20), anchor="w")

        # Lưu các biến thành thuộc tính của self
        self.form_fields_kh = {
            "ID:": tk.StringVar(),
            "Khách hàng:": tk.StringVar(),
            "Địa chỉ:": tk.StringVar(),
            "Số điện thoại:": tk.StringVar()
        }
        # self.loai_kh_var = tk.StringVar(value="Khách lẻ") # Đặt giá trị mặc định

        form_frame = tk.Frame(self.details_container_kh, bg="#f7f9fc")
        form_frame.pack(fill="x")

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
        button_frame = tk.Frame(self.details_container_kh, bg="#f7f9fc")
        button_frame.pack(pady=20, fill="x")

        self.button_frame = button_frame

        self.update_btn = ctk.CTkButton(self.button_frame, text="Sửa", command=self.update_customer, corner_radius=10, fg_color="#f39c12", font=("Segoe UI", 15), width=100)
        self.cancel_btn = ctk.CTkButton(self.button_frame, text="Hủy", command=self.clear_selection_and_form, corner_radius=10, fg_color="#7f8c8d", font=("Segoe UI", 15), width=100)
        self.delete_btn = ctk.CTkButton(self.button_frame, text="Xóa", command=self.delete_customer, corner_radius=10, fg_color="#e74c3c", font=("Segoe UI", 15), width=100)

        self._show_initial_buttons()

        # Xử lý sự kiện khi ô tìm kiếm được focus
    def on_search_focus_in(self, event):
        if self.search_var.get() == self.placeholder:
            event.widget.delete(0, "end")
            event.widget.config(fg='black')

    # Xử lý sự kiện khi ô tìm kiếm mất focus
    def on_search_focus_out(self, event):
        if not self.search_var.get():
            event.widget.config(fg='grey')
            event.widget.insert(0, self.placeholder)

    # Phương thức lọc dữ liệu
    def filter_data(self, event=None):
        """Lọc dữ liệu trong Treeview dựa trên nội dung ô tìm kiếm."""
        search_term = self.search_var.get().lower().strip() if self.search_var.get() != self.placeholder else ""
        
        # Xóa hết các dòng hiện tại
        for i in self.tree_kh.get_children():
            self.tree_kh.delete(i)
            
        # Nếu không có từ khóa tìm kiếm, hiển thị tất cả
        if not search_term:
            for item in self.all_customers_data:
                self.tree_kh.insert("", "end", values=item)
            return
                
        # Lọc và hiển thị các dòng phù hợp
        for item in self.all_customers_data:
            # item[1] là cột 'ten_khach_hang'
            if search_term in item[1].lower():
                self.tree_kh.insert("", "end", values=item)

    def _show_initial_buttons(self):
        """Ẩn form chi tiết và chỉ hiển thị nút Thêm chính."""
        self.details_container_kh.pack_forget()
        self.add_btn.pack(expand=True, fill="x")

    def _show_edit_buttons(self):
        """Hiển thị form chi tiết và các nút Sửa, Hủy, Xóa."""
        self.add_btn.pack_forget()
        self.details_container_kh.pack(fill="both", expand=True, padx=20)
        self.update_btn.pack(side="left", expand=True, pady=5)
        self.cancel_btn.pack(side="left", expand=True, pady=5, padx=10)
        self.delete_btn.pack(side="left", expand=True, pady=5)

    def clear_selection_and_form(self):
        """Xóa lựa chọn trên Treeview, xóa form và đặt lại các nút."""
        if self.tree_kh.selection():
            self.tree_kh.selection_remove(self.tree_kh.selection()[0])
        self.clear_details_form()
        self._show_initial_buttons()
        self.selected_customer_id = None
        
    def set_customer_list(self, data):
        """
        Xóa dữ liệu cũ trong bảng và hiển thị dữ liệu mới.
        Phương thức này sẽ được gọi bởi Controller.
        """
        for item in self.tree_kh.get_children():
            self.tree_kh.delete(item)
        
        self.all_customers_data = data # Lưu lại dữ liệu gốc

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
        
        self.original_customer_data = values # Lưu dữ liệu gốc khi chọn
        # Cập nhật dữ liệu lên các ô Entry
        self.form_fields_kh["ID:"].set(values[0])
        self.form_fields_kh["Khách hàng:"].set(values[1])
        self.form_fields_kh["Địa chỉ:"].set(values[2])
        self.form_fields_kh["Số điện thoại:"].set(values[3])
        
        self.selected_customer_id = values[0]
        self._show_edit_buttons()

    def add_customer_window(self):
        # Tạo cửa sổ thêm mặt hàng
        add_window = tk.Toplevel(self.root_window)
        add_window.title("Thêm khách hàng mới")
        
        window_width = 400
        window_height = 200

        screen_width = self.root_window.winfo_screenwidth()
        screen_height = self.root_window.winfo_screenheight()

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        add_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
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
    
    def update_customer(self):
        """
        Cập nhật thông tin khách hàng trực tiếp từ form chi tiết.
        """
        # 1. Kiểm tra xem có khách hàng nào được chọn trong form không
        selected_id = self.form_fields_kh["ID:"].get()
        if not selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một khách hàng để sửa!")
            return

        # 2. Lấy dữ liệu đã được người dùng chỉnh sửa từ các ô Entry
        #    Hàm .strip() giúp loại bỏ các khoảng trắng thừa ở đầu và cuối
        ten_kh = self.form_fields_kh["Khách hàng:"].get().strip()
        dia_chi = self.form_fields_kh["Địa chỉ:"].get().strip()
        so_dien_thoai = self.form_fields_kh["Số điện thoại:"].get().strip()

        # 3. So sánh dữ liệu mới với dữ liệu gốc
        if self.original_customer_data:
            _, original_ten, original_diachi, original_sdt = self.original_customer_data
            if (ten_kh == original_ten and 
                dia_chi == original_diachi and 
                so_dien_thoai == original_sdt):
                messagebox.showinfo("Thông báo", "Không có thay đổi nào để cập nhật.")
                return

        # 4. Kiểm tra dữ liệu đầu vào (ví dụ: tên không được để trống)
        if not ten_kh or not dia_chi:
            messagebox.showerror("Lỗi", "Tên khách hàng và địa chỉ không được để trống.")
            return

        # 5. Yêu cầu xác nhận từ người dùng
        confirm = messagebox.askyesno(
            "Xác nhận sửa", 
            "Xác nhận thay đổi thông tin khách hàng?"
        )
        
        if not confirm:
            return # Nếu người dùng chọn "No", không làm gì cả

        try:
            # 6. Gọi phương thức update_customer từ controller để lưu vào database
            self.controller.update_customer(selected_id, ten_kh, dia_chi, so_dien_thoai)
            
            # 7. Cập nhật lại dòng tương ứng trong Treeview mà không cần tải lại toàn bộ danh sách
            selection = self.tree_kh.selection()
            if selection:            
                selected_item = self.tree_kh.selection()[0]  # Lấy item đang được chọn
                self.tree_kh.item(selected_item, values=(selected_id, ten_kh, dia_chi, so_dien_thoai))
                # Cập nhật lại dữ liệu gốc sau khi đã lưu thành công
                self.original_customer_data = (selected_id, ten_kh, dia_chi, so_dien_thoai)
            

        except Exception as e:
            # Bắt lỗi nếu có sự cố xảy ra và thông báo cho người dùng
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi cập nhật: {e}")
    
    def delete_customer(self):
        selected_id = self.form_fields_kh["ID:"].get()
        selected_tree_item = self.tree_kh.selection()
        if not selected_id or selected_id != self.selected_customer_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một khách hàng để xóa!")
            return
        
        confirm = messagebox.askyesno("Xác nhận xóa", "Bạn có chắc chắn muốn xóa khách hàng này?")
        if confirm:
            # Gọi phương thức delete_item từ controller
            self.controller.delete_customer(selected_id)
            # Xóa thông tin trong form
            self.tree_kh.delete(selected_tree_item)
            self.clear_selection_and_form()

    def clear_details_form(self):
        """Xóa toàn bộ nội dung trong các ô Entry của form chi tiết."""
        for var in self.form_fields_kh.values():
            var.set("")
        self.original_customer_data = None
        self.selected_customer_id = None