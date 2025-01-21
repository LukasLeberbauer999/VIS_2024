import sys
from PySide6.QtWidgets import QApplication
import qtmain_window as mainwindow
import qt_widget as mainwidget

# Initialisiere die Qt-Anwendung
app = QApplication(sys.argv)

# Hauptfenster
widget = mainwidget.Widget()
window = mainwindow.MainWindow(widget)
window.show()

# Beende die Anwendung, wenn das Hauptfenster geschlossen wird
sys.exit(app.exec())