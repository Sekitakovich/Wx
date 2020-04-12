#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade
#

import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((400, 300))
        self.SetTitle("frame")
        
        # Menu Bar
        self.frame_menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        self.frame_menubar.item1 = wxglade_tmp_menu.Append(wx.ID_ANY, "My Menu Item 1", "")
        self.Bind(wx.EVT_MENU, self.on_menu_item1, id=self.frame_menubar.item1.GetId())
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "My Menu Item 1", "without attribute name")
        self.Bind(wx.EVT_MENU, self.on_menu_item2, id=item.GetId())
        self.frame_menubar.Append(wxglade_tmp_menu, "Menu 1")
        self.SetMenuBar(self.frame_menubar)
        # Menu Bar end
        
        # Tool Bar
        self.frame_toolbar = wx.ToolBar(self, -1)
        tool = self.frame_toolbar.AddTool(wx.ID_ANY, "My Tool", wx.Bitmap("D:\\Python\\wxglade\\wxglade_dev_master\\icons\\button.xpm", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, "", "")
        self.Bind(wx.EVT_TOOL, self.on_my_tool, id=tool.GetId())
        self.frame_toolbar.Realize()
        self.SetToolBar(self.frame_toolbar)
        # Tool Bar end
        
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        
        sizer_1.Add((0, 0), 0, 0, 0)
        
        self.SetSizer(sizer_1)
        
        self.Layout()

        # end wxGlade

    def on_menu_item1(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'on_menu_item1' not implemented!")
        event.Skip()

    def on_menu_item2(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'on_menu_item2' not implemented!")
        event.Skip()

    def on_my_tool(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'on_my_tool' not implemented!")
        event.Skip()

# end of class MyFrame

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
