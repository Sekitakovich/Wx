from loguru import logger
import wx
import sono1


class sono1top(sono1.Top):

    def __init__(self, parent=None):
        sono1.Top.__init__(self, parent)

    # Handlers for top events.
    def tako(self, event):
        logger.debug('OK')
        pass

    def talk(self, event):
        # TODO: Implement talk
        logger.debug('あふん♪')

    def speech(self, event: wx.Event):
        logger.debug(event.EventObject.Value)
