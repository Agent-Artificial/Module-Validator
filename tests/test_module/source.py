import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--arg1', type=str, default='default1', help='Argument 1')

parser.add_argument('--arg2', type=int, default=2, help='Argument 2')