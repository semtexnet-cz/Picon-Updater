from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Plugins.Plugin import PluginDescriptor
import os
import zipfile
import urllib.request

# Cesty a URL
PICON_DIR = "/usr/share/enigma2/picon/"
PLUGIN_DIR = "/usr/lib/enigma2/python/Plugins/Extensions/Piconupdater/"
LOCAL_PICON_VERSION_FILE = os.path.join(PLUGIN_DIR, "version.txt")
REMOTE_PICON_VERSION_URL = "https://raw.githubusercontent.com/semtexnet-cz/Picon-Updater/main/version.txt"
PICON_ZIP_URL = "https://raw.githubusercontent.com/semtexnet-cz/Picon-Updater/main/picon.zip"
TMP_PICON_ZIP = "/tmp/picon.zip"

LOCAL_PLUGIN_VERSION_FILE = os.path.join(PLUGIN_DIR, "plugin_version.txt")
REMOTE_PLUGIN_VERSION_URL = "https://raw.githubusercontent.com/semtexnet-cz/Picon-Updater/main/plugin_version.txt"
PLUGIN_ZIP_URL = "https://raw.githubusercontent.com/semtexnet-cz/Picon-Updater/main/plugin.zip"
TMP_PLUGIN_ZIP = "/tmp/plugin.zip"


class PiconUpdater(Screen):
    skin = """
    <screen name="PiconUpdater" position="center,center" size="600,450" title="Picon Updater">
        <widget name="status" position="20,20" size="560,50" font="Regular;22" halign="center" valign="center"/>
        <widget name="localver" position="20,100" size="560,40" font="Regular;20" halign="center"/>
        <widget name="remotever" position="20,150" size="560,40" font="Regular;20" halign="center"/>
        <widget name="localpluginver" position="20,200" size="560,40" font="Regular;20" halign="center"/>
        <widget name="remotepluginver" position="20,250" size="560,40" font="Regular;20" halign="center"/>
        <widget name="icon" position="268,300" size="64,64" pixmap="plugin.png" transparent="1" alphatest="blend"/>
        <widget name="help" position="20,360" size="560,40" font="Regular;18" halign="center"/>
        <!-- Action Buttons -->
        <widget name="key_green" position="20,400" size="135,50" font="Regular;18" halign="center" backgroundColor="#008000" foregroundColor="black"/>
        <widget name="key_yellow" position="160,400" size="135,50" font="Regular;18" halign="center" backgroundColor="#FFD700" foregroundColor="black"/>
        <widget name="key_blue" position="300,400" size="135,50" font="Regular;19" halign="center" backgroundColor="#3399FF" foregroundColor="black"/>
        <widget name="key_red" position="440,400" size="135,50" font="Regular;19" halign="center" backgroundColor="#CC0000" foregroundColor="black"/>
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session

        self["status"] = Label("Načítání verzí...")
        self["localver"] = Label("")
        self["remotever"] = Label("")
        self["localpluginver"] = Label("")
        self["remotepluginver"] = Label("")
        self["help"] = Label("Vyberte akci tlačítkem níže")
        self["icon"] = Pixmap()

        # Akční tlačítka
        self["key_green"] = Label("Aktualizovat picony")
        self["key_yellow"] = Label("Aktualizovat plugin")
        self["key_blue"] = Label("Aktualizovat vše")
        self["key_red"] = Label("Ukončit")

        self["actions"] = ActionMap(
            ["ColorActions", "OkCancelActions"],
            {
                "green": self.updatePicons,
                "yellow": self.updatePlugin,
                "blue": self.updateAll,
                "red": self.close,
                "ok": self.updatePicons,
                "cancel": self.close
            },
            -1
        )

        self.local_picon_version = "Neznámá"
        self.remote_picon_version = "Neznámá"
        self.local_plugin_version = "Neznámá"
        self.remote_plugin_version = "Neznámá"

        self.onLayoutFinish.append(self.loadVersions)

    def loadVersions(self):
        if os.path.exists(LOCAL_PICON_VERSION_FILE):
            with open(LOCAL_PICON_VERSION_FILE, "r") as f:
                self.local_picon_version = f.read().strip()
        else:
            self.local_picon_version = "Není nainstalováno"

        try:
            with urllib.request.urlopen(REMOTE_PICON_VERSION_URL) as response:
                self.remote_picon_version = response.read().decode("utf-8").strip()
        except Exception as e:
            self.remote_picon_version = f"Chyba: {e}"

        if os.path.exists(LOCAL_PLUGIN_VERSION_FILE):
            with open(LOCAL_PLUGIN_VERSION_FILE, "r") as f:
                self.local_plugin_version = f.read().strip()
        else:
            self.local_plugin_version = "1.0"

        try:
            with urllib.request.urlopen(REMOTE_PLUGIN_VERSION_URL) as response:
                self.remote_plugin_version = response.read().decode("utf-8").strip()
        except Exception as e:
            self.remote_plugin_version = f"Chyba: {e}"

        self.updateUI()

    def updateUI(self):
        self["status"].setText("Kontrola verzí dokončena.")
        self["localver"].setText(f"Picony - nainstalovaná verze: {self.local_picon_version}")
        self["remotever"].setText(f"Picony - dostupná verze: {self.remote_picon_version}")
        self["localpluginver"].setText(f"Plugin - nainstalovaná verze: {self.local_plugin_version}")
        self["remotepluginver"].setText(f"Plugin - dostupná verze: {self.remote_plugin_version}")

    def updatePicons(self, callback=None):
        if "Chyba" in self.remote_picon_version:
            self.session.open(MessageBox, "Nepodařilo se získat vzdálenou verzi picon!", MessageBox.TYPE_ERROR, timeout=5)
            return

        if self.local_picon_version == self.remote_picon_version:
            if callback:
                callback()
            else:
                self.session.open(MessageBox, "Picony jsou aktuální, není co aktualizovat.", MessageBox.TYPE_INFO, timeout=5)
            return

        try:
            urllib.request.urlretrieve(PICON_ZIP_URL, TMP_PICON_ZIP)
            with zipfile.ZipFile(TMP_PICON_ZIP, 'r') as zip_ref:
                zip_ref.extractall(PICON_DIR)
            os.remove(TMP_PICON_ZIP)
            with open(LOCAL_PICON_VERSION_FILE, "w") as f:
                f.write(self.remote_picon_version)
            self.local_picon_version = self.remote_picon_version

            if callback:
                callback()
            else:
                self.session.openWithCallback(self.restartEnigma, MessageBox,
                    "Picony byly úspěšně aktualizovány!\n\nEnigma2 bude nyní restartována.",
                    MessageBox.TYPE_INFO, timeout=5)
        except Exception as e:
            self.session.open(MessageBox, f"Chyba při aktualizaci picon: {e}", MessageBox.TYPE_ERROR, timeout=5)

    def updatePlugin(self, callback=None):
        if "Chyba" in self.remote_plugin_version:
            self.session.open(MessageBox, "Nepodařilo se získat vzdálenou verzi pluginu!", MessageBox.TYPE_ERROR, timeout=5)
            return

        if self.local_plugin_version == self.remote_plugin_version:
            if callback:
                callback()
            else:
                self.session.open(MessageBox, "Plugin je aktuální, není co aktualizovat.", MessageBox.TYPE_INFO, timeout=5)
            return

        try:
            urllib.request.urlretrieve(PLUGIN_ZIP_URL, TMP_PLUGIN_ZIP)
            with zipfile.ZipFile(TMP_PLUGIN_ZIP, 'r') as zip_ref:
                zip_ref.extractall(PLUGIN_DIR)
            os.remove(TMP_PLUGIN_ZIP)
            with open(LOCAL_PLUGIN_VERSION_FILE, "w") as f:
                f.write(self.remote_plugin_version)
            self.local_plugin_version = self.remote_plugin_version

            if callback:
                callback()
            else:
                self.session.openWithCallback(self.restartEnigma, MessageBox,
                    "Plugin byl úspěšně aktualizován!\n\nEnigma2 bude nyní restartována.",
                    MessageBox.TYPE_INFO, timeout=5)
        except Exception as e:
            self.session.open(MessageBox, f"Chyba při aktualizaci pluginu: {e}", MessageBox.TYPE_ERROR, timeout=5)

    def updateAll(self):
        if self.local_picon_version == self.remote_picon_version and self.local_plugin_version == self.remote_plugin_version:
            self.session.open(MessageBox, "Vše je aktuální, není co aktualizovat.", MessageBox.TYPE_INFO, timeout=5)
            return

        # pouze jedna společná hláška a restart na konci
        def afterAll():
            self.session.openWithCallback(self.restartEnigma, MessageBox,
                "Picony a plugin byly úspěšně aktualizovány!\n\nEnigma2 bude nyní restartována.",
                MessageBox.TYPE_INFO, timeout=5)

        self.updatePicons(callback=lambda: self.updatePlugin(callback=afterAll))

    def restartEnigma(self, result=None):
        self.session.open(TryQuitMainloop, 3)


def main(session, **kwargs):
    session.open(PiconUpdater)


def Plugins(path, **kwargs):
    return [PluginDescriptor(
        name="Picon Updater",
        description="Aktualizace picon - obrázků kanálů pro Skylink (M7 Group)",
        where=PluginDescriptor.WHERE_PLUGINMENU,
        icon="plugin.png",
        fnc=main
    )]
