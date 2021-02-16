"""
Main driver file, responsible for handling user input and displaying
"""


import pygame as p
import math as m
from Tak import TakEngine as t

WIDTH = HEIGHT = 800
MAX_FPS = 15
DIM = 6
SQSIZE = m.floor((WIDTH-100)/DIM)
IMAGES = {}

'''
Initialise a global dictionary of images. This will be called exactly once in the main
'''


def loadImages():
    # 'w' and 'b' are white and black flats respectively
    # 'e' and 'n' are white and black standing stones, respectively
    # 'A' and 'Z' are white and black capstone
    pieces = ['w', 'e', 'A', 'b', 'n', 'Z']
    for piece in pieces:
        IMAGES[piece] = p.image.load("images/" + piece + ".png")
    # Note: we can access an image by saying 'IMAGES['wp']'



def main():
    # Initialises Pygame's screen
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("light gray"))
    gs = t.GameState(DIM)
    loadImages()  # Only once, before the loop
    running = True

    while running:
        # All input related events
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN and gs.winner == "": # There is a click and no one has won yet
                # First, we locate which square has been clicked
                location = p.mouse.get_pos()  # (x,y) location of the mouse
                col = (location[0] - 50) // SQSIZE
                row = (location[1] - 50) // SQSIZE
                sqSel = (col, row)

                if 0 <= col < DIM and 0 <= row < DIM:
                    if not gs.movingStack: # If we are not in the middle of moving a stack
                        # Check what type of action, set or move stack
                        move = ""
                        if gs.board[sqSel[0]][sqSel[1]] == '':
                            move += "set" + gs.pieceType
                        else:
                            move += "move"

                        # We define the action intended to take
                        action = t.Action(sqSel, move, gs)

                        # Check if it is a valid action
                        validActions = gs.get_valid_actions()
                        if action in validActions:
                            gs.make_action(action, gs)

                        # print(action.move)
                    else:
                        gs.move_stack(sqSel)
                    # print(gs.board)
                    # print(gs.stack)


            elif e.type == p.KEYDOWN:
                if e.key == p.K_q:
                    gs.change_piece_type()
                    # print(gs.pieceType)
                if e.key == p.K_w:
                    print(gs.whiteCount)
                    print(gs.piecenum)
                    print(gs.blackCount)
        # Drawing
        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()

'''
Handles drawing
'''

def draw_game_state(screen, gs):
    draw_board(screen)
    draw_pieces(screen, gs)

    ##### Debug drawing
    # Shows current piece type
    if gs.pieceType == "flat":
        p.draw.rect(screen, p.Color("black"), (5, 5, 10, 10))
    elif gs.pieceType == "standing":
        p.draw.rect(screen, p.Color("green"), (5, 5, 10, 10))
    elif gs.pieceType == "cap":
        p.draw.rect(screen, p.Color("red"), (5, 5, 10, 10))

    # Shows turn
    if gs.whiteTurn:
        p.draw.rect(screen, p.Color("white"), (30, 10, 10, 10))
    else:
        p.draw.rect(screen, p.Color("black"), (30, 10, 10, 10))


def draw_board(screen):
    colors = [p.Color("brown"), p.Color("orange")]
    for c in range(DIM):
        for r in range(DIM):
            p.draw.rect(screen, colors[(r+c) % 2], (50+c*SQSIZE, 50+r*SQSIZE, SQSIZE, SQSIZE))


def draw_pieces(screen, gs):
    for c in range(DIM):
        for r in range(DIM):
            if gs.board[c][r] != '':
                count = 0
                for i in gs.board[c][r]:
                    '''
                    p.draw.rect(screen, colors[i], (50+m.floor((c+0.25)*SQSIZE), 50+m.floor((r+0.25-count/8)*SQSIZE),
                                                            m.floor(SQSIZE/2), m.floor(SQSIZE/2)))
                    p.draw.rect(screen, p.Color("green"),
                                (50 + m.floor((c + 0.25) * SQSIZE), 50 + m.floor((r + 0.25 - count / 8) * SQSIZE),
                                 m.floor(SQSIZE / 2), m.floor(SQSIZE / 2)), 2)
                    '''
                    # 'i' is the character that represents each piece as stored in the board.
                    # 'w' and 'b' are white and black flats respectively
                    # 'e' and 'n' are white and black standing stones, respectively
                    # 'A' and 'Z' are white and black capstone
                    screen.blit(IMAGES[i], p.Rect(50+m.floor((c+0.25)*SQSIZE), 50+m.floor((r+0.25-count/8)*SQSIZE),
                                                            m.floor(SQSIZE/2), m.floor(SQSIZE/2)))
                    count += 1


if __name__ == "__main__":
    main()
