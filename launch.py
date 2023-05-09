import gradio as gr
import modules.ui



if __name__ == "__main__":
    demo = modules.ui.create_ui()
    demo.queue(20).launch()