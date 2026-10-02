# -*- coding: utf-8 -*-
from __future__ import print_function
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from os import environ as os_environ
import gettext


def localeInit():
    # getLanguage returns e.g. "fi_FI" for "language_country"
    lang = language.getLanguage()[:2]
    # Enigma doesn't set this (or LC_ALL, LC_MESSAGES, LANG). gettext needs it!
    os_environ["LANGUAGE"] = lang
    gettext.bindtextdomain("CacheFlush", resolveFilename(
        SCOPE_PLUGINS, "Extensions/CacheFlush/locale"))


def _(txt):
    t = gettext.dgettext("CacheFlush", txt)
    if t == txt:
        print("[CacheFlush] fallback to default translation for", txt)
        t = gettext.gettext(txt)
    return t


localeInit()
language.addCallback(localeInit)
