import sqlite3

class BaseModel:
    def __init__(self, db_path):
        """Kết nối đến cơ sở dữ liệu được chỉ định."""
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        """Đóng kết nối cơ sở dữ liệu."""
        if self.conn:
            self.conn.close()