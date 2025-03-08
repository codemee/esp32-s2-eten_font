from big5_utils import ch_to_font_info

count = 0

def make_big5_table(f, start, end):
    global count
    utf16_code = start
    max_code = 0
    min_code = -1
    for i in range(end - start + 1):
        try:
            ch = chr(utf16_code)
            big5_code = ch.encode('big5')
            if len(big5_code) == 1:
                print(f'{ch} is a half-width character')
                continue
            max_code = utf16_code
            if min_code == -1:
                min_code = utf16_code
            # no = ch_to_font_info(ch)['no']
            count += 1
        except UnicodeEncodeError:
            # no = 0
            big5_code = b'\x00\x00'
        # f.write(big5_code.to_bytes(2, 'little'))
        f.write(big5_code)
        utf16_code += 1

    print(f'最大字碼：{hex(max_code)}')
    print(f'最小字碼：{hex(min_code)}')
    print(f'累積共 {count} 個字元')

with open('big5_table.bin', 'wb') as f:
    # 0x0080-0x2FFF
    # 有效範圍 0x00a2-0x2642
    make_big5_table(f, 0x00a2, 0x2642)

    # 標點符號與全形字符：U+3000-U+3FFF（包含頓號、句號等）
    # 有效範圍 0x3000-0x33D5
    make_big5_table(f, 0x3000, 0x33D5)

    # make_big5_no_table('spc_table3.bin', 0x4000, 0x4dff)

    # CJK統一漢字：U+4E00-U+9FFF（涵蓋Big5收錄的13,060個漢字）
    # 有效範圍 0x4E00-0x9FA4
    make_big5_table(f, 0x4E00, 0x9FA4)

    # make_big5_no_table('spc_table3.bin', 0xA000, 0xf8ff)

    # 擴展漢字與兼容字符：U+F900-U+FFFF（部分Big5擴展字符的映射區域）
    # 有效範圍 0xfa0c-0xffe3
    make_big5_table(f, 0xFA0C, 0xFFE3)
