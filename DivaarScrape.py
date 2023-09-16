import requests
import json
import pandas as pd
import matplotlib.pyplot as plt

query = "رانا"

def convert_fa_nums(value: str) -> str:
    return value.replace("۰","0").replace("۱", "1").replace("۲", "2").replace("۳", "3").replace("۴", "4").replace("۵", "5").replace("۶", "6").replace("۷", "7").replace("۸", "8").replace("۹", "9")

def clean_num(value:str) :
    value = value.replace("تومان","").replace(",","").replace("٬","").strip()
    if value.isnumeric():
        return int(value)
    else:
        return value

def get_ads(page):
    success = False
    while not success:
        try:
            url = "https://api.divar.ir/v8/web-search/3/light"
            payload = '{"page":' + \
                str(page) + \
                ',"json_schema":{"category":{"value":"light"},"query":"'+query+'","cities":["3"]},"last-post-date":0}'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/json; charset=utf-8',
                'Connection': 'keep-alive',
                'TE': 'trailers'
            }
            response = requests.request(
                "POST", url, headers=headers, data=payload.encode('utf-8'))
            js = json.loads(response.text)
            success = response.ok
            if response.ok:
                return js
        except:
            print("exception occured retring...")
            get_ads(page)


def get_ad_details(ad_token):
    success = False
    while not success:
        try:
            response = requests.get(
                f'https://api.divar.ir/v8/posts-v2/web/{post_data["token"]}')
            js = json.loads(response.text)
            success = response.ok
            if response.ok:
                return js
        except:
            print("exception occured in get ad details, retring...")
            

page_count = int(input("Enter page count to fetch:"))
page = 1
rows = []
while (page <= page_count):
    print(f"Fetching page {page}.")
    js = get_ads(page)

    posts = js["web_widgets"]["post_list"]
    if len(posts) == 0:
        break
    for post in posts:
        post_data = post["data"]
        print("---------------------------------")
        json_post = get_ad_details(post_data["token"])
        sections = json_post["sections"]
        data_section = [
            sec for sec in sections if sec["section_name"] == "LIST_DATA"][0]
        row = {"token":post_data["token"]}
        for widget in data_section["widgets"]:
            if widget["widget_type"] == "UNEXPANDABLE_ROW":
                row[widget["data"]["title"]] = clean_num( convert_fa_nums( widget["data"]["value"]))
            elif widget["widget_type"] == "GROUP_INFO_ROW":
                for item in widget["data"]["items"]:
                    row[item["title"]] = clean_num( convert_fa_nums( item["value"]))
        print(row)
        rows.append(row)
    page += 1
df = pd.DataFrame(rows)
df.to_excel(f'output-{query}.xlsx', encoding='utf-8')
df.hist()

plt.show()