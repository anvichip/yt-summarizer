import requests
from api_key import server_url
#url = server_url
def jsonify(url):
    data = {"url" : url }
    return data

def make_api_request(url_vid):
    try:
        url = server_url
        data = jsonify(url_vid)
        print(url)
        print(data)
        response = requests.post(url, json=data)

        # Process the response
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            return None
            #print(f"Request failed with status code {response.status_code}")
    except Exception as e:
        #print(f"An error occurred: {str(e)}")
        return None

# Example usage:
# url1 = "https://anvichip--example-whisper-streaming-main-dev.modal.run"
#data = {"url": "https://www.youtube.com/watch?v=Jqoasg8HJsk"}
# url = 'https://www.youtube.com/watch?v=Jqoasg8HJsk'
# result = make_api_request(url)
# # # # if result is not None:
# print(result)
