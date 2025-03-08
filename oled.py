# 安裝模組
# 開發版要先連上網路
# import mip
# mip.install('ssd1306')

from ssd1306 import SSD1306_I2C
from machine import SoftI2C, Pin
from framebuf import FrameBuffer, MONO_HLSB

i2c = SoftI2C(scl=Pin(9), sda=Pin(8))
oled = SSD1306_I2C(128, 64, i2c)

# 放置已開啟的字型檔以及相關資訊
font_files = {
    # '代號'： (檔案代碼, 寬度, 高度, 補白)
    # 補白是指例如 24x24 中文字形搭配的半形英文字型，應為 12x24
    # 但會用 2 個 byts 放 12 個 bits，會有 4 個 bits 沒用
    # 實際顯示時可以重疊到這 4 個 bits 的空間
    'asc': (open('./fonts/ascfntkc.24', 'rb'), 16, 24, 4), # 英數字（延伸版 ASCII 字集）
    'std': (open('./fonts/stdfont.24f', 'rb'), 24, 24, 0), # 中文字
    'spc': (open('./fonts/spcfont.24', 'rb'), 24, 24, 0)   # 全形符號
}

# 在 oled 指定位置繪製單一字元
def draw_ch(oled, ch_info, x, y):
    f = font_files[ch_info['type']][0]      # 字元所屬字型檔
    width = font_files[ch_info['type']][1]  # 字元寬度
    height = font_files[ch_info['type']][2] # 字元高度
    bytes_per_char = width * height // 8    # 單一字元耗用位元組數
    f.seek(ch_info['no'] * bytes_per_char)  # 移到字型檔中該字元位置
    pic_bytes = f.read(bytes_per_char)      # 讀取該字元圖形資料
    pic_array = bytearray(pic_bytes)        # 轉換成位元組陣列
    frame = FrameBuffer(                    # 建立影格
        pic_array,                         
        width,
        height,
        MONO_HLSB # 單色圖形、每個位元組代表水平排列的 8 個像素、最高位元是最左邊的點
    )
    oled.blit(frame, x, y) # 繪製圖形

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

x = 0
y = 16
text = '天氣真好！\nGo→玩A'
for c in text:
    if c == '\n':
        y += 25
        x = 0
        continue
    ch_info = lookup_for_font_info(c)
    draw_ch(oled, ch_info, x, y)
    font_info = font_files[ch_info['type']]
    x += font_info[1] + 1 - font_info[3] # 英文字會多佔用空間
oled.show()

