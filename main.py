# main.py

import os
import wx

from file_panel import FilePanel
from leaderboard import Leaderboard
from pubsub import pub
import wx.lib.agw.flatnotebook as fnb


wildcard = "Text files (*.txt)|*.txt"

def prompt_to_save():
    """
    Prompt user for save location
    """
    paths = wx.StandardPaths.Get()
    with wx.FileDialog(
                    None, message="Save file as ...",
                                defaultDir=paths.GetDocumentsDir(),
                                defaultFile='',
                                wildcard=wildcard,
                                style=wx.FD_SAVE
                                ) as dlg:
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            _, ext = os.path.splitext(path)
            if '.txt' not in ext.lower():
                path = f'{path}.txt'
            return path


class MainPanel(wx.Panel):
    """
    Class that holds the main panel's UI code / logic
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.create_ui()
        pub.subscribe(self.update_counts, 'update_counts')

    def create_ui(self):
        """
        Create UI in main panel
        """
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Add leaderboard button
        btn_sizer = wx.BoxSizer()
        bmp = wx.ArtProvider.GetBitmap(
            wx.ART_INFORMATION, wx.ART_TOOLBAR, (16,16))
        self.leaderboard_btn = wx.ToggleButton(self, size=(40, 40))
        self.leaderboard_btn.SetBitmap(bmp)
        self.leaderboard_btn.Bind(wx.EVT_TOGGLEBUTTON, self.on_leaderboard)
        btn_sizer.AddStretchSpacer(prop=2)
        btn_sizer.Add(self.leaderboard_btn, 0, wx.ALL, 5)
        self.main_sizer.Add(btn_sizer, 0, wx.EXPAND)

        # Add notebook
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.notebook = fnb.FlatNotebook(self)
        style = self.notebook.GetAGWWindowStyleFlag()
        style |= fnb.FNB_NO_X_BUTTON
        self.notebook.SetAGWWindowStyleFlag(style)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_change)

        for tab in range(8):
            tab_panel = FilePanel(self.notebook)
            self.notebook.AddPage(tab_panel, f'File {tab+1}')
        hsizer.Add(self.notebook, 2, wx.ALL | wx.EXPAND, 5)

        # Add leaderboard widget (HtmlWindow)
        self.leaderboard = Leaderboard(self)
        self.leaderboard.SetPage(
            '''
            <h2>Leaderboard</h2>
            ''')
        hsizer.Add(self.leaderboard, 1, wx.ALL | wx.EXPAND, 5)
        self.leaderboard.Hide()
        self.main_sizer.Add(hsizer, 1, wx.ALL | wx.EXPAND)

        # Add counters
        self.current_count = wx.StaticText(
            self, label='Current: Characters: 0 / Words: 0')
        self.main_sizer.Add(self.current_count, 0, wx.TOP | wx.LEFT, 5)
        self.remaining = wx.StaticText(
            self, label='Remaining: Characters: 5000 / Words 2500')
        self.main_sizer.Add(self.remaining, 0, wx.LEFT, 5)
        target = wx.StaticText(
            self, label='(Target: 5000 Characters / 2500 Words)')
        self.main_sizer.Add(target, 0, wx.LEFT|wx.BOTTOM, 5)

        self.SetSizer(self.main_sizer)
        self.main_sizer.Layout()

    def update_counts(self, chars, words):
        """
        PubSub Subscriber for updating the char / word counts
        """
        curr_lbl = f'Current: Characters: {chars} / Words: {words}'
        self.current_count.SetLabel(curr_lbl)

        if chars > 5000:
            remain_lbl = f'Remaining: Characters: 0 / Words: 0'
        else:
            chars = 5000 - chars
            words = 2500 - words
            remain_lbl = f'Remaining: Characters: {chars} / Words: {words}'
        self.remaining.SetLabel(remain_lbl)

    def on_leaderboard(self, event):
        """
        Toggle visibility of leaderboard
        """
        if self.leaderboard_btn.GetValue():
            self.leaderboard.Show()
        else:
            self.leaderboard.Hide()
        self.main_sizer.Layout()

    def on_tab_change(self, event):
        """
        Event handler for changing tabs in the notebook
        """
        current_page = self.notebook.GetCurrentPage()
        if current_page:
            current_page.get_counts()

    def save_all_pages(self):
        """
        Loop through all pages in notebook and prompt to save if
        they are currently saved to a temp location
        """
        pages = self.notebook.GetPageCount()
        for page in range(pages):
            self.notebook.SetSelection(page)
            current_page = self.notebook.GetCurrentPage()
            data = current_page.text_ctrl.GetValue()
            if current_page.tmp_location and data:
                # prompt to save
                current_page.save_location = prompt_to_save()
                current_page.save()


class MainFrame(wx.Frame):
    """
    The class that holds the top level widget
    """

    def __init__(self):
        super().__init__(None, title='acmeScribe',
                         size=(800, 600))
        self.panel = MainPanel(self)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Show()

    def on_close(self, event):
        """
        Event handler that runs when the application is closing
        """
        self.panel.save_all_pages()
        self.Destroy()


if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = MainFrame()
    app.MainLoop()