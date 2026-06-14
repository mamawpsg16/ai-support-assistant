"""
database.py — the single place that sets up our database connection.

Everything else in the app imports from here:
  - `Base`   : the parent class every model (table) inherits from.
  - `engine` : the actual connection to the SQLite file.
  - `get_db` : a helper that hands a database session to each request.

Concept map (read this once and the rest of the project makes sense):

  ENGINE   = the phone line to the database.
  SESSION  = one phone call. You make a call, do your talking (queries), hang up.
  BASE     = the blueprint registry. Every model class registers itself on Base,
             so `Base.metadata.create_all()` knows what tables to create.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# --- 1. Where the database lives -------------------------------------------------
# "sqlite:///./support.db" means: use SQLite, in a file called support.db,
# in the current folder (the ./ part). SQLite is just a file on disk — no server.
#
# We read it from the DATABASE_URL env var so it can be overridden (e.g. Docker points
# it at a mounted volume), falling back to the local file for the normal venv workflow.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./support.db")

# --- 2. The engine ---------------------------------------------------------------
# create_engine opens the "phone line" to that database file.
#
# check_same_thread=False is a SQLite-specific quirk: by default SQLite refuses to be
# used from more than one thread. FastAPI may handle requests on different threads,
# so we turn that guard off. (This is safe for our usage and standard for FastAPI+SQLite.)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# --- 3. The session factory ------------------------------------------------------
# sessionmaker is a factory: calling SessionLocal() gives us a fresh session (one
# "phone call") to talk to the DB. We configure it once here and reuse everywhere.
#   autocommit=False -> changes aren't saved until we call .commit() ourselves.
#   autoflush=False  -> don't auto-sync pending changes until we ask.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 4. The declarative base -----------------------------------------------------
# Base is the parent class for all our models. When a model class subclasses Base,
# SQLAlchemy records its table definition on Base.metadata. Later, one call to
# Base.metadata.create_all(engine) creates every registered table at once.
Base = declarative_base()


# --- 5. The per-request session dependency --------------------------------------
def get_db():
    """
    Hands a database session to a request, then guarantees it gets closed.

    FastAPI's "dependency injection": a route can ask for `db = Depends(get_db)` and
    FastAPI will run THIS function to produce that `db`. Because we use `yield`, the
    code AFTER yield (db.close()) runs once the request is finished — even if it errors.
    That gives every request its own session and prevents leaked connections.
    """
    db = SessionLocal()      # open one "phone call"
    try:
        yield db             # give it to the route to use
    finally:
        db.close()           # always hang up when the request is done
