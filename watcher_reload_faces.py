
import os
import time
import requests

FACES_DIR = "faces"
API_RELOAD_ENDPOINT = "http://localhost:5000/reload-faces"
INTERVALO_SEGUNDOS = 60

def listar_cpfs():
    return set(nome for nome in os.listdir(FACES_DIR) if os.path.isdir(os.path.join(FACES_DIR, nome)))

def recarregar_faces():
    try:
        response = requests.post(API_RELOAD_ENDPOINT)
        if response.status_code == 200:
            print(f"[RELOAD] ✅ Faces recarregadas: {response.json().get('quantidade_faces')} rostos")
        else:
            print(f"[RELOAD] ❌ Falha ao recarregar - Status: {response.status_code}")
    except Exception as e:
        print(f"[RELOAD] ❌ Erro ao tentar recarregar faces: {e}")

def monitorar_pastas():
    print("[MONITOR] 🕵️‍♂️ Iniciando monitoramento da pasta 'faces/'...")
    cpfs_anteriores = listar_cpfs()

    while True:
        time.sleep(INTERVALO_SEGUNDOS)
        cpfs_atuais = listar_cpfs()

        novos_cpfs = cpfs_atuais - cpfs_anteriores
        if novos_cpfs:
            print(f"[NOVO] 🆕 Novas pastas detectadas: {', '.join(novos_cpfs)}")
            recarregar_faces()
            cpfs_anteriores = cpfs_atuais
        else:
            print("[MONITOR] 🔄 Nenhuma nova pasta detectada.")

if __name__ == '__main__':
    monitorar_pastas()
