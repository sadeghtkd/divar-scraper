import requests
import json
import pandas as pd
import matplotlib.pyplot as plt

query = "برلیانس H320"

def convert_fa_nums(value: str) -> str:
    return value.replace("۰","0").replace("۱", "1").replace("۲", "2").replace("۳", "3").replace("۴", "4").replace("۵", "5").replace("۶", "6").replace("۷", "7").replace("۸", "8").replace("۹", "9")

def clean_num(value:str) :
    value = value.replace("تومان","").replace(",","").replace("٬","").strip()
    if value.isnumeric():
        return int(value)
    else:
        return value

def get_ads(page):
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
            #'Cookie': '_ga=GA1.2.322852851.1628572990; multi-city=mashhad^%^7C; city=mashhad; _ga_SXEW31VJGJ=GS1.1.1694787170.8.1.1694788282.58.0.0; did=a45164e0-599b-4f53-8c56-08a1d67cf2f1; _gcl_au=1.1.1467059821.1692583415; token=; chat_opened=; sessionid=; _gid=GA1.2.369161043.1694787170; _gat=1',
            'TE': 'trailers'
        }
        response = requests.request(
            "POST", url, headers=headers, data=payload.encode('utf-8'))
        js = json.loads(response.text)
        if js != None:
            return js
        else:
            print("None returned in get ads, retring...")
            get_ads(page)
    except:
        print("exception occured retring...")
        get_ads(page)


def get_ad_details(ad_token):
    try:
        response = requests.get(
            f'https://api.divar.ir/v8/posts-v2/web/{post_data["token"]}')
        js = json.loads(response.text)
        if js != None:
            return js
        else:
            print("None returned in get ad details, retring...")
            get_ad_details(ad_token)
    except:
        print("exception occured in get ad details, retring...")
        get_ad_details(ad_token)

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
                # print(  widget["data"]["title"]+" , "+widget["data"]["value"])
            elif widget["widget_type"] == "GROUP_INFO_ROW":
                for item in widget["data"]["items"]:
                    row[item["title"]] = clean_num( convert_fa_nums( item["value"]))
                    # print(  item["title"]+" , "+item["value"])
        print(row)
        rows.append(row)
    page += 1
df = pd.DataFrame(rows)
df.to_excel(f'output-{query}.xlsx', encoding='utf-8')
df.hist()

plt.show()