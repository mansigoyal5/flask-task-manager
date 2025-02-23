from app import db  # Ensure 'app' is your main Flask file

with db.app.app_context():
    db.drop_all()  # Drop old tables (even if they don't exist)
    db.create_all()  # Create tables again
    print("Database recreated successfully!")