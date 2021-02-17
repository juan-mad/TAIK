"""
This class is responsible for storing all the information about the current state of the game. It will also be
responsible for determining the valid moves at the current state. It will also keep a move log.
"""
import copy


class GameState():
    def create_board(self, d):
        if d == 3:
            self.capnum = 0
            self.piecenum = 10
            self.board = [['', '', ''], ['', '', ''], ['', '', '']]
        if d == 4:
            self.capnum = 0
            self.piecenum = 15
            self.board = [['', '', '', ''], ['', '', '', ''], ['', '', '', ''], ['', '', '', '']]
        if d == 5:
            self.capnum = 1
            self.piecenum = 21
            self.board = [['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
                          ['', '', '', '', '']]
        if d == 6:
            self.capnum = 1
            self.piecenum = 30
            self.board = [['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', ''],
                          ['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', '']]
        if d == 7:
            self.capnum = 1  # 1 or 2, not definitive
            self.piecenum = 40
            self.board = [['', '', '', '', '', '', ''], ['', '', '', '', '', '', ''], ['', '', '', '', '', '', ''],
                          ['', '', '', '', '', '', ''], ['', '', '', '', '', '', ''], ['', '', '', '', '', '', ''],
                          ['', '', '', '', '', '', '']]
        if d == 8:
            self.capnum = 2
            self.piecenum = 50
            self.board = [['', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', ''],
                          ['', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', ''],
                          ['', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', ''],
                          ['', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '']]

    def __init__(self, dim):
        # Create the board
        self.dim = dim
        self.winner = ""
        self.ROAD = set(range(self.dim))
        self.board = []
        self.capnum = -1
        self.piecenum = -1
        self.create_board(self.dim)
        self.whiteCount = 0
        self.whiteCapCount = 0
        self.blackCount = 0
        self.blackCapCount = 0

        self.roadBoard = []
        self.startPoints = set()
        for i in range(self.dim):
            self.startPoints.add((i, 0))
            self.startPoints.add((self.dim - 1, i))
        # Dictionary with the equivalence between coordinates and Tak notation for each square
        self.ranksToRows = {}
        self.rowsToRanks = {}
        self.filesToCols = {}
        self.colsToFiles = {}
        for i in range(dim):
            self.ranksToRows[chr(49 + i)] = dim - i - 1
            self.filesToCols[chr(97 + i)] = i

        self.rowsToRanks = {v: k for k, v in self.ranksToRows.items()}
        self.colsToFiles = {v: k for k, v in self.filesToCols.items()}

        self.whiteTurn = False
        self.initialTurn = True
        self.actionLog = []
        self.pieceType = "flat"
        self.movingStack = False
        self.stack = ""
        self.stackOrigin = [-1, -1]
        self.stackPos = [-1, -1]
        self.aux = self.stackPos
        self.leftPiece = True
        self.stackInitialLen = 0
        self.stackMoves = 0
        self.moveDir = -1

    def get_valid_actions(self):
        actions = []
        # Goes through every square
        for c in range(self.dim):
            for r in range(self.dim):
                # Adds possible setting actions
                if self.board[c][r] == '':  # If square is empty
                    # Possible to set a new flatstone or standing stone
                    if ((self.whiteTurn and self.whiteCount < self.piecenum) or
                            ((not self.whiteTurn) and self.blackCount < self.piecenum)):
                        actions.append(Action((c, r), "setflat", self))
                        actions.append(Action((c, r), "setstanding", self))
                    # Possible to set a new capstone
                    if ((self.whiteTurn and self.whiteCapCount < self.capnum) or
                            ((not self.whiteTurn) and self.blackCapCount < self.capnum)):
                        actions.append(Action((c, r), "setcap", self))

                # Adds possible move actions
                if self.board[c][r] != '':
                    topPiece = self.board[c][r][-1:]
                    if self.whiteTurn:
                        if topPiece == 'w' or topPiece == 'e' or topPiece == 'A':
                            actions.append(Action((c, r), "move", self))
                    else:
                        if topPiece == 'b' or topPiece == 'n' or topPiece == 'Z':
                            actions.append(Action((c, r), "move", self))
        return actions

    def make_action(self, action, gs):
        '''
        SETTING A NEW PIECE IN THE BOARD
        '''
        # If user wants to set a flatstone
        if action.move == "setflat":
            if self.whiteTurn:  # white's turn
                self.board[action.pos[0]][action.pos[1]] += "w"
                self.whiteCount = self.whiteCount + 1
                print(self.whiteCount)
            else:  # black's turn
                self.board[action.pos[0]][action.pos[1]] += "b"
                self.blackCount = self.blackCount + 1
                print(self.blackCount)
            self.change_turn()

        # If user wants to set a standing stone
        if action.move == "setstanding":
            if self.whiteTurn:  # white's turn
                self.board[action.pos[0]][action.pos[1]] += "e"
                self.whiteCount += 1
            else:  # black's turn
                self.board[action.pos[0]][action.pos[1]] += "n"
                self.blackCount += 1
            self.change_turn()

        # If user wants to set a standing stone
        if action.move == "setcap":
            if self.whiteTurn:  # white's turn
                self.board[action.pos[0]][action.pos[1]] += "A"
                self.whiteCapCount += 1
            else:  # black's turn
                self.board[action.pos[0]][action.pos[1]] += "Z"
                self.blackCapCount += 1
            self.change_turn()

        '''
        MOVING A STACK OF PIECES
        '''
        if action.move == "move":
            # Select maximum stack possible (all pieces or top DIM pieces)
            self.stack = gs.board[action.pos[0]][action.pos[1]][-6:]
            self.stackInitialLen = len(self.stack)
            gs.board[action.pos[0]][action.pos[1]] = gs.board[action.pos[0]][action.pos[1]][:-len(self.stack)]
            self.stackOrigin = [action.pos[0], action.pos[1]]
            self.stackPos[0] = self.stackOrigin[0]
            self.stackPos[1] = self.stackOrigin[1]
            self.movingStack = True

            # The change of turns when moving a stack will take place in the method move_stack
        # Record the action in the log
        self.actionLog.append(action)

    def change_piece_type(self):
        if self.pieceType == "flat":
            self.pieceType = "standing"
            return
        if self.pieceType == "standing":
            self.pieceType = "cap"
            return
        if self.pieceType == "cap":
            self.pieceType = "flat"
            return

    def move_stack(self, clickpos):  # This method is called if self.movingStack == True AND there has been a click
        # Click again on the original square to drop bottom piece
        if clickpos == tuple(self.stackOrigin) and self.stackOrigin == self.stackPos:
            self.board[self.stackOrigin[0]][self.stackOrigin[1]] += self.stack[0]
            self.stack = self.stack[1:]
            # If no piece remains, action is cancelled
            if len(self.stack) == 0:
                self.stackOrigin = [-1, -1]
                self.stackPos = [-1, -1]
                self.movingStack = False
                self.moveDir = -1
                return
            return

        # Click again on the current square to drop bottom piece
        if clickpos == tuple(self.stackPos):
            self.board[self.stackPos[0]][self.stackPos[1]] += self.stack[0]
            self.stack = self.stack[1:]
            self.leftPiece = True
            # If no piece remains, action is cancelled
            if len(self.stack) == 0:
                self.stackOrigin = [-1, -1]
                self.stackPos = [-1, -1]
                self.movingStack = False
                self.leftPiece = True
                self.moveDir = -1
                # Changes turns
                self.change_turn()
                return
            return

        # Click on valid adjacent square to move the stack
        # self.dir controls the selected direction
        # TO DO: check if top piece of adjacent stack is flatstone so that move is legal

        # Move to right sq
        if clickpos == (self.stackPos[0] + 1, self.stackPos[1]) and self.stackPos[0] < (
                self.dim - 1) and self.leftPiece:
            if (self.board[self.stackPos[0] + 1][self.stackPos[1]] == '' or
                    self.board[self.stackPos[0] + 1][self.stackPos[1]][-1:] == 'b' or
                    self.board[self.stackPos[0] + 1][self.stackPos[1]][-1:] == 'w'):
                # if no move direction has been selected, or it has and the move is correct, proceed
                if self.moveDir == 0 or self.moveDir == -1:
                    self.stackPos[0] += 1
                    self.leftPiece = False
                    self.moveDir = 0
                return

        # Move to left sq
        if clickpos == (self.stackPos[0] - 1, self.stackPos[1]) and self.stackPos[0] > 0 and self.leftPiece:
            if (self.board[self.stackPos[0] - 1][self.stackPos[1]] == '' or
                    self.board[self.stackPos[0] - 1][self.stackPos[1]][-1:] == 'b' or
                    self.board[self.stackPos[0] - 1][self.stackPos[1]][-1:] == 'w'):
                # if no move direction has been selected, or it has and the move is correct, proceed
                if self.moveDir == 2 or self.moveDir == -1:
                    self.stackPos[0] -= 1
                    self.leftPiece = False
                    self.moveDir = 2
                return

        # Move to below sq
        if clickpos == (self.stackPos[0], self.stackPos[1] + 1) and self.stackPos[1] < (
                self.dim - 1) and self.leftPiece:
            if (self.board[self.stackPos[0]][self.stackPos[1] + 1] == '' or
                    self.board[self.stackPos[0]][self.stackPos[1] + 1][-1:] == 'b' or
                    self.board[self.stackPos[0]][self.stackPos[1] + 1][-1:] == 'w'):
                # if no move direction has been selected, or it has and the move is correct, proceed
                if self.moveDir == 3 or self.moveDir == -1:
                    self.stackPos[1] += 1
                    self.leftPiece = False
                    self.moveDir = 3
                return

        # Move to above sq
        if clickpos == (self.stackPos[0], self.stackPos[1] - 1) and self.stackPos[1] > 0 and self.leftPiece:
            if (self.board[self.stackPos[0]][self.stackPos[1] - 1] == '' or
                    self.board[self.stackPos[0]][self.stackPos[1] - 1][-1:] == 'b' or
                    self.board[self.stackPos[0]][self.stackPos[1] - 1][-1:] == 'w'):
                # if no move direction has been selected, or it has and the move is correct, proceed
                if self.moveDir == 1 or self.moveDir == -1:
                    self.stackPos[1] -= 1
                    self.leftPiece = False
                    self.moveDir = 1
                return
        # If click in that square, place bottom piece. Iterate.
        # If click next square, move stack, one piece must have stayed behind
        # Once no controllable stack remains, end the action, this time it is complete

    def change_turn(self):
        # Checks (road) victory
        self.check_victory()

        # Changes turns
        if self.whiteTurn and self.initialTurn:
            self.whiteTurn = not self.whiteTurn
            self.initialTurn = False
        self.whiteTurn = not self.whiteTurn

    def check_victory(self):
        # First, we check a road win
        pathCheck = set(range(self.dim))
        whitePieces = set()
        blackPieces = set()
        # We get the top piece of every square
        self.roadBoard = copy.deepcopy(self.board)
        for c in range(self.dim):
            for r in range(self.dim):
                self.roadBoard[c][r] = self.roadBoard[c][r][-1:]
                if self.roadBoard[c][r] == 'A' or self.roadBoard[c][r] == 'w':
                    whitePieces.add((c, r))
                    self.roadBoard[c][r] = 'w'
                if self.roadBoard[c][r] == 'Z' or self.roadBoard[c][r] == 'b':
                    blackPieces.add((c, r))
                    self.roadBoard[c][r] = 'b'

        # Check for paths
        # A path must start/end in col 0 or in row 0. We first check in col 0, then in row 0
        # startPieces holds the white pieces (later the black ones) that are in the upper row and rightmost column.
        startPieces = self.startPoints.intersection(whitePieces)
        if startPieces != set():  # If this set isn't empty, we check for a path
            self.check_path("w", startPieces)
        startPieces = self.startPoints.intersection(blackPieces)
        if startPieces != set():
            self.check_path("b", startPieces)

        # Check for flat win
        # If a player has no pieces left
        if ((self.whiteCount == self.piecenum and self.whiteCapCount == self.capnum) or
                (self.blackCount == self.piecenum and self.blackCapCount == self.capnum)):
            self.check_flat_win()

        # If there are no free spaces left
        freeSpaceLeft = False
        for c in range(self.dim):
            for r in range(self.dim):
                if self.board[c][r] == '':
                    freeSpaceLeft = True
                    break
            else:  # This 'else' is only entered if the inner for loop is not broken.
                continue
            break  # If the inner loop was broken, we want to break the outer loop too.

        if not freeSpaceLeft:
            self.check_flat_win()

    def check_flat_win(self):
        topBoard = copy.deepcopy(self.board)
        count = 0
        for c in range(self.dim):
            for r in range(self.dim):
                if topBoard[c][r][-1:] == 'w':
                    count += 1
                if topBoard[c][r][-1:] == 'b':
                    count -= 1

        if count == 0:
            self.winner = 'tie'
            print("Game ended in TIE")
        if count > 0:
            self.winner = 'w'
            print("White flat win")
        if count < 0:
            self.winner = 'b'
            print("Black flat win")

    def check_path(self, color, startPieces):
        pathContinues = True
        beginningExists = True
        pathBeginning = startPieces.copy()

        while beginningExists:
            piece = pathBeginning.pop()
            toCheck = {piece}
            checked = set()
            pathcol = set()
            pathrow = set()
            pathContinues = True

            while pathContinues:
                piece = toCheck.pop()
                checked.add(piece)
                c = piece[0]
                r = piece[1]
                pathcol.add(c)
                pathrow.add(r)

                if pathcol == self.ROAD or pathrow == self.ROAD:
                    beginningExists = False
                    pathContinues = False
                    self.winner = color
                    if color == 'w':
                        print("White Road Victory")
                    if color == 'b':
                        print("Black Road Victory")
                    break

                if c + 1 < self.dim:
                    if (not {(c + 1, r)}.issubset(checked)) and self.roadBoard[c + 1][r] == color:
                        toCheck.add((c + 1, r))
                if c - 1 >= 0:
                    if (not {(c - 1, r)}.issubset(checked)) and self.roadBoard[c - 1][r] == color:
                        toCheck.add((c - 1, r))
                if r + 1 < self.dim:
                    if (not {(c, r + 1)}.issubset(checked)) and self.roadBoard[c][r + 1] == color:
                        toCheck.add((c, r + 1))
                if r - 1 >= 0:
                    if (not {(c, r - 1)}.issubset(checked)) and self.roadBoard[c][r - 1] == color:
                        toCheck.add((c, r - 1))

                if toCheck == set():
                    pathContinues = False
                    if pathBeginning == set():
                        beginningExists = False




class Action():
    def __init__(self, pos, move, gs):
        self.dim = gs.dim
        self.move = move
        self.pos = pos

    def get_tak_notation(self, gs):
        return gs.colsToFiles[self.pos[0]] + gs.rowsToRanks[self.pos[1]]

    def __eq__(self, other):
        if isinstance(other, Action):
            if (self.pos == other.pos) and (self.move == other.move):
                return True
        return False
