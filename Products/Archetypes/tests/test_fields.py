# -*- coding: UTF-8 -*-
################################################################################
#
# Copyright (c) 2002-2005, Benjamin Saller <bcsaller@ideasuite.com>, and
#                              the respective authors. All rights reserved.
# For a list of Archetypes contributors see docs/CREDITS.txt.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of the author nor the names of its contributors may be used
#   to endorse or promote products derived from this software without specific
#   prior written permission.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
################################################################################
"""
"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase
from Products.Archetypes.tests.atsitetestcase import portal_name
from Products.Archetypes.tests.attestcase import HAS_PLONE
from Products.Archetypes.tests.attestcase import HAS_PLONE21
from Products.Archetypes.tests.utils import mkDummyInContext
from Products.Archetypes.tests.utils import PACKAGE_HOME

from Products.Archetypes.atapi import *
from Products.Archetypes.config import PKG_NAME
from Products.Archetypes.interfaces.vocabulary import IVocabulary
from Products.Archetypes import Field as at_field
from Products.Archetypes.Field import ScalableImage, Image
from OFS.Image import File, Image
from DateTime import DateTime


test_fields = [
          ('ObjectField', 'objectfield'),
          ('StringField', 'stringfield'),
          ('FileField', 'filefield'),
          ('TextField', 'textfield'),
          ('DateTimeField', 'datetimefield'),
          ('LinesField','linesfield'),
          ('IntegerField', 'integerfield'),
          ('FloatField', 'floatfield'),
          ('FixedPointField', 'fixedpointfield1'),
          ('FixedPointField', 'fixedpointfield2'),
          ('BooleanField', 'booleanfield'),
          ('ImageField', 'imagefield'),
          ('PhotoField', 'photofield'),
          # 'ReferenceField', 'ComputedField', 'CMFObjectField',
          ]

field_instances = []
for type, name in test_fields:
    field_instances.append(getattr(at_field, type)(name))

txt_file = open(os.path.join(PACKAGE_HOME, 'input', 'rest1.rst'))
txt_content = txt_file.read()
img_file = open(os.path.join(PACKAGE_HOME, 'input', 'tool.gif'))
img_content = img_file.read()

field_values = {'objectfield':'objectfield',
                'stringfield':'stringfield',
                'filefield_file':txt_file,
                'textfield':'textfield',
                'datetimefield':'2003-01-01',
                'linesfield':'bla\nbla',
                'integerfield':'1',
                'floatfield':'1.5',
                'fixedpointfield1': '1.5',
                'fixedpointfield2': '1,5',
                'booleanfield':'1',
                'imagefield_file':img_file,
                'photofield_file':img_file}

expected_values = {'objectfield':'objectfield',
                   'stringfield':'stringfield',
                   'filefield':txt_content,
                   'textfield':'textfield',
                   'datetimefield':DateTime('2003-01-01'),
                   'linesfield':('bla', 'bla'),
                   'integerfield': 1,
                   'floatfield': 1.5,
                   'fixedpointfield1':  '1.50',
                   'fixedpointfield2': '1.50',
                   'booleanfield': 1,
                   'imagefield':'<img src="%s/dummy/imagefield" alt="Spam" title="Spam" height="16" width="16" border="0" />' % portal_name, 
                   'photofield':'<img src="%s/dummy/photofield/variant/original" alt="" title="" height="16" width="16" border="0" />' % portal_name
                   }
if HAS_PLONE:
    # Plone has a patch which removed the border="0" 
    if HAS_PLONE21:
        expected_values['imagefield'] = '<img src="%s/dummy/imagefield" alt="Spam" title="Spam" height="16" width="16" />' % portal_name
    else:
        # Plone 2.0 has a longdesc attribute
        expected_values['imagefield'] = '<img src="%s/dummy/imagefield" alt="Spam" title="Spam" longdesc="" height="16" width="16" />' % portal_name

empty_values = {'objectfield':None,
                   'stringfield':'',
                   'filefield':None,
                   'textfield':'',
                   'datetimefield':None,
                   'linesfield':(),
                   'integerfield': None,
                   'floatfield': None,
                   'fixedpointfield1': None,
                   'fixedpointfield2': None,
                   'booleanfield': None,
                   #XXX'imagefield':"DELETE_IMAGE",
                   #XXX'photofield':"DELETE_IMAGE",
               }

schema = Schema(tuple(field_instances))
sampleDisplayList = DisplayList([('e1', 'e1'), ('element2', 'element2')])

class sampleInterfaceVocabulary:
    __implements__ = IVocabulary
    def getDisplayList(self, instance):
        return sampleDisplayList

class Dummy(BaseContentMixin):
    def Title(self):
        # required for ImageField
        return 'Spam'

    def aMethod(self):
        return sampleDisplayList


class FakeRequest:

    def __init__(self):
        self.other = {}
        self.form = {}


class ProcessingTest(ATSiteTestCase):

    def afterSetUp(self):
        self.setRoles(['Manager'])
        ATSiteTestCase.afterSetUp(self)
        self._dummy = mkDummyInContext(Dummy, oid='dummy', context=self.portal,
                                       schema=schema)
        txt_file.seek(0)
        img_file.seek(0)

    def makeDummy(self):
        return self._dummy

    def test_processing(self):
        dummy = self.makeDummy()
        request = FakeRequest()
        request.form.update(field_values)
        dummy.REQUEST = request
        dummy.processForm(data=1)
        for k, v in expected_values.items():
            got = dummy.getField(k).get(dummy)
            if isinstance(got, File):
                got = str(got)
            self.assertEquals(got, v, 'got: %r, expected: %r, field "%s"' %
                              (got, v, k))

##    def test_empty_processing(self):
##        dummy = self.makeDummy()
##        request = FakeRequest()
##        request.form.update(field_values)
##        dummy.REQUEST = request
##        dummy.processForm(data=1)
##
##        request.form.update(empty_values)
##        dummy.REQUEST = request
##        dummy.processForm(data=1)
##
##        for k, v in empty_values.items():
##            got = dummy.Schema()[k].get(dummy)
##            if isinstance(got, (File)) and not got.data:
##                got = None
##            if not got:
##                v = None
##            self.assertEquals(got, v, 'got: %r, expected: %r, field "%s"' %
##                              (got, v, k))


    def test_processing_fieldset(self):
        dummy = self.makeDummy()
        request = FakeRequest()
        request.form.update(field_values)
        request.form['fieldset'] = 'default'
        dummy.REQUEST = request
        dummy.processForm()
        for k, v in expected_values.items():
            got = dummy.getField(k).get(dummy)
            if isinstance(got, (File, ScalableImage, Image)):
                got = str(got)
            self.assertEquals(got, v, 'got: %r, expected: %r, field "%s"' %
                              (got, v, k))

    def test_get_size(self):
        dummy = self.makeDummy()
        request = FakeRequest()
        request.form.update(field_values)
        request.form['fieldset'] = 'default'
        dummy.REQUEST = request
        dummy.processForm()
        size = 0
        for k, v in expected_values.items():
            field = dummy.getField(k)
            s = field.get_size(dummy)
            size+=s
            self.failUnless(s, 'got: %s, field: %s' % (s, k))
        self.failUnlessEqual(size, dummy.get_size())

    def test_validation(self):
        dummy = self.makeDummy()
        request = FakeRequest()
        request.form.update(field_values)
        request.form['fieldset'] = 'default'
        dummy.REQUEST = request
        errors = {}
        dummy.validate(errors=errors)
        self.failIf(errors, errors)

    def test_required(self):
        request = FakeRequest()
        request.form.update(empty_values)
        request.form['fieldset'] = 'default'
        self._test_required(request)
        
    def test_required_empty_request(self):
        request = FakeRequest()
        request.form = {}
        request.form['fieldset'] = 'default'
        self._test_required(request)

    def _test_required(self, request):
        dummy = self.makeDummy()
        f_names = []

        schema = dummy.Schema()
        for f in schema.fields():
            name = f.getName()
            f.required = 1
            f_names.append(name)
        errors = {}
        dummy.validate(REQUEST=request, errors=errors)
        self.failUnless(errors, "Errors dictionary is empty.")
        err_fields = errors.keys()
        failures = []
        for f_name in f_names:
            if f_name not in err_fields:
                failures.append(f_name)
        self.failIf(failures, "%s failed to report error." % failures)

    def test_static_vocabulary(self):
        dummy = self.makeDummy()
        request = FakeRequest()
        field = dummy.Schema().fields()[0]

        # Default
        self.failUnlessEqual(field.Vocabulary(), DisplayList())
        # DisplayList
        field.vocabulary = sampleDisplayList()
        self.failUnlessEqual(field.Vocabulary(), sampleDisplayList)
        # List
        field.vocabulary = ['e1', 'element2']
        self.failUnlessEqual(field.Vocabulary(), sampleDisplayList)
        # 2-Tuples
        field.vocabulary = [('e1', 'e1'), ('element2', 'element2')]
        self.failUnlessEqual(field.Vocabulary(), sampleDisplayList)

    def test_dynamic_vocabulary(self):
        dummy = self.makeDummy()
        request = FakeRequest()
        field = dummy.Schema().fields()[0]

        # Default
        self.failUnlessEqual(field.Vocabulary(dummy), DisplayList())
        # Method
        field.vocabulary = 'aMethod'
        self.failUnlessEqual(field.Vocabulary(dummy), sampleDisplayList)
        # DisplayList
        field.vocabulary = sampleDisplayList()
        self.failUnlessEqual(field.Vocabulary(dummy), sampleDisplayList)
        # List
        field.vocabulary = ['e1', 'element2']
        self.failUnlessEqual(field.Vocabulary(dummy), sampleDisplayList)
        # 2-Tuples
        field.vocabulary = [('e1', 'e1'), ('element2', 'element2')]
        self.failUnlessEqual(field.Vocabulary(dummy), sampleDisplayList)
        # Interface
        field.vocabulary = sampleInterfaceVocabulary()
        self.failUnlessEqual(field.Vocabulary(dummy), sampleDisplayList)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ProcessingTest))
    return suite

if __name__ == '__main__':
    framework()
