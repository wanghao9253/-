import requests
from lxml import etree
import re
import execjs
import time
import os


class GetMusic:
    def __init__(self, gedan_id):
        self.gedan_id = gedan_id  # 歌单id
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36"
        }

    def get_music_data(self):
        response = requests.get(f"https://music.163.com/playlist?id={self.gedan_id}", headers=self.headers)  # 请求歌单页面
        text = response.content.decode("utf-8")
        html_element = etree.HTML(text)
        li_list = html_element.xpath("//ul[@class='f-hide']/li")  # 歌曲li
        item_list = []  # 歌曲列表
        for li in li_list:
            item = dict()
            href = li.xpath("./a/@href")[0]  # /song?id=515601126
            item["id"] = re.findall("id=(.*)", href)[0]  # 匹配歌曲id
            item["name"] = li.xpath("./a/text()")[0]  # 歌曲名
            item_list.append(item)
        return item_list

    def get_music(self, id):
        js = open('./music.js', 'r').read()
        ext = execjs.compile(js, cwd=r'F:\nodejs\node_global\node_modules')
        result = ext.call('start', id)
        data = result
        headers = {
            "cookie": "_iuqxldmzr_=32; _ntes_nuid=1327493c62a1f635ca97e7e6dc8fc980; WM_TID=2wWCAomgT2JABBAQUBYptTQQsxpIyKH7; mail_psc_fingerprint=6dcc26c996acf5fe872eb0698dd0a940; usertrack=CrGYY12G2OahenXNAxm4Ag==; vinfo_n_f_l_n3=7bd22332ad5b1402.1.1.1568705256411.1568705324397.1572854751503; nts_mail_user=wanghao9253@163.com:-1:1; _ga=GA1.2.734435097.1581565312; __root_domain_v=.163.com; _qddaz=QD.qo1ld3.e7t4wa.k6qdnm8l; P_INFO=925378361@qq.com|1584539933|0|partner|00&99|shh&1584539878&partner#shh&null#10#0#0|&0|partner|925378361@qq.com; _ntes_nnid=1327493c62a1f635ca97e7e6dc8fc980,1592187734993; WM_NI=FII3n0AuyNXK4bQIjiywOUo8pzQAcG36RypYkpMjCUWDDbCsh8sWSFgG%2FfAtAV3uKYsfcrqzBq%2BW3q8fG4WZriwz15X8SnVOBqm6G9pIWdilS3iVkThex3gS69QJ%2F9pQNFc%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eeb5d14292a7b886c94a95ac8fb7c44e869e8aaff150a2befa94e247a2b7ae89c42af0fea7c3b92a869787d4ed3c83abb7afdb41f8be9faae963bba981b6ee34b4a69fa2e24df1ea9e9af353a9b0838bc25f959c8c83c279ace8bdb8d24ea599e187c480838afd96ca53b1baad93f47282afe5b8b27bfcba89d5d652b2b7b99bb43f9ce89d8fd54582afa3d7c633b4979985ec6891eda7b7ea60acbbb8d4e659f6e79fabae33b48f82a7e237e2a3; ntes_kaola_ad=1; JSESSIONID-WYYY=JbJOJJFpytfrHiUr4f%2BnuFSvPR8HWD%2FfP635oNyO%5C%2BE0tHe9vuIVTHxl75fz%2F11WegAbW%2BOpmZg%2BWNODF%2F0nAps0Zb24UderRcYTHreGh11YBcDfcPgt6gGtE0EFWQqfX32cbl%5CNts%2BvvM%2F%5Cc5jZtryV0KlH3gM1Kj4ei2ckw1xcQs7T%3A1592915435869",
            "referer": "https://music.163.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        }
        response = requests.post("https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token=", headers=headers,
                                 data=data)
        return response.json()

    def download_music(self, music_name, music_url):
        """
        :param music_name: 歌曲名
        :param music_url: 歌曲下载url
        :return:
        """
        content = requests.get(f"{music_url}").content
        if not os.path.exists(f'./{self.gedan_id}'):
            os.makedirs(f"{self.gedan_id}")
        with open(f"./{self.gedan_id}/{music_name}.m4a", "wb") as f:
            f.write(content)

    def run(self):
        data_list = self.get_music_data()  # 获取歌曲数据
        for data in data_list:
            id = f"[{data['id']}]"  # 将歌曲id两边加上 [],然后转字符串
            response = self.get_music(id)  # 传入："[歌曲id]"，通过执行js文件获取歌曲下载地址
            music_url = response["data"][0]["url"]  # 音乐下载url
            music_name = data["name"]  # 音乐名字
            print(f"下载{music_name}")
            try:
                self.download_music(music_name=music_name, music_url=music_url)
            except requests.exceptions.MissingSchema:
                print(f"{music_name}为vip歌曲，下载失败")
            except FileNotFoundError:
                print(f"{music_name}有特殊字符，下载失败")
                rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
                music_name = re.sub(rstr, "_", music_name)
                print(f"重新下载{music_name}")
                self.download_music(music_name=music_name, music_url=music_url)
                print(f"{music_name},下载成功")
            else:
                print(f"{music_name},下载成功")
            time.sleep(1)


if __name__ == '__main__':
    get_music = GetMusic(2821115454)  # 歌单id
    get_music.run()
