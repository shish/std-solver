#!/usr/bin/python

import Image
import time

try:
    import wx
except:
    wx = False

try:
    import ImageGrab
except:
    ImageGrab = False

try:
    # could use ctypes?
    import win32api
    import win32con
except:
    win32api = False

try:
    import Xlib
    import Xlib.display
except:
    Xlib = False


class AutoMeta:
    def __init__(self):
        if wx:
            self.__wx_app = wx.App()
        elif ImageGrab:
            pass

        if Xlib:
            self.__display = Xlib.display.Display()


    def grab_screen(self, x, y, w, h):
        if wx:
            screen = wx.ScreenDC()
            size = screen.GetSize()
            bmp = wx.EmptyBitmap(w, h)
            wx.MemoryDC(bmp).Blit(
                0, 0,   # dest x, y
                w, h,   # area w, h
                screen, # src
                x, y    # src x, y
            )
            img = wx.ImageFromBitmap(bmp)
            pil_image = Image.new('RGB', (img.GetWidth(), img.GetHeight()))
            pil_image.fromstring(img.GetData())
            return pil_image
        elif ImageGrab:
            return ImageGrab.grab((x, y, w, h))


    def move_mouse(self, x, y):
        if Xlib:
            Xlib.ext.xtest.fake_input(self.__display, Xlib.X.MotionNotify, x=x, y=y)
            self.__display.sync()
        elif win32api:
            win32api.SetCursorPos((x, y))


    def left_click(self):
        if Xlib:
            button = 1
            Xlib.ext.xtest.fake_input(self.__display, Xlib.X.ButtonPress, [None, 1, 3, 2, 4, 5][button])
            self.__display.sync()
            time.sleep(.1)
            Xlib.ext.xtest.fake_input(self.__display, Xlib.X.ButtonRelease, [None, 1, 3, 2, 4, 5][button])
            self.__display.sync()
        elif win32api:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            time.sleep(.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


    def mouse_pos(self):
        if Xlib:
            pos = self.__display.screen().root.query_pointer()._data
            return pos["root_x"], pos["root_y"]


    def prompt_pos(self, prompt):
        for n in [3, 2, 1]:
            print "\r" + prompt + " " + str(n),
            import sys
            sys.stdout.flush()
            time.sleep(1)
        p = self.mouse_pos()
        print "\r" + prompt + " " + str(p)
        return p


def test():
    a = AutoMeta()
    g = a.screengrab(0,0,512,512)
    print g
    g.show()
    g.show()
    a.move_mouse(80, 80)
    a.left_click()


if __name__ == "__main__":
    test()
