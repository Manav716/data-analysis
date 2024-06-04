from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
import os
from werkzeug.utils import secure_filename
import logging

# Set the Matplotlib backend to Agg to avoid GUI issues
plt.switch_backend('Agg')

app = Flask(__name__)

# Directory to save uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed extensions for file upload
ALLOWED_EXTENSIONS = {'csv'}

# Set up logging
logging.basicConfig(filename='error.log', level=logging.ERROR)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return redirect(url_for('analyze', filename=filename))
    return redirect(request.url)

@app.route('/analyze/<filename>', methods=['GET', 'POST'])
def analyze(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        df = pd.read_csv(file_path)
        
        if request.method == 'POST':
            column = request.form.get('column')
            if column not in df.columns:
                return jsonify({'error': 'Invalid column'}), 400
            
            summary_stats = df[column].describe().to_dict()
            plot_path = os.path.join('static', 'plot.png')
            
            # Debugging information
            app.logger.info(f"Generating histogram for column: {column}")
            
            plt.figure()
            df[column].hist()
            plt.title(f'Histogram of {column}')
            plt.savefig(plot_path)
            plt.close()
            
            # Debugging information
            app.logger.info(f"Histogram saved to: {plot_path}")
            
            return jsonify({'summary_stats': summary_stats, 'plot_url': plot_path})

        columns = df.columns.tolist()
        return render_template('analyze.html', columns=columns, filename=filename)
    except Exception as e:
        app.logger.error(f"Error occurred: {e}", exc_info=True)
        return "An error occurred. Please check the server logs for more details.", 500

if __name__ == '__main__':
    app.run(debug=True)
