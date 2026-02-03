from flask import Flask, request, send_file, jsonify, render_template
from flask_cors import CORS
import os
import tempfile
from pathlib import Path
import traceback

from defacers import DEFACERS


# ------------------------------------------------------
#   OPTIONAL: VENV ACTIVATION (generally not recommended in production)
# ------------------------------------------------------
venv_path = os.path.join(os.path.dirname(__file__), "venv")
if os.path.exists(venv_path):
    activate_this = os.path.join(venv_path, "bin", "activate_this.py")
    if os.path.exists(activate_this):
        exec(open(activate_this).read(), {"__file__": activate_this})

app = Flask(__name__)
CORS(app)


# ------------------------------------------------------
#   HOME PAGE (WEB UI)
# ------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    """
    Simple web interface.
    Renders templates/index.html
    """
    return render_template("index.html")


# ------------------------------------------------------
#   /methods ENDPOINT
# ------------------------------------------------------
@app.route("/methods", methods=["GET"])
def get_methods():
    """
    Lists available defacing methods on this machine (based on PATH/import checks).
    """
    available = []
    for key, d in DEFACERS.items():
        try:
            if d.is_available():
                available.append(
                    {
                        "value": key,
                        "label": d.label,
                        "description": d.description,
                    }
                )
        except Exception:
            # Keep it silent; optionally log if desired
            pass

    return jsonify({"methods": available, "total": len(available)})


# ------------------------------------------------------
#   /deface ENDPOINT
# ------------------------------------------------------
@app.route("/deface", methods=["POST"])
def deface():
    """
    Deface/anonymize an MRI volume.
    Expects multipart/form-data with:
      - file: .nii or .nii.gz
      - method: one of DEFACERS keys (optional, default: pydeface)
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part found in the request."}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    filename = file.filename
    if not (filename.endswith(".nii") or filename.endswith(".nii.gz")):
        return jsonify({"error": "Only .nii or .nii.gz files are supported."}), 400

    method = request.form.get("method", "pydeface").strip()
    if method not in DEFACERS:
        return jsonify({"error": f"Unsupported method: {method}"}), 400

    defacer = DEFACERS[method]
    if not defacer.is_available():
        return jsonify(
            {
                "error": f"Method '{method}' is not available on this system.",
                "hint": "Please ensure the required tool is installed and available in PATH (or Python package is installed).",
            }
        ), 400

    print(f"[UPLOAD] file={filename}")
    print(f"[METHOD] method={method}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Save uploaded file
        input_path = temp_path / filename
        file.save(str(input_path))

        # Output filename: anonymized name (does not include original filename)
        output_filename = f"defaced_{method}.nii"
        output_path = temp_path / output_filename

        try:
            print(f"[INPUT]  path={input_path} size={input_path.stat().st_size} bytes")

            # Run selected defacer (implemented in defacers/ modules)
            defacer.run(input_path, output_path)

            if not output_path.exists():
                return jsonify({"error": "Output file was not created."}), 500

            print(f"[OUTPUT] path={output_path} size={output_path.stat().st_size} bytes")

            return send_file(
                str(output_path),
                as_attachment=True,
                download_name=output_filename,
                mimetype="application/octet-stream",
                conditional=False,
            )

        except Exception as e:
            print(f"[ERROR] {e}")
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500


# ------------------------------------------------------
#   /health ENDPOINT
# ------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "ok",
            "message": "API is running.",
            "supported_methods": list(DEFACERS.keys()),
        }
    )


# ------------------------------------------------------
#   MAIN
# ------------------------------------------------------
if __name__ == "__main__":
    print("MRI Defacing Platform starting...")
    print("URL: http://localhost:5000")
    print("Web UI: GET /")
    print("Methods: GET /methods")
    print("Deface: POST /deface")
    print(f"Registered methods: {', '.join(DEFACERS.keys())}")
    app.run(host="0.0.0.0", port=8080, debug=True)
