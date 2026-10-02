from __future__ import absolute_import
from enigma import getDesktop  # type: ignore
from Components.config import ConfigSubsection, config, ConfigSelection
from Plugins.Plugin import PluginDescriptor
# for localized messages
from . import _

VERSION = "2.0.0"


config.plugins.CacheFlush = ConfigSubsection()
config.plugins.CacheFlush.where = ConfigSelection(default="0", choices=[("0", _(
    "plugins")), ("1", _("menu-system")), ("2", _("extensions")), ("3", _("event info"))])


def startSetup(menuid, **kwargs):
    if menuid != "system":
        return []
    return [(_("Setup CacheFlush"), main, "CacheFlush", None)]


def sessionAutostart(reason, **kwargs):
    if reason == 0:
        from . import ui
        ui.CacheFlushAuto.startCacheFlush(kwargs["session"])


def main(session, **kwargs):
    from . import ui
    session.open(ui.CacheFlushSetupMenu)


def Plugins(path, **kwargs):
    name = "CacheFlush"
    descr = _("Automatic cache flushing")

    # Detect Resolution for dynamic icon loading
    desk_width = getDesktop(0).size().width()
    if desk_width >= 3840:
        icon_file = "img/icon_4k.png"
    elif desk_width >= 2560:
        icon_file = "img/icon_2k.png"
    elif desk_width >= 1920:
        icon_file = "img/icon_fhd.png"
    else:
        icon_file = "img/icon_hd.png"

    list = [PluginDescriptor(
        where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionAutostart),]

    if config.plugins.CacheFlush.where.value == "0":
        list.append(PluginDescriptor(name=name, description=descr,
                    where=PluginDescriptor.WHERE_PLUGINMENU, needsRestart=True, icon=icon_file, fnc=main))
    elif config.plugins.CacheFlush.where.value == "1":
        list.append(PluginDescriptor(name=name, description=descr,
                    where=PluginDescriptor.WHERE_MENU, needsRestart=True, fnc=startSetup))
    elif config.plugins.CacheFlush.where.value == "2":
        list.append(PluginDescriptor(name=name, description=descr,
                    where=PluginDescriptor.WHERE_EXTENSIONSMENU, needsRestart=True, fnc=main))
    elif config.plugins.CacheFlush.where.value == "3":
        list.append(PluginDescriptor(name=name, description=descr,
                    where=PluginDescriptor.WHERE_EVENTINFO, needsRestart=True, fnc=main))

    return list
