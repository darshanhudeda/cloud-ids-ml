import json
import boto3
import joblib
import numpy as np
import os
import tempfile

# AWS clients
s3 = boto3.client('s3')
sns = boto3.client('sns', region_name='us-east-1')

# Environment variables (set in Lambda console)
BUCKET = os.environ['BUCKET_NAME']
SNS_ARN = os.environ['SNS_ARN']


def load_artifact(filename):
    """Download model artifact from S3 and load into memory."""
    tmp_path = os.path.join(tempfile.gettempdir(), filename)
    s3.download_file(BUCKET, f'models/{filename}', tmp_path)
    return joblib.load(tmp_path)


# Load once at cold start (not on every request)
print("Loading model artifacts from S3...")
model = load_artifact('rf_model.pkl')
scaler = load_artifact('scaler.pkl')
label_encoder = load_artifact('label_encoder.pkl')
print("Model loaded and ready.")


def lambda_handler(event, context):
    """
    Main Lambda handler — classifies network traffic.

    Input:
        event['body'] = JSON string with 'features' key
        features = list of 41 numerical values

    Output:
        JSON with prediction, confidence, alert status
    """
    try:
        # Parse request body
        body = json.loads(event['body'])
        features = np.array(body['features']).reshape(1, -1)

        # Scale features
        features_scaled = scaler.transform(features)

        # Predict
        prediction = model.predict(features_scaled)
        category = label_encoder.inverse_transform(prediction)[0]
        confidence = round(float(model.predict_proba(features_scaled).max()), 4)

        # Two-layer alert system:
        # Layer 1: Explicit attack classification
        # Layer 2: Low confidence on normal = suspicious
        is_alert = category != 'normal'
        if category == 'normal' and confidence < 0.60:
            is_alert = True
            category = 'Suspicious'

        # Send SNS alert if attack detected
        if is_alert:
            message = "INTRUSION DETECTED\n"
            message += "Attack Type: " + category + "\n"
            message += "Confidence: " + str(confidence) + "\n"
            message += "Immediate action may be required."

            sns.publish(
                TopicArn=SNS_ARN,
                Subject="IDS ALERT: " + category + " Attack Detected!",
                Message=message
            )

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'prediction': category,
                'confidence': confidence,
                'alert': is_alert
            })
        }

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
