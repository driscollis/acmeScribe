# file_panel.py

import os
import re
import time
import wx

from pubsub import pub


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