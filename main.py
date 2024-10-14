import numpy as np
import soundfile as sf
from scipy.signal import convolve
import matplotlib.pyplot as plt
import tkinter as tk
import tkinter.filedialog
from canva import RealTimeAudioPlot
#-------------------------------- FUNCIONES --------------------------------#
audio = None
sr = None
audioConEfecto = None
app = None
#---------------- Cargar Archivo ----------------#
def cargarArchivo():
    global audio, sr
    archivo = tk.filedialog.askopenfilename(title="Seleccionar archivo de audio", filetypes=[("Archivos de audio", "*.wav")])
    if archivo:
        audio, sr = sf.read(archivo)
        print(f"Audio: {audio.shape}, SR: {sr}")
    else:
        print("No se seleccionó ningún archivo")

#---------------- Generar Impulso Eco ----------------#
def generarImpulsoEco(duracionImpulso, retardo, decaimiento, sr):
    duracionMuestras = int(duracionImpulso * sr) # Duración total del impulso
    retardoMuestras = int(retardo * sr) # Retardo del eco
    
    impulso = np.zeros(duracionMuestras)
    impulso[0] = 1  # Impulso principal
    if retardoMuestras < duracionMuestras:
        impulso[retardoMuestras] = decaimiento  # Eco
    
    return impulso

#---------------- Función Eco ----------------#
def ecoFuncion():
    global audioConEfecto, sr, audio, app
    duracionImpulso = 2.0  # Duración total del impulso
    retardo = 0.5  # Retardo del eco 
    decaimiento = 0.6  # Factor de decaimiento del eco
    impulso_echo = generarImpulsoEco(duracionImpulso, retardo, decaimiento, sr)
        
    if len(audio.shape) == 1:  # Mono
        audioConEfecto = convolve(audio, impulso_echo, mode='full')
    else:  # Estéreo o más canales
        audioConEfecto = np.array([convolve(channel, impulso_echo, mode='full') for channel in audio.T]).T

    audioConEfecto = audioConEfecto / np.max(np.abs(audioConEfecto))
    sf.write("audioConEco.wav", audioConEfecto, sr)

    
    app.cargarWav("audioConEco.wav")


#---------------- Función Paso Bajo ----------------#
def pasoBajoFuncion():
    global audioConEfecto, sr, audio, app
    tamanokernel=101
    kernel = np.ones(tamanokernel) / tamanokernel  # Kernel promedio simple (filtro paso bajo)
    if len(audio.shape) == 1:  # Mono
        audioConEfecto = convolve(audio, kernel, mode='same')
    else:  # Estéreo o más canales
        audioConEfecto = np.array([convolve(channel, kernel, mode='same') for channel in audio.T]).T
    audioConEfecto = audioConEfecto / np.max(np.abs(audioConEfecto))
    sf.write("audioPasoBajo.wav", audioConEfecto, sr)

    app.cargarWav("audioPasoBajo.wav")

#---------------- Función Paso Alto ----------------#
def pasoAltoFuncion():
    global audioConEfecto, sr, audio, app
    tamanokernel=101
    kernel = -np.ones(tamanokernel) / tamanokernel
    kernel[tamanokernel // 2] = 1 + kernel[tamanokernel // 2]  # Asegurar que pasa las altas frecuencias
    if len(audio.shape) == 1:  # Mono
        audioConEfecto = convolve(audio, kernel, mode='same')
    else:  # Estéreo o más canales
        audioConEfecto = np.array([convolve(channel, kernel, mode='same') for channel in audio.T]).T
    audioConEfecto = audioConEfecto / np.max(np.abs(audioConEfecto))
    sf.write("audioPasoAlto.wav", audioConEfecto, sr)

    root.update()
    app.cargarWav("audioPasoAlto.wav")

#---------------- Función Reverberación ----------------#
def reverbFuncion():
    global audioConEfecto, sr, audio, app
    reverbDecay = 0.5
    duracionImpulso = 2.5  # 1.5 segundos de reverberación
    impulsoReverb = generarImpulsoEco(duracionImpulso, 0.05, reverbDecay, sr)
    if len(audio.shape) == 1:  # Mono
        audioConEfecto = convolve(audio, impulsoReverb, mode='full')
    else:  # Estéreo o más canales
        audioConEfecto = np.array([convolve(channel, impulsoReverb, mode='full') for channel in audio.T]).T
    audioConEfecto = audioConEfecto / np.max(np.abs(audioConEfecto))
    sf.write("audioReverb.wav", audioConEfecto, sr)

    
    app.cargarWav("audioReverb.wav")

#---------------- Función Graficar ----------------#
#Código tuyo @Ulisex#



#-------------------------------- PARTE GRÁFICA --------------------------------#
root = tk.Tk()
root.title("Práctica Convolución")
root.geometry("900x800")
root.configure(bg='#D8DFE8')

#Texto hasta arriba de la ventana
title_label = tk.Label(root, text="Práctica Convolución", font=("Helvetica", 30, "bold"), bg='#D8DFE8')
title_label.pack(pady=10)
button = tk.Button(root, text="Cargar Archivo", width=20, bg="#609ED4", font=("Helvetica", 15, "bold"),
                     fg="white", relief="flat", activebackground="#1A5CBF", activeforeground="white", command=cargarArchivo)
button.pack(pady=10)


#------------------------ Botones Frame ------------------------#
button_frame = tk.Frame(root, bg='#D8DFE8')
button_frame.pack(pady=10)

#---------------- ECO ----------------#
sub_ECO = tk.Frame(button_frame, bg='#D8DFE8')
sub_ECO.pack(anchor="w", pady=5)
button = tk.Button(sub_ECO, height=2,text="Filtro Eco", width=20, bg="#0A3871", font=("Helvetica", 15, "bold"), 
                   fg="white", relief="flat", activebackground="#1A5CBF", activeforeground="white", command=ecoFuncion)
button.pack(side=tk.LEFT, padx=10)
label = tk.Label(sub_ECO, text="Este filtro....", font=("Helvetica", 15), bg='#D8DFE8')
label.pack(side=tk.LEFT)

#---------------- PASO BAJO ----------------#
sub_PB = tk.Frame(button_frame, bg='#D8DFE8')
sub_PB.pack(anchor="w", pady=5)
button = tk.Button(sub_PB, height=2,text="Filtro Paso Bajo", width=20, bg="#0A3871", font=("Helvetica", 15, "bold"), 
                   fg="white", relief="flat", activebackground="#1A5CBF", activeforeground="white", command=pasoBajoFuncion)
button.pack(side=tk.LEFT, padx=10)
label = tk.Label(sub_PB, text="Este filtro....", font=("Helvetica", 15), bg='#D8DFE8')
label.pack(side=tk.LEFT)

#---------------- PASO ALTO ----------------#
sub_PA = tk.Frame(button_frame, bg='#D8DFE8')
sub_PA.pack(anchor="w", pady=5)
button = tk.Button(sub_PA, height=2,text="Filtro Paso Alto", width=20, bg="#0A3871", font=("Helvetica", 15, "bold"), 
                   fg="white", relief="flat", activebackground="#1A5CBF", activeforeground="white", command=pasoAltoFuncion)
button.pack(side=tk.LEFT, padx=10)
label = tk.Label(sub_PA, text="Este filtro....", font=("Helvetica", 15), bg='#D8DFE8')
label.pack(side=tk.LEFT)

#---------------- REVERBERACIÓN ----------------#
sub_REVERB = tk.Frame(button_frame, bg='#D8DFE8')
sub_REVERB.pack(anchor="w", pady=5)
button = tk.Button(sub_REVERB, height=2,text="Filtro Reverberación", width=20, bg="#0A3871", font=("Helvetica", 15, "bold"), 
                   fg="white", relief="flat", activebackground="#1A5CBF", activeforeground="white", command=reverbFuncion)
button.pack(side=tk.LEFT, padx=10)
label = tk.Label(sub_REVERB, text="Este filtro....", font=("Helvetica", 15), bg='#D8DFE8')
label.pack(side=tk.LEFT)

#------------------------ Canvas Frame ------------------------#
canvas_frame = tk.Frame(root, bg='#D8DFE8')
canvas_frame.pack(pady=10)

# Integrar la clase RealTimeAudioPlot aquí
app = RealTimeAudioPlot(root, canvas_frame)

#------------------------ Main Loop ------------------------#
root.mainloop()
