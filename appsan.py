from flask import Flask, render_template, request
import requests, os

app = Flask(__name__)

VISION_ENDPOINT = os.getenv("VISION_ENDPOINT")
VISION_KEY = os.getenv("VISION_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        image = request.files['file']
        
        # Reset the file pointer after reading the file (important!)
        image.seek(0)
        
        # Prepare headers and OCR URL
        headers = {'Ocp-Apim-Subscription-Key': VISION_KEY, 'Content-Type': 'application/octet-stream'}
        ocr_url = f"{VISION_ENDPOINT}/vision/v3.2/ocr"
        
        # Send image to Azure for OCR processing
        response = requests.post(ocr_url, headers=headers, data=image.read())
        
        # Check if API request was successful
        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            return f"Error: {response.text}"
        
        # Print the full response content for debugging
        result = response.json()
        print("OCR Response:", result)
        
        # Process the response and extract text
        text_output = []
        if 'regions' in result:
            for region in result['regions']:
                for line in region['lines']:
                    line_text = ' '.join([word['text'] for word in line['words']])
                    text_output.append(line_text)
        else:
            print("No text detected in the image.")

        # If text is found, return it; otherwise, notify the user
        if text_output:
            return render_template('result.html', text="\n".join(text_output))
        else:
            return render_template('result.html', text="No text detected in the image. Please try again with a clearer image.")
    
    except Exception as e:
        print(f"Error during OCR processing: {str(e)}")
        return f"Error: {str(e)}"



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
