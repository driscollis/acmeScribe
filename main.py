import wx
import wx.richtext as rt

class FilePanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.create_ui()

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
        value = self.text_ctrl.GetValue()
        print(f'Number of characters: {len(value)}')
        words = re.findall('\w+', value)
        print(f'Number of words: {len(words)}')


class MainPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.create_ui()

    def create_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        notebook = wx.Notebook(self)

        for tab in range(8):
            tab_panel = FilePanel(notebook)
            notebook.AddPage(tab_panel, f'File {tab+1}')
        main_sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(main_sizer)


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