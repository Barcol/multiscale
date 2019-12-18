import glob
import os
import random
import imageio
import cv2
from PySide2.QtCore import Slot, Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QInputDialog, QSlider
from tqdm import tqdm

from src.application import Application
from src.boundaries_creator import BoundariesCreator
from src.energy_matrix import EnergyMatrix
from src.nucleons import Nucleons


class UserInterface(QWidget):
    def __init__(self, drawer):
        QWidget.__init__(self)
        self.drawer = drawer
        self.settings = {}
        self.dimensions = (0, 0)
        self.colors = {}
        self.app = Application((0, 0), 0)
        self.bc = 0

        self.temp_list, self.cp_list = None, None

        self.image_rect = QPixmap("./images/rect.png")

        self.button_data_input = QPushButton("Insert settings data")
        self.button_run_simulation = QPushButton("Run the simulation")
        self.button_rerun_simulation = QPushButton("Run second simulation")
        self.button_create_boundaries = QPushButton("Create boundaries and energy matrix")
        self.button_show_gif = QPushButton("Show simulation results")
        self.button_recrystallize = QPushButton("Run the recrystallization process")

        self.slider_structure = QSlider(Qt.Horizontal)
        self.slider_structure.setMinimum(19)
        self.slider_structure.setMaximum(20)
        self.slider_structure.setValue(20)
        self.slider_structure.setTickPosition(QSlider.TicksBelow)
        self.slider_structure.setTickInterval(1)

        self.slider_nucleon_start = QSlider(Qt.Horizontal)
        self.slider_nucleon_start.setMinimum(19)
        self.slider_nucleon_start.setMaximum(21)
        self.slider_nucleon_start.setValue(21)
        self.slider_nucleon_start.setTickPosition(QSlider.TicksBelow)
        self.slider_nucleon_start.setTickInterval(1)

        self.slider_recrystallization = QSlider(Qt.Horizontal)
        self.slider_recrystallization.setMinimum(19)
        self.slider_recrystallization.setMaximum(20)
        self.slider_recrystallization.setValue(20)
        self.slider_recrystallization.setTickPosition(QSlider.TicksBelow)
        self.slider_recrystallization.setTickInterval(1)

        self.slider_nucleon_start_text = QLabel("Beginnning")
        self.slider_nucleon_start_text.setAlignment(Qt.AlignCenter)

        self.slider_recrystallization_text = QLabel("On random")
        self.slider_recrystallization_text.setAlignment(Qt.AlignCenter)

        self.slider_energy_distribution_text = QLabel("Homogenius")
        self.slider_energy_distribution_text.setAlignment(Qt.AlignCenter)

        self.slider_energy_distribution = QSlider(Qt.Horizontal)
        self.slider_energy_distribution.setMinimum(19)
        self.slider_energy_distribution.setMaximum(20)
        self.slider_energy_distribution.setValue(20)
        self.slider_energy_distribution.setTickPosition(QSlider.TicksBelow)
        self.slider_energy_distribution.setTickInterval(1)

        self.slider_structure_text = QLabel("Dual Phase")
        self.settings["energy_distribution"] = "homo"
        self.settings["nucleon_start"] = "beginning"
        self.slider_structure_text.setAlignment(Qt.AlignCenter)

        self.slider_grow_type = QSlider(Qt.Horizontal)
        self.slider_grow_type.setMinimum(19)
        self.slider_grow_type.setMaximum(20)
        self.slider_grow_type.setValue(20)
        self.slider_grow_type.setTickPosition(QSlider.TicksBelow)
        self.slider_grow_type.setTickInterval(1)

        self.slider_grow_type_text = QLabel("Monte Carlo")
        self.slider_grow_type_text.setAlignment(Qt.AlignCenter)

        self.text = QLabel("Use buttons bellow to control application behavior")
        self.text.setAlignment(Qt.AlignCenter)

        self.result_image = QLabel("")
        self.result_image.setAlignment(Qt.AlignCenter)

        self.settings["second_simulation_type"] = "dual_phase"
        self.settings["second_grow_type"] = "monte_carlo"
        self.settings["recrystallization"] = "random"
        self.settings["gb_value"] = 5

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.result_image)

        self.layout.addWidget(self.slider_structure_text)
        self.layout.addWidget(self.slider_grow_type_text)
        self.layout.addWidget(self.slider_energy_distribution_text)
        self.layout.addWidget(self.slider_recrystallization_text)
        self.layout.addWidget(self.slider_nucleon_start_text)

        self.layout.addWidget(self.button_data_input)
        self.layout.addWidget(self.button_run_simulation)

        self.layout.addWidget(self.slider_structure)
        self.layout.addWidget(self.slider_grow_type)
        self.layout.addWidget(self.slider_energy_distribution)
        self.layout.addWidget(self.slider_recrystallization)
        self.layout.addWidget(self.slider_nucleon_start)

        self.layout.addWidget(self.button_rerun_simulation)
        self.layout.addWidget(self.button_create_boundaries)
        self.layout.addWidget(self.button_show_gif)
        self.layout.addWidget(self.button_recrystallize)

        self.setLayout(self.layout)

        self.button_run_simulation.setDisabled(False)
        self.button_show_gif.setDisabled(False)

        self.setWindowTitle("Multiscale Modeling \"Dej Boże 4.0\"")

        self.button_data_input.clicked.connect(self.set_settings)
        self.button_run_simulation.clicked.connect(self.simulate)
        self.button_show_gif.clicked.connect(self.show_movie)
        self.button_create_boundaries.clicked.connect(self.create_boundaries)
        self.button_rerun_simulation.clicked.connect(self.rerun_simulation)
        self.button_recrystallize.clicked.connect(self.recrystallize)

        self.slider_structure.valueChanged.connect(self.change_slider)
        self.slider_grow_type.valueChanged.connect(self.change_slider_grow_type)
        self.slider_energy_distribution.valueChanged.connect(self.change_slider_energy)
        self.slider_recrystallization.valueChanged.connect(self.change_slider_recrystallization)
        self.slider_nucleon_start.valueChanged.connect(self.change_slider_nucleon)

    @Slot()
    def set_settings(self):
        self.settings["X"], ok = QInputDialog.getInt(self, "Dimension X", "Enter value", value=100)
        self.settings["Y"], ok = QInputDialog.getInt(self, "Dimension Y", "Enter value", value=100)
        self.settings["grains"], ok = QInputDialog.getInt(self, "Number of grains", "Enter value", value=5)
        self.settings["iterations"], ok = QInputDialog.getInt(self, "Iterations", "Enter value", value=10)

        dimensions = (int(self.settings["X"]), int(self.settings["Y"]))
        for index in range(0, int(self.settings["grains"]) + 1):
            self.colors[index] = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
        self.colors[999] = (1, 1, 1)
        self.app = Application(dimensions, int(self.settings["grains"]))

    @Slot()
    def simulate(self):
        self.entire_simulation()

    @Slot()
    def change_slider(self):
        picked_value = self.slider_structure.value()
        if picked_value == 19:
            self.settings["second_simulation_type"] = "substructure"
            self.slider_structure_text.setText("Substructure")
        if picked_value == 20:
            self.slider_structure_text.setText("Dual Phase")
            self.settings["second_simulation_type"] = "dual_phase"

    @Slot()
    def change_slider_nucleon(self):
        picked_value = self.slider_nucleon_start.value()
        if picked_value == 19:
            self.slider_nucleon_start_text.setText("Constant")
            self.settings["nucleon_start"] = "constant"
        if picked_value == 20:
            self.slider_nucleon_start_text.setText("Growing")
            self.settings["nucleon_start"] = "growing"
        if picked_value == 21:
            self.slider_nucleon_start_text.setText("Only at beginning")
            self.settings["nucleon_start"] = "beginning"

    @Slot()
    def change_slider_energy(self):
        picked_value = self.slider_energy_distribution.value()
        if picked_value == 19:
            self.settings["energy_distribution"] = "hetero"
            self.slider_energy_distribution_text.setText("Heterogenius")
        if picked_value == 20:
            self.slider_energy_distribution_text.setText("Homogenious")
            self.settings["energy_distribution"] = "homo"

    @Slot()
    def change_slider_recrystallization(self):
        picked_value = self.slider_recrystallization.value()
        if picked_value == 19:
            self.slider_recrystallization_text.setText("On boundaries")
            self.settings["recrystallization"] = "boundaries"
        if picked_value == 20:
            self.slider_recrystallization_text.setText("On random")
            self.settings["recrystallization"] = "random"

    @Slot()
    def change_slider_grow_type(self):
        picked_value = self.slider_grow_type.value()
        if picked_value == 19:
            self.slider_grow_type_text.setText("Cellural Automata")
            self.settings["second_grow_type"] = "cellural_automata"
        if picked_value == 20:
            self.slider_grow_type_text.setText("Monte Carlo")
            self.settings["second_grow_type"] = "monte_carlo"

    @Slot()
    def rerun_simulation(self):
        self.settings["number_of_old_grains_to_keep"], ok = QInputDialog.getInt(self, "How many grains to keep?",
                                                                                "Enter value",
                                                                                value=int(self.settings["grains"]))
        self.settings["number_of_new_grains"], ok = QInputDialog.getInt(self, "How many new grains?",
                                                                        "Enter value",
                                                                        value=int(self.settings["grains"]))
        for index in range(1, int(self.settings["number_of_new_grains"]) + 1):
            self.colors[index] = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
        self.app.change_old_cells_state(self.settings["second_simulation_type"],
                                        int(self.settings["number_of_old_grains_to_keep"]),
                                        int(self.settings["grains"]),
                                        int(self.settings["number_of_new_grains"]),
                                        self.colors)

        self.entire_simulation()
        self.settings["grains"] = self.settings["number_of_new_grains"]

    @Slot()
    def create_boundaries(self):
        if self.settings["energy_distribution"] == "hetero":
            self.settings["gb_value"], ok = QInputDialog.getInt(self, "Grain boundaries energy", "Enter value", value=5)
        self.settings["cell_value"], ok = QInputDialog.getInt(self, "Cell boundaries energy", "Enter value", value=15)
        last_frame = sorted(glob.glob('temp/*'))[-1]
        self.bc = BoundariesCreator(last_frame)
        self.bc.decode_image()
        self.bc.calculate_boundaries()
        self.bc.create_image()
        em = EnergyMatrix(self.settings["energy_distribution"], int(self.settings["gb_value"]),
                          int(self.settings["cell_value"]), self.bc.new_board)
        em.dispose_energy()
        self.result_image.setPixmap(QPixmap("boundaries/picture00.png"))

    @Slot()
    def recrystallize(self):
        self.settings["nucleons_number"], ok = QInputDialog.getInt(self, "How many nucleons?", "Enter value", value=5)
        self.settings["nucleons_iter"], ok = QInputDialog.getInt(self, "How many iterations?", "Enter value", value=5)
        if self.settings["recrystallization"] == "random":
            nucleon_dispenser = Nucleons(self.app.board, self.settings["nucleon_start"])
            nucleon_dispenser.put_nucleons(self.settings["nucleons_number"])
        else:
            nucleon_dispenser = Nucleons(self.app.board,  self.settings["nucleon_start"], gb_board=self.bc.new_board)
            nucleon_dispenser.put_nucleons(self.settings["nucleons_number"])
        nucleon_dispenser.set_looping(self.settings["nucleons_iter"])
        self.result_image.setPixmap(QPixmap(sorted(glob.glob('temp/*'))[-1]))
        self.create_video()

    @Slot()
    def show_movie(self):
        link_to_movie = sorted(glob.glob("results/*"))[-1]
        command_to_run = "mplayer -loop 0 -speed 1 -vf scale -zoom -xy 600 /home/radek/PycharmProjects/untitled2/{}".format(
            link_to_movie)
        os.system(command_to_run)

    def entire_simulation(self):
        self.drawer.create_png(self.app.board, self.colors)
        for _ in tqdm(range(int(self.settings["iterations"]))):
            self.app.iterate()
            self.drawer.create_png(self.app.board, self.colors)
        self.result_image.setPixmap(sorted(glob.glob('temp/*'))[-1])
        self.create_video()

    def create_video(self):
        images = []
        for image in sorted(glob.glob('temp/*')):
            images.append(imageio.imread(image))
        imageio.mimsave('gifs/gif' + '00' + '.gif', images)
