# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.adv

###########################################################################
## Class TopFrame
###########################################################################

class TopFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 800,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

		Top = wx.BoxSizer( wx.HORIZONTAL )

		self.MenuPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		MenuSizer = wx.BoxSizer( wx.VERTICAL )

		self.topButton = wx.Button( self.MenuPanel, wx.ID_ANY, u"click me", wx.DefaultPosition, wx.DefaultSize, 0 )
		MenuSizer.Add( self.topButton, 0, wx.ALL, 5 )

		self.calendar = wx.adv.CalendarCtrl( self.MenuPanel, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, wx.DefaultSize, wx.adv.CAL_SHOW_HOLIDAYS )
		self.calendar.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ) )

		MenuSizer.Add( self.calendar, 0, wx.ALL, 5 )

		self.m_slider1 = wx.Slider( self.MenuPanel, wx.ID_ANY, 50, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
		MenuSizer.Add( self.m_slider1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )


		self.MenuPanel.SetSizer( MenuSizer )
		self.MenuPanel.Layout()
		MenuSizer.Fit( self.MenuPanel )
		Top.Add( self.MenuPanel, 0, wx.ALL|wx.EXPAND, 5 )

		self.Stage = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.Stage.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNHIGHLIGHT ) )

		bSizer3 = wx.BoxSizer( wx.VERTICAL )

		self.m_bitmap1 = wx.StaticBitmap( self.Stage, wx.ID_ANY, wx.Bitmap( u"images/640.jpg", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_bitmap1, 1, wx.TOP|wx.RIGHT|wx.EXPAND, 5 )


		self.Stage.SetSizer( bSizer3 )
		self.Stage.Layout()
		bSizer3.Fit( self.Stage )
		Top.Add( self.Stage, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( Top )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.topButton.Bind( wx.EVT_BUTTON, self.click )
		self.calendar.Bind( wx.adv.EVT_CALENDAR_SEL_CHANGED, self.onCalendar )
		self.m_slider1.Bind( wx.EVT_SCROLL, self.onSlider )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def click( self, event ):
		event.Skip()

	def onCalendar( self, event ):
		event.Skip()

	def onSlider( self, event ):
		event.Skip()


