#!/usr/bin/env python
#
# Copyright (C) 2017-2018 Alex Manuskin
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

"""
A class displaying all available sensors
"""

from __future__ import print_function
from __future__ import absolute_import
import urwid
from s_tui.UiElements import ViListBox


import logging
logger = logging.getLogger(__name__)


class SensorsMenu:
    MAX_TITLE_LEN = 70

    def on_mode_button(self, button, state):
        pass

    def __init__(self, return_fn, source_list):

        self.return_fn = return_fn

        # create the cancel and apply buttons, and put the in an urwid column
        cancel_button = urwid.Button('Cancel', on_press=self.on_cancel)
        cancel_button._label.align = 'center'
        apply_button = urwid.Button('Apply', on_press=self.on_apply)
        apply_button._label.align = 'center'

        if_buttons = urwid.Columns([apply_button, cancel_button])

        self.sensor_status_dict = {}
        sensor_column_list = []
        self.sensor_button_dict = {}
        self.sensor_current_active_dict = {}
        for source in source_list:
            # TODO use saved values for default windows that are open
            source_name = source.get_source_name()

            # get the saves sensor visibility list
            self.sensor_status_dict[source_name] =\
                [True] * len(source.get_sensor_list())
            self.sensor_button_dict[source_name] = []
            self.sensor_current_active_dict[source_name] = []

            # add the title at the head of the checkbox column
            sensor_title_str = "  " + source_name + " Sensors  \n"
            sensor_title = urwid.Text(
                ('bold text', sensor_title_str), 'center')

            # create the checkbox buttons with the saved visibility
            for sensor, s_tatus in \
                    zip(source.get_sensor_list(),
                        self.sensor_status_dict[source_name]):
                cb = urwid.CheckBox(sensor, s_tatus)
                self.sensor_button_dict[source_name].append(cb)
                self.sensor_current_active_dict[source_name].append(s_tatus)

            sensor_title_and_buttons = \
                [sensor_title] + self.sensor_button_dict[source_name]
            listw = urwid.SimpleFocusListWalker(sensor_title_and_buttons)

            sensor_column_list.append(urwid.Pile(listw))

        sensor_select_widget = urwid.Columns(sensor_column_list)
        list_temp = [sensor_select_widget, if_buttons]
        listw = urwid.SimpleFocusListWalker(list_temp)
        self.main_window = urwid.LineBox(ViListBox(listw))

        max_height = 6
        for sensor, s_tatus in self.sensor_current_active_dict.items():
            max_height = max(max_height, len(s_tatus) + 6)

        self.size = max_height, self.MAX_TITLE_LEN

    def get_size(self):
        return self.size

    def set_checkbox_value(self):
        for sensor, sensor_cb in self.sensor_button_dict.items():
            sensor_cb_next_state = self.sensor_current_active_dict[sensor]
            for (checkbox, state) in zip(sensor_cb, sensor_cb_next_state):
                checkbox.set_state(state)

    def on_cancel(self, w):
        self.set_checkbox_value()
        self.return_fn(update=False)

    def on_apply(self, w):
        update_sensor_visibility = False
        for s_name, sensor_buttons in self.sensor_button_dict.items():
            cb_sensor_visibility = []
            for sensor_cb in sensor_buttons:
                cb_sensor_visibility.append(sensor_cb.get_state())

            update_sensor_visibility = \
                (cb_sensor_visibility !=
                 self.sensor_current_active_dict[s_name])

            self.sensor_current_active_dict[s_name] = cb_sensor_visibility

            if update_sensor_visibility:
                break

        self.set_checkbox_value()
        self.return_fn(update=update_sensor_visibility)
