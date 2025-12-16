from dynamic import PieceManager
import wx

app = wx.App()
frame = wx.Frame(None, title="Sample Chess Window",size=(1400,1000),style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
panel = wx.Panel(frame, size=frame.Size)
print(panel.Size)
print(frame.Size)
frame.Show()

PieceManager(None,panel=panel)
app.MainLoop()


board = [
    ["r","n","b","q","k","b","n","r"],
    ["p","p","p","p","p","p","p","p"],
    [".",".",".",".",".",".",".","."],
    [".",".",".",".",".",".",".","."],
    [".",".",".",".",".",".",".","."],
    [".",".",".",".",".",".",".","."],
    ["P","P","P","P","P","P","P","P"],
    ["R","N","B","Q","K","B","N","R"],
]



# import wx
# from wx.svg import SVGimage


# # ----------------------------------------------------------
# # UNIVERSAL SVG → BITMAP RASTERIZER  (works on all versions)
# # ----------------------------------------------------------
# def rasterize_svg(svg: SVGimage, target_size):
#     """
#     Convert an SVGimage into a wx.Bitmap at a proper size.
#     Works on versions where RenderToBitmap / SetScale are missing.
#     """

#     tw, th = target_size

#     # Render at a large size (fixes viewBox issues)
#     BIG_W = 800
#     BIG_H = 800

#     big_bmp = svg.ConvertToBitmap(width=BIG_W, height=BIG_H)

#     # Scale down with high quality
#     img = big_bmp.ConvertToImage()
#     img = img.Scale(tw, th, wx.IMAGE_QUALITY_HIGH)

#     return wx.Bitmap(img)


# # ----------------------------------------------------------
# # PANEL THAT DRAWS THE CHESS PIECE
# # ----------------------------------------------------------
# class BoardPanel(wx.Panel):
#     def __init__(self, parent):
#         super().__init__(parent)

#         # Load SVG once (example: black knight)
#         self.svg = SVGimage.CreateFromFile("./piece/icpieces/bN.svg")

#         self.Bind(wx.EVT_PAINT, self.on_paint)

#     def on_paint(self, event):
#         dc = wx.BufferedPaintDC(self)
#         dc.Clear()

#         # Rasterize SVG → bitmap at 100x100
#         bmp = rasterize_svg(self.svg, (100, 100))

#         # Draw the piece
#         dc.DrawBitmap(bmp, 100, 100, True)


# # ----------------------------------------------------------
# # FRAME AND APP
# # ----------------------------------------------------------
# class Main(wx.Frame):
#     def __init__(self):
#         super().__init__(None, title="Chess SVG Test", size=(600, 600))
#         BoardPanel(self)
#         self.Show()


# # ----------------------------------------------------------
# # RUN APPLICATION
# # ----------------------------------------------------------
# app = wx.App()
# Main()
# app.MainLoop()
