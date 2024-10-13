import numpy as np
import soundfile as sf
from scipy.signal import convolve
import matplotlib.pyplot as plt

# Función para crear un impulso con eco
def generar_impulso_echo(duracion_impulso, retardo, decaimiento, sr):
    duracion_muestras = int(duracion_impulso * sr)
    retardo_muestras = int(retardo * sr)
    
    impulso = np.zeros(duracion_muestras)
    impulso[0] = 1  # Impulso principal
    if retardo_muestras < duracion_muestras:
        impulso[retardo_muestras] = decaimiento  # Eco
    
    return impulso

# Función para un filtro paso bajo utilizando convolución
def filtro_paso_bajo_conv(audio, sr, tam_kernel=101):
    kernel = np.ones(tam_kernel) / tam_kernel  # Kernel promedio simple (filtro paso bajo)
    if len(audio.shape) == 1:  # Mono
        audio_filtrado = convolve(audio, kernel, mode='same')
    else:  # Estéreo o más canales
        audio_filtrado = np.array([convolve(channel, kernel, mode='same') for channel in audio.T]).T
    return audio_filtrado / np.max(np.abs(audio_filtrado))

# Función para un filtro paso alto utilizando convolución
def filtro_paso_alto_conv(audio, sr, tam_kernel=101):
    kernel = -np.ones(tam_kernel) / tam_kernel
    kernel[tam_kernel // 2] = 1 + kernel[tam_kernel // 2]  # Asegurar que pasa las altas frecuencias
    if len(audio.shape) == 1:  # Mono
        audio_filtrado = convolve(audio, kernel, mode='same')
    else:  # Estéreo o más canales
        audio_filtrado = np.array([convolve(channel, kernel, mode='same') for channel in audio.T]).T
    return audio_filtrado / np.max(np.abs(audio_filtrado))

# Función para agregar reverberación simulando una sala
def agregar_reverberacion(audio, sr, reverb_decay=0.5):
    duracion_impulso = 2.5  # 1.5 segundos de reverberación
    impulso_reverb = generar_impulso_echo(duracion_impulso, 0.05, reverb_decay, sr)
    if len(audio.shape) == 1:  # Mono
        audio_con_reverb = convolve(audio, impulso_reverb, mode='full')
    else:  # Estéreo o más canales
        audio_con_reverb = np.array([convolve(channel, impulso_reverb, mode='full') for channel in audio.T]).T
    return audio_con_reverb / np.max(np.abs(audio_con_reverb))

# Función para graficar las señales
def graficar_comparacion(audio_original, audio_procesado, sr, titulo):
    tiempo_original = np.linspace(0, len(audio_original) / sr, num=len(audio_original))
    tiempo_procesado = np.linspace(0, len(audio_procesado) / sr, num=len(audio_procesado))
    
    plt.figure(figsize=(10, 6))
    
    # Gráfico de la señal original
    plt.subplot(2, 1, 1)
    plt.plot(tiempo_original, audio_original, color='blue')
    plt.title('Señal Original')
    plt.xlabel('Tiempo [s]')
    plt.ylabel('Amplitud')

    # Gráfico de la señal procesada
    plt.subplot(2, 1, 2)
    plt.plot(tiempo_procesado, audio_procesado, color='green')
    plt.title(titulo)
    plt.xlabel('Tiempo [s]')
    plt.ylabel('Amplitud')

    plt.tight_layout()
    plt.show()

# Leer el archivo de audio
audio, sr = sf.read('Senales/Practicas/p1Convolucion/audio3.wav')

# Menú de selección de efecto
print("Seleccione el efecto que desea aplicar:")
print("1. Eco")
print("2. Filtro Paso Bajo")
print("3. Filtro Paso Alto")
print("4. Reverberación")
opcion = int(input("Ingrese el número de la opción: "))

# Aplicar el efecto seleccionado
if opcion == 1:
    duracion_impulso = 2.0  # Duración total del impulso (en segundos)
    retardo = 0.5  # Retardo del eco (en segundos)
    decaimiento = 0.6  # Factor de decaimiento del eco
    impulso_echo = generar_impulso_echo(duracion_impulso, retardo, decaimiento, sr)
    
    if len(audio.shape) == 1:  # Mono
        audio_con_efecto = convolve(audio, impulso_echo, mode='full')
    else:  # Estéreo o más canales
        audio_con_efecto = np.array([convolve(channel, impulso_echo, mode='full') for channel in audio.T]).T
    
    audio_con_efecto = audio_con_efecto / np.max(np.abs(audio_con_efecto))
    titulo = "Señal con Eco"

elif opcion == 2:
    audio_con_efecto = filtro_paso_bajo_conv(audio, sr)
    titulo = "Señal con Filtro Paso Bajo (Convolución)"

elif opcion == 3:
    audio_con_efecto = filtro_paso_alto_conv(audio, sr)
    titulo = "Señal con Filtro Paso Alto (Convolución)"

elif opcion == 4:
    reverb_decay = 0.5  # Decaimiento de la reverberación
    audio_con_efecto = agregar_reverberacion(audio, sr, reverb_decay)
    titulo = "Señal con Reverberación"
    
else:
    print("Opción no válida")
    exit()

# Guardar el resultado en un nuevo archivo de audio
sf.write(f'Senales/Practicas/p1Convolucion/audio_con_efecto_{opcion}.wav', audio_con_efecto, sr)

# Graficar la comparación entre la señal original y la procesada
graficar_comparacion(audio, audio_con_efecto, sr, titulo)

print(f"El efecto ha sido aplicado y el archivo ha sido guardado como 'audio_con_efecto_{opcion}.wav'.")
