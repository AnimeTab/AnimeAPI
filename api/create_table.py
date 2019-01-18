import json, sqlite3, os

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname,'db.json')

with open (filename, 'r', encoding = "utf8") as f:
    quotes = json.load(f)

connection = sqlite3.connect('data.db')
cursor = connection.cursor()

create_table = "CREATE TABLE IF NOT EXISTS anime (anime text, quote text, author text)"
cursor.execute(create_table)

query = "INSERT INTO anime VALUES (?, ?, ?)"
for quote in quotes["List"]:
    cursor.execute(query,(quote['anime'], quote['quote'], quote['author']))

temp_table = "CREATE TABLE IF NOT EXISTS temp (anime text, quote text, author text)"
cursor.execute(temp_table)

connection.commit()
connection.close()