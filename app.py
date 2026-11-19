import asyncio
import os
import socket
import aiohttp
from flask import Flask, request, jsonify

app = Flask(__name__)

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Chuyển Giọng Nói Thành Văn Bản (Speech-to-Text)</title>
  <style>
    :root {
      --primary: #4f46e5;
      --primary-hover: #4338ca;
      --success: #059669;
      --success-hover: #047857;
      --danger: #dc2626;
      --danger-hover: #b91c1c;
      --card: #ffffff;
      --text: #0f172a;
      --muted: #64748b;
      --border: #e2e8f0;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: linear-gradient(135deg, #e0f2fe 0%, #f1f5f9 50%, #ede9fe 100%);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 20px;
    }

    .container {
      width: 100%;
      max-width: 820px;
      background: var(--card);
      border-radius: 20px;
      box-shadow: 0 20px 40px -15px rgba(15, 23, 42, 0.12);
      padding: 28px;
    }

    header {
      margin-bottom: 20px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border);
    }

    header h1 { font-size: 1.5rem; font-weight: 700; }
    header p { font-size: 0.9rem; color: var(--muted); margin-top: 4px; }

    .card {
      padding: 18px;
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: 14px;
      margin-bottom: 18px;
    }

    .card h2 {
      font-size: 1.02rem;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .card p.desc {
      font-size: 0.85rem;
      color: var(--muted);
      margin-bottom: 14px;
      line-height: 1.5;
    }

    .row {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
    }

    select, input[type="text"], input[type="password"] {
      padding: 10px 12px;
      border-radius: 10px;
      border: 1.5px solid var(--border);
      background: #fff;
      font-size: 0.92rem;
      color: var(--text);
    }

    select { flex: 1; min-width: 190px; }
    input[type="text"], input[type="password"] { width: 100%; }

    select:focus, input:focus, textarea:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
    }

    .btn {
      padding: 11px 18px;
      border: none;
      border-radius: 10px;
      font-size: 0.94rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      justify-content: center;
      align-items: center;
      gap: 8px;
      transition: transform 0.1s, opacity 0.2s, background-color 0.2s;
      min-width: 190px;
    }

    .btn:active:not(:disabled) { transform: scale(0.98); }
    .btn:disabled { opacity: 0.55; cursor: not-allowed; }

    .btn-primary { background: var(--primary); color: #fff; }
    .btn-primary:hover:not(:disabled) { background: var(--primary-hover); }

    .btn-success { background: var(--success); color: #fff; }
    .btn-success:hover:not(:disabled) { background: var(--success-hover); }

    .btn-danger { background: var(--danger); color: #fff; }
    .btn-danger:hover:not(:disabled) { background: var(--danger-hover); }

    .status-line {
      display: none;
      align-items: center;
      gap: 8px;
      margin-top: 12px;
      font-size: 0.88rem;
      font-weight: 600;
      color: var(--danger);
    }
    .status-line.active { display: flex; }

    .dot-pulse {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--danger);
      animation: pulse 1s infinite;
    }

    @keyframes pulse {
      0%, 100% { transform: scale(1); opacity: 1; }
      50% { transform: scale(1.45); opacity: 0.45; }
    }

    .interim-box {
      margin-top: 8px;
      font-size: 0.88rem;
      color: var(--muted);
      font-style: italic;
      min-height: 20px;
    }

    .stack { display: flex; flex-direction: column; gap: 10px; }

    input[type="file"] {
      padding: 10px;
      background: #fff;
      border: 1.5px dashed #cbd5e1;
      border-radius: 10px;
      font-size: 0.9rem;
      cursor: pointer;
    }

    .api-row { display: flex; gap: 8px; align-items: center; }

    .btn-chip {
      background: #f1f5f9;
      border: 1px solid var(--border);
      color: #334155;
      padding: 6px 11px;
      border-radius: 7px;
      font-size: 0.82rem;
      font-weight: 500;
      cursor: pointer;
    }
    .btn-chip:hover { background: #e2e8f0; }

    .hint {
      font-size: 0.8rem;
      color: var(--muted);
      line-height: 1.45;
    }
    .hint a { color: var(--primary); font-weight: 600; text-decoration: none; }
    .hint a:hover { text-decoration: underline; }

    .error-box {
      display: none;
      margin-top: 10px;
      padding: 10px 12px;
      background: #fef2f2;
      color: #b91c1c;
      border: 1px solid #fecaca;
      border-radius: 10px;
      font-size: 0.88rem;
    }

    .output-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 8px;
    }

    .output-header label { font-weight: 700; font-size: 0.98rem; }

    textarea {
      width: 100%;
      min-height: 180px;
      padding: 14px;
      border: 1.5px solid var(--border);
      border-radius: 12px;
      font-family: inherit;
      font-size: 1rem;
      line-height: 1.6;
      resize: vertical;
      color: var(--text);
    }

    .meta {
      margin-top: 6px;
      font-size: 0.82rem;
      color: var(--muted);
    }

    @media (max-width: 640px) {
      .container { padding: 18px; }
      .btn { width: 100%; }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>🎙️ Chuyển Giọng Nói Thành Văn Bản</h1>
        <p>Thu âm trực tiếp ra chữ ngay lập tức hoặc gỡ băng từ file âm thanh bằng AI</p>
      </div>
    </header>

    <!-- PHẦN 1: NÓI TRỰC TIẾP QUA MICRO (KHÔNG CẦN KEY) -->
    <div class="card">
      <h2>⚡ Cách 1: Nói trực tiếp ra chữ ngay (Miễn phí, không cần Key)</h2>
      <p class="desc">Bấm bắt đầu và nói vào micro, chữ sẽ hiện ra ngay theo giọng nói (tốt nhất trên Chrome, Cốc Cốc, Edge, Safari).</p>
      <div class="row">
        <select id="micLangSelect">
          <option value="vi-VN">🇻🇳 Tiếng Việt (vi-VN)</option>
          <option value="en-US">🇺🇸 Tiếng Anh (en-US)</option>
          <option value="ja-JP">🇯🇵 Tiếng Nhật (ja-JP)</option>
          <option value="ko-KR">🇰🇷 Tiếng Hàn (ko-KR)</option>
          <option value="zh-CN">🇨🇳 Tiếng Trung (zh-CN)</option>
          <option value="fr-FR">🇫🇷 Tiếng Pháp (fr-FR)</option>
        </select>
        <button type="button" id="micToggleBtn" class="btn btn-primary">🎙️ Bắt đầu nói</button>
      </div>

      <div id="micStatus" class="status-line">
        <span class="dot-pulse"></span>
        <span>Đang nghe... Hãy nói vào micro</span>
      </div>
      <div id="interimText" class="interim-box"></div>
      <div id="micError" class="error-box"></div>
    </div>

    <!-- PHẦN 2: AI WHISPER (GHI ÂM HOẶC TẢI FILE LÊN) -->
    <div class="card">
      <h2>🤖 Cách 2: Gỡ băng chính xác cao bằng AI (Ghi âm hoặc Tải file MP3/WAV/M4A)</h2>
      <p class="desc">Tự động thêm dấu chấm phẩy chuẩn xác. Bạn có thể ghi âm trực tiếp hoặc chọn file có sẵn (tối đa 25MB).</p>

      <div class="stack">
        <div class="row">
          <select id="whisperLangSelect">
            <option value="vi">🇻🇳 Tiếng Việt</option>
            <option value="auto">🌐 Tự nhận diện ngôn ngữ</option>
            <option value="en">🇺🇸 Tiếng Anh</option>
            <option value="ja">🇯🇵 Tiếng Nhật</option>
            <option value="ko">🇰🇷 Tiếng Hàn</option>
            <option value="zh">🇨🇳 Tiếng Trung</option>
          </select>
          <button type="button" id="aiRecordBtn" class="btn btn-danger">🔴 Ghi âm gửi AI</button>
        </div>

        <div id="aiRecStatus" class="status-line">
          <span class="dot-pulse"></span>
          <span id="aiRecTimer">Đang ghi âm: 00:00</span>
        </div>

        <div class="row">
          <input type="file" id="audioFileInput" style="flex: 1;" accept="audio/*,video/mp4,.mp3,.wav,.m4a,.ogg,.webm,.flac" />
          <button type="button" id="transcribeFileBtn" class="btn btn-success">✨ Dịch file thành chữ</button>
        </div>

        <div class="api-row">
          <input type="password" id="groqKeyInput" placeholder="Groq API Key miễn phí (gsk_...) — bỏ trống nếu chủ web đã cài sẵn" />
          <button type="button" class="btn-chip" id="toggleKeyBtn" style="padding: 10px 12px;">👁️</button>
        </div>

        <p class="hint">
          💡 Lấy key miễn phí trong 30 giây (không cần thẻ ngân hàng): vào <a href="https://console.groq.com/keys" target="_blank" rel="noopener">console.groq.com/keys</a> → Create API Key → dán vào ô trên.
        </p>
      </div>
      <div id="aiError" class="error-box"></div>
    </div>

    <!-- KẾT QUẢ VĂN BẢN -->
    <div class="output-header">
      <label for="sttOutput">📝 Văn bản kết quả</label>
      <div class="row" style="gap: 6px;">
        <button type="button" class="btn-chip" id="copyBtn">📋 Sao chép</button>
        <button type="button" class="btn-chip" id="downloadTxtBtn">💾 Tải .TXT</button>
        <button type="button" class="btn-chip" id="clearBtn">🗑 Xóa hết</button>
      </div>
    </div>
    <textarea id="sttOutput" placeholder="Văn bản sau khi chuyển đổi sẽ xuất hiện tại đây... Bạn có thể chỉnh sửa tự do trước khi sao chép hoặc tải về."></textarea>
    <div class="meta" id="sttMeta">0 ký tự • 0 từ</div>
  </div>

  <script>
    const sttOutput = document.getElementById('sttOutput');
    const sttMeta = document.getElementById('sttMeta');

    function updateMeta() {
      const val = sttOutput.value.trim();
      const words = val ? val.split(/\s+/).length : 0;
      sttMeta.textContent = `${sttOutput.value.length} ký tự • ${words} từ`;
    }
    sttOutput.addEventListener('input', updateMeta);

    function appendResultText(newText) {
      if (!newText || !newText.trim()) return;
      const cur = sttOutput.value;
      const sep = cur && !cur.endsWith(' ') && !cur.endsWith('\n') ? '\n' : '';
      sttOutput.value = cur + sep + newText.trim();
      updateMeta();
    }

    // ==================== CÁCH 1: WEB SPEECH API ====================
    const micLangSelect = document.getElementById('micLangSelect');
    const micToggleBtn = document.getElementById('micToggleBtn');
    const micStatus = document.getElementById('micStatus');
    const interimText = document.getElementById('interimText');
    const micError = document.getElementById('micError');

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let isLiveRecording = false;

    if (!SpeechRecognition) {
      micToggleBtn.disabled = true;
      micError.style.display = 'block';
      micError.textContent = '⚠️ Trình duyệt này không hỗ trợ nhận diện giọng nói trực tiếp. Hãy dùng Chrome, Cốc Cốc, Edge, Safari hoặc dùng Cách 2 bên dưới.';
    } else {
      recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;

      recognition.onresult = (event) => {
        let interim = '';
        let finalChunk = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalChunk += transcript + ' ';
          } else {
            interim += transcript;
          }
        }
        if (finalChunk) {
          const cur = sttOutput.value;
          const sep = cur && !cur.endsWith(' ') && !cur.endsWith('\n') ? ' ' : '';
          sttOutput.value = cur + sep + finalChunk.trim();
          updateMeta();
        }
        interimText.textContent = interim ? `Đang nghe: "${interim}"` : '';
      };

      recognition.onerror = (event) => {
        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
          isLiveRecording = false;
          updateLiveMicUI();
          micError.style.display = 'block';
          micError.textContent = '⚠️ Chưa cấp quyền Micro. Hãy bấm biểu tượng ổ khóa trên thanh địa chỉ và cho phép Micro.';
        }
      };

      recognition.onend = () => {
        if (isLiveRecording) {
          try { recognition.start(); } catch (e) { isLiveRecording = false; updateLiveMicUI(); }
        } else {
          interimText.textContent = '';
          updateLiveMicUI();
        }
      };
    }

    function updateLiveMicUI() {
      if (isLiveRecording) {
        micToggleBtn.textContent = '⏹ Dừng nói';
        micToggleBtn.className = 'btn btn-danger';
        micStatus.classList.add('active');
        micError.style.display = 'none';
      } else {
        micToggleBtn.textContent = '🎙️ Bắt đầu nói';
        micToggleBtn.className = 'btn btn-primary';
        micStatus.classList.remove('active');
      }
    }

    micToggleBtn.addEventListener('click', () => {
      if (!recognition) return;
      if (isLiveRecording) {
        isLiveRecording = false;
        recognition.stop();
        updateLiveMicUI();
      } else {
        recognition.lang = micLangSelect.value;
        isLiveRecording = true;
        try {
          recognition.start();
          updateLiveMicUI();
        } catch (e) {
          isLiveRecording = false;
          updateLiveMicUI();
        }
      }
    });

    // ==================== CÁCH 2: GROQ WHISPER AI ====================
    const whisperLangSelect = document.getElementById('whisperLangSelect');
    const aiRecordBtn = document.getElementById('aiRecordBtn');
    const aiRecStatus = document.getElementById('aiRecStatus');
    const aiRecTimer = document.getElementById('aiRecTimer');
    const audioFileInput = document.getElementById('audioFileInput');
    const transcribeFileBtn = document.getElementById('transcribeFileBtn');
    const groqKeyInput = document.getElementById('groqKeyInput');
    const toggleKeyBtn = document.getElementById('toggleKeyBtn');
    const aiError = document.getElementById('aiError');

    const savedKey = localStorage.getItem('groq_api_key');
    if (savedKey) groqKeyInput.value = savedKey;
    groqKeyInput.addEventListener('input', () => {
      localStorage.setItem('groq_api_key', groqKeyInput.value.trim());
    });
    toggleKeyBtn.addEventListener('click', () => {
      groqKeyInput.type = groqKeyInput.type === 'password' ? 'text' : 'password';
    });

    async function sendAudioToServer(fileOrBlob, filename) {
      aiError.style.display = 'none';
      if (fileOrBlob.size > 25 * 1024 * 1024) {
        aiError.style.display = 'block';
        aiError.textContent = '⚠️ File âm thanh vượt quá 25MB.';
        return;
      }

      const formData = new FormData();
      formData.append('audio', fileOrBlob, filename);
      formData.append('language', whisperLangSelect.value);
      formData.append('api_key', groqKeyInput.value.trim());

      transcribeFileBtn.disabled = true;
      aiRecordBtn.disabled = true;
      transcribeFileBtn.textContent = '⏳ AI đang xử lý...';

      try {
        const res = await fetch('/api/stt', { method: 'POST', body: formData });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Không thể chuyển đổi âm thanh.');
        appendResultText(data.text);
      } catch (err) {
        aiError.style.display = 'block';
        aiError.textContent = '⚠️ ' + err.message;
      } finally {
        transcribeFileBtn.disabled = false;
        aiRecordBtn.disabled = false;
        transcribeFileBtn.textContent = '✨ Dịch file thành chữ';
      }
    }

    transcribeFileBtn.addEventListener('click', () => {
      const file = audioFileInput.files[0];
      if (!file) {
        aiError.style.display = 'block';
        aiError.textContent = '⚠️ Vui lòng chọn một file âm thanh trước!';
        return;
      }
      sendAudioToServer(file, file.name);
    });

    // Ghi âm trực tiếp thành file gửi Whisper
    let mediaRecorder = null;
    let aiStream = null;
    let audioChunks = [];
    let timerInterval = null;
    let secondsElapsed = 0;

    function formatTime(sec) {
      const m = String(Math.floor(sec / 60)).padStart(2, '0');
      const s = String(sec % 60).padStart(2, '0');
      return `${m}:${s}`;
    }

    aiRecordBtn.addEventListener('click', async () => {
      aiError.style.display = 'none';
      if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        return;
      }

      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        aiError.style.display = 'block';
        aiError.textContent = '⚠️ Trình duyệt không hỗ trợ ghi âm.';
        return;
      }

      try {
        aiStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioChunks = [];
        mediaRecorder = new MediaRecorder(aiStream);

        mediaRecorder.ondataavailable = (e) => {
          if (e.data && e.data.size > 0) audioChunks.push(e.data);
        };

        mediaRecorder.onstop = async () => {
          clearInterval(timerInterval);
          aiRecStatus.classList.remove('active');
          aiRecordBtn.textContent = '🔴 Ghi âm gửi AI';
          aiStream.getTracks().forEach(t => t.stop());

          const mime = mediaRecorder.mimeType || 'audio/webm';
          const ext = mime.includes('mp4') ? 'mp4' : (mime.includes('ogg') ? 'ogg' : 'webm');
          const blob = new Blob(audioChunks, { type: mime });
          await sendAudioToServer(blob, `recording.${ext}`);
        };

        mediaRecorder.start();
        secondsElapsed = 0;
        aiRecTimer.textContent = 'Đang ghi âm: 00:00';
        aiRecStatus.classList.add('active');
        aiRecordBtn.textContent = '⏹ Dừng & Dịch ngay';
        timerInterval = setInterval(() => {
          secondsElapsed++;
          aiRecTimer.textContent = `Đang ghi âm: ${formatTime(secondsElapsed)}`;
        }, 1000);
      } catch (err) {
        aiError.style.display = 'block';
        aiError.textContent = '⚠️ Không thể truy cập Micro: ' + err.message;
      }
    });

    // ==================== TIỆN ÍCH KẾT QUẢ ====================
    document.getElementById('copyBtn').addEventListener('click', async () => {
      if (!sttOutput.value.trim()) return;
      await navigator.clipboard.writeText(sttOutput.value);
      const btn = document.getElementById('copyBtn');
      const old = btn.textContent;
      btn.textContent = '✅ Đã chép!';
      setTimeout(() => { btn.textContent = old; }, 1500);
    });

    document.getElementById('downloadTxtBtn').addEventListener('click', () => {
      if (!sttOutput.value.trim()) return alert('Chưa có văn bản để tải!');
      const blob = new Blob([sttOutput.value], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `van-ban-${Date.now()}.txt`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    });

    document.getElementById('clearBtn').addEventListener('click', () => {
      sttOutput.value = '';
      updateMeta();
    });
  </script>
</body>
</html>
"""


@app.route("/")
def index():
    return HTML_PAGE


async def transcribe_with_groq(file_bytes: bytes, filename: str, content_type: str, api_key: str, language: str) -> str:
    form = aiohttp.FormData()
    form.add_field(
        "file",
        file_bytes,
        filename=filename or "audio.mp3",
        content_type=content_type or "audio/mpeg",
    )
    form.add_field("model", "whisper-large-v3-turbo")
    if language and language != "auto":
        form.add_field("language", language)
    form.add_field("response_format", "json")

    headers = {"Authorization": f"Bearer {api_key}"}
    timeout = aiohttp.ClientTimeout(total=120)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers=headers,
            data=form,
        ) as resp:
            resp_json = await resp.json(content_type=None)
            if resp.status != 200:
                err_msg = (resp_json.get("error") or {}).get("message") or f"Mã lỗi HTTP {resp.status}"
                raise RuntimeError(err_msg)
            return (resp_json.get("text") or "").strip()


@app.route("/api/stt", methods=["POST"])
def speech_to_text():
    if "audio" not in request.files:
        return jsonify({"error": "Không tìm thấy file âm thanh gửi lên."}), 400

    audio_file = request.files["audio"]
    api_key = (request.form.get("api_key") or os.environ.get("GROQ_API_KEY") or "").strip()
    language = (request.form.get("language") or "vi").strip()

    if not api_key:
        return jsonify({
            "error": "Chưa có Groq API Key. Bạn hãy lấy key miễn phí tại console.groq.com/keys rồi dán vào ô Key."
        }), 400

    file_bytes = audio_file.read()
    if not file_bytes:
        return jsonify({"error": "File âm thanh bị rỗng."}), 400

    if len(file_bytes) > 25 * 1024 * 1024:
        return jsonify({"error": "File vượt quá giới hạn 25MB."}), 400

    try:
        text = asyncio.run(
            transcribe_with_groq(
                file_bytes=file_bytes,
                filename=audio_file.filename,
                content_type=audio_file.content_type,
                api_key=api_key,
                language=language,
            )
        )
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": f"Lỗi khi chuyển đổi âm thanh: {str(e)}"}), 500


def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    lan_ip = get_lan_ip()
    print(f"Mở trên máy này: http://127.0.0.1:{port}")
    print(f"Mở trên mạng LAN: http://{lan_ip}:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)