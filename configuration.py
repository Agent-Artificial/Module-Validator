import os
import sys
import yaml
import copy
from munch import DefaultMunch
from bittensor.config import config as conf
import argparse


class config(DefaultMunch):
    def __init__(self, parser=None, args=None, strict=False, default=None):
        super().__init__(default)
        self["__is_set"] = {}

        if parser is None:
            return

        # Add config-specific arguments
        self._add_config_arguments(parser)

        # Parse arguments
        args = sys.argv[1:] if args is None else args
        config_params = self.__parse_args__(args, parser, False)

        # Load config from file if specified
        self._load_config_file(parser, args)

        # Parse arguments again with potential new defaults
        params = self.__parse_args__(args, parser, config_params.strict or strict)

        # Split params and add to config
        self.__split_params__(params, self)

        # Track which parameters are set
        self._track_set_parameters(parser, args, params)
        

    def _load_config_file(self, parser, args):
        if config_file_path := self._get_config_file_path(parser, args):
            with open(config_file_path) as f:
                params_config = yaml.safe_load(f)
                parser.set_defaults(**params_config)

    @staticmethod
    def _get_config_file_path(parser, args):
        try:
            return os.path.expanduser(vars(parser.parse_known_args(args)[0])["config"])
        except:
            return None

    @staticmethod
    def __parse_args__(args, parser, strict):
        if not strict:
            params, unrecognized = parser.parse_known_args(args=args)
            for unrec in unrecognized:
                if unrec.startswith("--") and unrec[2:] in params.__dict__:
                    setattr(params, unrec[2:], True)
        else:
            params = parser.parse_args(args=args)
        return params

    @staticmethod
    def __split_params__(params, _config):
        for arg_key, arg_val in params.__dict__.items():
            keys = arg_key.split(".")
            head = _config
            while len(keys) > 1:
                if not hasattr(head, keys[0]) or head[keys[0]] is None:
                    head[keys[0]] = config()
                head = head[keys[0]]
                keys = keys[1:]
            head[keys[0]] = arg_val

    def _track_set_parameters(self, parser, args, params):
        parser_no_defaults = copy.deepcopy(parser)
        parser_no_defaults.set_defaults(**{key: argparse.SUPPRESS for key in params.__dict__})
        params_no_defaults = self.__parse_args__(args, parser_no_defaults, False)
        self["__is_set"] = {k: True for k, v in params_no_defaults.__dict__.items() if v != argparse.SUPPRESS}
        
        
    def __deepcopy__(self, memo):
        config_copy = config()
        memo[id(self)] = config_copy
        for k, v in self.items():
            config_copy[k] = copy.deepcopy(v, memo)
        return config_copy

    def __str__(self):
        visible = copy.deepcopy(self.toDict())
        visible.pop("__parser", None)
        visible.pop("__is_set", None)
        return "\n" + yaml.dump(visible, sort_keys=False)

    def is_set(self, param_name):
        return self.get("__is_set", {}).get(param_name, False)

    @classmethod
    def merge(cls, a, b):
        for key in b:
            if key in a and isinstance(a[key], dict) and isinstance(b[key], dict):
                cls.merge(a[key], b[key])
            else:
                a[key] = b[key]
        return a

parser = argparse.ArgumentParser()
config = config(parser, args=[sys.argv[i] for i in range(1, len(sys.argv))], strict=False, default=conf)
print(config)