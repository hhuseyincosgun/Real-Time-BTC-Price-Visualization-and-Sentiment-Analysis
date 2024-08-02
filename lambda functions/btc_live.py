import json
import mysql.connector
from datetime import datetime

RDS_HOST = 'database-1.cv4u0u4003q1.eu-central-1.rds.amazonaws.com'
RDS_USER = 'admin'
RDS_PASSWORD = 'tpN4dpYJ2S9di0vhAXWt'
RDS_DB = 'btcDB'

def get_db_connection():
    conn = mysql.connector.connect(
        host=RDS_HOST,
        user=RDS_USER,
        password=RDS_PASSWORD,
        database=RDS_DB
    )
    return conn

def lambda_handler(event, context):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT event_time, open_price, high_price, low_price, close_price, sentiment, no_comments FROM kline_data WHERE event_time >= NOW() - INTERVAL 1 HOUR"
    cursor.execute(query)
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    data = []
    for row in rows:
        date = row['event_time']
        open_price = float(row['open_price'])
        high = float(row['high_price'])
        low = float(row['low_price'])
        close = float(row['close_price'])
        sentiment = float(row['sentiment']) if row['sentiment'] is not None else 0
        comments = int(row['no_comments']) if row['no_comments'] is not None else 0
        timestamp = int(date.timestamp() * 1000)
        data.append([timestamp, open_price, high, low, close, sentiment, comments])
    
    return {
        'statusCode': 200,
        'body': json.dumps(data),
        'headers': {
            'Content-Type': 'application/json',
            "Access-Control-Allow-Origin": event['headers']['origin']
        }
    }
