# -*- coding: utf-8 -*-
import typing
from   typing import *

import math
import os
import pprint
import sys


# Credits
__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2020'
__credits__ = None
__version__ = str(1/math.pi)
__maintainer__ = 'George Flanagin'
__email__ = ['me@georgeflanagin.com', 'gflanagin@richmond.edu']
__status__ = 'Teaching example'
__license__ = 'MIT'



class SloppyTree: pass
class SloppyTree(dict):
    """
    Like SloppyDict() only worse -- much worse.
    """

    def __missing__(self, k:str) -> object:
        """
        If we reference an element that doesn't exist, we create it,
        and assign a SloppyTree to its value.
        """
        self[k] = SloppyTree()
        return self[k]


    def __getattr__(self, k:str) -> object:
        """
        Retrieve the element, or implicity call the over-ridden 
        __missing__ method, and make a new one.
        """
        return self[k]


    def __setattr__(self, k:str, v:object) -> None:
        """
        Assign the value as expected.
        """
        self[k] = v


    def __delattr__(self, k:str) -> None:
        """
        Remove it if we can.
        """
        if k in self: del self[k]


    def __ilshift__(self, keys:Union[list, tuple]) -> SloppyTree:
        """
        Create a large number of sibling keys from a list.
        """
        for k in keys:
            self[k] = SloppyTree()
        return self


    def _leaves(self) -> str:
        """
        Walk the leaves only, left to right.
        """ 
        for k, v in self.items():
            if isinstance(v, dict):
                yield from self._leaves(v)
            else:
                yield v


    def _walk(self, level=0) -> Tuple[str, int]:
        """
        Emit all the nodes of a tree left-to-right and top-to-bottom.
        The bool is included so that you can know whether you have reached
        a leaf. (NOTE: dict.__iter__ only sees keys.)
        """
        for k, v in self.items():
            level += 1
            yield k, level
            if isinstance(v, dict):
                yield from self._walk(level)
                level -= 1
            else:
                yield v, None


    def __str__(self) -> str:
        """
        Printing one of these things requires a bit of finesse.
        """
        return pprint.pformat(self, compact=True, indent=4, width=100)
