from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import pyaudio
import wave
import threading
from threading import Condition

class RealTimeAudioPlot:
    def __init__(self, root, parent_frame):
        self.root = root
        self.root.title("Gráfico de Audio en Tiempo Real")

        # Usamos el Frame que se pasa como argumento
        self.frame = parent_frame

        imgPausa = Image.open("pausaIcon.png")
        imgPlay = Image.open("playIcon.png")

        # Redimensionar las imágenes
        imgPausa = imgPausa.resize((32, 32), Image.LANCZOS)
        imgPlay = imgPlay.resize((32, 32), Image.LANCZOS)

        # Iconos 
        self.iconPausa = ImageTk.PhotoImage(imgPausa)
        self.iconReanudar = ImageTk.PhotoImage(imgPlay)

        # Botón de pausa
        self.btnPausar = tk.Button(self.frame, image=self.iconPausa, command=self.pausarAudio, state=tk.DISABLED)
        self.btnPausar.pack(side=tk.TOP, padx=10, pady=10)

        # Botón de reanudar
        self.btnReanudar = tk.Button(self.frame, image=self.iconReanudar, command=self.reanudarAudio, state=tk.DISABLED)
        self.btnReanudar.pack(side=tk.TOP, padx=10, pady=10)

        # Boton cerrar ventana
        # self.btnCerrar = tk.Button(self.frame, text="Cerrar", command=self.cerrarVentana)
        # self.btnCerrar.pack(side=tk.TOP, padx=10, pady=10)

        # Configuración de matplotlib para la gráfica dinámica (reducir tamaño con figsize)
        self.fig, self.ax = plt.subplots(figsize=(5, 2))  # Ancho, alto reducido
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_ylim(-1, 1)
        self.ax.set_xlim(0, 1024)

        # Lienzo de matplotlib en Tkinter para gráfico dinámico
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.X, expand=1)  # Expansión solo horizontal

        # Lienzo de matplotlib para gráfico estático (reducir tamaño con figsize)
        self.fig_static, self.ax_static = plt.subplots(figsize=(5, 2))  # Ancho, alto reducido
        self.canvas_static = FigureCanvasTkAgg(self.fig_static, master=self.frame)
        self.canvas_static.get_tk_widget().pack(side=tk.LEFT, fill=tk.X, expand=1)  # Expansión solo horizontal

        # Variables para PyAudio y datos del archivo
        self.chunk = 1024
        self.rate = 44100
        self.stream = None
        self.dataAudio = np.zeros(self.chunk)
        self.estaEjecutando = False
        self.estaPausado = True
        self.wf = None
        self.lock = threading.Lock()
        self.condition = Condition(self.lock)

        # self.cargarWav("audioWhatsapp.wav")


    def cargarWav(self, rutaArchivo):
        # Abrir el archivo WAV
        self.wf = wave.open(rutaArchivo, 'rb')
        self.rate = self.wf.getframerate()
        self.chunk = 1024

        # Leer todos los datos del archivo para el gráfico estático
        audio_data_full = self.wf.readframes(self.wf.getnframes())
        self.audio_data_static = np.frombuffer(audio_data_full, dtype=np.int16) / 32768.0

        # Configurar PyAudio
        p = pyaudio.PyAudio()
        self.stream = p.open(format=p.get_format_from_width(self.wf.getsampwidth()),
                             channels=self.wf.getnchannels(),
                             rate=self.rate,
                             output=True)

        # Resetear posición del archivo después de leer todo para la gráfica
        self.wf.rewind()

        self.estaEjecutando = True
        self.estaPausado = False
        self.btnPausar.config(state=tk.NORMAL)
        self.btnReanudar.config(state=tk.DISABLED)

        # Crear un hilo para la reproducción del audio
        self.hiloAudio = threading.Thread(target=self.reproducirWav)
        self.hiloAudio.start()

        # Limpiar y actualizar las gráficas
        self.limpiarGraficas()
        self.mostrarPlotEstatico()
        self.actualizarPlot()
        self.root.update()

    def limpiarGraficas(self):
        # Limpiar gráfico dinámico
        self.ax.clear()
        self.ax.set_ylim(-1, 1)
        self.ax.set_xlim(0, 1024)
        self.line, = self.ax.plot([], [], lw=2)
        self.canvas.draw()

        # Limpiar gráfico estático
        self.ax_static.clear()
        self.canvas_static.draw()

    def mostrarPlotEstatico(self):
        # Limpiar el gráfico estático y plotear toda la señal
        self.ax_static.clear()
        self.ax_static.plot(self.audio_data_static)
        self.ax_static.set_title("Señal completa")
        self.ax_static.set_xlim(0, len(self.audio_data_static))
        self.ax_static.set_ylim(-1, 1)
        self.canvas_static.draw()

    def reproducirWav(self):
        while self.estaEjecutando:
            with self.condition:
                while self.estaPausado:
                    self.condition.wait()  # Pausar el hilo sin consumir recursos

            data = self.wf.readframes(self.chunk)
            if not data:
                break

            self.stream.write(data)

            # Convertir el audio en una forma apta para graficar
            self.dataAudio = np.frombuffer(data, dtype=np.int16) / 32768.0
            if len(self.dataAudio) < self.chunk:
                self.dataAudio = np.pad(self.dataAudio, (0, self.chunk - len(self.dataAudio)), 'constant')

        self.stream.stop_stream()
        self.stream.close()
        self.estaEjecutando = False
        self.btnPausar.config(state=tk.DISABLED)

    def actualizarPlot(self):
        if self.estaEjecutando:
            self.line.set_ydata(self.dataAudio)
            self.line.set_xdata(np.arange(len(self.dataAudio)))
            self.ax.draw_artist(self.ax.patch)
            self.ax.draw_artist(self.line)
            self.canvas.draw()
            self.root.after(10, self.actualizarPlot)

    def pausarAudio(self):
        with self.condition:
            self.estaPausado = True
        self.btnPausar.config(state=tk.DISABLED)
        self.btnReanudar.config(state=tk.NORMAL)

    def reanudarAudio(self):
        with self.condition:
            self.estaPausado = False
            self.condition.notify() 
        self.btnPausar.config(state=tk.NORMAL)
        self.btnReanudar.config(state=tk.DISABLED)

    def cerrarVentana(self):
        self.estaEjecutando = False
        if self.wf:
            self.wf.close()
        self.root.destroy()

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = RealTimeAudioPlot(root)
#     root.protocol("WM_DELETE_WINDOW", app.cerrarVentana)
#     root.mainloop()
