#!/usr/bin/env python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  language.py
#  
#  Copyright 2013 Antergos
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

from gi.repository import Gtk, GLib
import gettext
import locale
import os
import logging

# Useful vars for gettext (translations)
APP_NAME = "cnchi"
LOCALE_DIR = "/usr/share/locale"

# Import functions
import config
import i18n

_next_page = "location"
_prev_page = "welcome"

class Language(Gtk.Box):

    def __init__(self, params):
        self.header = params['header']
        self.ui_dir = params['ui_dir']
        self.forward_button = params['forward_button']
        self.backwards_button = params['backwards_button']
        self.settings = params['settings']

        super().__init__()

        self.ui = Gtk.Builder()
        self.ui.add_from_file(os.path.join(self.ui_dir, "language.ui"))
        self.ui.connect_signals(self)

        self.label_choose_language = self.ui.get_object("label_choose_language")

        # Set up list box
        self.listbox = self.ui.get_object("listbox")
        self.listbox.connect("row-selected", self.on_listbox_row_selected)
        self.listbox.set_selection_mode(Gtk.SelectionMode.BROWSE)
        #self.listbox.set_sort_func(self.listbox_sort_by_name, None)
        #self.listbox.set_filter_func(self.listbox_filter_by_name, None)
        
        self.translate_ui()
        
        data_dir = self.settings.get('data')
        
        self.current_locale = locale.getdefaultlocale()[0]
        self.language_list =  os.path.join(data_dir, "languagelist.data.gz")
        self.set_languages_list()
        
        image1 = self.ui.get_object("image1")
        image1.set_from_file(os.path.join(data_dir, "languages.png"))
        
        label = self.ui.get_object("welcome_label")
        label.set_name("WelcomeMessage")

        super().add(self.ui.get_object("language"))

    def on_listbox_row_selected(self, listbox, listbox_row):
        # Someone selected a different row of the listbox
        if listbox_row is not None:
            for vbox in listbox_row:
                for label in vbox.get_children():
                    current_language, sorted_choices, display_map = i18n.get_languages(self.language_list)
                    lang = label.get_text()
                    lang_code = display_map[lang][1]
                    self.set_language(lang_code)

    def listbox_filter_by_name(self, row, user_data):
        pass
        #bus_name_box_list = row.get_children()
        #return self.__bus_name_filter.get_text().lower() in bus_name_box_list[0].bus_name.lower()
    
    def listbox_sort_by_name(self, row1, row2, user_data):
        # Sort function for listbox
        pass
        '''
        child1 = row1.get_children()
        child2 = row2.get_children()
        un1 = child1[0].bus_name
        un2 = child2[0].bus_name
        '''
        
    def translate_ui(self):
        txt = _("Please choose your language:")
        txt = '<span weight="bold">%s</span>' % txt
        self.label_choose_language.set_markup(txt)
        
        label = self.ui.get_object("welcome_label")
        txt_bold = _("Notice: The Cnchi Installer is beta software.")
        txt = _("Cnchi is pre-release beta software that is under active development. \n" \
        "It does not yet properly handle RAID, btrfs subvolumes, or other " \
        "advanced setups. Please proceed with caution as data loss is possible! \n\n" \
        "If you find any bugs, please report them at <a href='http://bugs.antergos.com'>http://bugs.antergos.com</a>")
        txt = "<span weight='bold'>%s</span>\n\n" % txt_bold + txt
        label.set_markup(txt)

        txt = _("Welcome to Antergos!")
        #txt = "<span weight='bold' size='large'>%s</span>" % txt
        #self.title.set_markup(txt)
        #self.header.set_title("Cnchi")
        self.header.set_subtitle(txt)
    
    def langcode_to_lang(self, display_map):
        # Special cases in which we need the complete current_locale string
        if self.current_locale not in ('pt_BR', 'zh_CN', 'zh_TW'):
            self.current_locale = self.current_locale.split("_")[0]
    
        for lang, lang_code in display_map.items():
            if lang_code[1] == self.current_locale:
                return lang

    def set_languages_list(self):
        current_language, sorted_choices, display_map = i18n.get_languages(self.language_list)
        current_language = self.langcode_to_lang(display_map)
        for lang in sorted_choices:
            box = Gtk.VBox()
            label = Gtk.Label(lang)
            box.add(label)
            self.listbox.add(box)
            if current_language == lang:
                self.select_default_row(current_language)

    def set_language(self, locale_code):
        if locale_code is None:
            locale_code, encoding = locale.getdefaultlocale()

        try:
            lang = gettext.translation(APP_NAME, LOCALE_DIR, [locale_code])
            lang.install()
            self.translate_ui()
        except IOError:
            logging.error(_("Can't find translation file for the %s language") % locale_code)
    
    def select_default_row(self, language):   
        for listbox_row in self.listbox:
            for vbox in listbox_row:
                for label in vbox.get_children():
                    if language == label.get_text():
                        self.listbox.select_row(listbox_row)
                        return
                
    def store_values(self):
        listbox_row = self.listbox.get_selected_row()
        if listbox_row != None:
            for vbox in listbox_row:
                for label in vbox.get_children():
                    lang = label.get_text()

        current_language, sorted_choices, display_map = i18n.get_languages(self.language_list)

        self.settings.set("language_name", display_map[lang][0])
        self.settings.set("language_code", display_map[lang][1])
        
        return True

    def prepare(self, direction):
        self.translate_ui()
        
        # scroll language treeview to selected item
        #self.scroll_to_selected_item(self.treeview_language)
        
        self.show_all()

    def get_prev_page(self):
        return _prev_page

    def get_next_page(self):
        return _next_page
