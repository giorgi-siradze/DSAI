from together import Together

# Initialize Together AI client
client = Together()

# Calls the AI model and returns the full response.
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


# Generates an antithesis that challenges the thesis.
def generate_antithesis(thesis: str) -> str:
    prompt = ("You are a dialectical thinker. Given the following thesis:\n\n"
              f"Thesis = {thesis}\n\n"
              "GProvide a single-sentence antithesis without explanation.")

    return ai_call(prompt)


# Synthesizes a new thesis by reconciling the contradiction.
def synthesize(thesis: str, antithesis: str) -> str:
    prompt = (" You are a dialectical thinker. Given the following thesis and antithesis:\n\n"
              f" Thesis = {thesis}\n\n"
              f" Antithesis = {antithesis}\n\n"
              "Generate a single-sentence synthesis that reconciles the contradiction between them, making up a refined, improved hypothesis without explanation.")
    return ai_call(prompt)


def synthesis(initial_thesis: str, max_iterations: int) -> str:
    # Runs the dialectical process iteratively.
    current_thesis = initial_thesis
    for i in range(max_iterations):
        print(f"Iteration {i + 1}")
        print("Current Thesis = ", current_thesis)

        antithesis = generate_antithesis(current_thesis)
        print("Generated Antithesis = ", antithesis)

        new_thesis = synthesize(current_thesis, antithesis)
        print("Synthesized Thesis = ", new_thesis)
        print("-" * 40)

        current_thesis = new_thesis  # Update thesis for next iteration

    return current_thesis


def run_chatbot():
    # Runs the chatbot in an infinite loop, allowing new prompts each time.
    while True:
        user_input = input("Enter your initial thesis: ")
        iteration_number = int(input("Enter number of iterations: "))

        current_thesis = synthesis(user_input, iteration_number)
        print("\nFinal Refined Synthesis:", current_thesis)

        while True:
            user_choice = input("Type 'refine' for refinement of the last thesis or type 'new' for a new prompt: ").strip().lower()

            if user_choice == "refine":
                refinement_number = int(input("Enter number of refinement (integer number): "))
                refined_thesis = synthesis(current_thesis, refinement_number)
                print("\nFinal Refined Synthesis:", refined_thesis)
            elif user_choice == "new":
                break


# Interactive Chatbot Loop
if __name__ == "__main__":
    print("Welcome to DSAI (Dialectical Synthesis via AI).")
    run_chatbot()
