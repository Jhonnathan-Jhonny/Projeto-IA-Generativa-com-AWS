#Lambda utilizado no console AWS

import json
import urllib3
import boto3

http = urllib3.PoolManager()
TELEGRAM_TOKEN = "8179843366:AAExdCmFNsFI2Ym83IWeGlkLm50ypSTZTX4"
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
ec2_client = boto3.client("ec2")

def get_ec2_ip(instance_id="i-0187f2439bb3a9c83"):
    reservations = ec2_client.describe_instances(InstanceIds=[instance_id])
    instance = reservations["Reservations"][0]["Instances"][0]
    return instance.get("PublicIpAddress")

def lambda_handler(event, context):
    EC2_IP = get_ec2_ip()
    EC2_URL = f"http://{EC2_IP}/"
    
    try:
        # 1. Parse do body
        body = event
        if 'body' in event and isinstance(event['body'], str):
            try:
                body = json.loads(event['body'])
            except json.JSONDecodeError:
                body = event['body']
        
        # 2. Extrai dados do formato Telegram
        if isinstance(body, dict):
            message = body.get('message', {})
            text = message.get('text', '').strip()
            chat_id = message.get('chat', {}).get('id')
        else:
            text = str(body)
            chat_id = 123456789
        
        print(f"Pergunta recebida: {text}")
        
        if not text or text == '{}':
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Pergunta é obrigatória'})
            }
        
        # 3. Envia para sua EC2
        try:
            ec2_response = http.request(
                "POST",
                EC2_URL,
                body=json.dumps({"question": text}),
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            ec2_data = json.loads(ec2_response.data.decode('utf-8'))
            bot_response = ec2_data.get('response', 'Desculpe, não consegui processar sua pergunta.')

            print(f"Resposta gerada: {bot_response}")
            
        except Exception as ec2_error:
            bot_response = f"Erro ao conectar com EC2: {str(ec2_error)}"
        
        # 4. Se tem chat_id, envia para Telegram (usando urllib3)
        if chat_id:
            send_telegram_message(chat_id, bot_response)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'success',
                'response': bot_response,
                'processed_text': text
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Erro interno: {str(e)}'})
        }

def send_telegram_message(chat_id, text):
    """Envia mensagem para o Telegram usando urllib3"""
    try:
        url = f"{TELEGRAM_URL}/sendMessage"
        payload = json.dumps({
            'chat_id': chat_id,
            'text': text[:4096],  # Telegram limita a 4096 caracteres
            'parse_mode': 'HTML'
        })
        
        response = http.request(
            "POST",
            url,
            body=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        return json.loads(response.data.decode('utf-8'))
        
    except Exception as e:
        print(f"Erro ao enviar para Telegram: {e}")
        return None