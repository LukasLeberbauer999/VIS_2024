from pathlib import Path
from PySide6.QtGui import QAction, QKeySequence, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QDockWidget, QListView, QVBoxLayout, QWidget, QTreeView, QColorDialog
from PySide6.QtCore import Qt
import mbsModel
import qt_widget as mwid
import vtk

class MainWindow(QMainWindow):
    def __init__(self, widget):
        super().__init__()

        self.setWindowTitle("VISUALISIERUNG")
        self.setCentralWidget(widget)

        # Initialisiere MBS Modell
        self.myModel = mbsModel.mbsModel()

        # Menü und Aktionen erstellen
        self._create_menus()

        # Statusleiste initialisieren
        self.statusBar().showMessage("Öffnen SIE das zu darstellende Modell!")

        # Initialisierung vom Interactor
        self.current_interactor_style = "default"
        # Text-Actor initialisieren 
        self.is_text_visible = False
        self.centralWidget().update_text_actor("")

        # Hintergrundfarbe-Status (True = Weiß, False = Dunkelgrau)
        self.is_background_light = True
    
    #Erstellen der Menüs
    def _create_menus(self):
        #Erstellt ein Menü
        menu_bar = self.menuBar()

        # Datei-Menü
        file_menu = menu_bar.addMenu("Datei") #Erstellt ein Dropdown
        file_menu.addAction(self._create_action("JSON Datei laden", self.lade_json))   # Fügt zum Dropdown hinzu
        file_menu.addAction(self._create_action("FDD Datei laden", self.lade_fdd))
        file_menu.addAction(self._create_action("JSON Datei speichern", self.speichern_json))
        file_menu.addAction(self._create_action("FDD Datei speichern", self.speichern_fdd))
        file_menu.addAction(self._create_action("Beenden", self.close, QKeySequence.Quit))

        # Ansicht-Menü
        ansicht_menu = menu_bar.addMenu("Ansicht")
        ansicht_menu.addAction(self._create_action("Fullscreen", self.fullscreen, QKeySequence("F11")))
        ansicht_menu.addAction(self._create_action("Hintergrund HELL/DUNKEL", self.toggle_background_color, QKeySequence("Ctrl+B")))
        
        # Weitere Actions
        menu_bar.addAction(self._create_action("Screenshot speichern", self.screenshot))
        menu_bar.addAction(self._create_action("Vorderansicht", self.vorderansicht))
        menu_bar.addAction(self._create_action("Draufsicht", self.draufsicht))
        menu_bar.addAction(self._create_action("Seitenansicht", self.seitenansicht))
        menu_bar.addAction(self._create_action("ISO-Ansicht", self.isoansicht))

    def _create_action(self, name, method, shortcut=None):
        #führt Aktionen (geklickte Buttons) aus
        action = QAction(name, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(method)
        return action

    def lade_json(self):
        #Lädt JSON Datei
        filename, _ = QFileDialog.getOpenFileName(self, "JSON Datei laden", "", "JSON Files (*.json)")
        if filename:
            if filename.lower().endswith(".json"):
                self.myModel.loadDatabase(Path(filename))
                self.statusBar().showMessage(f"Modell aus JSON geladen: {filename}")
                self.centralWidget().update_renderer(self.myModel)
                
            else:
                self._show_message("Bitte JSON Datei wählen")

    def speichern_json(self):
        # Speichert das Modell als JSON
        filename, _ = QFileDialog.getSaveFileName(self, "JSON Datei speichern", "", "JSON Files (*.json)")
        if filename:
            self.myModel.saveDatabase(Path(filename))
            self.statusBar().showMessage(f"Modell gespeichert: {filename}")

    def lade_fdd(self):
        #Lädt FDD Datei
        filename, _ = QFileDialog.getOpenFileName(self, "FDD Datei laden", "", "FDD Files (*.fdd)")
        if filename.lower().endswith(".fdd"):
            self.myModel.importFddFile(filename)
            self.statusBar().showMessage(f"FDD-Datei importiert: {filename}")
            self.centralWidget().update_renderer(self.myModel)
            
        else:
            self._show_message("Bitte FDD Datei wählen")

    def speichern_fdd(self):
        # Speichert das Modell als JSON
        filename, _ = QFileDialog.getSaveFileName(self, "FDD Datei speichern", "", "FDD Files (*.fdd)")
        if filename:
            self.myModel.saveDatabase(Path(filename))
            self.statusBar().showMessage(f"Modell gespeichert: {filename}")

    def toggle_background_color(self):
        renderer = self.centralWidget().GetRenderer()

        if self.is_background_light:
             # Hintergrundfarbe auf Dunkelgrau setzen
            renderer.SetBackground(0.1, 0.1, 0.1)  # Dunkelgrau (RGB: 10%)
            self.statusBar().showMessage("Hintergrund geändert: Dunkelgrau")
        else:
            # Hintergrundfarbe auf Weiß setzen
            renderer.SetBackground(1.0, 1.0, 1.0)  # Weiß (RGB: 100%)
            self.statusBar().showMessage("Hintergrund geändert: Weiß")

        # Umschalten der Hintergrundfarbe
        self.is_background_light = not self.is_background_light

        # Renderfenster aktualisieren
        self.centralWidget().GetRenderWindow().Render()

    def screenshot(self):
        # Dialog für Dateispeicherung öffnen
        filename, _ = QFileDialog.getSaveFileName(self, "Screenshot speichern", "", "PNG Files (*.png)")
        if filename:
            # Screenshot vom VTK-Renderfenster erstellen
            render_window = self.centralWidget().GetRenderWindow()
            window_to_image_filter = vtk.vtkWindowToImageFilter()
            window_to_image_filter.SetInput(render_window)
            window_to_image_filter.SetScale(1)  # Skalierung (1 = Originalgröße)
            window_to_image_filter.SetInputBufferTypeToRGBA()
            window_to_image_filter.ReadFrontBufferOff()
            window_to_image_filter.Update()

            # PNG-Schreiber für die Datei
            writer = vtk.vtkPNGWriter()
            writer.SetFileName(filename)
            writer.SetInputConnection(window_to_image_filter.GetOutputPort())
            writer.Write()

            self.statusBar().showMessage(f"Screenshot gespeichert: {filename}")


    def fullscreen(self):
        #Vollbild
        if self.isFullScreen():
            self.showNormal()
            self.setGeometry()
        else:
            self.showFullScreen()

    def vorderansicht(self): #Zeigt die Vorderansicht
        self._set_camera_orientation(0, -1, 0, 0, 0, 1)
        self.statusBar().showMessage("Vorderansicht")

    def seitenansicht(self): #Zeigt die Seitenansicht
        self._set_camera_orientation(-1, 0, 0, 0, 0, 1)
        self.statusBar().showMessage("Seitenansicht")

    def draufsicht(self): #Zeigt die Draufsicht
        self._set_camera_orientation(0, 0, 1, 0, -1, 0)
        self.statusBar().showMessage("Draufsicht")

    def isoansicht(self): #Zeigt die ISO Ansicht
        self._set_camera_orientation(1, 1, 1, -1, 0, 0)
        self.statusBar().showMessage("ISO-Ansicht")

    def _set_camera_orientation(self, pos_x, pos_y, pos_z, up_x, up_y, up_z):
        #Kameraausrichtung
        renderer = self.centralWidget().GetRenderer()
        camera = renderer.GetActiveCamera()
        camera.SetPosition(pos_x, pos_y, pos_z)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(up_x, up_y, up_z)
        renderer.ResetCamera()
        self.centralWidget().GetRenderWindow().Render()

    def _show_message(self, title, text):
        QMessageBox.critical(self, title, text)
