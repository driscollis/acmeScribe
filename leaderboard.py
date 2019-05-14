# leaderboard.py

import wx

from wx.html import HtmlWindow


class Leaderboard(HtmlWindow):

    def __init__(self, parent):
        super().__init__(parent, wx.ID_ANY, style=wx.NO_FULL_REPAINT_ON_RESIZE)
