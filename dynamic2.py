import wx
from wx import (
    Panel, BufferedPaintDC, Bitmap,
    Brush, Event, Colour
)

from wx.svg import SVGimage
from wx import IMAGE_QUALITY_HIGH, EVT_PAINT, EVT_LEFT_DOWN

import MoveGen
from unit import Unit


BLUEBLACK = True
SQAUREPIX = 60


# =========================
# Utility functions
# =========================

def rasterize_svg(svg: SVGimage, target_size):
    """Converts the image to a smaller size by first converting it into an image instance 
    and then converting it into bitmap
    """
    tw, th = target_size
    big = svg.ConvertToBitmap(width=800, height=800)
    img = big.ConvertToImage()
    img = img.Scale(tw, th, IMAGE_QUALITY_HIGH)
    return Bitmap(img)


# def generate_chess_centers(square_size=SQAUREPIX):
#     board = []
#     for row in range(8):
#         row_centers = []
#         for col in range(8):
#             center_x = col * square_size
#             center_y = row * square_size
#             row_centers.append((center_x, center_y))
#         board.append(row_centers)
#     return board


# =========================
# PieceManager (UI Layer)
# =========================

class PieceManager:

    def __init__(self, centers, panel: Panel, white_captured_panel:Panel, black_captured_panel:Panel, colour=False):
        self.centers = centers 
        # or generate_chess_centers()
        self.board_panel = panel

        self.whites_move = True
        self.selected_square = None     # Index of the selected square in the fen notation
        self.legal_moves = []           # A list of all the legal moves that the current piece can make
        self.highlight_points = []      # A lsit of points to be highlighted on the baord that the piece can move
        self.input_locked = False       # Locks the input pannel from any input
        
        # Panel containting the captured pieces
        self.white_captured_panel = white_captured_panel    
        self.black_captured_panel = black_captured_panel

        # A dictionary of items containting the piece symbol as the key and the rasterize bitmap image as the value
        self.loaded_svg = dict()
        self.preload_svg()

        # Chess engine
        self.ChessBoard = MoveGen.IB_ChessPy()
        self.ChessBoard.setCustomBoard(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        )
        self.fen = self.ChessBoard.board

        panel.Bind(EVT_PAINT, self.init_paint)
        panel.Bind(EVT_LEFT_DOWN, self.on_click)
        
        self.white_captured = list()
        self.black_captured = list()
        
        white_captured_panel.Bind(EVT_PAINT, self.display_captured_white)
        black_captured_panel.Bind(EVT_PAINT, self.display_captured_black)
        
        self.colour = ('white','black') if not colour else ("#f0f0f0",'#4287f5')
        self.highlight_colour = '#494eeb' if colour else '#f5473b'
        
        
    
    def display_captured_white(self, event):
        dc = BufferedPaintDC(self.white_captured_panel)
        dc.Clear()

        size = 40      
        padding = 6    

        for i, piece in enumerate(self.white_captured):
            bmp = self.loaded_svg[piece]
            x = i * (size + padding)
            y = 10
            dc.DrawBitmap(bmp, int(x), int(y), True)


    def display_captured_black(self, event):
        dc = BufferedPaintDC(self.black_captured_panel)
        dc.Clear()

        size = 40
        padding = 6

        for i, piece in enumerate(self.black_captured):
            bmp = self.loaded_svg[piece]
            x = i * (size + padding)
            y = 10
            dc.DrawBitmap(bmp, int(x), int(y), True)




    def ui_to_engine(self, row, col):
        """Conversion due to different sign conventions used in the UI and Engine
        """
        return col, 7 - row

    def engine_to_ui(self, x, y):
        return 7 - y, x

    # =====================
    # Rendering
    # =====================

    def preload_svg(self):
        svgs = Unit.load_all()
        for k, v in svgs.items():
            self.loaded_svg[k] = rasterize_svg(v, (60, 60))

    def PAINT(self, dc: BufferedPaintDC):
        """Function to draw the board"""
        for row in range(8):
            for col in range(8):
                color = self.colour[0] if (row + col) % 2 == 0 else self.colour[1]
                dc.SetBrush(wx.Brush(color))
                dc.SetPen(wx.Pen(color))
                x = col * SQAUREPIX
                y = row * SQAUREPIX
                dc.DrawRectangle(x,y,SQAUREPIX,SQAUREPIX)

    def configure_pieces(self, dc: BufferedPaintDC):
        for r in range(8):
            for c in range(8):
                piece = self.fen[r][c]
                if piece != '.':
                    x, y = self.centers[r][c]
                    dc.DrawBitmap(
                        self.loaded_svg[piece],
                        int(x), int(y),
                        True
                    )

    def highlight(self, point, dc):
        dc.SetBrush(wx.Brush(Colour(self.highlight_colour)))
        dc.DrawCircle(int(point[0]) + 15, int(point[1]) + 15, 10)

    def init_paint(self, event: Event):
        dc = BufferedPaintDC(self.board_panel)
        dc.SetBackground(Brush("white"))
        dc.Clear()

        self.PAINT(dc)
        self.configure_pieces(dc)

        for p in self.highlight_points:
            self.highlight(p, dc)

        self.highlight_points.clear()
        self.black_captured_panel.Refresh()
        self.white_captured_panel.Refresh()



    def on_click(self, event: Event):
        """Handles all clicks on the board"""
        if self.input_locked:
            return

        x, y = event.GetPosition()
        col = x // SQAUREPIX
        row = y // SQAUREPIX

        if not (0 <= row < 8 and 0 <= col < 8):
            return

        # Move execution
        if (row, col) in self.legal_moves:
            self.move(self.selected_square, (row, col))
            return

        piece = self.fen[row][col]
        if piece == '.':
            return

        if self.whites_move and piece.isupper():
            self.selected_square = (row, col)
            self.show_all_possible_moves(row, col)

        elif not self.whites_move and piece.islower():
            self.selected_square = (row, col)
            self.show_all_possible_moves(row, col)


    def show_all_possible_moves(self, row, col):
        """
        Gets all the legal moves for a specific piece and adds to the highlight points
        """
        engine_pos = self.ui_to_engine(row, col)
        moveDict, _ = self.ChessBoard.getLegalMoves(self.whites_move)

        moves = moveDict.get(engine_pos, set())

        self.legal_moves = [
            self.engine_to_ui(x, y) for (x, y) in moves
        ]

        self.highlight_points = [
            self.centers[r][c] for r, c in self.legal_moves
        ]

        self.board_panel.Refresh()

    def move(self, selected_square, clicked_square):
        sr, sc = selected_square
        tr, tc = clicked_square

        piece = self.fen[sr][sc]

        from_pos = self.ui_to_engine(sr, sc)
        to_pos = self.ui_to_engine(tr, tc)

        if self.fen[tr][tc]!='.':
            if self.whites_move:self.white_captured.append(self.fen[tr][tc])
            else:self.black_captured.append(self.fen[tr][tc])
        
        promote = None
        if piece.lower() == 'p' and to_pos[1] in (0, 7):
            dlg = wx.SingleChoiceDialog(
                self.board_panel,
                "Choose promotion piece",
                "Promotion",
                ["Queen", "Rook", "Bishop", "Knight"]
            )
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return

            promote = dlg.GetStringSelection()[0]
            if piece.islower():
                promote = promote.lower()
            dlg.Destroy()

        self.ChessBoard.MakeMove(
            self.whites_move,
            from_pos,
            to_pos,
            False,
            False,
            False,
            promote
        )

        self.whites_move = not self.whites_move
        self.fen = self.ChessBoard.board

        self.selected_square = None
        self.legal_moves.clear()
        self.highlight_points.clear()

        self.board_panel.Refresh()


# =========================
# App bootstrap
# =========================

# class ChessFrame(wx.Frame):
#     def __init__(self):
#         super().__init__(None, title="Chess", size=(520, 560))
#         panel = wx.Panel(self)
#         panel.SetSize((480, 480))
#         PieceManager(generate_chess_centers(), panel)
#         self.Show()


# if __name__ == "__main__":
#     app = wx.App(False)
#     ChessFrame()
#     app.MainLoop()
