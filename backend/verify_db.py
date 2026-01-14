from sqlmodel import Session, select
from database import engine
from models import Vendor

def check_vendors():
    with Session(engine) as session:
        vendors = session.exec(select(Vendor)).all()
        print(f"Found {len(vendors)} vendors in the database:")
        for v in vendors:
            print(f"ID: {v.id} | Name: {v.name} | Email: {v.email} | Contact: {v.contact_person}")

if __name__ == "__main__":
    check_vendors()
