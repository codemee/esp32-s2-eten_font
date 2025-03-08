from big5_utils import show_font, lookup_for_font_info

font_files = {
    # '代號'： (檔案代碼, 寬度, 高度, 補白)
    # 補白是指例如 24x24 中文字形搭配的半形英文字型，應為 12x24
    # 但會用 2 個 byts 放 12 個 bits，會有 4 個 bits 沒用
    # 實際顯示時可以重疊到這 4 個 bits 的空間
    'asc': (open('./fonts/ascfntkc.24', 'rb'), 16, 24, 4),
    'std': (open('./fonts/stdfont.24f', 'rb'), 24, 24, 0),
    'spc': (open('./fonts/spcfont.24', 'rb'), 24, 24, 0)
}


while True:
    text = input('輸入中文：')
    if text == '':
        break
    for ch in text:
        font_info = lookup_for_font_info(ch)
        print('--------------------------------')
        show_font(font_info, font_files)
