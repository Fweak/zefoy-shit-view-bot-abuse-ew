import requests
import time
import shutil
import re
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bs4 import BeautifulSoup
from urllib.parse import unquote
from base64 import b64decode


class Zefoy:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0",
        "Accept": "*",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Host": "zefoy.com",
    }

    @staticmethod
    def decode(string: str):
        return b64decode(unquote(string[::-1])).decode("utf-8").replace("\n", "  ")

    @staticmethod
    def make_request(
        method: str,
        path: str,
        cookies: requests.cookies.RequestsCookieJar,
        body: dict = None,
    ) -> requests.PreparedRequest():
        request = requests.Request(
            method=method,
            url="https://zefoy.com" + path,
            headers=Zefoy.headers.copy(),
            cookies=cookies,
        )

        if body != None:
            multipart_data = MultipartEncoder(fields={k: body[k] for k in body})
            request.headers["Content-Type"] = multipart_data.content_type
            request.data = multipart_data
        if "_CAPTCHA" in path:
            request.headers["Sec-Fetch-Dest"] = "image"
            request.headers["Sec-Fetch-Mode"] = "no-cors"
            request.headers["Accept"] = "image/avif,image/webp,*/*"
        if "c2VuZC9mb2xeb3dlcnNfdGlrdG9V" in path:
            request.headers["X-Requested-With"] = "XMLHttpRequest"
            request.headers["Sec-Fetch-Dest"] = "empty"
            request.headers["Sec-Fetch-Site"] = "same-origin"
            request.headers["Origin"] = "https://zefoy.com"
            del request.headers["Upgrade-Insecure-Requests"]

        return request.prepare()


class ViewBotter:
    def __init__(self, tiktok_url: str, count: int) -> None:
        self.tiktok = tiktok_url
        self.count = count

        self.session = None
        self.captcha_url = None
        self.form_action_key = None
        self.form_input_key = None
        self.views_name = None
        self.views_value = None
        self.captcha_payload = dict()

    def create_session(self, proxy: str):
        self.session = requests.Session()

    def get_cookies(self):
        cookies = self.session.send(Zefoy.make_request("GET", "/", self.session.cookies))

        if cookies.status_code != 200:
            print("error.. bad status code", cookies.text)
            exit(1)
            return

        main_html = BeautifulSoup(cookies.text, "html.parser")
        main_form = main_html.find("form", attrs={"method": "POST"})
        main_inputs = main_form.find_all("input")
        for i in main_inputs:
            try:
                self.captcha_payload[i["name"]] = i["value"]
            except KeyError:
                if i["name"] == "token":
                    self.captcha_payload["token"] = ""
                    continue
                self.captcha_payload["captcha"] = i["name"]

        self.captcha_url = re.findall(r"(\/\w+\.php\?(.*))cl", cookies.text, re.MULTILINE)[0][0].split('"')[0]
        print("[COOKIES]: ", cookies.status_code)

    def request_captcha(self):
        captcha_response = self.session.send(Zefoy.make_request("GET", f"{self.captcha_url}", self.session.cookies), stream=True)

        with open(f"./data/blob_{self.count}.png", "wb") as f:
            captcha_response.raw.decode_content = True
            shutil.copyfileobj(captcha_response.raw, f)
            f.close()

        self.session.cookies.set("user_agent","Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0")
        self.session.cookies.set("window_size", "1920x947")
        print("[CAPTCHA]: ", captcha_response.status_code)

    def post_captcha(self, code: str):
        payload = self.captcha_payload
        payload[payload["captcha"]] = code
        del payload["captcha"]

        post_captcha_response = self.session.send(Zefoy.make_request("POST", f"/",self.session.cookies,payload))
        print("[SENTCAPTCHA]: ", post_captcha_response.status_code)
        self.parse_captcha_request(post_captcha_response.text)

    def parse_captcha_request(self, html: str):
        soup = BeautifulSoup(html, "html.parser")
        form_element = soup.find("div", attrs={"class": "t-views-menu"}).find("form")
        self.form_action_key = form_element.attrs["action"]
        self.form_input_key = form_element.find("input", attrs={"type": "search"}).attrs["name"]

    def send_verify(self):
        verify_response = self.session.send(Zefoy.make_request( "POST","/" + self.form_action_key,self.session.cookies,{self.form_input_key: self.tiktok}))
        print("[VERIFYREQUEST]: ", verify_response.status_code)

        self.parse_verify_request(verify_response.text)

    def parse_verify_request(self, html: str):
        soup = BeautifulSoup(Zefoy.decode(html), "html.parser")
        myes = soup.find("form").find("input")
        self.views_name = myes.attrs["name"]
        self.views_value = myes.attrs["value"]

    def send_views(self):
        views_response = self.session.send(Zefoy.make_request( "POST", "/" + self.form_action_key, self.session.cookies, {self.views_name: self.views_value}))
        print("[VIEWSREQUEST]: ", views_response.status_code)
        print(Zefoy.decode(views_response.text))


if __name__ == "__main__":
    print(
        """
⣤⡶⠛⣉⣋⠛⠻⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⡟⠀⣾⣿⣿⣿⠀⢻⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣷⡀⣘⡿⣷⠟⢀⣼⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠿⠟⠿⣽⡇⢰⣟⡃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣤⣤⣴⡦⠀
⠀⠀⠀⣸⣇⣸⣯⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⣤⣤⣤⣤⣦⣤⣤⣄⣀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾⠋⣡⣤⣧⡈⠹⡗
⠀⠀⠀⣷⡏⠀⢹⣷⠀⠀⠀⠀⢀⣠⣴⣾⣿⠿⠶⠞⢛⣫⣭⣭⣝⣽⣿⣿⣿⣿⣻⡛⢦⣄⡀⠀⠀⠀⠀⠀⠀⢨⣅⠀⣿⣾⣟⡿⠀⣹
⠀⠀⠀⠓⠛⠷⠟⠿⠀⠀⣤⣾⣿⠷⠛⠁⠀⣠⣴⣾⠿⠛⠛⠿⠛⠉⠉⠉⠙⠋⠙⠛⠷⣮⣳⣆⡀⠀⠀⠀⠀⠀⠉⢿⡯⠟⠛⢁⣠⡟
⠀⠀⠀⠀⠀⠀⠀⠀⣤⣾⡿⠋⠀⠀⠀⣰⣾⠿⠋⠀⠀⠀⠀⠀⠀⠀⠂⠀⠀⠙⣦⠀⠀⠀⠙⢮⡿⣄⠀⠀⠀⠀⣤⣾⠁⣴⢾⡿⠟⠀
⠀⠀⠀⠀⠀⠀⢀⣼⣷⠏⠀⠤⠈⢀⣾⡿⠋⠀⠀⠀⠀⢸⡃⠀⠈⠀⡀⠀⠠⠀⠸⣇⠀⠀⠀⠀⢻⣞⢧⡀⠀⢸⡷⠛⢶⣿⡛⠀⠀⠀
⠀⠀⠀⠀⠀⢀⣾⣳⠏⠀⢀⠂⢀⣿⡟⠀⢀⡄⠀⠀⢀⣿⠀⠀⠀⢰⠇⠀⠐⠀⠀⣿⡀⠀⠀⢳⡀⠹⣏⣷⠀⢚⣷⣀⣤⡿⠁⠀⠀⠀
⠀⠀⠀⠀⠀⢸⣿⡟⠀⢈⠀⠀⣼⡟⠀⠀⣇⠀⠰⠚⢛⡯⠁⠐⠀⢸⠆⠀⠈⠀⠀⢹⡏⠑⠀⠈⣷⠀⢹⣟⡇⠀⠉⠉⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣿⣿⠃⠀⢂⠀⢠⣿⠁⠀⠐⣿⠀⠀⠀⣾⡇⠀⠐⠀⣹⠆⠃⠈⠀⢠⡞⣷⠀⠀⠀⢿⡀⠈⣿⣿⠄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⣿⣿⠀⡀⠂⠄⣸⡿⠀⠀⢈⣿⠀⠀⠀⣿⣗⠀⢀⠀⣽⡆⠁⠀⠀⢰⣏⣿⡃⠀⠀⢸⡇⠀⣻⣽⣧⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢸⡏⣟⠀⠠⢁⠢⢸⡏⠀⠁⢈⣷⠀⠀⠐⣿⣿⠀⠀⠀⣿⡇⣶⠀⠀⢸⣧⣟⣇⠀⠀⣿⡇⢠⡜⣧⢿⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣸⣷⣏⠀⣷⠛⠀⣿⡇⠀⠀⢈⣿⣀⣠⣴⣿⣿⣻⣤⡴⣿⣧⡿⣤⢦⣾⣷⣿⣿⣶⣶⣿⡇⠈⣿⡹⣯⣇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣽⣽⠃⢰⡏⠁⣸⣿⡇⠀⡀⠠⣿⣿⣿⣿⣿⣿⣿⣍⠁⠀⠀⠀⠀⠀⣹⣿⣿⣷⣬⡽⢿⡇⠀⣹⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣼⣿⡟⠀⣾⠃⢀⣾⣿⣿⠀⡁⠀⣿⠀⢻⣿⣿⣾⣿⣿⠀⠀⠀⠄⠀⠀⢸⣿⣿⣿⣿⠇⣿⠀⣷⣿⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣿⣹⠀⢰⣿⠀⢨⣟⡿⣽⡆⠀⡀⢿⡀⠈⠻⠾⣽⠟⠃⠀⠀⠀⠀⡁⠀⠀⠙⠛⠋⠁⡘⣷⠀⢿⣿⣽⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣿⣿⠀⢸⡿⡀⠈⡿⣷⢸⡇⢻⡄⢺⡅⠐⢄⢠⠀⢀⠀⠈⠀⠈⠀⠀⠈⠀⠄⢂⠂⡑⠀⣿⠆⣻⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣿⣽⡆⠘⣿⣷⡀⢱⠻⣦⣟⠸⣇⠼⣇⠈⠄⠠⠈⠀⡀⠄⠀⠄⠀⠄⢀⠁⠠⠀⠀⣀⣴⡟⠡⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠈⢳⣹⣆⡹⣶⢋⡔⢣⢜⣻⣎⣿⢀⢿⣄⣀⠀⠁⠀⠀⠀⠀⠀⡄⠀⠀⣀⣠⣤⡶⣿⡏⢄⣷⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢹⣯⢻⣯⣷⣬⣃⢾⡣⢿⣞⣧⢚⣿⠛⠻⠿⢶⣶⣶⣶⣶⣾⢿⣛⠻⣭⣓⣶⣿⡇⢎⣿⣿⣿⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠘⢻⣿⣬⣿⣿⣿⣿⣾⡿⣯⢿⣏⣿⡌⠱⢌⠆⡆⣌⣩⠳⠙⢷⣾⣿⣻⢿⣿⣾⣙⢾⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⡨⢒⣹⣿⣿⣿⣿⡿⢃⣽⣿⡿⣿⣞⣷⠯⠶⡼⣴⣤⣤⣤⣤⠾⣿⣿⣿⡿⣯⣿⣼⣿⣿⡾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣀⡀⢠⡾⢿⣯⣿⣿⣧⣸⣿⣯⣿⠁⠀⠉⠉⠀⢀⣀⣀⣀⣠⣀⠀⠀⠙⢿⣶⣟⣿⣿⣾⣶⣟⣁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """
    )

    views = ViewBotter(tiktok_url=input("[TikTok] :+~-> "), count=1)
    views.create_session(proxy="")
    views.get_cookies()
    views.request_captcha()
    code = input(f"[TikTok] :+~->")
    views.post_captcha(code=code)
    views.send_verify()
    views.send_views()
