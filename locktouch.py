import configparser
import os
import argparse


import gi
from gi.repository import Gtk
gi.require_version('Gtk', '3.0')

PASSWORD_SUCCESS = 0
PASSWORD_FAILURE = 1
PASSWORD_CONTINUE = 2

KEY_CAPTION = 1
KEY_WRONG = 2
KEY_ERROR = 4
KEY_CONFIRM = 8

CONFIG_DIRECTORY = '~/.config/locktouch/'
CONFIG_FILE = '~/.config/locktouch/locktouch.conf'

STRINGS = {
    KEY_CAPTION: "LOCKTOUCH",
    KEY_WRONG:   "WRONG",
    KEY_ERROR:   "Supplied password is invalid. Check Locktouch "
                 "arguments and/or configuration file.",
    KEY_CONFIRM: "CONFIRM"
}


class LockTouchErrorWindow(Gtk.Window):
    def __init__(self, cfg):
        Gtk.Window.__init__(self, title="Locktouch Error")
        grid = Gtk.Grid()
        self.add(grid)
        label = Gtk.Label(STRINGS[KEY_ERROR], wrap=True,
                          justify=Gtk.Justification.FILL)
        grid.attach(label, 0, 0, 1, 1)
        button = Gtk.Button(label=STRINGS[KEY_CONFIRM])
        grid.attach(button, 0, 1, 1, 1)
        button.connect("clicked", Gtk.main_quit)


class LockTouchWindow(Gtk.Window):
    def __init__(self, cfg):
        self.cfg = cfg
        Gtk.Window.__init__(self, title="Locktouch", decorated=False,
                            is_maximized=True, modal=True)
        self.fullscreen()
        self.grid = Gtk.Grid(expand=True)
        self.add(self.grid)
        self.buttons = []
        self.label = Gtk.Label(STRINGS[KEY_CAPTION], margin_top=10,
                               margin_bottom=10)
        self.grid.attach(self.label, 0, 0, 3, 1)
        for i in range(1, 10):
            btn = Gtk.Button(label="{}".format(i), expand=True)
            btn.connect("clicked", self.on_button_clicked)
            btn.password_id = '{}'.format(i)
            self.grid.attach(btn, i % 3, 1 + i / 3, 1, 1)
            self.buttons.append(btn)

    def on_button_clicked(self, widget):
        result = self.cfg.check(widget.password_id)
        if result == PASSWORD_SUCCESS:
            Gtk.main_quit()
        elif result == PASSWORD_FAILURE:
            self.label.set_text(STRINGS[KEY_WRONG])
        elif result == PASSWORD_CONTINUE:
            self.label.set_text(STRINGS[KEY_CAPTION])


class LockTouchConfig():
    def __init__(self, argcfg):
        self.valid = False
        self.password = argcfg.password
        self.user_input = ''
        if self.password is not None and len(self.password) > 0:
            self.valid = True
        else:
            if not os.path.exists(os.path.expanduser(CONFIG_DIRECTORY)):
                os.makedirs(os.path.expanduser(CONFIG_DIRECTORY))
            if not os.path.exists(os.path.expanduser(CONFIG_FILE)):
                parser = configparser.ConfigParser()
                parser['default'] = {'password': ''}
                with open(os.path.expanduser(CONFIG_FILE), 'w') as cfg_file:
                    parser.write(cfg_file)
            else:
                parser = configparser.ConfigParser()
                parser.read(os.path.expanduser(CONFIG_FILE))
                try:
                    self.password = parser['default']['password']
                    if len(self.password) > 0:
                        self.valid = True
                        self.user_input = ''
                except KeyError:
                    pass

    def check(self, char):
        self.user_input += char
        if len(self.user_input) == len(self.password):
            if self.user_input == self.password:
                return PASSWORD_SUCCESS
            else:
                self.user_input = ''
                return PASSWORD_FAILURE
        else:
            return PASSWORD_CONTINUE


def start_locktouch(argcfg):
    cfg = LockTouchConfig(argcfg)
    if cfg.valid:
        win = LockTouchWindow(cfg)
        win.show_all()
    else:
        win = LockTouchErrorWindow(cfg)
        win.show_all()
    Gtk.main()


if __name__ == '__main__':
    args = argparse.ArgumentParser(description="Locktouch is a "
                                   "touch-friendly screen locker. "
                                   "Configuration file location is "
                                   "~/.config/locktouch/locktouch.conf.")
    args.add_argument('--password', metavar='N',
                      help='unlocking password')
    start_locktouch(args.parse_args())
