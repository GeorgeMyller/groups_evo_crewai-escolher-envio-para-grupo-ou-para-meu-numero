#!/usr/bin/env python3
"""
Script para executar testes do sistema / Test runner script
"""
import subprocess
import sys
import os


def run_tests():
    """Executa todos os testes do sistema"""
    
    print("🧪 Executando testes do sistema...")
    print("=" * 50)
    
    # Verifica se pytest está disponível
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/",
            "--verbose",
            "--tb=short",
            "--cov=.",
            "--cov-report=term-missing"
        ], check=True, cwd=os.path.dirname(__file__))
        
        print("\n✅ Todos os testes passaram!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Alguns testes falharam (código: {e.returncode})")
        return False
        
    except FileNotFoundError:
        print("❌ pytest não encontrado. Instale com:")
        print("pip install pytest pytest-cov pytest-mock")
        return False


def run_type_check():
    """Executa verificação de tipos (se mypy estiver disponível)"""
    try:
        print("\n🔍 Verificando tipos com mypy...")
        subprocess.run([
            sys.executable, "-m", "mypy", 
            ".", 
            "--ignore-missing-imports"
        ], check=True)
        print("✅ Verificação de tipos passou!")
        return True
        
    except subprocess.CalledProcessError:
        print("⚠️  Alguns problemas de tipo encontrados")
        return False
        
    except FileNotFoundError:
        print("ℹ️  mypy não encontrado (opcional)")
        return True


def main():
    """Função principal"""
    print("🚀 Sistema de Testes - WhatsApp Group Resumer")
    print("Desenvolvido com excelência técnica! 🏆\n")
    
    success = True
    
    # Executa testes
    if not run_tests():
        success = False
    
    # Executa verificação de tipos (opcional)
    if not run_type_check():
        pass  # Não falha o processo principal
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Todos os testes executados com sucesso!")
        print("✨ Código com qualidade profissional!")
        sys.exit(0)
    else:
        print("🔧 Algumas correções são necessárias")
        sys.exit(1)


if __name__ == "__main__":
    main()
