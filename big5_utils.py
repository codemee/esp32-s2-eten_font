def ch_to_font_info(ch):
    big5_code = ch.encode('big5')
    return big5_code_to_font_info(big5_code)

def big5_code_to_font_info(big5_code):
    code = int.from_bytes(big5_code)
    # 半形英數字
    # ascxxx.xx 字型檔內容
    # 0x00 至 0xFF EASCII 字元
    if len(big5_code) == 1:
        return {'type': 'asc', 'no': big5_code[0]}
    
    # 全形字
    # 低位元組：0x40 至 0x7E
    #         0xA1 至 0xFE
    # 低位元組完整區段的字數
    low_chars = (0x7E - 0x40 + 1) + (0xFE - 0xA1 + 1)

    hi = big5_code[0]   # 高位元組
    low = big5_code[1]  # 低位元組

    no = -1 # 不在字型檔範圍內
    # 特殊符號
    # spcxxx.xx 字型檔內容
    # 高位元組：0xA140 至 0xA3(BF)
    if code >= 0xA140 and code <= 0xA3BF:
        no = (hi - 0xA1) * low_chars
        no += ((low - 0xA1) + (0x7E- 0x40 + 1)) if low >= 0xA1 else ((low - 0x40))
        return {'type': 'spc', 'no': no}
    
    # 中文字
    # stdxxx.xx 字型檔內容
    # 高位：0xA4 至 0xC6(7E) 常用字 5401 字
    #      0xC9 至 0xF9     次常用字 7693 字
    # encode 方法 轉不出 big5_code): 碼在 0xF9D5 後的字
    if code >= 0xA440 and code <= 0xC67E:
        no = ((hi - 0xA4) * low_chars)
    elif code >= 0xC940 and code <= 0xF9FE:
        no = ((hi - 0xC9 + (0xC6 - 0xA4)) * low_chars 
              + (0x7E - 0x40 + 1)) # 0xC640-0xC67E 的字數
    if no != -1:
        no += ((low - 0xA1) + (0x7E- 0x40 + 1)) if low >= 0xA1 else ((low - 0x40))
    # no -= 472
    # no = 5401
    return {'type': 'std', 'no': no}

big5_tables = [
    (0x00A2, 0x2642),
    (0x3000, 0x33D5),
    (0x4E00, 0x9FA4),
    (0xFA0C, 0xFFE3)
]

big5_table_file = open('./tables/big5_table.bin', 'rb')

def lookup_for_font_info(ch):
    utf16_code = ord(ch)
    if utf16_code <= 0x7F:
        big5_code = utf16_code.to_bytes()
    else:
        offset = 0
        for start, end in big5_tables:
            if utf16_code <= end:
                offset += (utf16_code - start) * 2
                big5_table_file.seek(offset)
                big5_code = big5_table_file.read(2)
                break
            else:
                offset += (end - start + 1) * 2
    print(f'big5_code: {big5_code.hex()}')
    return big5_code_to_font_info(big5_code)

# 用 O 表示 bit 1 顯示字形
def print_byte(b):
    out = bin(b)[2:].zfill(8).replace('0', ' ').replace('1', 'O')
    print(out, end='')

def show_font(ch_info, font_files):
    if ch_info['no'] == -1:
        print('字元不在字型檔範圍內')
        return
    f = font_files[ch_info['type']][0]
    width = font_files[ch_info['type']][1]
    height = font_files[ch_info['type']][2]
    bytes_per_char = width * height // 8
    f.seek(ch_info['no'] * bytes_per_char)
    data = f.read(bytes_per_char)
    for i in range(height):
        for j in range(width // 8):
            print_byte(data[i * (width // 8) + j])
        print('')