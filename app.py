import gradio as gr
from big5_utils import ch_to_font_info

def get_font_info_list(text):
    font_info_list = []
    for ch in text:
        font_info = ch_to_font_info(ch)
        font_info_list.append(font_info)
    return str(font_info_list)

converter = gr.Interface(
    fn=get_font_info_list,
    inputs=[
        gr.Textbox(
            label='請輸入要轉換的文字', 
            value='',
            placeholder='輸入要轉換的文字'
        ),
    ],
    outputs=[
        gr.TextArea(
            label='轉換後的字型資訊', 
            type='text',
            placeholder='轉換後的字型資訊',
        )
    ]
)

converter.queue()
converter.launch()
