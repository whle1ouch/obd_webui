import os
import gradio as gr
import gradio.routes


from modules import ui_extra_networks
from modules.paths import script_path, data_path
from modules.scripts import list_files_with_name
from modules.shared import opts
from modules import script_callbacks
from modules import shared
from modules import call_queue


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

def get_value_for_setting(key):
    value = getattr(opts, key)

    info = opts.data_labels[key]
    args = info.component_args() if callable(info.component_args) else info.component_args or {}
    args = {k: v for k, v in args.items() if k not in {'precision'}}

    return gr.update(value=value, **args)

def create_ui():
    
    reload_javascript()
    from modules.detects import image_detect, video_detect
    
    with gr.Blocks() as image_interface:
        with gr.Row():
            with gr.Column(variant="compact", scale=6):
                with gr.Row(elem_id="models"):
                    model_name = gr.Dropdown(["yolov4", "yolov5"], label="select detect model")
                    model_checkpoint = gr.Dropdown(["yolov4.pth", "yolov5.pth"], label="select model checkpoint")
                
                with gr.Row(elem_id="image_size"):
                    image_height = gr.Slider(1, 512, 204, step=1, label="image height")
                    image_width = gr.Slider(1, 512, 204, step=1, label="image width")
            with gr.Column(variant="compact"):
                with gr.Row():
                    with gr.Column():
                        submit_button = gr.Button("Submit", elem_id="image_submit")
            
        with gr.Row():
            with gr.Column():
                pic_uploader = gr.Image()
            with gr.Column():
                pic_shower = gr.AnnotatedImage()
                
        image_detect_args = dict(
            fn=call_queue.wrap_gradio_gpu_call(image_detect, extra_outputs=None),
            inputs=[
                pic_uploader,
                image_height,
                image_width,
            ],
            outputs=[pic_shower]
        )
        submit_button.click(**image_detect_args)
                
    
    with gr.Blocks() as video_interface:
        with gr.Row():
            with gr.Column(variant="compact", scale=6):
                with gr.Row(elem_id="models"):
                    model_name = gr.Dropdown(["yolov4", "yolov5"], label="select detect model")
                    model_checkpoint = gr.Dropdown(["yolov4.pth", "yolov5.pth"], label="select model checkpoint")
                
                with gr.Row(elem_id="image_size"):
                    image_height = gr.Slider(1, 512, 204, step=1, label="image height")
                    image_width = gr.Slider(1, 512, 204, step=1, label="image width")
            with gr.Column(variant="compact"):
                with gr.Row():
                    with gr.Column():
                        run_button = gr.Button("Run", elem_id="image_submit")
        with gr.Row():
            with gr.Column():
                pic_uploader = gr.Video(label="upload the video")
            with gr.Column():
                pic_shower = gr.Video(interactive=False)
                    
    with gr.Blocks() as train_interface:
        with gr.Row():
            with gr.Column(variant="compact", scale=6):
                with gr.Row(elem_id="models"):
                    model_name = gr.Dropdown(["yolov4", "yolov5"], label="select detect model")
                    model_checkpoint = gr.Dropdown(["yolov4.pth", "yolov5.pth"], label="select model checkpoint")
                
                with gr.Row(elem_id="image_size"):
                    image_height = gr.Slider(1, 512, 204, step=1, label="image height")
                    image_width = gr.Slider(1, 512, 204, step=1, label="image width")
            with gr.Column(variant="compact"):
                with gr.Row():
                    with gr.Column():
                        run_button = gr.Button("Run", elem_id="image_submit")
        with gr.Row():
             train_progress = gr.Progress()
             
    interfaces = [
        (image_interface, "imageDetect", "imageDetect"),
        (video_interface, "videoDetect", "videoDetect"),
        (train_interface, "Train", "ti"),
    ]
    
    #interfaces += script_callbacks.ui_tabs_callback()
    #interfaces+= [(settings_interface, "Settings", "settings")]
    
    # shared.tab_names = []
    # for _interface, label, _ifid in interfaces:
    #     shared.tab_names.append(label)
        
    with gr.Blocks() as demo:
        
        with gr.Tabs(elem_id="tabs") as tabs:
            for interface, label, ifid in interfaces:
                # if label in shared.opts.hidden_tabs:
                #     continue
                with gr.TabItem(label, id=ifid, elem_id='tab_' + ifid):
                    interface.render()
            
    
        # components = []
        # component_dict = {}
        # shared.settings_components = component_dict
        
        # component_keys = [k for k in opts.data_labels.keys() if k in component_dict]
        
        # def get_settings_values():
        #         return [get_value_for_setting(key) for key in component_keys]
        
        # demo.load(fn=get_settings_values, inputs=[],outputs=[component_dict[k] for k in component_keys],queue=False,)
            
            
    return demo