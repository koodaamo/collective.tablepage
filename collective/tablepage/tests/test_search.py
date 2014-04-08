# -*- coding: utf-8 -*-

import unittest
from zope.component import getMultiAdapter

from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login

from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.testing import TABLE_PAGE_INTEGRATION_TESTING


class TablePageCatalogTestCase(unittest.TestCase):

    layer = TABLE_PAGE_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        request = self.layer['request']
        login(portal, TEST_USER_NAME)
        portal.invokeFactory(type_name='TablePage', id='table_page', title="The Table Document")
        portal.table_page.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                                             'type': 'String', 'vocabulary': '', 'options': []},
                                            {'id': 'col_b', 'label': 'Col B', 'description': '',
                                             'type': 'String', 'vocabulary': '', 'options': []}
        ])
        self.tp_catalog = portal.tablepage_catalog
        self.storage = IDataStorage(portal.table_page)
        request.set('ACTUAL_URL', 'http://nohost/plone/table_page')


    def test_search_form_not_shown1(self):
        portal = self.layer['portal']
        output = portal.table_page()
        self.assertFalse('id="searchTablePage"' in output)

    def test_search_form_not_shown2(self):
        portal = self.layer['portal']
        tp = portal.table_page
        tp.edit(searchConfig=[{'id': 'col_a', 'label': '', 'description': '', 'additionalConfiguration': []}])
        self.assertFalse('id="searchTablePage"' in tp())

    def test_search_form_shown(self):
        portal = self.layer['portal']
        tp = portal.table_page
        tp.edit(searchConfig=[{'id': 'col_a', 'label': '', 'description': '', 'additionalConfiguration': []}])
        self.tp_catalog.addIndex('col_a', 'FieldIndex')
        output = tp()
        self.assertTrue('id="searchTablePage"' in output)

    def test_search_form_values_selector_shown(self):
        portal = self.layer['portal']
        tp = portal.table_page
        tp.edit(searchConfig=[{'id': 'col_a', 'label': '', 'description': '', 'additionalConfiguration': []}])
        self.storage.add({'__creator__': 'user1', 'col_a': 'Foo Bar Baz', '__uuid__': 'aaa'})
        self.tp_catalog.addIndex('col_a', 'FieldIndex')
        self.tp_catalog.clearFindAndRebuild()
        output = tp()
        self.assertTrue('<select name="col_a:list"' in output)
        self.assertTrue('<option value="Foo Bar Baz">' in output)

    def test_search_form_postback1(self):
        portal = self.layer['portal']
        request = self.layer['request']
        tp = portal.table_page
        tp.edit(searchConfig=[{'id': 'col_a', 'label': '', 'description': '', 'additionalConfiguration': []}])
        self.storage.add({'__creator__': 'user1', 'col_a': 'Foo Bar Baz', '__uuid__': 'aaa'})
        self.tp_catalog.addIndex('col_a', 'FieldIndex')
        self.tp_catalog.clearFindAndRebuild()
        request.form['col_a'] = 'Foo Bar Baz'
        output = tp()
        self.assertTrue('<select name="col_a:list"' in output)
        self.assertTrue('<option value="Foo Bar Baz" selected="selected">' in output)