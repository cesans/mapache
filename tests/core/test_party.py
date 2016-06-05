"""mapache.Party tests."""

import unittest
from nose.tools import *

import sys
sys.path.append('../')
import mapache

img_url = 'https://github.com/cesans/mapache/raw/master/doc/source/mapache.png'
class PartyTests(unittest.TestCase):
    def test(self):
        party = mapache.Party(name='name',  logo_url=img_url,
                      short_name='short_name', full_name='full_name',
                      extra_names=['extra_name1, extra_name2', 'extra_name3'])        
        assert(len(party.get_all_names()) != 6)

p = PartyTests()
p.test()
