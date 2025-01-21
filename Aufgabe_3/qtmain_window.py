from pathlib import Path
from PySide6.QtGui import QAction, QKeySequence, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QDockWidget, QListView, QVBoxLayout, QWidget, QTreeView, QColorDialog
from PySide6.QtCore import Qt
import mbsModel
import qt_widget as mwid
import vtk

class MainWindow(QMainWindow):
    #WINDOW_GEOMETRY = (300, 300, 2000, 2000)  # x, y, Breite, Höhe

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

        # Strukturbaum-Dock-Widget hinzufügen
        self.strukturbaum = self._erstelle_strukturbaum()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.strukturbaum)
    
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

        # Weitere Actions
        menu_bar.addAction(self._create_action("Fullscreen", self.fullscreen, QKeySequence("F11")))
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
                # Aktualisiere den Strukturbaum mit dem tatsächlichen Dateinamen
                self.update_strukturbaum(file_name=Path(filename).name)
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
            # Aktualisiere den Strukturbaum mit dem tatsächlichen Dateinamen
            self.update_strukturbaum(file_name=Path(filename).name)
        else:
            self._show_message("Bitte FDD Datei wählen")

    def speichern_fdd(self):
        # Speichert das Modell als JSON
        filename, _ = QFileDialog.getSaveFileName(self, "FDD Datei speichern", "", "FDD Files (*.fdd)")
        if filename:
            self.myModel.saveDatabase(Path(filename))
            self.statusBar().showMessage(f"Modell gespeichert: {filename}")

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

    def _erstelle_strukturbaum(self):
        #erstellt Dock widget für Strukturbaum (also die Positionierung)
        dock_widget = QDockWidget("Strukturbaum", self)
        dock_widget.setFeatures(QDockWidget.NoDockWidgetFeatures) #fixiert an linke Seite
        
        # Erstelle ein Widget für den Strukturbaum
        tree_widget = QWidget()
        layout = QVBoxLayout(tree_widget)

        # Erstelle den Baum-Modell
        self.tree_model = QStandardItemModel()
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.tree_model)
        layout.addWidget(self.tree_view)

        # updaten der Baum Struktur
        self.update_strukturbaum()

        # Setze das Widget im Dock-Widget
        dock_widget.setWidget(tree_widget)

        return dock_widget
    
    def update_strukturbaum(self, file_name="File Name"):
        #Aktualisiert den Strukturbaum

        # Clear the model completely
        self.tree_model.clear()

        # Explicitly set the root item
        root_item = QStandardItem(file_name)
        root_item.setEditable(False)  # Schreibschutz
        self.tree_model.appendRow(root_item)

        # Add child categories to the root item
        rigid_bodies_item = QStandardItem("Rigid Bodies")
        rigid_bodies_item.setEditable(False)
        constraints_item = QStandardItem("Constraints")
        constraints_item.setEditable(False)
        forces_item = QStandardItem("Forces")
        forces_item.setEditable(False)
        measures_item = QStandardItem("Measures")
        measures_item.setEditable(False)

        # Befüllen der Kategorien
        for obj in self.myModel.get_mbsObjectList():
            obj_type, name = self.myModel.get_object_type_and_name(obj)
            item = QStandardItem(name)

            if obj_type == "Body":
                rigid_bodies_item.appendRow(item)
                rigid_bodies_item.setEditable(False) 
            elif obj_type == "Constraint":
                constraints_item.appendRow(item)
                constraints_item.setEditable(False)
            elif obj_type == "Force":
                forces_item.appendRow(item)
                forces_item.setEditable(False)
            elif obj_type == "Measure":
                measures_item.appendRow(item)
                measures_item.setEditable(False)

        # Fügt die Kategorien der Struktur hinzu
        root_item.appendRow(rigid_bodies_item)
        root_item.appendRow(constraints_item)
        root_item.appendRow(forces_item)
        root_item.appendRow(measures_item)

    def _show_message(self, title, text):
        QMessageBox.critical(self, title, text)
