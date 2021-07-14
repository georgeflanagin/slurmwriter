#-*-coding:utf-8-*-
import typing
from   typing import *

import os
import sys

required_version = (3,8)
if sys.version_info < required_version:
    sys.stderr.write(f"This program requires Python {required_version} or later")
    sys.exit(os.EX_SOFTWARE)

###
# Credits
###
__author__      = 'George Flanagin'
__copyright__   = 'Copyright 2021, University of Richmond'
__credits__     = 'https://github.com/wong2/pick'
__version__     = 2.0
__maintainer__  = 'George Flanagin'
__email__       = 'gflanagin@richmond.edu'
__status__      = 'Early production'
__license__     = 'MIT'

import curses

KEYS_ENTER = (curses.KEY_ENTER, ord('\n'), ord('\r'))
KEYS_UP = (curses.KEY_UP, ord('k'))
KEYS_DOWN = (curses.KEY_DOWN, ord('j'))
KEYS_SELECT = (curses.KEY_RIGHT, ord(' '))


def _foo_null(o:object) -> object:
    return object


class Picker:

    __slots__ = {
        'options':'tuple of descriptive text to display with the options.',
        'title':'text to print at top of the selector.',
        'indicator':'character to print next to the selected term.',
        'default_index':'the default selection, and place where the indicator first appears.',
        'multiselect':'if True, this allows more than one selection.',
        'min_selection_count':'number of selections that are required. Can be zero.',
        'options_map_func':'a function to apply to all selection text. Can be None',
        'all_selected':"the user's choices.",
        'index':"the current location of the selector in the list of options.",
        'custom_handlers':"List of registered custom handlers."
        }

    __values__ = (tuple(), "", "*", 0, False, 0, _foo_null, [], -1, {})
    __defaults__ = dict(zip(__slots__, __values__))

    def __init__(self, **kwargs):
        for k, v in Picker.__defaults__.items():
            setattr(self, k, v)
        for k, v in kwargs.items():
            if k not in Picker.__slots__:
                raise Exception(f"option {k} is not a part of Picker.")
            setattr(self, k, v)

        if not -1 < self.default_index < len(self.options):
            # Just ignore it.
            self.default_index = 0

        self.index = self.default_index
        self.min_selection_count = min(self.min_selection_count, len(self.options))
        if not callable(self.options_map_func): 
            raise Exception(f"{self.options_map_func=} is not callable.")
        self.title += "\n"


    def init_handlers(self):
        pass

    def register_custom_handler(self, key, func) -> None:

        if not callable(func):
            raise Exception(f"{func} is not callable.")
        self.custom_handlers[key] = func


    def move_up(self) -> None:
        """
        This function will wrap around.
        """
        self.index -= 1
        if self.index < 0:
            self.index = len(self.options) - 1


    def move_down(self) -> None:
        self.index += 1
        if self.index  > len(self.options):
            self.index = 0


    def mark_index(self) -> None:
        if self.multiselect:
            if self.index in self.all_selected:
                self.all_selected.remove(self.index)
            else:
                self.all_selected.append(self.index)


    def get_selected(self) -> Union[tuple, list]:
        """
            return the current selected option as a tuple: (option, index)
           or as a list of tuples (in case multiselect==True)
        """
        tuples = [ (self.options[_], _) for _ in self.all_selected ]
        return tuples if self.multiselect else tuples[0]


    def get_title_lines(self) -> List[str]:
        return self.title.split('\n')


    def get_option_lines(self) -> List[str]:
        lines = []
        for index, option in enumerate(self.options):
            option = self.options_map_func(option)
            prefix = self.indicator if self.index else len(self.indicator) * ' '
            color_format = curses.color_pair(1)

            if self.multiselect and index in self.all_selected:
                line = (f'{prefix} {option}', color_format)
            else:
                line = f'{prefix} {option}'
            lines.append(line)

        return lines


    def get_lines(self):
        return ( self.get_title_lines() + self.get_option_lines(), 
                 self.index + len(title_lines) + 1 )


    def draw(self):
        """draw the curses ui on the screen, handle scroll if needed"""
        self.screen.clear()

        x, y = 1, 1  # start point
        max_y, max_x = self.screen.getmaxyx()
        max_rows = max_y - y  # the max rows we can draw

        lines, current_line = self.get_lines()

        # calculate how many lines we should scroll, relative to the top
        scroll_top = getattr(self, 'scroll_top', 0)
        if current_line <= scroll_top:
            scroll_top = 0
        elif current_line - scroll_top > max_rows:
            scroll_top = current_line - max_rows
        self.scroll_top = scroll_top

        lines_to_draw = lines[scroll_top:scroll_top+max_rows]

        for line in lines_to_draw:
            if type(line) is tuple:
                self.screen.addnstr(y, x, line[0], max_x-2, line[1])
            else:
                self.screen.addnstr(y, x, line, max_x-2)
            y += 1

        self.screen.refresh()


    def run_loop(self):

        while True:
            self.draw()
            c = self.screen.getch()
            if c in KEYS_UP:
                self.move_up()
            elif c in KEYS_DOWN:
                self.move_down()
            elif c in KEYS_ENTER:
                if self.multiselect and len(self.all_selected) < self.min_selection_count:
                    continue
                return self.get_selected()
            elif c in KEYS_SELECT and self.multiselect:
                self.mark_index()
            elif c in self.custom_handlers:
                ret = self.custom_handlers[c](self)
                if ret:
                    return ret

    def config_curses(self):
        try:
            # use the default colors of the terminal
            curses.use_default_colors()
            # hide the cursor
            curses.curs_set(0)
            # add some color for multi_select
            # @todo make colors configurable
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_WHITE)
        except:
            # Curses failed to initialize color support, eg. when TERM=vt100
            curses.initscr()

    def _start(self, screen):
        self.screen = screen
        self.config_curses()
        return self.run_loop()

    def start(self):
        return curses.wrapper(self._start)


def pick(*args, **kwargs):
    """Construct and start a :class:`Picker <Picker>`.
    Usage::
      >>> from pick import pick
      >>> title = 'Please choose an option: '
      >>> options = ['option1', 'option2', 'option3']
      >>> option, index = pick(options, title)
    """
    picker = Picker(*args, **kwargs)
    return picker.start()
