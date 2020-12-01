import boto3
# Get the service resource.
import config as keys

dynamodb = boto3.resource('dynamodb',
                    aws_access_key_id=keys.S3_KEY,
                    aws_secret_access_key=keys.S3_SECRET)

#dynamodb = boto3.resource('dynamodb')

# Create the DynamoDB table.
table = dynamodb.create_table(
    TableName='Story1',
    KeySchema=[
        {
            'AttributeName': 'link',
            'KeyType': 'HASH'
        } 
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'link',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

# Wait until the table exists.
table.meta.client.get_waiter('table_exists').wait(TableName='Story1')

# Print out some data about the table.
print(table.item_count)
