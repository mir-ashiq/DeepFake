from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import subprocess
import uuid  # Import the UUID module
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration for file uploads and output
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output_files'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file uploads and processing options
        source_file = request.files['source']
        target_file = request.files['target']
        frame_processors = request.form.getlist('frame_processor')
        
        if source_file and allowed_file(source_file.filename) and target_file and allowed_file(target_file.filename):
            # Generate unique filenames with UUIDs for uploaded files
            source_filename = str(uuid.uuid4()) + '_' + secure_filename(source_file.filename)
            target_filename = str(uuid.uuid4()) + '_' + secure_filename(target_file.filename)
            
            # Save uploaded files
            source_path = os.path.join(app.config['UPLOAD_FOLDER'], source_filename)
            target_path = os.path.join(app.config['UPLOAD_FOLDER'], target_filename)
            source_file.save(source_path)
            target_file.save(target_path)
            
            # Determine output file name with UUID
            output_filename = str(uuid.uuid4()) + '.jpg'  # Default output format is JPEG
            
            # Build and execute the processing command here
            processing_command = ['python', 'run.py', '-s', source_path, '-t', target_path, '-o', os.path.join(app.config['OUTPUT_FOLDER'], output_filename)]
            processing_command.extend(['--frame-processor', *frame_processors])
            
            try:
                # Execute the processing command using subprocess
                subprocess.run(processing_command, check=True)
                
                # Redirect to the output page
                return redirect(url_for('output', filename=output_filename))
            except subprocess.CalledProcessError:
                return render_template('error.html')
    
    return render_template('index.html')

@app.route('/output/<filename>')
def output(filename):
    return render_template('output.html', filename=filename)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    app.run(host="0.0.0.0", port=7860, debug=True)
    