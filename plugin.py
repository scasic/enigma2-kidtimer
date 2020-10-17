from Plugins.Plugin import PluginDescriptor
from Components.config import config, ConfigInteger, ConfigSubsection, configfile
from Components.Label import Label
from Screens.Screen import Screen
import NavigationInstance
from enigma import eTimer
import time, datetime
from Screens.InputBox import PinInput

TIMELIMIT=5400
CHANNELS=["1:0:1:2777:444:1:C00000:0:0:0:", "1:0:16:328:8:70:168AFFB:0:0:0:", "1:0:16:71B:12:70:1680000:0:0:0:", "1:0:16:336:8:70:168AFFB:0:0:0:", "1:0:19:6594:9:70:1680000:0:0:0:", "1:0:16:71B:12:70:1680000:0:0:0:", "1:0:16:2C4:7:70:1680000:0:0:0:","1:0:16:32E:8:70:168AFFB:0:0:0:", "1:0:16:2C5:7:70:1680000:0:0:0:","1:0:19:371A:E:70:1680000:0:0:0:","1:0:16:2BF:7:70:1680000:0:0:0:","1:0:16:520:D:70:1680000:0:0:0:","1:0:16:193:4:70:1680000:0:0:0:","1:0:16:7A:1:70:1680000:0:0:0:","1:0:16:4AB0:13:70:1680000:0:0:0:","1:0:16:197:4:70:1680000:0:0:0:","1:0:16:1A4:4:70:1680000:0:0:0:","1:0:16:1AC:4:70:1680000:0:0:0:"]
config.plugins.KidTimer = ConfigSubsection()
config.plugins.KidTimer.remainingTime = ConfigInteger(default=TIMELIMIT)
config.plugins.KidTimer.day = ConfigInteger(default=20200101)

class KidTimerScreen(Screen):
    skin =  """
            <screen flags="wfNoBorder" position="10,10" size="82,104" title="Kiddy Timer" backgroundColor="#ff000000">
                <widget name="TimerText" zPosition="3" position="0,30" size="82,21" font="Regular;18" halign="center" valign="center" foregroundColor="#FF0000" transparent = "0" />
            </screen>
            """

    def __init__(self, session):
        Screen.__init__(self, session)
        self["TimerText"] = Label(_("0"))
        
    def renderScreen(self,seconds):
        self["TimerText"].setText(str(datetime.timedelta(seconds=seconds)))
        self["TimerText"].show()


class KidTimer():
    def __init__(self):
        self.session = None 
        self.dialog = None
        self.channel = None
        self.channels = CHANNELS
        self.loopTimer=eTimer()
        self.loopTimer.callback.append(self.checkChannel)
        self.remainingTime = config.plugins.KidTimer.remainingTime.getValue()
        self.day = config.plugins.KidTimer.day.getValue()

    def gotSession(self, session):
        self.session = session
        self.dialog = self.session.instantiateDialog(KidTimerScreen)
        self.loopTimer.start(5000,1)

    def askForPIN(self):
        print "oooooo1: ", self.channel
        self.session.openWithCallback( self.pinEntered, PinInput, pinList = [1212,2121], triesEntry = config.ParentalControl.retries.setuppin, title = _("Please enter the correct pin code"), windowTitle = _("Enter pin code"))

    def pinEntered(self, result):
        if not result:
            pass
        else:
            self.remainingTime=TIMELIMIT
            print "oooooo2: ", self.channel
            NavigationInstance.instance.playService(self.channel)
    

    def checkChannel(self):
        print "rem4: ", self.remainingTime
        timestamp=int(time.strftime("%Y%d%m" , time.localtime()))
        if self.day != timestamp:
            self.day = config.plugins.KidTimer.day.value = timestamp
            config.plugins.KidTimer.day.save()
            self.remainingTime=TIMELIMIT
            print "rem5: ", self.remainingTime

        currentChannel = NavigationInstance.instance.getCurrentlyPlayingServiceReference()

        print "loop channel:", self.channel
        print "conf: ", config.plugins.KidTimer.remainingTime.getValue()

        if currentChannel is not None and currentChannel.toString() in self.channels:
            self.channel = currentChannel
            if self.remainingTime <= 0:
                NavigationInstance.instance.stopService()
                self.askForPIN()
                print "rem1: ", self.remainingTime
            else:
                self.remainingTime-=5
                config.plugins.KidTimer.remainingTime.value = self.remainingTime
                config.plugins.KidTimer.remainingTime.save()
                configfile.save()
                print "rem2: ", self.remainingTime
            self.dialog.show()
            self.dialog.renderScreen(self.remainingTime)
            print "rem3: ", self.remainingTime
        else:
            self.dialog.hide()

        self.loopTimer.start(5000, 1)

        

kidTimer = KidTimer()       

def sessionstart(reason, **kwargs):
    if reason == 0:
        kidTimer.gotSession(kwargs["session"])

def autostart(reason, **kwargs):
    print "\n<<<<<<<<<< KIDTIMER AUTOSTART >>>>>>>>>>\n"
    if reason == 1:
        kidTimer = None

def setup(session, **kwargs):
    kidTimer = KidTimer()
    kidTimer.gotSession(session)


def Plugins(path,**kwargs):
    return [
            PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=sessionstart),
            PluginDescriptor(where=PluginDescriptor.WHERE_AUTOSTART, fnc=autostart),
            PluginDescriptor(name=_("KidTimer"), description=_("Allows to controls your kids' daily TV usage"), where = PluginDescriptor.WHERE_PLUGINMENU, fnc=setup)]
