#MIT License
#
#Copyright (c) 2018 Jonathan A. White
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from USB_GUI import *
from Therm import Thermocycler
from matplotlib import pyplot as plt
import matplotlib
from threading import Thread, Lock
import tkMessageBox
import csv


class tempGUI(usbGUI):
    def __init__(self, master):
        self.devicetype = Thermocycler
        self.master = master
        usbGUI.__init__(self, master)
        master.wm_title("Temperature Controller")
        self.canvas.config(width = 600, height = 400)
        self.connected = False

        #choose/display current temperature pFrame
        manualTempControlFrame = LabelFrame(self.mainframe, padx = 5, pady = 5)
        manualTempControlFrame.grid(row = 1, column = 0, sticky = W)
        Label(manualTempControlFrame, text=" Current Set Point (C):").grid(column = 0, row = 0, sticky = W)
        self.setptdisp = Label(manualTempControlFrame, text = "Undefined")
        self.setptdisp.grid(column = 1, row = 0)
        Label(manualTempControlFrame, text = "Current Temperature (C): ").grid(column = 0, row = 1, sticky = W)
        self.currTemp = Label(manualTempControlFrame, text = "Unknown")
        self.currTemp.grid(column = 1, row = 1)


        self.tempHistory = [] # array to store past temperature measurements for plotting/saving

        #set setPoint inteface
        Button(manualTempControlFrame, text = "New Set Point (C): ", command = self.set_setpt_btn). grid(column = 0, row = 2, sticky = W)
        self.newSetpt = Entry(manualTempControlFrame)
        self.newSetpt.grid(column = 1, row = 2, sticky = W)

        self.powerrunbox = LabelFrame(self.mainframe)
        self.powerrunbox.grid(row = 1, column = 1)

        #Turn output on/off
        self.output = False
        self.powerButton = Button(self.powerrunbox, text = "Turn On", command = self.toggleOutput)
        self.powerButton.grid(column = 0, row = 0, sticky = W)

        # Draw Protocol Box
        self.ProtocolBox(3,0, TempStep)

        # If this box is checked, will plot recent temperatures in a separate window
        self.logTempBtn = Button(self.powerrunbox, text = "Display Temperature Plot", command = self.livePlot)
        self.logTempBtn.grid(column = 0, row = 2, sticky = W)
        self.liveplotting = False
        self.firstlog = True
        self.logLock = Lock()
        plt.ion() #allow interactive plotting
        self.templog = []
        self.setptLog = []
        self.times = []
        self.setpt = "Undefined"
        self.logTime = 0


        #save logged data
        self.saveButton = Button(self.powerrunbox, text = "Save Temperature Logs", command = self.save)
        self.saveButton.grid(column = 0, row = 3, sticky = W)

    def connect(self, port):
        try:
            usbGUI.connect(self, port)
        except Exception as E:
            tkMessageBox.showerror("Error", E.message)
            return
        TempStep.setPoint = self.set_setpt
        TempStep.getTemp = self.device.getTemp
        print("Connected")
        self.connected = True



    #called every second to update temperature display
    def updateTemp(self):
        if self.connected:
            self.logTime += 1
            try:
                temp = self.device.getTemp()
            except:
                tkMessageBox.showerror("IOError", "IOError: could not communicate with the temperature controller. Please try reconnecting.")
                self.connected = False
                return
            if int(temp) < -200: # If not connected to the thermistor\
                no_wait_Dialog(self.master, "Error", "The connection to the thermistor is bad. Please adjust the connection.")
                self.currTemp.config(text="?")
            else:
                self.logLock.acquire()
                self.templog.append(temp)
                self.times.append(time.clock())
                if self.setpt != "Undefined":
                    self.setptLog.append(float(self.device.setpt))
                self.logLock.release()
                self.currTemp.config(text= temp)
            time.sleep(1)


    def livePlot(self):
        if not self.connected:
            tkMessageBox.showerror("Error", "Error: Not connected to Temperature Controller")
            return
        try:
            if not self.liveplotting:
                self.logTempBtn.config(bg = "green")
                self.liveplotting = True
                self.plotThread = Thread(target=self.plotTempRun)
                self.plotThread.daemon = True
                self.plotThread.start()
            else:
                self.logTempBtn.config(bg = "gray")
                self.liveplotting = False
                plt.close()
        except E:
            tkMessageBox.showerror("Error",E.message)

    def save(self):
        file = tkFileDialog.asksaveasfile(mode='w', title="Save Procedure", defaultextension='.csv')
        try:
            writer = csv.writer(file, delimiter = ',')
            setpt = ["Ndef"]* len(self.templog)
            setpt[-len(self.setptLog):] = self.setptLog
            writer.writerow(["Time(s)","Temperature(C)", "SetPoint(C)"])
            for i in range(len(self.templog)):
                writer.writerow([self.times[i],self.templog[i], setpt[i]])
        except E:
            tkMessageBox.showerror("Error",E.message)
        finally:
            file.close()

    def plotTemp(self):

        plt.clf()
        self.logLock.acquire()
        timescopy = list(self.times)
        setptcopy = list(self.setptLog)
        templogcopy = list(self.templog)
        self.logLock.release()
        plt.plot(timescopy, templogcopy, color = 'k')
        plt.xlabel("Time (s)")
        plt.ylabel("Temperature (C)")
        if len(setptcopy) != len(templogcopy) and len(setptcopy) != 0:
            try:
                plt.plot(timescopy[-len(setptcopy):],setptcopy, color = 'r')
            except E:
                print(E.message)
                pass
        elif(len(setptcopy) == len(templogcopy)):
            plt.plot(timescopy, setptcopy,  color = 'r')
        plt.pause(1)

    def plotTempRun(self):
        while self.liveplotting == True:
            self.plotTemp()
        plt.close()


    #called when the New setPoint     button is pressed, sends entered value to controller
    def set_setpt_btn(self):
        if not self.connected:
            tkMessageBox.showerror("Error","Error: Not connected to temperature controller.")
            return
        if Protocol.running or config.stopEditing:
            no_wait_Dialog(self.master,"Error", "You cannot manually set the set point while a protocol is running.")
            return
        setpoint = self.newSetpt.get()
        self.set_setpt(setpoint)
        self.setpt = setpoint

    # set_setpoint can be called by step objects and the set_setpt_btn method
    def set_setpt(self, setpoint):
        if not self.connected:
            tkMessageBox.showerror("Error","Error: Not connected to temperature controller.")
            return
        self.setptdisp.config(text = setpoint)


        self.device.setPoint(int(setpoint))#Turn On/Turn Off button pressed

    def toggleOutput(self):
        self.output = not self.output
        if not self.connected:
            tkMessageBox.showerror("Error","Error: Not connected to temperature controller.")
            return
        try:
            if self.output:
                self.device.setPowerOn()
                self.powerButton.config(text = "Turn Off", bg = 'green')
            else:
                self.device.setPowerOff()
                self.powerButton.config(text = "Turn On", bg = 'gray')
        except E:
            tkMessageBox.showerror("Error",E.message)



class updater(Thread):
    def __init__(self, time, call):
        self.time = time
        self.call = call
        Thread.__init__(self)
        self.setDaemon(True)

    def run(self):
        while True:
            self.call()



root = Tk()

app = tempGUI(root)

#updtr is a thread that updates the current temperature display every second by calling the updateTemp method
updtr = updater(1, app.updateTemp)
updtr.start()

root.mainloop()