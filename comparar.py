
import os
import io
import base64
import numpy as np
from flask import Flask, request, jsonify
from PIL import Image
import face_recognition
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# === ARMAZENAMENTO EM MEMÓRIA ===
encodings_memoria = []
nomes_memoria = []

def decode_base64_image(base64_string):
    """Remove prefixo data:image/... e decodifica"""
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    image_data = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(image_data))

def carregar_faces():
    encodings = []
    nomes = []
    base_dir = "faces"

    for cpf in os.listdir(base_dir):
        caminho_cpf = os.path.join(base_dir, cpf)

        if not os.path.isdir(caminho_cpf):
            continue

        for filename in os.listdir(caminho_cpf):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                path = os.path.join(caminho_cpf, filename)
                imagem = face_recognition.load_image_file(path)
                face_enc = face_recognition.face_encodings(imagem)
                if face_enc:
                    encodings.append(face_enc[0])
                    nomes.append(cpf)
                else:
                    print(f"[AVISO] Nenhum rosto detectado em: {path}")
    return encodings, nomes

@app.route('/reload-faces', methods=['POST'])
def recarregar_faces():
    global encodings_memoria, nomes_memoria
    encodings_memoria, nomes_memoria = carregar_faces()
    return jsonify({"status": "ok", "quantidade_faces": len(encodings_memoria)})

@app.route('/comparar', methods=['POST'])
def comparar():
    dados = request.get_json()

    if 'imagem_base64' not in dados:
        return jsonify({"erro": "Campo 'imagem_base64' é obrigatório"}), 400

    try:
        imagem = decode_base64_image(dados['imagem_base64'])
        imagem_np = np.array(imagem)

        encodings_recebidos = face_recognition.face_encodings(imagem_np)
        if not encodings_recebidos:
            return jsonify({"erro": "Nenhum rosto detectado na imagem enviada", "match": False}), 400

        encoding_recebido = encodings_recebidos[0]

        if not encodings_memoria:
            return jsonify({"erro": "Nenhuma face carregada na memória", "match": False}), 400

        resultados = face_recognition.compare_faces(encodings_memoria, encoding_recebido)
        distancias = face_recognition.face_distance(encodings_memoria, encoding_recebido)

        melhor_indice = np.argmin(distancias)
        melhor_distancia = distancias[melhor_indice]

        if resultados[melhor_indice]:
            return jsonify({
                "match": True,
                "pessoa": nomes_memoria[melhor_indice],
                "distancia": float(melhor_distancia),
                "avaliadas": nomes_memoria,
                "todas_distancias": distancias.tolist()
            })
        else:
            return jsonify({
                "match": False,
                "mensagem": "Rosto detectado, mas não foi reconhecido.",
                "avaliadas": nomes_memoria,
                "todas_distancias": distancias.tolist()
            })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    print("[BOOT] 🔁 Carregando rostos na memória...")
    encodings_memoria, nomes_memoria = carregar_faces()
    print(f"[OK] {len(encodings_memoria)} rostos carregados.")
    app.run(host="0.0.0.0", port=5000)
