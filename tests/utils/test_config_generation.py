import unittest
import os
import ast
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from collections import defaultdict
from utils.config_generator import (
    extract_argparse_arguments,
    parse_add_argument,
    find_arguments,
    parse_default_value,
    get_field_type,
    parse_items_to_nested_dict,
    convert_defaultdict_to_dict,
    save_file,
    save_template_file,
    create_paths,
    parse_subnet_folder,
    nested_dict
)

class TestYourModuleName(unittest.TestCase):

    def setUp(self):
        self.file_path = "tests/test_module/source.py"
        self.file_content = """
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--arg1', type=str, default='default1', help='Argument 1')
parser.add_argument('--arg2', type=int, default=2, help='Argument 2')
        """
        self.mock_open = mock_open(read_data=self.file_content)

    def test_extract_argparse_arguments(self):
        with patch("builtins.open", self.mock_open):
            arguments = extract_argparse_arguments(self.file_path)
            self.assertEqual(len(arguments), 2)
            self.assertEqual(arguments[0]['name'], 'arg1')
            self.assertEqual(arguments[0]['type'], 'str')
            self.assertEqual(arguments[0]['default'], 'default1')
            self.assertEqual(arguments[0]['help'], 'Argument 1')

    def test_parse_add_argument(self):
        node = ast.parse("parser.add_argument('--arg1', type=str, default='default1', help='Argument 1')").body[0].value
        arg_info = parse_add_argument(node)
        self.assertEqual(arg_info['name'], 'arg1')
        self.assertEqual(arg_info['type'], 'str')
        self.assertEqual(arg_info['default'], 'default1')
        self.assertEqual(arg_info['help'], 'Argument 1')

    def test_find_arguments(self):
        arguments = find_arguments(self.file_content)
        self.assertEqual(len(arguments), 2)
        self.assertEqual(arguments[0], ('--arg1', "'default1'"))

    def test_parse_default_value(self):
        node = ast.parse("'default1'").body[0].value
        default_value = parse_default_value(node)
        self.assertEqual(default_value, 'default1')

    def test_get_field_type(self):
        field_type = get_field_type("str")
        self.assertEqual(field_type, str)
        field_type = get_field_type("int")
        self.assertEqual(field_type, int)

    def test_parse_items_to_nested_dict(self):
        items = [{'name': 'arg1', 'type': 'str', 'default': 'default1', 'help': 'Argument 1'}]
        nested_dict = parse_items_to_nested_dict(items)
        self.assertIn('arg1', nested_dict)
        self.assertEqual(nested_dict['arg1']['default'], 'default1')

    def test_convert_defaultdict_to_dict(self):
        d = defaultdict(nested_dict)
        d['arg1']['type'] = 'str'
        normal_dict = convert_defaultdict_to_dict(d)
        self.assertIsInstance(normal_dict, dict)
        self.assertEqual(normal_dict['arg1']['type'], 'str')

    def test_save_file(self):
        with patch("builtins.open", self.mock_open):
            save_file(Path("test_output.txt"), "test content")
            self.mock_open.assert_called_once_with(Path("test_output.txt"), "w")
            self.mock_open().write.assert_called_once_with("test content")

    @patch("tests.test_module.target")
    def test_save_template_file(self, mock_save_file):
        templates = {
            "class": "class content",
            "argument": "argument content",
            "attribute": "attribute content",
            "environment": "environment content"
        }
        paths_dict = {
            "template_path": Path("tests/test_module/template.py"),
            "environment_path": Path("tests/test_module/test.env"),
            "generated_path": Path("tests/test_module/generated.py")
        }
        with patch("pathlib.Path.read_text", return_value="class_template"):
            save_template_file(templates, paths_dict)
            mock_save_file.assert_called()

    def test_create_paths(self):
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            paths_dict, file_dir = create_paths()
            self.assertIn("environment_path", paths_dict)
            mock_mkdir.assert_called()

    def test_parse_subnet_folder(self):
        with patch("os.walk") as mock_os_walk:
            mock_os_walk.return_value = [("root", [], ["file.py"])]
            with patch("builtins.open", self.mock_open):
                arguments = parse_subnet_folder("test_dir")
                self.assertEqual(len(arguments), 2)

if __name__ == "__main__":
    unittest.main()
