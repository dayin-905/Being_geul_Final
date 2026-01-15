from database import SessionLocal
from models import Policy
from sqlalchemy import distinct

def get_distinct_regions():
    db = SessionLocal()
    try:
        regions = db.query(distinct(Policy.region)).all()
        # regions is a list of tuples like [('Seoul',), ('Busan',)]
        # We flatten it to a simple list
        region_list = [r[0] for r in regions if r[0] is not None]
        print("Distinct Regions found in 'being_test' table:")
        for region in sorted(region_list):
            print(f"- {region}")
    except Exception as e:
        print(f"Error querying regions: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    get_distinct_regions()
