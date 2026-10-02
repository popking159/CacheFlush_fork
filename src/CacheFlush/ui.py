# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from . import _
import gettext

# Flake8 ngettext fix and local binding for translations
try:
    def ngettext(singular, plural, n):
        return gettext.dngettext("CacheFlush", singular, plural, n)
except Exception:
    pass

from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.config import ConfigYesNo, ConfigSelection, ConfigInteger, config, getConfigListEntry
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ProgressBar import ProgressBar
from enigma import eTimer, getDesktop  # pyright: ignore[reportMissingImports]
from os import system

from .plugin import VERSION

# ---------------------------------------------------------------------------
# Resolution Detection: SD (<1280), HD (1280), FHD (1920), 2K/WQHD (2560), 4K/UHD (3840)
# ---------------------------------------------------------------------------
desk_width = getDesktop(0).size().width()
IS_4K = desk_width >= 3840
IS_2K = 2560 <= desk_width < 3840
IS_FHD = 1920 <= desk_width < 2560
IS_HD = 1280 <= desk_width < 1920

config.plugins.CacheFlush.enable = ConfigYesNo(default=False)
config.plugins.CacheFlush.type = ConfigSelection(
    default="3",
    choices=[
        ("1", _("pagecache")),
        ("2", _("dentries and inodes")),
        ("3", _("pagecache, dentries and inodes")),
    ]
)
config.plugins.CacheFlush.sync = ConfigYesNo(default=False)

NGETTEXT = False
try:
    ngettext("%d minute", "%d minutes", 5)
    NGETTEXT = True
except Exception as e:
    print("[CacheFlush] ngettext is not supported:", e)

timeout_choices = []
for i in range(5, 151, 5):
    if NGETTEXT:
        timeout_choices.append(
            ("%d" % i, ngettext("%d minute", "%d minutes", i) % i))
    else:
        timeout_choices.append(("%d" % i, "%d min" % i))
config.plugins.CacheFlush.timeout = ConfigSelection(
    default="30", choices=timeout_choices)

config.plugins.CacheFlush.scrinfo = ConfigYesNo(default=True)

timescrinfo_choices = []
for i in range(1, 11):
    if NGETTEXT:
        timescrinfo_choices.append(
            ("%d" % i, ngettext("%d second", "%d seconds", i) % i))
    else:
        timescrinfo_choices.append(("%d" % i, "%d sec" % i))
config.plugins.CacheFlush.timescrinfo = ConfigSelection(
    default="10", choices=timescrinfo_choices)

uncached_choices = [("0", _("Default"))]
for i in range(1, 21):
    uncached_choices.append(("%d" % i, "%d kB" % (1024 * i)))
config.plugins.CacheFlush.uncached = ConfigSelection(
    default="1", choices=uncached_choices)
config.plugins.CacheFlush.free_default = ConfigInteger(
    default=0, limits=(0, 9999999999))
cfg = config.plugins.CacheFlush

ALL = 0x17


def dropCache():
    if cfg.sync.value:
        system("sync")
        print("[CacheFlush] sync")
    if cfg.type.value in ("1", "2", "3"):
        system("echo %s > /proc/sys/vm/drop_caches" % cfg.type.value)
        print("[CacheFlush] drop_caches type %s" % cfg.type.value)


def getMinFreeKbytes():
    line = "0"
    try:
        with open("/proc/sys/vm/min_free_kbytes", "r") as f:
            line = f.read().strip()
    except Exception as e:
        print("[CacheFlush] read min_free_kbytes failed:", e)
    return line


def setMinFreeKbytes(size):
    try:
        with open("/proc/sys/vm/min_free_kbytes", "w") as f:
            f.write("%d\n" % size)
        print("[CacheFlush] set min_free_kbytes to %d kB" % size)
    except Exception as e:
        system("echo %d > /proc/sys/vm/min_free_kbytes" % size)
        print("[CacheFlush] fallback setting min_free_kbytes via system():", e)


class CacheFlushSetupMenu(Screen, ConfigListScreen):
    if IS_4K:
        skin = """
        <screen name="CacheFlushSetupMenu" position="center,center" size="2000,1240" title="Setup CacheFlush" backgroundColor="#1a000000" flags="wfNoBorder">
            <widget name="title_version" position="40,20" size="1920,80" font="Regular;64" foregroundColor="#00a0e6" backgroundColor="#1a000000" transparent="1" halign="center" />
            <widget name="config" position="40,110" size="1920,710" zPosition="1" transparent="0" backgroundColor="#1a000000" backgroundColorSelected="#7f847d" foregroundColorSelected="#ffffff" scrollbarMode="showOnDemand" font="Regular;40" itemHeight="60" />
            <eLabel position="0,850" zPosition="2" size="2000,4" backgroundColor="#555555" />
            <widget name="min_free_kb" font="Regular;36" position="40,870" size="1920,64" zPosition="2" valign="center" backgroundColor="#1a000000" transparent="1" foregroundColor="#aaaaaa" />
            <widget name="memory" font="Regular;40" position="40,940" zPosition="2" size="1920,68" valign="center" halign="left" transparent="1" foregroundColor="#ffffff" />
            <widget name="slide_g" position="40,1020" zPosition="2" borderWidth="3" size="1920,24" backgroundColor="#202020" foregroundColor="#00ff00" pixmap="None" />
            <widget name="slide_y" position="40,1020" zPosition="2" borderWidth="3" size="1920,24" backgroundColor="#202020" foregroundColor="#ffff00" pixmap="None" />
            <widget name="slide_r" position="40,1020" zPosition="2" borderWidth="3" size="1920,24" backgroundColor="#202020" foregroundColor="#ff0000" pixmap="None" />
            <eLabel position="0,1080" zPosition="2" size="2000,4" backgroundColor="#555555" />

            <eLabel position="40,1135" zPosition="2" size="40,40" backgroundColor="red" />
            <widget name="key_red" position="90,1110" zPosition="2" size="410,90" valign="center" halign="left" font="Regular;40" transparent="1" foregroundColor="white" />

            <eLabel position="530,1135" zPosition="2" size="40,40" backgroundColor="green" />
            <widget name="key_green" position="580,1110" zPosition="2" size="410,90" valign="center" halign="left" font="Regular;40" transparent="1" foregroundColor="white" />

            <eLabel position="1020,1135" zPosition="2" size="40,40" backgroundColor="yellow" />
            <widget name="key_yellow" position="1070,1110" zPosition="2" size="410,90" valign="center" halign="left" font="Regular;40" transparent="1" foregroundColor="white" />

            <eLabel position="1510,1135" zPosition="2" size="40,40" backgroundColor="blue" />
            <widget name="key_blue" position="1560,1110" zPosition="2" size="410,90" valign="center" halign="left" font="Regular;40" transparent="1" foregroundColor="white" />
        </screen>"""
    elif IS_2K:
        skin = """
        <screen name="CacheFlushSetupMenu" position="center,center" size="1360,840" title="Setup CacheFlush" backgroundColor="#1a000000" flags="wfNoBorder">
            <widget name="title_version" position="30,15" size="1300,50" font="Regular;42" foregroundColor="#00a0e6" backgroundColor="#1a000000" transparent="1" halign="center" />
            <widget name="config" position="30,75" size="1300,470" zPosition="1" transparent="0" backgroundColor="#1a000000" backgroundColorSelected="#7f847d" foregroundColorSelected="#ffffff" scrollbarMode="showOnDemand" font="Regular;32" itemHeight="50" />
            <eLabel position="0,560" zPosition="2" size="1360,3" backgroundColor="#555555" />
            <widget name="min_free_kb" font="Regular;28" position="30,575" size="1300,45" zPosition="2" valign="center" backgroundColor="#1a000000" transparent="1" foregroundColor="#aaaaaa" />
            <widget name="memory" font="Regular;32" position="30,625" zPosition="2" size="1300,45" valign="center" halign="left" transparent="1" foregroundColor="#ffffff" />
            <widget name="slide_g" position="30,680" zPosition="2" borderWidth="2" size="1300,16" backgroundColor="#202020" foregroundColor="#00ff00" pixmap="None" />
            <widget name="slide_y" position="30,680" zPosition="2" borderWidth="2" size="1300,16" backgroundColor="#202020" foregroundColor="#ffff00" pixmap="None" />
            <widget name="slide_r" position="30,680" zPosition="2" borderWidth="2" size="1300,16" backgroundColor="#202020" foregroundColor="#ff0000" pixmap="None" />
            <eLabel position="0,730" zPosition="2" size="1360,3" backgroundColor="#555555" />

            <eLabel position="30,765" zPosition="2" size="25,25" backgroundColor="red" />
            <widget name="key_red" position="65,750" zPosition="2" size="275,60" valign="center" halign="left" font="Regular;32" transparent="1" foregroundColor="white" />

            <eLabel position="360,765" zPosition="2" size="25,25" backgroundColor="green" />
            <widget name="key_green" position="395,750" zPosition="2" size="275,60" valign="center" halign="left" font="Regular;32" transparent="1" foregroundColor="white" />

            <eLabel position="690,765" zPosition="2" size="25,25" backgroundColor="yellow" />
            <widget name="key_yellow" position="725,750" zPosition="2" size="275,60" valign="center" halign="left" font="Regular;32" transparent="1" foregroundColor="white" />

            <eLabel position="1020,765" zPosition="2" size="25,25" backgroundColor="blue" />
            <widget name="key_blue" position="1055,750" zPosition="2" size="275,60" valign="center" halign="left" font="Regular;32" transparent="1" foregroundColor="white" />
        </screen>"""
    elif IS_FHD:
        skin = """
        <screen name="CacheFlushSetupMenu" position="center,center" size="1000,620" title="Setup CacheFlush" backgroundColor="#1a000000" flags="wfNoBorder">
            <widget name="title_version" position="20,10" size="960,40" font="Regular;32" foregroundColor="#00a0e6" backgroundColor="#1a000000" transparent="1" halign="center" />
            <widget name="config" position="20,60" size="960,350" zPosition="1" transparent="0" backgroundColor="#1a000000" backgroundColorSelected="#7f847d" foregroundColorSelected="#ffffff" scrollbarMode="showOnDemand" font="Regular;25" itemHeight="40" />
            <eLabel position="0,425" zPosition="2" size="1000,2" backgroundColor="#555555" />
            <widget name="min_free_kb" font="Regular;22" position="20,435" size="960,32" zPosition="2" valign="center" backgroundColor="#1a000000" transparent="1" foregroundColor="#aaaaaa" />
            <widget name="memory" font="Regular;24" position="20,470" zPosition="2" size="960,34" valign="center" halign="left" transparent="1" foregroundColor="#ffffff" />
            <widget name="slide_g" position="20,510" zPosition="2" borderWidth="2" size="960,12" backgroundColor="#202020" foregroundColor="#00ff00" pixmap="None" />
            <widget name="slide_y" position="20,510" zPosition="2" borderWidth="2" size="960,12" backgroundColor="#202020" foregroundColor="#ffff00" pixmap="None" />
            <widget name="slide_r" position="20,510" zPosition="2" borderWidth="2" size="960,12" backgroundColor="#202020" foregroundColor="#ff0000" pixmap="None" />
            <eLabel position="0,540" zPosition="2" size="1000,2" backgroundColor="#555555" />

            <eLabel position="20,568" zPosition="2" size="20,20" backgroundColor="red" />
            <widget name="key_red" position="50,555" zPosition="2" size="190,45" valign="center" halign="left" font="Regular;24" transparent="1" foregroundColor="white" />

            <eLabel position="265,568" zPosition="2" size="20,20" backgroundColor="green" />
            <widget name="key_green" position="295,555" zPosition="2" size="190,45" valign="center" halign="left" font="Regular;24" transparent="1" foregroundColor="white" />

            <eLabel position="510,568" zPosition="2" size="20,20" backgroundColor="yellow" />
            <widget name="key_yellow" position="540,555" zPosition="2" size="190,45" valign="center" halign="left" font="Regular;24" transparent="1" foregroundColor="white" />

            <eLabel position="755,568" zPosition="2" size="20,20" backgroundColor="blue" />
            <widget name="key_blue" position="785,555" zPosition="2" size="190,45" valign="center" halign="left" font="Regular;24" transparent="1" foregroundColor="white" />
        </screen>"""
    elif IS_HD:
        skin = """
        <screen name="CacheFlushSetupMenu" position="center,center" size="700,440" title="Setup CacheFlush" backgroundColor="#31000000" flags="wfNoBorder">
            <widget name="title_version" position="15,10" size="670,30" font="Regular;24" foregroundColor="#00a0e6" backgroundColor="#31000000" transparent="1" halign="center" />
            <widget name="config" position="15,45" size="670,240" zPosition="1" transparent="0" backgroundColor="#31000000" backgroundColorSelected="#7f847d" foregroundColorSelected="#ffffff" scrollbarMode="showOnDemand" font="Regular;20" itemHeight="30" />
            <eLabel position="0,295" zPosition="2" size="700,2" backgroundColor="#555555" />
            <widget name="min_free_kb" font="Regular;17" position="15,302" size="670,25" zPosition="2" valign="center" backgroundColor="#31000000" transparent="1" foregroundColor="#bbbbbb" />
            <widget name="memory" font="Regular;19" position="15,330" zPosition="2" size="670,26" valign="center" halign="left" transparent="1" foregroundColor="#ffffff" />
            <widget name="slide_g" position="15,360" zPosition="2" borderWidth="1" size="670,10" backgroundColor="#202020" foregroundColor="#00ff00" pixmap="None" />
            <widget name="slide_y" position="15,360" zPosition="2" borderWidth="1" size="670,10" backgroundColor="#202020" foregroundColor="#ffff00" pixmap="None" />
            <widget name="slide_r" position="15,360" zPosition="2" borderWidth="1" size="670,10" backgroundColor="#202020" foregroundColor="#ff0000" pixmap="None" />
            <eLabel position="0,380" zPosition="2" size="700,2" backgroundColor="#555555" />

            <eLabel position="15,398" zPosition="2" size="15,15" backgroundColor="red" />
            <widget name="key_red" position="35,390" zPosition="2" size="140,36" valign="center" halign="left" font="Regular;20" transparent="1" foregroundColor="white" />

            <eLabel position="185,398" zPosition="2" size="15,15" backgroundColor="green" />
            <widget name="key_green" position="205,390" zPosition="2" size="140,36" valign="center" halign="left" font="Regular;20" transparent="1" foregroundColor="white" />

            <eLabel position="355,398" zPosition="2" size="15,15" backgroundColor="yellow" />
            <widget name="key_yellow" position="375,390" zPosition="2" size="140,36" valign="center" halign="left" font="Regular;20" transparent="1" foregroundColor="white" />

            <eLabel position="525,398" zPosition="2" size="15,15" backgroundColor="blue" />
            <widget name="key_blue" position="545,390" zPosition="2" size="140,36" valign="center" halign="left" font="Regular;20" transparent="1" foregroundColor="white" />
        </screen>"""
    else:  # SD
        skin = """
        <screen name="CacheFlushSetupMenu" position="center,center" size="520,330" title="Setup CacheFlush" backgroundColor="#31000000" flags="wfNoBorder">
            <widget name="title_version" position="10,5" size="500,25" font="Regular;19" foregroundColor="#00a0e6" backgroundColor="#31000000" transparent="1" halign="center" />
            <widget name="config" position="10,35" size="500,175" zPosition="1" transparent="0" backgroundColor="#31000000" backgroundColorSelected="#7f847d" foregroundColorSelected="#ffffff" scrollbarMode="showOnDemand" font="Regular;16" />
            <eLabel position="0,218" zPosition="2" size="520,2" backgroundColor="#555555" />
            <widget name="min_free_kb" font="Regular;14" position="10,222" size="500,22" zPosition="2" valign="center" backgroundColor="#31000000" transparent="1" />
            <widget name="memory" font="Regular;16" position="10,246" zPosition="2" size="500,24" valign="center" halign="left" transparent="1" foregroundColor="white" />
            <widget name="slide_g" position="10,274" zPosition="2" borderWidth="1" size="500,8" backgroundColor="#202020" foregroundColor="#00ff00" pixmap="None" />
            <widget name="slide_y" position="10,274" zPosition="2" borderWidth="1" size="500,8" backgroundColor="#202020" foregroundColor="#ffff00" pixmap="None" />
            <widget name="slide_r" position="10,274" zPosition="2" borderWidth="1" size="500,8" backgroundColor="#202020" foregroundColor="#ff0000" pixmap="None" />
            <eLabel position="0,288" zPosition="2" size="520,2" backgroundColor="#555555" />

            <eLabel position="10,300" zPosition="2" size="12,12" backgroundColor="red" />
            <widget name="key_red" position="27,292" zPosition="2" size="103,32" valign="center" halign="left" font="Regular;17" transparent="1" foregroundColor="white" />

            <eLabel position="137,300" zPosition="2" size="12,12" backgroundColor="green" />
            <widget name="key_green" position="154,292" zPosition="2" size="103,32" valign="center" halign="left" font="Regular;17" transparent="1" foregroundColor="white" />

            <eLabel position="265,300" zPosition="2" size="12,12" backgroundColor="yellow" />
            <widget name="key_yellow" position="282,292" zPosition="2" size="103,32" valign="center" halign="left" font="Regular;17" transparent="1" foregroundColor="white" />

            <eLabel position="393,300" zPosition="2" size="12,12" backgroundColor="blue" />
            <widget name="key_blue" position="410,292" zPosition="2" size="103,32" valign="center" halign="left" font="Regular;17" transparent="1" foregroundColor="white" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.onChangedEntry = []
        self.list = []
        ConfigListScreen.__init__(
            self, self.list, session=session, on_change=self.changedEntry)
        self["actions"] = ActionMap(
            ["SetupActions", "ColorActions"],
            {
                "cancel": self.keyCancel,
                "green": self.keySave,
                "ok": self.keySave,
                "red": self.keyCancel,
                "blue": self.freeMemory,
                "yellow": self.memoryInfo,
            },
            -2,
        )

        self["title_version"] = Label(_("Setup CacheFlush") + "  v" + VERSION)
        self["key_green"] = Label(_("Save"))
        self["key_red"] = Label(_("Cancel"))
        self["key_blue"] = Label(_("Clear Now"))
        self["key_yellow"] = Label(_("Info"))

        self["slide_g"] = ProgressBar()
        self["slide_y"] = ProgressBar()
        self["slide_r"] = ProgressBar()
        self["slide_g"].hide()
        self["slide_y"].hide()
        self["slide_r"].hide()
        self["memory"] = Label()
        self["min_free_kb"] = Label(
            _("Uncached memory: %s kB, (default: %s kB)") % (
                getMinFreeKbytes(), str(cfg.free_default.value))
        )

        self.runSetup()
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self["memory"].setText(self.getMemory(ALL))

    def runSetup(self):
        self.list = [getConfigListEntry(_("Enable CacheFlush"), cfg.enable)]
        if cfg.enable.value:
            autotext = _("Auto timeout")
            timetext = _("Time of info message")
            if not NGETTEXT:
                autotext = _("Auto timeout (5-150min)")
                timetext = _("Time of info message (1-10sec)")
            self.list.extend(
                (
                    getConfigListEntry(_("Cache drop type"), cfg.type),
                    getConfigListEntry(_('Clean "dirty" cache too'), cfg.sync),
                    getConfigListEntry(autotext, cfg.timeout),
                    getConfigListEntry(_("Show info on screen"), cfg.scrinfo),
                    getConfigListEntry(timetext, cfg.timescrinfo),
                    getConfigListEntry(_("Display plugin in"), cfg.where),
                )
            )
        self.list.extend(
            (getConfigListEntry(_("Uncached memory size"), cfg.uncached),))
        self["config"].list = self.list
        self["config"].setList(self.list)

    def keySave(self):
        for x in self["config"].list:
            x[1].save()
        self.setUncachedMemory()

        # Apply settings immediately and forcefully show the banner
        if CacheFlushAuto.dialog is not None:
            CacheFlushAuto.dialog.state = None
            CacheFlushAuto.dialog.chckState()

        self.close()

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close()

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        if self["config"].getCurrent() and self["config"].getCurrent()[1] == cfg.enable:
            self.runSetup()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        if self["config"].getCurrent() and self["config"].getCurrent()[1] == cfg.enable:
            self.runSetup()

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()

    def freeMemory(self):
        dropCache()
        self["memory"].setText(self.getMemory(ALL))

    def getMemory(self, par=0x01):
        try:
            mm = mu = mf = 0
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if "MemTotal:" in line:
                        mm = int(line.split()[1])
                    elif "MemFree:" in line:
                        mf = int(line.split()[1])
                        break
            if mm == 0:
                return ""
            mu = mm - mf
            self["memory"].setText("")
            self["slide_g"].hide()
            self["slide_y"].hide()
            self["slide_r"].hide()

            memory = ""
            if par & 0x01:
                memory += "".join((_("Memory:"), " %d " %
                                  (mm / 1024), _("MB"), "   "))
            if par & 0x02:
                memory += "".join((_("Used:"), " %.2f%%" %
                                  (100.0 * mu / mm), "   "))
            if par & 0x04:
                memory += "".join((_("Free:"), " %.2f%%" % (100.0 * mf / mm)))
            if par & 0x10:
                pct = int(100.0 * mu / mm + 0.25)
                # Color thresholds: < 75% Green, 75%-90% Yellow, > 90% Red
                if pct < 75:
                    self["slide_g"].setValue(pct)
                    self["slide_g"].show()
                elif pct < 90:
                    self["slide_y"].setValue(pct)
                    self["slide_y"].show()
                else:
                    self["slide_r"].setValue(pct)
                    self["slide_r"].show()
            return memory
        except Exception as e:
            print("[CacheFlush] getMemory FAIL:", e)
            return ""

    def memoryInfo(self):
        self.session.openWithCallback(self.afterInfo, CacheFlushInfoScreen)

    def afterInfo(self, answer=False):
        self["memory"].setText(self.getMemory(ALL))

    def setUncachedMemory(self):
        if cfg.uncached.value == "0":
            setMinFreeKbytes(cfg.free_default.value)
        else:
            setMinFreeKbytes(int(cfg.uncached.value) * 1024)


class CacheFlushAutoMain(object):
    def __init__(self):
        self.dialog = None
        if cfg.free_default.value == 0:
            cfg.free_default.value = int(getMinFreeKbytes())
            cfg.free_default.save()

    def startCacheFlush(self, session):
        self.dialog = session.instantiateDialog(CacheFlushAutoScreen)
        self.makeShow()

    def makeShow(self):
        if self.dialog is not None:
            if cfg.scrinfo.value:
                self.dialog.show()
            else:
                self.dialog.hide()


CacheFlushAuto = CacheFlushAutoMain()


class CacheFlushAutoScreen(Screen):
    if IS_4K:
        skin = """
        <screen name="CacheFlushAutoScreen" position="center,120" zPosition="10" size="1200,100" title="CacheFlush Status" backgroundColor="#31000000" flags="wfNoBorder">
            <widget name="message_label" font="Regular;45" position="0,0" zPosition="2" valign="center" halign="center" size="1200,100" backgroundColor="#31000000" transparent="1" foregroundColor="#ffffff" />
        </screen>"""
    elif IS_2K:
        skin = """
        <screen name="CacheFlushAutoScreen" position="center,80" zPosition="10" size="800,68" title="CacheFlush Status" backgroundColor="#31000000" flags="wfNoBorder">
            <widget name="message_label" font="Regular;34" position="0,0" zPosition="2" valign="center" halign="center" size="800,68" backgroundColor="#31000000" transparent="1" foregroundColor="#ffffff" />
        </screen>"""
    elif IS_FHD:
        skin = """
        <screen name="CacheFlushAutoScreen" position="center,60" zPosition="10" size="600,50" title="CacheFlush Status" backgroundColor="#31000000" flags="wfNoBorder">
            <widget name="message_label" font="Regular;26" position="0,0" zPosition="2" valign="center" halign="center" size="600,50" backgroundColor="#31000000" transparent="1" foregroundColor="#ffffff" />
        </screen>"""
    elif IS_HD:
        skin = """
        <screen name="CacheFlushAutoScreen" position="center,45" zPosition="10" size="450,36" title="CacheFlush Status" backgroundColor="#31000000" flags="wfNoBorder">
            <widget name="message_label" font="Regular;20" position="0,0" zPosition="2" valign="center" halign="center" size="450,36" backgroundColor="#31000000" transparent="1" foregroundColor="#ffffff" />
        </screen>"""
    else:  # SD
        skin = """
        <screen name="CacheFlushAutoScreen" position="center,40" zPosition="10" size="300,28" title="CacheFlush Status" backgroundColor="#31000000" flags="wfNoBorder">
            <widget name="message_label" font="Regular;16" position="0,0" zPosition="2" valign="center" halign="center" size="300,28" backgroundColor="#31000000" transparent="1" foregroundColor="#ffffff" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self["message_label"] = Label(_("CacheFlush: Starting..."))
        self.CacheFlushTimer = eTimer()
        self.CacheFlushTimer.timeout.get().append(self.makeWhatYouNeed)
        self.showTimer = eTimer()
        self.showTimer.timeout.get().append(self.endShow)
        self.state = None
        self.onLayoutFinish.append(self.chckState)
        self.onShow.append(self.startsuspend)
        self.setUncachedMemory()

    def getQuickMemInfo(self):
        # A lightweight, fast function just for the banner to grab free memory and percentage
        try:
            mm = mf = 0
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if "MemTotal:" in line:
                        mm = int(line.split()[1])
                    elif "MemFree:" in line:
                        mf = int(line.split()[1])
                        break
            if mm > 0:
                free_mb = mf // 1024
                free_pct = (100.0 * mf) / mm
                return "   ( Free: %d MB  /  %.1f%% )" % (free_mb, free_pct)
        except Exception:
            pass
        return ""

    def startsuspend(self):
        self.showTimer.start(int(cfg.timescrinfo.value) * 1000)

    def chckState(self):
        if self.instance and self.state is None:
            if cfg.enable.value:
                mem_info = self.getQuickMemInfo()
                self["message_label"].setText(
                    _("CacheFlush: Started") + mem_info)
            else:
                self["message_label"].setText(_("CacheFlush: Stopped"))

            self.state = cfg.enable.value
            if cfg.scrinfo.value and CacheFlushAuto.dialog is not None:
                CacheFlushAuto.dialog.show()

        self.CacheFlushTimer.start(int(cfg.timeout.value) * 60000)

    def makeWhatYouNeed(self):
        self.chckState()
        if cfg.enable.value:
            dropCache()
            if self.instance:
                mem_info = self.getQuickMemInfo()
                self["message_label"].setText(
                    _("CacheFlush: Mem cleared") + mem_info)
                if cfg.scrinfo.value and CacheFlushAuto.dialog is not None:
                    CacheFlushAuto.dialog.show()

    def endShow(self):
        if CacheFlushAuto.dialog is not None:
            CacheFlushAuto.dialog.hide()

    def setUncachedMemory(self):
        if cfg.uncached.value != "0":
            setMinFreeKbytes(int(cfg.uncached.value) * 1024)


class CacheFlushInfoScreen(Screen):
    if IS_4K:
        skin = """
        <screen name="CacheFlushInfoScreen" position="center,center" zPosition="2" size="2160,1760" title="CacheFlush Info" backgroundColor="#1a000000" flags="wfNoBorder">
            <widget name="title_version" position="40,20" size="2080,80" font="Regular;64" foregroundColor="#00a0e6" backgroundColor="#1a000000" transparent="1" halign="center" />

            <!-- Left Memory Column -->
            <widget name="lmemtext" font="Regular;32" position="40,110" size="500,1450" zPosition="2" valign="top" halign="left" transparent="1" foregroundColor="#ffffff" />
            <widget name="lmemvalue" font="Regular;32" position="550,110" size="360,1450" zPosition="2" valign="top" halign="right" transparent="1" foregroundColor="#20ebff" />

            <!-- Center Vertical Gauge -->
            <widget name="pfree" position="930,410" size="200,64" font="Regular;30" zPosition="3" halign="right" transparent="1" foregroundColor="green" />
            <widget name="slide_g" position="1150,110" size="52,1450" zPosition="3" borderWidth="3" orientation="orBottomToTop" backgroundColor="#202020" foregroundColor="#00ff00" pixmap="None" />
            <widget name="slide_y" position="1150,110" size="52,1450" zPosition="3" borderWidth="3" orientation="orBottomToTop" backgroundColor="#202020" foregroundColor="#ffff00" pixmap="None" />
            <widget name="slide_r" position="1150,110" size="52,1450" zPosition="3" borderWidth="3" orientation="orBottomToTop" backgroundColor="#202020" foregroundColor="#ff0000" pixmap="None" />
            <widget name="pused" position="930,1210" size="200,64" font="Regular;30" zPosition="3" halign="right" transparent="1" foregroundColor="red" />

            <!-- Right Memory Column -->
            <widget name="rmemtext" font="Regular;32" position="1230,110" size="520,1450" zPosition="2" valign="top" halign="left" transparent="1" foregroundColor="#ffffff" />
            <widget name="rmemvalue" font="Regular;32" position="1760,110" size="360,1450" zPosition="2" valign="top" halign="right" transparent="1" foregroundColor="#20ebff" />

            <eLabel position="0,1600" zPosition="2" size="2160,4" backgroundColor="#555555" />

            <eLabel position="90,1662" zPosition="2" size="40,40" backgroundColor="red" />
            <widget name="key_red" position="140,1636" zPosition="2" size="400,92" valign="center" halign="left" font="Regular;38" transparent="1" foregroundColor="white" />

            <eLabel position="870,1662" zPosition="2" size="40,40" backgroundColor="green" />
            <widget name="key_green" position="920,1636" zPosition="2" size="400,92" valign="center" halign="left" font="Regular;38" transparent="1" foregroundColor="white" />

            <eLabel position="1650,1662" zPosition="2" size="40,40" backgroundColor="blue" />
            <widget name="key_blue" position="1700,1636" zPosition="2" size="400,92" valign="center" halign="left" font="Regular;38" transparent="1" foregroundColor="white" />
        </screen>"""
    elif IS_2K:
        skin = """
        <screen name="CacheFlushInfoScreen" position="center,center" zPosition="2" size="1480,1180" title="CacheFlush Info" backgroundColor="#1a000000" flags="wfNoBorder">
            <widget name="title_version" position="25,15" size="1430,50" font="Regular;42" foregroundColor="#00a0e6" backgroundColor="#1a000000" transparent="1" halign="center" />

            <!-- Left Memory Column -->
            <widget name="lmemtext" font="Regular;26" position="25,75" size="340,970" zPosition="2" valign="top" halign="left" transparent="1" foregroundColor="#ffffff" />
            <widget name="lmemvalue" font="Regular;26" position="370,75" size="240,970" zPosition="2" valign="top" halign="right" transparent="1" foregroundColor="#20ebff" />

            <!-- Center Vertical Gauge -->
            <widget name="pfree" position="630,280" size="130,40" font="Regular;24" zPosition="3" halign="right" transparent="1" foregroundColor="green" />
            <widget name="slide_g" position="775,75" size="35,970" zPosition="3" borderWidth="2" orientation="orBottomToTop" backgroundColor="#202020" foregroundColor="#00ff00" pixmap="None" />
            <widget name="slide_y" position="775,75" size="35,970" zPosition="3" borderWidth="2" orientation="orBottomToTop" backgroundColor="#202020" foregroundColor="#ffff00" pixmap="None" />
            <widget name="slide_r" position="775,75" size="35,970" zPosition="3" borderWidth="2" orientation="orBottomToTop" backgroundColor="#202020" foregroundColor="#ff0000" pixmap="None" />
            <widget name="pused" position="630,830" size="130,40" font="Regular;24" zPosition="3" halign="right" transparent="1" foregroundColor="red" />

            <!-- Right Memory Column -->
            <widget name="rmemtext" font="Regular;26" position="830,75" size="360,970" zPosition="2" valign="top" halign="left" transparent="1" foregroundColor="#ffffff" />
            <widget name="rmemvalue" font="Regular;26" position="1200,75" size="250,970" zPosition="2" valign="top" halign="right" transparent="1" foregroundColor="#20ebff" />

            <eLabel position="0,1070" zPosition="2" size="1480,3" backgroundColor="#555555" />

            <eLabel position="60,1112" zPosition="2" size="25,25" backgroundColor="red" />
            <widget name="key_red" position="95,1095" zPosition="2" size="265,60" valign="center" halign="left" font="Regular;32" transparent="1" foregroundColor="white" />

            <eLabel position="600,1112" zPosition="2" size="25,25" backgroundColor="green" />
            <widget name="key_green" position="635,1095" zPosition="2" size="265,60" valign="center" halign="left" font="Regular;32" transparent="1" foregroundColor="white" />

            <eLabel position="1140,1112" zPosition="2" size="25,25" backgroundColor="blue" />
            <widget name="key_blue" position="1175,1095" zPosition="2" size="265,60" valign="center" halign="left" font="Regular;32" transparent="1" foregroundColor="white" />
        </screen>"""
    elif IS_FHD:
        skin = """
        <screen name="CacheFlushInfoScreen" position="center,center" zPosition="2" size="1080,880" title="CacheFlush Info" backgroundColor="#1a000000" flags="wfNoBorder">
            <widget name="title_version" position="20,10" size="1040,40" font="Regular;32" foregroundColor="#00a0e6" backgroundColor="#1a000000" transparent="1" halign="center" />

            <!-- Left Memory Column -->
            <widget name="lmemtext" font="Regular;20" position="20,60" size="250,720" zPosition="2" valign="top" halign="left" transparent="1" foregroundColor="#ffffff" />
            <widget name="lmemvalue" font="Regular;20" position="275,60" size="180,720" zPosition="2" valign="top" halign="right" transparent="1" foregroundColor="#20ebff" />

            <!-- Center Vertical Gauge -->
            <widget name="pfree" position="465,180" size="100,32" font="Regular;19" zPosition="3" halign="right" transparent="1" foregroundColor="green" />
            <widget name="slide_g" position="575,60" size="26,720" zPosition="3" borderWidth="2" orientation="orBottomToTop" backgroundColor="#202020" foregroundColor="#00ff00" pixmap="None" />
            <widget name="slide_y" position="575,60" size="26,720" zPosition="3" borderWidth="2" orientation="orBottomToTop" backgroundColor="#202020" foregroundColor="#ffff00" pixmap="None" />
            <widget name="slide_r" position="575,60" size="26,720" zPosition="3" borderWidth="2" orientation="orBottomToTop" backgroundColor="#202020" foregroundColor="#ff0000" pixmap="None" />
            <widget name="pused" position="465,580" size="100,32" font="Regular;19" zPosition="3" halign="right" transparent="1" foregroundColor="red" />

            <!-- Right Memory Column -->
            <widget name="rmemtext" font="Regular;20" position="615,60" size="260,720" zPosition="2" valign="top" halign="left" transparent="1" foregroundColor="#ffffff" />
            <widget name="rmemvalue" font="Regular;20" position="880,60" size="180,720" zPosition="2" valign="top" halign="right" transparent="1" foregroundColor="#20ebff" />

            <eLabel position="0,800" zPosition="2" size="1080,2" backgroundColor="#555555" />

            <eLabel position="50,830" zPosition="2" size="20,20" backgroundColor="red" />
            <widget name="key_red" position="80,818" zPosition="2" size="190,46" valign="center" halign="left" font="Regular;24" transparent="1" foregroundColor="white" />

            <eLabel position="440,830" zPosition="2" size="20,20" backgroundColor="green" />
            <widget name="key_green" position="470,818" zPosition="2" size="190,46" valign="center" halign="left" font="Regular;24" transparent="1" foregroundColor="white" />

            <eLabel position="830,830" zPosition="2" size="20,20" backgroundColor="blue" />
            <widget name="key_blue" position="860,818" zPosition="2" size="190,46" valign="center" halign="left" font="Regular;24" transparent="1" foregroundColor="white" />
        </screen>"""
    elif IS_HD:
        skin = """
        <screen name="CacheFlushInfoScreen" position="center,center" zPosition="2" size="740,620" title="CacheFlush Info" backgroundColor="#31000000" flags="wfNoBorder">
            <widget name="title_version" position="15,10" size="710,30" font="Regular;24" foregroundColor="#00a0e6" backgroundColor="#31000000" transparent="1" halign="center" />

            <!-- Left Memory Column -->
            <widget name="lmemtext" font="Regular;16" position="15,45" size="170,500" zPosition="2" valign="top" halign="left" transparent="1" foregroundColor="#ffffff" />
            <widget name="lmemvalue" font="Regular;16" position="190,45" size="120,500" zPosition="2" valign="top" halign="right" transparent="1" foregroundColor="#20ebff" />

            <!-- Center Vertical Gauge -->
            <widget name="pfree" position="315,160" size="80,24" font="Regular;15" zPosition="3" halign="right" transparent="1" foregroundColor="green" />
            <widget name="slide_g" position="400,45" size="20,500" zPosition="3" borderWidth="1" orientation="orBottomToTop" backgroundColor="#202020" foregroundColor="#00ff00" pixmap="None" />
            <widget name="slide_y" position="400,45" size="20,500" zPosition="3" borderWidth="1" orientation="orBottomToTop" backgroundColor="#202020" foregroundColor="#ffff00" pixmap="None" />
            <widget name="slide_r" position="400,45" size="20,500" zPosition="3" borderWidth="1" orientation="orBottomToTop" backgroundColor="#202020" foregroundColor="#ff0000" pixmap="None" />
            <widget name="pused" position="315,440" size="80,24" font="Regular;15" zPosition="3" halign="right" transparent="1" foregroundColor="red" />

            <!-- Right Memory Column -->
            <widget name="rmemtext" font="Regular;16" position="430,45" size="175,500" zPosition="2" valign="top" halign="left" transparent="1" foregroundColor="#ffffff" />
            <widget name="rmemvalue" font="Regular;16" position="610,45" size="115,500" zPosition="2" valign="top" halign="right" transparent="1" foregroundColor="#20ebff" />

            <eLabel position="0,560" zPosition="2" size="740,2" backgroundColor="#555555" />

            <eLabel position="30,582" zPosition="2" size="15,15" backgroundColor="red" />
            <widget name="key_red" position="50,572" zPosition="2" size="140,36" valign="center" halign="left" font="Regular;20" transparent="1" foregroundColor="white" />

            <eLabel position="295,582" zPosition="2" size="15,15" backgroundColor="green" />
            <widget name="key_green" position="315,572" zPosition="2" size="140,36" valign="center" halign="left" font="Regular;20" transparent="1" foregroundColor="white" />

            <eLabel position="560,582" zPosition="2" size="15,15" backgroundColor="blue" />
            <widget name="key_blue" position="580,572" zPosition="2" size="140,36" valign="center" halign="left" font="Regular;20" transparent="1" foregroundColor="white" />
        </screen>"""
    else:  # SD
        skin = """
        <screen name="CacheFlushInfoScreen" position="center,center" zPosition="2" size="560,490" title="CacheFlush Info" backgroundColor="#31000000" flags="wfNoBorder">
            <widget name="title_version" position="10,5" size="540,25" font="Regular;19" foregroundColor="#00a0e6" backgroundColor="#31000000" transparent="1" halign="center" />

            <widget name="lmemtext" font="Regular;14" position="10,35" size="130,385" zPosition="2" valign="top" halign="left" transparent="1" />
            <widget name="lmemvalue" font="Regular;14" position="145,35" size="90,385" zPosition="2" valign="top" halign="right" transparent="1" />

            <widget name="pfree" position="238,120" size="65,20" font="Regular;13" zPosition="3" halign="right" transparent="1" />
            <widget name="slide_g" position="305,35" size="16,385" zPosition="3" borderWidth="1" orientation="orBottomToTop" backgroundColor="#202020" foregroundColor="#00ff00" pixmap="None" />
            <widget name="slide_y" position="305,35" size="16,385" zPosition="3" borderWidth="1" orientation="orBottomToTop" backgroundColor="#202020" foregroundColor="#ffff00" pixmap="None" />
            <widget name="slide_r" position="305,35" size="16,385" zPosition="3" borderWidth="1" orientation="orBottomToTop" backgroundColor="#202020" foregroundColor="#ff0000" pixmap="None" />
            <widget name="pused" position="238,345" size="65,20" font="Regular;13" zPosition="3" halign="right" transparent="1" />

            <widget name="rmemtext" font="Regular;14" position="330,35" size="130,385" zPosition="2" valign="top" halign="left" transparent="1" />
            <widget name="rmemvalue" font="Regular;14" position="465,35" size="85,385" zPosition="2" valign="top" halign="right" transparent="1" />

            <eLabel position="0,432" zPosition="2" size="560,2" backgroundColor="#555555" />

            <eLabel position="15,450" zPosition="2" size="12,12" backgroundColor="red" />
            <widget name="key_red" position="32,442" zPosition="2" size="108,30" valign="center" halign="left" font="Regular;17" transparent="1" foregroundColor="white" />

            <eLabel position="220,450" zPosition="2" size="12,12" backgroundColor="green" />
            <widget name="key_green" position="237,442" zPosition="2" size="108,30" valign="center" halign="left" font="Regular;17" transparent="1" foregroundColor="white" />

            <eLabel position="425,450" zPosition="2" size="12,12" backgroundColor="blue" />
            <widget name="key_blue" position="442,442" zPosition="2" size="108,30" valign="center" halign="left" font="Regular;17" transparent="1" foregroundColor="white" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self["actions"] = ActionMap(
            ["SetupActions", "ColorActions"],
            {
                "cancel": self.cancel,
                "blue": self.freeMemory,
                "green": self.getMemInfo,
            },
            -2,
        )

        self["title_version"] = Label(_("CacheFlush Info") + "  v" + VERSION)
        self["key_red"] = Label(_("Cancel"))
        self["key_green"] = Label(_("Refresh"))
        self["key_blue"] = Label(_("Clear Now"))

        self["lmemtext"] = Label()
        self["lmemvalue"] = Label()
        self["rmemtext"] = Label()
        self["rmemvalue"] = Label()
        self["pfree"] = Label()
        self["pused"] = Label()

        self["slide_g"] = ProgressBar()
        self["slide_y"] = ProgressBar()
        self["slide_r"] = ProgressBar()
        self["slide_g"].hide()
        self["slide_y"].hide()
        self["slide_r"].hide()

        self.onLayoutFinish.append(self.getMemInfo)

    def getMemInfo(self):
        try:
            ltext = []
            rtext = []
            lvalue = []
            rvalue = []
            mem = 0
            free = 0
            i = 0

            with open("/proc/meminfo", "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        name = parts[0]
                        size = parts[1]
                        units = parts[2] if len(parts) > 2 else ""

                        if "MemTotal" in name:
                            mem = int(size)
                        elif "MemFree" in name:
                            free = int(size)

                        val_str = (size + " " + units).strip()
                        if i < 28:
                            ltext.append(name)
                            lvalue.append(val_str)
                        else:
                            rtext.append(name)
                            rvalue.append(val_str)
                        i += 1

            self["lmemtext"].setText("\n".join(ltext))
            self["lmemvalue"].setText("\n".join(lvalue))
            self["rmemtext"].setText("\n".join(rtext))
            self["rmemvalue"].setText("\n".join(rvalue))

            if mem > 0:
                used = mem - free
                pct = int(100.0 * used / mem + 0.25)

                # Update text labels
                self["pfree"].setText("%.1f%%" % (100.0 * free / mem))
                self["pused"].setText("%.1f%%" % (100.0 * used / mem))

                # Reset all visibility
                self["slide_g"].hide()
                self["slide_y"].hide()
                self["slide_r"].hide()

                # Show the correct color based on memory usage
                if pct < 75:
                    self["slide_g"].setValue(pct)
                    self["slide_g"].show()
                elif pct < 90:
                    self["slide_y"].setValue(pct)
                    self["slide_y"].show()
                else:
                    self["slide_r"].setValue(pct)
                    self["slide_r"].show()

        except Exception as e:
            print("[CacheFlush] getMemInfo FAIL:", e)

    def freeMemory(self):
        dropCache()
        self.getMemInfo()

    def cancel(self):
        self.close()
