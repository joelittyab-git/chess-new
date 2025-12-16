import wx
from wx.svg import SVGimage
from unit import Unit
from dynamic import rasterize_svg
    
    

app = wx.App()
    
img = Unit.get_svg(Unit.BLACK_PAWN)
bmp = rasterize_svg(img, (100,100))

def paint(event):
     dc = wx.PaintDC(panel)
     dc.SetBrush(wx.Brush("blue"))
     
     dc.DrawBitmap(bmp, (50,50))
     

frame = wx.Frame(None)

panel =  wx.Panel(frame)

panel.Bind(wx.EVT_PAINT, paint)

timer = wx.Timer(panel)


frame.Show()

app.MainLoop()
