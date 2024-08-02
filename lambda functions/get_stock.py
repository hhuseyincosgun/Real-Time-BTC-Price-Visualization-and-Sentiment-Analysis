import os
import json
import mysql.connector
from mysql.connector import Error

def lambda_handler(event, context):
    try:
        # Fetching environment variables
        db_host = os.environ['DB_HOST']
        db_user = os.environ['DB_USER']
        db_password = os.environ['DB_PASSWORD']
        db_name = os.environ['DB_NAME']
        db_port = os.environ['DB_PORT']
        
        # Extracting query parameters from the event
        stock1 = event['queryStringParameters']['stock1']
        stock2 = event['queryStringParameters']['stock2']
        startDate = event['queryStringParameters']['startDate']
        endDate = event['queryStringParameters']['endDate']
        
        # Establishing the connection
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Query to fetch stock data based on the parameters
            query = """
                SELECT Date, {stock1}, {stock2}
                FROM stockcomparison
                WHERE Date BETWEEN %s AND %s
            """.format(stock1=stock1, stock2=stock2)
            
            cursor.execute(query, (startDate, endDate))
            rows = cursor.fetchall()

            # Closing the cursor and connection
            cursor.close()
            connection.close()

            return {
                'statusCode': 200,
                'headers': {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": event['headers']['origin']
                },
                'body': json.dumps(rows)
            }

    except Error as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
