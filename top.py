import wx
from sono1top import sono1top

if __name__ == '__main__':
    app = wx.App(False)
    frame = sono1top(None)
    frame.Show(True)
    app.MainLoop()