# -*- coding: utf-8 -*-
import sys
import os

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.connection import init_db, execute_query, execute_one
from database.seed import run_seed
from utils.security import hash_password, verify_password

def run_tests():
    print("=== INICIANDO TESTES DO SISTEMA METROCON ===")
    
    init_db()
    run_seed()
    
    users = execute_query('SELECT * FROM users')
    print(f"[OK] Usuarios cadastrados: {len(users)}")
    assert len(users) >= 4, "Deveria ter pelo menos 4 usuarios cadastrados"
    
    admin = execute_one('SELECT * FROM users WHERE email = ?', ('admin@metrocon.com.br',))
    assert admin is not None, "Usuario admin nao encontrado"
    assert verify_password('Admin@123456', admin['password_hash'], admin['salt']), "Falha na verificacao de senha do admin"
    print("[OK] Autenticacao e Hashing PBKDF2: OK")
    
    projects = execute_query('SELECT * FROM projects')
    print(f"[OK] Projetos cadastrados: {len(projects)}")
    assert len(projects) >= 3, "Deveria ter pelo menos 3 projetos cadastrados"
    
    docs = execute_query('SELECT * FROM documents')
    print(f"[OK] Documentos cadastrados: {len(docs)}")
    assert len(docs) >= 10, "Deveria ter pelo menos 10 documentos cadastrados"
    
    logs = execute_query('SELECT * FROM daily_logs')
    print(f"[OK] Diarios de obra/processo: {len(logs)}")
    assert len(logs) >= 3, "Deveria ter pelo menos 3 diarios cadastrados"
    
    stages = execute_query('SELECT * FROM schedule_stages')
    print(f"[OK] Etapas de cronograma: {len(stages)}")
    assert len(stages) >= 10, "Deveria ter pelo menos 10 etapas cadastradas"
    
    meetings = execute_query('SELECT * FROM meeting_minutes')
    messages = execute_query('SELECT * FROM messages')
    print(f"[OK] Atas de reuniao: {len(meetings)} | Mensagens trocadas: {len(messages)}")
    
    audit = execute_query('SELECT * FROM audit_logs')
    print(f"[OK] Logs de auditoria LGPD: {len(audit)}")
    
    uploads_dir = os.path.join(BASE_DIR, 'uploads')
    files = os.listdir(uploads_dir)
    print(f"[OK] Arquivos no diretorio de uploads: {len(files)}")
    assert len(files) >= 10, "Deveria ter pelo menos 10 arquivos mock gerados"
    
    print("=== TODOS OS TESTES PASSARAM COM SUCESSO! ===")

if __name__ == '__main__':
    run_tests()
