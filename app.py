import os
import subprocess
import tempfile
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Nova AI Backend Running ✅"

@app.route("/process", methods=["POST"])
def process_video():

    if "video" not in request.files:
        return jsonify({"error": "Video upload nahi hui"}), 400

    video = request.files["video"]

    if video.filename == "":
        return jsonify({"error": "File ka naam khali hai"}), 400

    fd_in, input_path = tempfile.mkstemp(suffix=".mp4")
    fd_out, output_path = tempfile.mkstemp(suffix=".mp4")
    os.close(fd_in)
    os.close(fd_out)

    try:

        video.save(input_path)

        flip = request.form.get("flip") == "true"
        speed = request.form.get("speed") == "true"
        pitch = request.form.get("pitch") == "true"

        vf = []
        af = []

        if flip:
            vf.append("hflip")

        if speed:
            vf.append("setpts=0.95*PTS")
            af.append("atempo=1.05")

        if pitch:
            af.append("asetrate=48000*1.1,atempo=1/1.1")

        cmd = ["ffmpeg", "-y", "-i", input_path]

        if vf:
            cmd.extend(["-vf", ",".join(vf)])

        if af:
            cmd.extend(["-af", ",".join(af)])

        cmd.extend([
            "-preset", "ultrafast",
            "-crf", "28",
            "-threads", "0",
            output_path
        ])

        if not vf and not af:
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                input_path,
                "-c",
                "copy",
                output_path
            ]

        print("========== FFMPEG COMMAND ==========")
        print(cmd)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        print("========== RETURN CODE ==========")
        print(result.returncode)

        print("========== STDOUT ==========")
        print(result.stdout)

        print("========== STDERR ==========")
        print(result.stderr)

        if result.returncode != 0:
            return jsonify({
                "error": result.stderr
            }), 500

        return send_file(
            output_path,
            as_attachment=True,
            download_name="pro_cloned.mp4"
        )

    except subprocess.TimeoutExpired:
        return jsonify({
            "error": "Processing timeout (5 min)"
        }), 500

    except Exception as e:
        print(str(e))
        return jsonify({
            "error": str(e)
        }), 500

    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
