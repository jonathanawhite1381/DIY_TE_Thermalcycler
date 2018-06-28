#MIT License
#
#Copyright (c) 2018 Jonathan A. White
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from Step import Step
from LabelEntry import LabelEntry
try:
    from Tkinter import * #python 2.7
except:
    from tkinter import * #python 3


# steps denote a phyical step in the thermocycling procedure where the plate is held at a specified temperature for a specified time.
class TempStep(Step):
    parameter = "Temperature"
    def __init__(self, _super):
        Step.__init__(self, _super)
        self.box.config(text = self.parameter)
        self.temp = LabelEntry(self.box, 0, 2, "Temperature (C): ")
        self.time = LabelEntry(self.box, 0, 0, "Time (s):")
        self.entries.append(self.time)
        self.entries.append(self.temp)
        self.steptype = "TempStep"

    def run(self, cleanup = None, iter = None, time = None):
        self.setPoint(self.temp.saved)
        self.box.config(bg='green')
        self.timerWidget.config(text="Waiting to reach set point...")
        while abs(self.getTemp() - self.temp.saved) > 1:
            self.event.wait(1)
            self.checkIfCancel()
            print("Equilibrating...")
        Step.pause(self, self.time.saved)

    def setPoint(self, temp):
        raise NotImplementedError("Error: must redefine setPoint method for TempStep class when initializing the device connection")

    def getTemp(self):
        raise NotImplementedError(
            "Error: must redefine getTemp method for TempStep class when initializing the device connection")