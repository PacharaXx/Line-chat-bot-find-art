import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('test1.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# SQL command to clear data from a table
sql_command = "DELETE FROM ArtworkColors"

try:
    # Execute the SQL command
    cursor.execute(sql_command)

    # Commit the changes to the database
    conn.commit()
    print("Data cleared from the table successfully.")
except sqlite3.Error as e:
    # Handle exceptions
    print("Error:", e)
    conn.rollback()  # Roll back changes if an error occurs

# Close the connection
conn.close()
