from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt as QtCoreQtClass
from pyqtgraph import PlotWidget, PlotCurveItem
import numpy as np

class FigureWidget(QWidget):
    def __init__(   self, title=f"Figure", yRange=[-2, 6], \
                    xdata=[], ydata=[], \
                    color=20 \
                ):
        super().__init__()
        self.title = f'<h3> {title} </h3>'
        
        self.color = color
        self.x_data = np.array(xdata)
        self.y_data = np.array(ydata)
        self.y_min, self.y_max = yRange[0] , yRange[1]
        self.initFigure()

    
    def initFigure(self):

        # Configure Layout
        self.layout_model = QGridLayout()
        self.setLayout( self.layout_model )

        # Figure title is 1x3 (row x col) excel cell
        self.TITLE = QLabel(text=self.title)
        self.TITLE.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.TITLE.setAlignment(QtCoreQtClass.AlignCenter)
        self.layout_model.addWidget(self.TITLE, 0, 0, 1, 3)
        self.layout_model.setRowStretch(0, 1)

        #Figure size is 4x3 (row x col) excel cell
        self.Figure = PlotWidget()
        self.Figure.setYRange(self.y_min, self.y_max)
        self.graph = PlotCurveItem(pen = self.color )
        self.graph.viewPos()

        #plot initial data
        self.graph.setData(self.x_data, self.y_data)
        self.Figure.addItem(self.graph)

        # add to main figure widget & resize the grid layout
        self.layout_model.addWidget(self.Figure, 1, 0, 4, 3)
        for n in range(4):
            self.layout_model.setRowStretch(n+1, 7)
    
    def PlotData(self, x_data, y_data):
        self.x_data = x_data
        self.y_data = y_data

        self.graph.setData(self.x_data, self.y_data)
