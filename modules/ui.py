import os
import gradio as gr
import gradio.routes


from modules import ui_extra_networks
from .paths import script_path, data_path
from .scripts import list_files_with_name
from .ui_components import FormRow

def webpath(fn):
    if fn.startswith(script_path):
        web_path = os.path.relpath(fn, script_path).replace('\\', '/')
    else:
        web_path = os.path.abspath(fn)

    return f'file={web_path}?{os.path.getmtime(fn)}'

def javascript_html():
    script_js = os.path.join(script_path, "script.js")
    head = f'<script type="text/javascript" src="{webpath(script_js)}"></script>\n'

    # inline = f"{localization.localization_js(shared.opts.localization)};"
    # if cmd_opts.theme is not None:
    #     inline += f"set_theme('{cmd_opts.theme}');"

    # for script in modules.scripts.list_scripts("javascript", ".js"):
    #     head += f'<script type="text/javascript" src="{webpath(script.path)}"></script>\n'

    # for script in modules.scripts.list_scripts("javascript", ".mjs"):
    #     head += f'<script type="module" src="{webpath(script.path)}"></script>\n'

    #head += f'<script type="text/javascript">{inline}</script>\n'

    return head


def css_html():
    head = ""

    def stylesheet(fn):
        return f'<link rel="stylesheet" property="stylesheet" href="{webpath(fn)}">'

    for cssfile in list_files_with_name("style.css"):
        if not os.path.isfile(cssfile):
            continue

        head += stylesheet(cssfile)

    if os.path.exists(os.path.join(data_path, "user.css")):
        head += stylesheet(os.path.join(data_path, "user.css"))

    return head

def reload_javascript():
    js = javascript_html()
    css = css_html()

    def template_response(*args, **kwargs):
        res = gradio.routes.templates.TemplateResponse(*args, **kwargs)
        res.body = res.body.replace(b'</head>', f'{js}</head>'.encode("utf8"))
        res.body = res.body.replace(b'</body>', f'{css}</body>'.encode("utf8"))
        res.init_headers()
        return res



def create_ui():
    
    reload_javascript()
    
    with gr.Blocks() as demo:
        
        with gr.Row():
            extra_button = gr.Button("submit")
        with gr.Row():
            with gr.Column():
                pic_uploader = gr.Image()
            with gr.Column():
                pic_shower = gr.Image()
        
        with FormRow(variant="compact") as extra_networks:
            ui_extra_networks.create_ui(extra_networks, extra_button, "text")
            
            
    return demo