import tkinter as tk
from tkinter import ttk, scrolledtext
import queue
import threading
from together import Together

# Initialize Together AI client
client = Together()

# Global variables
current_thesis = ""
message_queue = queue.Queue()

total_iterations = 0

def ai_call(prompt: str, temperature: float = 0.8) -> str:
    stream = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        temperature=temperature,
    )

    response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            response += chunk.choices[0].delta.content
    return response


def generate_antithesis(thesis: str) -> str:
    prompt = ("You are a dialectical thinker. Given the following thesis:\n\n"
              f"Thesis = {thesis}\n\n"
              "Provide a single-sentence antithesis without explanation.")
    return ai_call(prompt, temperature=0.9)


def synthesize(thesis: str, antithesis: str) -> str:
    prompt = ("You are a dialectical thinker. Given the following thesis and antithesis:\n\n"
              f"Thesis = {thesis}\n\n"
              f"Antithesis = {antithesis}\n\n"
              "Generate a single-sentence synthesis that reconciles the contradiction between them, making up a refined, improved hypothesis without explanation.")
    return ai_call(prompt)


def synthesis_thread(initial_thesis, max_iterations):
    global total_iterations
    current_thesis = initial_thesis

    for i in range(max_iterations):
        total_iterations += 1
        message_queue.put({'type': 'iteration_start', 'iteration': total_iterations, 'thesis': current_thesis + "\n"})

        antithesis = generate_antithesis(current_thesis)
        message_queue.put({'type': 'antithesis', 'text': antithesis + "\n"})

        new_thesis = synthesize(current_thesis, antithesis)
        message_queue.put({'type': 'synthesis', 'text': new_thesis + "\n"})

        current_thesis = new_thesis

    message_queue.put({'type': 'final_synthesis', 'text': current_thesis + "\n"})


class DialecticalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dialectical Synthesis AI")
        self.root.geometry("800x600")

        # Create GUI elements
        self.create_widgets()
        self.check_queue()

    def create_widgets(self):
        # Input Frame
        input_frame = ttk.Frame(self.root, padding=10)
        input_frame.pack(fill=tk.X)

        # Thesis Input
        ttk.Label(input_frame, text="Initial Thesis:").grid(row=0, column=0, sticky=tk.W)
        self.thesis_input = ttk.Entry(input_frame, width=70)
        self.thesis_input.grid(row=0, column=1, padx=5, columnspan=3)

        # Iteration Controls
        ttk.Label(input_frame, text="Initial Iterations:").grid(row=1, column=0, sticky=tk.W)
        self.iterations_input = ttk.Spinbox(input_frame, from_=1, to=10, width=5)
        self.iterations_input.grid(row=1, column=1, sticky=tk.W, padx=5)
        self.iterations_input.set(3)

        ttk.Label(input_frame, text="Refinement Iterations:").grid(row=1, column=2, padx=10, sticky=tk.E)
        self.refinement_iterations_input = ttk.Spinbox(input_frame, from_=1, to=10, width=5)
        self.refinement_iterations_input.grid(row=1, column=3, sticky=tk.W)
        self.refinement_iterations_input.set(1)
        self.refinement_iterations_input.config(state=tk.DISABLED)

        self.start_button = ttk.Button(input_frame, text="Start Synthesis", command=self.start_synthesis)
        self.start_button.grid(row=0, column=4, rowspan=2, padx=10)

        # Output Area
        self.output_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='normal')
        self.output_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Control Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        self.refine_button = ttk.Button(
            button_frame,
            text="Refine",
            state=tk.DISABLED,
            command=self.refine
        )
        self.refine_button.pack(side=tk.LEFT, padx=5)

        self.new_button = ttk.Button(
            button_frame,
            text="New Prompt",
            state=tk.DISABLED,
            command=self.new_prompt
        )
        self.new_button.pack(side=tk.LEFT, padx=5)

    def check_queue(self):
        while True:
            try:
                msg = message_queue.get_nowait()
                if msg['type'] == 'iteration_start':
                    self.output_text.insert(tk.END, f"\nIteration {msg['iteration']}\n")
                    self.output_text.insert(tk.END, f"Thesis: {msg['thesis']}\n")
                elif msg['type'] == 'antithesis':
                    self.output_text.insert(tk.END, f"Antithesis: {msg['text']}\n")
                elif msg['type'] == 'synthesis':
                    self.output_text.insert(tk.END, f"Synthesis: {msg['text']}\n")
                    self.output_text.insert(tk.END, "-" * 60 + "\n")
                elif msg['type'] == 'final_synthesis':
                    global current_thesis
                    current_thesis = msg['text']
                    self.output_text.insert(tk.END, f"\nFinal Synthesis: {current_thesis}\n")
                    self.enable_refinement_mode()

                self.output_text.see(tk.END)
            except queue.Empty:
                break
        self.root.after(100, self.check_queue)

    def toggle_processing_state(self, processing=True):
        state = tk.DISABLED if processing else tk.NORMAL
        self.thesis_input.config(state=state)
        self.iterations_input.config(state=state)
        self.start_button.config(state=state)
        self.refinement_iterations_input.config(state=state)
        self.refine_button.config(state=state)
        self.new_button.config(state=state)

    def enable_refinement_mode(self):
        self.thesis_input.config(state=tk.DISABLED)
        self.iterations_input.config(state=tk.DISABLED)
        self.start_button.config(state=tk.DISABLED)
        self.refinement_iterations_input.config(state=tk.NORMAL)
        self.refine_button.config(state=tk.NORMAL)
        self.new_button.config(state=tk.NORMAL)

    def start_synthesis(self):
        initial_thesis = self.thesis_input.get()
        iterations = int(self.iterations_input.get())

        self.output_text.delete('1.0', tk.END)
        self.toggle_processing_state(True)

        thread = threading.Thread(
            target=synthesis_thread,
            args=(initial_thesis, iterations),
            daemon=True
        )
        thread.start()

    def refine(self):
        iterations = int(self.refinement_iterations_input.get())
        self.output_text.insert(tk.END, f"\nStarting refinement ({iterations} iterations)\n")
        self.toggle_processing_state(True)

        thread = threading.Thread(
            target=synthesis_thread,
            args=(current_thesis, iterations),
            daemon=True
        )
        thread.start()

    def new_prompt(self):
        self.thesis_input.delete(0, tk.END)
        self.iterations_input.set(3)
        self.refinement_iterations_input.set(1)
        self.output_text.delete('1.0', tk.END)
        self.thesis_input.config(state=tk.NORMAL)
        self.iterations_input.config(state=tk.NORMAL)
        self.start_button.config(state=tk.NORMAL)
        self.refinement_iterations_input.config(state=tk.DISABLED)
        self.refine_button.config(state=tk.DISABLED)
        self.new_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = DialecticalApp(root)
    root.mainloop()
