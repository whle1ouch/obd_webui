import gradio as gr

extra_pages = []

class ExtraNetworksUi:
    def __init__(self):
        self.pages = None
        self.stored_extra_pages = None

        self.button_save_preview = None
        self.preview_target_filename = None

        self.tabname = None


def pages_in_preferred_order(pages):
    tab_order = []

    def tab_name_score(name):
        name = name.lower()
        for i, possible_match in enumerate(tab_order):
            if possible_match in name:
                return i

        return len(pages)

    tab_scores = {page.name: (tab_name_score(page.name), original_index) for original_index, page in enumerate(pages)}

    return sorted(pages, key=lambda x: tab_scores[x.name])


def create_ui(container, button, tabname):
    ui = ExtraNetworksUi()
    ui.pages = []
    ui.stored_extra_pages = pages_in_preferred_order(extra_pages.copy())
    ui.tabname = tabname
    
    with gr.Tabs(elem_id=tabname+"_extra_tabs") as tabs:
        for page in ui.stored_extra_pages:
            with gr.Tab(page.title, id=page.title.lower().replace(" ", "_")):
                page_elem = gr.HTML(page.create_html(ui.tabname))
                ui.pages.append(page_elem)
    
    filter = gr.Textbox("", show_label=False, elem_id=tabname+"_extra_search", placeholder="Search...", visible=False)
    button_refresh = gr.Button("Refresh", elem_id=tabname+"_extra_refresh")
    ui.button_save_preview = gr.Button("Save preview", elem_id=tabname+"_save_preview", visible=False)
    ui.preview_target_filename = gr.Textbox("Preview save filename", elem_id=tabname+"_preview_filename", visible=False)
    
    def toggle_visibility(is_visible):
        is_visible = not is_visible
        return is_visible, gr.update(visible=is_visible), gr.update(variant=("secondary-down" if is_visible else "secondary"))

    state_visible = gr.State(value=False)
    button.click(fn=toggle_visibility, inputs=[state_visible], outputs=[state_visible, container, button])

    def refresh():
        res = []

        for pg in ui.stored_extra_pages:
            pg.refresh()
            res.append(pg.create_html(ui.tabname))

        return res

    button_refresh.click(fn=refresh, inputs=[], outputs=ui.pages)

    return ui
                                