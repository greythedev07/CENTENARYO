import webview
import sqlite3

conn = sqlite3.connect('centenaryo.db')
print("Database connected successfully!")

html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {
            margin: 0;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: Arial, sans-serif;
            font-size: 80px;
            font-weight: bold;
            background-color: #2c3e50;
            color: white;
        }
    </style>
</head>
<body>
    CENTENARYO
</body>
</html>
"""

if __name__ == '__main__':
    webview.create_window(
        title="CENTENARYO",
        html=html_content,
        width=800,
        height=600,
        resizable=True,
        min_size=(800, 600)
    )
    webview.start()