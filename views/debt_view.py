import tkinter as tk
from tkinter import ttk
from tkinter import messagebox # Import messagebox để hiện thông báo
import customtkinter as ctk
from datetime import datetime
from tkcalendar import DateEntry
from tkinter import font
from controllers.debt_controller import DebtController

class CongNoView(tk.Frame):
    def __init__(self, parent, root_window):
        super().__init__(parent, bg="white")
        
        self.root_window = root_window # Lưu lại cửa sổ gốc để dùng cho Toplevel
        

        # Gọi phương thức để tạo tất cả các widget
        self.create_widgets()
        
        self.debt_controller = DebtController(view=self, db_path=getattr(root_window, "db_path", None))

        # Tải dữ liệu ban đầu
        self.debt_controller.load_debts()

    # Phương thức để tạo các widget trong frame 
    def create_widgets(self):

        # --- Cấu hình layout chính: 2 cột ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3) # Cột trái (danh sách) chiếm nhiều không gian hơn
        self.grid_columnconfigure(1, weight=2) # Cột phải (cập nhật)

        # --- 1. Frame bên trái: Danh sách công nợ ---
        left_frame = tk.Frame(self, bg="white", padx=10, pady=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_rowconfigure(2, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # -- Thanh tìm kiếm --
        search_frame = ctk.CTkFrame(left_frame, fg_color="white")
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(0, weight=1)
        
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
        search_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Bind sự kiện KeyRelease thay vì dùng trace
        search_entry.bind("<KeyRelease>", self.filter_data)

        # -- Label danh sách --
        tk.Label(left_frame, text="Danh sách công nợ", font=("Segoe UI", 14, "bold"), bg="white").grid(row=1, column=0, sticky="w", pady=(5, 5))

        # -- Bảng danh sách công nợ --
        tree_container = tk.Frame(left_frame)
        tree_container.grid(row=2, column=0, sticky="nsew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        cols = ("ten_kh", "no_cu", "da_thanh_toan", "tong_no", "ngay_cap_nhat")
        self.tree_cn = ttk.Treeview(tree_container, columns=cols, show="headings", selectmode="browse")
        self.tree_cn.heading("ten_kh", text="Tên khách hàng")
        self.tree_cn.heading("no_cu", text="Nợ cũ")
        self.tree_cn.heading("da_thanh_toan", text="Đã thanh toán")
        self.tree_cn.heading("tong_no", text="Tổng nợ")
        self.tree_cn.heading("ngay_cap_nhat", text="Ngày cập nhật")

        # Định dạng cột
        for col in cols:
            if col != "ten_kh":
                self.tree_cn.column(col, width=120, anchor="e") # Căn phải cho các cột số
                scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree_cn.yview)
                self.tree_cn.configure(yscrollcommand=scrollbar.set)
                self.tree_cn.grid(row=0, column=0, sticky="nsew")
                scrollbar.grid(row=0, column=1, sticky="ns")
                style = ttk.Style()
                style.configure("Bold.Treeview", font=("TkDefaultFont", 10, "bold"))

                # Áp dụng style cho toàn bộ Treeview
                self.tree_cn.configure(style="Bold.Treeview")
                self.tree_cn.bind("<<TreeviewSelect>>", self.on_cong_no_select)

                # --- 2. Frame bên phải: Thông tin cập nhật ---
                right_frame = tk.Frame(self, bg="#f7f9fc", padx=20, pady=10)
                right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
                right_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(right_frame, text="Thông tin cập nhật", font=("Segoe UI", 14, "bold"), bg="#f7f9fc").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # -- Các trường thông tin --
        self.update_fields_vars = {
            "Tên khách hàng:": tk.StringVar(),
            "Công nợ hiện tại:": tk.StringVar(),
            "Đã thanh toán:": tk.StringVar(),
            "Ngày thanh toán:": tk.StringVar()
        }
        
        # Tên khách hàng (chỉ đọc)
        tk.Label(right_frame, text="Tên khách hàng:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(right_frame, textvariable=self.update_fields_vars["Tên khách hàng:"], state="readonly", font=("Segoe UI", 10)).grid(row=1, column=1, sticky="ew", pady=5)
        
        # Công nợ hiện tại (chỉ đọc, được tính toán)
        tk.Label(right_frame, text="Công nợ hiện tại:", font=("Segoe UI", 10, "bold"), bg="#f7f9fc").grid(row=2, column=0, sticky="w", pady=5)
        tk.Label(right_frame, textvariable=self.update_fields_vars["Công nợ hiện tại:"], font=("Segoe UI", 11, "bold"), bg="#f7f9fc").grid(row=2, column=1, sticky="w", pady=5)
        
        # Nhập số tiền đã thanh toán (đây là ô người dùng nhập)
        tk.Label(right_frame, text="Đã thanh toán:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=3, column=0, sticky="w", pady=5)
        self.thanh_toan_entry = tk.Entry(right_frame, textvariable=self.update_fields_vars["Đã thanh toán:"], font=("Segoe UI", 10))
        self.thanh_toan_entry.grid(row=3, column=1, sticky="ew", pady=5)
        self.thanh_toan_entry.bind("<KeyRelease>", self.format_thanh_toan_entry)  # Bind sự kiện KeyRelease để định dạng số

        # Cập nhật lần cuối (chỉ đọc)
        tk.Label(right_frame, text="Cập nhật lần cuối:", font=("Segoe UI", 10), bg="#f7f9fc").grid(row=4, column=0, sticky="w", pady=5)
        # tk.Entry(right_frame, textvariable=self.update_fields_vars["Ngày thanh toán:"], state="readonly", font=("Segoe UI", 10)).grid(row=4, column=1, sticky="ew", pady=5)
        self.date_entry = DateEntry(
            right_frame,
            date_pattern="dd/mm/yyyy",
            font=("Segoe UI", 10)
        )
        self.date_entry.grid(row=4, column=1, sticky="ew", pady=5)

        # -- Frame nút bấm --
        # Tạo một frame cho các button
        button_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        button_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=20)

        # Button "Cập nhật" với bo góc
        ctk.CTkButton(
            button_frame,
            text="Cập nhật",
            command=self.update_cong_no,
            font=("Segoe UI", 11, "bold"),
            fg_color="#2ecc71",
            corner_radius=10,  
            height=30,        
            width=100        
        ).pack(side="right", padx=5)

        # Button "Chuyển tiếp" với bo góc
        ctk.CTkButton(
            button_frame,
            text="Chuyển tiếp >",
            font=("Segoe UI", 11),
            fg_color="#f39c12",
            text_color="white", # Đổi màu chữ để dễ nhìn
            corner_radius=10,  # Thêm bo góc
            height=30,
            width=100,
            command=self.next_customer
        ).pack(side="right", padx=5)

    # --- Các phương thức xử lý sự kiện ---

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
        search_term = self.search_var.get().lower().strip()
        
        # Xóa hết các dòng hiện tại
        for i in self.tree_cn.get_children():
            self.tree_cn.delete(i)
            
        # Nếu không có từ khóa tìm kiếm, hiển thị tất cả
        if not search_term:
            for item in self.cong_no_data:
                self.insert_cong_no_item(item)
            return
                
        # Lọc và hiển thị các dòng phù hợp
        for item in self.cong_no_data:
            if search_term in item[1].lower():
                self.insert_cong_no_item(item)

    # Phương thức thêm một dòng công nợ vào Treeview
    def insert_cong_no_item(self, item):
        id_cn, ten, cong_no_cu, cong_no_dtt, tong_cong_no, ngay_cap_nhat = item
        
        # Format số tiền với dấu chấm phân cách hàng nghìn
        cong_no_cu_fmt = f"{cong_no_cu:,}".replace(",", ".") if cong_no_cu else "0"
        cong_no_dtt_fmt = f"{cong_no_dtt:,}".replace(",", ".") if cong_no_dtt else "0"
        tong_cong_no_fmt = f"{tong_cong_no:,}".replace(",", ".") if tong_cong_no else "0"
        
        # Thêm dòng mới vào Treeview
        self.tree_cn.insert("", "end", 
            values=(ten, cong_no_cu_fmt, cong_no_dtt_fmt, tong_cong_no_fmt, ngay_cap_nhat),
            iid=str(id_cn),
            tags=("bold_ten",)
        )
        

    # Phương thức tải dữ liệu công nợ
    def load_debt_data(self, debts=None):
        """Tải và hiển thị danh sách công nợ."""
        # Xóa dữ liệu cũ trong bảng
        for i in self.tree_cn.get_children():
            self.tree_cn.delete(i)

        if debts is None:
            # Nếu không có dữ liệu được truyền vào, yêu cầu controller load lại
            self.debt_controller.load_debts()
            return

        # Lưu lại dữ liệu để dùng cho tìm kiếm
        self.cong_no_data = debts

        # Hiển thị từng dòng công nợ
        for item in debts:
            self.insert_cong_no_item(item)

    # Phương thức hiển thị thông tin chi tiết khi một dòng được chọn
    def on_cong_no_select(self, event):
        """Hiển thị thông tin chi tiết khi một dòng được chọn."""
        selected_items = self.tree_cn.selection()
        if not selected_items:
            return
            
        selected_id = selected_items[0]  # Lấy id được lưu trong iid của tree item
        
        # Tìm dữ liệu trong danh sách đã lưu
        item_data = next(
            (item for item in self.cong_no_data if str(item[0]) == selected_id), 
            None
        )
        
        if item_data:
            # Unpack dữ liệu: id_cn, ten, cong_no_cu, cong_no_dtt, tong_cong_no, ngay_cap_nhat
            _, ten, cong_no_cu, cong_no_dtt, tong_cong_no, ngay_cap_nhat = item_data
            # Format số tiền với dấu chấm phân cách hàng nghìn
            cong_no_cu_fmt = f"{cong_no_cu:,}".replace(",", ".") if cong_no_cu else "0"
            cong_no_dtt_fmt = f"{cong_no_dtt:,}".replace(",", ".") if cong_no_dtt else "0"
            tong_cong_no_fmt = f"{tong_cong_no:,}".replace(",", ".") if tong_cong_no else "0"
            
            # Cập nhật các ô thông tin bên phải
            self.update_fields_vars["Tên khách hàng:"].set(ten)
            self.update_fields_vars["Công nợ hiện tại:"].set(tong_cong_no_fmt)
            self.update_fields_vars["Đã thanh toán:"].set(cong_no_dtt_fmt)
            # self.update_fields_vars["Ngày thanh toán:"].set(ngay_cap_nhat) # Biến này không còn được dùng cho widget nào
            try:
                # Cập nhật DateEntry widget với ngày từ database
                date_part = ngay_cap_nhat.split(' ')[0]
                date_obj = datetime.strptime(date_part, '%d/%m/%Y').date()
                self.date_entry.set_date(date_obj)
            except (ValueError, IndexError):
                # Nếu ngày không hợp lệ, đặt là ngày hôm nay
                self.date_entry.set_date(datetime.now().date())

    # Phương thức lưu lại thông tin công nợ đã cập nhật
    def update_cong_no(self):
        """Lưu lại thông tin công nợ đã cập nhật."""
        selected_items = self.tree_cn.selection()
        if not selected_items:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một khách hàng để cập nhật.")
            return
        
        # Lấy id_cn từ id của dòng được chọn
        debt_id = int(selected_items[0])
        
        try:
            # Lấy số tiền thanh toán mới từ ô Entry, loại bỏ dấu chấm
            payment_str = self.update_fields_vars["Đã thanh toán:"].get().replace(".", "")
            new_payment_amount = int(payment_str) if payment_str else 0
        except ValueError:
            messagebox.showerror("Lỗi", "Số tiền thanh toán không hợp lệ. Vui lòng chỉ nhập số.")
            return

        # Lấy ngày thanh toán mới từ DateEntry
        new_payment_date = self.date_entry.get_date() 
        
        # Tìm ngày cập nhật cũ từ dữ liệu đã lưu
        item_data = next((item for item in self.cong_no_data if str(item[0]) == str(debt_id)), None)
        
        date_to_pass = new_payment_date # Mặc định là ngày người dùng chọn
        if item_data:
            old_date_str = item_data[5] # ngay_cap_nhat
            try:
                old_date_obj = datetime.strptime(old_date_str.split(' ')[0], '%d/%m/%Y').date()
                # Kiểm tra nếu ngày mới nhỏ hơn ngày đã lưu
                if new_payment_date < old_date_obj:
                    messagebox.showerror("Ngày không hợp lệ", "Ngày thanh toán mới không được nhỏ hơn ngày cập nhật gần nhất. Đã tự động chọn ngày hiện tại.")
                    today = datetime.now().date()
                    self.date_entry.set_date(today)
                    date_to_pass = today 
            except (ValueError, IndexError):
                # Nếu ngày cũ không hợp lệ, không cần làm gì, cứ dùng ngày mới đã chọn
                pass

        # Gọi controller để xử lý việc cập nhật
        self.debt_controller.update_debt(debt_id, new_payment_amount, payment_date=date_to_pass)

    # Phương thức chuyển sang khách hàng tiếp theo
    def next_customer(self):
        """Chuyển sang khách hàng tiếp theo trong danh sách."""
        all_items = self.tree_cn.get_children()
        if not all_items:
            return

        selected_items = self.tree_cn.selection()
        if not selected_items:
            self.tree_cn.selection_set(all_items[0])
            self.tree_cn.focus(all_items[0])
            self.tree_cn.see(all_items[0])
            self.on_cong_no_select(None)
            return

        try:
            current_index = list(all_items).index(selected_items[0])
        except ValueError:
            return

        next_index = current_index + 1
        if next_index < len(all_items):
            next_item = all_items[next_index]
            self.tree_cn.selection_remove(*all_items)  # Xóa selection cũ
            self.tree_cn.selection_set(next_item)
            self.tree_cn.focus(next_item)
            self.tree_cn.see(next_item)
            self.on_cong_no_select(None)
        else:
            print("Đã ở dòng cuối cùng, không thể chuyển tiếp.")

    # Phương thức định dạng ô nhập số tiền thanh toán
    def format_thanh_toan_entry(self, event=None):
        value = self.thanh_toan_entry.get().replace(".", "")
        if value.isdigit():
            formatted_value = "{:,}".format(int(value)).replace(",", ".")
            self.thanh_toan_entry.delete(0, tk.END)
            self.thanh_toan_entry.insert(0, formatted_value)
        elif value == "":
            self.thanh_toan_entry.delete(0, tk.END)