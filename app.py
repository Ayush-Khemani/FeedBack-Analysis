from flask import Flask, render_template, redirect, request, url_for
import sqlite3
import matplotlib.pyplot as plt
import base64
import io
from textblob import TextBlob
plt.switch_backend('Agg')
app = Flask(__name__)

sentiments = []
def get_db_connection():
    conn = sqlite3.connect("reviews.db")
    conn.row_factory = sqlite3.Row

    return conn

@app.route('/')
def index():
    return redirect(url_for('products'))

@app.route('/upload/<int:product_id>', methods=["GET", "POST"])
def upload(product_id):
    if request.method == "POST":
        file = request.files['file']
        if file:
            conn = get_db_connection()
            reviews = file.read().decode('utf-8').splitlines()
            print(reviews)

            for review in reviews:
                if not review.strip():
                    continue
                else:
                    blob = TextBlob(review)
                    polarity = blob.sentiment.polarity

                    if polarity > 0:
                        sentiment = "Positive"
                    elif polarity == 0:
                        sentiment = "Neutral"
                    else:
                        sentiment = "Negative"

                sentiments.append(sentiment)

                # Insert each review into the database
                conn.execute("""
                    INSERT INTO REVIEWS (PRODUCT_ID, REVIEW_TEXT, SENTIMENT, DATE)
                    VALUES (?, ?, ?, DATE("now"))
                """, (product_id, review , sentiment))

            # Commit all inserts and close the connection
            conn.commit()
            conn.close()
        return redirect(url_for('products'))

    return render_template('upload.html', product_id=product_id)


@app.route('/compare/<int:product_id>')
def compare(product_id):
    conn = get_db_connection()

    # Retrieve monthly counts of positive, negative, and neutral reviews
    monthly_counts = conn.execute('''
        SELECT strftime('%Y-%m', DATE) AS Month, 
               SUM(CASE WHEN SENTIMENT = 'Positive' THEN 1 ELSE 0 END) AS PositiveCount,
               SUM(CASE WHEN SENTIMENT = 'Negative' THEN 1 ELSE 0 END) AS NegativeCount,
               SUM(CASE WHEN SENTIMENT = 'Neutral' THEN 1 ELSE 0 END) AS NeutralCount
        FROM REVIEWS
        WHERE PRODUCT_ID = ?
        GROUP BY Month
        ORDER BY Month
    ''', (product_id,)).fetchall()

    conn.close()

    # Prepare data for plotting
    months = [row['Month'] for row in monthly_counts]
    positive_counts = [row['PositiveCount'] for row in monthly_counts]
    negative_counts = [row['NegativeCount'] for row in monthly_counts]
    neutral_counts = [row['NeutralCount'] for row in monthly_counts]

    # 1. Grouped Bar Chart
    plt.figure(figsize=(10, 5))
    width = 0.25  # width of each bar

    # Position of each group of bars on the x-axis
    x = range(len(months))

    # Plot each category at a different position within each month
    plt.bar([p - width for p in x], positive_counts, width=width, label='Positive', color='green')
    plt.bar(x, neutral_counts, width=width, label='Neutral', color='gray')
    plt.bar([p + width for p in x], negative_counts, width=width, label='Negative', color='red')

    plt.xlabel("Month")
    plt.ylabel("Review Count")
    plt.title("Monthly Sentiment Distribution")
    plt.xticks(ticks=x, labels=months, rotation=45)
    plt.legend()
    plt.tight_layout()
    img1 = io.BytesIO()
    plt.savefig(img1, format='png')
    img1.seek(0)
    grouped_bar_chart_url = base64.b64encode(img1.getvalue()).decode()

    # 2. Line Chart for Trajectory
    plt.figure(figsize=(10, 5))
    plt.plot(months, positive_counts, marker='o', color='green', label='Positive')
    plt.plot(months, neutral_counts, marker='o', color='gray', label='Neutral')
    plt.plot(months, negative_counts, marker='o', color='red', label='Negative')

    plt.xlabel("Month")
    plt.ylabel("Review Count")
    plt.title("Sentiment Trajectory Over Time")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    img2 = io.BytesIO()
    plt.savefig(img2, format='png')
    img2.seek(0)
    line_chart_url = base64.b64encode(img2.getvalue()).decode()

    return render_template('compare.html', 
                           grouped_bar_chart_url=grouped_bar_chart_url,
                           line_chart_url=line_chart_url)



@app.route('/products')
def products():
    
    conn = get_db_connection()
    products  = conn.execute("SELECT * FROM PRODUCTS").fetchall()
    conn.close()

    return render_template('products.html', products=products)

@app.route('/add_product', methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        name = request.form['product_name']
        image_url = request.form['image_url']

        conn = get_db_connection()
        conn.execute("""
                        INSERT INTO PRODUCTS (NAME, IMAGE_URL) 
                        VALUES
                        (?, ?)
                     """, (name, image_url))
        
        conn.commit()
        conn.close()
        return redirect(url_for('products'))
    return render_template('create_product.html')



if __name__ == '__main__':
    app.run(debug=True)