import os
import json
import mysql.connector
from mysql.connector import Error

def lambda_handler(event, context):
    try:
        db_host = os.environ['DB_HOST']
        db_user = os.environ['DB_USER']
        db_password = os.environ['DB_PASSWORD']
        db_name = os.environ['DB_NAME']
        db_port = os.environ['DB_PORT']
        
        print("Received event:", json.dumps(event))
        
        # Check if queryStringParameters exists in the event object
        if 'queryStringParameters' in event and event['queryStringParameters']:
            startDate = event['queryStringParameters'].get('startDate')
            endDate = event['queryStringParameters'].get('endDate')
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "Missing query parameters"})
            }
        
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT Date, BTCUSD, CRUDE_OIL, DOW_JONES, ETHER, EUR, GOLD, NASDAQ100, SILVER, SP500
                FROM nebahat
                WHERE Date BETWEEN %s AND %s
            """
            
            cursor.execute(query, (startDate, endDate))
            rows = cursor.fetchall()
            
            cursor.close()
            connection.close()

            return {
                'statusCode': 200,
                'headers': {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": event["headers"]["origin"]
                },
                'body': json.dumps(rows)
            }

    except Error as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
