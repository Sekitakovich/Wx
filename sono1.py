# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class Top
###########################################################################

class Top ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Top!", pos = wx.DefaultPosition, size = wx.Size( 1024,768 ), style = wx.CAPTION|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		self.SetFont( wx.Font( 16, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "メイリオ" ) )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHTTEXT ) )
		self.SetToolTip( u"How?" )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.bbb = wx.Button( self, wx.ID_ANY, u"Touch me", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.bbb.SetLabelMarkup( u"Touch me" )
		self.bbb.SetFont( wx.Font( 16, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "メイリオ" ) )

		bSizer1.Add( self.bbb, 0, wx.ALL, 5 )

		self.mayu = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 64,64 ), wx.BU_AUTODRAW|wx.BORDER_NONE|wx.BU_BOTTOM|wx.BU_LEFT|wx.BU_RIGHT|wx.BU_TOP )

		self.mayu.SetBitmap( wx.Bitmap( u"images/640.jpg", wx.BITMAP_TYPE_ANY ) )
		bSizer1.Add( self.mayu, 0, wx.ALL, 5 )

		self.m_toggleBtn1 = wx.ToggleButton( self, wx.ID_ANY, u"とぐる", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_toggleBtn1.SetValue( True )
		self.m_toggleBtn1.SetFont( wx.Font( 16, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_BOLD, False, "メイリオ" ) )
		self.m_toggleBtn1.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNTEXT ) )
		self.m_toggleBtn1.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

		bSizer1.Add( self.m_toggleBtn1, 0, wx.ALL, 5 )

		self.m_checkBox1 = wx.CheckBox( self, wx.ID_ANY, u"Check Me!", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer1.Add( self.m_checkBox1, 0, wx.ALL, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()
		self.m_statusBar1 = self.CreateStatusBar( 1, wx.STB_SIZEGRIP, wx.ID_ANY )

		self.Centre( wx.BOTH )

		# Connect Events
		self.bbb.Bind( wx.EVT_BUTTON, self.tako )
		self.mayu.Bind( wx.EVT_BUTTON, self.talk )
		self.m_checkBox1.Bind( wx.EVT_CHECKBOX, self.speech )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def tako( self, event ):
		event.Skip()

	def talk( self, event ):
		event.Skip()

	def speech( self, event ):
		event.Skip()


