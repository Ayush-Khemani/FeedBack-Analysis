import sqlite3

def create_databse():
    conn = sqlite3.connect("reviews.db")
    cur = conn.cursor()

    cur.execute("""
                    CREATE TABLE IF NOT EXISTS PRODUCTS (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        NAME TEXT NOT NULL,
                        IMAGE_URL TEXT NOT NULL                    
                    )
                """)
    
    cur.execute("""
                    CREATE TABLE IF NOT EXISTS REVIEWS(
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        PRODUCT_ID INTEGER,
                        REVIEW_TEXT TEXT NOT NULL,
                        SENTIMENT TEXT,
                        DATE TEXT,
                        FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCTS (ID)
                    )
                """)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_databse()