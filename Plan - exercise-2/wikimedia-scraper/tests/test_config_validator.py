import unittest
import tempfile
import os
import yaml

from config_validator import ConfigValidator


class TestConfigValidator(unittest.TestCase):
    def _write_config(self, data):
        fd, path = tempfile.mkstemp(suffix='.yaml')
        os.close(fd)
        with open(path, 'w') as f:
            yaml.safe_dump(data, f)
        return path

    def test_valid_config_loads(self):
        data = {
            'keyword': 'butterfly',
            'offset': 0,
            'batch_size': 5,
            'max_retries': 3,
            'request_timeout': 10
        }
        path = self._write_config(data)
        try:
            cfg = ConfigValidator.load_config(path)
            self.assertEqual(cfg['keyword'], 'butterfly')
            self.assertEqual(cfg['offset'], 0)
            self.assertEqual(cfg['batch_size'], 5)
        finally:
            os.remove(path)

    def test_missing_keyword_raises(self):
        data = {'offset': 0, 'batch_size': 5}
        path = self._write_config(data)
        try:
            with self.assertRaises(ValueError):
                ConfigValidator.load_config(path)
        finally:
            os.remove(path)

    def test_invalid_batch_size_raises(self):
        data = {'keyword': 'x', 'batch_size': 3}
        path = self._write_config(data)
        try:
            with self.assertRaises(ValueError):
                ConfigValidator.load_config(path)
        finally:
            os.remove(path)

    def test_negative_offset_raises(self):
        data = {'keyword': 'x', 'offset': -1, 'batch_size': 5}
        path = self._write_config(data)
        try:
            with self.assertRaises(ValueError):
                ConfigValidator.load_config(path)
        finally:
            os.remove(path)

    def test_output_file_type_invalid(self):
        data = {'keyword': 'x', 'batch_size': 5, 'output_file': 123}
        path = self._write_config(data)
        try:
            with self.assertRaises(ValueError):
                ConfigValidator.load_config(path)
        finally:
            os.remove(path)

    def test_non_dict_yaml_raises(self):
        # write a YAML list instead of dict
        path = self._write_config(['a', 'b', 'c'])
        try:
            with self.assertRaises(ValueError):
                ConfigValidator.load_config(path)
        finally:
            os.remove(path)


if __name__ == '__main__':
    unittest.main()
