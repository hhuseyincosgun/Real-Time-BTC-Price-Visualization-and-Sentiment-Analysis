import json
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime

def convert_rows_to_epoch(rows):
    result = []
    for row in rows:
        epoch_row = {}
        for key, value in row.items():
            if key == 'kline_time':
                if isinstance(value, datetime):
                    epoch_row[key] = int(value.timestamp()) * 1000  # Convert to milliseconds for Highcharts
                else:
                    # Assuming 'kline_time' is in a format like 'YYYY-MM-DD HH:MM:SS'
                    dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                    epoch_row[key] = int(dt.timestamp()) * 1000  # Convert to milliseconds for Highcharts
            else:
                if key == 'moon_age':
                    epoch_row[key] = int(value)
                else:    
                    epoch_row[key] = str(value)
        result.append(epoch_row)
    return result

def lambda_handler(event, context):
    try:
        # Fetch database credentials from environment variables
        db_host = os.environ['DB_HOST']
        db_user = os.environ['DB_USER']
        db_password = os.environ['DB_PASSWORD']
        db_name = 'btcDB'  # Updated to your database name
        db_port = int(os.environ.get('DB_PORT', 3306))

        # Check if queryStringParameters exists in the event object
        if 'queryStringParameters' in event and event['queryStringParameters']:
            start_date = event['queryStringParameters'].get('startDate')
            end_date = event['queryStringParameters'].get('endDate')
            
            if not start_date or not end_date:
                return {
                    'statusCode': 400,
                    'body': json.dumps({"error": "Missing startDate or endDate parameter"})
                }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "Missing query parameters"})
            }

        # Establish database connection
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Define the SQL query
            query = """
                WITH daily_first_row AS (
    SELECT
        k.event_time AS kline_time,
        k.close_price AS btc_close_price,
        m.age AS moon_age,
        ROW_NUMBER() OVER (PARTITION BY DATE(k.event_time) ORDER BY k.event_time) AS row_num
    FROM
        kline_data k
    JOIN
        moon m ON k.event_time = m.time
    WHERE
        k.event_time BETWEEN %s AND %s
)
SELECT
    kline_time,
    btc_close_price,
    moon_age
FROM
    daily_first_row
WHERE
    row_num = 1;

            """
            
            cursor.execute(query, (start_date, end_date))
            rows = cursor.fetchall()

            cursor.close()
            connection.close()

            # Convert rows to epoch format
            rows_epoch = convert_rows_to_epoch(rows)

            return {
                'statusCode': 200,
                'headers': {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                'body': json.dumps(rows_epoch)
            }

    except Error as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({"error": "Internal server error"})
        }
