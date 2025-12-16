class IB_ChessPy:
    def __init__(self):
        self.fiftyMoveRuleCounter = 0
        
        self.HasCastledBlackKingSide = False
        self.HasCastledBlackQueenSide = False
        self.HasCastledWhiteKingSide = False
        self.HasCastledWhiteQueenSide = False
        
        self.currentEnPassantableSquare = None
        
        self.board = [list("rnbqkbnr"),
                list("p"*8),
                list("."*8),
                list("."*8),
                list("."*8),
                list("."*8),
                list("P"*8),
                list("RNBQKBNR")]
        
        # NOTE: the first index refers to the rank and not the file
        # counterintuitive to and in violation of common convention
        # this CAN cause confusion, but uhh, skill issue
        # but dw the getPiece method handles the conversion properly

        self.wkXPos = 4  #wk = white king, bk = black king
        self.wkYPos = 0
        self.bkXPos = 4
        self.bkYPos = 7


    def getPiece(self, xPos: int, yPos: int):
        if xPos > 7 or xPos < 0 or yPos > 7 or yPos < 0:
            return None
        else:
            #no this is NOT a mistake, the yPos is first index and xPos is second index
            # becuz i like the x is left-right and y is up-down notation
            return self.board[7-yPos][xPos]
    
    #needed so that king doesnt go to those squares
    def getAttacks(self):
        danger = set()
        
        #direction which pieces move
        moveDirection = {'R': [(-1, 0), (1, 0), (0, -1), (0, 1)],
            'B': [(-1, -1), (-1, 1), (1, -1), (1, 1)],
            'Q': [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]}

        # knight moves
        knightMoves = [(1, 2), (1, -2), (-1, 2), (-1, -2),(2, 1), (2, -1), (-2, 1), (-2, -1)]

        for y in range(8):
            for x in range(8):
                piece = self.getPiece(x, y)

                if piece is None or piece == '.' or piece in "PRNBQK":
                    continue

                # just go diagonally left and right and add the attack squares to the danger set
                if piece == 'p':
                    attack_moves = [(x - 1, y - 1), (x + 1, y - 1)]
                    for newPosX, newPosY in attack_moves:
                        targetPiece = self.getPiece(newPosX, newPosY)
                        
                        if targetPiece is not None:
                            danger.add((newPosX, newPosY))
                            
                elif piece == 'n':
                    for xChange, yChange in knightMoves:
                        newPosX, newPosY = x + xChange, y + yChange
                        targetPiece = self.getPiece(newPosX, newPosY)

                        if targetPiece is not None:
                            danger.add((newPosX, newPosY))

                elif piece == 'k':
                    for yChange in [-1, 0, 1]:
                        for xChange in [-1, 0, 1]:
                            if xChange == 0 and yChange == 0:
                                continue
                            
                            newPosX, newPosY = x + xChange, y + yChange
                            targetPiece = self.getPiece(newPosX, newPosY)
                            
                            if targetPiece is not None:
                                danger.add((newPosX, newPosY))

                elif piece in "rbq":
                    piece_type = piece.upper()
                    
                    for xChange, yChange in moveDirection[piece_type]:
                        newPosX, newPosY = x + xChange, y + yChange
                        
                        #code to move queen/rook/bishop in direction it is going 1 move after another
                        while True:
                            targetPiece = self.getPiece(newPosX, newPosY)
                            
                            #if we encounter square outside board
                            if targetPiece is None:
                                break
                            
                            #add regardless of piece colour
                            danger.add((newPosX, newPosY))

                            if targetPiece != '.' and targetPiece != "K":
                                break
                            
                            newPosX += xChange
                            newPosY += yChange
                            
        return danger
    
    
    def getLegalMoves(self, whiteToMove: bool):
        
        # variables to use starter pack:
        CanCastleKingSide = False
        CanCastleQueenSide = False


        #NOTE: chess is completely symmetric in its rules for black and white and
        #the ONLY difference is that white goes first, but for move generation that doesnt matter at all

        #the swapping logic:
        if not whiteToMove:

            self.HasCastledBlackKingSide, self.HasCastledWhiteKingSide = self.HasCastledWhiteKingSide, self.HasCastledBlackKingSide
            self.HasCastledBlackQueenSide, self.HasCastledWhiteQueenSide = self.HasCastledWhiteQueenSide, self.HasCastledBlackQueenSide
            
            if self.currentEnPassantableSquare:
                self.currentEnPassantableSquare = (self.currentEnPassantableSquare[0],7 - self.currentEnPassantableSquare[1])

            self.board = [
                [p.upper() if p.islower() else p.lower() if p.isupper() else p for p in rank]
                for rank in self.board[::-1]   # reverse the ranks
            ]

        
        for yPos in range(8):
            for xPos in range(8):
                if self.getPiece(xPos, yPos) == "k":
                    self.bkXPos = xPos
                    self.bkYPos = yPos
                elif self.getPiece(xPos, yPos) == "K":
                    self.wkXPos = xPos
                    self.wkYPos = yPos


        wkXPos = self.wkXPos
        wkYPos = self.wkYPos
            
        
        inCheck = False
        doubleCheck = False

        # if in check by a single piece, then if player chooses to capture attacking
        # piece or block attacking piece then it must go to one of these squares
        # if in double check then ignore cuz the player has no other choice than to
        # king to move out of the way or else king die 😔
        
        needToGoSquares = set()

        #the dict of squares where the piece is pinned along with information on which direction
        #its pinned because pinned pieces can still move along the direction they are pinned

        pinnedSquares = dict()

        # eg: (5,5): "urdl"


        # danger squares are the squares that are dangerous for king to go or cant castle through or both

        dangerSquares = self.getAttacks()

        #moveDict is just dictionary of possible moves
        moveDict = dict()

        # (5,5): set((6,6),(4,4))

        #pre move generation restriction check, for example checking for pins
        #castling rights, squares king cant move (also generates squares king CAN move cuz why
        # do it later wen u can do it now)

        if self.getPiece(wkXPos+1, wkYPos+1) == "p":
            inCheck = True
        elif self.getPiece(wkXPos-1, wkYPos+1) == "p":
            inCheck = True
        
        #Knight Check code
        if self.getPiece(wkXPos+1, wkYPos+2) == "n":
            inCheck = True
            needToGoSquares.add((wkXPos+1, wkYPos+2))
        elif self.getPiece(wkXPos+2, wkYPos+1) == "n":
            inCheck = True
            needToGoSquares.add((wkXPos+2, wkYPos+1))
        elif self.getPiece(wkXPos-1, wkYPos-2) == "n":
            inCheck = True
            needToGoSquares.add((wkXPos-1, wkYPos-2))
        elif self.getPiece(wkXPos-2, wkYPos-1) == "n":
            inCheck = True
            needToGoSquares.add((wkXPos-2, wkYPos-1))
        elif self.getPiece(wkXPos+1, wkYPos-2) == "n":
            inCheck = True
            needToGoSquares.add((wkXPos+1, wkYPos-2))
        elif self.getPiece(wkXPos-2, wkYPos+1) == "n":
            inCheck = True
            needToGoSquares.add((wkXPos-2, wkYPos+1))
        elif self.getPiece(wkXPos-1, wkYPos+2) == "n":
            inCheck = True
            needToGoSquares.add((wkXPos-1, wkYPos+2))
        elif self.getPiece(wkXPos+2, wkYPos-1) == "n":
            inCheck = True
            needToGoSquares.add((wkXPos+2, wkYPos-1))

        
        #for up direction
        potentiallyPinnedPiece = False

        #stands for potential pinned piece position
        pppp = (0,0)

        visited = set()

        for i in range(wkYPos+1,8):
            cur = self.getPiece(wkXPos,i)
            if cur == ".":
                visited.add((wkXPos,i))
            elif cur in "qr":
                if not potentiallyPinnedPiece:
                    if inCheck:
                        doubleCheck = True
                    else:
                        inCheck = True
                        #add the squares where another piece can go to block
                        needToGoSquares.update(visited)
                        #add square where other pieces can capture to stop the check
                        needToGoSquares.add((wkXPos,i))
                    
                else:
                    pinnedSquares[pppp] = "ud"   #pinned to only move up and down
                break
            elif cur in "bnpk":
                break
            elif cur in "QBPNR":
                if potentiallyPinnedPiece:
                    break
                else:
                    potentiallyPinnedPiece = True
                    pppp = (wkXPos,i)
        


        #for down direction
        potentiallyPinnedPiece = False
        pppp = (0,0)
        visited = set()

        for i in range(wkYPos-1,-1, -1):
            cur = self.getPiece(wkXPos,i)
            if cur == ".":
                visited.add((wkXPos,i))
            elif cur in "qr":
                if not potentiallyPinnedPiece:
                    if inCheck:
                        doubleCheck = True
                    else:
                        inCheck = True
                        #add the squares where another piece can go to block
                        needToGoSquares.update(visited)
                        #add square where other pieces can capture to stop the check
                        needToGoSquares.add((wkXPos,i))
                    
                else:
                    pinnedSquares[pppp] = "ud"   #pinned to only move up and down
                break
            elif cur in "bnpk":
                break
            elif cur in "QBPNR":
                if potentiallyPinnedPiece:
                    break
                else:
                    potentiallyPinnedPiece = True
                    pppp = (wkXPos,i)
        


        #the code for checking sideways is almost the exact same thing:  
        #right direction          
        potentiallyPinnedPiece = False
        pppp = (0,0)
        visited = set()

        #for right direction
        for i in range(wkXPos+1,8):
            cur = self.getPiece(i, wkYPos)
            if cur == ".":
                visited.add((i,wkYPos))
            elif cur in "qr":
                if not potentiallyPinnedPiece:
                    if inCheck:
                        doubleCheck = True
                    else:
                        inCheck = True
                        #add the squares where another piece can go to block
                        needToGoSquares.update(visited)
                        #add square where other pieces can capture to stop the check
                        needToGoSquares.add((i,wkYPos))
                    
                else:
                    pinnedSquares[pppp] = "lr"   #pinned to only move left and right
                break
            elif cur in "bnpk":
                break
            elif cur in "QBPNR":
                if potentiallyPinnedPiece:
                    break
                else:
                    potentiallyPinnedPiece = True
                    pppp = (i,wkYPos)



        potentiallyPinnedPiece = False
        pppp = (0,0)
        visited = set()

        #for left direction
        for i in range(wkXPos-1,-1,-1):
            cur = self.getPiece(i, wkYPos)
            if cur == ".":
                visited.add((i,wkYPos))
            elif cur in "qr":
                if not potentiallyPinnedPiece:
                    if inCheck:
                        doubleCheck = True
                    else:
                        inCheck = True
                        #add the squares where another piece can go to block
                        needToGoSquares.update(visited)
                        #add square where other pieces can capture to stop the check
                        needToGoSquares.add((i,wkYPos))
                else:
                    pinnedSquares[pppp] = "lr"   #pinned to only move left and right
                break
            elif cur in "bnpk":
                break
            elif cur in "QBPNR":
                if potentiallyPinnedPiece:
                    break
                else:
                    potentiallyPinnedPiece = True
                    pppp = (i,wkYPos)
        


        #up right direction
        potentiallyPinnedPiece = False
        pppp = (0,0)
        visited = set()

        diagIter = [wkXPos+1,wkYPos+1]
        while diagIter[0] < 8 and diagIter[1] < 8:
            cur = self.getPiece(diagIter[0], diagIter[1])
            if cur == ".":
                visited.add(tuple(diagIter))
            elif cur in "qb":
                if not potentiallyPinnedPiece:
                    if inCheck:
                        doubleCheck = True
                    else:
                        inCheck = True
                        #add the squares where another piece can go to block
                        needToGoSquares.update(visited)
                        #add square where other pieces can capture to stop the check
                        needToGoSquares.add(tuple(diagIter))
                    
                else:
                    pinnedSquares[pppp] = "urdl"   #pinned to only diagonally in up right down left direction
                break
            elif cur in "rnpk":
                break
            elif cur in "QBPNR":
                if potentiallyPinnedPiece:
                    break
                else:
                    potentiallyPinnedPiece = True
                    pppp = tuple(diagIter)
            
            diagIter[0] += 1
            diagIter[1] += 1
        


        #down right direction
        potentiallyPinnedPiece = False
        pppp = (0,0)
        visited = set()

        diagIter = [wkXPos+1,wkYPos-1]
        while diagIter[0] < 8 and diagIter[1] > -1:
            cur = self.getPiece(diagIter[0], diagIter[1])
            if cur == ".":
                visited.add(tuple(diagIter))
            elif cur in "qb":
                if not potentiallyPinnedPiece:
                    if inCheck:
                        doubleCheck = True
                    else:
                        inCheck = True
                        #add the squares where another piece can go to block
                        needToGoSquares.update(visited)
                        #add square where other pieces can capture to stop the check
                        needToGoSquares.add(tuple(diagIter))
                    
                else:
                    pinnedSquares[pppp] = "uldr"   #pinned to only diagonally in up left down right direction
                break
            elif cur in "rnpk":
                break
            elif cur in "QBPNR":
                if potentiallyPinnedPiece:
                    break
                else:
                    potentiallyPinnedPiece = True
                    pppp = tuple(diagIter)
            
            diagIter[0] += 1
            diagIter[1] -= 1
        



        #down left direction
        potentiallyPinnedPiece = False
        visited = set()

        diagIter = [wkXPos-1,wkYPos-1]
        while diagIter[0] > -1 and diagIter[1] > -1:
            cur = self.getPiece(diagIter[0], diagIter[1])
            if cur == ".":
                visited.add(tuple(diagIter))
            elif cur in "qb":
                if not potentiallyPinnedPiece:
                    if inCheck:
                        doubleCheck = True
                    else:
                        inCheck = True
                        #add the squares where another piece can go to block
                        needToGoSquares.update(visited)
                        #add square where other pieces can capture to stop the check
                        needToGoSquares.add(tuple(diagIter))
                    
                else:
                    pinnedSquares[pppp] = "urdl"   #pinned to only diagonally in up right down left direction
                break
            elif cur in "rnpk":
                break
            elif cur in "QBPNR":
                if potentiallyPinnedPiece:
                    break
                else:
                    potentiallyPinnedPiece = True
                    pppp = tuple(diagIter)
            
            diagIter[0] -= 1
            diagIter[1] -= 1
        



        #up left direction
        potentiallyPinnedPiece = False
        visited = set()

        diagIter = [wkXPos-1,wkYPos+1]
        while diagIter[0] > -1 and diagIter[1] < 8:
            cur = self.getPiece(diagIter[0], diagIter[1])
            if cur == ".":
                visited.add(tuple(diagIter))
            elif cur in "qb":
                if not potentiallyPinnedPiece:
                    if inCheck:
                        doubleCheck = True
                    else:
                        inCheck = True
                        #add the squares where another piece can go to block
                        needToGoSquares.update(visited)
                        #add square where other pieces can capture to stop the check
                        needToGoSquares.add(tuple(diagIter))
                    
                else:
                    pinnedSquares[pppp] = "uldr"   #pinned to only diagonally in up left down right direction
                break
            elif cur in "rnpk":
                break
            elif cur in "QBPNR":
                if potentiallyPinnedPiece:
                    break
                else:
                    potentiallyPinnedPiece = True
                    pppp = tuple(diagIter)
            
            diagIter[0] -= 1
            diagIter[1] += 1

        
        # the actual move generator
        

        if not doubleCheck:
            for y in range(8):
                for x in range(8):
                    piece = self.getPiece(x, y)
                    if piece is None or piece.islower() or piece == '.' or piece == 'K':
                        continue

                    curPos = (x, y)
                    pseudoLegalMoves = set() #pseudo legal moves that i will intersect with pinnedMoves and needToGoSquares
                    pinnedMoves = set()    #for generating the set of all pos the pinned piece can move

                    if piece == 'P':

                        targetPos = (x, y + 1)
                        if self.getPiece(targetPos[0], targetPos[1]) == '.':
                            pseudoLegalMoves.add(targetPos)
                            
                            # for double push
                            if y == 1:
                                target_pos_2 = (x, y + 2)
                                if self.getPiece(target_pos_2[0], target_pos_2[1]) == '.':
                                    pseudoLegalMoves.add(target_pos_2)

                        for xChange in [-1, 1]:
                            targetPos = (x + xChange, y + 1)
                            targetPiece = self.getPiece(targetPos[0], targetPos[1])
                            
                            # diagonal pawn capture
                            if targetPiece is not None and targetPiece.islower():
                                pseudoLegalMoves.add(targetPos)
                                
                            #en passant logic
                            if self.currentEnPassantableSquare is not None and targetPos == self.currentEnPassantableSquare:
                                pseudoLegalMoves.add(targetPos)

                    elif piece == 'N':
                        knightPossibleMoves = [
                            (1, 2), (1, -2), (-1, 2), (-1, -2),
                            (2, 1), (2, -1), (-2, 1), (-2, -1)
                        ]
                        for xChange, yChange in knightPossibleMoves:
                            newPosX, newPosY = x + xChange, y + yChange
                            targetPiece = self.getPiece(newPosX, newPosY)
                            
                            if targetPiece is not None and not targetPiece.isupper():
                                pseudoLegalMoves.add((newPosX, newPosY))

                    elif piece in ('R', 'B', 'Q'):
                        movementDirections = []
                        if piece in ('R', 'Q'):
                            movementDirections.extend([(-1, 0), (1, 0), (0, -1), (0, 1)])
                        if piece in ('B', 'Q'):
                            movementDirections.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])

                        #very similar logic stuff in getAttacks func
                        for xChange, yChange in movementDirections:
                            newPosX, newPosY = x + xChange, y + yChange
                            
                            while True:
                                targetPiece = self.getPiece(newPosX, newPosY)
                                
                                if targetPiece is None:
                                    break
                                
                                if not targetPiece.isupper():
                                    pseudoLegalMoves.add((newPosX, newPosY))

                                if targetPiece != '.':
                                    break
                                
                                newPosX += xChange
                                newPosY += yChange

                    if curPos in pinnedSquares:
                        pin_direction = pinnedSquares[curPos]
                        
                        pinDirections = {'ud': [(0, 1), (0, -1)],
                            'lr': [(1, 0), (-1, 0)],
                            'uldr': [(-1, 1), (1, -1)],
                            'urdl': [(1, 1), (-1, -1)]}
                        
                        for xChange, yChange in pinDirections[pin_direction]:
                            for distance in range(1, 8): 
                                #its fine even if the position goes out of board, the intersect will handle that stuff
                                newPosX = x + xChange * distance
                                newPosY = y + yChange * distance
                                
                                pinnedMoves.add((newPosX, newPosY))

                        #intersect generated moves with possible moves along the pinned dir the piece can move
                        #to get the legal moves
                        pseudoLegalMoves = pseudoLegalMoves.intersection(pinnedMoves)
                    


                    if needToGoSquares:
                        #similar logic to the pin but for blocking / capturing piece that is giving check
                        pseudoLegalMoves = pseudoLegalMoves.intersection(needToGoSquares)

                    if pseudoLegalMoves:

                        #even though it says pseudo legal moves after the set intersections
                        #it becomes true legal moves
                        moveDict[curPos] = pseudoLegalMoves
        

        #king moving logic

        kingMovesSet = set()

        potentialKingMove = (wkXPos+1, wkYPos+1)
        kingadjacentPiece = self.getPiece(potentialKingMove[0], potentialKingMove[1])
        kingadjacentPiece = "invalid" if kingadjacentPiece is None else kingadjacentPiece
        if kingadjacentPiece in "pnbrq." and potentialKingMove not in dangerSquares:
            kingMovesSet.add(potentialKingMove)
        
        potentialKingMove = (wkXPos+1, wkYPos-1)
        kingadjacentPiece = self.getPiece(potentialKingMove[0], potentialKingMove[1])
        kingadjacentPiece = "invalid" if kingadjacentPiece is None else kingadjacentPiece
        if kingadjacentPiece in "pnbrq." and potentialKingMove not in dangerSquares:
            kingMovesSet.add(potentialKingMove)
        
        potentialKingMove = (wkXPos-1, wkYPos+1)
        kingadjacentPiece = self.getPiece(potentialKingMove[0], potentialKingMove[1])
        kingadjacentPiece = "invalid" if kingadjacentPiece is None else kingadjacentPiece
        if kingadjacentPiece in "pnbrq." and potentialKingMove not in dangerSquares:
            kingMovesSet.add(potentialKingMove)
        
        potentialKingMove = (wkXPos-1, wkYPos-1)
        kingadjacentPiece = self.getPiece(potentialKingMove[0], potentialKingMove[1])
        kingadjacentPiece = "invalid" if kingadjacentPiece is None else kingadjacentPiece
        if kingadjacentPiece in "pnbrq." and potentialKingMove not in dangerSquares:
            kingMovesSet.add(potentialKingMove)

        potentialKingMove = (wkXPos+1, wkYPos)
        kingadjacentPiece = self.getPiece(potentialKingMove[0], potentialKingMove[1])
        kingadjacentPiece = "invalid" if kingadjacentPiece is None else kingadjacentPiece
        if kingadjacentPiece in "pnbrq." and potentialKingMove not in dangerSquares:
            kingMovesSet.add(potentialKingMove)
        
        potentialKingMove = (wkXPos-1, wkYPos)
        kingadjacentPiece = self.getPiece(potentialKingMove[0], potentialKingMove[1])
        kingadjacentPiece = "invalid" if kingadjacentPiece is None else kingadjacentPiece
        if kingadjacentPiece in "pnbrq." and potentialKingMove not in dangerSquares:
            kingMovesSet.add(potentialKingMove)
        
        potentialKingMove = (wkXPos, wkYPos+1)
        kingadjacentPiece = self.getPiece(potentialKingMove[0], potentialKingMove[1])
        kingadjacentPiece = "invalid" if kingadjacentPiece is None else kingadjacentPiece
        if kingadjacentPiece in "pnbrq." and potentialKingMove not in dangerSquares:
            kingMovesSet.add(potentialKingMove)
        
        potentialKingMove = (wkXPos, wkYPos-1)
        kingadjacentPiece = self.getPiece(potentialKingMove[0], potentialKingMove[1])
        kingadjacentPiece = "invalid" if kingadjacentPiece is None else kingadjacentPiece
        if kingadjacentPiece in "pnbrq." and potentialKingMove not in dangerSquares:
            kingMovesSet.add(potentialKingMove)
        


        #CASTLING LOGIC:

        #if castled kingside just skip the castling code
        if not self.HasCastledWhiteKingSide:
            if not inCheck and (5,0) not in dangerSquares and (6,0) not in dangerSquares:
                if self.getPiece(5,0) == "." and self.getPiece(6,0) == ".":
                    if self.getPiece(4,0) == "K" and self.getPiece(7,0) == "R":
                        CanCastleKingSide = True
        
        #queenside stuff
        if not self.HasCastledWhiteKingSide:
            if not inCheck and (2,0) not in dangerSquares and (3,0) not in dangerSquares:
                if self.getPiece(2,0) == "." and self.getPiece(3,0) == "." and self.getPiece(1,0):
                    if self.getPiece(4,0) == "K" and self.getPiece(0,0) == "R":
                        CanCastleQueenSide = True
        
        if CanCastleKingSide:
            kingMovesSet.add((6,0))
        
        if CanCastleQueenSide:
            kingMovesSet.add((2,0))

        if kingMovesSet:
            moveDict[(wkXPos, wkYPos)] = kingMovesSet

        

        if not whiteToMove:

            self.HasCastledBlackKingSide, self.HasCastledWhiteKingSide = self.HasCastledWhiteKingSide, self.HasCastledBlackKingSide
            self.HasCastledBlackQueenSide, self.HasCastledWhiteQueenSide = self.HasCastledWhiteQueenSide, self.HasCastledBlackQueenSide
            
            self.board = [
                [p.upper() if p.islower() else p.lower() if p.isupper() else p for p in rank]
                for rank in self.board[::-1]   # reverse the ranks
            ]

            if self.currentEnPassantableSquare:
                self.currentEnPassantableSquare = (self.currentEnPassantableSquare[0],7 - self.currentEnPassantableSquare[1])

            #mirroring the moveDict back
            mirroredMoveDict = {}

            for (x, y), moves in moveDict.items():
                mirrored_key = (x, 7 - y)
                mirrored_values = {(mx, 7 - my) for (mx, my) in moves}
                mirroredMoveDict[mirrored_key] = mirrored_values

            moveDict = mirroredMoveDict
        
        for yPos in range(8):
            for xPos in range(8):
                if self.getPiece(xPos, yPos) == "k":
                    self.bkXPos = xPos
                    self.bkYPos = yPos
                elif self.getPiece(xPos, yPos) == "K":
                    self.wkXPos = xPos
                    self.wkYPos = yPos


        wkXPos = self.wkXPos
        wkYPos = self.wkYPos
        

        return moveDict, inCheck
        


        

        
    



    def MakeMove(self, isWhiteMove: bool, fromPos: tuple, toPos: tuple, isCastleKingSide: bool, isCastleQueenSide: bool, isEnPassant: bool, Promote = None):
        BoardFromPos = (7-fromPos[1], fromPos[0])
        BoardToPos = (7-toPos[1], toPos[0])

        #the piece at the from position
        piece = self.getPiece(fromPos[0], fromPos[1])

        #50 move rule logic
        if piece in "pP" or self.getPiece(toPos[0], toPos[1]) in "rnbqpRNBQP":
            self.fiftyMoveRuleCounter = 0
        else:
            self.fiftyMoveRuleCounter += 1

        #making the actual move
        self.board[BoardFromPos[0]][BoardFromPos[1]] = "."
        self.board[BoardToPos[0]][BoardToPos[1]] = piece

        #setting up potential en passant square

        if piece == "p" and toPos[1] == 4 and fromPos[1] == 6:
            self.currentEnPassantableSquare = (fromPos[0], fromPos[1]-1)
        elif piece == "P" and toPos[1] == 3 and fromPos[1] == 1:
            self.currentEnPassantableSquare = (fromPos[0], fromPos[1]+1)
        else:
            self.currentEnPassantableSquare = None


        #castling logic:

        if isWhiteMove and fromPos[0] == 0 and fromPos[1] == 0 and piece == "R":
            self.HasCastledWhiteQueenSide = True
        elif isWhiteMove and fromPos[0] == 7 and fromPos[1] == 0 and piece == "R":
            self.HasCastledWhiteKingSide = True

        if piece == "K" and not (isCastleQueenSide or isCastleKingSide):
            self.HasCastledWhiteKingSide = True
            self.HasCastledWhiteQueenSide = True

        if isWhiteMove and isCastleKingSide:
            self.board[7][7] = "."
            self.board[7][5] = "R"
            self.HasCastledWhiteKingSide = True
            self.HasCastledWhiteQueenSide = True
        
        if isWhiteMove and isCastleQueenSide:
            self.board[7][0] = "."
            self.board[7][3] = "R"
            self.HasCastledWhiteKingSide = True
            self.HasCastledWhiteQueenSide = True



        
        if not isWhiteMove and fromPos[0] == 0 and fromPos[1] == 7 and piece == "r":
            self.HasCastledBlackQueenSide = True
        
        if not isWhiteMove and fromPos[0] == 7 and fromPos[1] == 7 and piece == "r":
            self.HasCastledBlackKingSide = True

        if piece == "K" and not (isCastleQueenSide or isCastleKingSide):
            self.HasCastledBlackKingSide = True
            self.HasCastledBlackQueenSide = True

        if not isWhiteMove and isCastleKingSide:
            self.board[0][7] = "."
            self.board[0][5] = "r"
            self.HasCastledBlackKingSide = True
            self.HasCastledBlackQueenSide = True
        
        if not isWhiteMove and isCastleQueenSide:
            self.board[0][0] = "."
            self.board[0][3] = "r"
            self.HasCastledBlackKingSide = True
            self.HasCastledBlackQueenSide = True

        
        #en passant logic

        if isEnPassant:
            if isWhiteMove:
                self.board[BoardToPos[0]+1][BoardToPos[1]] = "."
            else:
                self.board[BoardToPos[0]-1][BoardToPos[1]] = "."
            
        #promotion logic
        if Promote is not None and Promote in "rnbqRNBQ":
            self.board[BoardToPos[0]][BoardToPos[1]] = Promote





    def setCustomBoard(self, fen, pHasCastledWhiteKingSide=False, pHasCastledWhiteQueenSide=False, 
                       pHasCastledBlackKingSide=False, pHasCastledBlackQueenSide=False, pcurrentEnPassantableSquare=None):
        
        self.HasCastledBlackKingSide = pHasCastledBlackKingSide
        self.HasCastledBlackQueenSide = pHasCastledBlackQueenSide
        self.HasCastledWhiteKingSide = pHasCastledWhiteKingSide
        self.HasCastledWhiteQueenSide = pHasCastledWhiteQueenSide
        self.currentEnPassantableSquare = pcurrentEnPassantableSquare

        board_fen = fen.split(' ')[0]

        ranks = board_fen.split('/')

        self.board = []
        
        for rank in ranks:
            rank_list = []
            for char in rank:
                if char.isdigit():
                    num_empty = int(char)
                    rank_list.extend(list('.'*num_empty))
                else:
                    # If the character is a letter, it represents a piece.
                    # FEN alreayChange uses lowercase for black and uppercase for white.
                    rank_list.append(char)
            
            # Ensure every rank has exactly 8 squares for sanity check
            if len(rank_list) != 8:
                raise ValueError(f"FEN parsing error: Rank '{rank}' did not produce 8 squares.")
                
            self.board.append(rank_list)

        for yPos in range(8):
            for xPos in range(8):
                if self.getPiece(xPos, yPos) == "k":
                    self.bkXPos = xPos
                    self.bkYPos = yPos
                elif self.getPiece(xPos, yPos) == "K":
                    self.wkXPos = xPos
                    self.wkYPos = yPos