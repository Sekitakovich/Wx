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
## Class top
###########################################################################

class top ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Top!", pos = wx.DefaultPosition, size = wx.Size( 800,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.bbb = wx.Button( self, wx.ID_ANY, u"Touch me", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer1.Add( self.bbb, 0, wx.ALL, 5 )

		self.mayu = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.BORDER_NONE|wx.BU_BOTTOM|wx.BU_LEFT|wx.BU_RIGHT|wx.BU_TOP )

		self.mayu.SetBitmap( wx.Bitmap( u"640.jpg", wx.BITMAP_TYPE_ANY ) )
		bSizer1.Add( self.mayu, 0, wx.ALL, 5 )

		self.m_toggleBtn1 = wx.ToggleButton( self, wx.ID_ANY, u"Toggle me!", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_toggleBtn1.SetValue( True )
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


