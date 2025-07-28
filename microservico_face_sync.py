
import os
import requests
import threading
import time
import signal
import sys

# === CONFIGURAÇÕES ===
URL = 'https://systex.com.br/systex-face/public/api/listar-fotos'
DESTINO = 'faces'
INTERVALO_SEGUNDOS = 60
TOKEN = '4|rseZSYQy2UPX74dRBh2MAU0ynGqmUr6fs3R8DqmYa75c07c7'

# === CONTROLE DE EXECUÇÃO ===
parar_evento = threading.Event()

def baixar_imagem(url, caminho_destino):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Accept': 'image/png,image/*;q=0.8,*/*;q=0.5'
        }

        r = requests.get(url, timeout=10, headers=headers)
        r.raise_for_status()

        with open(caminho_destino, 'wb') as f:
            f.write(r.content)
    except Exception as e:
        print(f"[ERRO] Falha ao baixar {url}: {e}")


def sincronizar():
    if parar_evento.is_set():
        return

    print(f"[INFO] ⏳ Sincronizando às {time.strftime('%H:%M:%S')}...")

    try:
        headers = {
            'Authorization': f'Bearer {TOKEN}',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }

        response = requests.get(URL, headers=headers)

        print("[DEBUG] Status Code:", response.status_code)
        print("[DEBUG] Headers:", response.headers)
        print("[DEBUG] Content:", response.text[:300])  # Limita preview

        response.raise_for_status()
        dados = response.json()

        if "fotos" not in dados:
            print("[ERRO] Estrutura inesperada na resposta da API.")
            return

        fotos_servidor = dados['fotos']
        cpfs_servidor = set(fotos_servidor.keys())
        cpfs_locais = set(os.listdir(DESTINO)) if os.path.exists(DESTINO) else set()

        # Cria diretório base, se não existir
        os.makedirs(DESTINO, exist_ok=True)

        # Identifica novos CPFs
        novos_cpfs = cpfs_servidor - cpfs_locais
        if not novos_cpfs:
            print("[INFO] Nenhuma nova pasta de CPF detectada.")
        else:
            for cpf in novos_cpfs:
                print(f"[NOVO] 📥 Baixando fotos do CPF: {cpf}")
                pasta_cpf = os.path.join(DESTINO, cpf)
                os.makedirs(pasta_cpf, exist_ok=True)

                for i, url_foto in enumerate(fotos_servidor[cpf]):
                    nome_arquivo = f"{i+1}.jpg"
                    caminho_arquivo = os.path.join(pasta_cpf, nome_arquivo)
                    baixar_imagem(url_foto, caminho_arquivo)

        print("[OK] ✅ Sincronização finalizada.")
    except Exception as e:
        print(f"[FALHA] ❌ Erro na sincronização: {e}")

def ciclo_de_sincronizacao():
    while not parar_evento.is_set():
        sincronizar()
        for _ in range(INTERVALO_SEGUNDOS):
            if parar_evento.is_set():
                break
            time.sleep(1)

def encerrar_graciosamente(sig, frame):
    print("\n[ENCERRANDO] 🛑 Interrupção recebida. Finalizando microserviço...")
    parar_evento.set()
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, encerrar_graciosamente)
    signal.signal(signal.SIGTERM, encerrar_graciosamente)

    print("[BOOT] 🚀 Microserviço de sincronização iniciado...")

    thread = threading.Thread(target=ciclo_de_sincronizacao, daemon=True)
    thread.start()

    # Mantém o script vivo até que seja interrompido
    while not parar_evento.is_set():
        time.sleep(1)
