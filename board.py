from dynamic import PieceManager

import MoveGen

import wx
BOARDSIZE=8
SQUAREPIX=60
BOARDPIX=BOARDSIZE * SQUAREPIX

app=wx.App(False)
frame=wx.Frame(None,title="Chessboard",size=(BOARDPIX+20,BOARDPIX+80))
# panel=wx.Panel(frame)
  

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

centers=[]

for row in range(BOARDSIZE):
     r = []
     for col in range(BOARDSIZE):
          x = col * SQUAREPIX + SQUAREPIX/4
          y = row * SQUAREPIX + SQUAREPIX/4
          r.append((x, y))
     centers.append(r)

# def PAINT(event):
#     dc = wx.PaintDC(panel)
#     for row in range(BOARDSIZE):
#         for col in range(BOARDSIZE):
#             x = col * SQUAREPIX
#             y = row * SQUAREPIX
#             if (row + col) % 2 == 0:
#                 dc.SetBrush(wx.Brush("white"))
#             else:
#                 color = "blue" if blublack else "black"
#                 dc.SetBrush(wx.Brush(color))
#             color = "blue" if blublack else "black"
#             dc.SetPen(wx.Pen(color))
#             dc.DrawRectangle(x, y, SQUAREPIX, SQUAREPIX)
# panel.Bind(wx.EVT_PAINT, PAINT)

# def toggle_color(event):
#     global blublack
#     blublack = not blublack
#     panel.Refresh()
# button = wx.Button(panel,label="Black and white <-> Blue and white", pos=(120, 500))
# button.Bind(wx.EVT_BUTTON,toggle_color)


container = wx.Panel(frame)

main_sizer = wx.BoxSizer(wx.VERTICAL)

# Top: captured black
captured_black_panel = wx.Panel(container, size=(-1, 80))
captured_black_panel.SetBackgroundColour("#eeeeee")

# Middle: board
board_panel = wx.Panel(container, size=(480, 480))
board_panel.SetBackgroundColour("white")

# Bottom: captured white
captured_white_panel = wx.Panel(container, size=(-1, 80))
captured_white_panel.SetBackgroundColour("#eeeeee")

main_sizer.Add(captured_black_panel, 0, wx.EXPAND | wx.ALL, 5)
main_sizer.Add(board_panel, 0)
main_sizer.Add(captured_white_panel, 0, wx.EXPAND | wx.ALL, 5)

container.SetSizer(main_sizer)

manager = PieceManager(centers, board_panel,captured_white_panel, captured_black_panel)


# container = wx.Panel(frame)

# board_panel = wx.Panel(container, size=(480, 480))
# captured_panel = wx.Panel(container, size=(200, 480))

# sizer = wx.BoxSizer(wx.HORIZONTAL)
# sizer.Add(board_panel, 0)
# sizer.Add(captured_panel, 0, wx.LEFT, 5)

# container.SetSizer(sizer)

# manager = PieceManager(centers, board_panel,captured_panel)


# t = PieceManager(centers, panel, None)


frame.Show()
app.MainLoop()