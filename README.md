# 使用倚天字型結構結合國喬中文字形在 ESP32-S2 控制 OLED 顯示中文

為了讓 ESP32-S2 可以在 OLED 上顯示中文，第一步想到的就是使用倚天中文字型檔，不過因為倚天中文字型檔需要授權，所以在 [AdafruitGFX-ChineseFont-Addon](https://github.com/will127534/AdafruitGFX-ChineseFont-Addon) 專案這裡找到了以國喬中文字形為基礎，整理成倚天中文字型檔結構（也就是個別字元字型排列順序）的字型檔，但因為這裡缺了 stdfont.15，所以只能使用 24x24 的字型，雖然可行，但在 0.96 吋上的 OLED 上等於只能顯示兩橫列、每列五個字的內容，所以最後我其實沒有採用此方案，而是改用 [fusion pixel font](https://github.com/codemee/esp32-s2-bitmap-font) 的方案。以下仍然說明此專案的內容。

## 說明

由於我的目的是想要在 ESP32-S2 上使用 MicroPython 在 OLED 顯示中文，但倚天中文字型檔的排列是以 BIG5 的順序，MicroPython 上 `str` 的 `encode` 方法並不支援 `encoding` 參數，無法直接轉成 BIG5 碼，所以我的作法就是針對中文字涵蓋的範圍，另外製作一個 UTF16 轉 BIG5 的對照表，表中有許多是 BIG5 沒有對照字的空位，不過因為比較散亂，所以我採用偷懶的作法，耗費空間來換取實作上的便利。

以下說明專案中個別檔案的作用：

|檔案|作用|
|---|---|
|fonts|這個資料夾下士從前面提到的 [AdafruitGFX-ChineseFont-Addon](https://github.com/will127534/AdafruitGFX-ChineseFont-Addon/tree/master/font) 取得的字型檔，其中副檔名表示是 16x15 還是 24x24 的字型，檔名字首 std 為中文字、spc 為特殊符號、asc 為英文半形字|
|tables\big5_table.bin|我製作出來的 UTF16 轉 BIG5 的對照表|
|big5_utils.py|工具模組，內含許多便於查表的函式|
|make_tables.py|製作轉碼對照表|
|test_tables.py|測試可以透過轉碼對照表從 UTF16 編碼字元轉成 BIG5 編碼|
|test_big5_utils.py|測試依據字元取得點陣圖資料|

`big5_utils.py` 中提供有以下函式：

|函式|說明|
|---|---|
|ch_to_font_info(ch)|取得指定字元在字型檔中的相關資訊，這個函式會直接透過 `str` 的 `encode` 方法從 UTF16 轉 BIG5，**不**適用 MicroPython|
|lookup_for_font_info(ch)|取得指定字元在字型檔中的相關資訊，這個函式會透過查對照表的方式從 UTF16 轉 BIG5，**專門**用在 MicroPython|
|big5_code_to_font_info(big5_code)|取得指定字元在字型檔中的相關資訊，傳入的參數是 `bytes` 型別的字元 BIG5 編碼，上面兩個函式都會轉叫用此函式完成最後的工作|
|print_byte(b)|以二進位格式顯示 `bytes` 資料，但會用大寫 'O' 顯示 1，空白顯示 0|
|show_font(ch_info, font_files)|字距字元的字型相關資訊顯示點陣圖，細節稍後說明|

由於倚天中文字形分散在三個個別檔案中，所以上述工具函式都只會查得該字元位於哪一個字型檔中，以及該字元在該字型檔中從 0 起算的序號，並以如下格式的字典傳回：

```python
{'type': 'std', 'no': no}
```

其中 `type` 項目可能值就是對應到三種檔案的 'std'、'spc' 或是 'asc'，而 `no` 項目就是該字元在字型檔中的序號。`show_font` 就是根據這樣的資訊從字型檔中取得點陣圖資料後再顯示，它的第二個參數必須傳入如下的字典：

```python
font_files = {
    # '代號'： (檔案代碼, 寬度, 高度, 補白)
    # 補白是指例如 24x24 中文字形搭配的半形英文字型，應為 12x24
    # 但會用 2 個 byts 放 12 個 bits，會有 4 個 bits 沒用
    # 實際顯示時可以重疊到這 4 個 bits 的空間
    'asc': (open('./fonts/ascfont12.bdf', 'rb'), 8, 12, 2),
    'std': (open('./fonts/stdfont.24f', 'rb'), 24, 24, 0),
    'spc': (open('./fonts/spcfont.24', 'rb'), 24, 24, 0)
}
```

你可以自由替換字型檔。

## MicroPython 用法

要在 MicroPython 上使用，必須將 fonts 與 tables 資料夾上傳到開發板，你可以把不需要用到的字型檔移除，我使用的 ESP32-S2 本身有 4MB 的 flash，通常在安裝完 MicroPython 韌體後都至少還有 2MB 的空間可用，所已上傳這些檔案綽綽有餘。另外還要上傳 big5_utils.py 檔，範例程式可參考 oled.py：

```python
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
```

