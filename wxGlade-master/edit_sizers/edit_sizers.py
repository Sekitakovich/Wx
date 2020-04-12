"""
Hierarchy of Sizers supported by wxGlade

@copyright: 2002-2007 Alberto Griggio
@copyright: 2014-2016 Carsten Grohmann
@copyright: 2016-2020 Dietmar Schwertberger
@license: MIT (see LICENSE.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import wx
from wx.lib.buttons import GenButton

import new_properties as np
import clipboard
import common, compat, config, misc
import edit_base

HAVE_WRAP_SIZER = hasattr(wx, "WrapSizer")  # only for 3.0

def _frozen(method):
    "freeze toplevel parent during update"
    def _frozen(sizer, *args):
        if sizer.window.widget:
            toplevel = sizer.window.widget.GetTopLevelParent()
            toplevel.Freeze()
        else:
            toplevel = None
        try:
            return method(sizer, *args)
        finally:
            if toplevel:
                toplevel.Refresh()
                toplevel.Thaw()
    return _frozen


class SizerSlot(edit_base.Slot):
    "A window to represent a slot in a sizer"
    WX_CLASS ="sizerslot"
    def __init__(self, parent, pos=0, label=None):
        edit_base.Slot.__init__(self, parent, pos, label)
        self.klass = self.classname = self.base = "sizerslot"

    def set_overlap(self, overlapped=True, add_to_sizer=True):
        # interface from GridBagSizer; so self.parent is a sizer
        if overlapped==self.overlapped: return
        self.overlapped = overlapped
        sizer = self.parent
        if overlapped:
            if self.widget:
                if add_to_sizer:
                    sizer.widget.Detach(self.widget)
                compat.DestroyLater(self.widget)
                self.widget = None
        else:
            if sizer.widget and not self.widget:
                self.create_widget()
                if add_to_sizer:
                    sizer.widget.Add(self.widget, self.pos, self.span, wx.EXPAND, self.border)
        # XXX update icon in Tree

    def check_drop_compatibility(self):
        return (True,None)

    # clipboard handling ###############################################################################################
    def check_compatibility(self, widget, typename=None):
        "check whether widget can be pasted here"
        if typename is not None:
            #if typename=="sizer" and self.sizer.is_virtual():
                #return (False, "No sizer can be pasted here")
            if typename=="window":
                return (False, "No toplevel object can be pasted here.")
            return (True,None)

        if widget.IS_TOPLEVEL:
            return (False, "No toplevel object can be pasted here.")
        #if self.sizer.is_virtual() and isinstance(widget, Sizer):
            ## e.g. a sizer dropped on a splitter window slot; instead, a panel would be required
            #return (False, "No sizer can be pasted here")
        return (True,None)

    def write(self, output, tabs):
        output.extend( common.format_xml_tag( u'object', '', tabs, **{'class': 'sizerslot'}) )

    def _get_tooltip(self):
        return "Add a widget or another sizer here."


class SizerHandleButton(GenButton):
    'Provides a "handle" to activate a Sizer and to access its popup menu'
    def __init__(self, parent, id, sizer):
        GenButton.__init__(self, parent.widget, id, '', size=(5, 5))
        self.sizer = sizer
        self.SetUseFocusIndicator(False)
        self.Bind(wx.EVT_RIGHT_DOWN, self.sizer.popup_menu )
        #self.Bind(wx.EVT_KEY_DOWN, misc.on_key_down_event)
        color = compat.wx_SystemSettings_GetColour(wx.SYS_COLOUR_BTNFACE)
        self.SetBackgroundColour(color)

class BaseSizerBuilder(object):
    "Language independent base class for all sizer builders / code generators"

    tmpl = []                 # Statements to generate the sizer from, the stmt has to end with a newline character

    klass = ''                # klass: Sizer class name
    language = None           # Language to generate the code for

    tmpl_SetSizer = ''        # Template to call SetSizer()
    tmpl_Fit = ''             # Template to call Fit()
    tmpl_Realize = ''         # Template to call Realize() for StdDialogButtonSizer
    tmpl_SetSizeHints = ''    # Template to set the size hints
    tmpl_AddGrowableRow = ''  # Template for wxFlexGridSizer to set growable rows
    tmpl_AddGrowableCol = ''  # Template for wxFlexGridSizer to set growable columns

    def __init__(self):
        "Initialise sizer builder"
        self.tmpl_dict = {}                               # properties to replace in tmpl
        self.codegen = common.code_writers[self.language] #language specific code generator (codegen.BaseLangCodeWriter)

    def _get_wparent(self, topl, obj):
        "Return the parent widget or a reference to it as string"
        raise NotImplementedError

    def _prepare_tmpl_content(self, obj):
        """Prepare template variables"""
        self.tmpl_dict.clear()
        self.tmpl_dict['klass'] = self.codegen.cn(self.klass)
        self.tmpl_dict['wxIDANY'] = self.codegen.cn('wxID_ANY')
        #self.tmpl_dict['parent_widget'] = self._get_wparent(obj)
        self.tmpl_dict['parent_widget'] = self._get_wparent(obj)
        self.tmpl_dict['sizer_name'] = self.codegen._format_classattr(obj)

    def _get_code(self, obj):
        "Generates the language specific code for sizer specified in klass"
        if not self.tmpl:
            return [], []  # init, final

        init = []
        layout = []

        # generate init lines from tmpl filled with tmpl_dict
        init.append(self.tmpl % self.tmpl_dict)

        # generate layout lines
        if not obj.parent.IS_SIZER:
            layout.append(self.tmpl_SetSizer % self.tmpl_dict)
            if not obj.parent.check_prop("size") and obj.parent.IS_TOPLEVEL:
                layout.append(self.tmpl_Fit % self.tmpl_dict)
            if "sizehints" in obj.window.properties and obj.window.sizehints:
                layout.append(self.tmpl_SetSizeHints % self.tmpl_dict)

        return init, layout  # init, post

    def get_code(self, obj):
        "Generates the language specific code for sizer specified in klass"
        self._prepare_tmpl_content(obj)
        if self.klass == 'wxBoxSizer':             return self.get_code_wxBoxSizer(obj)
        if self.klass == 'wxWrapSizer':            return self.get_code_wxBoxSizer(obj)  # the same here
        if self.klass == 'wxStaticBoxSizer':       return self.get_code_wxStaticBoxSizer(obj)
        if self.klass == 'wxStdDialogButtonSizer': return self.get_code_wxStdDialogButtonSizer(obj)
        if self.klass == 'wxGridSizer':            return self.get_code_wxGridSizer(obj)
        if self.klass == 'wxFlexGridSizer':        return self.get_code_wxFlexGridSizer(obj)
        if self.klass == 'wxGridBagSizer':         return self.get_code_wxFlexGridSizer(obj)
        return self._get_code(obj)

    def get_code_wxStaticBoxSizer(self, obj):
        "Set sizer specific properties and generate the code"
        self.tmpl_dict['orient'] = self.codegen.cn( obj.properties["orient"].get_string_value() )
        self.tmpl_dict['label'] = self.codegen.quote_str( obj.label )
        return self._get_code(obj)

    def get_code_wxBoxSizer(self, obj):
        "Set sizer specific properties and generate the code"
        self.tmpl_dict['orient'] = self.codegen.cn( obj.properties["orient"].get_string_value() )
        return self._get_code(obj)

    def get_code_wxStdDialogButtonSizer(self, obj):
        "Set sizer specific properties and generate the code"
        init, layout = self._get_code(obj)
        layout.append(self.tmpl_Realize % self.tmpl_dict)
        return init, layout

    def get_code_wxGridSizer(self, obj):
        "Set sizer specific properties and generate the code"
        if self.klass != 'wxGridBagSizer':
            self.tmpl_dict['rows'] = obj.rows
            self.tmpl_dict['cols'] = obj.cols
        self.tmpl_dict['vgap'] = obj.vgap
        self.tmpl_dict['hgap'] = obj.hgap
        return self._get_code(obj)

    def get_code_wxFlexGridSizer(self, obj):
        "Set sizer specific properties and generate the code"
        ret = list( self.get_code_wxGridSizer(obj) )

        if obj.klass=="wxGridBagSizer":
            max_row, max_col = obj._get_max_row_col()
        else:
            max_row = max_col = None

        growable = []
        if 'growable_rows' in obj.properties:
            for row in obj.growable_rows:
                if max_row is None or row<=max_row:
                    self.tmpl_dict['row'] = row
                    growable.append(self.tmpl_AddGrowableRow % self.tmpl_dict)
        if 'growable_cols' in obj.properties:
            for col in obj.growable_cols:
                if max_col is None or col<=max_col:
                    self.tmpl_dict['col'] = col
                    growable.append(self.tmpl_AddGrowableCol % self.tmpl_dict)
        ret[-1] = growable + ret[-1]
        return ret

    def get_code_per_child(self, obj, child):
        """Returns code that will be inserted after the child code; e.g. for adding element to a sizer.
        It's placed before the final code returned from get_code()."""

        if child.classname in ("spacer","sizerslot"):  # spacer and slot are adding itself to the sizer
            return []

        # the name attribute of a spacer is already formatted "<width>, <height>".
        # This string can simply inserted in Add() call.
        obj_name = self.codegen._format_classattr(child)

        # check if sizer has to store as a class attribute
        sizer_name = self.codegen._format_classattr(obj)

        flag = child.properties["flag"].get_string_value()  # as string, joined with "|"
        flag = self.codegen.cn_f(flag) or '0'

        if self.klass=="wxStdDialogButtonSizer" and child.WX_CLASS=='wxButton':
            # XXX optionally use SetAffirmativeButton, SetCancelButton, SetNegativeButton
            id_value = child.check_prop("id") and child.properties["id"].value.strip() or ""  # e.g. 'wxID_CANCEL'
            if ( (child.check_prop_truth("stockitem") and child.stockitem in obj.BUTTON_STOCKITEMS) or 
                 (id_value and id_value.startswith("wxID_") and id_value[5:] in obj.BUTTON_STOCKITEMS) ):
                tmpl = self.codegen.tmpl_sizeritem_button
                return [tmpl % ( sizer_name, obj_name )]

        if self.klass!="wxGridBagSizer":
            stmt = self.codegen.tmpl_sizeritem % ( sizer_name, obj_name, child.proportion, flag, child.border )
        else:
            pos = obj._get_row_col(child.pos)
            stmt = self.codegen.tmpl_gridbagsizeritem % ( sizer_name, obj_name, pos, child.span, flag, child.border )

        return [stmt]


class SlotGenerator(object):
    # generic code generator; as a slot does not have flags etc. we don't need BaseWidgetBuilder etc.
    def __init__(self, language):
        self.language = language
        self.codegen = common.code_writers[self.language] #language specific code generator (codegen.BaseLangCodeWriter)

    def get_code(self, obj):
        # add spacer for empty sizer slot
        parent = obj.parent
        if not parent.IS_SIZER or parent._IS_GRIDBAG: return [], []
        sizer_name = self.codegen._format_classattr(parent)
        size = self.codegen.tmpl_spacersize%(0, 0)
        stmt = self.codegen.tmpl_sizeritem % ( sizer_name, size, 0, '0', 0 )
        return [stmt], []

    def get_event_handlers(self, obj):
        return []


class Sizer(edit_base.EditBase):
    "Base class for every Sizer handled by wxGlade"
    # XXX move this into BaseSizer, as virtual sizers are no longer used
    IS_SIZER = True
    IS_TOPLEVEL = IS_WINDOW = IS_SLOT = False
    _IS_GRIDBAG = False
    CHILDREN = None  # any number
    def __init__(self, name, parent, pos):
        edit_base.EditBase.__init__(self, name, parent, pos)

    window = edit_base.EditBase.parent_window

    def set_item(self, pos, option=None, flag=None, border=None, size=None, force_layout=True):
        "Updates the layout of the item at the given pos"
        raise NotImplementedError

    def add_item(self, item, pos=None, option=0, flag=0, border=0, size=None, force_layout=True):
        "Adds an item to self"
        raise NotImplementedError


class OrientProperty(np.Property):
    "orientation property for BoxSizers; hidden property to be set by the ClassOrientProperty"
    ORIENTATION_to_STRING = {wx.HORIZONTAL: 'wxHORIZONTAL', wx.VERTICAL: 'wxVERTICAL'}
    STRING_to_ORIENTATION = {'wxHORIZONTAL': wx.HORIZONTAL, 'wxVERTICAL': wx.VERTICAL}

    def __init__(self, value, default_value=None, name=None):
        assert value!=0
        np.Property.__init__(self, value, default_value, name)
    def _set_converter(self, value):
        if not value: return None
        if isinstance(value, int): return value
        return self.STRING_to_ORIENTATION.get(value, value)
    def _write_converter(self, value):
        if not value: return None
        return self.ORIENTATION_to_STRING[value]
    def get_string_value(self):
        return self.ORIENTATION_to_STRING[self.value]


class ClassOrientProperty(np.RadioProperty):
    # radio box: class name and orientation; will not be written to XML file, but will influence class and orient
    CHOICES = [ ('wxBoxSizer (wxVERTICAL)', 'without box and label'),
                ('wxBoxSizer (wxHORIZONTAL)', 'without box and label'),
                ('wxStaticBoxSizer (wxVERTICAL)', 'with box and label'),
                ('wxStaticBoxSizer (wxHORIZONTAL)', 'with box and label') ]
    if HAVE_WRAP_SIZER:
        CHOICES += [
                ('wxWrapSizer (wxVERTICAL)', 'without box and label; wraps around'),
                ('wxWrapSizer (wxHORIZONTAL)', 'without box and label; wraps around') ]
    CHOICES += [('wxStdDialogButtonSizer', 'for dialog buttons (will be rearranged acc. to platform style guide)'),
                ('wxGridSizer', None),
                ('wxFlexGridSizer', "with columns/rows of different widths"),
                ('wxGridBagSizer', "with cell spanning (i.e. item may populate multiple grid cells)")]

    TOOLTIPS = [c[1] for c in CHOICES]
    CHOICES  = [c[0] for c in CHOICES]

    def __init__(self, value=None):
        np.RadioProperty.__init__(self, value, self.CHOICES, tooltips=self.TOOLTIPS)
    def write(self, output, tabs=0):
        pass


class SizerBase(Sizer, np.PropertyOwner):
    "Base class for every non-virtual Sizer handled by wxGlade"
    PROPERTIES = ["Common", "name", "attribute", "class", "orient", "class_orient", # class and orient are hidden
                  "Layout"]  # not a property, just start the next page in the editor
    EXTRA_PROPERTIES = []

    MANAGED_PROPERTIES  = edit_base.MANAGED_PROPERTIES
    TOPLEVEL_PROPERTIES = ["fit"]

    _PROPERTY_LABELS = {"fit":"Fit parent",
                        "attribute":'Store as attribute',
                        "option": "Proportion",
                        "class_orient":"Sizer Type"}
    _PROPERTY_HELP = {"fit":'Sizes the window so that it fits around its subwindows',
                      "attribute":'Store instance as attribute of window class; e.g. self.sizer_1 = wx.BoxSizer(...)\n'
                                  'Without this, you can not access the sizer from your program'}

    def __init__(self, name, klass, orient, parent, pos):
        Sizer.__init__(self, name, parent, pos)

        # if True, self is not inside another sizer, but it is the responsible of the layout of self.window
        toplevel = not parent.IS_SIZER
        self.toplevel = toplevel

        # initialise instance properties
        self.classname    = klass
        self.klass        = np.Property(klass, name="class")             # class and orient are hidden
        self.orient       = OrientProperty(orient)                       # they will be set from the class_orient property
        self.class_orient = ClassOrientProperty(self.get_class_orient()) # this will set the class and orient properties
        self.attribute    = np.CheckBoxProperty(False, default_value=False)
        self.fit          = np.ActionButtonProperty(self.fit_parent)

        if not self.toplevel:
            self.PROPERTIES = self.PROPERTIES + self.MANAGED_PROPERTIES + self.EXTRA_PROPERTIES
            # if within another sizer: the arguments to sizer.Add(self, proportion, flag, border)
            # same as for edit_windows.ManagedBase
            if pos is None: pos = self.parent.children.index(self)
            self.pos        = np.LayoutPosProperty(pos)        # the position within the sizer, 0-based
            self.span       = np.LayoutSpanProperty((1,1) )  # row,colspan for items in GridBagSizers
            self.proportion = np.LayoutProportionProperty(1)
            self.border     = np.SpinProperty(0, immediate=True)
            self.flag       = np.ManagedFlags(wx.EXPAND)
            self._has_layout = True
        else:
            self._has_layout = False
            self.PROPERTIES = self.PROPERTIES + self.TOPLEVEL_PROPERTIES + self.EXTRA_PROPERTIES

        self._btn = None      # "handle" to activate a Sizer and to access its popup menu (SizerHandleButton)

    def frozen(self):
        return self.window.frozen()

    def create_widget(self, dont_add=False):
        "Creates the wxSizer self.widget"
        # dont_add is True when called from change_sizer, in order not to add the new widget to the parent sizer
        raise NotImplementedError

    def create(self, dont_set=False):
        if self.widget: return  # nothing to do if the sizer has already been created
        self._btn = SizerHandleButton(self.window, self.id, self ) # XXX handle the popupmenu creation in SizerHandleButton
        # ScreenToClient used by WidgetTree for the popup menu
        self._btn.Bind(wx.EVT_BUTTON, self.on_selection, id=self.id)
        self._btn.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse_events, id=self.id)
        self.create_widget(dont_set)
        self.widget.Refresh = self.refresh
        self.widget.GetBestSize = self.widget.GetMinSize
        self.widget.ScreenToClient = self._btn.ScreenToClient
        if self.toplevel and not dont_set:  # is dont_set useful here?
            self.window.set_sizer(self)
        if not config.preferences.show_sizer_handle:
            self.widget.Show(self._btn, False)

    def on_mouse_events(self, event):
        if event.Dragging():
            # start drag & drop
            window = misc.get_toplevel_parent(self._btn)
            if self._btn:
                self._btn.OnLeftUp(event)
            clipboard.begin_drag(window, self)
            return
        event.Skip()

    def on_selection(self, event):
        # button clicked -> set ourself as current widget
        misc.set_focused_widget(self)

    def get_class_orient(self):
        # as string
        return self.WX_CLASS

    def properties_changed(self, modified):
        # "class" and "orient" will only display; "class_orient"
        if modified and "name" in modified:
            previous_name = self.properties["name"].previous_value
            common.app_tree.refresh(self, refresh_label=True, refresh_image=False)
            
        if not modified or "class" in modified:
            self.properties["class_orient"].set(self.get_class_orient())
        if not modified or "orient" in modified:
            self.properties["class_orient"].set(self.get_class_orient())
        if "class_orient" in modified:
            # user has selected -> change
            value = self.class_orient
            if misc.focused_widget is self: misc.set_focused_widget(None)
            wx.CallAfter(change_sizer, self, value)
        if (not modified or "flag" in modified or "option" in modified or "border" in modified or "span" in modified):
            if not self.toplevel and self.sizer is not None:
                if "border" in modified and self.border and not "flag" in modified:
                    # enable border flags if not yet done
                    p = self.properties["flag"]
                    if not p.value_set.intersection(p.FLAG_DESCRIPTION["Border"]):
                        p.add("wxALL")
                if self.widget:
                    self.sizer.item_properties_modified(self, modified)
        edit_base.EditBase.properties_changed(self, modified)

    def check_drop_compatibility(self):
        return (False, "Items can only be added to empty slots; add/insert a slot first, if required.")

    def check_compatibility(self, widget, typename=None):
        if typename is not None:
            if typename in ("widget","sizer"):
                return ("AddSlot",None)
            return (False,"Only widgets and sizers can be pasted here")
        if widget.IS_TOPLEVEL:
            return (False,"No toplevel objects can be pasted here")
        return ("AddSlot",None) # a slot is to be added before inserting/pasting

    # popup menu #######################################################################################################
    def popup_menu(self, event, pos=None):
        "pops up a menu to add or remove slots from self, or to remove self from the application."
        event_widget = event.GetEventObject()
        menu = self._create_popup_menu(widget=event_widget)
        if pos is None:
            # convert relative event position to relative widget position
            event_pos  = event.GetPosition()
            screen_pos = event_widget.ClientToScreen(event_pos)
            pos        = event_widget.ScreenToClient(screen_pos)
        event_widget.PopupMenu(menu, pos)
        menu.Destroy()

    def _can_add_insert_slots(self, report=False):
        return True

    def _create_popup_menu(self, widget):
        # provide popup menu for removal
        menu = misc.wxGladePopupMenu(self.name)

        widgetclass = self.__class__.__name__.lstrip("Edit")
        i = misc.append_menu_item(menu, -1, _('Remove %s\tDel')%widgetclass, wx.ART_DELETE)
        misc.bind_menu_item_after(widget, i, self.remove)

        if not self.toplevel and self.sizer and self.sizer._can_add_insert_slots():
            i = misc.append_menu_item( menu, -1, _('Insert slot before\tCtrl+I') )
            misc.bind_menu_item_after(widget, i, self.sizer.insert_slot, self.pos)
            menu.AppendSeparator()

        # other menu items: add/insert slot, copy, cut
        if self._can_add_insert_slots():
            i = misc.append_menu_item( menu, -1, _('Add slot\tCtrl+A') )
            misc.bind_menu_item_after(widget, i, self.add_slot)

        if "cols" in self.PROPERTIES:  # a grid sizer
            i = misc.append_menu_item( menu, -1, _('Add row') )
            misc.bind_menu_item_after(widget, i, self.insert_row, -1)
            i = misc.append_menu_item( menu, -1, _('Add column') )
            misc.bind_menu_item_after(widget, i, self.insert_col, -1)
            menu.AppendSeparator()

        i = misc.append_menu_item( menu, -1, _('Copy\tCtrl+C'), wx.ART_COPY )
        misc.bind_menu_item_after(widget, i, clipboard.copy, self)
        i = misc.append_menu_item( menu, -1, _('Cut\tCtrl+X'), wx.ART_CUT )
        misc.bind_menu_item_after(widget, i, clipboard.cut, self)

        # preview (create or close?)
        menu.AppendSeparator()
        p = misc.get_toplevel_widget(self)
        if p is not None and p.preview_is_visible():
            item = _('Close preview (%s)\tF5') % p.name
        else:
            item = _('Preview (%s)\tF5') % p.name
        i = misc.append_menu_item( menu, -1, item )
        misc.bind_menu_item_after(widget, i, self.preview_parent)

        return menu

    def _add_parent_popup_menu_items(self, menu, item, widget):
        # called from managed widget items' _create_popup_menu method

        # rows/cols if inside a grid sizer
        if "rows" in self.PROPERTIES:
            row, col = self._get_row_col(item.pos)
            i = misc.append_menu_item(menu, -1, _('Insert Row before') )
            misc.bind_menu_item_after(widget, i, self.insert_row, item.pos)
            i = misc.append_menu_item(menu, -1, _('Insert Column before') )
            misc.bind_menu_item_after(widget, i, self.insert_col, item.pos)
            if row==self.rows-1:
                # last row
                i = misc.append_menu_item(menu, -1, _('Add Row') )
                misc.bind_menu_item_after(widget, i, self.insert_row, -1)
            if col==self.cols-1:
                # last col
                i = misc.append_menu_item(menu, -1, _('Add Column') )
                misc.bind_menu_item_after(widget, i, self.insert_col, -1)

        if "growable_rows" in self.PROPERTIES:
            i = misc.append_menu_item(menu, -1, _('Make Row growable'), kind=wx.ITEM_CHECK )
            i.Check(row in self.growable_rows)
            misc.bind_menu_item_after(widget, i, self.make_growable, "row", row)
            i = misc.append_menu_item(menu, -1, _('Make Column growable'), kind=wx.ITEM_CHECK )
            i.Check(col in self.growable_cols)
            misc.bind_menu_item_after(widget, i, self.make_growable, "col", col)
            

        if "rows" in self.PROPERTIES:
            menu.AppendSeparator()

        if self._can_add_insert_slots():
            # slots
            i = misc.append_menu_item(menu, -1, _('Insert Slot before\tCtrl+I') )
            misc.bind_menu_item_after(widget, i, self.insert_slot, item.pos)
            i = misc.append_menu_item(menu, -1, _('Insert Slots before...\tCtrl+Shift+I') )
            misc.bind_menu_item_after(widget, i, self.insert_slot, item.pos, True)
    
            if item.pos==len(self.children)-1: # last slot -> allow to add
                i = misc.append_menu_item(menu, -1, _('Add Slot\tCtrl+A') )
                misc.bind_menu_item_after(widget, i, self.add_slot)
                i = misc.append_menu_item(menu, -1, _('Add Slots...\tCtrl+Shift+A') )
                misc.bind_menu_item_after(widget, i, self.add_slot, True)
            menu.AppendSeparator()

        ####################################################################################################################
    def _remove(self):
        "removes the sizer from his parent, if it has one"
        return self.parent._free_slot( self.parent.children.index(self) )

    def remove(self):
        # entry point from GUI
        common.root.saved = False  # update the status of the app
        focus = self._remove()  # slot or window
        misc.rebuild_tree(focus)

    def Destroy(self):
        GenButton.Destroy(self)
        if misc.focused_widget is self:
            misc.focused_widget = None

    def preview_parent(self):
        # context menu callback
        p = misc.get_toplevel_widget(self)
        p.preview()

    def fit_parent(self, *args):
        "Tell the sizer to resize the window to match the sizer's minimal size"
        if self.widget and self.window.widget:
            if self.window.IS_TOPLEVEL:
                self.widget.Fit(self.window.widget.GetTopLevelParent())
            else:
                self.widget.Fit(self.window.widget)
            # self.widget.SetSizeHints(self.window.widget)
            self.window.widget.Layout()

    def add_item(self, item, pos=None, size=None, force_layout=True):
        "Adds an item to self."
        # called from ManagedBase.__init__ when adding an item to the end from XML parser
        # or interactively when adding an item to an empty sizer slot
        #assert item in self.children
        if pos is None:
            pos = len(self.children)

        if pos==len(self.children):
            self.children.append(None)
        else:
            old_child = self.children[pos]
            if old_child and old_child.IS_SLOT and old_child.widget:
                # XXX move Detach to delete; don't remove the leaf; also the above checks can probably be removed and just .delete() being called
                self.widget.Detach(old_child.widget)
                old_child.delete()
        if "rows" in self.PROPERTIES and not self._IS_GRIDBAG:
            self._adjust_rows_cols()  # for GridSizer
        self.children[pos] = item
        item._size = size

        ################################################################################################################
        # actually add item.widget to self.widget, i.e. the wxWidget to the wxSizer
        if self.widget and item.widget:
            self._add_item(item, pos, size, force_layout=force_layout)

    def _add_item(self, item, pos, size=None, force_layout=True):
        "called from finish_widget_creation() to add to sizer widget"

        # calculate width, height
        size_arg = size
        if not size or -1 in size:
            best_size = item.widget.GetBestSize()
        if size:
            w, h = size
            if w == -1: w = best_size[0]
            if h == -1: h = best_size[1]
        else:
            w, h = best_size

        if pos>len(self.widget.GetChildren()):
            ## I have to set wxADJUST_MINSIZE to handle a bug that I'm not able to detect (yet): if the width or height
            ## of a widget is -1, the layout is messed up!
            if self._IS_GRIDBAG:
                self.widget.Add( item.widget, pos, item.span, item.flag, item.border )
            else:
                self.widget.Add( item.widget, item.proportion, item.flag, item.border )

            self.widget.SetItemMinSize(item.widget, w, h)
            return

        if self._IS_GRIDBAG:
            # XXX check item.widget.span and remove empty slots
            self.widget.Add( item.widget, pos, item.span, item.flag, item.border, destroy=True )
            self.widget.Layout()
            return

        # no GridBagSizer
        self.widget.Insert(pos+self.widget._BTN_OFFSET, item.widget, item.proportion, item.flag, item.border)

        try:  # if the item was a window, set its size to a reasonable value
            self.widget.SetItemMinSize(item.widget, w, h)  # w,h is GBestSize
        except Exception:
            # production version: exceptions to be ignored
            if config.debugging: raise
        if self.widget:
            self.window.widget.Refresh()
        if force_layout:
            self.layout()  # update the layout of self

    def get_child_index(self, pos):
        # return the index of the widget; in GridBagSizers, overlapped slots are skipped
        return pos

    def _fix_notebook(self, pos, notebook_sizer, force_layout=True):   # XXX check this with new implementation
        """Replaces the widget at 'pos' with 'notebook_sizer':
        this is intended to be used by wxNotebook widgets, to add the notebook sizer to this sizer.
        This is a hack, but it's the best I could find without having to rewrite too much code :-("""
        # no error checking at all, this is a "protected" method, so it should
        # be safe to assume the caller knows how to use it
        pos = self.get_child_index(pos)
        item = self.widget.GetChildren()[pos]
        if item.IsWindow():
            w = item.GetWindow()
            w.SetContainingSizer(None)
        compat.SizerItem_SetSizer(item, notebook_sizer)
        if force_layout:
            self.layout()

    def set_item_best_size(self, widget, size=(-1,-1), force_layout=True):
        if not self.widget or not widget.widget: return

        elem = self.widget.GetItem(widget.widget)
        if not elem: return

        if elem.IsWindow():
            item = elem.GetWindow()
            w, h = size
            if w==-1 or h==-1: best_size = item.GetBestSize()
            if w == -1: w = best_size[0]
            if h == -1: h = best_size[1]
            self.widget.SetItemMinSize(item, w, h)

        if force_layout:
            self.layout(True)

    @_frozen
    def item_properties_modified(self, widget, modified=None, force_layout=True):
        "update layout properties"
        if not self.widget or not widget.widget:
            return

        item = self.widget.GetItem(widget.widget)  # a SizerItem or GBSizerItem instance
        if not item: return

        size_was_reduced = False  # will the new scaled/expanded size be smaller than the previous?
        if modified is None or ("proportion" in modified or "option" in modified) and not self._IS_GRIDBAG:
            if widget.proportion<item.GetProportion(): size_was_reduced = True
            item.SetProportion(widget.proportion)
        if modified is None or "flag" in modified and widget.flag is not None:
            if (item.GetFlag() & wx.EXPAND) and not (widget.flag & wx.EXPAND): size_was_reduced = True
            item.SetFlag(widget.flag)
        if modified is None or "border" in modified:
            item.SetBorder(widget.border)
        if (modified is None or "span" in modified) and self._IS_GRIDBAG:
            self._check_slots(remove_only=True)
            item.SetSpan(widget.span)
            self._check_slots(add_only=True)

        # set either specified size or GetBestSize
        if item.IsWindow():
            widget.widget.SetMinSize( (-1,-1) )  # needed e.g. for TextCtrl after a style change
            best_size = widget.widget.GetBestSize()
            size_p = widget.properties["size"]
            if size_p.is_active():
                size = size_p.get_size(widget.widget) # XXX check dialog units -> call with window
                w, h = size
                if w == -1: w = best_size[0]
                if h == -1: h = best_size[1]
            elif widget.__class__.__name__=="EditSpacer":
                w = widget.width
                h = widget.height
            else:
                if size_was_reduced and  widget.__class__.__name__ in ("EditPanel","CustomWidget"):
                    # if proportion is reduced and no size defined, set to a minimum size of 20,20
                    # as GetBestSize returns the current size
                    # maybe refactoring is required; search for RRR
                    w,h = 20,20
                else:
                    w,h = best_size
            self.widget.SetItemMinSize(widget.widget, w, h)

        if force_layout:
            self.layout(True)

    def remove_item(self, elem, force_layout=True):
        "Removes elem from self"
        # called e.g. from context menu of SizerSlot; detaches element and does re-layout
        if elem:
            for c in self.children[elem.pos + 1:]:
                c.properties["pos"].value -= 1
            del self.children[elem.pos]
        if "rows" in self.PROPERTIES and not self._IS_GRIDBAG:
            self._adjust_rows_cols()  # for GridSizer
        if self.widget and elem.widget:
            if not self._IS_GRIDBAG:
                self.widget.Detach(elem.pos+self.widget._BTN_OFFSET)
            else:
                self.widget.Detach(elem.widget)  # don't use pos, as for gridbag it might be invalid
            if force_layout:
                self.layout(True)
                self.window.widget.Refresh()
                # if not self.toplevel: self.sizer.Layout()

    def layout(self, recursive=True):
        # update slot labels in tree view
        for c in self.children:
            if isinstance(c, SizerSlot):
                common.app_tree.refresh(c, refresh_image=False, refresh_label=True) # refresh_name( c.node )

        if not self.widget:
            return

        # layout
        window = self.window
        if self.toplevel and not window.IS_TOPLEVEL and hasattr(window.sizer, 'widget'):
            if not window.properties['size'].is_active():
                szr = window.sizer.widget
                w, h = window.widget.GetBestSize()
                szr.SetItemMinSize(window.widget, w, h)
            if window.sizer is not self:
                window.sizer.layout(False)
            else:
                szr.Layout()
            return
        elif self.toplevel and window.IS_TOPLEVEL:
            # self.window.widget.Layout()
            self.widget.Layout()
            evt = wx.SizeEvent( window.widget.GetSize(), window.widget.GetId() )
            wx.PostEvent(window.widget, evt)
            # don't change the size of the window
            if not misc.check_wx_version(2, 6, 0):
                self.widget.FitInside(window.widget)
            return
        self.widget.SetMinSize(self.widget.CalcMin())
        self.widget.Layout()
        for c in self.children:
            try:
                c.widget.Refresh()
            except:
                pass
        if recursive:
            if getattr(self, 'sizer', None) is not None:
                self.sizer.layout(recursive)

    def destroy_widget(self):
        # actually, the sizer widget is not destroyed
        if self._btn:
            # delete SizerHandleButton first, as the sizer widget may be destroyed already when called from change_sizer
            self._btn.Destroy()
            self._btn = None
        if not self.widget: return
        if self.toplevel:
            self.window.widget.SetSizer(None)
        else:
            self.widget.Clear()  # without deleting window items; but sets the sizer of the windows to NULL

    if wx.Platform == '__WXMSW__':
        def finish_set(self):  # previously called after self.set_option(...)
            for c in self.children:
                if c.widget:
                    try:
                        c.widget.Refresh()
                    except AttributeError:
                        pass  # sizers have no Refresh
    else:
        def finish_set(self):
            pass

    def refresh(self, *args):
        # this will be self.widget.Refresh
        for c in self.children:
            if c.widget:
                try:
                    c.widget.Refresh()
                except AttributeError:
                    pass

    def update_view(self, selected):
        if self._btn is None: return
        if selected:
            color = wx.RED
        else:
            color = compat.wx_SystemSettings_GetColour(wx.SYS_COLOUR_BTNFACE)
        self._btn.SetBackgroundColour(color)
        self._btn.Refresh(True)

    # add/insert/free slots; interface mainly from context menus #######################################################
    def _add_slot(self, loading=False):
        "adds an empty slot to the sizer, i.e. a fake window that will accept the dropping of widgets"
        # called from "add slot" context menu handler of sizer
        # called from XML parser for adding empty 'sizerslot': sizer._add_slot(loading=True)
        slot = SizerSlot(self, len(self.children))
        if "rows" in self.PROPERTIES: self._adjust_rows_cols(loading)  # for GridSizer

        if self.widget:
            slot.create()  # create the actual SizerSlot widget
            if not self._IS_GRIDBAG:
                self.widget.Add(slot.widget, 1, wx.EXPAND)
            else:
                self._check_slots(remove_only=True)  # the added slot could be hidden
                self.widget.Add( slot.widget, slot.pos, slot.span, slot.flag, slot.border )
            self.widget.SetItemMinSize(slot.widget, 20, 20)
        return slot

    def _insert_slot(self, pos=None, select=True, no_add=False):
        "Inserts an empty slot into the sizer at pos (1 based); optionally force layout update"
        # called from context menu handler; multiple times if applicable; layout will be called there
        # also called from SizerBase._remove after a sizer has removed itself and inserts an empty slot instead
        if pos>=len(self.children) or not self.children[pos] is None:
            self.children.insert( pos, None)  # placeholder to be overwritten
        slot = SizerSlot(self, pos)
        for p,c in enumerate(self.children):
            if c is None: continue
            pos_p = c.properties["pos"]
            if pos_p.value!=p: pos_p.value=p

        if "rows" in self.PROPERTIES: self._adjust_rows_cols()  # for GridSizer

        if self.widget:
            slot.create()  # create the actual SizerSlot
            if not no_add:
                if not self._IS_GRIDBAG:
                    self.widget.Insert(pos+self.widget._BTN_OFFSET, slot.widget, slot.proportion, slot.flag)
                else:
                    self._check_slots(remove_only=True)  # the added slot could be hidden
                    self.widget.Add(slot.widget, slot.pos, slot.span, slot.flag, slot.border)
            self.widget.SetItemMinSize(slot.widget, 20, 20)
        return slot

    # insert/add slot callbacks for context menus ######################################################################
    def _ask_count(self, insert=True):
        # helper for next method (insertion/adding of multiple slots)
        choices = [str(n) for n in range(1,11)]
        if insert:
            dlg = wx.SingleChoiceDialog(None, "Select number of slots to be inserted", "Insert Slots", choices)
        else:
            dlg = wx.SingleChoiceDialog(None, "Select number of slots to be added", "Add Slots", choices)
        ret = 0  if dlg.ShowModal()==wx.ID_CANCEL  else   int(dlg.GetStringSelection())
        dlg.Destroy()
        return ret

    def insert_slot(self, pos, multiple=False):
        # insert before current
        if not self._can_add_insert_slots(report=True):
            return
        count = self._ask_count() if multiple else 1
        with self.window.frozen():
            for n in range(count):
                slot = self._insert_slot(pos)
            if self.widget: self.layout(True)
        misc.rebuild_tree(slot, recursive=False)

    def add_slot(self, multiple=False):
        # add to the end
        if not self._can_add_insert_slots(report=True):
            return
        count = self._ask_count(insert=False) if multiple else 1
        with self.window.frozen():
            for n in range(count):
                slot = self._add_slot()
            if self.widget: self.layout()
        misc.rebuild_tree(slot, recursive=False)  # rebuild also slots

    @_frozen
    def _free_slot(self, pos, force_layout=True):
        "Replaces the element at pos with an empty slot"
        # called from ManagedBase context menu when removing an item
        old_child = self.children[pos]
        slot = SizerSlot(self, pos)

        # replace the node with a SlotNode
        if self.widget:
            # required here; otherwise removal of a StaticBox of a StaticBoxSizer will cause a crash
            self.widget.Detach(old_child.widget)
        old_child.recursive_remove(overwritten=True)

        if self.widget:
            slot.create()  # create the actual SizerSlot as wx.Window with hatched background
            if not self._IS_GRIDBAG:
                self.widget.Insert(pos+self.widget._BTN_OFFSET, slot.widget, 1, wx.EXPAND)
            else:
                self.widget.Add( slot.widget, pos, slot.span, slot.flag, slot.border )
                self._check_slots(add_only=True)
            if force_layout:
                self.layout()
        return slot

    ####################################################################################################################
    def is_visible(self):
        return self.window.is_visible()

    def post_load(self):
        """Called after loading of an app from a XML file, before showing the hierarchy of widget for the first time.
        This is used only for container widgets, to adjust their size appropriately."""
        if "rows" in self.PROPERTIES: self._adjust_rows_cols()  # for GridSizer
        if not self.toplevel:
            return
        size_p = self.window.properties['size']
        if not size_p.is_active():
            self.fit_parent()
            w, h = self.widget.GetSize()
            postfix = ''
            if config.preferences.use_dialog_units:
                w, h = compat.ConvertPixelsToDialog( self.window.widget, self.widget.GetSize() )
                postfix = 'd'
            size_p.set('%s, %s%s' % (w, h, postfix))

    def _get_tree_image(self):
        "Get an image name for tree display"
        name = self.__class__.__name__

        if name in ("EditStaticBoxSizer", "EditBoxSizer"):
            # with or without label, horizontal/vertical
            if self.orient & wx.VERTICAL:
                name = "EditVerticalSizer"
            elif self.orient & wx.HORIZONTAL:
                name = "EditHorizontalSizer"
            else:
                name = "EditSpacer"
        elif name=="EditWrapSizer":
            if self.orient & wx.VERTICAL:
                name = "EditVerticalWrapSizer"
            else:
                name = "EditHorizontalWrapSizer"

        return name



class wxGladeBoxSizer(wx.BoxSizer):
    _BTN_OFFSET = 1
    def SetItemMinSize(self, item, w, h):
        if w==-1 or h==-1:
            try:
                w2, h2 = item.GetBestSize()
                if w == -1: w = w2
                if h == -1: h = h2
            except AttributeError:
                pass
        wx.BoxSizer.SetItemMinSize(self, item, w, h)


class BoxSizerBase(SizerBase):
    "orientation handling for BoxSizer and StaticBoxSizer"

    def __init__(self, name, parent, pos, orient=wx.VERTICAL, elements=0):
        # elements: number of slots
        SizerBase.__init__(self, name, self.WX_CLASS, orient, parent, pos)

        self.children = []

        for i in range(elements):
            self._add_slot()
        self.layout()

    def get_class_orient(self):
        return '%s (%s)'%( self.WX_CLASS, self.properties["orient"].get_string_value() )

    def properties_changed(self, modified):
        if not modified or "orient" in modified and self.item and config.use_gui:
            # update the image
            common.app_tree.refresh(self, refresh_label=False, refresh_image=True)

        SizerBase.properties_changed(self, modified)


class EditBoxSizer(BoxSizerBase):
    "Class to handle wxBoxSizer objects"
    WX_CLASS = "wxBoxSizer"

    def create_widget(self, dont_add=False):
        self.widget = wxGladeBoxSizer(self.orient)
        self.widget.Add(self._btn, 0, wx.EXPAND)
        to_lay_out = []
        for c in self.children:
            c.create()
            if isinstance(c, SizerSlot):
                self.widget.Add(c.widget, 1, wx.EXPAND)
                self.widget.SetItemMinSize(c.widget, 20, 20)
            else:
                sp = c.properties.get('size')
                if sp and sp.is_active():
                    if (c.proportion != 0 or (c.flag & wx.EXPAND)) and not (c.flag & wx.FIXED_MINSIZE):
                        c.widget.Layout()
                        size = sp.get_size(c.widget)
                        c.widget.SetMinSize(size)
                    else:
                        size = sp.get_size(c.widget)
                        # now re-set the item to update the size correctly...
                        to_lay_out.append((c.pos, size) )
        for pos, size in to_lay_out:
            self.set_item_best_size(self.children[pos], size)
        self.layout(True)
        if self.parent.IS_SIZER and not dont_add:
            self.parent._add_item( self, self.pos, self.widget.GetMinSize() )


if HAVE_WRAP_SIZER:
    class wxGladeWrapSizer(wx.WrapSizer):
        _BTN_OFFSET = 0
        def SetItemMinSize(self, item, w, h):
            if w==-1 or h==-1:
                try:
                    w2, h2 = item.GetBestSize()
                    if w == -1: w = w2
                    if h == -1: h = h2
                except AttributeError:
                    pass
            wx.BoxSizer.SetItemMinSize(self, item, w, h)


    class EditWrapSizer(BoxSizerBase):
        "Class to handle wxWrapSizer objects"
        WX_CLASS = "wxWrapSizer"
    
        def create_widget(self, dont_add=False):
            self.widget = wxGladeWrapSizer(self.orient)
            self.widget.Add(self._btn, 0, wx.EXPAND)
            to_lay_out = []
            for c in self.children:
                c.create()
                if isinstance(c, SizerSlot):
                    self.widget.Add(c.widget, 1, wx.EXPAND)
                    self.widget.SetItemMinSize(c.widget, 20, 20)
                else:
                    sp = c.properties.get('size')
                    if sp and sp.is_active():
                        if (c.proportion != 0 or (c.flag & wx.EXPAND)) and not (c.flag & wx.FIXED_MINSIZE):
                            c.widget.Layout()
                            size = sp.get_size(c.widget)
                            c.widget.SetMinSize(size)
                        else:
                            size = sp.get_size(c.widget)
                            # now re-set the item to update the size correctly...
                            to_lay_out.append((c.pos, size) )
            for pos, size in to_lay_out:
                self.set_item_best_size(self.children[pos], size)
            self.layout(True)
            if self.parent.IS_SIZER and not dont_add:
                self.sizer._add_item( self, self.pos, self.widget.GetMinSize() )


class EditStdDialogButtonSizer(EditBoxSizer):
    "Class to handle wxStdDialogButtonSizer objects"
    WX_CLASS = "wxStdDialogButtonSizer"
    # the stockitems that are handled specially by StdDialogButtonSizer
    BUTTON_STOCKITEMS = ["OK", "YES", "SAVE", "APPLY", "CLOSE","NO", "CANCEL", "HELP", "CONTEXT_HELP"]
    def __init__(self, name, parent, pos, elements=0):
        # elements: number of slots
        BoxSizerBase.__init__(self, name, parent, pos, wx.HORIZONTAL, elements)

    def get_class_orient(self):
        return self.WX_CLASS


class wxGladeStaticBoxSizer(wx.StaticBoxSizer):
    _BTN_OFFSET = 1
    def SetItemMinSize(self, item, w, h):
        if w==-1 or h==-1:
            try:
                w2, h2 = item.GetBestSize()
                if w == -1: w = w2
                if h == -1: h = h2
            except AttributeError:
                pass
        wx.StaticBoxSizer.SetItemMinSize(self, item, w, h)



class EditStaticBoxSizer(BoxSizerBase):
    "Class to handle wxStaticBoxSizer objects"
    WX_CLASS = "wxStaticBoxSizer"
    PROPERTIES = ["Common", "name", "class", "orient", "class_orient", # class and orient are hidden
                  "label", "attribute",
                  "Layout"]  # not a property, just start the next page in the editor
    EXTRA_PROPERTIES = []

    def __init__(self, name, parent, pos, orient=wx.VERTICAL, label='', elements=3):
        BoxSizerBase.__init__(self, name, parent, pos, orient, elements)
        self.label = np.TextProperty(label)

    def create_widget(self, dont_add=False):
        self.widget = wxGladeStaticBoxSizer( wx.StaticBox(self.window.widget, -1, self.label), self.orient )
        self.widget.Add(self._btn, 0, wx.EXPAND)
        for c in self.children:
            c.create()
            if isinstance(c, SizerSlot):
                self.widget.Add(c.widget, 1, wx.EXPAND)
                self.widget.SetItemMinSize(c.widget, 20, 20)
            else:
                size_p = c.properties.get('size')
                if size_p and size_p.is_active() and ( c.proportion == 0 or not (c.flag & wx.EXPAND) ):
                    w,h = size_p.get_size(c.widget)
                else:
                    w, h = c.widget.GetBestSize()
                self.widget.SetItemMinSize(c.widget, w, h)
        self.layout()
        if self.parent.IS_SIZER and not dont_add:
            self.parent._add_item(self, self.pos, self.widget.GetMinSize())

    def properties_changed(self, modified):
        if not modified or "label" in modified and self.widget:
            self.widget.GetStaticBox().SetLabel(self.label or "")
            #self.layout()
        if modified and "name" in modified:
            common.app_tree.refresh(self, refresh_label=True, refresh_image=False)
        elif not modified or "label" in modified or "name" in modified and self.node:
            common.app_tree.refresh(self, refresh_label=True, refresh_image=False)

        BoxSizerBase.properties_changed(self, modified)

    def destroy_widget(self):
        if self.widget:
            self.widget.GetStaticBox().Destroy()
        SizerBase.destroy_widget(self)



class CustomGridSizer(wx.BoxSizer):
    """Custom wxSizer class used to implement a GridSizer with an additional handle button.
    e.g. in EditGridSizer instance: self.widget = CustomGridSizer(self,rows,cols,vgap,hgap"""
    _BTN_OFFSET = 0
    def __init__(self, parent, rows, cols, vgap, hgap):
        wx.BoxSizer.__init__(self, wx.VERTICAL)
        self.parent = parent  # EditGridSizer or derived class
        self._create(rows, cols, vgap, hgap)
        wx.BoxSizer.Add(self, self.parent._btn, 0, wx.EXPAND)
        wx.BoxSizer.Add(self, self._grid, 1, wx.EXPAND)
        if wx.VERSION[:2] < (3,0):
            self._growable_rows = set()
            self._growable_cols = set()

    def _create(self, rows, cols, vgap, hgap):
        self._grid = wx.GridSizer(rows, cols, vgap, hgap)

    def __getattr__(self, name):
        return getattr(self._grid, name)

    def GetBestSize(self):
        return self._grid.GetMinSize()

    def Add(self, *args, **kwds):
        self._grid.Add(*args, **kwds)

    def Insert(self, pos, *args, **kwds):
        self._grid.Insert(pos, *args, **kwds)

    def Remove(self, *args, **kwds):
        try:
            pos = int(args[0])
            self._grid.Remove(pos)
        except TypeError:
            self._grid.Remove(*args, **kwds)

    def RemovePos(self, pos):
        self._grid.Remove(pos)

    def Detach(self, pos_or_obj):
        try:
            pos = int(pos_or_obj)
            self._grid.Detach(pos)
        except TypeError:
            self._grid.Detach(pos_or_obj)

    def SetItemMinSize(self, item, w, h):
        try:
            w2, h2 = item.GetBestSize()
            if w == -1: w = w2
            if h == -1: h = h2
        except AttributeError:
            pass
        self._grid.SetItemMinSize(item, w, h)

    def GetChildren(self):
        return self._grid.GetChildren()

    def GetItem(self, widget):
        if hasattr(self._grid, "FindItem"):
            return self._grid.FindItem(widget)  # GridBagSizer
        return self._grid.GetItem(widget)

    def Layout(self):
        self._grid.Layout()
        wx.BoxSizer.Layout(self)

    if wx.VERSION[:2] < (3,0):
        # compatibility for wxPython 2.8, as IsRowGrowable was only introduced with wx 2.9.1
        def IsRowGrowable(self, row):
            return row in self._growable_rows
        def IsColGrowable(self, col):
            return col in self._growable_cols
        def AddGrowableRow(self, row):
            self._grid.AddGrowableRow(row)
            self._growable_rows.add(row)
        def RemoveGrowableRow(self, row):
            self._grid.RemoveGrowableRow(row)
            self._growable_rows.remove(row)
        def AddGrowableCol(self, col):
            self._grid.AddGrowableCol(col)
            self._growable_cols.add(col)
        def RemoveGrowableCol(self, col):
            self._grid.RemoveGrowableCol(col)
            self._growable_cols.remove(col)


class CustomFlexGridSizer(CustomGridSizer):
    def _create(self, rows, cols, vgap, hgap):
        self._grid = wx.FlexGridSizer(rows, cols, vgap, hgap)


class CustomGridBagSizer(CustomFlexGridSizer):
    def _create(self, rows, cols, vgap, hgap):
        self._grid = wx.GridBagSizer(vgap, hgap)

    def Add(self, widget, pos, span, flag, border, destroy=False):
        "Add to sizer, re-use existing SizerItem if there is one; pos is (row,col)"
        if isinstance(pos, int):
            pos = self.parent._get_row_col(pos)
        old_sizer_item = self._grid.FindItemAtPosition(pos)
        if old_sizer_item:
            if destroy:
                old_window = old_sizer_item.GetWindow()
                if old_window:
                    compat.DestroyLater(old_window)
            old_sizer_item.SetSpan((1,1))
            old_sizer_item.SetFlag(wx.EXPAND)
            old_sizer_item.SetBorder(border)
            if isinstance(widget, wx.Sizer):
                old_sizer_item.AssignSizer(widget)
            else:
                old_sizer_item.AssignWindow(widget)
        else:
            self._grid.Add( widget, pos, span, flag, border )

    def Detach(self, obj):
        self._grid.Detach(obj)


class GridSizerBase(SizerBase):
    "Base class for Grid sizers"
    _PROPERTY_HELP = {"rows":"Number of sizer rows; can be set to 0 for 'as many as required'.\n"
                             "This will re-arrange the children and empty slots, but not add/remove slots.\n"
                             "To insert/add rows, better use the context menu items",
                      "cols":"Number of sizer columns; can be set to 0 for 'as many as required'.\n"
                             "This will re-arrange the children and empty slots, but not add/remove slots.\n"
                             "To insert/add columns, better use the context menu items",
                      "vgap":'Vertical extra space between all children',
                      "hgap":'Horizontal extra space between all children'}

    EXTRA_PROPERTIES = ["Grid", "rows", "cols", "vgap", "hgap"]

    def __init__(self, name, klass, parent, pos, rows=3, cols=3, vgap=0, hgap=0):
        SizerBase.__init__(self, name, klass, None, parent, pos)
        if self.WX_CLASS == "wxGridBagSizer":
            val_range=(1,1000)
        else:
            # Grid and FlexGrid sizers allow columns/rows to be 0, i.e. as many as required
            val_range=(0,1000)
        self.rows = np.SpinProperty(rows, val_range=val_range, immediate=True)
        self.cols = np.SpinProperty(cols, val_range=val_range, immediate=True)
        self.vgap = np.SpinProperty(vgap, immediate=True)
        self.hgap = np.SpinProperty(hgap, immediate=True)

    def create_widget(self):
        "This must be overriden and called at the end of the overriden version"
        to_lay_out = []
        for c in self.children:
            c.create()
            if isinstance(c, SizerSlot):
                self.widget.Add(c.widget, 1, wx.EXPAND)
                self.widget.SetItemMinSize(c.widget, 20, 20)
            else:
                sp = c.properties.get('size')
                if sp and sp.is_active():
                    if (c.proportion != 0 or (c.flag & wx.EXPAND)) and not (c.flag & wx.FIXED_MINSIZE):
                        c.widget.Layout()
                        size = sp.get_size(c.widget)
                        c.widget.SetMinSize(size)
                    else:
                        size = sp.get_size(c.widget)
                        # now re-set the item to update the size correctly...
                        to_lay_out.append( (c.pos, size) )

        for pos, size in to_lay_out:
            self.set_item_best_size(self.children[pos], size=size, force_layout=False)
        self.layout(True)

    def fit_parent(self, *args):
        "Tell the sizer to resize the window to match the sizer's minimal size"
        if self.widget and self.window.widget:
            self.widget.Fit(self.window.widget)
            self.widget.SetSizeHints(self.window.widget)

    def _can_add_insert_slots(self, report=False):
        if self.rows and self.cols and len(self.children)==self.rows*self.cols:
            # if both are defined, a re-sizing would need to be done
            if report:
                misc.error_message("Can't add or insert slots as sizer's Rows and Cols are fixed (see Properties -> Grid).")
            return False
        return True

    # helpers ##########################################################################################################
    def _get_actual_rows_cols(self):
        rows = self.rows
        cols = self.cols
        # for GridSizer and FlexGridSizer cols may be 0, i.e. auto calculated
        if cols==0:    cols = (len(self.children)-1)//rows + 1
        elif rows==0:  rows = (len(self.children)-1)//cols + 1
        return rows, cols
    def _get_row_col(self, pos, cols=None):
        if cols is None:
            rows, cols = self._get_actual_rows_cols()
        return pos // cols,  pos %  cols

    def _get_pos(self, row, col):
        rows, cols = self._get_actual_rows_cols()
        return row*cols + col

    def _adjust_rows_cols(self, loading=False):
        # called when items are added or removed: adjust number of rows
        cols_p = self.properties["cols"]
        rows_p = self.properties["rows"]
        if rows_p.value==0 or cols_p.value==0: return
        rows_new = (len(self.children)-1) // cols_p.get() + 1
        if rows_new==rows_p.value or (loading and rows_new<rows_p.value): return
        rows_p.set(rows_new)

    # context menu actions #############################################################################################
    @_frozen
    def insert_row(self, pos=-1):
        "inserts slots for a new row"
        rows, cols = self._get_actual_rows_cols()

        # calculate the row (0 based) to be inserted
        if pos==-1:
            add_row = rows
            # ensure that the last row is full
            for n in range( rows*cols - len(self.children) ):
                self._insert_slot( len(self.children) )
        else:
            add_row, dummy = self._get_row_col(pos)

        if rows:
            self.properties["rows"].set( rows+1 )
            if self.widget: self.widget.SetRows(rows+1)

        for n in range(cols):
            self._insert_slot( n + add_row*cols )

        if "growable_rows" in self.PROPERTIES:
            self.properties["growable_rows"].shift_items(add_row)

        if self.widget:
            if "growable_rows" in self.PROPERTIES:
                self._set_growable()
            self.layout(True)
        misc.rebuild_tree(self)

    @_frozen
    def insert_col(self, pos=-1):
        "inserts slots for a new column"
        rows, cols = self._get_actual_rows_cols()

        # calculate the column (0 based) to be added
        if pos==-1:
            add_col = cols
        else:
            dummy, add_col = self._get_row_col(pos)

        # calculate the column index of the last child (0 based)
        last_pos = len(self.children)
        last_pos_col = (last_pos % cols) - 1
        if last_pos_col == -1: last_pos_col = cols-1
        # fill up the last row up to the insertion position if required
        if last_pos_col < min(add_col,cols-1):
            for i in range(min(add_col,cols-1)-last_pos_col):
                self._insert_slot( last_pos+i )

        # insert the new colum
        if self.cols:
            self.properties["cols"].set( cols+1 )
            if self.widget: self.widget.SetCols(cols+1)
        # insert placeholders to avoid problems with GridBagSizers and overlap tests
        for r in range(rows-1,-1,-1):
            #self.children.insert( add_col+1 + r*cols, None )
            self.children.insert( add_col + r*cols, None )
        # actually create the slots
        for r in range(0,rows):
            self._insert_slot( self._get_pos(r,add_col) )

        if "growable_cols" in self.PROPERTIES:
            self.properties["growable_cols"].shift_items(add_col)

        if self.widget:
            if self.widget.GetCols()!=cols+1: self.widget.SetCols(cols+1)
            if "growable_rows" in self.PROPERTIES:
                self._set_growable()
            self.layout(True)
        misc.rebuild_tree(self)

    @_frozen
    def remove_row(self, pos):
        rows = self.rows
        cols = self.cols
        # calculate row and pos of the slot
        row,col = self._get_row_col(pos)
        # find the slots that are in the same row
        slots = []
        for pos,child in enumerate(self.children):
            child_row, child_col = self._get_row_col(pos)
            if child_row==row: slots.append(child)
        if rows: self.properties["rows"].set( rows-1 )
        # actually remove the slots
        for slot in reversed(slots): slot.remove()
        
        if "growable_rows" in self.PROPERTIES:
            self.properties["growable_rows"].remove_item(row)

        if self.widget:
            if "growable_rows" in self.PROPERTIES:
                self._set_growable()
            if self.rows: self.widget.SetRows(self.rows)
            self.layout(True)
        misc.rebuild_tree(self)

    @_frozen
    def remove_col(self, pos):
        cols = self.cols
        # calculate row and pos of the slot
        row,col = self._get_row_col(pos)
        # find the slots that are in the same row
        slots = []
        for pos,child in enumerate(self.children):
            child_row, child_col = self._get_row_col(pos)
            if child_col==col: slots.append(child)
        if cols: self.properties["cols"].set( cols-1 )
        # actually remove the slots
        for slot in reversed(slots): slot.remove()

        if "growable_cols" in self.PROPERTIES:
            self.properties["growable_cols"].remove_item(col)

        if self.widget:
            if not self._IS_GRIDBAG:
                self.widget.SetCols(cols-1)
            if "growable_cols" in self.PROPERTIES:
                self._set_growable()
            if self.cols: self.widget.SetCols(self.cols)
            self.layout(True)
        misc.rebuild_tree(self)

    ####################################################################################################################
    @_frozen
    def properties_changed(self, modified):
        rows, cols = self._get_actual_rows_cols()
        if rows*cols < len(self.children):
            # number of rows/cols too low; this is not called if rows or col==0
            if not modified or "cols" in modified:
                # adjust number of rows if required
                if rows*cols < len(self.children):
                    # more rows required
                    rows = len(self.children) // (cols or 1)
                    if len(self.children) % (cols or 1): rows += 1
                self.properties["rows"].set(rows)
                if modified and not "rows" in modified: modified.append("rows")
            elif "rows" in modified:
                cols = len(self.children) // (rows or 1)
                if len(self.children) % (rows or 1): cols += 1
                self.properties["cols"].set(cols)
                if modified and not "cols" in modified: modified.append("cols")

        if self.WX_CLASS != "wxGridBagSizer":
            if self.rows==0:
                self.properties["cols"].set_range(1,1000)
            else:
                self.properties["cols"].set_range(0,1000)
            if self.cols==0:
                self.properties["rows"].set_range(1,1000)
            elif self.WX_CLASS != "wxGridBagSizer":
                self.properties["rows"].set_range(0,1000)

        layout = False

        if not "class_orient" in modified:  # otherwise, change_sizer will be called and we can skip the following
            if not modified or "rows" in modified and self.widget:
                if self.widget.GetRows()!=self.rows:
                    self.widget.SetRows(self.rows)
                    layout = True
            if not modified or "cols" in modified and self.widget:
                if self.widget.GetCols()!=self.cols:
                    self.widget.SetCols(self.cols)
                    layout = True
            if not modified or "hgap" in modified and self.widget:
                if self.widget.GetHGap()!=self.hgap:
                    self.widget.SetHGap(self.hgap)
                    layout = True
            if not modified or "vgap" in modified and self.widget:
                if self.widget.GetVGap()!=self.vgap:
                    self.widget.SetVGap(self.vgap)
                    layout = True

        if "growable_rows" in self.properties and self.widget:
            if not modified or "growable_rows" in modified or "growable_cols" in modified:
                self._set_growable()
                layout = True

        if layout:
            self.layout(True)
            if self.widget: self.window.widget.Refresh()

        SizerBase.properties_changed(self, modified)


class EditGridSizer(GridSizerBase):
    "Class to handle wxGridSizer objects"
    WX_CLASS = "wxGridSizer"

    def __init__(self, name, parent, pos, rows=3, cols=3, vgap=0, hgap=0):
        GridSizerBase.__init__(self, name, 'wxGridSizer', parent, pos, rows, cols, vgap, hgap)

    def create_widget(self, dont_add=False):
        self.widget = CustomGridSizer(self, self.rows, self.cols, self.vgap, self.hgap)
        if self.parent.IS_SIZER and not dont_add:
            self.sizer.add_item(self, self.pos) # , self.widget.GetMinSize())
        GridSizerBase.create_widget(self)


class _GrowableDialog(wx.Dialog):
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, -1, title)
        self.sizer = sizer = wx.BoxSizer(wx.VERTICAL)
        self.message = wx.StaticText(self, -1, "")
        sizer.Add(self.message, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        self.choices = wx.CheckListBox(self, -1, choices=[])
        sizer.Add(self.choices, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 10)
        sz2 = wx.BoxSizer(wx.HORIZONTAL)
        sz2.Add(wx.Button(self, wx.ID_OK, ""), 0, wx.ALL, 10)
        sz2.Add(wx.Button(self, wx.ID_CANCEL, ""), 0, wx.ALL, 10)
        sizer.Add(sz2, 0, wx.ALIGN_CENTER)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.CenterOnScreen()

    def get_value(self):
        ret = []
        for c,choice in enumerate(self._choices):
            #in range(self.choices.GetCount()):
            if self.choices.IsChecked(c):
                ret.append(str(int(choice)-1))
        return ",".join(ret)

    def set_choices(self, choices, values):
        self.choices.Set(choices)
        self._choices = choices
        for i,value in enumerate(choices):
            if value in values: self.choices.Check(i)

    def set_descriptions(self, title, message):
        self.SetTitle(title)
        self.message.SetLabel(message)



class _GrowablePropertyD(np.DialogPropertyD):
    def _create_dialog(self):
        if self.dialog is None:
            parent = self.text.GetTopLevelParent()
            self.dialog = _GrowableDialog(parent, self.title)

        rows, cols = self.owner._get_actual_rows_cols()
        row_or_col_count = rows  if "rows" in self.name else  cols

        choices = [ str(n)   for n in range(1, row_or_col_count+1) ]  # dialog is 1 based
        selected = [str(n+1) for n in self.value]
        self.dialog.set_choices(choices, selected)
        self.dialog.sizer.Fit(self.dialog)
        return self.dialog

    def _set_converter(self, value):
        # used by set()
        if isinstance(value, compat.basestring):
            try:
                value = sorted( [int(n) for n in value.split(",") ] )
            except:
                return None
        return value

    def _convert_from_text(self, text=None):
        if text is None: text = self.text.GetValue()
        row_or_col_count = getattr(self.owner, self.name.split("_")[-1])
        try:
            value = [int(n)-1 for n in text.split(",")]  # text is 1-based, value is 0-based
            value.sort()
            if len(value)!=len(set(value)):  return None                 # double numbers
            if value and not row_or_col_count: return None                 # no rows/cols
            if min(value)<0 or max(value)>=row_or_col_count: return None  # number out of range
        except:
            return None
        return value

    def _convert_to_text(self, value):
        # from internal 0-based string value to text control 1-based: "0,1" -> "1,2"
        ret = [str(n+1) for n in self.value]
        return ",".join(ret)

    def get_string_value(self):
        # for XML file writing
        return ",".join( [str(n) for n in self.value] )

    def remove_item(self, item):
        # called when a column is deleted
        if not self.value: return
        new = []
        for n in self.value:
            if n!=item:
                if n<item:
                    new.append(n)
                else:
                    new.append(n-1)
        deactivate = not new
        self.set( new, deactivate=deactivate )

    def shift_items(self, item):
        # when a row/col is added, the values above need to be shifted by 1
        if not self.value: return
        new = []
        for n in self.value:
            if n<item:
                new.append(n)
            else:
                new.append(n+1)
        self.set( new )

    def keep_items(self, indices):
        if not self.value: return
        new = [indices.index(n) for n in self.value if n in indices]
        self.set( new )


class EditFlexGridSizer(GridSizerBase):
    "Class to handle wxFlexGridSizer objects"
    WX_CLASS = "wxFlexGridSizer"

    EXTRA_PROPERTIES = GridSizerBase.EXTRA_PROPERTIES + ["growable_rows", "growable_cols"]
    _PROPERTY_HELP = {"growable_rows":'Select growable rows',
                      "growable_cols":'Select growable columns'}

    def __init__(self, name, parent, pos, rows=3, cols=3, vgap=0, hgap=0):
        GridSizerBase.__init__(self, name, self.WX_CLASS, parent, pos, rows, cols, vgap, hgap)
        self.growable_rows = _GrowablePropertyD([], default_value=[])
        self.growable_cols = _GrowablePropertyD([], default_value=[])
        self.properties["growable_rows"].title = 'Select growable rows'
        self.properties["growable_cols"].title = 'Select growable cols'

    def create_widget(self, dont_add=False):
        self.widget = CustomFlexGridSizer(self, self.rows, self.cols, self.vgap, self.hgap)
        GridSizerBase.create_widget(self)
        self._set_growable()
        if self.parent.IS_SIZER and not dont_add:
            self.parent._add_item(self, self.pos)

    def _set_growable(self):
        rows = self.growable_rows
        cols = self.growable_cols
        rowcount,colcount = self._get_actual_rows_cols()
        for r in range(rowcount):
            growable = self.widget.IsRowGrowable(r)
            if growable and not r in rows:
                self.widget.RemoveGrowableRow(r)
            elif not growable and r in rows:
                self.widget.AddGrowableRow(r)
        for c in range(colcount):
            growable = self.widget.IsColGrowable(c)
            if growable and not c in cols:
                self.widget.RemoveGrowableCol(c)
            elif not growable and c in cols:
                self.widget.AddGrowableCol(c)

    @_frozen
    def make_growable(self, direction, row_or_col):
        "set growable_rows or growable_cols"
        p_name = "growable_%ss"%direction
        p = self.properties[p_name]
        if row_or_col in p.value:
            p.value.remove(row_or_col)
        else:
            p.value.append(row_or_col)
            p.value.sort()
        p.set_active(bool(p.value))
        self.properties_changed([p_name])
        p.update_display()

    def ask_growable(self, row, col):
        "ask user whether to make a row or col growable when the user has selected EXPAND without a growable row or col"
        import dialogs
        dlg = dialogs.MakeRowColGrowableDlg(common.main)
        usr = dlg.ShowModal()
        if usr != wx.ID_OK: return
        changed = []
        # we can be sure that row and col are not in the property values
        if dlg.cb_row_growable.GetValue():
            p = self.properties["growable_rows"]
            p.set(sorted(p.value+[row]), activate=True)
            changed.append("growable_rows")
        if dlg.cb_col_growable.GetValue():
            p = self.properties["growable_cols"]
            p.set(sorted(p.value+[col]), activate=True)
            changed.append("growable_cols")

        dont_show_again = dlg.cb_dont_show_again.GetValue()
        if changed: self.properties_changed(changed)


class EditGridBagSizer(EditFlexGridSizer):
    "Class to handle wxFlexGridSizer objects"
    WX_CLASS = "wxGridBagSizer"
    _IS_GRIDBAG = True
    _PROPERTY_HELP = {"rows":"Numbers of sizer rows; this is just used internally for wxGlade design, not by wx",
                      "cols":"Numbers of sizer columns; this is just used internally for wxGlade design, not by wx"}

    def create_widget(self, dont_add=False):  # this one does not call GridSizerBase.create_widget, as the strategy here is different
        self.widget = CustomGridBagSizer(self, self.rows, self.cols, self.vgap, self.hgap)
        #GridSizerBase.create_widget(self)
        ################################################################################################################
        
        to_lay_out = []
        for child in self.children:
            pos = self._get_row_col(child.pos)
            child.create()
            if isinstance(child, SizerSlot) and child.widget:
                self.widget.Add(child.widget, pos, (1,1), wx.EXPAND, 0)
                self.widget.SetItemMinSize(child.widget, 20, 20)
            else:
                sp = child.properties.get('size')
                if sp and sp.is_active():
                    if (child.proportion != 0 or (child.flag & wx.EXPAND)) and not (child.flag & wx.FIXED_MINSIZE):
                        child.widget.Layout()
                        w, h = child.widget.GetBestSize()
                        child.widget.SetMinSize((w, h))
                    else:
                        size = sp.get_size(child.widget)
                        to_lay_out.append((child.pos, size))  # re-set the item to update the size correctly...

        for pos, size in to_lay_out:
            self.set_item_best_size(self.children[pos], size)
        self.layout(True)
        ################################################################################################################
        self._set_growable()
        if self.parent.IS_SIZER and not dont_add:
            self.parent._add_item(self, self.pos)

    def check_span_range(self, pos, rowspan=1, colspan=1, inserting=False):
        "called from LayoutSpanProperty to set the maximum row/col span range"
        row, col = self._get_row_col(pos)
        # check max colspan
        max_col = col
        for c in range(col+1, self.cols):
            for r in range(row, row+rowspan):
                # check cell content
                p = self._get_pos(r,c)
                if p>=len(self.children):
                    #max_col = c
                    max_col = self.cols-1
                    break
                child = self.children[p]
                if not isinstance(child, SizerSlot): break
                if inserting and child.overlapped: break
            if p>=len(self.children) or not isinstance(child, SizerSlot): break
            if inserting and child.overlapped: break
            # only empty cells found
            max_col = c
        # check max rowspan
        max_row = row
        for r in range(row+1, self.rows):
            for c in range(col, col+colspan):
                # check cell content
                p = self._get_pos(r,c)
                if p>=len(self.children):
                    #max_row = r
                    max_row = self.rows-1
                    break
                child = self.children[p]
                if not isinstance(child, SizerSlot): break
                if inserting and child.overlapped: break
            if p>=len(self.children) or not isinstance(child, SizerSlot): break
            if inserting and child.overlapped: break
            # only empty cells found
            max_row = r
        return max_row-row+1, max_col-col+1

    def _get_occupied_slots(self):
        "get pos for all slots that are SizerSlots only, but are occupied by other items spanning over rows/cols"
        pos = 0
        occupied = []
        rows, cols = self._get_actual_rows_cols()
        for row in range(rows):
            for col in range(cols):
                if pos==len(self.children): break
                child = self.children[pos]
                if not isinstance(child, SizerSlot) and not child is None:
                    # an element, check whether it spans over any slots
                    span = child.span
                    if span != (1,1):
                        for r in range(row, row+span[0]):
                            for c in range(col, col+span[1]):
                                if r==row and c ==col: continue  # the original cell
                                if c>=self.cols: continue
                                occupied.append( self._get_pos(r,c) )
                pos += 1
            if pos==len(self.children): break
        return occupied

    def _get_max_row_col(self):
        "get last row and col indices that are populated or spanned; for use by rows/cols properties"
        max_row = max_col = 0
        for pos, child in enumerate(self.children):
            row, col = self._get_row_col(pos)
            if not isinstance(child, SizerSlot) and not child is None:
                span = child.span
                max_row = max( max_row, row + span[0] - 1 )
                max_col = max( max_col, col + span[1] - 1 )
        return max_row, max_col

    def _check_slots(self, remove_only=False, add_only=False, add_to_sizer=True):
        "add/remove the widgets for empty slots"
        occupied = set( self._get_occupied_slots() )
        for pos,child in enumerate(self.children):
            if isinstance(child, SizerSlot):
                if pos in occupied:
                    if not add_only: child.set_overlap(True, add_to_sizer=add_to_sizer)
                else:
                    if not remove_only: child.set_overlap(False, add_to_sizer=add_to_sizer)

    def get_child_index(self, pos):
        # return the index of the widget; overlapped slots are skipped
        ret = 0
        for p, child in enumerate(self.children):
            if child is None or (child.IS_SLOT and child.overlapped): continue
            if p==pos: return ret
            ret += 1

    def _can_add_insert_slots(self, report=False):
        if report:
            misc.error_message("Can't insert or add slots as sizer's Rows and Cols are fixed (see Properties -> Grid).")
        return False

    def get_child_index(self, pos):
        # return the index of the widget; overlapped slots are skipped
        ret = 0
        for p, child in enumerate(self.children):
            if child is None or (isinstance(child, SizerSlot) and child.overlapped): continue
            if p==pos: return ret
            ret += 1

    # context menu actions #############################################################################################
    @_frozen  # if _frozen is used, this should be called via wx.CallAfter
    def _recreate(self, rows, cols, previous_rows, previous_cols):
        "rows, cols: list of indices to keep or None for new rows/cols"
        if rows is None: rows = [r if r<previous_rows else None  for r in range(self.rows)]
        if cols is None: cols = [c if c<previous_cols else None  for c in range(self.cols)]
        remove_slots = [] # as of now, only slots are being removed
        remove_rows = [r for r in range(previous_rows) if not r in rows]
        remove_cols = [c for c in range(previous_cols) if not c in rows]
        new_children = [[None]*len(cols) for row in range(len(rows))]
        # detach all elements from old sizer
        for pos, child in enumerate(self.children):
            r,c = self._get_row_col(pos, previous_cols)
            if r not in rows or c not in cols:
                remove_slots.append(child)
                if child.widget:
                    self.widget.Detach(child.widget)
                continue
            new_children[rows.index(r)][cols.index(c)] = child

            if child.widget:
                self.widget.Detach(child.widget)

            # check whether an item is spanning over the removed row/col and reduce span by 1
            span = child.span
            r_end = r+span[0]-1
            c_end = c+span[1]-1
            spanned_rows = [r_ for r_ in range(r,r_end+1) if r_ in rows]
            spanned_cols = [c_ for c_ in range(c,c_end+1) if c_ in cols]
            new_span = (rows.index( spanned_rows[-1] ) - rows.index(r) + 1,
                        cols.index( spanned_cols[-1] ) - cols.index(c) + 1)
            if new_span != span:
                child.properties["span"].set( new_span )

        # remove the slots, if required
        set_focus = misc.focused_widget in remove_slots
        for slot in reversed(remove_slots): slot._remove()
        if set_focus:
            misc.set_focused_widget(self)

        self.properties["rows"].set( len(rows) )
        self.properties["growable_rows"].keep_items(rows)  # 1 based
        self.properties["cols"].set( len(cols) )
        self.properties["growable_cols"].keep_items(cols)

        # insert placeholders to avoid problems with GridBagSizers and overlap tests
        self.children[:] = sum(new_children,[])
        # actually create the new slots
        for pos, child in enumerate(self.children):
            if child is not None: continue
            self._insert_slot( pos, select=False, no_add=True )

        # check overlapped slots
        self._check_slots(add_to_sizer=False)

        if not self.widget: return
        # re-create the widget and add the items
        for c in self.widget._grid.GetChildren():
            if c and c.IsSizer():
                compat.SizerItem_SetSizer(c, None)

        self.widget._grid.Clear()
        #self.widget._grid.Destroy()  # spurious crashes, even with CallAfter
        self.widget._create(None,None, self.vgap, self.hgap)
        wx.BoxSizer.Add(self.widget, self.widget._grid, 1, wx.EXPAND)

        for child in self.children:
            if not child.widget: continue # for overlapped sizer slots, widget may be None
            self.widget.Add(child.widget, child.pos, child.span, child.flag, child.border)

        self._set_growable()
        self.layout(True)
        misc.rebuild_tree(self)

    def remove_row(self, pos):
        row,col = self._get_row_col(pos)
        rows = [r for r in range(self.rows) if r!=row]
        self._recreate(rows, None, self.rows, self.cols)

    def remove_col(self, pos):
        row,col = self._get_row_col(pos)
        cols = [c for c in range(self.cols) if c!=col]
        self._recreate(None, cols, self.rows, self.cols)

    def insert_row(self, pos=-1):
        row,col = self._get_row_col(pos)
        rows = [r for r in range(self.rows)]
        if pos==-1:
            rows.append(None)
        else:
            rows.insert(row, None)
        self._recreate(rows, None, self.rows, self.cols)

    def insert_col(self, pos=-1):
        row,col = self._get_row_col(pos)
        cols = [c for c in range(self.cols)]
        if pos==-1:
            cols.append(None)
        else:
            cols.insert(col, None)
        self._recreate(None, cols, self.rows, self.cols)

    def _set_row_col_range(self):
        "set ranges of rows/cols properties"
        max_row, max_col = self._get_max_row_col()
        rows_p = self.properties["rows"]
        cols_p = self.properties["cols"]
        rows_p.set_range(max_row+1, rows_p.val_range[1])
        cols_p.set_range(max_col+1, cols_p.val_range[1])
    
    def check_property_modification(self, name, value, new_value):
        max_row, max_col = self._get_max_row_col()
        if name=="rows" and new_value<max_row+1: return False
        if name=="cols" and new_value<max_col+1: return False
        return EditFlexGridSizer.check_property_modification(self, name, value, new_value)

    def properties_changed(self, modified):
        if modified and ("rows" in modified or "cols" in modified):
            rows_p = self.properties["rows"]
            cols_p = self.properties["cols"]
            if rows_p.previous_value is not None or cols_p.previous_value is not None:
                # actually a user input
                rows = cols = None # default arguments
                if "rows" in modified:
                    previous_rows = rows_p.previous_value
                    previous_cols = self.cols
                    if previous_rows<rows_p.value:
                        # add rows
                        rows = list(range(previous_rows)) + [None]*(rows_p.value-previous_rows)
                    else:
                        # remove rows
                        rows = list(range(rows_p.value))
                if "cols" in modified:
                    previous_rows = self.rows
                    previous_cols = cols_p.previous_value
                    if previous_cols<cols_p.value:
                        # add cols
                        cols = list(range(previous_cols)) + [None]*(cols_p.value-previous_cols)
                    else:
                        # remove cols
                        cols = list(range(cols_p.value))
                self._recreate(rows, cols, previous_rows, previous_cols)
                return

        EditFlexGridSizer.properties_changed(self, modified)

    def on_load(self, child=None):
        # called from XML parser right after loading the widget or when pasting an item into a slot
        # ensure that rows/cols is not 0; this is actually an error in the file
        rows = self.rows
        cols = self.cols
        if rows==0: self.properties["rows"].set( (len(self.children)-1)//cols +1 )
        if cols==0: self.properties["cols"].set( (len(self.children)-1)//rows +1 )

        if child is not None:
            # an item is being pasted into a slot; we might need to limit the spanning
            span_p = child.properties["span"]
            if span_p.value != (1,1):
                # check whether spanning is OK or needs to be reduced
                span = span_p.value
                max_span = self.check_span_range(child.pos, *span, inserting=True)
                new_span = (min(span[0], max_span[0]), min(span[1], max_span[1]))
                if new_span != span: span_p.set(new_span)

        self._check_slots(remove_only=True)
        EditFlexGridSizer.on_load(self, child)


def change_sizer(old, new):
    """Replaces sizer instance 'old' with a new one; 'new' is the name of the new one.
    (which_page: index of the property windows notebook page; used only by set_growable_(rows|cols)"""
    pos = 0 if old.toplevel else old.pos
    constructors = {
        'wxBoxSizer (wxVERTICAL)':         lambda: EditBoxSizer(old.name, old.parent, pos, wx.VERTICAL, 0),
        'wxBoxSizer (wxHORIZONTAL)':       lambda: EditBoxSizer(old.name, old.parent, pos, wx.HORIZONTAL, 0),
        'wxWrapSizer (wxVERTICAL)':        lambda: EditWrapSizer(old.name, old.parent, pos, wx.VERTICAL, 0),
        'wxWrapSizer (wxHORIZONTAL)':      lambda: EditWrapSizer(old.name, old.parent, pos, wx.HORIZONTAL, 0),
        'wxStaticBoxSizer (wxVERTICAL)':   lambda: EditStaticBoxSizer(old.name, old.parent, pos, wx.VERTICAL,
                                                                      getattr(old, 'label', old.name), 0),
        'wxStaticBoxSizer (wxHORIZONTAL)': lambda: EditStaticBoxSizer(old.name, old.parent, pos, wx.HORIZONTAL,
                                                                      getattr(old, 'label', old.name), 0),
        'wxStdDialogButtonSizer':          lambda: EditStdDialogButtonSizer(old.name, old.parent, pos, 0),
        'wxGridSizer':     lambda: EditGridSizer(old.name, old.parent, pos, rows=0, cols=0),
        'wxFlexGridSizer': lambda: EditFlexGridSizer(old.name, old.parent, pos, rows=0, cols=0),
        'wxGridBagSizer': lambda: EditGridBagSizer(old.name, old.parent, pos, rows=0, cols=0) }

    with old.window.frozen():
        # construct without children, take then the children from the old sizer
        old.parent.children[pos] = None  # avoid recursive_remove being called
        szr = constructors[new]()
        if old._IS_GRIDBAG and old.widget:
            for c in old.children:
                if c:
                    if c.widget:
                        old.widget.Detach(c.widget)
                    elif isinstance(c, SizerSlot) and c.overlapped:
                        # re-create hidden widget
                        c.set_overlap(False, add_to_sizer=False)

        szr.children.extend(old.children)

        # copy/set properties
        if isinstance(szr, GridSizerBase):
            # take rows, cols, hgap, vgap from old sizer, if applicable
            rows = getattr(old, "rows", 1)
            cols = getattr(old, "cols", len(szr.children))
            if isinstance(szr, EditGridBagSizer):
                # for GridSizer and FlexGridSizer cols may be 0, i.e. auto calculated
                if rows==0: rows = (len(szr.children)-1)//cols +1
                if cols==0: cols = (len(szr.children)-1)//rows +1

            szr.properties["rows"].set( rows )
            szr.properties["cols"].set( cols )
            szr.properties["hgap"].set( getattr(old, "hgap", 0) )
            szr.properties["vgap"].set( getattr(old, "vgap", 0) )
            szr.properties_changed( ["rows","cols","hgap","vgap"] )
        if isinstance(szr, EditFlexGridSizer) and isinstance(old, EditFlexGridSizer):
            # take growable rows and cols from old sizer
            grow_r_p = old.properties["growable_rows"]
            grow_c_p = old.properties["growable_cols"]
            if grow_r_p.is_active():
                szr.properties['growable_rows'].value = grow_r_p.value
                szr.properties['growable_rows'].deactivated = False
            if grow_c_p.is_active():
                szr.properties['growable_cols'].value = grow_c_p.value
                szr.properties['growable_cols'].deactivated = False
        # XXX keep rows, cols, growable_rows, growable_cols in attributes of new sizer if it's not a (Flex)GridSizer
        #     and re-use them if user switches back

        if szr._IS_GRIDBAG:
            szr._check_slots(remove_only=True)  # for the children, .parent is still the old sizer here

        for widget in szr.children:
            widget.parent = szr

        if old.widget is not None:
            for c in old.widget.GetChildren():
                if c and c.IsSizer():
                    compat.SizerItem_SetSizer(c, None)
            old.widget.Clear()  # without deleting window items; but sets the sizer of the windows to NULL

            szr.create(dont_set=True)

        for widget in szr.children:
            if not isinstance(widget, SizerSlot):
                if szr.widget is not None:
                    if not isinstance(szr, EditGridBagSizer):
                        pos = widget.pos + szr.widget._BTN_OFFSET
                        szr.widget.Insert(pos, widget.widget, widget.proportion, widget.flag, widget.border)
                    else:
                        szr.widget.Add(widget.widget, widget.pos, widget.span, widget.flag, widget.border)
    
        if szr.parent.IS_SIZER:
            szr.copy_properties(old, szr.MANAGED_PROPERTIES, notify=False)  # "pos","span","proportion","border","flag"
            szr.sizer.children[szr.pos] = szr
            if szr.sizer.widget:
                pos = szr.sizer.widget._BTN_OFFSET + szr.sizer.get_child_index(szr.pos)
                elem = szr.sizer.widget.GetChildren()[pos]
                compat.SizerItem_SetSizer(elem, szr.widget)

        common.app_tree.change_item_editor(old, szr, keep_children=True)

        old.toplevel = False  # could probably be omitted
        del old.children[:]
        old.delete()

        for c in szr.children:
            if c: c.parent = szr
        if not szr.parent.IS_SIZER:
            szr.window.set_sizer(szr)

        szr.layout(True)
        if szr.widget: szr.window.widget.Refresh()

        misc.set_focused_widget(szr)


def _builder(parent, pos, orientation=wx.VERTICAL, slots=1, is_static=False, label="", is_wrap=False):
    name = parent.toplevel_parent.get_next_contained_name('sizer_%d')

    # add slots later
    if orientation=="StdDialogButtonSizer":
        editor = EditStdDialogButtonSizer(name, parent, pos, 0)
    elif is_static:
        editor = EditStaticBoxSizer(name, parent, pos, orientation, label, 0)
    elif is_wrap:
        editor = EditWrapSizer(name, parent, pos, orientation, 0)
    else:
        editor = EditBoxSizer(name, parent, pos, orientation, 0)

    if parent.IS_SIZER:
        if orientation=="StdDialogButtonSizer":
            editor.properties['proportion'].set(0)
            editor.properties['flag'].set('wxALIGN_RIGHT')
        else:
            editor.properties['flag'].set('wxEXPAND')
        editor.properties['pos'].set(pos)

    # add the slots
    for i in range(slots):
        editor._add_slot()
    editor.layout()

    if parent.widget: editor.create()
    return editor


class _SizerDialog(wx.Dialog):
    def __init__(self, parent):
        pos = wx.GetMousePosition()
        wx.Dialog.__init__( self, misc.get_toplevel_parent(parent), -1, _('Select sizer type'), pos )
        choices = [_('Horizontal'), _('Vertical'), 'StdDialogButtonSizer']
        self.orientation = wx.RadioBox( self, -1, _('Orientation'), choices=choices )
        self.orientation.SetSelection(0)
        self.orientation.Bind(wx.EVT_RADIOBOX, self.on_choice_orientation)
        tmp = wx.BoxSizer(wx.HORIZONTAL)
        tmp.Add( wx.StaticText(self, -1, _('Slots: ')), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3 )
        self.num = wx.SpinCtrl(self, -1)
        self.num.SetRange(1, 100)
        self.num.SetValue(1)
        tmp.Add(self.num, 1, wx.ALL, 3)
        szr = wx.BoxSizer(wx.VERTICAL)
        szr.Add(self.orientation, 0, wx.ALL | wx.EXPAND, 4)
        szr.Add(tmp, 0, wx.EXPAND)
        self.checkbox_static = wx.CheckBox(self, -1, _('Has a Static Box:'))
        compat.SetToolTip(self.checkbox_static, "Use wxStaticBoxSizer")
        self.label = wx.TextCtrl(self, -1, "")
        self.label.Enable(False)
        self.checkbox_static.Bind(wx.EVT_CHECKBOX, self.on_check_statbox)
        szr.Add(self.checkbox_static, 0, wx.ALL | wx.EXPAND, 4)
        tmp = wx.BoxSizer(wx.HORIZONTAL)
        tmp.Add(wx.StaticText(self, -1, _("Label: ")), 0, wx.ALIGN_CENTER)
        tmp.Add(self.label, 1)
        szr.Add(tmp, 0, wx.ALL | wx.EXPAND, 4)

        if HAVE_WRAP_SIZER:
            self.checkbox_wrap = wx.CheckBox(self, -1, _('Wraps around'))
            compat.SetToolTip(self.checkbox_wrap, "Use wxWrapSizer")
            self.checkbox_wrap.Bind(wx.EVT_CHECKBOX, self.on_check_wrapbox)
            szr.Add(self.checkbox_wrap, 0, wx.ALL | wx.EXPAND, 4)

        # horizontal sizer for action buttons
        #hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer = wx.StdDialogButtonSizer()
        hsizer.Add( wx.Button(self, wx.ID_CANCEL, _('Cancel')), 1, wx.ALL, 5)
        btn = wx.Button(self, wx.ID_OK, _('OK'))
        btn.SetDefault()
        hsizer.Add(btn, 1, wx.ALL, 5)
        szr.Add(hsizer, 0, wx.EXPAND|wx.ALIGN_CENTER )
        self.SetAutoLayout(1)
        self.SetSizer(szr)
        szr.Fit(self)
        self.Layout()
        #self.CenterOnScreen()

    def reset(self):
        self.orientation.SetSelection(0)
        self.num.SetValue(1)
        self.checkbox_static.SetValue(0)
        self.label.SetValue("")
        self.label.Enable(False)
        if HAVE_WRAP_SIZER:
            self.checkbox_wrap.SetValue(0)
    
    def on_choice_orientation(self, event):
        choice = event.GetSelection()
        self.checkbox_wrap.Enable( choice<2 )
        self.checkbox_static.Enable( choice<2 and not self.checkbox_wrap.IsChecked() )
        self.label.Enable( choice<2 and self.checkbox_static.IsChecked() )
        if choice==2 and self.num.Value<2:
            self.num.SetValue(2)

    def on_check_statbox(self, event):
        checked = event.IsChecked()
        self.label.Enable(checked)
        if HAVE_WRAP_SIZER:
            self.checkbox_wrap.Enable(not checked)
            if checked: self.checkbox_wrap.SetValue(False)

    def on_check_wrapbox(self, event):
        checked = event.IsChecked()
        self.checkbox_static.Enable(not checked)
        if checked:
            self.checkbox_static.SetValue(False)
            self.label.Disable()


def builder(parent, pos):
    "factory function for box sizers"

    dialog = _SizerDialog(common.adding_window or parent)
    with misc.disable_stay_on_top(common.adding_window or parent):
        res = dialog.ShowModal()
    choice = dialog.orientation.GetSelection()  # 0, 1 or 2
    if choice==0:
        orientation = wx.HORIZONTAL
    elif choice==1:
        orientation = wx.VERTICAL
    else:
        orientation = "StdDialogButtonSizer"

    num = dialog.num.GetValue()
    wrap = HAVE_WRAP_SIZER and dialog.checkbox_wrap.GetValue() or False
    label = dialog.label.GetValue()
    static = dialog.checkbox_static.GetValue()

    dialog.Destroy()
    if res != wx.ID_OK: return
    with parent.frozen():
        editor = _builder( parent, pos, orientation, num, static, label, wrap )

    return editor


def xml_builder(attrs, parent, pos=None):
    "factory function to build EditBoxSizer objects from a XML file"
    from xml_parse import XmlParsingError

    try:
        name = attrs['name']
    except KeyError:
        raise XmlParsingError( _("'name' attribute missing") )
    orientation = wx.VERTICAL  # default value
    if attrs['base'] == 'EditStaticBoxSizer':
        return EditStaticBoxSizer(name, parent, pos, orientation, '', 0)
    if attrs['base'] == 'EditWrapSizer':
        return EditWrapSizer(name, parent, pos, orientation, 0)
    if attrs['base'] == 'EditStdDialogButtonSizer':
        return EditStdDialogButtonSizer(name, parent, pos, 0)
    return EditBoxSizer(name, parent, pos, orientation, 0)


class _GridBuilderDialog(wx.Dialog):
    def __init__(self, parent):
        pos = wx.GetMousePosition()
        wx.Dialog.__init__( self, misc.get_toplevel_parent(parent), -1, _('Select sizer type and attributes'), pos )
        # the main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # type
        choices = ["Grid", "FlexGrid", "GridBag"]
        self.type_ = wx.RadioBox(self, -1, _('Type'), choices=choices, majorDimension=1)
        sizer.Add(self.type_, 1, wx.ALL|wx.EXPAND, 3)
        # layout
        self.rows = wx.SpinCtrl(self, -1, "3")
        self.cols = wx.SpinCtrl(self, -1, "3")
        self.vgap = wx.SpinCtrl(self, -1, "0")
        self.hgap = wx.SpinCtrl(self, -1, "0")
        # grid sizer with the controls
        gsizer = wx.FlexGridSizer(cols=2)
        for label, control, tooltip in [("Rows", self.rows, 'Numbers of sizer rows'),
                                        ("Cols", self.cols, 'Numbers of sizer colums'),
                                        ("Vgap", self.vgap, 'Vertical extra space between all children'),
                                        ("Hgap", self.hgap, 'Horizontal extra space between all children')]:
            gsizer.Add(wx.StaticText(self, -1, _(label)), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
            gsizer.Add(control, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 3)
            compat.SetToolTip( control, tooltip )
        self.rows.SetFocus()
        for ctrl in (self.rows, self.cols, self.hgap, self.vgap):
            ctrl.SetSelection(-1, -1)
        # static box sizer around the grid sizer
        boxsizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, _("Layout")), wx.VERTICAL)
        boxsizer.Add(gsizer)
        sizer.Add(boxsizer, 0, wx.ALL, 3)

        # horizontal sizer for action buttons
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add( wx.Button(self, wx.ID_CANCEL, _('Cancel')), 1, wx.ALL, 5)
        btn = wx.Button(self, wx.ID_OK, _('OK') )
        btn.SetDefault()
        hsizer.Add(btn, 1, wx.ALL, 5)
        sizer.Add(hsizer, 0, wx.EXPAND|wx.ALIGN_CENTER )

        self.SetAutoLayout(True)
        self.SetSizer(sizer)

        sizer.Fit(self)
        self.Layout()



def grid_builder(parent, pos):
    "factory function for grid sizers"
    #dialog = _GridBuilderDialog(parent)
    dialog = _GridBuilderDialog(common.adding_window or parent)
    with misc.disable_stay_on_top(common.adding_window or parent):
        res = dialog.ShowModal()
    rows = dialog.rows.GetValue()
    cols = dialog.cols.GetValue()
    vgap = dialog.vgap.GetValue()
    hgap = dialog.hgap.GetValue()
    type_ = dialog.type_.GetStringSelection()
    dialog.Destroy()
    if res != wx.ID_OK: return

    name = parent.toplevel_parent.get_next_contained_name('grid_sizer_%d')
    if type_=="Grid":
        constructor = EditGridSizer
    elif type_=="FlexGrid":
        constructor = EditFlexGridSizer
    elif type_=="GridBag":
        constructor = EditGridBagSizer

    with parent.frozen():
        editor = constructor(name, parent, pos, rows, cols, vgap, hgap)
        if parent.IS_SIZER:
            editor.properties['flag'].set('wxEXPAND')
            editor.properties['pos'].set(pos)

        # add the slots
        for i in range(rows*cols):
            editor._add_slot()
        editor.layout()

        if parent.widget: editor.create()

    return editor


def grid_xml_builder(attrs, parent, pos=None):
    "factory function to build EditGridSizer objects from a XML file"
    from xml_parse import XmlParsingError

    try:
        name = attrs['name']
    except KeyError:
        raise XmlParsingError(_("'name' attribute missing"))
    if attrs['base'] == 'EditGridSizer':
        constructor = EditGridSizer
    elif attrs['base'] == 'EditFlexGridSizer':
        constructor = EditFlexGridSizer
    elif attrs['base'] == 'EditGridBagSizer':
        constructor = EditGridBagSizer
    return constructor(name, parent, pos, rows=0, cols=0)


def init_all():
    "Module initialization function: returns dict w. key 'Sizers' and an assigned list of buttons for the main palette"

    common.widgets['EditBoxSizer'] = builder
    common.widgets['EditGridSizer'] = grid_builder

    common.widget_classes['EditBoxSizer'] = EditBoxSizer
    common.widget_classes['EditStdDialogButtonSizer'] = EditStdDialogButtonSizer
    if HAVE_WRAP_SIZER:
        common.widget_classes['EditWrapSizer'] = EditWrapSizer
    common.widget_classes['EditStaticBoxSizer'] = EditStaticBoxSizer
    common.widget_classes['EditGridSizer'] = EditGridSizer
    common.widget_classes['EditFlexGridSizer'] = EditFlexGridSizer
    common.widget_classes['EditGridBagSizer'] = EditGridBagSizer

    common.widgets_from_xml['EditBoxSizer'] = xml_builder
    common.widgets_from_xml['EditStdDialogButtonSizer'] = xml_builder
    if HAVE_WRAP_SIZER:
        common.widgets_from_xml['EditWrapSizer'] = xml_builder
    common.widgets_from_xml['EditStaticBoxSizer'] = xml_builder
    common.widgets_from_xml['EditGridSizer'] = grid_xml_builder
    common.widgets_from_xml['EditFlexGridSizer'] = grid_xml_builder
    common.widgets_from_xml['EditGridBagSizer'] = grid_xml_builder

    import os.path
    from tree import WidgetTree

    if HAVE_WRAP_SIZER:
        WidgetTree.images['EditWrapSizer'] = os.path.join( config.icons_path, 'wrap_sizer_h.xpm')
        WidgetTree.images['EditHorizontalWrapSizer'] = os.path.join( config.icons_path, 'wrap_sizer_h.xpm')
        WidgetTree.images['EditVerticalWrapSizer'] = os.path.join( config.icons_path, 'wrap_sizer.xpm')
    WidgetTree.images['EditStaticBoxSizer'] = os.path.join( config.icons_path, 'sizer.xpm')
    WidgetTree.images['EditFlexGridSizer']  = os.path.join( config.icons_path, 'grid_sizer.xpm' )
    WidgetTree.images['EditGridBagSizer']  = os.path.join( config.icons_path, 'grid_sizer.xpm' )

    WidgetTree.images['EditVerticalSizer']   = os.path.join( config.icons_path, 'sizer_v.xpm' )
    WidgetTree.images['EditHorizontalSizer'] = os.path.join( config.icons_path, 'sizer_h.xpm' )
    WidgetTree.images['EditStdDialogButtonSizer'] = os.path.join( config.icons_path, 'button_sizer.xpm' )

    WidgetTree.images['EditVerticalSizerSlot']   = os.path.join( config.icons_path, 'sizer_slot_v.xpm' )
    WidgetTree.images['EditHorizontalSizerSlot'] = os.path.join( config.icons_path, 'sizer_slot_h.xpm' )
    WidgetTree.images['EditSizerSlot'] = os.path.join( config.icons_path, 'sizer_slot.xpm' )
    WidgetTree.images['EditSlot'] = os.path.join( config.icons_path, 'slot.xpm' )

    ret = {'Sizers': [
        common.make_object_button('EditBoxSizer', 'sizer.xpm'),
        common.make_object_button('EditGridSizer', 'grid_sizer.xpm')] }
    return ret
