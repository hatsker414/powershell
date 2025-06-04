import subprocess
import win32service
import win32serviceutil
import pywintypes
import tkinter as tk
from tkinter import ttk, messagebox

class ServiceRestarterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Remote Service Manager")
        self.root.geometry("600x500")  # Увеличил размер окна

        # Переменные
        self.remote_pc = tk.StringVar()
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.service_name = tk.StringVar()

        # GUI
        self.setup_ui()

    def setup_ui(self):
        # Фрейм для полей ввода
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10, fill=tk.X)

        # Поля ввода
        ttk.Label(input_frame, text="Remote PC (IP/Hostname):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(input_frame, textvariable=self.remote_pc).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(input_frame, text="Username (domain\\user):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(input_frame, textvariable=self.username).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(input_frame, text="Password:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(input_frame, textvariable=self.password, show="*").grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(input_frame, text="Service Name:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(input_frame, textvariable=self.service_name).grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)

        input_frame.columnconfigure(1, weight=1)

        # Фрейм для кнопок
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        # Кнопки действий
        ttk.Button(button_frame, text="List Services", command=self.list_services).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Stop Service", command=self.stop_service).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Start Service", command=self.start_service).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Restart Service", command=self.restart_service).grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, text="Restart ALL Services", command=self.restart_all_services).grid(row=1, column=0, columnspan=4, pady=10, sticky=tk.EW)

        # Лог
        self.log = tk.Text(self.root, height=15, state="disabled")
        scrollbar = ttk.Scrollbar(self.root, command=self.log.yview)
        self.log.configure(yscrollcommand=scrollbar.set)
        
        self.log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def log_message(self, msg):
        self.log.config(state="normal")
        self.log.insert(tk.END, msg + "\n")
        self.log.config(state="disabled")
        self.log.see(tk.END)

    def connect_rdp(self):
        """Подключение к RDP (демонстрация, реальное управление через WMI)"""
        pc = self.remote_pc.get()
        user = self.username.get()
        pwd = self.password.get()

        if not pc or not user:
            messagebox.showerror("Error", "Укажите PC и Username!")
            return False

        try:
            self.log_message(f"Подключение к {pc} под {user}...")
            return True
        except Exception as e:
            self.log_message(f"Ошибка подключения: {e}")
            return False

    def manage_service(self, action, service=None):
        """Управление службой (старт/стоп/рестарт)"""
        service = service or self.service_name.get()
        if not service:
            messagebox.showerror("Error", "Укажите имя службы!")
            return

        try:
            if action == "stop":
                win32serviceutil.StopService(service, machine=self.remote_pc.get())
                self.log_message(f"Служба {service} остановлена.")
            elif action == "start":
                win32serviceutil.StartService(service, machine=self.remote_pc.get())
                self.log_message(f"Служба {service} запущена.")
            elif action == "restart":
                win32serviceutil.RestartService(service, machine=self.remote_pc.get())
                self.log_message(f"Служба {service} перезапущена.")
        except pywintypes.error as e:
            self.log_message(f"Ошибка при работе с {service}: {e.strerror}")
        except Exception as e:
            self.log_message(f"Неожиданная ошибка: {str(e)}")

    def list_services(self):
        """Список служб (через WMI)"""
        try:
            services = win32serviceutil.EnumServicesStatus(self.remote_pc.get())
            self.log_message("\nДоступные службы:")
            for svc in services:
                self.log_message(f"- {svc[0]}")
            self.log_message(f"\nВсего служб: {len(services)}")
        except Exception as e:
            self.log_message(f"Ошибка при получении списка служб: {e}")

    def restart_all_services(self):
        """Перезапуск всех служб"""
        if not self.connect_rdp():
            return

        answer = messagebox.askyesno(
            "Подтверждение",
            "Вы действительно хотите перезапустить ВСЕ службы?\nЭто может повлиять на работу системы!",
            parent=self.root
        )
        if not answer:
            return

        try:
            services = win32serviceutil.EnumServicesStatus(self.remote_pc.get())
            total = len(services)
            self.log_message(f"\nНачало перезапуска {total} служб...")
            
            for i, svc in enumerate(services, 1):
                service_name = svc[0]
                self.log_message(f"{i}/{total}: Перезапуск {service_name}...")
                try:
                    self.manage_service("restart", service_name)
                except Exception as e:
                    self.log_message(f"Ошибка при перезапуске {service_name}: {str(e)}")
                self.root.update()  # Обновляем GUI
            
            self.log_message("\nВсе службы обработаны!")
        except Exception as e:
            self.log_message(f"Критическая ошибка: {str(e)}")

    def stop_service(self):
        if self.connect_rdp():
            self.manage_service("stop")

    def start_service(self):
        if self.connect_rdp():
            self.manage_service("start")

    def restart_service(self):
        if self.connect_rdp():
            self.manage_service("restart")

if __name__ == "__main__":
    root = tk.Tk()
    app = ServiceRestarterApp(root)
    root.mainloop()
