import sqlite3

# Define SQLite database path
db_path = r"C:\Users\Analy\datamules\UserActivityTracker\data\user_activity.db"

# Connect to SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Fetch all rows where either WindowTitle or ApplicationProcess is blank or 'Unknown'
cursor.execute("""
    SELECT id, WindowTitle, ApplicationProcess 
    FROM user_activity 
    WHERE WindowTitle = '' OR WindowTitle = 'Unknown' 
       OR ApplicationProcess = '' OR ApplicationProcess = 'Unknown'
""")
rows = cursor.fetchall()

# Process each row
for row in rows:
    row_id, window_title, app_process = row

    # Check if both fields are blank or 'Unknown'
    if (window_title.strip() == "" or window_title.strip().lower() == "unknown") and \
       (app_process.strip() == "" or app_process.strip().lower() == "unknown"):
        new_window_title = "Unknown"
        new_app_process = "Unknown"

    else:
        new_window_title = window_title
        new_app_process = app_process

        # Fill missing values
        if window_title.strip() == "" or window_title.strip().lower() == "unknown":
            new_window_title = app_process  # Fill WindowTitle with ApplicationProcess

        if app_process.strip() == "" or app_process.strip().lower() == "unknown":
            new_app_process = window_title  # Fill ApplicationProcess with WindowTitle

    # Ensure we update only if changes were made
    if new_window_title != window_title or new_app_process != app_process:
        cursor.execute("""
            UPDATE user_activity 
            SET WindowTitle = ?, ApplicationProcess = ? 
            WHERE id = ?
        """, (new_window_title, new_app_process, row_id))

        print(f"Updated ID {row_id}: WindowTitle='{new_window_title}', ApplicationProcess='{new_app_process}'")

# Commit changes and close connection
conn.commit()
conn.close()

print("Blank or 'Unknown' fields have been updated successfully!")
