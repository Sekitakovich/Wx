import wx
from studyTopFrame import studyTopFrame

if __name__ == '__main__':
    app = wx.App()
    frame = studyTopFrame(parent=None)
    frame.Show(True)
    app.MainLoop()