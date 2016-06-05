"""mapache.Party tests."""

import unittest
from nose.tools import *

import sys
sys.path.append('../')
import mapache

img_url = 'https://github.com/cesans/mapache/raw/master/doc/source/mapache.png'
class TestPartyNames(unittest.TestCase):
    
    def test_getnames(self):
        party = mapache.Party(name='name',  logo_url=img_url,
                              short_name='short_name', full_name='full_name')        
        self.assertEqual(len(party.get_all_names()), 3)

    def test_extra_names(self):
        party = mapache.Party(name='name',  logo_url=img_url,
                              short_name='short_name', full_name='full_name',
                              extra_names=['extra_name1', 'extra_name2'])
        self.assertEqual(len(party.get_all_names()), 5)

    def test_repeated_names(self):
        party = mapache.Party(name='name',  logo_url=img_url,
                              short_name='short_name', full_name='full_name',
                              extra_names=['extra_name1', 'full_name'])
        self.assertEqual(len(party.get_all_names()), 4)

    def test_short_name_too_long(self):
        party = mapache.Party(name='name',  logo_url=img_url,
                              short_name='1234567891011')
        self.assertLessEqual(len(party.short_name), 7)

    def test_short_name_from_name(self):
        party = mapache.Party(name='Name', logo_url=img_url)
        self.assertEqual(party.short_name, party.name)

    def test_short_name_from_name_initials(self):
        party = mapache.Party(name='Name Name Name Name', logo_url=img_url)
        self.assertEqual(party.short_name, 'NNNN')

    def test_short_name_from_name_initials(self):
        party = mapache.Party(name='Name Name', logo_url=img_url)
        self.assertEqual(party.short_name, 'NAM')

class TestLogos(unittest.TestCase):
    pass
    #distance and logo

class TestMatch(unittest.TestCase):
    pass

class TestCoallition(unittest.TestCase):
    pass
