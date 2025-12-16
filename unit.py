from wx.svg import SVGimage

class Unit:
     BLACK_PAWN = 'p'
     BLACK_ROOK = 'r'
     BLACK_KNIGHT = 'n'
     BLACK_BISHOP = 'b'
     BLACK_KING = 'k'
     BLACK_QUEEN = 'q'

     WHITE_PAWN = 'P'
     WHITE_ROOK = 'R'
     WHITE_KNIGHT = 'N'
     WHITE_BISHOP = 'B'
     WHITE_KING = 'K'
     WHITE_QUEEN = 'Q'
     
     ROOT_DIR = './piece'
     
     
     def get_svg(unit:str, group = 'icpieces')->SVGimage:
          """Returns the svg of the chess piece.
          Pass the unit name from the given UNIT constants
          
          BLACK_PAWN
          BLACK_ROOK
          BLACK_KNIGHT
          BLACK_BISHOP
          BLACK_KING
          BLACK_QUEEN

          WHITE_PAWN
          WHITE_ROOK
          WHITE_KNIGHT
          WHITE_BISHOP
          WHITE_KING
          WHITE_QUEEN
          """
          assert type(unit)==str
          assert len(unit)==1
          
          file = f'b{unit[0].upper()}.svg' if unit.islower() else f'w{unit[0].upper()}.svg'
          path = f"{Unit.ROOT_DIR}/{group}/{file}"
          try:
               svg =  SVGimage.CreateFromFile(path)
               return svg
          except:
               raise FileNotFoundError("The given path or piece might be invalid")
          
          
     def get_all():
          """Retunrs all the pieces in the FEN notations
          """
          return [
               Unit.BLACK_PAWN,
               Unit.BLACK_ROOK,
               Unit.BLACK_KNIGHT,
               Unit.BLACK_BISHOP,
               Unit.BLACK_KING,
               Unit.BLACK_QUEEN,

               Unit.WHITE_PAWN,
               Unit.WHITE_ROOK,
               Unit.WHITE_KNIGHT,
               Unit.WHITE_BISHOP,
               Unit.WHITE_KING,
               Unit.WHITE_QUEEN
          ]
          
     def load_all()->dict:
          """Loads all the SVGimages into a disctionary with the FEN notation as the key"""
          return {key:Unit.get_svg(key) for key in Unit.get_all()}
               