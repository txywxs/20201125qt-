import json
import os
import re
import subprocess
import sys
import time
import hashlib
from pprint import pprint

import requests
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QMutex, QWaitCondition
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QHeaderView, QTableWidget, QTableWidgetItem
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker

from model import DownloadHistory


class HistoryDB(QThread):
    # 自定义一个信号
    history_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.mutex = QMutex()
        self.cond = QWaitCondition()
        # 初始化SQLAlchemy相关
        db_file_path = 'sqlite:///' + os.path.join(os.path.expanduser('~')) + '/douyin.db?check_same_thread=False'
        engine = create_engine(db_file_path, echo=True)
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()
        try:
            had_need_db_table = self.session.query(exists().where(DownloadHistory.id == 1)).scalar()
        except Exception as ret:
            self.session.execute("CREATE TABLE download_history(id INTEGER PRIMARY KEY AUTOINCREMENT, url varchar(200) not null, video_title varchar(200));")
            self.session.commit()

    def run(self):
        self.get_history_info()
        while True:
            time.sleep(1)

    def update_download_info(self, video_info_str):
        video_info = json.loads(video_info_str)
        new_history = DownloadHistory()
        new_history.url = video_info.get('url')
        new_history.video_title = video_info.get('video_title')
        self.session.add(new_history)
        self.session.commit()

    def get_history_info(self):
        """
        获取历史下载记录，发送信号给主线程
        """
        download_history = self.session.query(DownloadHistory).all()
        for history_info in download_history:
            self.history_signal.emit(json.dumps({
                "type": "init",
                "url": history_info.url,
                "percent": "100%",
                "video_title": history_info.video_title
            }))


class DownloadVideo(QThread):
    # 自定义一个信号
    signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.douyin_url = ""

    def run(self):
        # 测试是否可以下载视频
        # print("-----1----")
        # url = "http://v6-dy-x.ixigua.com/8b3f3df21f998e7c2445e96fe984074f/5f96b1b0/video/tos/cn/tos-cn-ve-15/6a278f276d7b448bab1e4e5ef6cab9b1/?a=1128&br=1452&bt=484&cr=0&cs=0&cv=1&dr=0&ds=6&er=&l=202010261820070101980601962601DBDB&lr=&mime_type=video_mp4&qs=0&rc=ajN0bmdpO29weDMzZGkzM0ApNGQ2OWVoNDs4NzNlO2RmM2dzYjZocC9jZF5fLS0vLWFzc2EuMTZjLjNiYzFiYmE2MDQ6Yw%3D%3D&vl=&vr="
        # response = requests.get(url)
        # with open("./1.mp4", "wb") as f:
        #     f.write(response.content)

        # 1. 加载抖音分享的视频URL
        # douyin_url = "https://v.douyin.com/J5gQPeY/"
        douyin_url = self.douyin_url
        if not douyin_url:
            return

        request_headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
            "Host": "v.douyin.com",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        }
        response = requests.get(douyin_url, headers=request_headers, allow_redirects=False)
        # print(response.request.headers)
        # print(response.status_code)
        # print(response.headers)

        # 2. 提取302响应头中的location地址，这个地址就是需要进一步处理的地址
        douyin_url_2 = response.headers.get("location")
        # print(douyin_url_2)

        # 3. 提取视频id
        ret = re.match(r".*/(\d+)/", douyin_url_2)
        if not ret:
            return
        douyin_video_id = ret.group(1)

        # 4. 组一个新的URL（这个URL返回的响应是json，里面包含了真正的视频地址）
        douyin_url_3 = "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=%s" % douyin_video_id

        # 5. 加载上述的URL地址
        # print("正在加载的地址：", douyin_url_3)
        r = requests.get(douyin_url_3)
        # print(r.status_code)
        # print(r.text)
        r_dict = json.loads(r.text)
        # print(type(r_dict))
        # pprint(r_dict)

        # 6. 提取json中返回的抖音视频下载地址
        douyin_url_4 = r_dict.get("item_list")[0].get("video").get("play_addr").get("url_list")[0]
        # print(douyin_url_4)

        # 7. 将URL中的playwm改为play，这样URL就意味着是 无水印的（也就是说wm的意思是watermark 水印的意思）
        douyin_url_5 = douyin_url_4.replace("playwm", "play")
        # print(douyin_url_5)

        # 8. 访问上述视频地址，获取302返回的最终地址（说真的 这次是真的视频地址了。。。。o(╥﹏╥)o）
        request_headers_2 = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
        }
        r = requests.get(douyin_url_5, headers=request_headers_2, allow_redirects=False)
        # print(r.status_code)
        douyin_url_6 = r.headers.get("location")
        # print(douyin_url_6)

        # 9. 下载视频
        request_headers_3 = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
        }
        r = requests.get(douyin_url_6, headers=request_headers_3, stream=True)
        # print(r.status_code)
        video_title = r_dict.get("item_list")[0].get("desc") + ".mp4"
        with open(os.path.join(os.path.expanduser('~')) + "/" + video_title, "wb") as f:
            video_content_len = int(r.headers.get("Content-Length", 1))
            writed_content_len = 0

            one_histroy = {
                "type": "update",
                "url": douyin_url,
                "percent": "0%",
                "video_title": video_title
            }

            last_time = time.time()

            while True:
                try:
                    video_content = r.iter_content(100)
                    for temp in video_content:
                        write_len = f.write(temp)
                        print("正在写入视频文件, 字节大小为:", write_len)
                        writed_content_len += write_len
                        percent = "%02.2f%%" % (100 * writed_content_len / video_content_len)
                        print(percent)
                        if time.time() - last_time >= 1:
                            last_time = time.time()
                            one_histroy['percent'] = percent
                            self.signal.emit(json.dumps(one_histroy))
                        if write_len < 100:
                            one_histroy['percent'] = "100%"
                            self.signal.emit(json.dumps(one_histroy))
                except requests.exceptions.StreamConsumedError:
                    # print("写入文件成功...")
                    one_histroy['percent'] = "100%"
                    self.signal.emit(json.dumps(one_histroy))
                    break


class OpenFileBtn(QPushButton):
    def __init__(self, file_name, name="打开文件"):
        super().__init__(name)
        self.clicked.connect(self.open_file)
        self.file_name = file_name

    def open_file(self):
        # print("点击了 打开文件 按钮")
        # Windows电脑打开视频方式
        # os.startfile(具体的文件路径 例如 c:/a/b/c/123.mp4)
        # Mac电脑打开视频方式
        subprocess.call(["open", os.path.join(os.path.expanduser('~')) + "/" + self.file_name])


class DownloadHistoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__init_ui()

    def __init_ui(self):
        self.table = QTableWidget(0, 3)  # 4行3列
        self.table.setHorizontalHeaderLabels(['视频名称', '下载进度', '操作'])

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)  # 第2列的宽度随内容自适应
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)  # 第3列的宽度随内容自适应
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)
class MainWidget(QWidget):
    # 自定义一个信号
    db_signal = pyqtSignal(str)

    def __init__(self):
        # 调用父类的初始化方法
        super().__init__()
        # 完成对本widget的初始化操作
        self.__init_ui()
        # 定义一些用到的属性
        self.histroy_dict = dict()

    def __init_ui(self):
        # 步骤1：调整窗口位置、大小、要显示的控件等
        self.resize(780, 400)
        self.setWindowTitle('抖音下载神器')
        # 将窗口显示到屏幕中央
        screen = QDesktopWidget().screenGeometry()  # 获取屏幕坐标系
        size = self.geometry()  # 获取窗口坐标系
        left = (screen.width() - size.width()) / 2
        top = (screen.height() - size.height()) / 2
        self.move(left, top)
        # 创建一个输入框
        self.url_input = QLineEdit()
        # 创建一个按钮
        download_btn = QPushButton("开始下载")
        # 给按钮设置信号被触发后要调用的槽函数
        download_btn.clicked.connect(self.click_handle)
        # 创建一个水平布局容器
        h_layout = QHBoxLayout()
        # 将输入框、按钮添加到水平布局容器
        h_layout.addWidget(self.url_input)
        h_layout.addWidget(download_btn)
        # 创建一个垂直布局容器
        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout)
        self.download_history = DownloadHistoryWidget()
        v_layout.addWidget(self.download_history)
        # 将水平布局容器添加到本widget
        self.setLayout(v_layout)

        # 步骤2：创建子线程，并设置信号对应的槽函数
        self.history_db_thread = HistoryDB()
        self.history_db_thread.start()
        # 当db_signal信号被触发时，调用history_db_thread中的update_download_info方法
        self.db_signal.connect(self.history_db_thread.update_download_info)
        # 当history_db_thread里的history_signal信号被触发，调用当前对象的update_table_data方法
        self.history_db_thread.history_signal.connect(self.update_table_data)

    def click_handle(self):
        # print("点击了 开始下载按钮...")

        # 获取输入框中的 分享的抖音的地址(抖音分享的地址例如： 一个人的心小，他藏都藏不住#格局#人生  https://v.douyin.com/J5gQPeY/ 复制此链接，打开抖音，直接观看视频！)
        douyin_url_text = self.url_input.text()
        if not douyin_url_text:
            return
        ret = re.search(r".*(http[^ ]+)", douyin_url_text)
        if not ret:
            return

        # 提取出要下载的抖音URL
        douyin_url = ret.group(1)

        # 将下载视频的代码封装到另外一个线程中执行，这样在下载的过程中，主线程（即显示qt界面的这个线程就不会卡）
        self.thread_download = DownloadVideo()
        # self.thread_download.douyin_url = "https://v.douyin.com/J5gQPeY/"
        self.thread_download.douyin_url = douyin_url
        self.thread_download.signal.connect(self.update_table_data)
        self.thread_download.start()

    def get_row_col(self, one_download_history):
        h = hashlib.md5()
        h.update(one_download_history['url'].encode())
        hash_val = h.hexdigest()[:6]  # 只留6位即可
        histroy_info = self.histroy_dict.get(hash_val)
        if not histroy_info:
            row = len(self.histroy_dict.keys())
            one_download_history['id'] = row
            self.histroy_dict[hash_val] = one_download_history
            return row
        else:
            return histroy_info.get("id")

    def update_table_data(self, param):
        # print("槽函数被执行...", param)
        one_download_history = json.loads(param)
        row = self.get_row_col(one_download_history)
        # print(row)

        # 获取出发信号的类型
        signal_type = one_download_history.get("type")

        table_row_num = self.download_history.table.rowCount()
        if row >= table_row_num:
            # 每次新建一行时要发送信号给数据库线程，这样就更新了一条数据
            if signal_type == "update":
                temp_info = {
                    "url": one_download_history['url'],
                    "video_title": one_download_history['video_title']
                }
                self.db_signal.emit(json.dumps(temp_info))
            self.download_history.table.setRowCount(table_row_num + 1)

        self.download_history.table.setItem(row, 0, QTableWidgetItem(one_download_history['video_title']))
        self.download_history.table.setItem(row, 1, QTableWidgetItem(one_download_history['percent']))
        self.download_history.table.setCellWidget(row, 2, OpenFileBtn(one_download_history['video_title']))


if __name__ == '__main__':
    # 每一pyqt5应用程序必须创建一个应用程序对象。sys.argv参数是一个列表，从命令行输入参数。
    app = QApplication(sys.argv)
    main_widget = MainWidget()
    main_widget.show()
    app.exec()