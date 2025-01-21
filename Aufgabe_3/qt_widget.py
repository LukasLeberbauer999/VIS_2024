import vtk
import QVTKRenderWindowInteractor as QVTK

class Widget(QVTK.QVTKRenderWindowInteractor):
    def __init__(self):
        super().__init__()

        # Initialisiere Renderer und füge ihn zum RenderWindow hinzu
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(1.0, 1.0, 1.0) # weißer Hintergrund
        self.GetRenderWindow().AddRenderer(self.renderer)

        # Text-Annotation hinzufügen
        self.text_actor = vtk.vtkTextActor()
        self.text_actor.SetPosition(10, 10)  # Position: links unten
        self.text_actor.GetTextProperty().SetFontSize(14)
        self.text_actor.GetTextProperty().SetColor(0, 0, 0)  # Schwarzer Text
        self.renderer.AddActor2D(self.text_actor)

    def update_renderer(self, model):
        """Aktualisiert den Renderer mit einem neuen Modell."""
        #self.renderer.RemoveAllViewProps()  # Entfernt alte Modelle
        model.showModel(self.renderer)  # Zeigt das neue Modell an
        self.renderer.ResetCamera()  # Kamera zurücksetzen
        self.GetRenderWindow().Render()  # Rendern des aktualisierten Fensters

    def update_text_actor(self, text):
        """Aktualisiert den Text des Text-Actors."""
        self.text_actor.SetInput(text)  # Text setzen
        self.GetRenderWindow().Render()  # Neu rendern

    def GetRenderer(self):
        return self.renderer
