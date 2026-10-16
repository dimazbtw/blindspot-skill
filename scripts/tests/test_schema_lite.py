import unittest

import helpers  # noqa: F401  (sets sys.path)
import schema_lite


class SchemaLiteTests(unittest.TestCase):
    def test_valid_object(self):
        schema = {"type": "object", "required": ["a"], "additionalProperties": False,
                  "properties": {"a": {"type": "integer", "minimum": 1}}}
        self.assertEqual(schema_lite.validate({"a": 2}, schema), [])

    def test_missing_and_unexpected_fields(self):
        schema = {"type": "object", "required": ["a"], "additionalProperties": False,
                  "properties": {"a": {"type": "string"}}}
        errors = schema_lite.validate({"b": 1}, schema)
        self.assertTrue(any("missing required field 'a'" in e for e in errors))
        self.assertTrue(any("unexpected field 'b'" in e for e in errors))

    def test_bool_is_not_integer(self):
        self.assertTrue(schema_lite.validate(True, {"type": "integer"}))
        self.assertEqual(schema_lite.validate(3, {"type": "integer"}), [])

    def test_const_does_not_confuse_true_and_one(self):
        self.assertTrue(schema_lite.validate(1, {"const": True}))
        self.assertEqual(schema_lite.validate(True, {"const": True}), [])

    def test_enum_pattern_and_lengths(self):
        self.assertTrue(schema_lite.validate("c", {"enum": ["a", "b"]}))
        self.assertTrue(schema_lite.validate("abc", {"type": "string", "pattern": "^x"}))
        self.assertTrue(schema_lite.validate("", {"type": "string", "minLength": 1}))
        self.assertTrue(schema_lite.validate("abcd", {"type": "string", "maxLength": 3}))

    def test_arrays(self):
        schema = {"type": "array", "minItems": 1, "maxItems": 2, "items": {"type": "string"}}
        self.assertTrue(schema_lite.validate([], schema))
        self.assertTrue(schema_lite.validate(["a", "b", "c"], schema))
        self.assertTrue(schema_lite.validate([1], schema))
        self.assertEqual(schema_lite.validate(["a"], schema), [])

    def test_type_union_with_null(self):
        schema = {"type": ["integer", "null"]}
        self.assertEqual(schema_lite.validate(None, schema), [])
        self.assertTrue(schema_lite.validate("x", schema))

    def test_ref_resolution(self):
        schema = {"$defs": {"n": {"type": "integer"}}, "type": "object",
                  "properties": {"a": {"$ref": "#/$defs/n"}}}
        self.assertTrue(schema_lite.validate({"a": "x"}, schema))
        self.assertEqual(schema_lite.validate({"a": 1}, schema), [])

    def test_one_of_uses_discriminator_for_focused_errors(self):
        schema = {"oneOf": [
            {"type": "object", "required": ["kind", "x"], "properties": {"kind": {"const": "a"}, "x": {"type": "integer"}}},
            {"type": "object", "required": ["kind", "y"], "properties": {"kind": {"const": "b"}, "y": {"type": "string"}}},
        ]}
        self.assertEqual(schema_lite.validate({"kind": "a", "x": 1}, schema), [])
        errors = schema_lite.validate({"kind": "b", "y": 5}, schema)
        self.assertEqual(len(errors), 1)
        self.assertIn("$.y", errors[0])
        errors = schema_lite.validate({"kind": "c"}, schema)
        self.assertIn("is not one of", errors[0])

    def test_one_of_without_discriminator_needs_exactly_one_match(self):
        schema = {"oneOf": [{"type": "integer"}, {"type": "string"}]}
        self.assertEqual(schema_lite.validate(1, schema), [])
        self.assertTrue(schema_lite.validate(1.5, schema))

    def test_unsupported_keyword_raises(self):
        with self.assertRaises(ValueError):
            schema_lite.validate({}, {"type": "object", "patternProperties": {}})

    def test_error_paths_are_precise(self):
        schema = {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "integer"}}}}
        errors = schema_lite.validate({"items": [1, "x"]}, schema)
        self.assertIn("$.items[1]", errors[0])


if __name__ == "__main__":
    unittest.main()
