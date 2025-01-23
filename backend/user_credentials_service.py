from datetime import datetime, timedelta
from azure.data.tables import TableServiceClient
import secrets
import json

# Reads the "secrets.json" file containing configuration details like the Azure Storage key.
with open("secrets.json") as config_file:
    config = json.load(config_file)

storage_key = config["AZURE_STORAGE_KEY"]
connection_string = f"DefaultEndpointsProtocol=https;AccountName=cohort5storage;AccountKey={storage_key};EndpointSuffix=core.windows.net"
table_service = TableServiceClient.from_connection_string(conn_str=connection_string)
table_name = "Credentials"
table_client = table_service.get_table_client(table_name)

# Function to generate a secure random token
# Uses the `secrets` module to generate a hex-encoded token of the specified length (default: 25 bytes).
def generate_token(length: int = 25):
    return secrets.token_hex(length)

# Function to save a generated token into the Azure Table Storage
# Stores the token along with user details and timestamp in the "Credentials" table.
def save_token(user_id: str, email: str):
    entity = {
        "PartitionKey": "Users",  
        "RowKey": user_id,        
        "Token": generate_token(), 
        "Email": email,
        "CreatedAt": datetime.now().isoformat(), 
    }
    # Insert the entity into the Azure Table Storage.
    table_client.create_entity(entity)
    return entity

# Function to retrieve a token from the Azure Table Storage for a specific user
# Queries the table using the PartitionKey ("Users") and RowKey (user_id).
def retreive_token(user_id):
    try:
        entity = table_client.get_entity(partition_key="Users", row_key=user_id)
        return entity["Token"]  
    except Exception as e:
        return f"Error retrieving item: {str(e)}"

# Function to authenticate a user based on their user ID and token.
def authenticate(user_id, token: str):
    try:
        entity = retreive_token(user_id)
    except Exception as e:
        return f"Error retrieving item: {str(e)}"
        
    if entity==token:
        return True
    else:
        return False
