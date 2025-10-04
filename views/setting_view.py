import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import customtkinter as ctk
from datetime import datetime, timedelta

class CaiDatView(tk.Frame):
    def __init__(self, parent, root_window):
        super().__init__(parent, bg="white")
        
        self.root_window = root_window
        self.controller = None
        self.table_vars = {}

        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="white", padx=30, pady=20)
        main_frame.pack(expand=True, fill="both")

        tk.Label(main_frame, text="Quản lý và Xóa Dữ Liệu", font=("Segoe UI", 18, "bold"), bg="white").pack(anchor="w", pady=(0, 20))

        # --- Frame Xóa theo ngày ---
        date_frame = tk.LabelFrame(main_frame, text="Xóa dữ liệu theo khoảng thời gian", font=("Segoe UI", 12), bg="white", padx=15, pady=15)
        date_frame.pack(fill="x", pady=10)

        tk.Label(date_frame, text="Từ ngày:", bg="white", font=("Segoe UI", 10)).grid(row=0, column=0, padx=(0, 5), pady=5)
        self.start_date_entry = DateEntry(date_frame, width=15, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy', font=("Segoe UI", 10))
        self.start_date_entry.set_date(datetime.now() - timedelta(days=30))
        self.start_date_entry.grid(row=0, column=1, pady=5)

        tk.Label(date_frame, text="Đến ngày:", bg="white", font=("Segoe UI", 10)).grid(row=0, column=2, padx=(20, 5), pady=5)
        self.end_date_entry = DateEntry(date_frame, width=15, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy', font=("Segoe UI", 10))
        self.end_date_entry.grid(row=0, column=3, pady=5)

        # --- Frame chọn bảng ---
        tables_frame = tk.LabelFrame(main_frame, text="Chọn loại dữ liệu để xóa", font=("Segoe UI", 12), bg="white", padx=15, pady=15)
        tables_frame.pack(fill="x", pady=10)

        # Các bảng có thể xóa
        # Key: Tên hiển thị, Value: Tên bảng trong DB
        self.tables_map = {
            "Hóa đơn và Chi tiết HĐ": "invoices",
            "Công nợ": "debts",
            "Toàn bộ Khách hàng": "customers",
            "Toàn bộ Mặt hàng": "products",
            "Toàn bộ Bãi và Xe": "yards" # Chọn 1 đại diện
        }
        
        # Bảng phụ thuộc
        self.dependent_tables = {
            "invoices": ["invoice_details"],
            "customers": ["addresses"],
            "yards": ["cars"]
        }

        for i, (display_name, table_name) in enumerate(self.tables_map.items()):
            var = tk.BooleanVar()
            cb = ctk.CTkCheckBox(
                tables_frame,
                text=display_name,
                variable=var,
                font=("Segoe UI", 11),
                text_color="black"  # 🔹 Màu chữ đen
            )
            cb.grid(row=i, column=0, sticky="w", pady=4)
            self.table_vars[table_name] = var

        # --- Frame chứa các nút hành động ---
        action_frame = tk.Frame(main_frame, bg="white")
        action_frame.pack(fill="x", pady=20, side="bottom")

        delete_by_date_btn = ctk.CTkButton(action_frame, text="Xóa theo ngày đã chọn", command=self.delete_by_date, font=("Segoe UI", 11, "bold"), fg_color="#f39c12")
        delete_by_date_btn.pack(side="left", expand=True, padx=5, ipady=5)

        delete_all_btn = ctk.CTkButton(action_frame, text="XÓA TẤT CẢ DỮ LIỆU ĐÃ CHỌN", command=self.delete_all, font=("Segoe UI", 11, "bold"), fg_color="#e74c3c")
        delete_all_btn.pack(side="left", expand=True, padx=5, ipady=5)

    def get_selected_tables(self):
        """Lấy danh sách các bảng đã được chọn, bao gồm cả các bảng phụ thuộc."""
        selected = []
        for table_name, var in self.table_vars.items():
            if var.get():
                selected.append(table_name)
                # Thêm các bảng phụ thuộc nếu có
                if table_name in self.dependent_tables:
                    selected.extend(self.dependent_tables[table_name])
        return selected

    def delete_by_date(self):
        """Hàm xử lý khi nhấn nút 'Xóa theo ngày'."""
        selected_tables = self.get_selected_tables()
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()

        if not selected_tables:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn loại dữ liệu cần xóa.")
            return

        confirm_msg = f"Bạn có chắc muốn xóa dữ liệu của các mục đã chọn từ ngày {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')} không?\n\nHành động này KHÔNG THỂ hoàn tác."
        if messagebox.askyesno("Xác nhận xóa", confirm_msg):
            if self.controller:
                self.controller.delete_data_by_date(selected_tables, start_date, end_date)

    def delete_all(self):
        """Hàm xử lý khi nhấn nút 'Xóa tất cả'."""
        selected_tables = self.get_selected_tables()

        if not selected_tables:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn loại dữ liệu cần xóa.")
            return

        confirm_msg = f"CẢNH BÁO CỰC KỲ NGUY HIỂM!\n\nBạn có chắc chắn muốn xóa TOÀN BỘ dữ liệu khỏi các mục đã chọn không?\n\nHành động này sẽ xóa vĩnh viễn và KHÔNG THỂ hoàn tác."
        if messagebox.askyesno("XÁC NHẬN LẦN CUỐI", confirm_msg, icon='error'):
            if self.controller:
                self.controller.delete_all_data(selected_tables)
