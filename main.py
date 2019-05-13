import re
import wx
import wx.richtext as rt

from pubsub import pub


wildcard = "All files (*.*)|*.*"

def save_file():
    with wx.FileDialog(
                    self, message="Save file as ...",
                                defaultDir='~',
                                defaultFile='',
                                wildcard=wildcard,
                                style=wx.FD_SAVE
                                ) as dlg:
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.save(path)
            return True
    return False


class FilePanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.create_ui()
        pub.subscribe(self.get_counts, 'tab_changed')

    def create_ui(self):
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

    def get_counts(self):
        """
        Get char and word counts and update labels
        """
        value = self.text_ctrl.GetValue()
        chars = len(value)
        words = len(re.findall('\w+', value))
        pub.sendMessage('update_counts', chars=chars, words=words)


class MainPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.create_ui()
        pub.subscribe(self.update_counts, 'update_counts')

    def create_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
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
            self, label='Target: 5000 Characters / 2500 Words')
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


class MainFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, title='acmeScribe',
                         size=(800, 600))
        panel = MainPanel(self)
        self.Show()


if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = MainFrame()
    app.MainLoop()