# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class UltraLaunchCtrlDlgProto
###########################################################################

class UltraLaunchCtrlDlgProto ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"UltraLauncher", pos = wx.DefaultPosition, size = wx.Size( 404,147 ), style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer1.AddGrowableCol( 1 )
		fgSizer1.SetFlexibleDirection( wx.BOTH )
		fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_bitmap1 = wx.StaticBitmap( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_GO_FORWARD, wx.ART_CMN_DIALOG ), wx.DefaultPosition, wx.Size( 48,48 ), 0 )
		fgSizer1.Add( self.m_bitmap1, 0, wx.ALL, 5 )

		self.start_button = wx.Button( self, wx.ID_ANY, u"Запуск", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer1.Add( self.start_button, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.m_bitmap2 = wx.StaticBitmap( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_CROSS_MARK, wx.ART_CMN_DIALOG ), wx.DefaultPosition, wx.Size( 48,48 ), 0 )
		fgSizer1.Add( self.m_bitmap2, 0, wx.ALL, 5 )

		self.stop_button = wx.Button( self, wx.ID_ANY, u"Останов", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer1.Add( self.stop_button, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )


		self.SetSizer( fgSizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.onCloseWindow )
		self.start_button.Bind( wx.EVT_BUTTON, self.onStartButtonClick )
		self.stop_button.Bind( wx.EVT_BUTTON, self.onStopButtonClick )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def onCloseWindow( self, event ):
		event.Skip()

	def onStartButtonClick( self, event ):
		event.Skip()

	def onStopButtonClick( self, event ):
		event.Skip()


