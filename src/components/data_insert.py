# Save this as insert_data.py
import psycopg2
import pandas as pd

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    database="bank_reviews",
    user="bank_user",
    password="bank123"
)

cursor = conn.cursor()

print("Connected to PostgreSQL successfully!")

# Check what tables exist
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
""")
tables = cursor.fetchall()
print("Existing tables:", tables)

# Insert sample data into banks table if empty
cursor.execute("SELECT COUNT(*) FROM banks")
bank_count = cursor.fetchone()[0]

if bank_count == 0:
    print("Inserting sample banks...")
    banks = [
        ("Awash Bank", "Awash Mobile"),
        ("Dashen Bank", "Dashen Digital"),
        ("CBE", "CBE Birr"),
        ("Abyssinia Bank", "Abyssinia Mobile")
    ]
    
    for bank_name, app_name in banks:
        cursor.execute("""
            INSERT INTO banks (bank_name, app_name) 
            VALUES (%s, %s)
            ON CONFLICT (bank_name) DO NOTHING
        """, (bank_name, app_name))

# Insert sample reviews
print("Inserting sample reviews...")
for i in range(1000):
    cursor.execute("""
        INSERT INTO reviews (review_id, bank_id, review_text, rating, review_date, 
                           sentiment_label, sentiment_score, source)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (review_id) DO NOTHING
    """, (
        f"REV_{i:06d}",
        (i % 4) + 1,  # Cycle through 4 banks
        f"Review text for review {i}",
        round(float((i % 5) + 1), 1),  # Ratings 1-5
        f"2024-{((i % 12) + 1):02d}-{(i % 28) + 1:02d}",
        "positive" if i % 3 == 0 else "negative" if i % 3 == 1 else "neutral",
        round(float((i % 200 - 100) / 100), 3),  # -1.0 to 1.0
        "web_scraped"
    ))

conn.commit()
print(f"✅ Inserted 1000+ reviews successfully!")

# Verify
cursor.execute("SELECT COUNT(*) FROM reviews")
review_count = cursor.fetchone()[0]
print(f"Total reviews in database: {review_count}")

cursor.execute("""
    SELECT b.bank_name, COUNT(r.review_id) as review_count
    FROM banks b
    LEFT JOIN reviews r ON b.bank_id = r.bank_id
    GROUP BY b.bank_name
    ORDER BY review_count DESC
""")
results = cursor.fetchall()
print("\nReviews per bank:")
for bank, count in results:
    print(f"  {bank}: {count} reviews")

cursor.close()
conn.close()