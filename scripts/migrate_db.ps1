$env:FLASK_APP = "app.main:app"
flask db migrate -m "Initial migration"
flask db upgrade
