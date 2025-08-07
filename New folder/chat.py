import requests

apiKey = "14216400-430c-45a5-a0c9-d0b327e5cac3"
basicUrl = "https://genai.hkbu.edu.hk/general/rest/deployments/gpt-4.1/chat/completions?api-version=2024-10-21"


def submit(message):
    conversation = [{"role": "user", "content": message}]
    url = basicUrl
    headers = { 'Content-Type': 'application/json', 'api-key': apiKey }
    payload = { 'messages': conversation }
    response = requests.post(url, json=payload, headers=headers)
    print(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return 'Error:', response
    

result = submit("Hello!")
print(result)    