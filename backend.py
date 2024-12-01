from flask import Flask, jsonify, request
from flask_mqtt import Mqtt
import psycopg2
from datetime import datetime
import json

# Configuração do Flask
app = Flask(__name__)
    
# Configuração MQTT
app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'
app.config['MQTT_BROKER_PORT'] = 1883
# app.config['MQTT_USERNAME'] = 'Apontados'
# app.config['MQTT_PASSWORD'] = 'Apontados123'
app.config['MQTT_KEEPALIVE'] = 60
# app.config['MQTT_TLS_ENABLED'] = False

mqtt = Mqtt(app)

# Configuração do Banco de Dados PostgreSQL
DB_HOST = "dpg-cspqlnjv2p9s738u0560-a.oregon-postgres.render.com"
DB_NAME = "instituto_apontar"
DB_USER = "instituto_apontar_user"
DB_PASSWORD = "NqD6qhYNIm0X9TJvLPlsBTlRUIKIKClR"

def get_db_connection():
    """Estabelece uma conexão com o banco de dados PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port="5432"
        )
        print("[INFO] Conexão ao banco de dados estabelecida com sucesso.")
        return conn
    except Exception as e:
        print("[ERRO] Falha ao conectar ao banco de dados:", e)
        raise

def create_tables():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        create_cadastros_table = """
        CREATE TABLE IF NOT EXISTS cadastros (
            id SERIAL PRIMARY KEY,
            id_biometrico INT UNIQUE NOT NULL,
            nome VARCHAR(255),
            email VARCHAR(255),
            telefone VARCHAR(15),
            aluno BOOLEAN
        );
        """

        create_biometria_table = """
        CREATE TABLE IF NOT EXISTS biometria (
            id SERIAL PRIMARY KEY, 
            id_biometrico INT UNIQUE NOT NULL,
            data_cadastro TIMESTAMP DEFAULT NOW()
        );
        """

        create_acessos_table = """
        CREATE TABLE IF NOT EXISTS acessos (
            id SERIAL PRIMARY KEY,
            id_biometrico INT UNIQUE NOT NULL,
            nome VARCHAR(255),
            entrada TIMESTAMP NOT NULL,
            saida TIMESTAMP,
            tempo_permanencia INTERVAL
        );
        """

        cursor.execute(create_cadastros_table)
        cursor.execute(create_biometria_table)
        cursor.execute(create_acessos_table)

        conn.commit()
        cursor.close()
        conn.close()
        print("[INFO] Tabelas criadas com sucesso.")
    except Exception as e:
        print(f"[ERRO] Falha ao criar tabelas: {e}")

@mqtt.on_connect()
def on_connect(client, userdata, flags, rc):
    print(f"[INFO]Conectado ao MQTT com código {rc}")
    client.subscribe("instituto/biometria/cadastro")
    client.subscribe("instituto/biometria/acesso")

# Callback para mensagens MQTT
@mqtt.on_message()

def handle_mqtt_message(client, userdata, message):
    try:
        payload = message.payload.decode()
        data = json.loads(payload)

        print(f"[INFO] Mensagem recebida via MQTT: {data}")
        print(f"[INFO] Tópico: {message.topic}")

        if message.topic == "instituto/config/cadastro":
            id_biometrico = data.get("id_biometrico")
            nome = data.get("nome")

            if id_biometrico and nome:
                # Inserir na tabela cadastros
                conn = get_db_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO cadastros (id_biometrico, nome)
                    VALUES (%s, %s)
                    ON CONFLICT (id) DO UPDATE SET nome = EXCLUDED.nome;
                """, (id_biometrico, nome))
                conn.commit()

                cursor.close()
                conn.close()
                print(f"[INFO] Cadastro inserido/atualizado: ID={id_biometrico}, Nome={nome}")
            else:
                print("[ERRO] Dados inválidos no payload de cadastro.")

        if message.topic == "instituto/biometria/acesso":
            if "id" in data:
                id_biometrico = data["id"]
                print(f"[INFO] Processando ID: {id_biometrico}")

                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO acessos (id_biometrico, entrada)
                    VALUES (%s, %s);
                    """, (id_biometrico, datetime.now()))
                conn.commit()
                cursor.close()
                conn.close()
                print(f"[INFO] Acesso registrado para id {id_biometrico}.")
            else:
                print(f"[ERRO] Dados inválidos no tópico 'instituto/apontar/acesso'.")

        if message.topic == "instituto/biometria/cadastro":
            # Extrair informações do payload
            usuario_id = data.get("usuario_id")  # ID do usuário
            id_biometrico = data.get("id_biometrico")  # ID do leitor biométrico

            if usuario_id and id_biometrico:
                # Inserir no banco de dados
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO biometria (usuario_id, id_biometrico)
                    VALUES (%s, %s)
                    ON CONFLICT (id_biometrico) DO NOTHING;
                """, (usuario_id, id_biometrico))
                conn.commit()
                cursor.close()
                conn.close()
                print(f"[INFO] Biometria cadastrada para usuario_id {usuario_id} com id_biometrico {id_biometrico}.")
            else:
                print("[ERRO] Dados incompletos na mensagem de cadastro.")
        elif message.topic == "instituto/biometria/acesso":
            # Lógica existente para registrar acessos
            pass
    except Exception as e:
        print(f"[ERRO] Falha ao processar mensagem: {e}")

@app.route('/registro_acesso', methods=['GET'])
def get_acessos():
    """Retorna todos os acessos."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM acessos")
        acessos = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(acessos), 200
    except Exception as e:
        print(f"[ERRO] Falha ao buscar acessos: {e}")
        return jsonify({"status": "Erro", "message": "Falha ao buscar acessos"}), 500


@app.route('/registro_acesso', methods=['POST'])
def registrar_acesso():
    """Registra um acesso no banco de dados."""
    try:
        data = request.get_json()
        id_biometrico = data.get("id_biometrico")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO acessos (id_biometrico, entrada)
            VALUES (%s, %s);
            """, (id_biometrico, datetime.now()))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "Sucesso", "message": f"Acesso registrado para id {id_biometrico}"}), 201
    except Exception as e:
        print(f"[ERRO] Falha ao registrar acesso: {e}")
        return jsonify({"status": "Erro", "message": "Falha ao registrar acesso"}), 500

# Inicialização da aplicação Flask
if __name__ == "__main__":
    print("[INFO] Inicializando aplicação Flask...")
    # Criar as tabelas antes de iniciar o Flask
    create_tables()
    # Inicializar MQTT e executar o Flask
    mqtt.init_app(app)
    app.run(host='0.0.0.0', port=5000, debug=True)