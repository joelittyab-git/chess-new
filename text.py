import wx

def click(event:wx.Event):
     pass
     

app = wx.App()
frame = wx.Frame(None, title="New Window")
panel = wx.Panel(frame)

text = wx.StaticText(panel, label="This is my name, and this is a wx python text",pos=(100,100))
text.SetFont(wx.Font(20, wx.FONTFAMILY_SCRIPT, wx.FONTSTYLE_SLANT, wx.FONTWEIGHT_EXTRABOLD,faceName="Segoe Script"))
text.SetForegroundColour(wx.Colour(14,100,12))

button = wx.Button(panel, pos=(500,500))
button.SetLabelText("Chnage colour")
button.Bind(wx.EVT_LEFT_DOWN,click)

frame.Show()
app.MainLoop()