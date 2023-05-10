import argparse
import os
import json
import sys

from modules import errors
from modules.paths import data_path

parser = argparse.ArgumentParser()

parser.add_argument("--share", action="store_true")
parser.add_argument("--listen", action='store_true', help="launch gradio with 0.0.0.0 as server name, allowing to respond to network requests")
parser.add_argument("--server-name", type=str, help="Sets hostname of server", default=None)
parser.add_argument("-port", type=int, default=None)
parser.add_argument("--ui-settings-file", type=str, help="filename to use for ui settings", default=os.path.join(data_path, 'config.json'))

demo = None

cmd_opts, _ = parser.parse_known_args()

options_templates = {}

settings_components = None

restricted_opts = {
    "samples_filename_pattern",
    "directories_filename_pattern",
    "outdir_samples",
    "outdir_txt2img_samples",
    "outdir_img2img_samples",
    "outdir_extras_samples",
    "outdir_grids",
    "outdir_txt2img_grids",
    "outdir_save",
    "outdir_init_images"
    }

class Options:
    data = None
    data_labels = options_templates
    typemap = {int: float}

    def __init__(self):
        self.data = {k: v.default for k, v in self.data_labels.items()}

    def __setattr__(self, key, value):
        if self.data is not None:
            if key in self.data or key in self.data_labels:
                assert not cmd_opts.freeze_settings, "changing settings is disabled"

                info = opts.data_labels.get(key, None)
                comp_args = info.component_args if info else None
                if isinstance(comp_args, dict) and comp_args.get('visible', True) is False:
                    raise RuntimeError(f"not possible to set {key} because it is restricted")

                if cmd_opts.hide_ui_dir_config and key in restricted_opts:
                    raise RuntimeError(f"not possible to set {key} because it is restricted")

                self.data[key] = value
                return

        return super(Options, self).__setattr__(key, value)

    def __getattr__(self, item):
        if self.data is not None:
            if item in self.data:
                return self.data[item]

        if item in self.data_labels:
            return self.data_labels[item].default

        return super(Options, self).__getattribute__(item)

    def set(self, key, value):
        """sets an option and calls its onchange callback, returning True if the option changed and False otherwise"""

        oldval = self.data.get(key, None)
        if oldval == value:
            return False

        try:
            setattr(self, key, value)
        except RuntimeError:
            return False

        if self.data_labels[key].onchange is not None:
            try:
                self.data_labels[key].onchange()
            except Exception as e:
                errors.display(e, f"changing setting {key} to {value}")
                setattr(self, key, oldval)
                return False

        return True

    def get_default(self, key):
        """returns the default value for the key"""

        data_label = self.data_labels.get(key)
        if data_label is None:
            return None

        return data_label.default

    def save(self, filename):
        assert not cmd_opts.freeze_settings, "saving settings is disabled"

        with open(filename, "w", encoding="utf8") as file:
            json.dump(self.data, file, indent=4)

    def same_type(self, x, y):
        if x is None or y is None:
            return True

        type_x = self.typemap.get(type(x), type(x))
        type_y = self.typemap.get(type(y), type(y))

        return type_x == type_y

    def load(self, filename):
        with open(filename, "r", encoding="utf8") as file:
            self.data = json.load(file)

        bad_settings = 0
        for k, v in self.data.items():
            info = self.data_labels.get(k, None)
            if info is not None and not self.same_type(info.default, v):
                print(f"Warning: bad setting value: {k}: {v} ({type(v).__name__}; expected {type(info.default).__name__})", file=sys.stderr)
                bad_settings += 1

        if bad_settings > 0:
            print(f"The program is likely to not work with bad settings.\nSettings file: {filename}\nEither fix the file, or delete it and restart.", file=sys.stderr)

    def onchange(self, key, func, call=True):
        item = self.data_labels.get(key)
        item.onchange = func

        if call:
            func()

    def dumpjson(self):
        d = {k: self.data.get(k, self.data_labels.get(k).default) for k in self.data_labels.keys()}
        return json.dumps(d)

    def add_option(self, key, info):
        self.data_labels[key] = info

    def reorder(self):
        """reorder settings so that all items related to section always go together"""

        section_ids = {}
        settings_items = self.data_labels.items()
        for k, item in settings_items:
            if item.section not in section_ids:
                section_ids[item.section] = len(section_ids)

        self.data_labels = {k: v for k, v in sorted(settings_items, key=lambda x: section_ids[x[1].section])}

    def cast_value(self, key, value):
        """casts an arbitrary to the same type as this setting's value with key
        Example: cast_value("eta_noise_seed_delta", "12") -> returns 12 (an int rather than str)
        """

        if value is None:
            return None

        default_value = self.data_labels[key].default
        if default_value is None:
            default_value = getattr(self, key, None)
        if default_value is None:
            return None

        expected_type = type(default_value)
        if expected_type == bool and value == "False":
            value = False
        else:
            value = expected_type(value)

        return value

config_filename = cmd_opts.ui_settings_file

opts = Options()
if os.path.exists(config_filename):
    opts.load(config_filename)