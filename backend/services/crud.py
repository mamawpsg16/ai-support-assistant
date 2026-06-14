"""
crud.py — generic Create/Read/Update/Delete helpers.

These functions work on ANY model (Customer, Product, Order, Subscription) so each
router doesn't have to repeat the same database code. Each helper takes the SQLAlchemy
`Session` and the model class to operate on.

How a query works in SQLAlchemy:
  db.query(Model)              -> start a SELECT on that table
       .filter(Model.id == 5)  -> add a WHERE clause
       .first()                -> run it, return the first row (or None)
       .all()                  -> run it, return a list of rows
And to change data:
  db.add(obj)     -> stage an INSERT / track changes
  db.commit()     -> actually save to the database
  db.refresh(obj) -> reload the row so we get DB-filled values (id, created_at)
  db.delete(obj)  -> stage a DELETE
"""

from sqlalchemy.orm import Session


def get(db: Session, model, item_id: int):
    """Read ONE row by primary key. Returns the object, or None if not found."""
    return db.query(model).filter(model.id == item_id).first()


def get_all(db: Session, model, skip: int = 0, limit: int = 100):
    """
    Read MANY rows (a page of them).
      skip  -> how many rows to skip (offset) — for pagination
      limit -> max rows to return
    Returns a list (possibly empty).
    """
    return db.query(model).offset(skip).limit(limit).all()


def create(db: Session, model, data):
    """
    Create a new row.
      data is a Pydantic schema (e.g. CustomerCreate).

    model_dump(exclude_unset=True) turns the schema into a plain dict, dropping any
    field the client DIDN'T send. Dropping unsent fields is what lets the model's
    column defaults (like Order.status -> pending) take effect.

    `model(**fields)` unpacks the dict into keyword arguments:
        model(name="Ana", email="a@x.com")  == Customer(name="Ana", email="a@x.com")
    """
    fields = data.model_dump(exclude_unset=True)
    obj = model(**fields)
    db.add(obj)        # stage the INSERT
    db.commit()        # save it
    db.refresh(obj)    # reload so obj.id / obj.created_at are populated
    return obj


def update(db: Session, db_obj, data):
    """
    Update an existing row.
      db_obj -> the row already fetched from the DB.
      data   -> a Pydantic *Update* schema.

    exclude_unset=True again: only overwrite fields the client actually sent, leaving
    the rest untouched (a partial update / PATCH).
    setattr(obj, "name", value) sets obj.name = value using a field name string.
    """
    fields = data.model_dump(exclude_unset=True)
    for key, value in fields.items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, db_obj):
    """Delete a row that was already fetched."""
    db.delete(db_obj)
    db.commit()
