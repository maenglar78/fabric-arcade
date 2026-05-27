import requests
import json
import base64
import subprocess
import time

# Get token
token_result = subprocess.run(
    'az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv',
    capture_output=True, text=True, shell=True
)
token = token_result.stdout.strip()

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

workspace_id = 'a5235927-0289-4a06-83d1-456be383b496'
notebook_id = '27407ece-4b0a-4ba8-b00b-ad08ca9507c6'
base_url = f'https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/notebooks/{notebook_id}'

import os
os.chdir(r'c:\FabricMCP\FabricArcade')

# Load notebook
with open('catalog/fabric-racing-game/notebooks/racing_game_v2.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Local notebook: {len(nb['cells'])} cells")

# Encode
nb_json = json.dumps(nb)
b64 = base64.b64encode(nb_json.encode()).decode()
print(f"Payload size: {len(b64)} bytes")

# Create definition
definition = {
    'definition': {
        'format': 'ipynb',
        'parts': [{
            'path': 'notebook-content.ipynb',
            'payload': b64,
            'payloadType': 'InlineBase64'
        }]
    }
}

# Upload
print("\nUploading...")
response = requests.post(f'{base_url}/updateDefinition', headers=headers, json=definition)
print(f"Status: {response.status_code}")

if response.status_code == 202:
    location = response.headers.get('Location')
    print(f"LRO URL: {location}")
    
    # Poll LRO
    for i in range(10):
        time.sleep(2)
        lro_response = requests.get(location, headers={'Authorization': f'Bearer {token}'})
        lro_data = lro_response.json()
        print(f"Poll {i+1}: {lro_data.get('status')}")
        if lro_data.get('status') == 'Succeeded':
            print("✅ Upload succeeded!")
            break
        elif lro_data.get('status') == 'Failed':
            print(f"❌ Failed: {lro_data.get('error')}")
            break
    
    # Verify by getting definition
    print("\nVerifying...")
    get_response = requests.post(f'{base_url}/getDefinition?format=ipynb', 
                                  headers=headers, json={})
    if get_response.status_code == 202:
        get_location = get_response.headers.get('Location')
        time.sleep(3)
        get_lro = requests.get(get_location, headers={'Authorization': f'Bearer {token}'})
        if get_lro.json().get('status') == 'Succeeded':
            result = requests.get(f'{get_location}/result', headers={'Authorization': f'Bearer {token}'})
            result_data = result.json()
            payload = result_data['definition']['parts'][0]['payload']
            print(f"Retrieved payload size: {len(payload)} bytes")
            
            # Decode and check
            decoded = json.loads(base64.b64decode(payload).decode())
            print(f"Retrieved notebook: {len(decoded['cells'])} cells")
            print(f"First cell preview: {decoded['cells'][0]['source'][0][:50]}...")
else:
    print(f"Error: {response.text}")
