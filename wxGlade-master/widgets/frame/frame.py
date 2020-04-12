"""\
wxFrame objects (incl. wxMenuBar, wxToolBar and wxStatusBar)

@copyright: 2002-2007 Alberto Griggio
@copyright: 2014-2016 Carsten Grohmann
@copyright: 2016-2020 Dietmar Schwertberger
@license: MIT (see LICENSE.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import wx
import os
import common, config, misc, compat
import new_properties as np
from edit_windows import WindowBase, TopLevelBase, EditStylesMixin, Slot
from gui_mixins import BitmapMixin


class EditFrame(BitmapMixin, TopLevelBase, EditStylesMixin):
    WX_CLASS = "wxFrame"
    _PROPERTIES =["Widget", "title", "icon", "centered", "sizehints","menubar", "toolbar", "statusbar", "style"]
    PROPERTIES = TopLevelBase.PROPERTIES + _PROPERTIES + TopLevelBase.EXTRA_PROPERTIES
    _PROPERTY_HELP   = { 'icon':'Icon for this window.',
                         "size":WindowBase._PROPERTY_HELP["size_sizehints"] }
    _PROPERTY_LABELS = { "sizehints":'Set Size Hints', "menubar":'Has MenuBar', "toolbar":'Has ToolBar',
                         "statusbar":'Has StatusBar' }
    ATT_CHILDREN = ["_menubar", "_statusbar", "_toolbar"]

    def __init__(self, name, parent, title, style=wx.DEFAULT_FRAME_STYLE, klass='wxFrame'): #XXX style is not used
        TopLevelBase.__init__(self, name, klass, parent, title=title)
        EditStylesMixin.__init__(self)
        self.properties["style"].set(style)

        # initialise instance properties
        self.icon      = np.BitmapPropertyD("")
        self.centered  = np.CheckBoxProperty(False, default_value=False)
        self.sizehints = np.CheckBoxProperty(False, default_value=False)
        self.menubar   = np.CheckBoxProperty(False, default_value=False)
        self.toolbar   = np.CheckBoxProperty(False, default_value=False)
        if "statusbar" in self.PROPERTIES:
            self.statusbar = np.CheckBoxProperty(False, default_value=False)
            self._statusbar = None
        else:
            self.statusbar = None
        self._menubar = self._toolbar = None  # these properties will hold the EditMenubar instances etc.

    def create_widget(self):
        if self.parent:
            parent = self.parent.widget
        else:
            #parent = common.palette
            parent = None
        style = self.style
        if common.pin_design_window: style |= wx.STAY_ON_TOP
        self.widget = wx.Frame(parent, self.id, self.title, style=style)
        self._set_widget_icon()

    def finish_widget_creation(self):
        # add menu, status and tool bar
        TopLevelBase.finish_widget_creation(self)
        if not self.properties['size'].is_active():
            self.widget.SetSize((400, 300))
        if wx.Platform == '__WXMSW__':
            self.widget.CenterOnScreen()
        if self.menubar and self._menubar.widget:
            self.widget.SetMenuBar(self._menubar.widget)
        if self.statusbar and self._statusbar.widget:
            self.widget.SetStatusBar(self._statusbar.widget)
        if self.toolbar and self._toolbar.widget:
            self.widget.SetToolBar(self._toolbar.widget)

    def remove(self, *args):
        # remove menu, status and tool bar
        if self.menubar:
            self._menubar = self._menubar.remove(gtk_do_nothing=True)
        if self.statusbar:
            self._statusbar = self._statusbar.remove(do_nothing=True)
        if self.toolbar:
            self._toolbar = self._toolbar.remove(do_nothing=True)
        TopLevelBase.remove(self, *args)

    def _set_widget_icon(self):
        if self.icon:
            bitmap = self.get_preview_obj_bitmap(self.icon.strip())
        else:
            xpm = os.path.join(config.icons_path, 'frame.xpm')
            bitmap = misc.get_xpm_bitmap(xpm)

        icon = compat.wx_EmptyIcon()
        icon.CopyFromBitmap(bitmap)
        self.widget.SetIcon(icon)

    def _set_menu_bar(self):
        if self.menubar:
            # create a MenuBar
            from menubar import EditMenuBar
            self._menubar = EditMenuBar(self.name + '_menubar', 'wxMenuBar', self)
            if self.widget: self._menubar.create()
        else:
            # remove
            if self._menubar is None: return
            self._menubar = self._menubar.remove()

    def _set_status_bar(self):
        if self.statusbar:
            # create a StatusBar
            from statusbar import EditStatusBar
            self._statusbar = EditStatusBar(self.name + '_statusbar', 'wxStatusBar', self)
            if self.widget: self._statusbar.create()
        else:
            # remove
            if self._statusbar is None: return
            self._statusbar = self._statusbar.remove()
        if self.widget:
            # this is needed at least on win32
            wx.PostEvent( self.widget, wx.SizeEvent(self.widget.GetSize(), self.widget.GetId()) )

    def _set_tool_bar(self):
        if self.toolbar:
            # create a ToolBar
            from toolbar import EditToolBar
            EditToolBar(self.name + '_toolbar', 'wxToolBar', self)
            if self.widget: self._toolbar.create()
        else:
            # remove
            if self._toolbar is None: return
            self._toolbar = self._toolbar.remove()

    def properties_changed(self, modified):
        if not modified or "icon" in modified and self.widget: self._set_widget_icon()

        if not modified or "menubar" in modified:   self._set_menu_bar()
        if not modified or "statusbar" in modified: self._set_status_bar()
        if not modified or "toolbar" in modified:   self._set_tool_bar()

        if modified:
            intersection = {"menubar","statusbar","toolbar"}.intersection(modified)
            if intersection and self.properties[intersection.pop()].previous_value is not None:
                # previous value is not None -> triggered by user
                misc.rebuild_tree(widget=self, recursive=False, focus=False)

        TopLevelBase.properties_changed(self, modified)
        EditStylesMixin.properties_changed(self, modified)



class EditMDIChildFrame(EditFrame):
    WX_CLASS = "wxMDIChildFrame"
    IS_TOPLEVEL_WINDOW = False  # avoid to appear in the "Top Window" property of the app
    PROPERTIES = [p for p in EditFrame.PROPERTIES if p!="statusbar"]
    ATT_CHILDREN = ["_menubar", "_toolbar"]


# options for WindowDialog when interactively adding a Frame
options = ["Add panel and sizer"]
last_choices = [True]

if config.debugging:
    # for testing the error handling
    options.append("Provoke an error")
    last_choices.append(False)


def builder(parent, pos, klass=None, base=None, name=None):
    "factory function for EditFrame objects"
    global last_choices
    if klass is None or base is None:
        import window_dialog
        base_classes = ['wxFrame', 'wxMDIChildFrame']
        klass = 'wxFrame' if common.root.language.lower()=='xrc' else 'MyFrame'
        
        dialog = window_dialog.WindowDialog(klass, base_classes, 'Select frame class', True, options, last_choices)
        res = dialog.show()
        dialog.Destroy()
        if res is None: return None
        klass, base = res
        last_choices[:] = dialog.get_options()  # remember for next time
        if config.debugging and last_choices[1]: XXX  # provoke an error
        name = dialog.get_next_name("frame")
        interactive = True
    else:
        interactive = False  # last_choices not to be obeyed

    if base == "wxFrame":
        base_class = EditFrame
    else:
        base_class = EditMDIChildFrame
    editor = base_class(name, parent, name, "wxDEFAULT_FRAME_STYLE", klass=klass)
    editor.properties['size'].set( (400,300), activate=True )
    editor.create()
    editor.widget.Show()
    editor.design.update_label()

    if interactive and last_choices[0]:
        # add a default panel and vertical sizer to the frame
        import edit_sizers, widgets.panel.panel
        panel_editor = widgets.panel.panel.builder(editor, 0)
        edit_sizers._builder(panel_editor, 0)
    else:
        # just add a slot
        Slot(editor, 0)

    import clipboard
    editor.drop_target = clipboard.DropTarget(editor)
    editor.widget.SetDropTarget(editor.drop_target)

    if wx.Platform == '__WXMSW__':
        #editor.widget.CenterOnScreen()
        editor.widget.Raise()

    return editor


def _make_builder(base_class):
    def xml_builder(attrs, parent, pos=None):
        from xml_parse import XmlParsingError
        try:
            label = attrs['name']
        except KeyError:
            raise XmlParsingError(_("'name' attribute missing"))
        if attrs.input_file_version and attrs.input_file_version<(0,8):
            # backwards compatibility
            style = "wxDEFAULT_FRAME_STYLE"
        else:
            style = 0
        editor = base_class(label, parent, "", style)
        return editor
    return xml_builder


def initialize():
    "initialization function for the module: returns a wx.BitmapButton to be added to the main palette"
    common.widget_classes['EditFrame'] = EditFrame
    common.widgets['EditFrame'] = builder
    common.widgets_from_xml['EditFrame'] = _make_builder(EditFrame)

    common.widget_classes['EditMDIChildFrame'] = EditMDIChildFrame
    common.widgets_from_xml['EditMDIChildFrame'] = _make_builder(EditMDIChildFrame)

    from tree import WidgetTree
    import os.path
    WidgetTree.images['EditMDIChildFrame'] = os.path.join( config.icons_path, 'frame.xpm' )
    return common.make_object_button('EditFrame', 'frame.xpm', 1)
