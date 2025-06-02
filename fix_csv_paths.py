#!/usr/bin/env python3
"""
Script para corrigir os paths dos scripts no group_summary.csv
de /pages/../summary.py para src/whatsapp_manager/core/summary.py
"""

import os
import pandas as pd

# Define project root
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
CSV_PATH = os.path.join(PROJECT_ROOT, "group_summary.csv")
CORRECT_SCRIPT_PATH = os.path.join(PROJECT_ROOT, "src", "whatsapp_manager", "core", "summary.py")

def fix_csv_script_paths():
    """
    Corrige os paths dos scripts no CSV que apontam para a estrutura antiga
    """
    try:
        # Lê o CSV
        df = pd.read_csv(CSV_PATH)
        print(f"📊 Lendo CSV: {CSV_PATH}")
        print(f"📝 Total de registros: {len(df)}")
        
        # Conta quantos registros têm paths incorretos
        incorrect_paths = df['script'].str.contains('/pages/../summary.py', na=False).sum()
        print(f"🔍 Registros com paths incorretos: {incorrect_paths}")
        
        if incorrect_paths > 0:
            # Substitui os paths incorretos pelo path correto
            df['script'] = df['script'].str.replace(
                r'.*?/pages/../summary\.py', 
                CORRECT_SCRIPT_PATH, 
                regex=True
            )
            
            # Salva o CSV corrigido
            df.to_csv(CSV_PATH, index=False)
            print(f"✅ CSV corrigido! Paths atualizados para: {CORRECT_SCRIPT_PATH}")
            
            # Verifica se a correção funcionou
            df_check = pd.read_csv(CSV_PATH)
            remaining_incorrect = df_check['script'].str.contains('/pages/../summary.py', na=False).sum()
            print(f"🔎 Paths incorretos restantes: {remaining_incorrect}")
            
            if remaining_incorrect == 0:
                print("🎉 Todos os paths foram corrigidos com sucesso!")
            else:
                print("⚠️ Ainda há paths incorretos no CSV")
                
        else:
            print("✅ Todos os paths já estão corretos!")
            
    except FileNotFoundError:
        print(f"❌ Arquivo CSV não encontrado: {CSV_PATH}")
    except Exception as e:
        print(f"❌ Erro ao processar CSV: {e}")

if __name__ == "__main__":
    print("🔧 Corrigindo paths dos scripts no group_summary.csv...")
    fix_csv_script_paths()
    print("✨ Processo concluído!")
