"""Subclass of top, which is generated by wxFormBuilder."""

import wx
import sono1


# Implementing top
class sono1top(sono1.top):
    def __init__(self, parent):
        sono1.top.__init__(self, parent)

    # Handlers for top events.
    def tako(self, event):
        # TODO: Implement tako
        pass

    def talk(self, event):
        # TODO: Implement talk
        print('まゆ')

    def speech(self, event: wx.Event):
        print(event.EventObject.Value)
