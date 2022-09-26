from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.sql import text

engine = create_engine(
    "postgresql+psycopg2://docker:secret@progyny-assessment-db-1:5432/postgres"
)

# Initializing postgres, feeds two tables 'crypto' and 'transaction_history'
def initialize_db():
    metadata_obj = sa.MetaData()

    # Create crypto table
    crypto = sa.Table(
        "crypto",
        metadata_obj,
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("symbol", sa.String),
        sa.Column("name", sa.String),
        sa.Column("current_price", sa.Float),
    )

    # Create transaction history table
    transaction_history = sa.Table(
        "transaction_history",
        metadata_obj,
        sa.Column("id", sa.String),
        sa.Column("purchase_timestamp", sa.String),
        sa.Column("purchase_price", sa.Float),
    )

    # Create tables
    metadata_obj.create_all(engine)

    return engine


# Upserting to crypto table
def upsert_crypto(coin):
    sql = text(
        """
        INSERT INTO crypto (id, symbol, name, current_price) VALUES(:id, :symbol, :name, :current_price) ON CONFLICT(id) DO UPDATE SET symbol=:symbol, name=:name, current_price=:current_price
    """
    )
    with engine.connect() as conn:
        conn.execute(
            sql,
            {
                "id": coin.get("id"),
                "symbol": coin.get("symbol"),
                "name": coin.get("name"),
                "current_price": coin.get("current_price"),
            },
        )


# Inserting new transaction history
def insert_transaction_history(coin_id, price):
    sql = text(
        """
        INSERT INTO transaction_history (id, purchase_timestamp, purchase_price) VALUES(:id, :purchase_timestamp, :purchase_price)
        """
    )
    with engine.connect() as conn:
        conn.execute(
            sql,
            {
                "id": coin_id,
                "purchase_timestamp": datetime.timestamp(datetime.now()),
                "purchase_price": price,
            },
        )


# Get all transaction history
def get_transaction_history():
    sql = text(
        """
        SELECT * FROM transaction_history
        ORDER BY id, purchase_timestamp
        """
    )
    with engine.connect() as conn:
        res = conn.execute(sql)
        return res.all()
