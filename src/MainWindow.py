#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 14:53:13 2024

@author: fatihaltun
"""

import os
import re

import gi
from PIL import Image, ImageEnhance, ImageFilter
from pyzbar.pyzbar import decode

gi.require_version("GLib", "2.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, GLib, Gdk

try:
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3 as appindicator
except:
    # fall back to Ayatana
    gi.require_version('AyatanaAppIndicator3', '0.1')
    from gi.repository import AyatanaAppIndicator3 as appindicator

import locale
from locale import gettext as _

locale.bindtextdomain('eta-qr-reader', '/usr/share/locale')
locale.textdomain('eta-qr-reader')


class MainWindow(object):
    def __init__(self, application):
        self.Application = application

        self.main_window_ui_filename = os.path.dirname(os.path.abspath(__file__)) + "/../ui/MainWindow.glade"
        try:
            self.GtkBuilder = Gtk.Builder.new_from_file(self.main_window_ui_filename)
            self.GtkBuilder.connect_signals(self)
        except GObject.GError:
            print("Error reading GUI file: " + self.main_window_ui_filename)
            raise

        self.define_components()
        self.define_variables()
        self.main_window.set_application(application)

        self.init_indicator()

    def define_components(self):
        self.main_window = self.GtkBuilder.get_object("ui_main_window")

    def define_variables(self):
        self.screenshot_path = "/tmp/eta-qr-reader-screenshot.png"
        self.dialog = None

    def init_indicator(self):
        self.indicator = appindicator.Indicator.new(
            "eta-qr-reader", "eta-qr-reader-symbolic", appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_title(_("ETA QR Reader"))
        self.menu = Gtk.Menu()
        self.item_action = Gtk.MenuItem()
        self.item_action.set_label(_("Read QR Code"))
        self.item_action.connect("activate", self.on_menu_action)
        self.item_separator = Gtk.SeparatorMenuItem()
        self.item_quit = Gtk.MenuItem()
        self.item_quit.set_label(_("Quit"))
        self.item_quit.connect('activate', self.on_menu_quit_app)
        self.menu.append(self.item_action)
        self.menu.append(self.item_separator)
        self.menu.append(self.item_quit)
        self.menu.show_all()
        self.indicator.set_menu(self.menu)

    def on_menu_action(self, *args):
        if self.dialog:
            self.dialog.destroy()
        ss_command = None
        if os.path.isfile("/usr/bin/gnome-screenshot"):
            ss_command = ["/usr/bin/gnome-screenshot", "-a", "-f", self.screenshot_path]
            print("using gnome-screenshot")
        elif os.path.isfile("/usr/bin/xfce4-screenshooter"):
            ss_command = ["/usr/bin/xfce4-screenshooter", "-r", "-s", self.screenshot_path]
            print("using xfce4-screenshooter")
        elif os.path.isfile("/usr/bin/spectacle"):
            ss_command = ["/usr/bin/spectacle", "-brn", "-o", self.screenshot_path]
            print("using spectacle")

        if ss_command is not None:
            if os.path.isfile(self.screenshot_path):
                os.remove(self.screenshot_path)
            self.start_process(ss_command)
        else:
            self.show_message("<span color='red'><b>{}\n{}</b></span>".format(
                _("No screenshot application found on your system."),
                _("Supported applications are gnome-screenshot, xfce-screenshooter, kde-spectacle.")), status=False)

    def on_menu_quit_app(self, *args):
        self.main_window.get_application().quit()

    def on_ui_main_window_delete_event(self, widget, event):
        self.main_window.hide()
        return True

    def on_ui_main_window_destroy(self, widget, event):
        self.main_window.get_application().quit()

    def start_process(self, params):
        pid, stdin, stdout, stderr = GLib.spawn_async(params, flags=GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                                                      standard_output=True, standard_error=True)
        GLib.io_add_watch(GLib.IOChannel(stdout), GLib.IO_IN | GLib.IO_HUP, self.on_process_stdout)
        GLib.io_add_watch(GLib.IOChannel(stderr), GLib.IO_IN | GLib.IO_HUP, self.on_process_stderr)
        GLib.child_watch_add(GLib.PRIORITY_DEFAULT, pid, self.on_process_exit)

        return pid

    def on_process_stdout(self, source, condition):
        if condition == GLib.IO_HUP:
            return False
        line = source.readline()
        print(line)
        return True

    def on_process_stderr(self, source, condition):
        if condition == GLib.IO_HUP:
            return False
        line = source.readline()
        print(line)
        return True

    def on_process_exit(self, pid, status):
        print(status)
        try:
            image = Image.open(self.screenshot_path)
            decoded_objects = decode(image)
            if decoded_objects:
                qr_data = decoded_objects[0].data.decode("utf-8")
                print("{}".format(qr_data))
                self.show_message("{}".format(qr_data))
            else:
                print("No QR Code found. Trying image processing.")
                # resize 5x
                width, height = image.size
                new_size = (int(width * 5), int(height * 5))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                # grayscale
                image = image.convert('L')
                # contrast
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(20)
                # sharpness
                image = image.filter(ImageFilter.SHARPEN)
                # some blur
                image = image.filter(ImageFilter.GaussianBlur(radius=1.5))

                decoded_objects = decode(image)
                if decoded_objects:
                    qr_data = decoded_objects[0].data.decode("utf-8")
                    print("{}".format(qr_data))
                    self.show_message("{}".format(qr_data))
                else:
                    print("No QR Code found.")
                    self.show_message(_("No QR Code found."), status=False)
        except Exception as e:
            print("{}".format(e))
            self.show_message("{}".format(e), status=False)

    def show_message(self, content, status=True):
        if self.dialog:
            self.dialog.destroy()
        self.dialog = Gtk.MessageDialog(
            parent=None,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            title=_("QR Code Content")
        )
        label = Gtk.Label()
        url_regex = r"(http[s]?://[^\s<>\"';]+)"
        parts = re.split(url_regex, content)

        formatted_message = ""
        for part in parts:
            if re.match(url_regex, part):
                formatted_message += "<a href='{}' title='{}'>{}</a>".format(part, part, part)
            else:
                formatted_message += part

        def on_link_clicked(*args):
            self.dialog.response(Gtk.ResponseType.OK)

        label.set_markup(formatted_message)
        label.set_selectable(True)
        label.set_line_wrap(True)
        label.set_max_width_chars(100)
        label.set_line_wrap_mode(2)
        label.set_justify(Gtk.Justification.CENTER)
        label.connect("activate-link", on_link_clicked)

        def on_copy_clicked(*args):
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(content, -1)

        copy_image = Gtk.Image.new_from_icon_name("edit-copy-symbolic", Gtk.IconSize.BUTTON)
        button = Gtk.Button.new()
        button.props.valign = Gtk.Align.CENTER
        button.props.halign = Gtk.Align.CENTER
        button.add(copy_image)
        button.connect('clicked', on_copy_clicked)

        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 13)
        box.pack_start(label, False, True, 0)
        if status:
            box.pack_start(button, False, True, 0)
        else:
            retry_image = Gtk.Image.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
            retry_button = Gtk.Button.new()
            retry_button.props.valign = Gtk.Align.CENTER
            retry_button.props.halign = Gtk.Align.CENTER
            retry_button.add(retry_image)
            retry_button.connect('clicked', self.on_menu_action)
            box.pack_start(retry_button, False, True, 0)

        box.set_margin_top(0)
        box.set_margin_bottom(13)
        box.set_margin_start(13)
        box.set_margin_end(13)

        content_area = self.dialog.get_content_area()
        content_area.pack_start(box, False, False, 0)
        box.show_all()

        self.dialog.set_position(Gtk.WindowPosition.CENTER)
        self.dialog.present()
        self.dialog.set_keep_above(True)
        self.dialog.run()
        self.dialog.destroy()
