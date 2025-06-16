import json
import boto3
import uuid
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('FeedbackCollector')  # Replace with your actual table name

def lambda_handler(event, context):
    try:
        # Log raw event
        print("Received event:", json.dumps(event))

        # Support both API Gateway proxy and non-proxy formats
        if 'body' in event:
            try:
                body = json.loads(event['body'])
            except json.JSONDecodeError:
                return respond(400, "Invalid JSON in request body.")
        else:
            body = event  # Non-proxy integration sends JSON directly

        # Extract and clean values
        name = body.get('name', '').strip()
        feedback = body.get('feedback', '').strip()

        try:
            rating = int(body.get('rating'))
        except (TypeError, ValueError):
            return respond(400, "Rating must be an integer between 1 and 5.")

        # Validate input
        if not feedback:
            return respond(400, "Feedback text is required.")
        if not (1 <= rating <= 5):
            return respond(400, "Rating must be between 1 and 5.")

        # Construct item for DynamoDB
        item = {
            'ID': str(uuid.uuid4()),
            'feedback': feedback,
            'rating': rating,
            'timestamp': datetime.utcnow().isoformat()
        }

        if name:
            item['name'] = name  # Only include if not empty

        print("Saving item:", item)

        # Save item to DynamoDB
        table.put_item(Item=item)

        return respond(200, "Feedback submitted successfully.")

    except Exception as e:
        print("Unhandled error:", str(e))
        return respond(500, f"Internal server error: {str(e)}")

def respond(status_code, message):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*'
        },
        'body': json.dumps({'message': message})
    }
