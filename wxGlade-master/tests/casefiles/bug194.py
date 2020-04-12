#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade
#

import wx

# begin wxGlade: dependencies
import gettext
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class Frame194(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: Frame194.__init__
        kwds["style"] = kwds.get("style", 0)
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((800, 600))
        self.SetTitle(_("frame_1"))
        
        sizer_1 = wx.GridSizer(2, 3, 0, 0)
        
        self.list_box_single = wx.ListBox(self, wx.ID_ANY, choices=[_("Listbox wxLB_SINGLE")])
        self.list_box_single.SetSelection(0)
        sizer_1.Add(self.list_box_single, 1, wx.ALL | wx.EXPAND, 5)
        
        self.list_box_multiple = wx.ListBox(self, wx.ID_ANY, choices=[_("Listbox wxLB_MULTIPLE")], style=wx.LB_MULTIPLE)
        self.list_box_multiple.SetSelection(0)
        sizer_1.Add(self.list_box_multiple, 1, wx.ALL | wx.EXPAND, 5)
        
        self.list_box_extended = wx.ListBox(self, wx.ID_ANY, choices=[_("Listbox wxLB_EXTENDED")], style=wx.LB_EXTENDED)
        self.list_box_extended.SetSelection(0)
        sizer_1.Add(self.list_box_extended, 1, wx.ALL | wx.EXPAND, 5)
        
        self.check_list_box_single = wx.CheckListBox(self, wx.ID_ANY, choices=[_("CheckListBox wxLB_SINGLE")], style=wx.LB_SINGLE)
        self.check_list_box_single.SetSelection(0)
        sizer_1.Add(self.check_list_box_single, 1, wx.ALL | wx.EXPAND, 5)
        
        self.check_list_box_multiple = wx.CheckListBox(self, wx.ID_ANY, choices=[_("CheckListBox wxLB_MULTIPLE")], style=wx.LB_MULTIPLE)
        self.check_list_box_multiple.SetSelection(0)
        sizer_1.Add(self.check_list_box_multiple, 1, wx.ALL | wx.EXPAND, 5)
        
        self.check_list_box_extended = wx.CheckListBox(self, wx.ID_ANY, choices=[_("CheckListBox wxLB_EXTENDED")], style=wx.LB_EXTENDED)
        self.check_list_box_extended.SetSelection(0)
        sizer_1.Add(self.check_list_box_extended, 1, wx.ALL | wx.EXPAND, 5)
        
        self.SetSizer(sizer_1)
        
        self.Layout()
        # end wxGlade

# end of class Frame194

class MyApp(wx.App):
    def OnInit(self):
        self.Bug194_Frame = Frame194(None, wx.ID_ANY, "")
        self.SetTopWindow(self.Bug194_Frame)
        self.Bug194_Frame.Show()
        return True

# end of class MyApp

if __name__ == "__main__":
    gettext.install("app") # replace with the appropriate catalog name

    app = MyApp(0)
    app.MainLoop()
