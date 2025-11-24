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
        self.selected_yard_id = None # Giữ lại biến này từ code cũ của bạn
        self.original_yard_data = None # Biến lưu dữ liệu gốc của bãi

        self.selected_vehicle_id = None
        self.original_vehicle_data = None
        
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
            command=self.switch_view,
            height=40, # Tăng chiều cao của nút
            width= 80, # Tăng chiều rộng của nút
            font=("Segoe UI", 15, "bold"), # Tăng cỡ chữ
            corner_radius=12,
            border_width=5, # Tạo khoảng cách 5px giữa các nút
            fg_color="white", # Đặt màu nền widget trùng với màu nền của frame cha
            selected_color="#3498db",
            selected_hover_color="#2980b9",
            unselected_color="grey", # Nền nút chưa chọn là màu trắng
            unselected_hover_color="#3498db", # Khi hover, nền giống nút đã chọn
            text_color=("black", "white") # (màu chữ chưa chọn, màu chữ đã chọn)
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
        display_cols = ("ten_bai", "dia_chi")
        self.tree_y = ttk.Treeview(left_frame, columns=columns, displaycolumns=display_cols, show="headings", selectmode="browse")
        self.tree_y.heading("id", text="ID"); self.tree_y.heading("ten_bai", text="Tên bãi"); self.tree_y.heading("dia_chi", text="Địa chỉ")
        self.tree_y.column("id", width=0, stretch=False); self.tree_y.column("ten_bai", width=250); self.tree_y.column("dia_chi", width=100)
        
        scrollbar_y = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree_y.yview)
        self.tree_y.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_y.pack(side="right", fill="y")
        self.tree_y.pack(expand=True, fill="both")
        self.tree_y.bind("<<TreeviewSelect>>", self.on_item_select)

        self.right_frame_y = tk.Frame(parent, bg="#f7f9fc", width=450)
        self.right_frame_y.pack(side="right", fill="both", padx=(0, 10), pady=10)
        self.right_frame_y.pack_propagate(False)

        # --- Frame chứa nút Thêm chính, luôn hiển thị ---
        add_button_container_y = tk.Frame(self.right_frame_y, bg="#f7f9fc")
        add_button_container_y.pack(pady=20, padx=20, fill="x")
        self.add_btn_y = ctk.CTkButton(add_button_container_y, text="Thêm bãi mới", command=self.add_yard_window, corner_radius=10, fg_color="#27ae60", font=("Segoe UI", 15, "bold"), height=30)
        self.add_btn_y.pack(expand=True, fill="x")

        # --- Frame chứa toàn bộ form chi tiết, có thể ẩn/hiện ---
        self.yard_details_container = tk.Frame(self.right_frame_y, bg="#f7f9fc")
        self.yard_details_container.pack(fill="both", expand=True, padx=20)

        tk.Label(self.yard_details_container, text="Thông tin chi tiết bãi", font=("Segoe UI", 16, "bold"), bg="#f7f9fc").pack(pady=(0, 20), anchor="w")

        self.form_fields_y = {"ID:": tk.StringVar(), "Tên bãi:": tk.StringVar(), "Địa chỉ:": tk.StringVar()}
        form_frame_y = tk.Frame(self.yard_details_container, bg="#f7f9fc")
        form_frame_y.pack(fill="x")
        for label_text, var in self.form_fields_y.items():
            row = tk.Frame(form_frame_y, bg="#f7f9fc"); row.pack(fill="x", pady=5)
            label = tk.Label(row, text=label_text, width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10)); label.pack(side="left")
            entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 10))
            if label_text == "ID:": entry.config(state="readonly", relief="flat", bg="#e9ecef")
            entry.pack(side="left", expand=True, fill="x")

        button_frame_y = tk.Frame(self.yard_details_container, bg="#f7f9fc")
        button_frame_y.pack(pady=20, fill="x")

        self.button_frame_y = button_frame_y

        self.update_btn_y = ctk.CTkButton(self.button_frame_y, text="Sửa", command=self.update_yard, corner_radius=10, fg_color="#f39c12", font=("Segoe UI", 15), width=100)
        self.cancel_btn_y = ctk.CTkButton(self.button_frame_y, text="Hủy", command=self.clear_selection_and_form, corner_radius=10, fg_color="#7f8c8d", font=("Segoe UI", 15), width=100)
        self.delete_btn_y = ctk.CTkButton(self.button_frame_y, text="Xóa", command=self.delete_yard, corner_radius=10, fg_color="#e74c3c", font=("Segoe UI", 15), width=100)

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
        self.selected_yard_id = values[0]

        # Kiểm tra xem có thể xóa bãi này không
        is_deletable = self.controller.check_yard_deletable(self.selected_yard_id)
        # Hiển thị form với trạng thái nút xóa tương ứng
        self._show_edit_buttons(show_delete=is_deletable)
    
    def add_yard_window(self):
        # Tạo cửa sổ thêm mặt hàng
        add_window = tk.Toplevel(self.root_window)
        add_window.title("Thêm bãi mới")
        
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

            # Kiểm tra dữ liệu đầu vào
            if not ten or not dia_chi:
                messagebox.showwarning("Thiếu thông tin", "Tên bãi, địa chỉ không được để trống!")
                return
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
        if not ten_bai or not dia_chi:
            messagebox.showerror("Lỗi", "Tên bãi, Địa chỉ không được để trống.")
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
            #    và kiểm tra kết quả trả về
            success = self.controller.update_yard(selected_id, ten_bai, dia_chi)
            
            # 7. CHỈ cập nhật Treeview và dữ liệu gốc NẾU controller báo thành công
            if success:
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
        if not selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một bãi để xóa!")
            return
        
        confirm = messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa bãi này !")
        if not confirm:
            return
        selected_tree_item = self.tree_y.selection()[0]
        self.controller.delete_yard(selected_id)
        # Xóa dòng khỏi Treeview và dọn dẹp form
        self.tree_y.delete(selected_tree_item)
        self.clear_selection_and_form()

    def clear_details_form(self):
        """Xóa toàn bộ nội dung trong các ô Entry của form chi tiết."""
        for var in self.form_fields_y.values():
            var.set("")
        self.original_yard_data = None
        self.selected_yard_id = None

# ==============================================================================
# 3. HÀM DÀNH CHO GIAO DIỆN "DANH SÁCH XE"
# ==============================================================================
    
    def create_vehicle_view(self, parent):
        left_frame = tk.Frame(parent, bg="white")
        left_frame.pack(side="left", fill="both", expand=True, padx=(10, 10), pady=10)

        tk.Label(left_frame, text="Danh sách xe", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=(0, 10), anchor="w")
        style = ttk.Style()
        style.configure("Treeview", rowheight=40, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        columns = ("id", "bien_so_xe")
        display_cols = ("bien_so_xe",)
        self.tree_x = ttk.Treeview(left_frame, columns=columns, displaycolumns=display_cols, show="headings", selectmode="browse")
        self.tree_x.heading("id", text="ID")
        self.tree_x.heading("bien_so_xe", text="Biển số xe")

        self.tree_x.column("id", width=0, stretch=False)
        self.tree_x.column("bien_so_xe", width=10, anchor= "center")
        
        scrollbar_x = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree_x.yview)
        self.tree_x.configure(yscrollcommand=scrollbar_x.set)
        scrollbar_x.pack(side="right", fill="y")
        self.tree_x.pack(expand=True, fill="both")
        self.tree_x.bind("<<TreeviewSelect>>", self.on_vehicle_select)

        self.right_frame_x = tk.Frame(parent, bg="#f7f9fc", width=450)
        self.right_frame_x.pack(side="right", fill="both", padx=(0, 10), pady=10)
        self.right_frame_x.pack_propagate(False)

        # --- Frame chứa nút Thêm chính, luôn hiển thị ---
        add_button_container_x = tk.Frame(self.right_frame_x, bg="#f7f9fc")
        add_button_container_x.pack(pady=20, padx=20, fill="x")
        self.add_btn_x = ctk.CTkButton(add_button_container_x, text="Thêm xe mới", command=self.add_vehicle_window, corner_radius=10, fg_color="#27ae60", font=("Segoe UI", 15, "bold"), height=30)
        self.add_btn_x.pack(expand=True, fill="x")

        # --- Frame chứa toàn bộ form chi tiết, có thể ẩn/hiện ---
        self.vehicle_details_container = tk.Frame(self.right_frame_x, bg="#f7f9fc")
        self.vehicle_details_container.pack(fill="both", expand=True, padx=20)

        tk.Label(self.vehicle_details_container, text="Thông tin chi tiết xe", font=("Segoe UI", 16, "bold"), bg="#f7f9fc").pack(pady=(0, 20), anchor="w")

        self.form_fields_x = {
            "ID:": tk.StringVar(), 
            "Biển số xe:": tk.StringVar()
            }
        form_frame_x = tk.Frame(self.vehicle_details_container, bg="#f7f9fc")
        form_frame_x.pack(fill="x")
        for label_text, var in self.form_fields_x.items():
            row = tk.Frame(form_frame_x, bg="#f7f9fc"); row.pack(fill="x", pady=5)
            label = tk.Label(row, text=label_text, width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10))
            label.pack(side="left")
            entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 10))
            if label_text == "ID:": entry.config(state="readonly", relief="flat", bg="#e9ecef")
            entry.pack(side="left", expand=True, fill="x")

        button_frame_x = tk.Frame(self.vehicle_details_container, bg="#f7f9fc")
        button_frame_x.pack(pady=20, fill="x")

        self.button_frame_x = button_frame_x

        self.update_btn_x = ctk.CTkButton(self.button_frame_x, text="Sửa", command=self.update_vehicle, corner_radius=10, fg_color="#f39c12", font=("Segoe UI", 15), width=100)
        self.cancel_btn_x = ctk.CTkButton(self.button_frame_x, text="Hủy", command=self.clear_selection_and_form, corner_radius=10, fg_color="#7f8c8d", font=("Segoe UI", 15), width=100)
        self.delete_btn_x = ctk.CTkButton(self.button_frame_x, text="Xóa", command=self.delete_vehicle, corner_radius=10, fg_color="#e74c3c", font=("Segoe UI", 15), width=100)

    # Hàm tải dữ liệu
    def load_vehicles_data(self, data):
        for item in self.tree_x.get_children():
            self.tree_x.delete(item)
        for item in data:
            self.tree_x.insert("", "end", values=item)

    def on_vehicle_select(self, event):
        if self.current_view != "vehicles": return # Chỉ chạy khi đang ở view bãi
        selected_items = self.tree_x.selection()
        if not selected_items: return
        values = self.tree_x.item(selected_items[0], "values")

        self.original_vehicle_data = values # Lưu dữ liệu gốc khi chọn
        
        self.form_fields_x["ID:"].set(values[0])
        self.form_fields_x["Biển số xe:"].set(values[1])

        self.selected_vehicle_id = values[0]

        # Kiểm tra xem có thể xóa xe này không
        is_deletable = self.controller.check_vehicle_deletable(self.selected_vehicle_id)
        # Hiển thị form với trạng thái nút xóa tương ứng
        self._show_vehicle_edit_buttons(show_delete=is_deletable)

    def add_vehicle_window(self):
        # Tạo cửa sổ thêm mặt hàng
        add_window = tk.Toplevel(self.root_window)
        add_window.title("Thêm xe mới")
        
        window_width = 400
        window_height = 150

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
        "Biển số xe:": tk.StringVar(),
        }

        for label_text, var in add_fields.items():
            row = tk.Frame(form_add, bg="#f7f9fc")
            row.pack(fill="x", pady=8)

            label = tk.Label(row, text=label_text, width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10))
            label.pack(side="left")

            entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 10))
            entry.pack(side="left", expand=True, fill="x") 
            
        # Hàm lưu mặt hàng mới
        def save_new_vehicle():
            bien_so = add_fields["Biển số xe:"].get().strip()

            # Kiểm tra dữ liệu đầu vào
            if not bien_so:
                messagebox.showwarning("Thiếu thông tin", "Biển số xe không được để trống !")
                return

            # Gọi phương thức add_item từ controller
            success = self.controller.add_vehicle(bien_so)
            if success:
                add_window.destroy()

        def close_add_window():
            add_window.destroy()

        # Nút lưu và hủy
        button_frame_add = tk.Frame(form_add, bg="#f7f9fc")
        button_frame_add.pack(fill="x", pady=(20, 0))

        add_btn = ctk.CTkButton(button_frame_add, text="Lưu", command=save_new_vehicle, fg_color="#2ecc71", font=("Segoe UI", 15, "bold"), width=100)
        add_btn.pack(side="right", padx=5)

        cancel_btn = ctk.CTkButton(button_frame_add, text="Hủy", command=close_add_window, fg_color="#e74c3c", font=("Segoe UI", 15, "bold"), width=100)
        cancel_btn.pack(side="right")

    def update_vehicle(self):
        # 1. Kiểm tra xem có bãi nào được chọn trong form không
        selected_id = self.form_fields_x["ID:"].get()
        if not selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một xe để sửa!")
            return

        # 2. Lấy dữ liệu đã được người dùng chỉnh sửa từ các ô Entry
        bien_so = self.form_fields_x["Biển số xe:"].get().strip()

        # 3. So sánh dữ liệu mới với dữ liệu gốc
        if self.original_vehicle_data:
            _, original_vehicle = self.original_vehicle_data
            if (bien_so == original_vehicle):
                messagebox.showinfo("Thông báo", "Không có thay đổi nào để cập nhật.")
                return

        # 4. Kiểm tra dữ liệu đầu vào (ví dụ: tên không được để trống)
        if not bien_so:
            messagebox.showerror("Lỗi", "Tên bãi không được để trống.")
            return

        # 5. Yêu cầu xác nhận từ người dùng
        confirm = messagebox.askyesno(
            "Xác nhận sửa", 
            "Xác nhận thay đổi thông tin xe?"
        )
        
        if not confirm:
            return # Nếu người dùng chọn "No", không làm gì cả

        try:
            # 6. Gọi phương thức update_yard từ controller để lưu vào database
            success = self.controller.update_vehicle(selected_id, bien_so)
            
            # 7. CHỈ cập nhật Treeview và dữ liệu gốc NẾU controller báo thành công
            if success:
                selection = self.tree_x.selection()
                if selection:            
                    selected_item = self.tree_x.selection()[0]
                    self.tree_x.item(selected_item, values=(selected_id, bien_so))
                    # Cập nhật lại dữ liệu gốc sau khi đã lưu thành công
                    self.original_vehicle_data = (selected_id, bien_so)

        except Exception as e:
            # Bắt lỗi nếu có sự cố xảy ra và thông báo cho người dùng
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi cập nhật: {e}")

    def delete_vehicle(self):
        selected_id = self.form_fields_x["ID:"].get()
        if not selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một xe để xóa !")
            return
        
        confirm = messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa xe này !")
        if not confirm:
            return
        selected_tree_item = self.tree_x.selection()[0]
        self.controller.delete_vehicle(selected_id)
        # Xóa dòng khỏi Treeview và dọn dẹp form
        self.tree_x.delete(selected_tree_item)
        self.clear_selection_and_form()

    def clear_vehicle_detail_form(self):
        """Xóa toàn bộ nội dung trong các ô Entry của form chi tiết."""
        for var in self.form_fields_x.values():
            var.set("")
        self.original_vehicle_data = None
        self.selected_vehicle_id = None

# ==============================================================================
# 4. HÀM QUẢN LÝ TRẠNG THÁI NÚT BẤM VÀ FORM
# ==============================================================================
    def _show_vehicle_initial_buttons(self, show_delete=False):
        """Ẩn form chi tiết xe và chỉ hiển thị nút Thêm xe."""
        self.vehicle_details_container.pack_forget()
        self.add_btn_x.pack(expand=True, fill="x")

    def _show_vehicle_edit_buttons(self, show_delete=True):
        """Hiển thị form chi tiết xe và các nút Sửa, Hủy, Xóa."""
        self.add_btn_x.pack_forget()
        self.vehicle_details_container.pack(fill="both", expand=True, padx=20)
        self.update_btn_x.pack(side="left", expand=True, padx=(0, 5), fill="x")
        self.cancel_btn_x.pack(side="left", expand=True, padx=5, fill="x")
        
        if show_delete:
            self.delete_btn_x.pack(side="left", expand=True, padx=(5, 0), fill="x")
        else:
            self.delete_btn_x.pack_forget()
    
    def _show_initial_buttons(self, show_delete=False):
        """Ẩn form chi tiết bãi và chỉ hiển thị nút Thêm bãi."""
        self.yard_details_container.pack_forget()
        self.add_btn_y.pack(expand=True, fill="x")

    def _show_edit_buttons(self, show_delete=True):
        """Hiển thị form chi tiết bãi và các nút Sửa, Hủy, Xóa."""
        self.add_btn_y.pack_forget()
        self.yard_details_container.pack(fill="both", expand=True, padx=20)
        self.update_btn_y.pack(side="left", expand=True, padx=(0, 5), fill="x")
        self.cancel_btn_y.pack(side="left", expand=True, padx=5, fill="x")
        
        if show_delete:
            self.delete_btn_y.pack(side="left", expand=True, padx=(5, 0), fill="x")
        else:
            self.delete_btn_y.pack_forget()

    def clear_selection_and_form(self):
        """Xóa lựa chọn và form cho view hiện tại."""
        if self.current_view == "yards":
            if self.tree_y.selection():
                self.tree_y.selection_remove(self.tree_y.selection())
            for var in self.form_fields_y.values():
                var.set("")
            self.original_yard_data = None
            self._show_initial_buttons()
        elif self.current_view == "vehicles":
            if self.tree_x.selection():
                self.tree_x.selection_remove(self.tree_x.selection())
            for var in self.form_fields_x.values():
                var.set("")
            self.original_vehicle_data = None
        
        self.selected_yard_id = None
        self.selected_vehicle_id = None
        self._show_vehicle_initial_buttons()