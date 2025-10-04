from .base_model import BaseModel
import sqlite3
from datetime import datetime

class SettingModel(BaseModel):
    def __init__(self, db_path):
        # Gọi __init__ của lớp cha (BaseModel) để có self.conn và self.cursor
        super().__init__(db_path)

    def delete_data_in_date_range(self, tables, start_date, end_date):
        """
        Xóa dữ liệu trong một khoảng ngày nhất định từ các bảng được chỉ định.
        Lưu ý: Hàm này giả định ngày trong DB được lưu dưới dạng TEXT 'DD/MM/YYYY HH:MM'.
        """
        deleted_counts = {}
        try:
            # Chuyển đổi ngày tháng sang định dạng YYYY-MM-DD để so sánh chuỗi trong SQLite
            start_date_sql = start_date.strftime('%Y-%m-%d')
            end_date_sql = end_date.strftime('%Y-%m-%d')

            # Ánh xạ tên bảng với cột ngày tương ứng
            table_date_columns = {
                'invoices': 'ngay_tao_hd',
                'debts': 'ngay_cap_nhat'
            }

            for table_name in tables:
                if table_name in table_date_columns:
                    date_column = table_date_columns[table_name]
                    
                    # Câu lệnh phức tạp này chuyển đổi 'DD/MM/YYYY ...' thành 'YYYY-MM-DD' để so sánh
                    date_conversion_sql = f"SUBSTR({date_column}, 7, 4) || '-' || SUBSTR({date_column}, 4, 2) || '-' || SUBSTR({date_column}, 1, 2)"
                    
                    # Nếu là bảng invoices, cần xóa các chi tiết liên quan trước
                    if table_name == 'invoices':
                        # Lấy ID các hóa đơn cần xóa
                        self.cursor.execute(f"""
                            SELECT id_hd FROM invoices 
                            WHERE {date_conversion_sql} BETWEEN ? AND ?
                        """, (start_date_sql, end_date_sql))
                        invoice_ids_to_delete = [row[0] for row in self.cursor.fetchall()]

                        if invoice_ids_to_delete:
                            # Xóa trong invoice_details
                            placeholders = ','.join('?' for _ in invoice_ids_to_delete)
                            self.cursor.execute(f"DELETE FROM invoice_details WHERE id_hd IN ({placeholders})", invoice_ids_to_delete)
                            # Xóa trong invoices
                            self.cursor.execute(f"DELETE FROM invoices WHERE id_hd IN ({placeholders})", invoice_ids_to_delete)
                            deleted_counts[table_name] = self.cursor.rowcount
                        else:
                            deleted_counts[table_name] = 0
                    else:
                        # Xóa cho các bảng khác (ví dụ: debts)
                        self.cursor.execute(f"""
                            DELETE FROM {table_name} 
                            WHERE {date_conversion_sql} BETWEEN ? AND ?
                        """, (start_date_sql, end_date_sql))
                        deleted_counts[table_name] = self.cursor.rowcount

            self.conn.commit()
            return True, deleted_counts
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, str(e)

    def delete_all_data_from_tables(self, tables):
        """Xóa tất cả dữ liệu từ các bảng được chỉ định."""
        try:
            for table_name in tables:
                self.cursor.execute(f"DELETE FROM {table_name}")
            self.conn.commit()
            return True, f"Đã xóa thành công dữ liệu khỏi các bảng: {', '.join(tables)}"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, str(e)