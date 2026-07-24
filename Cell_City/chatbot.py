import google.generativeai as genai

# 🔑 paste your API key here
genai.configure(api_key="PASTE_YOUR_KEY_HERE")

# choose AI model
model = genai.GenerativeModel("gemini-1.5-flash")

print("Chatbot is ready! Type exit to stop")

while True:
    user_input = input("You: ")

    if user_input == "exit":
        break

    response = model.generate_content(user_input)
    print("Bot:", response.text)