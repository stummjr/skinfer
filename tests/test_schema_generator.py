#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
from skinfer.schema_generator import JsonSchemaGenerator
import unittest
import sys
from tests import fixtures


def generate_schema(sample):
    return JsonSchemaGenerator(sample).generate()


class TestJsonSchemaGenerator(unittest.TestCase):
    def test_empty_object(self):
        self.assertEqual(generate_schema({}), fixtures.REQUIRE_OBJECT_TYPE)

    def test_string(self):
        expected = {'$schema': u'http://json-schema.org/draft-04/schema', 'type': 'string'}
        self.assertEqual(generate_schema(''), expected)
        self.assertEqual(generate_schema(u''), expected)

    def test_boolean(self):
        expected = {'$schema': u'http://json-schema.org/draft-04/schema', 'type': 'boolean'}
        self.assertEqual(generate_schema(True), expected)
        self.assertEqual(generate_schema(False), expected)

    def test_list(self):
        expected = {'$schema': u'http://json-schema.org/draft-04/schema', 'type': 'array'}
        self.assertEqual(generate_schema([]), expected)

    def test_number(self):
        expected = {'$schema': u'http://json-schema.org/draft-04/schema', 'type': 'number'}
        self.assertEqual(generate_schema(1), expected)
        self.assertEqual(generate_schema(1.2), expected)
        long_number = sys.maxsize * 2
        self.assertEqual(generate_schema(long_number), expected)

    def test_list_with_items(self):
        expected = {'$schema': u'http://json-schema.org/draft-04/schema',
                    'type': 'array', 'items': {'type': 'number'}}
        self.assertEqual(generate_schema([1, 2, 3]), expected)

    def test_list_with_heterogeneous_items(self):
        expected = {'$schema': u'http://json-schema.org/draft-04/schema', 'type': 'array',
                    'items': {'anyOf': [{'type': 'number'}, {'type': 'string'}]}}
        self.assertSchemaEqual(generate_schema([1, 2, "3"]), expected)

    def test_simple_object(self):
        self.assertEqual(generate_schema({"something": "ai"}),
                         fixtures.REQUIRING_SOME_PROPERTY)

    def test_object_with_nested_properties(self):
        self.assertEqual(generate_schema({"something": {"nested_required": "1"}}),
                         fixtures.REQUIRING_SOME_PROPERTY_WITH_NESTED_REQUIRED_PROPERTY)

    def assertSchemaEqual(self, schema1, schema2):
        self.assertEqual(len(schema1), len(schema2))
        self.assertEqual(schema1.get('type'), schema2.get('type'))

        schema_type = schema1.get('type')

        if schema_type == 'object':
            for k, v in schema1.get('properties').items():
                self.assertIn(k, schema2['properties'])
            self.assertEqual(sorted(schema1.get('required')), sorted(schema2.get('required')))

        if schema1.get('anyOf'):
            self.assertEqual(sorted(schema1.get('anyOf')), sorted(schema2.get('anyOf')))

    def test_with_linkedin_minimal_example(self):
        data = fixtures.get_sample('minimal-1.json')

        expected = {
            '$schema': u'http://json-schema.org/draft-04/schema',
            'properties': {
                u'also_viewed': {'items': {'type': 'string'}, 'type': 'array'},
                u'family_name': {'type': 'string'},
                u'full_name': {'type': 'string'},
                u'given_name': {'type': 'string'},
                u'headline': {'type': 'string'},
                u'linkedin_id': {'type': 'string'},
                u'locality': {'type': 'string'},
                u'num_connections': {'type': 'string'},
                u'updated': {'type': 'string'},
                u'url': {'type': 'string'}},
            'required': [
                u'family_name',
                u'updated',
                u'linkedin_id',
                u'locality',
                u'headline',
                u'num_connections',
                u'url',
                u'also_viewed',
                u'given_name',
                u'full_name'],
            'type': 'object'
        }
        self.assertSchemaEqual(generate_schema(data), expected)
