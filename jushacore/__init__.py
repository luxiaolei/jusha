# -*- coding: utf-8 -*-
'''
This file is part of the Python Mapper package, an open source tool
for exploration, analysis and visualization of data.

Copyright 2011–2015 by the authors:
    Daniel Müllner, http://danifold.net
    Aravindakshan Babu, anounceofpractice@hotmail.com

Python Mapper is distributed under the GPLv3 license. See the project home page

    http://danifold.net/mapper

for more information.
'''
__version__ = '0.1.13'
__date__ = 'November 10, 2015'

import sys
if sys.hexversion < 0x02060000:
  raise ImportError('Python jushacore requires at least Python version 2.6.')
del sys

def cmappertoolserror(name):
    def f(*args, **kwargs):
        raise ImportError("please install the 'cmappertools' module "
        "for the '{}' function".format(name))
    return f

from jushacore._jushacore import *
from jushacore.draw_mapper_output import *
from jushacore.scale_graph import *

from jushacore import tools
from jushacore import metric
from jushacore import filters
from jushacore import cover
from jushacore import cutoff
