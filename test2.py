from PIL import Image

background = Image.open("border/test.png")
foreground = Image.open("border/border2.png")
s = background.size
foreground = foreground.resize(s)
background.paste(foreground, (0, 0), foreground)
