import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=DESKTOP-KOBL8E0,1433;"
    "DATABASE=lucenda_database;"
    "Trusted_Connection=yes;"
    "Encrypt=no;"
    "TrustServerCertificate=yes;"
)
try:
    conn = pyodbc.connect(conn_str)
    print("✅ Kết nối thành công!")
except Exception as e:
    print("❌ Lỗi:", e)
