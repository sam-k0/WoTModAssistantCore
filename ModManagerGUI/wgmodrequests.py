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
        # https://wgmods.net/api/mods/mods_start_page/?language=en&limit_recommended=12&limit_new=4&limit_updated=4&game_version_id=196
    def get_start_page(self,language:str, recommended:int, new:int, updated:int, game_version:int):
        self.start_page_url = "https://wgmods.net/api/mods/mods_start_page/?language={language}&limit_recommended={recommended}&limit_new={new}&limit_updated={updated}&game_version_id={game_version}"
        self.language = language
        self.recommended = recommended
        self.new = new
        self.updated = updated
        self.game_version = game_version
        self.headers = {
            "Host": "wgmods.net",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "DNT": "1",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0"
        }

        resp = requests.get(self.start_page_url.format(language=self.language, recommended=self.recommended, new=self.new, updated=self.updated, game_version=self.game_version), headers=self.headers)  
        if resp.status_code != 200:
            print(f"Error: {resp.status_code} - {resp.text}")
            return None
        return WGModsSearchResults(resp.text, result_type="start_page")

    def get_search_results(self, search_query:str, language:str, limit:int, game_version:int):
        # https://wgmods.net/api/mods/?limit=12&offset=0&ordering=-rating&query=Replay&game_version_id=196

        # if game_version is 0 or None, it will not be included in the URL
        if game_version == 0 or game_version is None:
            self.search_url = "https://wgmods.net/api/mods/?limit={limit}&offset=0&ordering=-rating&query={search_query}&language={language}"
        else:
            self.search_url = "https://wgmods.net/api/mods/?limit={limit}&offset=0&ordering=-rating&query={search_query}&game_version_id={game_version}&language={language}"
        self.search_query = search_query
        self.language = language
        self.limit = limit
        self.game_version = game_version
        self.headers = {
            "Host": "wgmods.net",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "X-Requested-With": "XMLHttpRequest",
            "DNT": "1",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
            "Referer": "https://wgmods.net/search/?title={search_query}",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0"
        }

        resp = requests.get(self.search_url.format(search_query=self.search_query, language=self.language, limit=self.limit, game_version=self.game_version), headers=self.headers)
        if resp.status_code != 200:
            print(f"Error: {resp.status_code} - {resp.text}")
            return None
        print(resp.text)
        return WGModsSearchResults(resp.text, result_type="search_results")
    
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
    def __init__(self, json_data:str, result_type:str="start_page"):
        if result_type not in ["start_page", "search_results"]:
            raise ValueError("Invalid type. Must be 'start_page' or 'search_results'.")
        self.json_data_str = json_data
        self.json_data = json.loads(json_data)
        self.result_type = result_type
        # Handle the different result types differently, idk why but wgmods.net has two different structures for the results
        if result_type == "start_page":
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

        elif result_type == "search_results": # different structure
            self.search_results_count = self.json_data["count"]
            self.search_results_list_raw = self.json_data["results"]
            self.search_mods_list = []

            for mod in self.search_results_list_raw:
                self.search_mods_list.append(WGModsMod(mod))

    def get_new_mods(self) -> list[WGModsMod]:
        if self.result_type != "start_page":
            raise ValueError("This method is only available for 'start_page' results.")
        return self.new_mods_list
    
    def get_recommended_mods(self)-> list[WGModsMod]:
        if self.result_type != "start_page":
            raise ValueError("This method is only available for 'start_page' results.")
        return self.recommended_mods_list
    
    def get_updated_mods(self) -> list[WGModsMod]:
        if self.result_type != "start_page":
            raise ValueError("This method is only available for 'start_page' results.")
        return self.updated_mods_list

    def get_search_mods(self) -> list[WGModsMod]:
        if self.result_type != "search_results":
            raise ValueError("This method is only available for 'search_results' results.")
        return self.search_mods_list
            


if __name__ =="__main__":
    req = WGModsRequest().get_search_results("Replay", "en", 10, 196)

    print(req.get_search_mods()[0].mod_name_eng)
