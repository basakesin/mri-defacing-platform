from flask import Flask, request, send_file, jsonify, render_template
from flask_cors import CORS
import os
import subprocess
import tempfile
from pathlib import Path
import traceback

# ------------------------------------------------------
#   SANAL ORTAM AYARI
# ------------------------------------------------------
venv_path = os.path.join(os.path.dirname(__file__), "venv")
if os.path.exists(venv_path):
    activate_this = os.path.join(venv_path, "bin", "activate_this.py")
    if os.path.exists(activate_this):
        exec(open(activate_this).read(), {"__file__": activate_this})

app = Flask(__name__)
CORS(app)

# ------------------------------------------------------
#   DESTEKLENEN METODLAR
# ------------------------------------------------------
SUPPORTED_METHODS = {
    "pydeface": "PyDeface - Industry standard FSL-based method",
    "quickshear": "Quickshear - Fast and high-quality defacing",
    "deepdefacer": "DeepDefacer - AI-powered face detection",
    "mri_deface": "MRI Deface - FreeSurfer-based approach",
    "anonymi": "AnonyMI - Advanced anonymization technique",
}


# ------------------------------------------------------
#   ANA SAYFA (BASİT ÖN YÜZ İÇİN)
# ------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    """
    Basit web arayüzü.
    templates/index.html dosyasını render eder.
    """
    return render_template("index.html")


# ------------------------------------------------------
#   YARDIMCI FONKSİYON
# ------------------------------------------------------
def strip_nii_suffix(name: str) -> str:
    """Dosya adından .nii veya .nii.gz uzantısını temizle."""
    if name.endswith(".nii.gz"):
        return name[: -len(".nii.gz")]
    if name.endswith(".nii"):
        return name[: -len(".nii")]
    return Path(name).stem


# ------------------------------------------------------
#   DEFACING METOD FONKSİYONLARI
# ------------------------------------------------------
def run_pydeface(input_path: Path, output_path: Path):
    """PyDeface ile defacing (çıktı: .nii)"""
    print("🔄 PyDeface çalıştırılıyor...")
    cmd = [
        "pydeface",
        str(input_path),
        "--outfile",
        str(output_path),
        "--force",
    ]
    print("▶️ PyDeface komutu:", " ".join(cmd))
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"✅ PyDeface başarılı → {output_path}")


def run_quickshear(input_path: Path, output_path: Path):
    """
    Quickshear ile defacing (FSL BET + quickshear)

    Konsolda çalışan akışla birebir:
      bet input.nii brain -m
      quickshear input.nii brain.nii.gz output_defaced.nii
    """
    print("🔄 Quickshear çalıştırılıyor...")

    base = strip_nii_suffix(input_path.name)
    brain_base = input_path.with_name(base + "_brain")  # 152_T1_1mm_brain

    # 1) BET (beyin segmentasyonu)
    bet_cmd = [
        "bet",
        str(input_path),
        str(brain_base),
        "-R",
        "-f",
        "0.5",
        "-g",
        "0",
        "-m",
    ]
    print("▶️ BET komutu:", " ".join(bet_cmd))

    try:
        bet_proc = subprocess.run(bet_cmd, check=True, capture_output=True)
        print("BET stdout:", bet_proc.stdout.decode() if bet_proc.stdout else "")
        print("BET stderr:", bet_proc.stderr.decode() if bet_proc.stderr else "")
    except subprocess.CalledProcessError as e:
        print("❌ BET hatası:", e.stderr.decode() if e.stderr else e)
        raise RuntimeError("BET maskesi/brain'i oluşturulamadı")

    brain_img_path = brain_base.with_suffix(".nii.gz")
    if not brain_img_path.exists():
        raise RuntimeError(f"BET brain çıktısı bulunamadı → {brain_img_path}")

    print(f"✅ BET brain çıktısı: {brain_img_path}")

    # 2) Quickshear (çıktı: output_path, .nii)
    qs_cmd = [
        "quickshear",
        str(input_path),
        str(brain_img_path),
        str(output_path),
    ]
    print("▶️ Quickshear komutu:", " ".join(qs_cmd))

    try:
        qs_proc = subprocess.run(qs_cmd, check=True, capture_output=True)
        print("Quickshear stdout:", qs_proc.stdout.decode() if qs_proc.stdout else "")
        print("Quickshear stderr:", qs_proc.stderr.decode() if qs_proc.stderr else "")
        print(f"✅ Quickshear başarılı → {output_path}")
    except subprocess.CalledProcessError as e:
        print("❌ Quickshear hatası:", e.stderr.decode() if e.stderr else e)
        raise RuntimeError("Quickshear defacing işlemi başarısız oldu")


def run_deepdefacer(input_path: Path, output_path: Path):
    """DeepDefacer (FSL CLI) ile defacing"""
    print("🔄 DeepDefacer çalıştırılıyor...")

    cmd = [
        "deepdefacer",
        "--input_file",
        str(input_path),
        "--defaced_output_path",
        str(output_path),
    ]

    print("▶️ DeepDefacer komutu:", " ".join(cmd))

    try:
        proc = subprocess.run(cmd, check=True, capture_output=True)
        print("DeepDefacer stdout:", proc.stdout.decode() if proc.stdout else "")
        print("DeepDefacer stderr:", proc.stderr.decode() if proc.stderr else "")
        print(f"✅ DeepDefacer başarılı → {output_path}")

    except FileNotFoundError:
        raise RuntimeError(
            "DeepDefacer bulunamadı! PATH ayarını yapman gerek.\n"
            'export PATH="/Users/basakesin/fsl/bin:$PATH"'
        )

    except subprocess.CalledProcessError as e:
        print("❌ DeepDefacer hata verdi!")
        print("Stdout:", e.stdout.decode() if e.stdout else "")
        print("Stderr:", e.stderr.decode() if e.stderr else "")
        raise RuntimeError("DeepDefacer CLI çalışırken hata oluştu.")


def run_mri_deface(input_path: Path, output_path: Path):
    """MRI Deface (FreeSurfer) ile defacing"""
    print("🔄 MRI Deface çalıştırılıyor...")
    cmd = [
        "mri_deface",
        str(input_path),
        str(output_path),
    ]
    print("▶️ MRI Deface komutu:", " ".join(cmd))
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"✅ MRI Deface başarılı → {output_path}")


def run_anonymi(input_path: Path, output_path: Path):
    """AnonyMI ile defacing"""
    print("🔄 AnonyMI çalıştırılıyor...")
    try:
        from anonymi import anonymize

        anonymize(str(input_path), str(output_path))
        print(f"✅ AnonyMI başarılı → {output_path}")
    except ImportError:
        cmd = [
            "anonymi",
            str(input_path),
            str(output_path),
        ]
        print("▶️ AnonyMI komutu:", " ".join(cmd))
        subprocess.run(cmd, check=True, capture_output=True)


# ------------------------------------------------------
#   /methods ENDPOINTİ
# ------------------------------------------------------
@app.route("/methods", methods=["GET"])
def get_methods():
    """Mevcut defacing metodlarını listele"""
    available_methods = []

    methods_to_check = {
        "pydeface": lambda: (
            subprocess.run(["which", "pydeface"], capture_output=True).returncode == 0
        ),
        "quickshear": lambda: (
            subprocess.run(["which", "quickshear"], capture_output=True).returncode == 0
        ),
        "deepdefacer": lambda: (
            subprocess.run(["which", "deepdefacer"], capture_output=True).returncode == 0
        ),
        "mri_deface": lambda: (
            subprocess.run(["which", "mri_deface"], capture_output=True).returncode == 0
        ),
        "anonymi": lambda: (
            subprocess.run(["which", "anonymi"], capture_output=True).returncode == 0
        ),
    }

    for method, check_func in methods_to_check.items():
        try:
            if check_func():
                available_methods.append(
                    {
                        "value": method,
                        "label": method.replace("_", " ").title(),
                        "description": SUPPORTED_METHODS[method],
                    }
                )
        except Exception:
            # Burada sessizce geçiyoruz; loglamak istersen print() ekleyebilirsin
            pass

    return jsonify({"methods": available_methods, "total": len(available_methods)})


# ------------------------------------------------------
#   /deface ENDPOINTİ
# ------------------------------------------------------
@app.route("/deface", methods=["POST"])
def deface():
    """MR görüntüsünü deface eden endpoint"""

    if "file" not in request.files:
        return jsonify({"error": "Dosya bulunamadı"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Dosya seçilmedi"}), 400

    method = request.form.get("method", "pydeface")
    if method not in SUPPORTED_METHODS:
        return jsonify({"error": f"Desteklenmeyen metod: {method}"}), 400

    print(f"📁 Gelen dosya: {file.filename}")
    print(f"🔧 Seçilen metod: {method}")

    if not (file.filename.endswith(".nii") or file.filename.endswith(".nii.gz")):
        return jsonify({"error": "Sadece .nii veya .nii.gz dosyaları desteklenir"}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Input'u geçici dizine kaydet
        input_path = temp_path / file.filename
        file.save(str(input_path))

        # Orijinal dosya adını içermeyen anonim isim
        output_filename = f"defaced_{method}.nii"
        output_path = temp_path / output_filename

        try:
            print(f"📥 Input dosya: {input_path}")
            print(f"📊 Dosya boyutu: {input_path.stat().st_size} bytes")

            method_functions = {
                "pydeface": run_pydeface,
                "quickshear": run_quickshear,
                "deepdefacer": run_deepdefacer,
                "mri_deface": run_mri_deface,
                "anonymi": run_anonymi,
            }

            method_func = method_functions.get(method)
            if not method_func:
                return jsonify({"error": f"Metod bulunamadı: {method}"}), 500

            # Tüm araçlar doğrudan output_path'e (.nii) yazacak
            method_func(input_path, output_path)

            print(f"✅ {method} başarılı")

            if not output_path.exists():
                print("❌ Output dosyası oluşturulamadı!")
                return jsonify({"error": "Output dosyası oluşturulamadı"}), 500

            print(f"📦 Output dosya: {output_path}")
            print(f"📊 Output boyutu: {output_path.stat().st_size} bytes")

            # Kullanıcıya doğrudan .nii ver
            return send_file(
                str(output_path),
                as_attachment=True,
                download_name=output_filename,
                mimetype="application/octet-stream",
                conditional=False,
            )

        except subprocess.CalledProcessError as e:
            print(f"❌ İşlem hatası: {e}")
            print(f"Stderr: {e.stderr.decode() if e.stderr else 'N/A'}")
            print(f"Stdout: {e.stdout.decode() if e.stdout else 'N/A'}")
            return (
                jsonify(
                    {
                        "error": f"{method} çalıştırılamadı",
                        "details": str(e),
                    }
                ),
                500,
            )
        except Exception as e:
            print(f"❌ Genel hata: {e}")
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500


# ------------------------------------------------------
#   /health ENDPOINTİ
# ------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    """API'nin çalışıp çalışmadığını kontrol et"""
    return jsonify(
        {
            "status": "ok",
            "message": "API çalışıyor",
            "supported_methods": list(SUPPORTED_METHODS.keys()),
        }
    )


# ------------------------------------------------------
#   MAIN
# ------------------------------------------------------
if __name__ == "__main__":
    print("🧠 MR Defacing API başlatılıyor...")
    print("📍 URL: http://localhost:5000")
    print("💡 Web arayüzü bu API'yi kullanacak (GET /)")
    print(f"🔧 Desteklenen metodlar: {', '.join(SUPPORTED_METHODS.keys())}")
    app.run(host="0.0.0.0", port=5000, debug=True)
