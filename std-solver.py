#!/usr/bin/python

"""
An experiment in solving spot-the-difference puzzles.

(c) Shish 2011, licensed under the GPLv3 because it's obnoxiously
forceful in its enforcement of freedom; I'm open to giving people
access with different licenses if you contact me and ask for it.
"""

import wx

class PlayZonesSelectFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, wx.ID_ANY, 'Select Play Zones', size=(parent.game_zone[2], parent.game_zone[3]))
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        self.parent = parent

        self.zone_a = [0, 0, 100, 100]
        self.zone_b = [150, 0, 100, 100]

        screen = wx.ScreenDC()
        size = screen.GetSize()
        self.bmp = wx.EmptyBitmap(size[0], size[1])
        wx.MemoryDC(self.bmp).Blit(0, 0, parent.game_zone[2], parent.game_zone[3], screen, parent.game_zone[0], parent.game_zone[1])

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)

        #self.Show()
        self.ShowFullScreen(True, wx.FULLSCREEN_ALL)

    def OnMotion(self, evt):
        if evt.LeftIsDown():
            self.parent.zone_a[2] = evt.GetX() - self.parent.zone_a[0]
            self.parent.zone_a[3] = evt.GetY() - self.parent.zone_a[1]
            self.OnPaint(None)
        if evt.RightIsDown():
            self.parent.zone_b[2] = evt.GetX() - self.parent.zone_b[0]
            self.parent.zone_b[3] = evt.GetY() - self.parent.zone_b[1]
            self.OnPaint(None)

    def OnLeftDown(self, evt):
        self.parent.zone_a[0] = evt.GetX()
        self.parent.zone_a[1] = evt.GetY()

    def OnLeftUp(self, evt):
        self.parent.zone_a[2] = evt.GetX() - self.parent.zone_a[0]
        self.parent.zone_a[3] = evt.GetY() - self.parent.zone_a[1]
        print "Zone A: %d:%d %dx%d" % tuple(self.parent.zone_a)
        self.OnPaint(None)

    def OnRightDown(self, evt):
        self.parent.zone_b[0] = evt.GetX()
        self.parent.zone_b[1] = evt.GetY()

    def OnRightUp(self, evt):
        self.parent.zone_b[2] = evt.GetX() - self.parent.zone_b[0]
        self.parent.zone_b[3] = evt.GetY() - self.parent.zone_b[1]
        print "Zone B: %d:%d %dx%d" % tuple(self.parent.zone_b)
        self.OnPaint(None)
        self.Destroy()

    def OnPaint(self, evt):
        dc = wx.AutoBufferedPaintDC(self)
        #dc.SetBackgroundMode(wx.SOLID)
        #dc.Clear()
        dc.DrawBitmap(self.bmp, 0, 0)
        dc.SetLogicalFunction(wx.INVERT)
        dc.DrawRectangle(*self.parent.zone_a)
        dc.DrawRectangle(*self.parent.zone_b)

    def OnCloseWindow(self, evt):
        self.Destroy()

class AlignmentPanel(wx.Panel):
    def __init__(self, frame, parent):
        wx.Panel.__init__(self, frame)
        self.frame = frame
        self.parent = parent

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKey)

        self.max_w = max(parent.zone_a[2], parent.zone_b[2])
        self.max_h = max(parent.zone_a[3], parent.zone_b[3])
        self.min_w = min(parent.zone_a[2], parent.zone_b[2])
        self.min_h = min(parent.zone_a[3], parent.zone_b[3])

        if parent.zone_a[2] > parent.zone_b[2]:
            self.widest = "A"
        elif parent.zone_a[2] < parent.zone_b[2]:
            self.widest = "B"
        else:
            self.widest = None

        if parent.zone_a[3] > parent.zone_b[3]:
            self.tallest = "A"
        elif parent.zone_a[3] < parent.zone_b[3]:
            self.tallest = "B"
        else:
            self.tallest = None

        self.offset_a = [0, 0]
        self.offset_b = [0, 0]

        self.highest_t = 0
        self.highest_a = [0, 0]
        self.highest_b = [0, 0]

        self.load_images()

    def load_images(self):
        parent = self.parent

        self.show_b = True
        self.aligning = False

        #print "Widest : %s" % self.widest
        #print "Tallest: %s" % self.tallest

        screen = wx.ScreenDC()
        size = screen.GetSize()
        self.bmp_a = wx.EmptyBitmap(self.parent.zone_a[2], self.parent.zone_a[3])
        wx.MemoryDC(self.bmp_a).Blit(
            0, 0,                                         # dest x, y
            self.parent.zone_a[2], self.parent.zone_a[3], # dest w, h
            screen,                                           # src
            self.parent.game_zone[0] + self.parent.zone_a[0], # src x
            self.parent.game_zone[1] + self.parent.zone_a[1], # src y
            )

        self.bmp_b = wx.EmptyBitmap(self.parent.zone_b[2], self.parent.zone_b[3])
        wx.MemoryDC(self.bmp_b).Blit(
            0, 0,                                         # dest x, y
            self.parent.zone_b[2], self.parent.zone_b[3], # dest w, h
            screen,                                           # src
            self.parent.game_zone[0] + self.parent.zone_b[0], # src x
            self.parent.game_zone[1] + self.parent.zone_b[1], # src y
            )

    def OnKey(self, evt):
        if evt.GetKeyCode() == wx.WXK_UP:
            if self.tallest == "A":
                if self.offset_b[1] > 0:
                    self.offset_b[1] = self.offset_b[1] - 1
            if self.tallest == "B":
                if self.offset_a[1] > 0:
                    self.offset_a[1] = self.offset_a[1] - 1

        if evt.GetKeyCode() == wx.WXK_DOWN:
            if self.tallest == "A":
                if self.offset_b[1] + self.parent.zone_b[3] < self.parent.zone_a[3]:
                    self.offset_b[1] = self.offset_b[1] + 1
            if self.tallest == "B":
                if self.offset_a[1] + self.parent.zone_a[3] < self.parent.zone_b[3]:
                    self.offset_a[1] = self.offset_a[1] + 1

        if evt.GetKeyCode() == wx.WXK_LEFT:
            if self.widest == "A":
                if self.offset_b[0] > 0:
                    self.offset_b[0] = self.offset_b[0] - 1
            if self.widest == "B":
                if self.offset_a[0] > 0:
                    self.offset_a[0] = self.offset_a[0] - 1

        if evt.GetKeyCode() == wx.WXK_RIGHT:
            if self.widest == "A":
                if self.offset_b[0] + self.parent.zone_b[2] < self.parent.zone_a[2]:
                    self.offset_b[0] = self.offset_b[0] + 1
            if self.widest == "B":
                if self.offset_a[0] + self.parent.zone_a[2] < self.parent.zone_b[2]:
                    self.offset_a[0] = self.offset_a[0] + 1

        if evt.GetKeyCode() == wx.WXK_RETURN:
            self.load_images()

        if evt.GetKeyCode() == wx.WXK_SPACE:
            self.show_b = not self.show_b

        if evt.GetKeyCode() == wx.WXK_BACK:
            self.align()

        if evt.GetKeyCode() == wx.WXK_ESCAPE:
            self.frame.Destroy()

        self.OnPaint(None)

    def align(self):
        self.aligning = True

        self.highest_t = 0
        self.highest_a = [0, 0]
        self.highest_b = [0, 0]

        self.offset_a = [0, 0]
        self.offset_b = [0, 0]

        for x in range(0, self.max_w - self.min_w):
            for y in range(0, self.max_h - self.min_h):
                if self.widest == "A":
                    self.offset_b[0] = x
                elif self.widest == "B":
                    self.offset_a[0] = x

                if self.tallest == "A":
                    self.offset_b[1] = y
                elif self.tallest == "B":
                    self.offset_a[1] = y

                self.OnPaint(None)

        self.offset_a = self.highest_a
        self.offset_b = self.highest_b
        self.OnPaint(None)

    def OnPaint(self, evt):
        dc = wx.AutoBufferedPaintDC(self)
        #dc.SetBackgroundMode(wx.SOLID)
        dc.Clear()
        dc.DrawBitmap(self.bmp_a, self.offset_a[0], self.offset_a[1])

        if self.show_b:
            dc.SetLogicalFunction(wx.EQUIV)
            dc.DrawBitmap(self.bmp_b, self.offset_b[0], self.offset_b[1])

        dc.SetLogicalFunction(wx.SET)

        if self.aligning:
            total = 0
            # sample pixels within the overlapping area
            for x in [n * 0.1 for n in range(1, 10)]:
                for y in [n * 0.1 for n in range(1, 10)]:
                    p = dc.GetPixel(
                        max(self.offset_a[0], self.offset_b[0]) + int(self.min_w * x),
                        max(self.offset_a[1], self.offset_b[1]) + int(self.min_h * y)
                    )
                    total = total + p[0] + p[1] + p[2]
            if total > self.highest_t:
                self.highest_t = total
                self.highest_a = [self.offset_a[0], self.offset_a[1]]
                self.highest_b = [self.offset_b[0], self.offset_b[1]]
            print total, self.highest_t

class MainFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, wx.ID_ANY, 'STD Solver', size=(200, 400), style=wx.STAY_ON_TOP)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        screen = wx.ScreenDC()
        self.game_zone = [0, 0, screen.GetSize()[0], screen.GetSize()[1]]
        self.zone_a = [50, 75, 100, 50]
        self.zone_b = [75, 50, 50, 100]

        #screen.StartDrawingOnTop()
        #screen.DrawCircle(100, 100, 100)
        #screen.Clear()
        #screen.EndDrawingOnTop()

        self.SelectPlayZonesBtn = wx.Button(self,label="Select Play Zones")
        self.SelectPlayZonesBtn.Bind(wx.EVT_BUTTON, self.OnSelectPlayZones)

        self.AlignBtn = wx.Button(self,label="Align")
        self.AlignBtn.Bind(wx.EVT_BUTTON, self.OnAlign)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.SelectPlayZonesBtn, 0, wx.EXPAND)
        sizer.Add(self.AlignBtn, 0, wx.EXPAND)
        self.SetSizer(sizer)
        self.Layout()
        self.Fit()

    def OnSelectPlayZones(self, event):
        PlayZonesSelectFrame(self)

    def OnAlign(self, event):
        #AlignmentFrame(self)
        max_w = max(self.zone_a[2], self.zone_b[2])
        max_h = max(self.zone_a[3], self.zone_b[3])

        f = wx.Dialog(self, title='Solver', size=(max_w, max_h))
        f.Bind(wx.EVT_CLOSE, lambda e: f.Destroy())
        p = AlignmentPanel(f, self)
        p.SetFocus()
        f.Show()

    def OnCloseWindow(self, event):
        self.Destroy()

def main():
    app = wx.App(redirect=False)
    frame = MainFrame(None)
    frame.Show()
    app.SetTopWindow(frame)
    app.MainLoop()

if __name__=='__main__':
    main()
