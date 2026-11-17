import os
import sys
import re
import json
import requests
from pathlib import Path

# ==============================
# KONFIGURASI
# ==============================
API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL = os.environ.get("OPENROUTER_MODEL") or "qwen/qwen-2.5-coder-32b-instruct"
TARGET_FILE = os.environ.get("TARGET_FILE")
PROMPT_FILE = Path("prompt.txt")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Batas ukuran file yang dikirim ke AI (biar nggak boncos token)
MAX_FILE_CHARS = 20000


# ==============================
# FUNGSI: PANGGIL OPENROUTER
# ==============================
def call_openrouter(system_prompt, user_prompt):
    if not API_KEY:
        print("❌ ERROR: OPENROUTER_API_KEY tidak diset di secrets!")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "GitHub Actions AI Modifier",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }

    print(f"📡 Request ke OpenRouter | model: {MODEL}")
    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=300)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        print(f"✅ Respons diterima ({len(content)} karakter)")
        return content
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Response: {resp.text}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


# ==============================
# FUNGSI: BERSIHKAN OUTPUT AI
# ==============================
def clean_ai_output(text):
    """
    AI kadang masih nyelipin blok markdown ```language ... ``` 
    walau udah disuruh jangan. Fungsi ini buang wrapper itu.
    """
    text = text.strip()
    # Kalau ada blok markdown di awal
    md_pattern = r"^```[\w\-]*\n(.*?)\n```$"
    match = re.match(md_pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


# ==============================
# FUNGSI: BACA FILE TARGET
# ==============================
def read_target_file(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"❌ File target '{filepath}' tidak ditemukan di repo!")
        print("💡 Pastikan path-nya benar, misal: src/main.py atau index.html")
        sys.exit(1)

    if not path.is_file():
        print(f"❌ '{filepath}' bukan file (mungkin folder?)")
        sys.exit(1)

    content = path.read_text(encoding="utf-8")

    if len(content) > MAX_FILE_CHARS:
        print(f"⚠️ File terlalu besar ({len(content)} char). Dipotong ke {MAX_FILE_CHARS} char.")
        content = content[:MAX_FILE_CHARS] + "\n\n# ... [FILE DIPOTONG KARENA TERLALU PANJANG] ..."

    print(f"📖 File target dibaca: {filepath} ({len(content)} karakter)")
    return content


# ==============================
# FUNGSI UTAMA: MODIFIKASI FILE
# ==============================
def modify_file(filepath, instruction):
    original_code = read_target_file(filepath)

    system_prompt = (
        "Kamu adalah coding agent ahli. Tugasmu memodifikasi kode yang diberikan "
        "sesuai instruksi user. ATURAN KETAT:\n"
        "1. Keluarkan HANYA kode lengkap hasil modifikasi.\n"
        "2. JANGAN pakai blok markdown ```...```.\n"
        "3. JANGAN tambahkan penjelasan, komentar pembuka, atau apapun di luar kode.\n"
        "4. Pastikan kode tetap valid dan bisa dijalankan.\n"
        "5. Pertahankan style/bahasa pemrograman dari kode asli.\n"
        "6. Jangan hapus fitur yang tidak diminta untuk dihapus."
    )

    user_prompt = f"""INSTRUKSI MODIFIKASI:
{instruction}

KODE ASLI ({filepath}):
{original_code}

Sekarang keluarkan kode lengkap hasil modifikasi:"""

    print(f"🤖 Minta AI modifikasi '{filepath}'...")
    ai_output = call_openrouter(system_prompt, user_prompt)
    new_code = clean_ai_output(ai_output)

    if len(new_code) < 20:
        print(f"⚠️ Output AI terlalu pendek ({len(new_code)} char), curiga gagal. Skip.")
        sys.exit(1)

    # Simpan
    Path(filepath).write_text(new_code, encoding="utf-8")
    print(f"✅ File '{filepath}' berhasil dimodifikasi ({len(new_code)} karakter)")


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AI CODE MODIFIER — START")
    print("=" * 60)

    # Validasi input
    if not TARGET_FILE:
        print("❌ TARGET_FILE tidak diset! Isi input 'target_file' di workflow.")
        sys.exit(1)

    if not PROMPT_FILE.exists():
        print("❌ prompt.txt tidak ditemukan di root repo!")
        print("💡 Bikin file prompt.txt di root repo, isinya instruksi buat AI.")
        sys.exit(1)

    instruction = PROMPT_FILE.read_text(encoding="utf-8").strip()
    if not instruction:
        print("❌ prompt.txt kosong!")
        sys.exit(1)

    print(f"📝 Prompt: {instruction[:150]}{'...' if len(instruction) > 150 else ''}")
    print(f"🎯 Target file: {TARGET_FILE}")
    print("-" * 60)

    # Gas modifikasi
    modify_file(TARGET_FILE, instruction)

    print("=" * 60)
    print("🎉 SELESAI")
    print("=" * 60)
