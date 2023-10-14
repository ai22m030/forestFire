import sys
import numpy as np
import random
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsRectItem
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QSlider, QLabel
from PyQt5.QtGui import QBrush
from PyQt5.QtCore import Qt, QTimer

TREE, FIRE, EMPTY = 0, 1, 2
SIZE = 10  # size of one square


class ForestFireSimulator(QGraphicsView):
    def __init__(self, width, height, p_tree, p_fire, p_grow):
        super().__init__()
        self.width = width
        self.height = height
        self.p_fire = p_fire
        self.p_grow = p_grow
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setSceneRect(0, 0, width * SIZE, height * SIZE)
        self.init_forest(p_tree)
        self.timer = QTimer()
        self.timer.timeout.connect(self.step_forest)
        self.timer.start(100)  # adjust time for each step

    def init_forest(self, p_tree):
        self.forest = np.zeros((self.width, self.height), dtype=int)
        for x in range(self.width):
            for y in range(self.height):
                if random.random() < p_tree:
                    self.forest[x, y] = TREE
                    self.draw_square(x, y, Qt.green)
                else:
                    self.draw_square(x, y, Qt.white)

    def draw_square(self, x, y, color):
        square = QGraphicsRectItem(x * SIZE, y * SIZE, SIZE, SIZE)
        square.setBrush(QBrush(color))
        self.scene.addItem(square)

    def step_forest(self):
        new_forest = self.forest.copy()
        dx = [0, 1, 0, -1]
        dy = [1, 0, -1, 0]

        for x in range(self.width):
            for y in range(self.height):
                if self.forest[x, y] == FIRE:
                    new_forest[x, y] = EMPTY
                    self.draw_square(x, y, Qt.white)
                elif self.forest[x, y] == TREE:
                    if any(self.forest[(x + dx[i]) % self.width, (y + dy[i]) % self.height] == FIRE for i in range(4)):
                        new_forest[x, y] = FIRE
                        self.draw_square(x, y, Qt.red)
                    elif random.random() < self.p_fire:
                        new_forest[x, y] = FIRE
                        self.draw_square(x, y, Qt.red)
                elif self.forest[x, y] == EMPTY and random.random() < self.p_grow:
                    new_forest[x, y] = TREE
                    self.draw_square(x, y, Qt.green)

        self.forest = new_forest

    def mousePressEvent(self, event):
        x, y = event.x() // SIZE, event.y() // SIZE
        if self.forest[x, y] == TREE:
            self.forest[x, y] = FIRE
            self.draw_square(x, y, Qt.red)


class MainWidget(QWidget):
    def __init__(self, simulator):
        super().__init__(None)
        self.layout = QVBoxLayout()

        self.simulator = simulator

        self.pFireSlider = QSlider(Qt.Horizontal)
        self.pFireSlider.valueChanged.connect(self.update_p_fire)
        self.layout.addWidget(QLabel("Probability of spontaneous fire:"))
        self.layout.addWidget(self.pFireSlider)

        self.pGrowSlider = QSlider(Qt.Horizontal)
        self.pGrowSlider.valueChanged.connect(self.update_p_grow)
        self.layout.addWidget(QLabel("Probability of tree growth:"))
        self.layout.addWidget(self.pGrowSlider)

        self.layout.addWidget(self.simulator)
        self.setLayout(self.layout)

    def update_p_fire(self, value):
        self.simulator.p_fire = value / 1000  # adjust as per your scaling

    def update_p_grow(self, value):
        self.simulator.p_grow = value / 1000  # adjust as per your scaling


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # parameters
    width, height = 1024, 1024
    p_tree, p_fire, p_grow = 0.5, 0.001, 0.01

    simulator = ForestFireSimulator(width, height, p_tree, p_fire, p_grow)
    mainWidget = MainWidget(simulator)
    mainWidget.show()

    sys.exit(app.exec_())
