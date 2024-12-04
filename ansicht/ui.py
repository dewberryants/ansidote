"""
ANSIcht -  A simple ANSI art editor.
Copyright (C) 2023 Dominik Behrens

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the Lesser GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import tkinter
import pygame
import numpy as np

from tkinter.simpledialog import Dialog

from ansicht.resources import def_palette


class CharacterMap:
    def __init__(self, w, h, font: pygame.font.Font):
        self.w, self.h = w, h
        self.surface = None
        self.font = font
        self.cols = int(w / font.size(" ")[1])
        self.sq = round(w / self.cols)
        # Ugly hardcoded characters right now, load these externally later
        self.chars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        self.chars += "1234567890!§$%&/()=?`´+#-.,;:_'*²³{[]}\\~@<>|^°"
        self.chars += "─━│┃┄┅┆┇┈┉┊┋┌┍┎┏┐┑┒┓└┕┖┗┘┙┚┛├┝┞┟┠┡┢┣┤┥┦┧┨┩┪┫┬┭┮┯┰┱┲┳┴┵" \
                      "┶┷┸┹┺┻┼┽┾┿╀╁╂╃╄╅╆╇╈╉╊╋╌╍╎╏═║╒╓╔╕╖╗╘╙╚╛╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬" \
                      "╭╮╯╰╱╲╳╴╵╶╷╸╹╺╻╼╽╾╿▀▁▂▃▄▅▆▇█▉▊▋▌▍▎▐░▒▓▔▕▖▗▘▙▚▛▜▝▞▟"
        self.marker = (0, 0)
        self.selected = " "
        self.redraw()

    def redraw(self):
        self.surface = pygame.Surface((self.w, self.h))
        self.surface.fill((30, 35, 40))
        x = 0
        y = 0
        for char in self.chars:
            srf = self.font.render(f"{char} ", 1, (180, 180, 180))
            if int(x) / self.sq == self.cols:
                x = 0
                y += self.sq
            self.surface.blit(srf, (x + .25 * self.sq, y))
            if (x / self.sq, y / self.sq) == self.marker:
                pygame.draw.rect(self.surface, (0, 255, 0), (x, y, self.sq, self.sq), width=1)
            x += self.sq

    def select(self, x, y):
        try:
            self.marker = (x, y)
            self.selected = self.chars[y * self.cols + x]
            self.redraw()
        except IndexError:
            pass


class Palette:
    def __init__(self, w, h):
        self.marker_bg = (0, 0)
        self.marker_fg = (0, 0)
        self.selected_bg = (0, 0, 0)
        self.selected_fg = (0, 0, 0)
        self.w = w
        self.h = h
        self.palette = def_palette
        self.cols = -1
        self.sq = -1
        self.surface = None
        self.redraw()

    def select(self, x, y, fg=False):
        if self.cols * y + x > self.palette.shape[0] - 1:
            return
        r, g, b = self.palette[self.cols * y + x]
        if fg:
            self.selected_fg = (r, g, b)
            self.marker_fg = (x, y)
        else:
            self.selected_bg = (r, g, b)
            self.marker_bg = (x, y)
        self.redraw()

    def redraw(self):
        self.sq = np.sqrt(self.w * self.h / self.palette.shape[0])
        self.cols = round(self.w / self.sq)
        rows = int(self.palette.shape[0] / self.cols)
        if self.palette.shape[0] - rows * self.cols > 0:
            rows += 1
        self.surface = pygame.Surface((self.cols * self.sq, self.h))
        self.surface.fill((30, 35, 40))
        for row in range(rows):
            for column in range(self.cols):
                if row * self.cols + column > self.palette.shape[0] - 1:
                    continue
                r, g, b = self.palette[row * self.cols + column]
                pygame.draw.rect(self.surface, (r, g, b), (column * self.sq, row * self.sq, self.sq, self.sq))
                if (column, row) == self.marker_bg:
                    pygame.draw.rect(self.surface, (0, 255, 0),
                                     (column * self.sq, row * self.sq, self.sq, self.sq),
                                     width=1)
                elif (column, row) == self.marker_fg:
                    pygame.draw.rect(self.surface, (0, 0, 255),
                                     (column * self.sq, row * self.sq, self.sq, self.sq),
                                     width=1)


class SettingsDialog(Dialog):
    def __init__(self, w, h):
        self.entry1, self.entry2 = None, None
        self.w, self.h = w, h
        super().__init__(None)

    def body(self, master):
        tkinter.Label(master, text="Canvas Width:").grid(row=0)
        self.entry1 = tkinter.Entry(master)
        self.entry1.insert(0, str(self.w))
        self.entry1.grid(row=0, column=1)

        tkinter.Label(master, text="Canvas Height:").grid(row=1)
        self.entry2 = tkinter.Entry(master)
        self.entry2.insert(0, str(self.h))
        self.entry2.grid(row=1, column=1)
        return self.entry1

    def apply(self):
        try:
            self.w = int(self.entry1.get())
            self.h = int(self.entry2.get())
        except ValueError:
            print("Invalid W/H")
        super().apply()

    def cancel(self, event: None = ...):
        self.withdraw()
        self.destroy()


def open_settings_dialog(w, h):
    d = SettingsDialog(w, h)
    return d.w, d.h
