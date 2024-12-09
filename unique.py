import tkinter as tk
from tkinter import scrolledtext
import threading
import speech_recognition as sr
import pyttsx3
from transformers import pipeline

# Initialize the recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Configure text-to-speech engine properties
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)

# Load NLP model
nlp_model = pipeline('text-generation', model='gpt2')

# Function to process user input
def process_input(user_input, output_box):
    """Process user input and display the response."""
    try:
        response = nlp_model(user_input, max_length=50, num_return_sequences=1, temperature=0.7, top_p=0.9)[0]['generated_text']
    except Exception as e:
        response = f"Error in processing input: {e}"
    output_box.config(state=tk.NORMAL)
    output_box.insert(tk.END, f"You: {user_input}\nBot: {response}\n\n")
    output_box.see(tk.END)
    output_box.config(state=tk.DISABLED)
    speak(response)

# Function to handle text input
def handle_text_input(input_box, output_box):
    user_input = input_box.get().strip()
    if user_input:
        input_box.delete(0, tk.END)
        threading.Thread(target=process_input, args=(user_input, output_box)).start()

# Function to handle speech input
def handle_speech(output_box):
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        output_box.config(state=tk.NORMAL)
        output_box.insert(tk.END, "Bot: Listening for your speech...\n")
        output_box.config(state=tk.DISABLED)
        try:
            audio = recognizer.listen(source)
            user_input = recognizer.recognize_google(audio)
            output_box.config(state=tk.NORMAL)
            output_box.insert(tk.END, f"You: {user_input}\n")
            output_box.config(state=tk.DISABLED)
            process_input(user_input, output_box)
        except sr.UnknownValueError:
            output_box.config(state=tk.NORMAL)
            output_box.insert(tk.END, "Bot: Sorry, I did not understand that.\n\n")
            output_box.config(state=tk.DISABLED)
        except sr.RequestError as e:
            output_box.config(state=tk.NORMAL)
            output_box.insert(tk.END, f"Bot: Error accessing recognition service: {e}\n\n")
            output_box.config(state=tk.DISABLED)

# Function to configure speech output
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Build the UI
def build_ui():
    root = tk.Tk()
    root.title("Colorful Chatbot")
    root.geometry("600x500")
    root.configure(bg="#283747")

    # Header
    header = tk.Label(root, text="ChatBot Assistant", font=("Helvetica", 20, "bold"), bg="#1ABC9C", fg="white", pady=10)
    header.pack(fill=tk.X)

    # Output area
    output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12), bg="#EAECEE", fg="#1B2631", padx=10, pady=10)
    output_box.pack(padx=10, pady=(10, 5), fill=tk.BOTH, expand=True)
    output_box.config(state=tk.DISABLED)

    # Input frame
    input_frame = tk.Frame(root, bg="#283747")
    input_frame.pack(padx=10, pady=5, fill=tk.X)

    input_box = tk.Entry(input_frame, font=("Arial", 14), bg="#FBFCFC", fg="#1B2631", width=50)
    input_box.pack(side=tk.LEFT, padx=(0, 5), pady=5, fill=tk.X, expand=True)

    send_button = tk.Button(input_frame, text="Send", font=("Arial", 12, "bold"), bg="#58D68D", fg="white",
                             command=lambda: handle_text_input(input_box, output_box))
    send_button.pack(side=tk.LEFT)

    # Speech button
    speech_button = tk.Button(root, text="🎤 Speak", font=("Arial", 12, "bold"), bg="#F4D03F", fg="white",
                               command=lambda: threading.Thread(target=handle_speech, args=(output_box,)).start())
    speech_button.pack(padx=10, pady=5)

    # Footer
    footer = tk.Label(root, text="Powered by GPT-2, SpeechRecognition, and pyttsx3", font=("Arial", 10), bg="#1ABC9C", fg="white")
    footer.pack(fill=tk.X, side=tk.BOTTOM)

    root.mainloop()

if __name__ == "__main__":
    build_ui()
