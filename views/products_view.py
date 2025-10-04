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
        self.selected_item_id = None
        self.original_item_data = None
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

        columns = ("id", "ten_mat_hang", "don_vi_gia", "ten_bai")
        self.tree_mh = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse")

        self.tree_mh.heading("id", text="ID")
        self.tree_mh.heading("ten_mat_hang", text="Tên mặt hàng")
        self.tree_mh.heading("don_vi_gia", text="Đơn vị : Giá")

        self.tree_mh.column("id", width=50, anchor="center")
        self.tree_mh.column("ten_mat_hang", width=200)
        self.tree_mh.column("don_vi_gia", width=300)
        self.tree_mh.column("ten_bai", width=0, stretch=False)

        # Thanh cuộn
        scrollbar_mh = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree_mh.yview)
        self.tree_mh.configure(yscrollcommand=scrollbar_mh.set)
        scrollbar_mh.pack(side="right", fill="y")
        self.tree_mh.pack(expand=True, fill="both")
        
        # Gán sự kiện chọn dòng
        self.tree_mh.bind("<<TreeviewSelect>>", self.on_item_select)

        # Form thông tin chi tiết
        right_frame = tk.Frame(self, bg="#f7f9fc", width=550)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)

        # --- Frame chứa nút Thêm chính, luôn hiển thị ---
        add_button_container = tk.Frame(right_frame, bg="#f7f9fc")
        add_button_container.pack(pady=20, padx=20, fill="x")
        self.add_btn = ctk.CTkButton(add_button_container, text="Thêm mặt hàng", command=self.add_item_window, corner_radius=10, fg_color="#27ae60", font=("Segoe UI", 15, "bold"), height=30)
        self.add_btn.pack(expand=True, fill="x")

        # --- Frame chứa toàn bộ form chi tiết, có thể ẩn/hiện ---
        self.details_container = tk.Frame(right_frame, bg="#f7f9fc")
        self.details_container.pack(fill="both", expand=True, padx=20)

        tk.Label(self.details_container, text="Thông tin chi tiết", font=("Segoe UI", 16, "bold"), bg="#f7f9fc").pack(pady=(0, 20), anchor="w")

        self.form_fields_mh = {
            "ID:": tk.StringVar(),
            "Tên mặt hàng:": tk.StringVar(),
            "Bãi:": tk.StringVar()
        }
        form_frame = tk.Frame(self.details_container, bg="#f7f9fc")
        form_frame.pack(fill="x")

        for label_text, var in self.form_fields_mh.items():
            row = tk.Frame(form_frame, bg="#f7f9fc")
            row.pack(fill="x", pady=5)

            label = tk.Label(row, text=label_text, width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10))
            label.pack(side="left")

            if label_text == "Bãi:":
                self.yard_combobox_mh = ttk.Combobox(row, textvariable=var, font=("Segoe UI", 10))
                self.yard_combobox_mh.config(state="disabled")
                self.yard_combobox_mh.pack(side="left", expand=True, fill="x")
            else:
                entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 10))
                if label_text == "ID:":
                    entry.config(state="readonly", relief="flat", bg="#e9ecef")
                entry.pack(side="left", expand=True, fill="x") 

        # --- Frame cho các cặp Đơn vị - Giá (thay thế cho các entry cũ) ---
        self.prices_frame_mh = tk.Frame(form_frame, bg="#f7f9fc")
        self.prices_frame_mh.pack(fill="x", pady=5)
        self.detail_price_entries = [] # List để lưu các cặp entry Đơn vị/Giá

        # Nút để thêm dòng giá mới (ban đầu bị ẩn)
        self.add_price_row_btn = ctk.CTkButton(
            form_frame,
            text="+ Thêm đơn vị/giá",
            command=self._add_price_row_to_details,
            fg_color="#3498db",
            font=("Segoe UI", 10),
            height=30,
            width=150
        )
        # --- Frame cho các nút Sửa/Hủy/Xóa ---
        button_frame = tk.Frame(self.details_container, bg="#f7f9fc")
        button_frame.pack(pady=20, fill="x")
        
        self.button_frame = button_frame

        self.update_btn = ctk.CTkButton(self.button_frame, text="Sửa", command=self.update_item, corner_radius=10, fg_color="#f39c12", font=("Segoe UI", 15), width=100)
        self.cancel_btn = ctk.CTkButton(self.button_frame, text="Hủy", command=self.clear_selection_and_form, corner_radius=10, fg_color="#7f8c8d", font=("Segoe UI", 15), width=100)
        self.delete_btn = ctk.CTkButton(self.button_frame, text="Xóa", command=self.delete_item, corner_radius=10, fg_color="#e74c3c", font=("Segoe UI", 15), width=100)

        self._show_initial_buttons()

    def _show_initial_buttons(self):
        """Ẩn form chi tiết và chỉ hiển thị nút Thêm chính."""
        self.details_container.pack_forget()
        self.add_btn.pack(expand=True, fill="x")

    def _show_edit_buttons(self):
        """Hiển thị form chi tiết và các nút Sửa, Hủy, Xóa."""
        self.add_btn.pack_forget()
        self.details_container.pack(fill="both", expand=True, padx=20)
        self.update_btn.pack(side="left", expand=True, pady=5)
        self.cancel_btn.pack(side="left", expand=True, pady=5, padx=10)
        self.delete_btn.pack(side="left", expand=True, pady=5)
        self.add_price_row_btn.pack(pady=(15, 5)) # Thêm khoảng cách trên

    # Xóa lựa chọn trên Treeview, xóa form và đặt lại các nút
    def clear_selection_and_form(self):
        """Xóa lựa chọn trên Treeview, xóa form và đặt lại các nút."""
        if self.tree_mh.selection():
            self.tree_mh.selection_remove(self.tree_mh.selection()[0])
        self.clear_details_form()
        self._show_initial_buttons()
        self.selected_item_id = None    
        self.yard_combobox_mh.config(state="disabled")

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

    # Hàm này sẽ được gọi từ Controller để lấy danh sách bãi
    def set_yard_list(self, load_yards):
        self.display_yard_info = []
        self.display_yard_info = load_yards

        # Cập nhật 
        try:
            # Trích xuất chỉ tên bãi
            yard_names = [yard[1] for yard in self.display_yard_info]
            
            # Cập nhật danh sách giá trị cho Combobox
            # Dùng `hasattr` để kiểm tra xem combobox đã được tạo chưa, tránh lỗi khi khởi tạo
            if hasattr(self, 'yard_combobox_mh'):
                self.yard_combobox_mh['values'] = yard_names
            
            # Tạo một "map" để tra cứu ID từ tên bãi sau này
            # Giả sử ID ở index 0 và tên bãi ở index 1
            self.yard_map = {yard[1]: yard[0] for yard in self.display_yard_info}

        except IndexError:
            messagebox.showerror("Lỗi dữ liệu", "Định dạng dữ liệu bãi không đúng. Không thể cập nhật dropdown.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật danh sách bãi: {e}")
    
    # Chọn một mặt hàng trong Treeview và cập nhật thông tin vào các ô Entry
    def on_item_select(self, event):
        selected_items = self.tree_mh.selection()
        if not selected_items:
            return
        
        self.yard_combobox_mh.config(state="readonly")

        # item_id_in_tree = selected_items[0]
        values = self.tree_mh.item(selected_items[0], "values")

        # lưu giá trị đang được chọn
        self.original_item_data = values

        # Xóa các dòng đơn vị/giá cũ trước khi tạo mới
        self.clear_price_entries()

        # Tách dữ liệu ra các biến riêng
        item_id = values[0]
        ten_sp = values[1]
        unit_price_str = values[2] # "m3 : 150.000 | xe : 2.000.000"
        ten_bai = values[3] or ''

        # Điền dữ liệu chung
        self.form_fields_mh["ID:"].set(item_id)
        self.form_fields_mh["Tên mặt hàng:"].set(ten_sp)
        self.form_fields_mh["Bãi:"].set(ten_bai)

        # Xử lý và hiển thị các cặp đơn vị/giá
        if unit_price_str and unit_price_str != "Lỗi định dạng":
            pairs = unit_price_str.split('|')
            for pair in pairs:
                parts = pair.split(':')
                if len(parts) == 2:
                    unit = parts[0].strip()
                    price = parts[1].strip()
                    self._add_price_row_to_details(unit, price)

        # Gán dữ liệu lại cho biến dữ diệu gốc
        self.original_item_data = (item_id, ten_sp, unit_price_str, ten_bai)
        self.selected_item_id = values[0]
        self._show_edit_buttons()

    # Tạo nút bấm 1 lần
    # def _create_main_buttons(self):
    #     """Tạo các nút bấm chính một lần duy nhất."""
    #     button_frame = tk.Frame(right_frame, bg="#f7f9fc")
    #     button_frame.pack(pady=30, padx=20, fill="x")
        
    #     self.button_frame = button_frame

    #     self.add_btn = ctk.CTkButton(self.button_frame, text="Thêm", command=self.add_item_window, corner_radius=10, fg_color="#27ae60", font=("Segoe UI", 15), width=100)
    #     self.update_btn = ctk.CTkButton(self.button_frame, text="Sửa", command=self.update_item, corner_radius=10, fg_color="#f39c12", font=("Segoe UI", 15), width=100)
    #     self.cancel_btn = ctk.CTkButton(self.button_frame, text="Hủy", command=self.clear_selection_and_form, corner_radius=10, fg_color="#7f8c8d", font=("Segoe UI", 15), width=100)
    #     self.delete_btn = ctk.CTkButton(self.button_frame, text="Xóa", command=self.delete_item, corner_radius=10, fg_color="#e74c3c", font=("Segoe UI", 15), width=100)

    #     self._show_initial_buttons()

    # Thêm mặt hàng mới
    def add_item_window(self):
        # Tạo cửa sổ thêm mặt hàng
        add_window = tk.Toplevel(self.root_window)
        add_window.title("Thêm mặt hàng mới")
        # Kích thước cửa sổ
        window_width = 550
        window_height = 450
        # Lấy kích thước màn hình
        screen_width = add_window.winfo_screenwidth()
        screen_height = add_window.winfo_screenheight()
        # Tính toán vị trí để căn giữa
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        # Gán geometry với cả kích thước và vị trí
        add_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        add_window.resizable(False, False)  # Không cho phép thay đổi kích thước
        add_window.configure(bg="#f7f9fc")
        add_window.transient(self.root_window)  # Cửa sổ luôn ở trên cùng
        add_window.grab_set()

        # Frame chứa form 
        form_add = tk.Frame(add_window, bg="#f7f9fc", padx=20, pady=20)
        form_add.pack(expand=True, fill="both")

        # --- Tên mặt hàng ---
        ten_mh_row = tk.Frame(form_add, bg="#f7f9fc")
        ten_mh_row.pack(fill="x", pady=8)
        tk.Label(ten_mh_row, text="Tên mặt hàng:", width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10)).pack(side="left")
        ten_mh_var = tk.StringVar()
        tk.Entry(ten_mh_row, textvariable=ten_mh_var, font=("Segoe UI", 10)).pack(side="left", expand=True, fill="x")

        # --- Chọn bãi ---
        yard_names = [yard[1] for yard in self.display_yard_info]
        yard_row = tk.Frame(form_add, bg="#f7f9fc")
        yard_row.pack(fill="x", pady=8)
        yard_label = tk.Label(yard_row, text="Bãi:", width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10))
        yard_label.pack(side="left")
        yard_var = tk.StringVar()
        yard_options = ["Không có bãi"] + yard_names
        yard_combo = ttk.Combobox(yard_row, textvariable=yard_var, values=yard_options, state="readonly", font=("Segoe UI", 10))
        yard_combo.pack(side="left", expand=True, fill="x")
        yard_combo.set("Không có bãi")

        # --- Frame cho các cặp Đơn vị - Giá ---
        prices_frame = tk.Frame(form_add, bg="#f7f9fc")
        prices_frame.pack(fill="x", pady=8)
        price_entries = []

        def add_price_row():
            row = tk.Frame(prices_frame, bg="#f7f9fc")
            row.pack(fill="x", pady=4)

            tk.Label(
                row, text="Đơn vị:", width=12, anchor="w",
                bg="#f7f9fc", font=("Segoe UI", 10)
            ).pack(side="left")

            # Tăng width từ 10 → 20 để rộng hơn
            don_vi_entry = tk.Entry(row, font=("Segoe UI", 10), width=20)
            don_vi_entry.pack(side="left", padx=(0, 10))

            tk.Label(
                row, text="Giá:", anchor="w",
                bg="#f7f9fc", font=("Segoe UI", 10)
            ).pack(side="left")

            gia_entry = tk.Entry(row, font=("Segoe UI", 10))
            gia_entry.pack(side="left", expand=True, fill="x")

            price_entries.append({'don_vi': don_vi_entry, 'gia': gia_entry, 'frame': row})

        # Thêm dòng đầu tiên
        add_price_row()

        # Nút thêm dòng giá
        add_row_btn = ctk.CTkButton(
            form_add,
            text="+ Thêm đơn vị/giá",
            command=add_price_row,
            fg_color="#3498db",
            font=("Segoe UI", 10),
            height=30,
            width=180
        )
        add_row_btn.pack(pady=10)

        # Hàm lưu mặt hàng mới
        def save_new_item():
            ten = ten_mh_var.get().strip()
            bai = yard_var.get()

            if not ten:
                messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên mặt hàng!")
                return

            # Lấy id_bai nếu có chọn bãi
            id_bai = None
            if bai != "Không có bãi":
                for yard in self.display_yard_info:
                    if yard[1] == bai:
                        id_bai = yard[0]
                        break

            units_list = []
            prices_list = []
            for entry_pair in price_entries:
                donvi = entry_pair['don_vi'].get().strip()
                gia_str = entry_pair['gia'].get().replace(".", "").replace(",", "").strip()

                if donvi and gia_str:
                    try:
                        # Thêm vào danh sách
                        units_list.append(donvi)
                        prices_list.append(int(gia_str))
                    except ValueError:
                        messagebox.showerror("Lỗi", f"Giá '{gia_str}' không phải là số hợp lệ. Vui lòng kiểm tra lại.")
                        return # Dừng lại nếu có lỗi
                elif donvi or gia_str: # Nếu chỉ điền 1 trong 2
                    messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đủ cả Đơn vị và Giá cho mỗi dòng.")
                    return

            if not units_list:
                messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập ít nhất một cặp Đơn vị và Giá.")
                return

            # Gọi controller một lần duy nhất với danh sách đơn vị và giá
            self.controller.add_item(id_bai, ten, units_list, prices_list)

            close_add_window()
        
        def close_add_window():
            add_window.destroy()

        # Nút lưu và hủy
        button_frame_add = tk.Frame(form_add, bg="#f7f9fc")
        button_frame_add.pack(fill="x", pady=(10, 0), side="bottom")

        add_btn = ctk.CTkButton(button_frame_add, text="Lưu", command=save_new_item, fg_color="#2ecc71", font=("Segoe UI", 10, "bold"), width=100)
        add_btn.pack(side="right", padx=5)

        cancel_btn = ctk.CTkButton(button_frame_add, text="Hủy", command=close_add_window, fg_color="#e74c3c", font=("Segoe UI", 10, "bold"), width=100)
        cancel_btn.pack(side="right")

    # Hàm tạo thêm đơn vị/giá cho form thông tin chi tiết
    def _add_price_row_to_details(self, unit="", price=""):
        """Hàm helper để thêm một dòng nhập đơn vị/giá vào form chi tiết."""
        row = tk.Frame(self.prices_frame_mh, bg="#f7f9fc")
        row.pack(fill="x", pady=4)

        tk.Label(row, text="Đơn vị:", width=12, anchor="w", bg="#f7f9fc", font=("Segoe UI", 10)).pack(side="left")
        don_vi_entry = tk.Entry(row, font=("Segoe UI", 10), width=15)
        don_vi_entry.pack(side="left", padx=(0, 10))
        don_vi_entry.insert(0, unit)

        tk.Label(row, text="Giá:", anchor="w", bg="#f7f9fc", font=("Segoe UI", 10)).pack(side="left")
        gia_entry = tk.Entry(row, font=("Segoe UI", 10))
        gia_entry.pack(side="left", expand=True, fill="x")
        gia_entry.insert(0, price)

        remove_btn = ctk.CTkButton(
        row, 
        text="-", 
        width=25, 
        height=20,
        font=("Segoe UI", 12),
        fg_color="#e74c3c", # Màu đỏ
        hover_color="#c0392b",
        # Dùng lambda để truyền `row` vào hàm xóa
        command=lambda r=row: self.remove_price_row(r)
        )
        remove_btn.pack(side="left", padx=(5, 0))

        self.detail_price_entries.append({'don_vi': don_vi_entry, 'gia': gia_entry, 'frame': row, 'button': remove_btn})

    # Hàm xóa dòng giá ở form chi tiết
    def remove_price_row(self, row):
        # Tìm index của dictionary chứa frame cần xóa
        index_to_remove = -1
        for i, entry_data in enumerate(self.detail_price_entries):
            if entry_data['frame'] == row:
                index_to_remove = i
                break
                
        # Nếu tìm thấy, xóa nó khỏi danh sách
        if index_to_remove != -1:
            self.detail_price_entries.pop(index_to_remove)
        
        # Hủy frame đó khỏi giao diện
        row.destroy()

    def update_item(self):
        selected_id = self.form_fields_mh["ID:"].get()
        if not selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một mặt hàng để sửa!")
            return

        ten_sp = self.form_fields_mh["Tên mặt hàng:"].get().strip()
        ten_bai = self.form_fields_mh["Bãi:"].get()

        if not ten_sp:
            messagebox.showwarning("Thiếu thông tin", "Tên mặt hàng không được để trống!")
            return

        # Lấy id_bai từ tên bãi
        id_bai = self.yard_map.get(ten_bai)

        # Thu thập các cặp đơn vị và giá từ các ô entry
        units_list = []
        prices_list = []
        for entry_pair in self.detail_price_entries:
            unit = entry_pair['don_vi'].get().strip()
            price_str = entry_pair['gia'].get().replace(".", "").replace(",", "").strip()

            if unit and price_str:
                try:
                    units_list.append(unit)
                    prices_list.append(str(int(price_str))) # Chuyển về chuỗi số nguyên
                except ValueError:
                    messagebox.showerror("Lỗi", f"Giá '{price_str}' không phải là số hợp lệ.")
                    return
            elif unit or price_str:
                messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đủ cả Đơn vị và Giá cho mỗi dòng.")
                return

        if not units_list:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập ít nhất một cặp Đơn vị và Giá.")
            return

        # Ghép thành chuỗi để so sánh và gửi đi
        units_str = "|".join(units_list)
        prices_str = "|".join(prices_list)

        # Tạo chuỗi đơn vị/giá mới để so sánh với chuỗi gốc
        new_formatted_pairs = []
        for unit, price in zip(units_list, prices_list):
            formatted_price = f"{int(price):,}".replace(",", ".")
            new_formatted_pairs.append(f"{unit} : {formatted_price}")
        unit_price_str = " | ".join(new_formatted_pairs)

        # So sánh với dữ liệu gốc
        if self.original_item_data:
            _, original_ten, original_unit_price_str, original_bai = self.original_item_data
            # So sánh dữ liệu mới với dữ liệu gốc
            if (ten_sp == original_ten and unit_price_str == original_unit_price_str and ten_bai == original_bai):
                messagebox.showinfo("Thông báo", "Không có thay đổi nào để cập nhật.")
                return

        confirm = messagebox.askyesno("Xác nhận sửa", "Xác nhận thay đổi thông tin mặt hàng này?")

        if not confirm:
            return

        # Cập nhật lại dữ liệu gốc sau khi xác nhận và trước khi gửi đi
        # để nếu người dùng bấm sửa lần nữa mà không thay đổi gì, nó sẽ không gửi lại
        self.original_item_data = (selected_id, ten_sp, unit_price_str, ten_bai)

        try:
            # Gọi controller với dữ liệu mới
            self.controller.update_item(selected_id, id_bai, ten_sp, units_str, prices_str)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi cập nhật: {e}")
    
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
        
    # Hàm để xóa các dòng nhập đơn vị/giá sau khi chọn sản phẩm khác
    def clear_price_entries(self):
        """Xóa các dòng nhập đơn vị/giá trong form chi tiết."""
        for entry_pair in self.detail_price_entries:
            entry_pair['frame'].destroy()
        self.detail_price_entries.clear()

    # Xóa dữ liệu trong các ô entry
    def clear_details_form(self):
        """Xóa toàn bộ nội dung trong các ô Entry của form chi tiết."""
        for var in self.form_fields_mh.values():
            var.set("")
        self.clear_price_entries()
        self.original_item_data = None