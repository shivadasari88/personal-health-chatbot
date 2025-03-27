from flask import Flask, request, render_template
import ollama

app = Flask(__name__)
convo = []

symptoms = {
    "Elevated Blood Sugar": ["Blood sugar level", "Dietary intake", "Activity levels"],
    "Pain": ["Pain location", "Pain intensity", "Duration"],
    "Abdominal Pain": ["Pain location", "Dietary intake", "Symptoms"],
    # Add more symptoms and their related inputs as needed
}

selected_symptom = None
symptom_inputs = []

def stream_response(prompt):
    convo.append({'role': 'user', 'content': prompt})
    response = ''
    stream = ollama.chat(model='llama3.1:8b', messages=convo, stream=True)
    for chunk in stream:
        response += chunk['message']['content']
        print(chunk['message']['content'], end='', flush=True)
    convo.append({'role': 'assistant', 'content': response})
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    global selected_symptom, symptom_inputs
    if request.method == 'POST':
        if 'symptom' in request.form:
            selected_symptom = request.form['symptom']
            symptom_inputs = symptoms[selected_symptom]
            return render_template('inputs.html', symptom=selected_symptom, inputs=symptom_inputs)
        elif 'user_inputs' in request.form:
            user_inputs = request.form.getlist('user_inputs')
            user_input_text = f"Symptom: {selected_symptom}, Inputs: {user_inputs}"
            response = stream_response(user_input_text)
            return render_template('index.html', user_input=user_input_text, response=response, convo=convo)
    return render_template('index.html', convo=convo, symptoms=symptoms.keys())

if __name__ == '__main__':
    app.run(debug=True)
