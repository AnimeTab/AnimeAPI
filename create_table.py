import json, sqlite3, os

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname,'seed.json')

with open (filename, 'r', encoding = "utf8") as f:
    quotes = json.load(f)

connection = sqlite3.connect('data.db')
cursor = connection.cursor()

cursor.execute("DROP TABLE anime")
cursor.execute("DROP TABLE temp")
create_table = "CREATE TABLE IF NOT EXISTS anime (anime text, quote text, author text, color text, logo text, email text)"
cursor.execute(create_table)

query = "INSERT INTO anime VALUES (?, ?, ?, ?, ?, ?)"
for quote in quotes["List"]:
    cursor.execute(query,(quote['anime'], quote['quote'], quote['author'], quote['color'], quote['logo'], quote['email']))

temp_table = "CREATE TABLE IF NOT EXISTS temp (anime text, quote text, author text, color text, logo text, email text)"
cursor.execute(temp_table)

connection.commit()
connection.close()