import oracledb

# Inicializa Oracle Client (usa la ruta exacta)
oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_26")

conn = oracledb.connect(
    user="django_user",
    password="django123",
    dsn="localhost:1521/XEPDB1"
)

print("Conexión exitosa con Oracle")
conn.close()
