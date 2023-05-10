import os
import signal
import gradio as gr
import modules.ui

import modules.script_callbacks
from modules import shared
from modules import timer
from modules.shared import cmd_opts


if cmd_opts.server_name:
    server_name = cmd_opts.server_name
else:
    server_name = "0.0.0.0" if cmd_opts.listen else None

startup_timer = timer.Timer()

def initialize():
    
    
    
    def sigint_handler(sig, frame):
        print(f'Interrupted with signal {sig} in {frame}')
        os._exit(0)
    signal.signal(signal.SIGINT, sigint_handler)


def webui():
    
    initialize()
    
    modules.script_callbacks.before_ui_callback()
    startup_timer.record("scripts before_ui_callback")
    
    shared.demo = modules.ui.create_ui()
    startup_timer.record("create ui")
    
    shared.demo.queue(20)
    
    
    shared.demo.launch(share=cmd_opts.share,
                       server_name=cmd_opts.server_name,
                       server_port=cmd_opts.port,
                       )
    
    