import tkinter as tk
from tkinter import ttk
from tkinter import messagebox # Import messagebox để hiện thông báo
import sqlite3
import customtkinter as ctk
from views.config import db_path

class YardVehicleManagementView(tk.Frame):
    def __init__(self, parent, root_window):
        super().__init__(parent, bg="white")
        
        self.root_window = root_window
        self.current_view = "yards" # Theo dõi giao diện hiện tại: "yards" hoặc "vehicles"
        self.selected_customer_id = None # Giữ lại biến này từ code cũ của bạn
        self.original_yard_data = None # Biến lưu dữ liệu gốc của bãi
        
        self.create_widgets()
        # self.set_yard_list(self.controller.get_all_yards()) # Ví dụ cách tải dữ liệu ban đầu

# ==============================================================================
# 1. HÀM CẤU TRÚC CHÍNH (TẠO GIAO DIỆN)
# ==============================================================================

    def create_widgets(self):
        """Hàm chính tạo ra các thành phần cốt lõi của giao diện."""
        # ------ Frame chứa nút chuyển đổi ------
        top_frame = tk.Frame(self, bg="white")
        top_frame.pack(pady=(10, 0), padx=10, fill="x")

        self.view_switcher = ctk.CTkSegmentedButton(
            top_frame,
            values=["Danh sách bãi", "Danh sách xe"],
            command=self.switch_view
        )
        self.view_switcher.set("Danh sách bãi")
        self.view_switcher.pack(anchor="w")

        # ------ Frame chính chứa các giao diện có thể chuyển đổi ------
        main_container = tk.Frame(self, bg="white")
        main_container.pack(expand=True, fill="both")
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        # ------ Tạo 2 Frame cho 2 giao diện, đặt chồng lên nhau ------
        self.yard_frame = tk.Frame(main_container, bg="white")
        self.vehicle_frame = tk.Frame(main_container, bg="white")

        self.yard_frame.grid(row=0, column=0, sticky="nsew")
        self.vehicle_frame.grid(row=0, column=0, sticky="nsew")

        # ------ Gọi các hàm để vẽ nội dung cho từng giao diện ------
        self.create_yard_view(self.yard_frame)
        self.create_vehicle_view(self.vehicle_frame)

        # ------ Hiển thị giao diện mặc định và cài đặt nút bấm ------
        self.switch_view("Danh sách bãi")

    def switch_view(self, view_name):
        """Chuyển đổi giữa các giao diện và cập nhật lại chức năng cho các nút bấm."""
        self.clear_selection_and_form() # Reset trạng thái trước khi chuyển

        if view_name == "Danh sách bãi":
            self.current_view = "yards"
            self.yard_frame.tkraise()
        elif view_name == "Danh sách xe":
            self.current_view = "vehicles"
            self.vehicle_frame.tkraise()
            # TODO: Gọi hàm tải dữ liệu cho xe nếu cần
            # self.load_vehicles_data()
        
        # self.update_button_commands()

    # def update_button_commands(self):
    #     """Cập nhật lại thuộc tính 'command' của các nút dựa trên view hiện tại."""
    #     if self.current_view == "yards":
    #         self.add_btn.configure(command=self.add_yard_window)
    #         self.update_btn.configure(command=self.update_yard)
    #         self.delete_btn.configure(command=self.delete_yard)
    #     elif self.current_view == "vehicles":
    #         self.add_btn.configure(command=self.add_vehicle_window)
    #         self.update_btn.configure(command=self.update_vehicle)
    #         self.delete_btn.configure(command=self.delete_vehicle)

# ==============================================================================
# 2. HÀM DÀNH CHO GIAO DIỆN "DANH SÁCH BÃI"
# ==============================================================================

    def create_yard_view(self, parent):
        left_frame = tk.Frame(parent, bg="white")
        left_frame.pack(side="left", fill="both", expand=True, padx=(10, 10), pady=10)

        tk.Label(left_frame, text="Danh sách bãi", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=(0, 10), anchor="w")
        style = ttk.Style()
        style.configure("Treeview", rowheight=40, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        columns = ("id", "ten_bai", "dia_chi")
        self.tree_y = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse")
        self.tree_y.heading("id", text="ID"); self.tree_y.heading("ten_bai", text="Tên bãi"); self.tree_y.heading("dia_chi", text="Địa chỉ")
        self.tree_y.column("id", width=50, anchor="center"); self.tree_y.column("ten_bai", width=250); self.tree_y.column("dia_chi", width=100)
        
        scrollbar_y = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree_y.yview)
        self.tree_y.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_y.pack(side="right", fill="y")
        self.tree_y.pack(expand=True, fill="both")
        self.tree_y.bind("<<TreeviewSelect>>", self.on_item_select)

        right_frame = tk.Frame(parent, bg="#f7f9fc", width=350)
        right_frame.pack(side="right", fill="both", padx=(0, 10), pady=10)
        right_frame.pack_propagate(False)

        tk.Label(right_frame, text="Thông tin chi tiết", font=("Segoe UI", 16, "bold"), bg="#f7f9fc").pack(pady=20, anchor="w", padx=20)

        self.form_fields_y = {"ID:": tk.StringVar(), "Tên bãi:": tk.StringVar(), "Địa chỉ:": tk.StringVar()}
        form_frame_y = tk.Frame(right_frame, bg="#f7f9fc")
        form_frame_y.pack(fill="x", padx=20)
        for label_text, var in self.form_fields_y.items():
            row = tk.Frame(form_frame_y, bg="#f7f9fc"); row.pack(fill="x", pady=5)
            label = tk.Label(row, text=label_text, width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10)); label.pack(side="left")
            entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 10))
            if label_text == "ID:": entry.config(state="readonly", relief="flat", bg="#e9ecef")
            entry.pack(side="left", expand=True, fill="x")

        button_frame = tk.Frame(right_frame, bg="#f7f9fc")
        button_frame.pack(pady=30, padx=20, fill="x")

        self.button_frame = button_frame

        self.add_btn = ctk.CTkButton(self.button_frame, text="Thêm", command=self.add_yard_window, corner_radius=10, fg_color="#27ae60", font=("Segoe UI", 15), width=100)
        self.update_btn = ctk.CTkButton(self.button_frame, text="Sửa", command=self.update_yard, corner_radius=10, fg_color="#f39c12", font=("Segoe UI", 15), width=100)
        self.cancel_btn = ctk.CTkButton(self.button_frame, text="Hủy", command=self.clear_selection_and_form, corner_radius=10, fg_color="#7f8c8d", font=("Segoe UI", 15), width=100)
        self.delete_btn = ctk.CTkButton(self.button_frame, text="Xóa", command=self.delete_yard, corner_radius=10, fg_color="#e74c3c", font=("Segoe UI", 15), width=100)

    # Các hàm chức năng cho Bãi (giữ nguyên từ code cũ của bạn)
    def set_yard_list(self, data):
        for item in self.tree_y.get_children(): self.tree_y.delete(item)
        for item in data: self.tree_y.insert("", "end", values=item)

    def on_item_select(self, event):
        if self.current_view != "yards": return # Chỉ chạy khi đang ở view bãi
        selected_items = self.tree_y.selection()
        if not selected_items: return
        values = self.tree_y.item(selected_items[0], "values")
        self.original_yard_data = values # Lưu dữ liệu gốc khi chọn
        self.form_fields_y["ID:"].set(values[0])
        self.form_fields_y["Tên bãi:"].set(values[1])
        self.form_fields_y["Địa chỉ:"].set(values[2])
        self.selected_customer_id = values[0]
        self._show_edit_buttons()
    
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

        add_btn = ctk.CTkButton(button_frame_add, text="Lưu", command=save_new_yard, fg_color="#2ecc71", font=("Segoe UI", 15, "bold"), width=100)
        add_btn.pack(side="right", padx=5)

        cancel_btn = ctk.CTkButton(button_frame_add, text="Hủy", command=close_add_window, fg_color="#e74c3c", font=("Segoe UI", 15, "bold"), width=100)
        cancel_btn.pack(side="right")

    def update_yard(self):
        # 1. Kiểm tra xem có bãi nào được chọn trong form không
        selected_id = self.form_fields_y["ID:"].get()
        if not selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một bãi để sửa!")
            return

        # 2. Lấy dữ liệu đã được người dùng chỉnh sửa từ các ô Entry
        ten_bai = self.form_fields_y["Tên bãi:"].get().strip()
        dia_chi = self.form_fields_y["Địa chỉ:"].get().strip()

        # 3. So sánh dữ liệu mới với dữ liệu gốc
        if self.original_yard_data:
            _, original_ten, original_diachi = self.original_yard_data
            if (ten_bai == original_ten and dia_chi == original_diachi):
                messagebox.showinfo("Thông báo", "Không có thay đổi nào để cập nhật.")
                return

        # 4. Kiểm tra dữ liệu đầu vào (ví dụ: tên không được để trống)
        if not ten_bai:
            messagebox.showerror("Lỗi", "Tên bãi không được để trống.")
            return

        # 5. Yêu cầu xác nhận từ người dùng
        confirm = messagebox.askyesno(
            "Xác nhận sửa", 
            "Xác nhận thay đổi thông tin bãi?"
        )
        
        if not confirm:
            return # Nếu người dùng chọn "No", không làm gì cả

        try:
            # 6. Gọi phương thức update_yard từ controller để lưu vào database
            self.controller.update_yard(selected_id, ten_bai, dia_chi)
            
            # 7. Cập nhật lại dòng tương ứng trong Treeview
            selection = self.tree_y.selection()
            if selection:            
                selected_item = self.tree_y.selection()[0]
                self.tree_y.item(selected_item, values=(selected_id, ten_bai, dia_chi))
                # Cập nhật lại dữ liệu gốc sau khi đã lưu thành công
                self.original_yard_data = (selected_id, ten_bai, dia_chi)

        except Exception as e:
            # Bắt lỗi nếu có sự cố xảy ra và thông báo cho người dùng
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
        self.original_yard_data = None
        self.selected_customer_id = None

# ==============================================================================
# 3. HÀM DÀNH CHO GIAO DIỆN "DANH SÁCH XE" (PLACEHOLDER)
# ==============================================================================
    
    def create_vehicle_view(self, parent):
        left_frame = tk.Frame(parent, bg="white")
        left_frame.pack(side="left", fill="both", expand=True, padx=(10, 10), pady=10)

        tk.Label(left_frame, text="Danh sách bãi", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=(0, 10), anchor="w")
        style = ttk.Style()
        style.configure("Treeview", rowheight=40, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        columns = ("id", "bien_so_xe")
        self.tree_x = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse")
        self.tree_x.heading("id", text="ID")
        self.tree_x.heading("bien_so_xe", text="Biển số xe")
        self.tree_x.column("id", width=10, anchor="center")
        self.tree_x.column("bien_so_xe", width=10)
        
        scrollbar_x = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree_x.yview)
        self.tree_x.configure(yscrollcommand=scrollbar_x.set)
        scrollbar_x.pack(side="right", fill="y")
        self.tree_x.pack(expand=True, fill="both")
        self.tree_x.bind("<<TreeviewSelect>>")

        right_frame = tk.Frame(parent, bg="#f7f9fc", width=350)
        right_frame.pack(side="right", fill="both", padx=(0, 10), pady=10)
        right_frame.pack_propagate(False)

        tk.Label(right_frame, text="Thông tin chi tiết", font=("Segoe UI", 16, "bold"), bg="#f7f9fc").pack(pady=20, anchor="w", padx=20)

        self.form_fields_x = {"ID:": tk.StringVar(), "Biển số xe:": tk.StringVar()}
        form_frame_x = tk.Frame(right_frame, bg="#f7f9fc")
        form_frame_x.pack(fill="x", padx=20)
        for label_text, var in self.form_fields_x.items():
            row = tk.Frame(form_frame_x, bg="#f7f9fc"); row.pack(fill="x", pady=5)
            label = tk.Label(row, text=label_text, width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10))
            label.pack(side="left")
            entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 10))
            if label_text == "ID:": entry.config(state="readonly", relief="flat", bg="#e9ecef")
            entry.pack(side="left", expand=True, fill="x")

        button_frame_x = tk.Frame(right_frame, bg="#f7f9fc")
        button_frame_x.pack(pady=30, padx=20, fill="x")

        self.button_frame_x = button_frame_x

        self.add_btn_x = ctk.CTkButton(self.button_frame_x, text="Thêm", corner_radius=10, fg_color="#27ae60", font=("Segoe UI", 15), width=100)
        self.update_btn_x = ctk.CTkButton(self.button_frame_x, text="Sửa", corner_radius=10, fg_color="#f39c12", font=("Segoe UI", 15), width=100)
        self.cancel_btn_x = ctk.CTkButton(self.button_frame_x, text="Hủy", corner_radius=10, fg_color="#7f8c8d", font=("Segoe UI", 15), width=100)
        self.delete_btn_x = ctk.CTkButton(self.button_frame_x, text="Xóa", corner_radius=10, fg_color="#e74c3c", font=("Segoe UI", 15), width=100)

    def on_vehicle_select(self, event):
        if self.current_view != "vehicles": return
        print("Đã chọn một xe")
        # Code lấy dữ liệu từ self.tree_v và điền vào form xe
        self._show_edit_buttons()

    def add_vehicle_window(self):
        print("Mở cửa sổ thêm Xe")

    def update_vehicle(self):
        print("Cập nhật Xe")

    def delete_vehicle(self):
        print("Xóa Xe")

# ==============================================================================
# 4. HÀM QUẢN LÝ TRẠNG THÁI NÚT BẤM VÀ FORM
# ==============================================================================
    def _show_vehicle_initial_buttons_(self):
        self.update_btn_x.pack_forget()
        self.cancel_btn_x.pack_forget()
        self.delete_btn_x.pack_forget()
        self.add_btn_x.pack(side="left", expand=True, fill="x")

    def _show_vehicle_edit_buttons(self):
        self.add_btn_x.pack_forget()
        self.update_btn_x.pack(side="left", expand=True, padx=(0, 5), fill="x")
        self.cancel_btn_x.pack(side="left", expand=True, padx=5, fill="x")
        self.delete_btn_x.pack(side="left", expand=True, padx=(5, 0), fill="x")
    
    def _show_initial_buttons(self):
        self.update_btn.pack_forget()
        self.cancel_btn.pack_forget()
        self.delete_btn.pack_forget()
        self.add_btn.pack(side="left", expand=True, fill="x")

    def _show_edit_buttons(self):
        self.add_btn.pack_forget()
        self.update_btn.pack(side="left", expand=True, padx=(0, 5), fill="x")
        self.cancel_btn.pack(side="left", expand=True, padx=5, fill="x")
        self.delete_btn.pack(side="left", expand=True, padx=(5, 0), fill="x")

    def clear_selection_and_form(self):
        """Xóa lựa chọn và form cho view hiện tại."""
        if self.current_view == "yards":
            if self.tree_y.selection():
                self.tree_y.selection_remove(self.tree_y.selection())
            for var in self.form_fields_y.values():
                var.set("")
            self.original_yard_data = None
        # elif self.current_view == "vehicles":
        #     if hasattr(self, 'add_btn_x'):
        #         self._show_initial_buttons(self.add_btn_x, self.update_btn_x, self.cancel_btn_x, self.delete_btn_x)
        
        self.selected_customer_id = None
        # Gọi hàm để hiển thị nút thêm khi chưa chọn dòng dữ liệu ở cả 2 giao diện
        self._show_initial_buttons()
        self._show_vehicle_initial_buttons_()