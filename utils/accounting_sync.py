import pandas as pd
from models.enterprise_data import Sales, db

def import_sales_from_excel(filepath, brand_id):
    df = pd.read_excel(filepath)
    for _, row in df.iterrows():
        sale = Sales(
            brand_id=brand_id,
            store_id=row['store_id'],
            date=row['date'],
            amount=row['amount']
        )
        db.session.add(sale)
    db.session.commit() 