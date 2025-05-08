import wx
from model import Model
from view import View
from controller import Controller

if __name__ == "__main__":
    app = wx.App()
    model = Model()
    view = View(None, None)  # Controller will be set in Controller init
    controller = Controller(model, view)
    app.MainLoop()