import argparse
import os

script_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

data_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

models_path = os.path.join(data_path, "models")
extensions_dir = os.path.join(data_path, "extensions")
extensions_builtin_dir = os.path.join(script_path, "extensions-builtin")