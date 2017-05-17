'''
Title: maverickGame.py
Author: Jake Zatecky
Description:
    Implementation of the mavEngine.
'''

import pygame, mavEngine

def main():
    BUTTON_FG = (205, 133, 63)
    BUTTON_BG = (0, 0, 0)

    mavIcon = pygame.image.load("mavIcon.gif")
    transColor = mavIcon.get_at((34, 0))  # non-alpha transparency
    mavIcon.set_colorkey(transColor)

    pygame.display.set_icon(mavIcon)  # attempt to change game icon
    pygame.display.set_caption("Maverick")

    keepGoing = True

    diff = 0.0

    while keepGoing:
        menu = mavEngine.Menu(BUTTON_FG, BUTTON_BG)
        menu.start()

        if menu.startGame:
            game = mavEngine.Game(BUTTON_FG, BUTTON_BG)
            game.difficulty = diff
            game.start()
            menu.startGame = False

            if game.exitProgram:
                keepGoing = False

        elif menu.about:
            about = mavEngine.About(BUTTON_FG, BUTTON_BG)
            about.start()

            if about.exitProgram:
                keepGoing = False

        elif menu.settings:
            settings = mavEngine.Settings(BUTTON_FG, BUTTON_BG)
            settings.sDiff.value = (diff * 16)  # sets default difficulty value; have to convert back for user
            settings.start()

            diff = settings.diff

            if settings.exitProgram:
                keepGoing = False

        else:
            keepGoing = False

if __name__ == "__main__":
    main()
