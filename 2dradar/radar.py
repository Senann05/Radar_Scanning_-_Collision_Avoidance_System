import matplotlib
matplotlib.rcParams['toolbar'] = 'None'

import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button

SERIAL_PORT = 'COM5'
BAUD_RATE = 9600
MAX_DISTANCE = 100.0

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.05)
    print(f"Successfully connected to [{SERIAL_PORT}]. Starting SCADA Panel...")
except Exception as e:
    print(f"ERROR: Could not connect to {SERIAL_PORT}. Please check the port name!")
    exit()

is_muted = False
is_repair_mode = False

STATE_NAMES  = {0: "NORMAL", 1: "WARNING", 2: "DANGER"}
STATE_COLORS = {0: "lime",   1: "yellow",  2: "red"}

fig = plt.figure(figsize=(9, 8), facecolor='#111111')
try:
    fig.canvas.manager.set_window_title("AGV SCADA Panel")
except Exception:
    pass

ax = fig.add_axes([0.08, 0.20, 0.84, 0.68], polar=True)
ax.set_facecolor('#001a00')
ax.tick_params(colors='white')
ax.grid(color='#004400', alpha=0.7)

ax.set_thetamin(0)
ax.set_thetamax(180)
ax.set_ylim(0, MAX_DISTANCE)

ax.set_yticks([20, 40, 60, 80, 100])
ax.set_yticklabels(['20cm', '40cm', '60cm', '80cm', '100cm'], color='lightgreen', fontsize=8)

fig.suptitle("AGV 2D RADAR & COLLISION AVOIDANCE SYSTEM", color='lime', size=13, weight='bold', y=0.965)

status_text = fig.text(0.87, 0.90, "NORMAL", color='lime', fontsize=11, weight='bold', ha='center')

angles_rad = np.radians(np.arange(0, 181, 1))
distances = np.full(181, MAX_DISTANCE)

scat = ax.scatter(angles_rad, distances, c='lime', s=40, alpha=0.8, edgecolors='none')
sweep_line, = ax.plot([], [], color='lime', lw=2, alpha=0.7)

mute_ax = fig.add_axes([0.12, 0.05, 0.32, 0.08])
mute_button = Button(mute_ax, 'BUZZER: ON', color='#1a1a1a', hovercolor='#333333')
mute_button.label.set_color('lime')
mute_button.label.set_fontweight('bold')

mode_ax = fig.add_axes([0.56, 0.05, 0.32, 0.08])
mode_button = Button(mode_ax, 'MODE: WORK', color='#1a1a1a', hovercolor='#333333')
mode_button.label.set_color('lime')
mode_button.label.set_fontweight('bold')

def toggle_mute(event):
    global is_muted
    is_muted = not is_muted
    if is_muted:
        ser.write(b'M')
        mute_button.label.set_text('BUZZER: MUTED')
        mute_button.label.set_color('red')
    else:
        ser.write(b'U')
        mute_button.label.set_text('BUZZER: ON')
        mute_button.label.set_color('lime')
    fig.canvas.draw_idle()

def toggle_mode(event):
    global is_repair_mode
    is_repair_mode = not is_repair_mode
    if is_repair_mode:
        ser.write(b'R')
        mode_button.label.set_text('MODE: REPAIR')
        mode_button.label.set_color('yellow')
    else:
        ser.write(b'N')
        mode_button.label.set_text('MODE: WORK')
        mode_button.label.set_color('lime')
    fig.canvas.draw_idle()

mute_button.on_clicked(toggle_mute)
mode_button.on_clicked(toggle_mode)

def update(frame):
    if ser.in_waiting > 0:
        try:
            line_data = ser.readline().decode('utf-8').strip()

            if ',' in line_data:
                parts = line_data.split(',')
                
                if len(parts) >= 2:
                    angle = int(parts[0])
                    distance = float(parts[1])

                    if distance > MAX_DISTANCE or distance == 999.0:
                        distance = MAX_DISTANCE

                    if 0 <= angle <= 180:
                        distances[angle] = distance

                    if len(parts) >= 3:
                        state = int(parts[2])
                    else:
                        if distance <= 20:
                            state = 2
                        elif distance <= 40:
                            state = 1
                        else:
                            state = 0

                    status_text.set_text(STATE_NAMES.get(state, "NORMAL"))
                    status_text.set_color(STATE_COLORS.get(state, "lime"))

                    colors = []
                    for d in distances:
                        if d <= 20:
                            colors.append('red')
                        elif d <= 40:
                            colors.append('yellow')
                        else:
                            colors.append('lime')

                    scat.set_color(colors)
                    scat.set_offsets(np.c_[angles_rad, distances])

                    sweep_line.set_data([0, np.radians(angle)], [0, MAX_DISTANCE])

        except (ValueError, IndexError, UnicodeDecodeError):
            pass

    return scat, sweep_line, status_text

ani = animation.FuncAnimation(fig, update, interval=15, blit=False, cache_frame_data=False)
plt.show()