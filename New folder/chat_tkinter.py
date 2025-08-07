import tkinter as tk
from tkinter import scrolledtext
import requests

apiKey = "14216400-430c-45a5-a0c9-d0b327e5cac3"
basicUrl = "https://genai.hkbu.edu.hk/general/rest/deployments/gpt-4.1/chat/completions?api-version=2024-10-21"

def submit(message):
    conversation = [{"role": "user", "content": message}]
    url = basicUrl
    headers = { 'Content-Type': 'application/json', 'api-key': apiKey }
    payload = { 'messages': conversation }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # Extract the model's reply from the response
        try:
            reply = data['choices'][0]['message']['content']
        except Exception:
            reply = str(data)
        return reply
    else:
        return f"Error: {response.status_code}"

class ChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LLM Chatbot (GPT-4.1)")
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', width=60, height=20)
        self.chat_area.pack(padx=10, pady=10)
        self.entry = tk.Entry(root, width=50)
        self.entry.pack(padx=10, pady=(0,10), side=tk.LEFT)
        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(padx=(0,10), pady=(0,10), side=tk.LEFT)
        self.entry.bind('<Return>', lambda event: self.send_message())

    def send_message(self):
        user_message = self.entry.get().strip()
        if not user_message:
            return
        self.entry.delete(0, tk.END)
        self.append_chat("You: " + user_message)
        self.root.after(100, self.get_bot_response, user_message)

    def get_bot_response(self, message):
        bot_reply = submit(message)
        self.append_chat("Bot: " + bot_reply)

    def append_chat(self, text):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, text + "\n")
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()
