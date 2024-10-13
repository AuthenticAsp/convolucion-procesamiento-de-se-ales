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
    def __init__(self, root):
        self.root = root
        self.root.title("Gráfico de Audio en Tiempo Real")

        # Marco principal
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

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
        self.btnCerrar = tk.Button(self.frame, text="Cerrar", command=self.cerrarVentana)
        self.btnCerrar.pack(side=tk.TOP, padx=10, pady=10)

        # Configuración de matplotlib para la gráfica
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_ylim(-1, 1)
        self.ax.set_xlim(0, 1024)

        # Lienzo de matplotlib en Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

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

        self.cargarWav("audioWhatsapp.wav")

    def cargarWav(self, rutaArchivo):
        # Abrir el archivo WAV
        self.wf = wave.open(rutaArchivo, 'rb')
        self.rate = self.wf.getframerate()
        self.chunk = 1024

        # Configurar PyAudio
        p = pyaudio.PyAudio()
        self.stream = p.open(format=p.get_format_from_width(self.wf.getsampwidth()),
                             channels=self.wf.getnchannels(),
                             rate=self.rate,
                             output=True)

        self.estaEjecutando = True
        self.estaPausado = False
        self.btnPausar.config(state=tk.NORMAL)
        self.btnReanudar.config(state=tk.DISABLED)

        # Crear un hilo para la reproducción del audio
        self.hiloAudio = threading.Thread(target=self.reproducirWav)
        self.hiloAudio.start()

        # Actualizar el gráfico conforme se reproduce el audio
        self.actualizarPlot()

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

if __name__ == "__main__":
    root = tk.Tk()
    app = RealTimeAudioPlot(root)
    root.protocol("WM_DELETE_WINDOW", app.cerrarVentana)
    root.mainloop()
