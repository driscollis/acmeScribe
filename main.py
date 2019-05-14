# main.py

import os
import re
import time
import wx

from pubsub import pub


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


class FilePanel(wx.Panel):
    """
    Class that contains UI for the Notebook page / tab
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.create_ui()
        pub.subscribe(self.get_counts, 'tab_changed')
        self.save_location = None
        self.tmp_location = True

    def create_ui(self):
        """
        Create the UI for the notebook page
        """
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.text_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.text_ctrl.Bind(wx.EVT_TEXT, self.on_text)
        main_sizer.Add(self.text_ctrl, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(main_sizer)

    def on_text(self, event):
        """
        Event handler that is fired when the user edits the
        text control
        """
        self.get_counts()
        self.save()

    def get_counts(self):
        """
        Get char and word counts and update labels
        """
        value = self.text_ctrl.GetValue()
        chars = len(value)
        words = len(re.findall('\w+', value))
        pub.sendMessage('update_counts', chars=chars, words=words)

    def save(self):
        """
        Save the file
        """
        if self.save_location is None:
            paths = wx.StandardPaths.Get()
            tmp = paths.GetTempDir()
            now = int(time.time())
            self.save_location = os.path.join(tmp, f'{now}.txt')
        data = self.text_ctrl.GetValue()
        if data:
            try:
                with open(self.save_location, 'w') as f:
                    f.write(data)
            except:
                # TODO - replace with message dialog
                print('Unable to save')


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
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Add leaderboard button
        btn_sizer = wx.BoxSizer()
        bmp = wx.ArtProvider.GetBitmap(
            wx.ART_INFORMATION, wx.ART_TOOLBAR, (16,16))
        leaderboard = wx.BitmapButton(self, bitmap=bmp, size=(40, 40))
        btn_sizer.AddStretchSpacer(prop=2)
        btn_sizer.Add(leaderboard, 0, wx.ALL, 5)
        main_sizer.Add(btn_sizer, 0, wx.EXPAND)

        # Add notebook
        self.notebook = wx.Notebook(self)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_change)

        for tab in range(8):
            tab_panel = FilePanel(self.notebook)
            self.notebook.AddPage(tab_panel, f'File {tab+1}')
        main_sizer.Add(self.notebook, 1, wx.ALL | wx.EXPAND, 5)

        self.current_count = wx.StaticText(
            self, label='Current: Characters: 0 / Words: 0')
        main_sizer.Add(self.current_count, 0, wx.TOP | wx.LEFT, 5)
        self.remaining = wx.StaticText(
            self, label='Remaining: Characters: 5000 / Words 2500')
        main_sizer.Add(self.remaining, 0, wx.LEFT, 5)
        target = wx.StaticText(
            self, label='(Target: 5000 Characters / 2500 Words)')
        main_sizer.Add(target, 0, wx.LEFT|wx.BOTTOM, 5)

        self.SetSizer(main_sizer)

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