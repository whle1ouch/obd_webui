# import gradio as gr


# class FormComponent:
#     def get_expected_parent(self):
#         return gr.components.Form


# class FormRow(FormComponent, gr.Row):
#     """Same as gr.Row but fits inside gradio forms"""

#     def get_block_name(self):
#         return "row"
    

# class DropdownMulti(FormComponent, gr.Dropdown):
#     """Same as gr.Dropdown but always multiselect"""
#     def __init__(self, **kwargs):
#         super().__init__(multiselect=True, **kwargs)

#     def get_block_name(self):
#         return "dropdown"