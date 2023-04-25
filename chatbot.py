import os
import openai
from flask import Flask, render_template, request, jsonify
# from PyPDF2 import PdfFileReader
import pdfplumber
from io import BytesIO

app = Flask(__name__)
openai.api_key = ""


def extract_text_from_pdf(file):
    try:
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None


@app.route("/ask", methods=["POST"])
def ask():
    question = request.form["question"]
    print(f"Received question: {question}")

    pdf_file = request.files.get("pdf", None)

    if pdf_file:
        try:
            pdf_file = BytesIO(pdf_file.read())
            text = extract_text_from_pdf(pdf_file)
            if text:
                print(f"Extracted text from PDF:\n{text}")
                prompt = f"Please read the following document and answer the user's question.\n\nUser question: {question}\n\nDocument content:\n{text}"
            else:
                prompt = f"User question: {question}"
        except Exception as e:
            print(f"Error processing PDF file: {e}")
            return jsonify({"error": "Error processing PDF file."}), 400
    else:
        prompt = f"User question: {question}"

    print(prompt)

    prompt += "\n\nAnswer:"

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.3,
    )
    answer = response.choices[0].text.strip()

    # Check if the answer is random or irrelevant
    if "I don't know" in answer or "I am not sure" in answer or len(answer) < 10:
        answer = "I'm sorry, I couldn't find a relevant answer. Please try asking a different question or provide more context."

    return jsonify({"answer": answer})


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
