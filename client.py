from customtkinter import *
from socket import *
import threading

class RegisterWindow(CTk):
    def __init__(self):
        super().__init__()
        self.username = None
        self.title('Приєднатися до сервера')
        self.geometry('300x300')
        CTkLabel(self, text='Вхід в Logitalk', font=('Arial', 20, 'bold')).pack(pady=40)
        self.name_entry = CTkEntry(self, placeholder_text='Введіть імя')
        self.name_entry.pack()
        self.host_entry = CTkEntry(self, placeholder_text='Введіть хост сервера localhost')
        self.host_entry.pack(pady=5)
        self.port_entry = CTkEntry(self, placeholder_text='Введіть порт сервера 12345')
        self.port_entry.pack()
        self.sumbit_button = CTkButton(self, text='Приєднатися', command=self.start_chat)
        self.sumbit_button.pack(pady=5)

    def start_chat(self):
        self.username = self.name_entry.get().strip()
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((self.host_entry.get(), int(self.port_entry.get())))
            hello = f"[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            self.destroy()
            win = MainWindow(self.sock, self.username)
            win.mainloop()
        except Exception as e:
            print(f"Не вдалося підключитись до сервера: {e}")

class MainWindow(CTk):
    def __init__(self, sock, username):
        super().__init__()
        self.geometry("400x500")
        
        self.frame = CTkFrame(self, width=200, height=self.winfo_height())
        self.frame.pack_propagate(False)
        self.frame.configure(width=0)
        self.frame.place(x=0, y=0)
        self.is_show_menu = False
        self.frame_width = 0

        self.frame.entry = CTkEntry(self.frame, placeholder_text="Введіть нікнейм...")
        self.frame.entry.pack(pady=30)
        self.frame.btn = CTkButton(self.frame, text="Встановити нікнейм", command=self.change_nickname)
        self.frame.btn.pack()
        
        self.label_theme = CTkOptionMenu(self.frame, values=['Темна', 'Світла'], command=self.change_theme)
        self.label_theme.pack(side='bottom', pady=20)
    

        self.btn = CTkButton(self, text='menu', command=self.toggle_show_menu)
        self.btn.place(x=0, y=0)
        self.menu_show_speed = 20
        
        self.chat_text = CTkTextbox(self, font=('Arial', 14, 'bold'), state="disable", fg_color="#994E4E")
        self.chat_text.place(x=0, y=30)

        self.message_input = CTkEntry(self, placeholder_text='Введіть повідомлення')
        self.message_input.place(x=0, y=250)

        self.send_button = CTkButton(self, text='Send', width=40, height=30, command=self.send_message)
        self.send_button.place(x=200, y=250)

        
        self.username = username
        self.sock = sock
        threading.Thread(target=self.recv_message, daemon=True).start()

        self.adaptive_ui()

    def show_menu(self):
        if self.frame_width <= 200:
            self.frame_width += self.menu_show_speed
            self.frame.configure(width=self.frame_width, height=self.winfo_height())
            if self.frame_width >= 30:
                self.btn.configure(width=self.frame_width, text='close')
        if self.is_show_menu:
            self.after(20, self.show_menu)

    def close_menu(self):
        if self.frame_width >= 0:
            self.frame_width -= self.menu_show_speed
            self.frame.configure(width=self.frame_width)
            if self.frame_width >= 30:
                self.btn.configure(width=self.frame_width, text='open')
        if not self.is_show_menu:
            self.after(20, self.close_menu)

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.close_menu()
        else:
            self.is_show_menu = True
            self.show_menu()

    def adaptive_ui(self):
        self.frame.configure(height=self.winfo_height())
        self.chat_text.place(x=self.frame.winfo_width())
        self.chat_text.configure(width=self.winfo_width() - self.frame.winfo_width(), height=self.winfo_height() - 40)
        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
        self.message_input.place(x=self.frame.winfo_width(), y=self.send_button.winfo_y())
        self.message_input.configure(width=self.winfo_width() - self.frame.winfo_width() - self.send_button.winfo_width())
        self.after(50, self.adaptive_ui)

    def add_message(self, text):
        self.chat_text.configure(state='normal')
        self.chat_text.insert(END, text + '\n')
        self.chat_text.configure(state='disable')

    def send_message(self):
        message = self.message_input.get()
        data = f"{self.username}: {message}"
        packet = data + "\n"
        if message:
            self.add_message(data)
            try:
                self.sock.sendall(packet.encode())
            except Exception as e:
                self.add_message(f"Не вдалося надіслати повідомлення: {e}")
        self.message_input.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.add_message(line.strip())
            except:
                break
        self.sock.close()

    def change_theme(self, value):
        if value == "Темна":
            set_appearance_mode("dark")
        else:
            set_appearance_mode("light")

    def change_nickname(self):
        nickname = self.frame.entry.get()
        if nickname:
            self.username = nickname

window = RegisterWindow()
window.mainloop()
