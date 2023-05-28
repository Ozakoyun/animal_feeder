from app import app

with app.app_context():
    from app.util import add_jobs
    add_jobs()
