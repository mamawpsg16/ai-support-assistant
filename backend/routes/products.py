"""
products.py — HTTP endpoints for products. Same shape as customers.py.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Product
from backend.schemas import ProductCreate, ProductRead, ProductUpdate
from backend.services import crud

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    return crud.create(db, Product, payload)


@router.get("/", response_model=list[ProductRead])
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all(db, Product, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    obj = crud.get(db, Product, product_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return obj


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
):
    obj = crud.get(db, Product, product_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.update(db, obj, payload)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    obj = crud.get(db, Product, product_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Product not found")
    crud.delete(db, obj)
