# -*- coding: UTF-8 -*-
#
# generated by wxGlade
#

import wx
# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class PythonSubclass(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: PythonSubclass.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetTitle(_("frame"))
        
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        
        label_1 = wx.StaticText(self, wx.ID_ANY, _("Hello World !"))
        sizer_1.Add(label_1, 0, wx.ALL, 5)
        
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        
        self.Layout()
        # end wxGlade

# end of class PythonSubclass
