import os
import subprocess
import tempfile
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Security bypass for Netlify

@app.route('/process', methods=['POST'])
def process_video():
    # Check 1: Kya user ne sach me video bheji hai?
    if 'video' not in request.files:
        return jsonify({"error": "Video upload nahi hui"}), 400
    
    video = request.files['video']
    if video.filename == '':
        return jsonify({"error": "File ka naam khali hai"}), 400

    # PRO FEATURE 1: OS level Temp Files (Fastest Read/Write Speed)
    fd_in, input_path = tempfile.mkstemp(suffix=".mp4")
    fd_out, output_path = tempfile.mkstemp(suffix=".mp4")
    os.close(fd_in)
    os.close(fd_out)

    try:
        # Video save karna
        video.save(input_path)

        # Settings
        flip = request.form.get('flip') == 'true'
        speed = request.form.get('speed') == 'true'
        pitch = request.form.get('pitch') == 'true'

        vf, af = [], []
        if flip: vf.append('hflip')
        if speed:
            vf.append('setpts=0.95*PTS')
            af.append('atempo=1.05')
        elif pitch:
            af.append('asetrate=48000*1.1,atempo=1/1.1')

        # PRO FEATURE 2: 10x Speed FFmpeg Command
        cmd = ['ffmpeg', '-y', '-i', input_path]
        if vf: cmd.extend(['-vf', ','.join(vf)])
        if af: cmd.extend(['-af', ','.join(af)])
        
        # -threads 0: Server ke paas jitne CPU hain sab laga do
        # -crf 28: Halki si compression jisse file ka size chota ho aur export superfast ho
        cmd.extend([
            '-preset', 'ultrafast', 
            '-crf', '28', 
            '-threads', '0', 
            output_path
        ])

        if not vf and not af:
            cmd = ['ffmpeg', '-y', '-i', input_path, '-c', 'copy', output_path]

        # PRO FEATURE 3: Timeout Protection (Agar koi 5GB ki movie daal de, toh server hang na ho, 5 minute me reject kar de)
        subprocess.run(cmd, check=True, timeout=300)

        # Fast delivery
        return send_file(output_path, as_attachment=True, download_name="pro_cloned.mp4")

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Video bahut badi hai, server ne time out kar diya."}), 500
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500
    
    finally:
        # PRO FEATURE 4: Auto-Cleanup (Server 10 saal tak bhi chalega toh Storage Full nahi hogi)
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == '__main__':
    # Local testing ke liye (Cloud par Gunicorn handle karega)
    app.run(host='0.0.0.0', port=10000, threaded=True)
