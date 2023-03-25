import os
import requests
import zipfile

API_URL = "https://osu.ppy.sh/api/v2"
TOKEN_URL = 'https://osu.ppy.sh/oauth/token'

username = input("Enter your osu! username: ")
client_id = input("Enter your client id: ")
client_secret = input("Enter your client secret: ")

def get_token():
    data = {
        'client_id': client_id ,
        'client_secret': client_secret ,
        'grant_type': 'client_credentials',
        'scope': 'public'
    }

    response = requests.post(TOKEN_URL, data=data)
    return response.json().get('access_token')

def unzip(file_path, path):
    with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(path)

def main():
    token = get_token()


    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    params = {
        'mode': 'osu',
        'limit': '100',
        'offset': '0'

    }

    user_id = requests.get(f'{API_URL}/users/{username}', params={'key': 'username'}, headers=headers).json()['id']

    beatmaps = requests.get(f'{API_URL}/users/{user_id}/beatmapsets/most_played', params={
        'mode': 'osu', 'limit': '100', 'offset': '0'}, headers=headers).json() + requests.get(f'{API_URL}/users/{user_id}/beatmapsets/most_played', params = {
        'mode': 'osu', 'limit': '100', 'offset': '100'}, headers=headers).json()

    id_list = []
    print(f'{len(beatmaps)} Beatmaps found for user {username} in most played')
    input("Press enter to start downloading beatmaps...")
    path = f"{os.path.dirname(os.path.abspath(__file__))}\osu!dl"
    os.makedirs(path, exist_ok=True)
    num_maps = 0
    for i, beatmap in enumerate(beatmaps):
        id = beatmap['beatmapset']['id']
        title = beatmap["beatmapset"]["title"]
        artist = beatmap["beatmapset"]['artist']

        dl_link = f"https://beatconnect.io/b/{id}"
        file_name = "".join(i for i in rf"{id} {artist} - {title}"  if i not in "\/:*?<>|")
        file_path = rf"{path}\{file_name}.zip"
        folder_path = rf"{path}\{file_name}"

        if os.path.exists(file_path) or os.path.exists(folder_path):
            print(f'Beatmap named {title} already exists, skipping download...')
            if os.path.exists(folder_path):
                print(f"Folder {folder_path} already exists, skipping unzip...")
                continue
            elif os.path.exists(file_path):
                print(f"ZIP File {file_name} already exists, unzipping to folder...")
                os.makedirs(rf'{path}\{file_name}')
                try:
                    unzip(file_path, rf'{path}\{file_name}')
                except:
                    print("Could not unzip file!")
        else:
            print(f'Downloading beatmap {i+1} of {len(beatmaps)} named "{title}"...')
            response = requests.get(dl_link)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            try:
                unzip(file_path, f'{path}\\{file_name}')
                num_maps += 1
            except:
                print("Could not unzip file!")

    print(f"\n{num_maps} beatmap sets downloaded into folder {path}.")



if __name__ == '__main__':
    main()
