from faker import Faker

from app import app
from config import db
from models import Note, User

fake = Faker()

with app.app_context():
    print("Clearing tables...")
    Note.query.delete()
    User.query.delete()

    print("Seeding users and notes...")
    for i in range(3):
        user = User(username=f"user{i + 1}")
        user.password_hash = "password123"
        db.session.add(user)
        db.session.flush()

        for _ in range(15):
            db.session.add(
                Note(
                    title=fake.sentence(nb_words=4),
                    content=fake.paragraph(),
                    user_id=user.id,
                )
            )

    db.session.commit()
    print("Done. Log in with user1 / password123")