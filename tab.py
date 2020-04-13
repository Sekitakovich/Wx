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
## Class topFrame
###########################################################################

class topFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer6 = wx.BoxSizer( wx.VERTICAL )

		self.m_notebook4 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_panel5 = wx.Panel( self.m_notebook4, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer7 = wx.BoxSizer( wx.VERTICAL )

		self.m_button7 = wx.Button( self.m_panel5, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer7.Add( self.m_button7, 0, wx.ALL, 5 )


		self.m_panel5.SetSizer( bSizer7 )
		self.m_panel5.Layout()
		bSizer7.Fit( self.m_panel5 )
		self.m_notebook4.AddPage( self.m_panel5, u"A", True )
		self.m_panel6 = wx.Panel( self.m_notebook4, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer8 = wx.BoxSizer( wx.VERTICAL )

		self.m_bitmap2 = wx.StaticBitmap( self.m_panel6, wx.ID_ANY, wx.Bitmap( u"images/640.jpg", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer8.Add( self.m_bitmap2, 0, wx.ALL, 5 )


		self.m_panel6.SetSizer( bSizer8 )
		self.m_panel6.Layout()
		bSizer8.Fit( self.m_panel6 )
		self.m_notebook4.AddPage( self.m_panel6, u"B", False )
		self.m_panel7 = wx.Panel( self.m_notebook4, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer9 = wx.BoxSizer( wx.VERTICAL )

		self.m_datePicker1 = wx.adv.DatePickerCtrl( self.m_panel7, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, wx.DefaultSize, wx.adv.DP_DEFAULT )
		bSizer9.Add( self.m_datePicker1, 0, wx.ALL, 5 )


		self.m_panel7.SetSizer( bSizer9 )
		self.m_panel7.Layout()
		bSizer9.Fit( self.m_panel7 )
		self.m_notebook4.AddPage( self.m_panel7, u"C", False )

		bSizer6.Add( self.m_notebook4, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( bSizer6 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.m_notebook4.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.tab )
		self.m_button7.Bind( wx.EVT_BUTTON, self.onButton )
		self.m_datePicker1.Bind( wx.adv.EVT_DATE_CHANGED, self.onDate )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def tab( self, event ):
		event.Skip()

	def onButton( self, event ):
		event.Skip()

	def onDate( self, event ):
		event.Skip()


