import psycopg2
from config import *

print("=" * 50)
print("SQL QUERY PERFORMANCE ANALYZER")
print("=" * 50)

try:
    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

    print("\n✅ Connected Successfully!")

    cursor = connection.cursor()

    print("\nDepartments\n")

    cursor.execute("SELECT * FROM department;")

    rows = cursor.fetchall()

    print("-" * 40)

    for row in rows:
        print(f"ID: {row[0]}")
        print(f"Department: {row[1]}")
        print(f"Location: {row[2]}")
        print("-" * 40)

    cursor.close()
    connection.close()

    print("\n✅ Database Closed Successfully.")

except Exception as e:
    print("\n❌ ERROR")
    print(e)