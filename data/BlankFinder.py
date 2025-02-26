import sqlite3

# Define SQLite database path
db_path = r"C:\Users\Analy\datamules\UserActivityTracker\data\user_activity.db"

# Connect to SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Fetch column names from the table
cursor.execute("PRAGMA table_info(user_activity);")
columns = [col[1] for col in cursor.fetchall()]

# Initialize a dictionary to store blank counts
blank_counts = {col: 0 for col in columns}
total_rows = 0

# Fetch all rows from the table
cursor.execute("SELECT * FROM user_activity;")
rows = cursor.fetchall()
total_rows = len(rows)

# Iterate through rows and count blanks
for row in rows:
    for i, value in enumerate(row):
        if value is None or str(value).strip() == "":
            blank_counts[columns[i]] += 1

# Display the results
print(f"Total Rows: {total_rows}")
print("\nBlank Value Counts Per Column:")
for col, count in blank_counts.items():
    percentage = (count / total_rows) * 100 if total_rows > 0 else 0
    print(f"{col}: {count} blanks ({percentage:.2f}%)")

# Identify columns with the highest number of missing values
most_missing = max(blank_counts, key=blank_counts.get)
print(f"\nColumn with the most missing values: {most_missing} ({blank_counts[most_missing]} blanks)")

# Close connection
conn.close()
