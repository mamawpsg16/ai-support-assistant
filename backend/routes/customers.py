"""
customers.py — the HTTP endpoints for customers.

A "router" is a group of related URLs. (Like a Laravel controller + its routes.)
main.py will include this router so these paths become live.

How one request flows:
  - @router.post("/") REGISTERS the function below as the handler for POST /customers/.
  - FastAPI validates the JSON body against the schema -> `payload`.
  - Depends(get_db) makes FastAPI run get_db() and inject the session -> `db`.
  - The function calls a crud helper and returns a model object.
  - response_model reshapes that object into JSON; status_code sets the HTTP code.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Customer
from backend.schemas import CustomerCreate, CustomerRead, CustomerUpdate
from backend.services import crud

# prefix -> every path here starts with /customers.
# tags   -> groups these endpoints together in the /docs page.
router = APIRouter(prefix="/customers", tags=["customers"])


# POST /customers/  -> create a customer
@router.post("/", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    # payload: validated JSON body. db: injected session.
    return crud.create(db, Customer, payload)


# GET /customers/  -> list customers (optional pagination ?skip=&limit=)
@router.get("/", response_model=list[CustomerRead])
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all(db, Customer, skip=skip, limit=limit)


# GET /customers/{customer_id}  -> read one customer
@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    obj = crud.get(db, Customer, customer_id)
    if obj is None:
        # No such row -> 404 with a clear message instead of crashing.
        raise HTTPException(status_code=404, detail="Customer not found")
    return obj


# PATCH /customers/{customer_id}  -> update some fields
@router.patch("/{customer_id}", response_model=CustomerRead)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
):
    obj = crud.get(db, Customer, customer_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud.update(db, obj, payload)


# DELETE /customers/{customer_id}  -> delete a customer
# 204 No Content = success, nothing to return.
@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    obj = crud.get(db, Customer, customer_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    crud.delete(db, obj)
