from flask import Flask, request, jsonify
import face_recognition
import numpy as np
import os
import base64
from PIL import Image
from io import BytesIO

app = Flask(__name__)

# Carregar todas as imagens conhecidas
def carregar_faces_conhecidas():
    faces_conhecidas = []
    nomes_conhecidos = []

    caminho_base = 'faces'
    for cpf in os.listdir(caminho_base):
        caminho_cpf = os.path.join(caminho_base, cpf)
        if os.path.isdir(caminho_cpf):
            for imagem_nome in os.listdir(caminho_cpf):
                caminho_imagem = os.path.join(caminho_cpf, imagem_nome)
                imagem = face_recognition.load_image_file(caminho_imagem)
                codigos = face_recognition.face_encodings(imagem)
                if codigos:
                    faces_conhecidas.append(codigos[0])
                    nomes_conhecidos.append(cpf)
    return faces_conhecidas, nomes_conhecidos

# Carrega uma vez ao iniciar
FACES, CPFS = carregar_faces_conhecidas()

@app.route('/verificar', methods=['POST'])
def verificar():
    data = request.get_json()
    imagem_base64 = data.get("imagem")

    if not imagem_base64:
        return jsonify({"erro": "Imagem não enviada"}), 400

    try:
        # Decodifica base64
        imagem_bytes = base64.b64decode(imagem_base64)
        imagem = Image.open(BytesIO(imagem_bytes)).convert('RGB')
        imagem_np = np.array(imagem)

        # Detecta e codifica
        rostos = face_recognition.face_encodings(imagem_np)

        if not rostos:
            return jsonify({"erro": "Nenhum rosto detectado"}), 400

        rosto_desconhecido = rostos[0]
        resultados = face_recognition.compare_faces(FACES, rosto_desconhecido)

        if True in resultados:
            index = resultados.index(True)
            cpf_reconhecido = CPFS[index]
            return jsonify({"status": "ok", "nome": cpf_reconhecido})
        else:
            return jsonify({"erro": "Face não reconhecida"}), 404

    except Exception as e:
        return jsonify({"erro": f"Erro ao processar imagem: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
