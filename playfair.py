import sys
import PyQt5.QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import Qt

qtCreatorFile = "playfair.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

ABECEDA_EN = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
ABECEDA_CZ = "ABCDEFGHIJKLMNOPRSTUVWXYZ"

DIAKRITIKA = str.maketrans({
    "á": "a", "č": "c", "ď": "d", "é": "e", "ě": "e",
    "í": "i", "ň": "n", "ó": "o", "ř": "r", "š": "s",
    "ť": "t", "ú": "u", "ů": "u", "ý": "y", "ž": "z",
    "ô": "o", "ĺ": "l", "ľ": "l", "ŕ": "r",
})

ZNAKY_EN = {
    " ": "QM",
    "0": "QA", "1": "QB", "2": "QC", "3": "QD", "4": "QE",
    "5": "QF", "6": "QG", "7": "QH", "8": "QI", "9": "QK",
}

ZNAKY_CZ = {
    " ": "YM",
    "0": "YA", "1": "YB", "2": "YC", "3": "YD", "4": "YE",
    "5": "YF", "6": "YG", "7": "YH", "8": "YI", "9": "YK",
}


def abeceda_pro(jazyk):
    return ABECEDA_CZ if jazyk == "CZ" else ABECEDA_EN


def znaky_pro(jazyk):
    return ZNAKY_CZ if jazyk == "CZ" else ZNAKY_EN


def normalizuj(text, jazyk):
    text = text.lower().translate(DIAKRITIKA).upper()
    if jazyk == "CZ":
        text = text.replace("Q", "O").replace("W", "V")
    else:
        text = text.replace("J", "I")
    return text


def filtruj(text, jazyk="EN"):
    text = normalizuj(text, jazyk)
    abeceda = abeceda_pro(jazyk)
    znaky = znaky_pro(jazyk)
    vysledek = []
    for c in text:
        if c in znaky:
            vysledek.append(znaky[c])
        elif c in abeceda:
            vysledek.append(c)
    return "".join(vysledek)


def filtruj_klic(klic, jazyk="EN"):
    klic = normalizuj(klic, jazyk)
    abeceda = abeceda_pro(jazyk)
    vysledek = []
    for c in klic:
        if c in abeceda:
            vysledek.append(c)
    return "".join(vysledek)


def vrat_zpet(text, jazyk="EN"):
    znaky = znaky_pro(jazyk)
    zpet_mapa = {}
    for k in znaky:
        v = znaky[k]
        zpet_mapa[v] = k

    for i in zpet_mapa:
        znak = zpet_mapa[i]
        text = text.replace(i, znak)
    return text


def vytvor_tabulku(klic, jazyk="EN"):
    abeceda = abeceda_pro(jazyk)
    klic = filtruj_klic(klic, jazyk)
    poradi = []
    for c in klic + abeceda:
        if c not in poradi:
            poradi.append(c)
    return [poradi[i:i + 5] for i in range(0, 25, 5)]


def najdi(tabulka, znak):
    for r in range(5):
        for s in range(5):
            if tabulka[r][s] == znak:
                return r, s

def vytvor_bigramy(text, jazyk="EN"):
    v1 = "X"
    v2 = "W" if jazyk == "EN" else "Z"
    bigramy = []
    i = 0
    while i < len(text):
        a = text[i]
        if i + 1 < len(text):
            b = text[i + 1]
            if a == b:
                bigramy.append(a + (v2 if a == v1 else v1))
                i += 1
            else:
                bigramy.append(a + b)
                i += 2
        else:
            bigramy.append(a + (v2 if a == v1 else v1))
            i += 1
    return bigramy


def posun(tabulka, bigram, krok):
    r1, s1 = najdi(tabulka, bigram[0])
    r2, s2 = najdi(tabulka, bigram[1])
    if r1 == r2:
        return tabulka[r1][(s1 + krok) % 5] + tabulka[r2][(s2 + krok) % 5]
    elif s1 == s2:
        return tabulka[(r1 + krok) % 5][s1] + tabulka[(r2 + krok) % 5][s2]
    else:
        return tabulka[r1][s2] + tabulka[r2][s1]


def po_peticich(text):
    text = text.replace(" ", "")
    casti = []
    for i in range(0, len(text), 5):
        petice = text[i:i + 5]
        casti.append(petice)
    return " ".join(casti)


def zasifruj(text, klic, jazyk="EN"):
    tabulka = vytvor_tabulku(klic, jazyk)
    filtr = filtruj(text, jazyk)
    bigramy = vytvor_bigramy(filtr, jazyk)
    sifra = ""
    for i in bigramy:
        zasifrovany_bigram = posun(tabulka, i, 1)
        sifra = sifra + zasifrovany_bigram
    return sifra, filtr, bigramy, tabulka


def desifruj(text, klic, jazyk="EN"):
    tabulka = vytvor_tabulku(klic, jazyk)
    abeceda = set(abeceda_pro(jazyk))

    cisty = ""
    for c in text.upper():
        if c in abeceda:
            cisty = cisty + c

    bigramy = []
    for i in range(0, len(cisty), 2):
        dvojica = cisty[i:i + 2]
        bigramy.append(dvojica)

    desifrovany = ""
    for i in bigramy:
        posunuty_bigram = posun(tabulka, i, -1)
        desifrovany = desifrovany + posunuty_bigram

    v1 = "X"
    v2 = "W" if jazyk == "EN" else "Z"

    for i in abeceda_pro(jazyk):
        while i + v1 +i in desifrovany:
            desifrovany=desifrovany.replace(i+v1+i,i+i)
        while i + v2 +i in desifrovany:
            desifrovany=desifrovany.replace(i+v2+i,i+i)


    otevreny = vrat_zpet(desifrovany, jazyk)

    if otevreny and otevreny[-1] in (v1, v2):
        otevreny = otevreny[:-1]

    return otevreny, cisty, bigramy, tabulka


class MyApp(PyQt5.QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.comboBoxJazyk.clear()
        self.comboBoxJazyk.addItems(["CZ", "EN"])

        self.tableWidget.setRowCount(5)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setSectionResizeMode(PyQt5.QtWidgets.QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(PyQt5.QtWidgets.QHeaderView.Stretch)

        for r in range(5):
            for s in range(5):
                item = PyQt5.QtWidgets.QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(r, s, item)

        self.pushButtonZasifruj.clicked.connect(self.zasifruj_klik)
        self.pushButtonDesifruj.clicked.connect(self.desifruj_klik)
        self.lineEditKlic.textChanged.connect(self.obnov_vsetko)
        self.comboBoxJazyk.currentIndexChanged.connect(self.obnov_vsetko)

        self.vykresli_tabulku()

    def jazyk(self):
        return self.comboBoxJazyk.currentText()

    def _klic_ok(self):
        if not filtruj_klic(self.lineEditKlic.text(), self.jazyk()):
            PyQt5.QtWidgets.QMessageBox.critical(self, "Chyba", "Zadejte prosím klíč.")
            return False
        return True

    def vykresli_tabulku(self):
        tab = vytvor_tabulku(self.lineEditKlic.text(), self.jazyk())
        for r in range(5):
            for s in range(5):
                it = self.tableWidget.item(r, s)
                if it:
                    it.setText(tab[r][s])

    def obnov_vsetko(self):
        self.vykresli_tabulku()
        if self.textEditVstup.toPlainText().strip():
            self.zasifruj_klik()

    def zasifruj_klik(self):
        if not self._klic_ok():
            return
        vstup = self.textEditVstup.toPlainText().strip()
        if not vstup:
            PyQt5.QtWidgets.QMessageBox.warning(self, "Chyba", "Vložte vstupní text.")
            return
        sifra, filtr, bigramy, _ = zasifruj(vstup, self.lineEditKlic.text(), self.jazyk())
        self.textEditFiltrovany.setPlainText(po_peticich(filtr))
        self.textEditBigramy.setPlainText(" ".join(bigramy))
        self.textEditSifra.setPlainText(po_peticich(sifra))
        self.textEditVysledek.setPlainText(po_peticich(sifra))

    def desifruj_klik(self):
        if not self._klic_ok():
            return
        sifra_pole = self.textEditSifra.toPlainText().strip()
        vstup = sifra_pole or self.textEditVstup.toPlainText().strip()
        if not vstup:
            PyQt5.QtWidgets.QMessageBox.warning(self, "Chyba", "Zadejte text k dešifrování.")
            return
        otevreny, cisty, bigramy, _ = desifruj(vstup, self.lineEditKlic.text(), self.jazyk())
        self.textEditFiltrovany.setPlainText(po_peticich(cisty))
        self.textEditBigramy.setPlainText(" ".join(bigramy))
        self.textEditVysledek.setPlainText(otevreny)


if __name__ == "__main__":
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    okno = MyApp()
    okno.show()
    sys.exit(app.exec_())