from flask import Flask, render_template, request, redirect, url_for
import subprocess
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
OUTPUT_FOLDER = 'output_files'
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file uploads
        source_file = request.files['source']
        target_file = request.files['target']
        frame_processor = request.form.getlist('frame_processor')
        
        # Save uploaded files
        source_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(source_file.filename))
        target_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(target_file.filename))
        source_file.save(source_path)
        target_file.save(target_path)
        
        # Determine output file name
        output_filename = secure_filename('output.jpg')  # Default output format is JPEG
        
        # Build the command based on the provided options
        command = ['python', 'run.py', '-s', source_path, '-t', target_path]
        command.extend(['-o', os.path.join(app.config['OUTPUT_FOLDER'], output_filename)])
        command.extend(['--frame-processor', *frame_processor])
        
        # Execute the command
        try:
            subprocess.run(command, check=True)
            return redirect(url_for('output', filename=output_filename))
        except subprocess.CalledProcessError:
            return render_template('error.html')
    
    return render_template('index.html')

@app.route('/output/<filename>')
def output(filename):
    return render_template('output.html', filename=filename)
@app.route('/output_image/<filename>')
def output_image(filename):
    return app.send_static_file(os.path.join(app.config['OUTPUT_FOLDER'], filename))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    app.run(host="0.0.0.0", port=7860, debug=True)
