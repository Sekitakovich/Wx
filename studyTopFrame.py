import wx
import study
from datetime import datetime as dt
from loguru import logger


class studyTopFrame(study.TopFrame):
    def __init__(self, parent):
        study.TopFrame.__init__(self, parent)

    def click(self, event: wx.Event):
        logger.debug(event.EventObject)

    def onCalendar(self, event: wx.Event):
        date: dt = event.EventObject.Date
        logger.debug(date)

    def onSlider(self, event: wx.Event):
        percent: int = event.EventObject.Value
        logger.debug(percent)
