import wx
import wx.richtext as rt

class FilePanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.create_ui()

    def create_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.text_ctrl = rt.RichTextCtrl(self, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER)
        main_sizer.Add(self.text_ctrl, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(main_sizer)

    def OnFont(self, evt):
        """
        MODIFY THIS CODE FROM DEMO
        """
        if not self.rtc.HasSelection():
            return

        r = self.rtc.GetSelectionRange()
        fontData = wx.FontData()
        fontData.EnableEffects(False)
        attr = wx.TextAttr()
        attr.SetFlags(wx.TEXT_ATTR_FONT)
        if self.rtc.GetStyle(self.rtc.GetInsertionPoint(), attr):
            fontData.SetInitialFont(attr.GetFont())

        dlg = wx.FontDialog(self, fontData)
        if dlg.ShowModal() == wx.ID_OK:
            fontData = dlg.GetFontData()
            font = fontData.GetChosenFont()
            if font:
                attr.SetFlags(wx.TEXT_ATTR_FONT)
                attr.SetFont(font)
                self.rtc.SetStyle(r, attr)
        dlg.Destroy()


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