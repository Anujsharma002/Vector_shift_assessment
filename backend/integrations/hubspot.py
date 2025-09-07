# hubspot.py

import json
import secrets
import base64
import asyncio
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
from redis_client import add_key_value_redis, get_value_redis, delete_key_redis
from integrations.integration_item import IntegrationItem

# Replace with your HubSpot app credentials
CLIENT_ID = 'clientid'
CLIENT_SECRET = 'client-secreate'
REDIRECT_URI = 'http://localhost:8000/integrations/hubspot/oauth2callback'
SCOPES = 'crm.objects.contacts.read'

# Step 1: Generate HubSpot OAuth authorization URL
async def authorize_hubspot(user_id, org_id):
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id
    }
    encoded_state = json.dumps(state_data)
    # Save state in Redis for later verification
    await add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', encoded_state, expire=600)

    authorization_url = (
        f'https://app.hubspot.com/oauth/authorize'
        f'?client_id={CLIENT_ID}'
        f'&redirect_uri={REDIRECT_URI}'
        f'&scope={SCOPES}'
        f'&state={encoded_state}'
        f'&response_type=code'
    )
    return authorization_url

# Step 2: OAuth callback handler
async def oauth2callback_hubspot(request: Request):
    if request.query_params.get('error'):
        raise HTTPException(status_code=400, detail=request.query_params.get('error'))

    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')
    if not code or not encoded_state:
        raise HTTPException(status_code=400, detail='Missing code or state in callback.')

    state_data = json.loads(encoded_state)
    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')

    saved_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}')
    if not saved_state or original_state != json.loads(saved_state).get('state'):
        raise HTTPException(status_code=400, detail='State does not match.')

    # Exchange authorization code for access token
    async with httpx.AsyncClient() as client:
        token_response, _ = await asyncio.gather(
            client.post(
                'https://api.hubapi.com/oauth/v1/token',
                data={
                    'grant_type': 'authorization_code',
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'redirect_uri': REDIRECT_URI,
                    'code': code
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            ),
            delete_key_redis(f'hubspot_state:{org_id}:{user_id}')
        )

    token_data = token_response.json()
    if 'access_token' not in token_data:
        raise HTTPException(status_code=400, detail=f"Failed to get access token: {token_data}")

    # Save credentials in Redis temporarily
    await add_key_value_redis(
        f'hubspot_credentials:{org_id}:{user_id}',
        json.dumps(token_data),
        expire=600
    )

    # Close OAuth window
    return HTMLResponse(content="<html><script>window.close();</script></html>")

# Step 3: Retrieve credentials
async def get_hubspot_credentials(user_id, org_id):
    credentials = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    credentials = json.loads(credentials)
    # Optional: remove after retrieval
    await delete_key_redis(f'hubspot_credentials:{org_id}:{user_id}')
    return credentials

# Step 4: Map HubSpot object to IntegrationItem
def create_integration_item_metadata_object(response_json):
    name = response_json.get('properties', {}).get('firstname') or response_json.get('properties', {}).get('name', 'Unnamed Item')
    return IntegrationItem(
        id=response_json.get('id'),
        type='hubspot_object',
        name=name,
        creation_time=response_json.get('createdAt', None),
        last_modified_time=response_json.get('updatedAt', None),
        parent_id=None
    )

# Step 5: Retrieve HubSpot items
async def get_items_hubspot(credentials):
    access_token = credentials.get('access_token')
    if not access_token:
        raise HTTPException(status_code=400, detail='Access token missing.')

    async with httpx.AsyncClient() as client:
        response = await client.get(
            'https://api.hubapi.com/crm/v3/objects/contacts',
            headers={'Authorization': f'Bearer {access_token}'}
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"HubSpot API error: {response.text}")

    results = response.json().get('results', [])
    return [create_integration_item_metadata_object(item) for item in results]
