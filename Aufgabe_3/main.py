import sys
from PySide6.QtWidgets import QApplication
import main_window as mwin
import main_widget as mwid

# Initialisiere die Qt-Anwendung
app = QApplication(sys.argv)

# Erstelle Hauptfenster und zeige es an
widget = mwid.Widget()
window = mwin.MainWindow(widget)
window.show()

# Beende die Anwendung, wenn das Hauptfenster geschlossen wird
sys.exit(app.exec())