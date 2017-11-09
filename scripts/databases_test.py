import sqlite3
conn = sqlite3.connect("emails.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE email_addresses ( email TEXT );")
