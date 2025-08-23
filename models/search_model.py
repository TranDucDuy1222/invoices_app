from .base_model import BaseModel
import sqlite3

class SearchModel(BaseModel):
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def search_invoices(self, query):
        self.cursor.execute("SELECT * FROM invoices WHERE description LIKE ?", ('%' + query + '%',))
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()