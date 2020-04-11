import wx
from sono1top import sono1top

if __name__ == '__main__':
    app = wx.App()
    frame = sono1top()
    frame.Show(True)
    app.MainLoop()