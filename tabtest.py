import wx
from tabTesttopFrame import tabTesttopFrame

if __name__ == '__main__':
    app = wx.App()
    frame = tabTesttopFrame(parent=None)
    frame.Show(True)
    app.MainLoop()