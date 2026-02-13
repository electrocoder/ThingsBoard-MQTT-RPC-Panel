"""
-------------------------------------------------------------------------
Project Name  : ThingsBoard MQTT & RPC Panel v1.0.1
Author        : [Sahin Mersin electrocoder@gmail.com / Mesebilisim.com]
Version       : 1.0.1
Created Date  : 2026-02-13
License       : MIT
Description   : This script provides a GUI to send 3 telemetry data points
                to the ThingsBoard platform via MQTT and receives real-time 
                RPC commands from the platform.
-------------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import messagebox
import json
import paho.mqtt.client as mqtt

# --- Configuration ---
THINGSBOARD_HOST = "raspi5-mese-iot.mesebilisim.com"  
ACCESS_TOKEN = "sfayhp1be225522tkrx8"     

class ThingsBoardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ThingsBoard MQTT & RPC Panel v1.0.1")
        self.root.geometry("400x480")
        self.root.configure(bg="#f4f4f9")

        # MQTT Setup
        self.client = mqtt.Client()
        self.client.username_pw_set(ACCESS_TOKEN)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # UI Setup
        self.setup_ui()
        
        # Start Connection
        try:
            self.client.connect(THINGSBOARD_HOST, 1883, 60)
            self.client.loop_start()
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server: {e}")

    def setup_ui(self):
        # Header Section
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="THINGSBOARD MONITOR", fg="white", bg="#2c3e50", 
                 font=('Helvetica', 12, 'bold')).pack(pady=15)

        # Telemetry Input Section
        input_container = tk.LabelFrame(self.root, text=" Telemetry Data ", padx=20, pady=20, bg="#f4f4f9")
        input_container.pack(padx=20, pady=20, fill=tk.X)

        self.temp_var = tk.DoubleVar(value=24.5)
        self.hum_var = tk.DoubleVar(value=45.0)
        self.pres_var = tk.DoubleVar(value=1012.0)

        self.create_input(input_container, "Temperature (°C):", self.temp_var)
        self.create_input(input_container, "Humidity (%):", self.hum_var)
        self.create_input(input_container, "Pressure (hPa):", self.pres_var)

        # Publish Button
        tk.Button(self.root, text="PUBLISH DATA", command=self.send_telemetry, 
                  bg="#27ae60", fg="white", font=('Arial', 10, 'bold'), 
                  padx=20, pady=8, bd=0, cursor="hand2").pack(pady=10)

        # RPC Status Panel
        rpc_frame = tk.Frame(self.root, bg="#ffffff", bd=1, relief=tk.RIDGE)
        rpc_frame.pack(padx=20, pady=20, fill=tk.X)
        
        tk.Label(rpc_frame, text="Command from Platform (RPC):", bg="#ffffff", font=('Arial', 9, 'italic')).pack(pady=5)
        self.rpc_label = tk.Label(rpc_frame, text="WAITING FOR COMMAND", bg="#ffffff", 
                                  fg="#e67e22", font=('Courier', 11, 'bold'))
        self.rpc_label.pack(pady=10)

    def create_input(self, parent, label_text, var):
        frame = tk.Frame(parent, bg="#f4f4f9")
        frame.pack(fill=tk.X, pady=5)
        tk.Label(frame, text=label_text, width=18, anchor="w", bg="#f4f4f9").pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=var, width=12, justify='center').pack(side=tk.RIGHT)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(">> Successfully connected to ThingsBoard.")
            client.subscribe("v1/devices/me/rpc/request/+")
        else:
            print(f">> Connection failed with code: {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            # RPC Method check
            if payload.get("method") == "setValue":
                new_val = payload.get("params")
                self.rpc_label.config(text=f"VALUE SET: {new_val}")
                
                # Send Response back to ThingsBoard
                request_id = msg.topic.split('/')[-1]
                client.publish(f"v1/devices/me/rpc/response/{request_id}", json.dumps({"status": "success"}), 1)
        except Exception as e:
            print(f"Error processing message: {e}")

    def send_telemetry(self):
        data = {
            "temperature": self.temp_var.get(),
            "humidity": self.hum_var.get(),
            "pressure": self.pres_var.get()
        }
        result = self.client.publish("v1/devices/me/telemetry", json.dumps(data))
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Data published: {data}")
        else:
            messagebox.showwarning("Warning", "Failed to send data. Check connection.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ThingsBoardApp(root)
    root.mainloop()
