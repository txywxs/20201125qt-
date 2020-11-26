import json

import jsonpath
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import qtawesome
from PyQt5.QtCore import pyqtSignal, QThread
import time
import requests
from PyQt5.QtWidgets import QTableWidgetItem


# class HistoryDB(QThread):
#     # 自定义一个信号
#     history_signal = pyqtSignal(str)
#
#     def __init__(self):
#         super().__init__()
#
#     def run(self):
#         print(1)
#
#     def update_download_info(self, video_info_str):
#         print(video_info_str)


class DownloadVideo(QThread):
    # 自定义一个信号
    signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.douyin_url = ''
        print(self.douyin_url)
    def run(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/84.0.4147.125 Safari/537.36',
            'cookie': "pgv_pvi=7982127104; ts_uid=9040743628; pgv_pvid=970052564; RK=6zikp2RyGT; "
                      "ptcz=b9714eb2392f801721e1c022b9db033c3173f0b436f1c508c304a2a5ff6b170e; tmeLoginType=2; "
                      "psrf_qqunionid=; tvfe_boss_uuid=65680c3022cf3c18; iip=0; ts_refer=ADTAGh5_playsong; "
                      "ptui_loginuin=2938979738; psrf_qqopenid=2247151C8813534EB6D1976C1BBE51E3; "
                      "euin=owEiNeElNKSiNn**; uin=2938979738; psrf_access_token_expiresAt=1613026944; "
                      "psrf_qqaccess_token=E60A1B623F4A9BDD5566D84ED2D32E81; "
                      "psrf_qqrefresh_token=D25A186390E730B4546296B18DF4B2D0; o_cookie=2938979738; "
                      "pac_uid=1_938979738; yqq_stat=0; pgv_info=ssid=s7993754560; pgv_si=s322131968; userAction=1; "
                      "player_exist=1; qqmusic_fromtag=66; yq_index=0; yplayer_open=1; ts_last=y.qq.com/ "
        }
        url = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp?ct=24&qqmusic_ver=1298&new_json=1&remoteplace=txt.yqq.song&searchid=63126059282582387&t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p=1&n=10&w={}&g_tk_new_20200303=408479224&g_tk=408479224&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0".format(self.douyin_url)
        if self.douyin_url == '//':
            raise StopIteration
        responses = requests.get(url=url, headers=headers)
        res1 = jsonpath.jsonpath(json.loads(responses.text), '$..song.list')[0]
        count = 1
        dicts = []
        print('选择你要下载的歌曲')
        for i in res1:
            name = ''
            for c in i.get("singer"):
                name += c.get('name') + ' '
            dicts.append({'歌名': i.get("name"), '歌手': name, 'mid': i.get("mid")})
            print(count, i.get("name") + '  ', '  ' + name)
            print()
            count += 1
        ints = input('输入序号(请输数字，并没有进行处理，想怎么搞你就怎么搞反正不是数字就没用)[输入（0）结束此次下载]')
        print(ints)
        lists = []
        if ints != '0':
            for i in dicts:
                url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?data=%7B%22req%22%3A%7B%22module%22%3A%22CDN' \
                      '.SrfCdnDispatchServer%22' \
                      '%2C%22method%22%3A%22GetCdnDispatch%22%2C%22param%22%3A%7B%7D%7D%2C%22req_0%22%3A%7B%22module%22' \
                      '%3A%22vkey' \
                      '.GetVkeyServer%22%2C%22method%22%3A%22CgiGetVkey%22%2C%22param%22%3A%7B%22guid%22%3A%2200%22%2C' \
                      '%22songmid' \
                      '%22%3A%5B%22{}%22%5D%2C%22songtype%22%3A%5B0%5D%2C%22uin%22%3A%2200%22%7D%7D%7D'.format(
                    i.get("mid"))
                lists.append(url)
            urls = lists[int(ints) - 1]
            gm = dicts[int(ints) - 1].get('歌名')
            ret = requests.get(url=urls, headers=headers)
            print(urls)
            vkey = jsonpath.jsonpath(json.loads(ret.text), '$..flowurl')[0]
            count_url = 'http://isure.stream.qqmusic.qq.com/{}'.format(vkey)

            one_histroy = {
                "type": "update",
                "url": self.douyin_url,
                "video_title": gm,
                "data": dicts
            }
            # musit = requests.get(url=count_url, headers=self.headers)
            if vkey:

                pass
            else:
                print('这首歌没得播放要vip')
        else:
            return




class MainUi(QtWidgets.QMainWindow):
    db_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(1024, 600)
        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QGridLayout()
        self.main_widget.setLayout(self.main_layout)

        self.left_widget = QtWidgets.QWidget()
        self.left_widget.setObjectName('left_widget')
        self.left_layout = QtWidgets.QGridLayout()
        self.left_widget.setLayout(self.left_layout)

        self.right_widget = QtWidgets.QWidget()
        self.right_widget.setObjectName('right_widget')
        self.right_layout = QtWidgets.QGridLayout()
        self.right_widget.setLayout(self.right_layout)  # 设置右侧部件布局为网格

        self.main_layout.addWidget(self.left_widget, 0, 0, 12, 2)  # 左侧部件在第0行第0列，占12行2列
        self.main_layout.addWidget(self.right_widget, 0, 2, 12, 10)  # 右侧部件在第0行第3列，占12行10列
        self.setCentralWidget(self.main_widget)  # 设置窗口主部件

        # 关闭按钮
        self.left_close = QtWidgets.QPushButton(qtawesome.icon('fa.times', color='white'), "")
        # 定义一个空白按钮
        self.left_kb = QtWidgets.QPushButton(qtawesome.icon('fa5s.music', color='white'), "")
        # 最小化按钮
        self.left_mini = QtWidgets.QPushButton(qtawesome.icon('fa.film', color='white'), "")
        self.left_close.clicked.connect(self.close_window)  # 关联
        self.left_mini.clicked.connect(self.mini)

        self.left_label_2 = QtWidgets.QPushButton("歌曲管理")
        self.left_label_2.setObjectName('left_label')

        self.left_label_3 = QtWidgets.QPushButton("联系与帮助")
        self.left_label_3.setObjectName('left_label')

        self.left_button_5 = QtWidgets.QPushButton(qtawesome.icon('fa.download', color='white'), "下载管理")
        self.left_button_5.setObjectName('left_button')

        self.left_button_7 = QtWidgets.QPushButton(qtawesome.icon('fa.comment', color='white'), "反馈建议")
        self.left_button_7.setObjectName('left_button')

        self.left_button_8 = QtWidgets.QPushButton(qtawesome.icon('fa.star', color='white'), "关注我们")
        self.left_button_8.setObjectName('left_button')

        self.left_layout.addWidget(self.left_mini, 0, 0, 1, 1)
        self.left_layout.addWidget(self.left_close, 0, 2, 1, 1)

        self.left_layout.addWidget(self.left_kb, 0, 1, 1, 1)

        self.left_layout.addWidget(self.left_button_5, 7, 0, 1, 3)
        self.left_layout.addWidget(self.left_label_3, 9, 0, 1, 3)

        self.left_layout.addWidget(self.left_label_2, 6, 0, 1, 3)

        self.left_layout.addWidget(self.left_button_7, 10, 0, 1, 3)
        self.left_layout.addWidget(self.left_button_8, 11, 0, 1, 3)

        self.right_bar_widget = QtWidgets.QWidget()  # 右侧顶部搜索框部件
        self.right_bar_layout = QtWidgets.QGridLayout()  # 右侧顶部搜索框网格布局
        self.right_bar_widget.setLayout(self.right_bar_layout)
        # self.search_icon = QtWidgets.QLabel(chr(0xf002) + ' ' + '搜索  ')
        # self.search_icon.setFont(qtawesome.font('fa', 16))
        self.right_bar_widget_search_input = QtWidgets.QLineEdit()
        self.right_bar_widget_search_input.setPlaceholderText("输入歌手、歌曲或用户，回车进行搜索")

        # self.right_bar_layout.addWidget(self.search_icon, 0, 0, 1, 1)
        self.right_bar_layout.addWidget(self.right_bar_widget_search_input, 0, 1, 1, 10)

        # 查询
        self.right_but = QtWidgets.QPushButton()
        self.right_but.setText('查询')
        # 上   左   下    右
        self.right_bar_layout.addWidget(self.right_but, 0, 10, 1, 1)

        self.right_layout.addWidget(self.right_bar_widget, 0, 0, 1, 9)

        self.right_recommend_widget = QtWidgets.QWidget()  # 推荐封面部件
        self.right_recommend_layout = QtWidgets.QGridLayout()  # 推荐封面网格布局
        self.right_recommend_widget.setLayout(self.right_recommend_layout)
        self.right_layout.addWidget(self.right_recommend_widget, 2, 0, 2, 9)

        self.right_newsong_widget = QtWidgets.QWidget()  # 最新歌曲部件
        self.right_newsong_layout = QtWidgets.QGridLayout()  # 最新歌曲部件网格布局
        self.right_newsong_widget.setLayout(self.right_newsong_layout)

        self.right_but.clicked.connect(self.CXun)
        # self.newsong_button_1 = QtWidgets.QPushButton(
        # "Bohemian Rhapsody    Queen           Bohemian Rhapsody         05::54")
        # self.newsong_button_2 = QtWidgets.QPushButton(
        #     "Dance Monkey         Tones and I     The Kids Are Coming       03::29")
        # self.newsong_button_3 = QtWidgets.QPushButton(
        #     "Girls Like You       Maroon 5        Red Pill Blues            03::55")
        # self.newsong_button_4 = QtWidgets.QPushButton(
        #     "Cheap Thrills        Sia             Cheap Thrills             03::31")
        # self.newsong_button_5 = QtWidgets.QPushButton(
        #     "Государственный гимн СССР                                  03::29")
        # self.newsong_button_6 = QtWidgets.QPushButton("リブート                ミワ              reboot               04::02")

        # self.right_newsong_layout.addWidget(self.newsong_button_1, 0, 1, )
        self.right_playlist_widget = QtWidgets.QWidget()  # 播放歌单部件
        self.right_playlist_layout = QtWidgets.QGridLayout()  # 播放歌单网格布局
        self.right_playlist_widget.setLayout(self.right_playlist_layout)

        self.right_layout.addWidget(self.right_newsong_widget, 5, 0, 1, 5)
        self.right_layout.addWidget(self.right_playlist_widget, 5, 5, 1, 4)

        self.right_process_bar = QtWidgets.QProgressBar()  # 播放进度部件
        self.right_process_bar.setValue(49)
        self.right_process_bar.setFixedHeight(3)  # 设置进度条高度
        self.right_process_bar.setTextVisible(False)  # 不显示进度条文字

        self.right_playconsole_widget = QtWidgets.QWidget()  # 播放控制部件
        self.right_playconsole_layout = QtWidgets.QGridLayout()  # 播放控制部件网格布局层
        self.right_playconsole_widget.setLayout(self.right_playconsole_layout)

        self.console_button_1 = QtWidgets.QPushButton(qtawesome.icon('fa.backward', color='#F76677'), "")
        self.console_button_2 = QtWidgets.QPushButton(qtawesome.icon('fa.forward', color='#F76677'), "")
        self.console_button_3 = QtWidgets.QPushButton(qtawesome.icon('fa.pause', color='#F76677', font=18), "")
        self.console_button_3.setIconSize(QtCore.QSize(30, 30))

        self.right_playconsole_layout.addWidget(self.console_button_1, 0, 0)
        self.right_playconsole_layout.addWidget(self.console_button_2, 0, 2)
        self.right_playconsole_layout.addWidget(self.console_button_3, 0, 1)
        self.right_playconsole_layout.setAlignment(QtCore.Qt.AlignCenter)  # 设置布局内部件居中显示

        self.right_layout.addWidget(self.right_process_bar, 9, 0, 1, 9)
        self.right_layout.addWidget(self.right_playconsole_widget, 10, 0, 1, 9)

        self.left_close.setFixedSize(16, 16)  # 设置关闭按钮的大小
        self.left_mini.setFixedSize(16, 16)  # 设置最小化按钮大小
        self.left_kb.setFixedSize(16, 16)  # 设置最小化按钮大小
        self.right_but.setStyleSheet('''QPushButton{background:#F76677;border-radius:5px;}QPushButton:hover{
        background:pink;}''')
        self.left_close.setStyleSheet(
            '''QPushButton{background:#F76677;border-radius:5px;}QPushButton:hover{background:red;}''')
        self.left_mini.setStyleSheet(
            '''QPushButton{background:#6DDF6D;border-radius:5px;}QPushButton:hover{background:green;}''')
        self.left_kb.setStyleSheet(
            '''QPushButton{background:#6DDF6D;border-radius:5px;}QPushButton:hover{background:pink;}''')
        self.left_widget.setStyleSheet('''
            QPushButton{border:none;color:white;}
            QPushButton#left_label{
                border:none;
                border-bottom:1px solid white;
                font-size:18px;
                font-weight:700;
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            }
            QPushButton#left_button:hover{border-left:4px solid red;font-weight:700;}
            QWidget#left_widget{
            background:pink;
            border-top:1px solid white;
            border-bottom:1px solid white;
            border-left:1px solid white;
            border-top-left-radius:10px;
            border-bottom-left-radius:10px;
        }
        ''')

        self.right_bar_widget_search_input.setStyleSheet(
            '''QLineEdit{
                    border:1px solid gray;
                    width:300px;
                    border-radius:10px;
                    padding:2px 4px;
            }''')

        self.right_widget.setStyleSheet('''
            QWidget#right_widget{
                color:#232C51;
                background:white;
                border-top:1px solid darkGray;
                border-bottom:1px solid darkGray;
                border-right:1px solid darkGray;
                border-top-right-radius:10px;
                border-bottom-right-radius:10px;
            }
            QLabel#right_lable{
                border:none;
                font-size:16px;
                font-weight:700;
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            }
        ''')
        self.right_recommend_widget.setStyleSheet(
            '''
                QToolButton{border:none;}
                QToolButton:hover{border-bottom:2px solid #F76677;}
            ''')
        self.right_playlist_widget.setStyleSheet(
            '''
                QToolButton{border:none;}
                QToolButton:hover{border-bottom:2px solid #F76677;}
            ''')
        self.right_newsong_widget.setStyleSheet('''
            QPushButton{
                border:none;
                color:gray;
                font-size:12px;
                height:40px;
                padding-left:5px;
                padding-right:10px;
                text-align:left;
            }
            QPushButton:hover{
                color:black;
                border:1px solid #F3F3F5;
                border-radius:10px;
                background:LightGray;
            }
        ''')
        self.right_process_bar.setStyleSheet('''
            QProgressBar::chunk {
                background-color: #F76677;
            }
        ''')

        self.right_playconsole_widget.setStyleSheet('''
            QPushButton{
                border:none;
            }
        ''')

        self.setWindowOpacity(0.95)  # 设置窗口透明度
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # 隐藏边框

        self.main_layout.setSpacing(0)
        # self.history_db_thread = HistoryDB()
        # self.history_db_thread.start()
        # self.right_but.connect(self.history_db_thread.update_download_info)
        # # 当history_db_thread里的history_signal信号被触发，调用当前对象的update_table_data方法
        # self.history_db_thread.history_signal.connect(self.update_table_data)
    # 无边框的拖动
    def mouseMoveEvent(self, e: QtGui.QMouseEvent):  # 重写移动事件
        self._endPos = e.pos() - self._startPos
        self.move(self.pos() + self._endPos)

    def mousePressEvent(self, e: QtGui.QMouseEvent):
        if e.button() == QtCore.Qt.LeftButton:
            self._isTracking = True
            self._startPos = QtCore.QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent):
        if e.button() == QtCore.Qt.LeftButton:
            self._isTracking = False
            self._startPos = None
            self._endPos = None

    # 关闭按钮动作函数
    def close_window(self):
        self.close()

    def mini(self):
        self.showMinimized()

    def CXun(self):
        self.Download = DownloadVideo()
        # self.right_bar_widget_search_input.text()
        self.Download.douyin_url = self.right_bar_widget_search_input.text()
        self.Download.start()
        self.Download.signal.connect(self.update_table_data)
        print(1213123123,'-112312312321132')
    def update_table_data(self, param):
        print("槽函数被执行...", param)
        # one_download_history = json.loads(param)
        # row = self.get_row_col(one_download_history)
        # # print(row)
        #
        # # 获取出发信号的类型
        # signal_type = one_download_history.get("type")
        #
        # table_row_num = self.download_history.table.rowCount()
        # if row >= table_row_num:
        #     # 每次新建一行时要发送信号给数据库线程，这样就更新了一条数据
        #     if signal_type == "update":
        #         temp_info = {
        #             "url": one_download_history['url'],
        #             "video_title": one_download_history['video_title']
        #         }
        #         self.db_signal.emit(json.dumps(temp_info))
        #     self.download_history.table.setRowCount(table_row_num + 1)
        #
        # self.right_playconsole_layout.table.setItem(0, 0, QTableWidgetItem(one_download_history['video_title']))
        # self.right_playconsole_layout.table.setItem(0, 1, QTableWidgetItem(one_download_history['percent']))

def main():
    app = QtWidgets.QApplication(sys.argv)
    gui = MainUi()
    gui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
