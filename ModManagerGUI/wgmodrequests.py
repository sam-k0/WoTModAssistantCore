import requests
import json


def download_from_url(url:str, fullfilepath:str, progress_callback=None):
    resp= requests.get(url, stream=True)
    total_size = int(resp.headers.get('content-length', 0))

    if total_size == 0:
        with open(fullfilepath, 'wb') as f:
            f.write(resp.content)
    else:
        downloaded = 0
        with open(fullfilepath, 'wb') as f:
            for data in resp.iter_content(chunk_size=4096):
                downloaded += len(data)
                f.write(data)
                if progress_callback:
                    progress_callback(downloaded, total_size)




class WGModsRequest:
    def __init__(self):
        pass

    def get_start_page(self,language:str, recommended:int, new:int, updated:int, game_version:int):
        self.start_page_url = "https://wgmods.net/api/mods/mods_start_page/?language={language}&limit_recommended={recommended}&limit_new={new}&limit_updated={updated}&game_version_id={game_version}"
        self.language = language
        self.recommended = recommended
        self.new = new
        self.updated = updated
        self.game_version = game_version
        self.headers = {
            "Host": "wgmods.net",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i"
        }

        resp = requests.get(self.start_page_url.format(language=self.language, recommended=self.recommended, new=self.new, updated=self.updated, game_version=self.game_version), headers=self.headers)  
        return WGModsSearchResults(resp.text)


    def get_mod_page(self, mod_id:int):
        self.mod_page_url = "https://wgmods.net/{mod_id}"
        self.mod_id = mod_id
        self.headers = {
            "Host": "wgmods.net",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json; charset=utf-8",
            "Connection": "keep-alive",
            "Referer": f"https://wgmods.net/{self.mod_id}/",
            "Cookie": "csrftoken=1pKko8fosLtGbtOEP6yTOhG3iG8zA148USxLTZQxCjq7gYPmhsOQruW7Yn0NMbfj; cm.internal.bs_id=e7323626-f07d-42b5-f9d0-07e9ad91daea; userrealm=ru; csrftoken=1pKko8fosLtGbtOEP6yTOhG3iG8zA148USxLTZQxCjq7gYPmhsOQruW7Yn0NMbfj; userrealm=ru",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }


class WGModsMod:
    def __init__(self, json_data:dict):
        self.json_dict = json_data
        self.mod_id = self.json_dict["id"]
        self.author_name = self.json_dict["owner"]["spa_username"]
        # mod name localized
        self.mod_name_eng = ""
        self.mod_name_rus = ""

        for elem in self.json_dict["localizations"]:
            if elem["lang"]["code"] == "en": # get the english name
                self.mod_name_eng = elem["title"]
            if elem["lang"]["code"] == "ru": # get the russian name
                self.mod_name_rus = elem["title"]

        self.download_url = ""

        # Get newest version
        newest_version = self.json_dict["versions"][0]
        self.download_url = newest_version["download_url"]
        self.game_version_id = newest_version["game_version"]["id"]
        self.game_version_human= newest_version["game_version"]["version"]

class WGModsSearchResults:
    def __init__(self, json_data:str):
        self.json_data_str = json_data
        self.json_data = json.loads(json_data)

        new_mods = self.json_data["new"]
        recommended_mods = self.json_data["recommended"]
        updated_mods = self.json_data["updated"]

        self.new_mods_count = new_mods["count"]
        self.recommended_mods_count = recommended_mods["count"]
        self.updated_mods_count = updated_mods["count"]

        new_mods_list_raw = new_mods["results"]
        recommended_mods_list_raw = recommended_mods["results"]
        updated_mods_list_raw = updated_mods["results"]

        self.new_mods_list = []
        self.recommended_mods_list = []
        self.updated_mods_list = []

        for mod in new_mods_list_raw:
            self.new_mods_list.append(WGModsMod(mod))
        
        for mod in recommended_mods_list_raw:   
            self.recommended_mods_list.append(WGModsMod(mod))

        for mod in updated_mods_list_raw:
            self.updated_mods_list.append(WGModsMod(mod))

    def get_new_mods(self):
        return self.new_mods_list
    
    def get_recommended_mods(self):
        return self.recommended_mods_list
    
    def get_updated_mods(self):
        return self.updated_mods_list
            


if __name__ =="__main__":
    req = WGModsRequest().get_start_page("en", 10, 10, 10, 185)
    


    