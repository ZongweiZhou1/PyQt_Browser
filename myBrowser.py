# --*-- coding:utf-8 --*--
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
import sys, os, datetime


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()
        self.setWindowTitle('personal Browser')
        self.setWindowIcon(QIcon('icons/icons/penguin.png'))
        self.setMinimumSize(QSize(800, 640))
        self.showMaximized()
        self.show()

        # 添加地址栏
        self.urlbar = QLineEdit()
        # 地址栏响应回车事件
        self.urlbar.returnPressed.connect(self.navigate_to_url)

        # 添加标签栏
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.add_new_tab(QUrl('http://baidu.com'), 'baidu')
        self.setCentralWidget(self.tabs)

        new_tab_action = QAction(QIcon('icons/icons/add_page.png'), 'New Page', self)
        new_tab_action.triggered.connect(self.add_new_tab)

        # 添加导航栏
        navigation_bar = QToolBar('Navigation')
        navigation_bar.setIconSize(QSize(16, 16))
        self.addToolBar(navigation_bar)

        # 添加前进， 后退， 停止和刷新按钮事件
        back_button = QAction(QIcon('icons/icons/back.png'), 'Back', self)
        next_button = QAction(QIcon('icons/icons/next.png'), 'Forward', self)
        stop_button = QAction(QIcon('icons/icons/cross.png'), 'Stop', self)
        fresh_button = QAction(QIcon('icons/icons/renew.png'), 'reload', self)
        # 给每一个事件绑定响应函数
        back_button.triggered.connect(self.tabs.currentWidget().back)
        next_button.triggered.connect(self.tabs.currentWidget().forward)
        stop_button.triggered.connect(self.tabs.currentWidget().stop)
        fresh_button.triggered.connect(self.tabs.currentWidget().reload)
        # 导航栏添加事件
        navigation_bar.addAction(back_button)
        navigation_bar.addAction(next_button)
        navigation_bar.addAction(stop_button)
        navigation_bar.addAction(fresh_button)

        navigation_bar.addSeparator()
        navigation_bar.addWidget(self.urlbar)

        bookmark_button =QAction(QIcon('icons/icons/penguin.png'), 'bookmark', self)
        bookmark_button.triggered.connect(self.bookmarks_list)
        navigation_bar.addSeparator()
        navigation_bar.addAction(bookmark_button)

    def bookmarks_list(self):
        pass

    def renew_urlbar(self, t, browser=None):
        # 将当前网页连接更新到地址栏
        if browser != self.tabs.currentWidget():
            return
        self.urlbar.setText(t.toString())
        self.urlbar.setCursorPosition(0)


    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == '':
            q.setScheme('http')
        self.tabs.currentWidget().setUrl(q)


    def add_new_tab(self, qurl=QUrl(''), label='Blank'):
        browser = WebEngineView(self)
        browser.setUrl(qurl)
        self.create_new_tab(browser, label)

    def create_new_tab(self, browser, label='Blank'):
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda qurl, browser=browser: self.renew_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()[:20]))

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.renew_urlbar(qurl, self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)
        else:
            self.close()

# each tab contains a webview
class WebEngineView(QWebEngineView):
    def __init__(self, mainwindow, parent=None):
        super(WebEngineView, self).__init__(parent)
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.page().windowCloseRequested.connect(self.on_windowCloseRequested)
        self.page().profile().downloadRequested.connect(self.on_downloadRequested)
        self.mainwindow = mainwindow

    def on_windowCloseRequested(self):
        the_index = self.mainwindow.tabs.currentIndex()
        self.mainwindow.tabs.removeTab(the_index)

    def on_downloadRequested(self, downloadItem):
        if  downloadItem.isFinished()==False and downloadItem.state()==0:
            ###生成文件存储地址
            the_filename = downloadItem.url().fileName()
            if len(the_filename) == 0 or "." not in the_filename:
                cur_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                the_filename = "下载文件" + cur_time + ".xls"
            the_sourceFile = os.path.join(os.getcwd(), the_filename)

            ###下载文件
            # downloadItem.setSavePageFormat(QWebEngineDownloadItem.CompleteHtmlSaveFormat)
            downloadItem.setPath(the_sourceFile)
            downloadItem.accept()
            downloadItem.finished.connect(self.on_downloadfinished)

    def on_downloadfinished(self):
        js_string = '''
                alert("下载成功，请到软件同目录下，查找下载文件！");
                '''
        self.page().runJavaScript(js_string)

        # 重写createwindow()
    def createWindow(self, QWebEnginePage_WebWindowType):
        new_webview = WebEngineView(self.mainwindow)
        self.mainwindow.create_new_tab(new_webview)
        return new_webview

if __name__=='__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())