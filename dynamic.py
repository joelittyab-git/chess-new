from wx import(
     Panel,BufferedPaintDC,Bitmap,
     Brush, Event, Colour
)

import MoveGen

from wx import(
     IMAGE_QUALITY_HIGH,
     EVT_PAINT,
     EVT_LEFT_DOWN
)



from wx.svg import SVGimage

from unit import Unit

import wx


BLUEBLACK = True
SQAUREPIX = 60

class PieceManager:
     
     START_BOARD = [
          ["r","n","b","q","k","b","n","r"],
          ["p","p","p","p","p","p","p","p"],
          [".",".",".",".",".",".",".","."],
          [".",".",".",".",".",".",".","."],
          [".",".",".",".",".",".",".","."],
          [".",".",".",".",".",".",".","."],
          ["P","P","P","P","P","P","P","P"],
          ["R","N","B","Q","K","B","N","R"],
     ]
     
     def __init__(self, centers, panel:Panel,captured_panel_white:Panel,captured_panel_black:Panel, callback=None, generate_moves=None, colour=False):
          """_summary_

          Args:
              centers (_type_): coordinates of each of the chess boxes on the chess board
              callback (_any_): the callback to refer to after a move is made
              generate_moves (_any_): Generate the set of moves for a particular pice on the board
              panel (_wx.Panel_): the panel where the board is present
          """
          
          self.colour = colour
          
          # test
          
          self.fen = [
               [".",".",".",".",".",".",".","."],
               [".",".",".",".",".",".",".","."],
               [".",".",".",".",".",".",".","."],
               [".",".",".",".",".",".",".","."],
               [".",".",".",".",".",".",".","."],
               [".",".",".",".",".",".",".","."],
               ["P",".",".",".",".",".",".","."],
               [".",".",".",".",".",".",".","."]
          ]
          
          # ---
          
          self.whites_move = True
          
          self.centers = centers
          self.call = callback
          self.get_moves = generate_moves
          self.board_panel = panel
          self.blueblack = BLUEBLACK
          
          self.SQAUREPIX = SQAUREPIX
          
          
          # A dictionary of all positions (x,y) paired up with the piece image
          self.piece_config = dict()
          self.fen = PieceManager.START_BOARD
          
          # All the points to be marked
          self.highlight_points = list()
          
          # All the points that are legal to move to: index from the fen notation
          self.legal_moves = list()
          
          # The index of the box selected using the fen
          self.selected_square = None
          
          # # Captured pins
          # self.captured_black = list()
          # self.captured_white = list()
          
          if centers is None:
               self.centers = generate_chess_centers()
          
          # Preload svg to reduce time while setting the peice on the board
          self.preload_svg()
          
          
          panel.Bind(EVT_PAINT, self.init_paint)
          panel.Bind(EVT_LEFT_DOWN, self.on_click)
          
          # TODO: Colour chnage 

          """          button = wx.Button(self.board_panel,label="Black and white <-> Blue and white", pos=(250, 500))
                    button.Bind(wx.EVT_BUTTON,self.toggle_color)
          """          
          
          self.ChessBoard = MoveGen.IB_ChessPy()
          # default chess starting position is rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 in FEN notation
          self.ChessBoard.setCustomBoard("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
          # self.ChessBoard.setCustomBoard("8/P7/8/8/8/8/8/8 w - - 0 1")
          self.fen = self.ChessBoard.board

          self.moveDict, self.inCheck = self.ChessBoard.getLegalMoves(whiteToMove=self.whites_move)
          
          self.input_locked = False
          
          self.captured_panel_white = captured_panel_white
          self.captured_panel_black = captured_panel_black
          
          self.captured_white = ['r','k','q']
          self.captured_black = ['B','N', 'N']
          
          self.captured_panel_black.Bind(wx.EVT_PAINT, self.paint_captured_black)
          self.captured_panel_white.Bind(wx.EVT_PAINT, self.paint_captured_white)


     
          
     def PAINT(self, dc:BufferedPaintDC):
          """Paints the board based on the selected colour

          Args:
              dc (BufferedPaintDC): _description_
          """
          BOARDSIZE=8
          BOARDPIX=BOARDSIZE * self.SQAUREPIX
          blublack=False 
          for row in range(BOARDSIZE):
               for col in range(BOARDSIZE):
                    x = col * self.SQAUREPIX
                    y = row * self.SQAUREPIX
                    if (row + col) % 2 == 0:
                         dc.SetBrush(wx.Brush("white"))
                    else:
                         color = "#2278a3" if self.colour else "black"
                         dc.SetBrush(wx.Brush(color))
                    color = "#2278a3" if self.colour else "black"
                    dc.SetPen(wx.Pen(color))
                    dc.DrawRectangle(x, y, self.SQAUREPIX, self.SQAUREPIX)
                    
     def paint_captured_white(self, event):
          dc = wx.BufferedPaintDC(self.captured_panel_white)
          dc.Clear()

          size = 32
          padding = 4

          for i, piece in enumerate(self.captured_white):
               bmp = self.loaded_svg[piece]
               x = (i % 4) * (size + padding)
               y = (i // 4) * (size + padding)
               dc.DrawBitmap(bmp, x, y, True)
               
     def paint_captured_black(self, event):
          dc = wx.BufferedPaintDC(self.captured_panel_black)
          dc.Clear()

          size = 32
          padding = 4

          for i, piece in enumerate(self.captured_black):
               bmp = self.loaded_svg[piece]
               x = (i % 4) * (size + padding)
               y = (i // 4) * (size + padding)
               dc.DrawBitmap(bmp, x, y, True)
                    
     def toggle_color(self, event):
          self.blueblack = not self.blueblack
          self.board_panel.Refresh()
          
     def preload_svg(self):
          """Loads the formatted and converetd bitmaps into an instance dictionary 'loaded_svg'"""
          formatted = dict()
          
          svgs :dict = Unit.load_all()
          
          for i in svgs.keys():
               formatted[i] = rasterize_svg(svgs[i], (70,70))
               
          self.loaded_svg = formatted
               
                    
     def configure_pieces(self, dc:BufferedPaintDC):
          # print("Board: ",self.centers)
          c = self.centers
          for i in range(len(self.fen)):
               for j in range(len(self.fen[i])):
                    if self.fen[i][j]!='.':
                         x,y  = c[i][j]
                         bmp = self.loaded_svg[self.fen[i][j]]
                         # TODO: Store all the bmp in a dictionary of their positions
                         self.piece_config[(x,y)]=bmp
                         dc.DrawBitmap(bmp,round(x),round(y) )
                    else:
                         x,y  = c[i][j]
                         # has no piece at point
                         self.piece_config[(x,y)] = None
          
     def init_paint(self,event:Event):          
          """Handles all the paint events on the board
          > Is called after any change on the board to repaint the panel 

          Args:
              event (Event): _description_
              highlight_point (_type_, optional): _description_. Defaults to None.
          """
          t = [f"{i}\n" for i in self.fen]
          print(*t)
          dc = BufferedPaintDC(self.board_panel)
          brush = Brush('white')
          
          dc.SetBackground(brush)
          dc.Clear()
          
          # Board paint
          self.PAINT(dc)
          
          # Set piece on the board
          self.configure_pieces(dc)
          
          # Hights any points on the board if any exists in the valid moves
          for point in self.highlight_points:
               self.highlight(point, dc)
          self.highlight_points.clear()
          
     def highlight(self, point, dc:BufferedPaintDC):
          dc.SetBrush(wx.Brush(Colour(237, 17, 28)))
          dc.SetPen(wx.Pen("red"))
          dc.DrawCircle(round(point[0])+15, round(point[1])+15, 12)
          

     def on_click(self, event:Event):
          
          if self.input_locked:
               return
          """Handles any click event on the board

          Args:
              event (Event): _description_
          """
          t = event.GetEventObject()
          p = event.GetPosition()
          print(f"Clicked at {t} {p}")
          
          """
          a = (p[0]+32)//64
          b = (p[1]+32)//64
          """
          a = (p[0])//self.SQAUREPIX
          b = (p[1])//self.SQAUREPIX
          
          print(self.fen[b][a])
          
          
          # Handles any click on the marked points (legal moves)
          if (b,a) in self.legal_moves:
               self.move(self.selected_square, (b,a))
               self.selected_square = None
               self.legal_moves.clear()
               self.highlight_points.clear()
               self.board_panel.Refresh()
               return
          
          # Handles all the click on the existing pieces on the board
          if self.fen[b][a]!='.':
               
               if self.whites_move and self.fen[b][a].isupper():
                    self.selected_square = (b,a)
                    self.show_all_possible_moves((a,b))
                    
               if not self.whites_move and self.fen[b][a].islower():
                    self.selected_square = (b,a)
                    self.show_all_possible_moves((a,b))
               
          print(f"BOX: {a} {b}")
          
          
          
     def move(self, selected_square, clicked_sqaure):
          """Moves the piece from selected square to the clicked sqaure in the fen list

          Args:
              selected_square (_tuple_): The selected square in the form (row_index, column_index)
              clicked_sqaure (_tuple_): The square to which the player desires to move. (row_index, column_index)
          """
          print(*self.fen)

          # if self.fen[clicked_sqaure[0]][clicked_sqaure[1]]=='.':
          #      # Swaps he notations on the board
          #      self.fen[clicked_sqaure[0]][clicked_sqaure[1]] = self.fen[selected_square[0]][selected_square[1]]
          #      self.fen[selected_square[0]][selected_square[1]] = '.'
          
          piece = self.fen[selected_square[0]][selected_square[1]]
          # print(piece)
          
          from_pos = PieceManager.Converter(selected_square[0],selected_square[1])
          to_pos = PieceManager.Converter(clicked_sqaure[0], clicked_sqaure[1])
          
          is_queenside_castle = False
          is_kingside_castle = False
          is_en_passant = None
          promote = None
          
          is_queenside_castle, is_kingside_castle  = PieceManager.detect_castling(from_pos, to_pos, piece)
          is_en_passant = PieceManager.detect_en_passant(from_pos, to_pos, piece, self.fen)
          # if PieceManager.detect_promotion(to_pos, piece):
          #      dlg = PromotionDialog(
          #           self.board_panel,
          #           is_white=piece.isupper(),
          #           piece_bitmaps=self.loaded_svg
          #      )

          #      if dlg.ShowModal() == wx.ID_OK:
          #           promote_to = dlg.selection
          #      else:
          #           return  # promotion cancelled

          #      dlg.Destroy()
          
          
          # self.ChessBoard.MakeMove(self.whites_move, from_index, )
          
          if PieceManager.detect_promotion(to_pos, piece):
               self.input_locked = True

               choices = ["Queen", "Rook", "Bishop", "Knight"]
               print(selected_square)
               print(*self.fen)
               print(self.fen[selected_square[0]][selected_square[1]])
                
               piece_map = str.lower if self.fen[selected_square[0]][selected_square[1]].islower() else str.upper
               print(piece_map("A"))
               dlg = wx.SingleChoiceDialog(
                    self.board_panel,
                    "Choose promotion piece",
                    "Promotion",
                    choices
               )

               if dlg.ShowModal() == wx.ID_OK:
                    choice = dlg.GetStringSelection()
                    promote_map = {
                         "Queen": "Q",
                         "Rook": "R",
                         "Bishop": "B",
                         "Knight": "N"
                    }
                    promote =  piece_map(promote_map[choice])
                    print("Promotion: ",promote)
               else:
                    dlg.Destroy()
                    self.input_locked = False
                    return

               dlg.Destroy()
               self.input_locked = False
          
     def detect_castling(from_sq, to_sq, piece):
          is_qs = False
          is_ks = False

          if piece.lower() == 'k':
               fx, fy = from_sq
               tx, ty = to_sq

               # King moves two squares horizontally
               if fy == ty and abs(tx - fx) == 2:
                    if tx < fx:
                         is_qs = True
                    else:
                         is_ks = True

          return is_qs, is_ks

     def detect_en_passant(from_sq, to_sq, piece, board):
          if piece.lower() != 'p':
               return None

          fx, fy = from_sq
          tx, ty = to_sq

          # Pawn moves diagonally but destination is empty
          if abs(tx - fx) == 1 and abs(ty - fy) == 1:
               board_row = 7 - ty
               board_col = tx
               if board[board_row][board_col] == '.':
                    return (tx, ty)

          return None

     def detect_promotion(to_sq, piece):
          x, y = to_sq
          if piece.lower() == 'p' and (y == 7 or y == 0):
               return True
          return False

     def detect_promotion(to_sq, piece):
          x, y = to_sq
          if piece.lower() == 'p' and (y == 7 or y == 0):
               return True
          return False
          
     def Converter(x, y):
          return 7-y, x
          
          
     def show_all_possible_moves(self, position):
          """the method that marks all the possible boxes at which the piece can move based on 
          the position of the piece

          Args:
              position (_tuple_): the index of the piece in the fen notations (x,y)
          """
          print("position: ", position)
          moves = [
               (position[0], position[1]-1)
          ]

          move = self.centers[position[1]-1][position[0]]
          move2 = self.centers[position[1]-1][position[0]+1]
          self.highlight_points.extend([move,move2])
          print(self.highlight_points)
          # TODO: get all valid moves and mark them
          
          
          
          
          l_m = [(position[1]-1, position[0]), (position[1]-1, position[0]+1)]
          print(l_m)
          self.legal_moves.extend(l_m)
          print(self.legal_moves)
          self.board_panel.Refresh()

def rasterize_svg(svg: SVGimage, target_size):
    """
    WxPython cannot rescale the bitmap image therefore we convert the svg image frist to wx.Image instance
    and then Scale it to the desired size and then make it a bitmap.
    Normal images cannot be drawn on the panel, therefore it must be converted to a drawable bitmap type.
    """

    tw, th = target_size

    # Render at a large size (fixes viewBox issues)
    BIG_W = 800
    BIG_H = 800

    big_bmp = svg.ConvertToBitmap(width=BIG_W, height=BIG_H)

    # Scale down with high quality
    img = big_bmp.ConvertToImage()
    img = img.Scale(tw, th, IMAGE_QUALITY_HIGH)

    return Bitmap(img) 
          
          
def generate_chess_centers(square_size=64):
    board = []

    for row in range(8):
        row_centers = []
        for col in range(8):
            center_x = col * square_size + square_size // 2
            center_y = row * square_size + square_size // 2
            row_centers.append((center_x, center_y))
        board.append(row_centers)

    return board
