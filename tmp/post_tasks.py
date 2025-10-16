import requests
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2MDYyMjc5Mn0.QBLQNymOzel8YWR7y5xIub9PYAnIFEt9jPUAb85tI3k'
FILES = ['youtube_task.json','manual_task.json','daily_task.json']
for fn in FILES:
    with open('/workspaces/codespaces-blank/tmp/'+fn,'r') as f:
        data = f.read()
    r = requests.post('http://localhost/api/tasks', headers={'Authorization': f'Bearer {TOKEN}','Content-Type':'application/json'}, data=data)
    print(fn, r.status_code)
    try:
        print(r.json())
    except Exception as e:
        print(r.text)
