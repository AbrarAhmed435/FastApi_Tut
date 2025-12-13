from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

engine = create_engine("sqlite:///database.db", echo=True)

Base = declarative_base()


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    difficulty = Column(String, nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=False)
    title = Column(String, nullable=False)
    options = Column(String, nullable=False)  # store JSON string
    correct_answer_id = Column(Integer, nullable=False)
    explanation = Column(String, nullable=True)


class ChallengeQuota(Base):
    __tablename__ = "challenge_quotas"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, unique=True)
    quota_remaining = Column(Integer, nullable=False, default=50)
    last_reset_date = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(engine)
""" 
SQLAlchemy looks at all the models (classes) that inherit from Base

It creates the corresponding database tables if they do not exist.
"""

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

""" 
| Parameter        | Meaning                                                                |
| ---------------- | ---------------------------------------------------------------------- |
| autocommit=False | You must manually call `commit()`                                      |
| autoflush=False  | SQLAlchemy won't auto-send changes until needed                        |
| bind=engine      | Connects this session factory to your SQLite/MySQL/PostgreSQL database |

"""


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


""" 
Why do we use yield instead of return?

Because FastAPI uses dependency injection.

yield allows:

Code before yield → runs before the request

Code after yield → runs after the request (cleanup)
"""