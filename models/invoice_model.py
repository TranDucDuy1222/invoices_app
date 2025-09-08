from .base_model import BaseModel
import sqlite3

class InvoiceModel(BaseModel):
    def __init__(self, db_path):
        # Gọi __init__ của lớp cha (BaseModel) để có self.conn và self.cursor
        super().__init__(db_path)

    def get_all_invoices(self):
        """Lấy tất cả hóa đơn từ cơ sở dữ liệu."""
        self.cursor.execute("SELECT * FROM invoices")
        return self.cursor.fetchall()
