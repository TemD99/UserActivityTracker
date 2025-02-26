import json
import sqlite3

# Load the JSON category mapping
json_mapping = {
    "chrome": "Web Browser",
    "firefox": "Web Browser",
    "msedge": "Web Browser",
    "safari": "Web Browser",
    "opera": "Web Browser",
    "iexplore": "Web Browser",
    "notepad": "Text Editor",
    "notepad++": "Text Editor",
    "sublime_text": "Text Editor",
    "vscode": "Development",
    "code": "Development",
    "visualstudio": "Development",
    "devenv": "Development",
    "powershell": "Shell",
    "cmd": "Shell",
    "conhost": "Shell",
    "excel": "Microsoft Office",
    "word": "Microsoft Office",
    "powerpnt": "Microsoft Office",
    "outlook": "Microsoft Office",
    "onenote": "Microsoft Office",
    "access": "Microsoft Office",
    "msaccess": "Microsoft Office",
    "onedrive": "Cloud Storage",
    "dropbox": "Cloud Storage",
    "googledrive": "Cloud Storage",
    "teams": "Communication",
    "skype": "Communication",
    "slack": "Communication",
    "discord": "Communication",
    "zoom": "Communication",
    "webex": "Communication",
    "thunderbird": "Email",
    "spotify": "Music",
    "itunes": "Music",
    "vlc": "Media Player",
    "wmplayer": "Media Player",
    "realplayer": "Media Player",
    "winamp": "Media Player",
    "steam": "Gaming",
    "epicgameslauncher": "Gaming",
    "uplay": "Gaming",
    "valorant": "Gaming",
    "leagueoflegends": "Gaming",
    "fortnite": "Gaming",
    "minecraft": "Gaming",
    "roblox": "Gaming",
    "pycharm": "Development",
    "eclipse": "Development",
    "intellij": "Development",
    "netbeans": "Development",
    "atom": "Development",
    "brackets": "Development",
    "acrobat": "PDF Reader",
    "foxit": "PDF Reader",
    "adobephotoshop": "Creative",
    "adobeillustrator": "Creative",
    "adobepremiere": "Creative",
    "lightroom": "Creative",
    "gimp": "Creative",
    "autocad": "Design",
    "sketchup": "Design",
    "solidworks": "Design",
    "matlab": "Science/Engineering",
    "rstudio": "Science/Engineering",
    "anaconda": "Science/Engineering",
    "explorer": "File Manager",
    "filezilla": "FTP Client",
    "winscp": "FTP Client",
    "putty": "Terminal/SSH",
    "vmware": "Virtualization",
    "virtualbox": "Virtualization",
    "docker": "Virtualization",
    "blender": "Creative/Design",
    "obs": "Streaming/Recording",
    "streamlabs": "Streaming/Recording",
    "powerbi": "Analytics",
    "tableau": "Analytics",
    "mspaint": "Graphics",
    "photos": "Graphics",
    "f.lux": "Utilities",
    "taskmgr": "Utilities",
    "calc": "Utilities",
    "snippingtool": "Utilities",
    "msconfig": "Utilities",
    "control": "Utilities",
    "regedit": "Utilities",
    "oculus": "VR/AR",
    "vive": "VR/AR",
    "vrchat": "VR/AR",
    "steamvr": "VR/AR",
    "unity": "Game Development",
    "unreal": "Game Development",
    "godot": "Game Development",
    "tensorflow": "AI/ML",
    "pytorch": "AI/ML",
    "keras": "AI/ML",
    "jupyter": "AI/ML/Research",
    "chatgpt": "AI/ML",
    "openai": "AI/ML",
    "colab": "AI/ML/Research",
    "pornhub": "Adult Content",
    "xvideos": "Adult Content",
    "redtube": "Adult Content",
    "xhamster": "Adult Content",
    "tinder": "Dating",
    "bumble": "Dating",
    "hinge": "Dating",
    "sqlite": "Database",
    "marvel": "Gaming",
    "dyingLight": "Gaming",
    "racing": "Gaming",
    "exoborne": "Gaming",
    "assettocorsa": "Gaming",
    "acs": "Gaming",
    "db browser for sqlite": "Database"
}

# Convert JSON keys to lowercase for case-insensitive matching
json_mapping = {k.lower(): v for k, v in json_mapping.items()}

# Connect to the SQLite database
db_path = r"C:\Users\Analy\datamules\UserActivityTracker\data\user_activity.db"  # Change this to your actual SQLite path
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Fetch all rows
cursor.execute("SELECT id, ApplicationProcess FROM user_activity")
rows = cursor.fetchall()

# Update each row with its category
for row in rows:
    row_id, app_process = row
    if app_process:
        app_process_lower = app_process.lower()  # Convert to lowercase
        category = "Uncategorized"  # Default category
        
        # **Partial Matching: Check if any key is in the application process name**
        for key in json_mapping.keys():
            if key in app_process_lower:  # If a key is found anywhere in the process name
                category = json_mapping[key]
                break  # Stop at first match

        print(f"Updating ID: {row_id}, Process: {app_process} -> Category: {category}")  # Debugging output

        # Update the database
        cursor.execute("UPDATE user_activity SET ActivityCategory = ? WHERE id = ?", (category, row_id))

# Commit changes and close connection
conn.commit()
conn.close()

print("Activity categories updated successfully!")

