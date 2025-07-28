import os
import urllib.request

os.makedirs("models", exist_ok=True)

MODELOS = {
    "shape_predictor_68_face_landmarks.dat":
    "https://github.com/ageitgey/face_recognition_models/raw/master/face_recognition_models/models/shape_predictor_68_face_landmarks.dat",

    "dlib_face_recognition_resnet_model_v1.dat":
    "https://github.com/ageitgey/face_recognition_models/raw/master/face_recognition_models/models/dlib_face_recognition_resnet_model_v1.dat"
}

for nome_arquivo, url in MODELOS.items():
    caminho = os.path.join("models", nome_arquivo)
    if not os.path.exists(caminho):
        print(f"Baixando {nome_arquivo}...")
        urllib.request.urlretrieve(url, caminho)
        print(f"{nome_arquivo} salvo em {caminho}")
    else:
        print(f"{nome_arquivo} já existe.")
