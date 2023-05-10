import sys
import traceback
from collections import namedtuple
import inspect
from typing import Optional, Dict, Any

def report_exception(c, job):
    print(f"Error executing callback {job} for {c.script}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    
    
ScriptCallback = namedtuple("ScriptCallback", ["script", "callback"])
callback_map = dict(
    callbacks_app_started = [],
    callbacks_model_loaded = [],
    callbacks_ui_tabs=[],
    callbacks_ui_train_tabs=[],
    callbacks_before_ui=[]
)


class UiTrainTabParams:
    def __init__(self, preview_params):
        self.preview_params = preview_params


def before_ui_callback():
    for c in reversed(callback_map['callbacks_before_ui']):
        try:
            c.callback()
        except Exception:
            report_exception(c, 'before_ui')


def add_callback(callbacks, fun):
    stack = [x for x in inspect.stack() if x.filename != __file__]
    filename = stack[0].filename if len(stack) > 0 else 'unknown file'

    callbacks.append(ScriptCallback(filename, fun))
    


def remove_current_script_callbacks():
    stack = [x for x in inspect.stack() if x.filename != __file__]
    filename = stack[0].filename if len(stack) > 0 else 'unknown file'
    if filename == 'unknown file':
        return
    for callback_list in callback_map.values():
        for callback_to_remove in [cb for cb in callback_list if cb.script == filename]:
            callback_list.remove(callback_to_remove)
            
            
def ui_tabs_callback():
    res = []

    for c in callback_map['callbacks_ui_tabs']:
        try:
            res += c.callback() or []
        except Exception:
            report_exception(c, 'ui_tabs_callback')

    return res


def ui_train_tabs_callback(params: UiTrainTabParams):
    for c in callback_map['callbacks_ui_train_tabs']:
        try:
            c.callback(params)
        except Exception:
            report_exception(c, 'callbacks_ui_train_tabs')
