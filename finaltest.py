import wx
from dynamic import PieceManager
import MoveGen

COLOUR = True

#time in seconds setting intial time 
GAME_TIME = 600  

def change_colour():

    def BLACK(event):
        global COLOUR
        COLOUR = False
        colourframe.Close()
        play()
    def BLUE(event):
          global COLOUR
          COLOUR = True
          colourframe.Close()
          play()


    colourframe=wx.Frame(None,title="colour selector",size = (900,900))

    Change_black = wx.Button(colourframe, label="BLACK BOARD", size=(300,300))
    Change_black.SetFont(wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

    Change_blue=wx.Button(colourframe, label="BLUE BOARD", size=(300,300))
    Change_blue.SetFont(wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

    Change_black.Bind(wx.EVT_BUTTON,BLACK)
    Change_blue.Bind(wx.EVT_BUTTON,BLUE)

    colour_sizer = wx.BoxSizer(wx.VERTICAL)
    colour_sizer.Add(Change_black ,0, wx.ALIGN_CENTER | wx.TOP, 40)
    colour_sizer.Add(Change_blue,0,wx.ALIGN_CENTER | wx.TOP, 40)
    colourframe.SetSizer(colour_sizer)


    colourframe.Show()


def play():

    white_time = GAME_TIME
    black_time = GAME_TIME
    turn = "white"

    BOARDSIZE=8
    SQUAREPIX=60
    BOARDPIX=BOARDSIZE * SQUAREPIX
    print("PLaying")

    frame=wx.Frame(None,title="Chessboard",size = (BOARDPIX+500,BOARDPIX+240))
    frame.SetMinClientSize((BOARDPIX+500,BOARDPIX+240))
    frame.SetMaxClientSize((BOARDPIX+500,BOARDPIX+240))
    

    #def colour(event):


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



    container = wx.Panel(frame)

    main_sizer = wx.BoxSizer(wx.HORIZONTAL)
    

    # Top: captured black
    captured_black_panel = wx.Panel(container, size=(-1, 40))
    captured_black_panel.SetBackgroundColour("#eeeeee")

    # Middle: board
    board_panel = wx.Panel(container, size=(480, 480))
    board_panel.SetBackgroundColour("white")

    # Bottom: captured white
    captured_white_panel = wx.Panel(container, size=(-1, 80))
    captured_white_panel.SetBackgroundColour("#eeeeee")



# ---------------- CLOCK + CAPTURED PANELS FIX ----------------
    
    def format_time(t):
        return f"{t//60:02d}:{t%60:02d}"
    clock_panel = wx.Panel(container, size=(200, -1))
    clock_panel.SetBackgroundColour("#dddddd")
# Black clock

    clock_sizer = wx.BoxSizer(wx.VERTICAL)

    black_clock = wx.StaticText(clock_panel, label=format_time(black_time))
    black_clock.SetFont(wx.Font(18, wx.FONTFAMILY_SWISS,
                                wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

    white_clock = wx.StaticText(clock_panel, label=format_time(white_time))
    white_clock.SetFont(wx.Font(18, wx.FONTFAMILY_SWISS,
                                wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

    clock_sizer.AddStretchSpacer()
    clock_sizer.Add(black_clock, 0, wx.ALIGN_CENTER | wx.BOTTOM, 40)
    clock_sizer.AddStretchSpacer()
    clock_sizer.Add(white_clock, 0, wx.ALIGN_CENTER)
    clock_sizer.AddStretchSpacer()

    clock_panel.SetSizer(clock_sizer)


# --------------------------------------------------------------


    timer = wx.Timer(frame)
    
    def switch_turn():
        nonlocal turn
        turn = "black" if turn == "white" else "white"


    def on_tick(event):
        nonlocal white_time, black_time, turn

        if turn == "white":
            white_time -= 1
            white_clock.SetLabel(format_time(white_time))
            if white_time <= 0:
                timer.Stop()
                wx.MessageBox("White ran out of time!")
                frame.Destroy()
        else:
            black_time -= 1
            black_clock.SetLabel(format_time(black_time))
            if black_time <= 0:
                timer.Stop()
                wx.MessageBox("Black ran out of time!")
                frame.Destroy()

    frame.Bind(wx.EVT_TIMER, on_tick, timer)
    timer.Start(1000)

    

    board_column = wx.BoxSizer(wx.VERTICAL)

    board_column.Add(captured_black_panel, 0, wx.EXPAND | wx.BOTTOM, 5)
    board_column.Add(board_panel, 0, wx.ALIGN_CENTER)
    board_column.Add(captured_white_panel, 0, wx.EXPAND | wx.TOP, 5)

    main_sizer.Add(board_column, 0, wx.ALL, 10)
    main_sizer.Add(clock_panel, 0, wx.EXPAND | wx.LEFT, 20)

    container.SetSizer(main_sizer)
 

    
    print(COLOUR)
    manager = PieceManager(centers,board_panel,captured_white_panel,captured_black_panel,colour=COLOUR,switch_turn=switch_turn)

 
    frame.Show()


def versus(event):

    
    def go_back(event):
        event.GetEventObject().GetParent().GetParent().Close()
    
    def ten(event):
        global GAME_TIME
        GAME_TIME = 10*60
        event.GetEventObject().GetTopLevelParent().Close()
        change_colour()

    def thirty(event):
        global GAME_TIME
        GAME_TIME = 30*60
        event.GetEventObject().GetTopLevelParent().Close()
        change_colour()

    def hour(event):
        global GAME_TIME
        GAME_TIME = 60*60
        event.GetEventObject().GetTopLevelParent().Close()
        change_colour()

    time_frame = wx.Frame(None, title="⚔️ Play Versus ⚔", size=(1600, 900))
    time_panel = wx.Panel(time_frame)
    time_panel.SetBackgroundColour("Black")

    title2 = wx.StaticText(time_panel, label="Select Timer")
    font = wx.Font(45, wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_BOLD)
    title2.SetForegroundColour("white")
    title2.SetFont(font)


    button_size = (400, 120)
    btn_ten = wx.Button(time_panel, label="10 Minute ⏲️", size=button_size)
    btn_thirty = wx.Button(time_panel, label="30 Minute ⏲️", size=button_size)
    btn_hour = wx.Button(time_panel, label="60 Minute ⏲️", size=button_size)
    btn_go_back= wx.Button(time_panel,label= "Go back",size=(200,60))

    btn_font = wx.Font(22, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
    btn_ten.SetFont(btn_font)
    btn_thirty.SetFont(btn_font)
    btn_hour.SetFont(btn_font)
    btn_go_back.SetFont(btn_font)

    btn_go_back.Bind(wx.EVT_BUTTON,go_back)
    btn_ten.Bind(wx.EVT_BUTTON,ten)
    btn_thirty.Bind(wx.EVT_BUTTON,thirty)
    btn_hour.Bind(wx.EVT_BUTTON,hour)

    vbox_time = wx.BoxSizer(wx.VERTICAL)


    vbox_time.Add(title2, 0, wx.ALIGN_CENTER | wx.TOP, 150)


    vbox_time.Add(btn_ten, 0, wx.ALIGN_CENTER | wx.TOP, 30)
    vbox_time.Add(btn_thirty, 0, wx.ALIGN_CENTER | wx.TOP, 30)
    vbox_time.Add(btn_hour, 0, wx.ALIGN_CENTER | wx.TOP, 30)
    vbox_time.Add(btn_go_back, 0, wx.ALIGN_CENTER | wx.TOP, 30)
    time_panel.SetSizer(vbox_time)

    
    time_frame.Show()

def chessbot(event):
    wx.MessageBox("Play ChessBot clicked")

def analyse(event):
    wx.MessageBox("Analyse clicked")

def exit(event):
    wx.Exit()

app = wx.App()

start_frame = wx.Frame(None, title="C H E S S   A P P", size=(1600, 900))
panel = wx.Panel(start_frame)
panel.SetBackgroundColour("Black")


title = wx.StaticText(panel, label="Chess App")
font = wx.Font(45, wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_BOLD)
title.SetForegroundColour("white")
title.SetFont(font)


button_size = (400, 120)
btn_versus = wx.Button(panel, label="⚔️ Play Versus ⚔️", size=button_size)
#btn_chessbot = wx.Button(panel, label="🤖 Play ChessBot 🤖", size=button_size)
#btn_analyse = wx.Button(panel, label="🔍 Analyse 🔍", size=button_size)
btn_exit = wx.Button(panel,label="Exit",size = (200,60))

btn_font = wx.Font(22, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
btn_versus.SetFont(btn_font)
#btn_chessbot.SetFont(btn_font)
#btn_analyse.SetFont(btn_font)
btn_exit.SetFont(btn_font)


btn_versus.Bind(wx.EVT_BUTTON, versus)
#btn_chessbot.Bind(wx.EVT_BUTTON, chessbot)
#btn_analyse.Bind(wx.EVT_BUTTON, analyse)
btn_exit.Bind(wx.EVT_BUTTON,exit)


vbox = wx.BoxSizer(wx.VERTICAL)


vbox.Add(title, 0, wx.ALIGN_CENTER | wx.TOP, 150)


vbox.Add(btn_versus, 0, wx.ALIGN_CENTER | wx.TOP, 40)
#vbox.Add(btn_chessbot, 0, wx.ALIGN_CENTER | wx.TOP, 40)
#vbox.Add(btn_analyse, 0, wx.ALIGN_CENTER | wx.TOP, 40)
vbox.Add(btn_exit,0,wx.ALIGN_CENTER | wx.TOP, 40)

panel.SetSizer(vbox)

start_frame.Show()
app.MainLoop()