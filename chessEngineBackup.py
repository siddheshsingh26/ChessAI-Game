"""
this class is responsible for starting all the information about the current state of a chess game . It will also be
responsible for determining the valid moves at the current state It will also keep move log
"""
from multiprocessing import set_forkserver_preload
from pickle import TRUE
from re import S
from tokenize import endpats



class GamerState():
    def __init__(self):
        #board is an 8x8 2d list,each element of the list has character 
        #the first character represents the color of the piece,'b' or 'w'
        #the second character represents the type of piece 'K','Q','R','B','N' or 'P'
        #"--" represent the empty space with no piece
        self.board=[
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]
        ]
        self.moveFuctions={'p':self.getPawnMoves,'R':self.getRookMoves,'N':self.getKnightMoves,
                           'B':self.getBishopMoves,'Q':self.getQueenMoves,'K':self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation=(7,4)
        self.blackKingLocation=(0,4)
        self.checkMate=False
        self.staleMate=False        
        

# takes a move as a parameter and executes it (this will not workfor castling ,pawn promotion and en-passant)


    def makeMove(self,move):
        self.board[move.startRow][move.startCol]="--"
        self.board[move.endRow][move.endCol]=move.pieceMoved
        self.moveLog.append(move)  #log the move so we can undo it later
        self.whiteToMove=not self.whiteToMove #swap players
        #udate the king's location if moved
        if move.pieceMoved=="wk":
            self.whiteKingLocation=(move.endRow,move.endCol)
        elif move.pieceMoved=="bk":
            self.blackKingLocation=(move.endRow,move.endCol)

# Undo the last move made
    def undoMove(self):
        if len (self.moveLog) !=0:   #Make sure that there is  a move to undo
            move=self.moveLog.pop()
            self.board[move.startRow][move.startCol]=move.pieceMoved
            self.board[move.endRow][move.endCol]=move.pieceCaptured
            self.whiteToMove=not self.whiteToMove   #switch turns back
#Update Kings position if needed
            if move.pieceMoved=="wK":
                self.whiteKingLocation=(move.startRow,move.startCol)
            elif move.pieceMoved=="bK":
                self.blackKingLocation=(move.endRow,move.endCol)
                




#All moves considering checks 
    def getValidMoves(self):
    # 1)generate all possible moves
        moves = self.getAllPossibleMoves()
    # 2)for each move,make the move
        for i in range(len(moves)-1,-1,-1):      #when removing from a list go back the through that list
            self.makeMove(moves[i])
    # 3) generate all opponent's moves
        
    # 4)for each of your opponent's moves ,see if they attack your king 
            self.whiteToMove=not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
    # 5)if they attack your king not a valid moves
            self.whiteToMove=not self.whiteToMove
            self.undoMove()
        if len(moves)==0:
            if self.inCheck():
                self.checkMate=True
                
            else:
                self.staleMate=True
        else:
            self.checkMate=False
            self.staleMate=False
        return moves  #Temporary


#this function for current player is in check or not 
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])

#this fuction for if enemy can attack it or not 
    def squareUnderAttack(self,r,c):
        self.whiteToMove=not self.whiteToMove       #switch to opponents turn
        oppMoves=self.getAllPossibleMoves()
        self.whiteToMove=not self.whiteToMove       #switch turns back
        for move in oppMoves:
            if move.endRow==r and move.endCol==c:
                return True
        return False

        
#All moves without considering checks
    def getAllPossibleMoves(self):
        moves=[]
        for r in range(len(self.board)):    #number of rows
            for c in range(len(self.board[r])):     #number of cols
                turn=self.board[r][c][0]        # to decect color by first letter of piece
                if (turn=="w" and self.whiteToMove) or (turn=='b' and not self.whiteToMove):
                    piece=self.board[r][c][1]
                    self.moveFuctions[piece](r,c,moves)     #calls the appropritate move fuction base on piece type
        return moves

# Get all the pawn moves for the pawn located at row,col and these moves to the list 
    def getPawnMoves(self,r,c,moves):
        if self.whiteToMove:    #white pawn moves
            if self.board[r-1][c]=="--":    # spuare pawn advance
                moves.append(Move((r,c),(r-1,c),self.board))
                if r==6 and self.board[r-2][c]=="--":   #2 sq pawn advance
                    moves.append(Move((r,c),(r-2,c),self.board))
            if c-1>=0:  #captures to the left
                if self.board[r-1][c-1][0]=="b":    #enemy piece to capture
                    moves.append(Move((r,c),(r-1,c-1),self.board))
            if c+1<=7:  #captures to the right
                if self.board[r-1][c+1][0]=="b":
                    moves.append(Move((r,c),(r-1,c+1),self.board))

        
        else:
            if self.board[r+1][c]=="--":    # spuare pawn advance
                moves.append(Move((r,c),(r+1,c),self.board))
                if r==1 and self.board[r+2][c]=="--":   #2 sq pawn advance
                    moves.append(Move((r,c),(r+2,c),self.board))
            if c-1>=0:  #captures to the left
                if self.board[r+1][c-1][0]=="w":    #enemy piece to capture
                    moves.append(Move((r,c),(r+1,c-1),self.board))
            if c+1<=7:  #captures to the right
                if self.board[r+1][c+1][0]=="w":
                    moves.append(Move((r,c),(r+1,c+1),self.board))

# Get all the Rook moves for the Rook located at row,col and these moves to the list 
    def getRookMoves(self,r,c,moves):
        directions=((-1,0),(0,-1),(1,0),(0,1))
        enemyColor="b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow=r+d[0]*i                        
                endCol=c+d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    endPiece=self.board[endRow][endCol]
                    if endPiece=="--":     #empty space valid
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0]==enemyColor:     #enemy piece valid
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:   #friendly piece invalid
                        break
                else:   #off board
                    break

                    
                        
            
                    

                
# Get all the knight moves for the knight located at row,col and these moves to the list 
    def getKnightMoves(self,r,c,moves):
        knightMoves=((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        allyColor="w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow=r+m[0]
            endCol=c+m[1]
            if 0<=endRow<8 and 0<=endCol<8:
                endPiece=self.board[endRow][endCol]
                if endPiece[0]!=allyColor:
                    moves.append(Move((r,c),(endRow,endCol),self.board))




# Get all the bishop moves for the bishop located at row,col and these moves to the list 
    def getBishopMoves(self,r,c,moves):
        directions=((-1,-1),(-1,1),(1,-1),(1,1))
        enemyColor="b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow=r+d[0]*i                        
                endCol=c+d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    endPiece=self.board[endRow][endCol]
                    if endPiece=="--":     #empty space valid
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0]==enemyColor:     #enemy piece valid
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:   #friendly piece invalid
                        break
                else:   #off board
                    break
# Get all the Queen moves for the Queen located at row,col and these moves to the list 
    def getQueenMoves(self,r,c,moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)
        pass
      
# Get all the King moves for the King located at row,col and these moves to the list 
    def getKingMoves(self,r,c,moves):
        kingMoves=((-1,-1),(-1,1),(1,-1),(1,1),(-1,0),(0,-1),(1,0),(0,1))
        allyColor="w" if self.whiteToMove else "b"
        for i in range(8):
            endRow=r+kingMoves[i][0]
            endCol=r+kingMoves[i][1]
            if 0<=endRow<8 and 0<=endCol<8:
                endPiece=self.board[endRow][endCol]
                if endPiece[0]!=allyColor:
                    moves.append(Move((r,c),(endRow,endCol),self.board))






class Move():
    #maps keys to values
    #key:value
    ranksToRows={"1":7,"2":6,"3":5,"4":4,
                "5":3,"6":2,"7":1,"8":0,}
    rowsToRanks={v: k for k,v in ranksToRows.items()}
    filesToCols={"a":0,"b":1,"c":2,"d":3,
                "e":4,"f":5,"g":6,"h":7,}
    colsToFiles={v: k for k,v in filesToCols.items()}



    def __init__(self,startSq,endSq,board):
        self.startRow=startSq[0]
        self.startCol=startSq[1]
        self.endRow=endSq[0]
        self.endCol=endSq[1]
        self.pieceMoved=board[self.startRow][self.startCol]
        self.pieceCaptured=board[self.endRow][self.endCol]
        
        self.moveID=self.startRow*1000 + self.startCol*100 + self.endRow + self.endCol
        

#overriding the equals method
    def __eq__(self,other):
        if isinstance(other,Move):
            return self.moveID==other.moveID
        return False




    def getchessNotation(self):
        return self.getRankFile(self.startRow,self.startCol)+self.getRankFile(self.endRow,self.endCol)

    def getRankFile(self,r,c):
        return self.colsToFiles[c]+self.rowsToRanks[r]


        






