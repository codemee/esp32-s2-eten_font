# 安裝模組
# 開發版要先連上網路
# import mip
# mip.install('ssd1306')

from ssd1306 import SSD1306_I2C
from machine import SoftI2C, Pin
from framebuf import FrameBuffer, MONO_HLSB
from big5_utils import lookup_for_font_info

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

