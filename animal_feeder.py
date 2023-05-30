from app import app

with app.app_context():
    """
    Executes the add_jobs() function at startup of the application.
    """
    from app.util import add_jobs
    add_jobs()
