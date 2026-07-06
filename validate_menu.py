#!/usr/bin/env python3
"""
Validador de menu.html para GitHub Pages
Corre antes de cada commit: python3 validate_menu.py menu.html
"""
import sys, re

if len(sys.argv) < 2:
    print("Uso: python3 validate_menu.py Apulia/Prod/menu.html")
    sys.exit(1)

path = sys.argv[1]
with open(path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

errors   = []
warnings = []

# 1. DOCTYPE primeiro
if not content.startswith('<!DOCTYPE'):
    errors.append("DOCTYPE nao e o primeiro elemento do ficheiro")

# 2. Tags balanceadas
for tag in ['<script', '</script>', '<style>', '</style>', '<body', '</body>']:
    count = content.count(tag)
    expected = 1 if tag in ['<style>', '</style>', '<body', '</body>'] else None
    if expected and count != expected:
        errors.append(f"Tag '{tag}' aparece {count}x (esperado {expected})")

if content.count('<script') != content.count('</script>'):
    errors.append(f"Tags <script> desbalanceadas: {content.count('<script')} abertas, {content.count('</script>')} fechadas")

# 3. Template literals aninhadas nos scripts
scripts = re.findall(r'<script(?! async)[^>]*>(.*?)</script>', content, re.DOTALL)
for i, s in enumerate(scripts):
    nested = re.findall(r'\$\{[^}]*`', s)
    if nested:
        errors.append(f"Script {i+1}: template literals aninhadas ({len(nested)}x): {nested[:2]}")

# 4. Caracteres box-drawing nos scripts (causam falha no Jekyll)
BOX_CHARS = {0x2500:'─', 0x2550:'═', 0x2190:'←', 0x2192:'→'}
for i, s in enumerate(scripts):
    found = {ch: s.count(ch) for cp,ch in BOX_CHARS.items() if chr(cp) in s}
    if found:
        errors.append(f"Script {i+1}: caracteres proibidos em JS: {found}")

# 5. Verificar flags do Surpreende-me
if 'SURPRESA_ENABLED' in content:
    m = re.search(r'const SURPRESA_ENABLED\s*=\s*(true|false)', content)
    if m:
        warnings.append(f"SURPRESA_ENABLED = {m.group(1)}")
    m2 = re.search(r'const SURPRESA_WEEKEND_ONLY\s*=\s*(true|false)', content)
    if m2:
        warnings.append(f"SURPRESA_WEEKEND_ONLY = {m2.group(1)}")

# 6. Tamanho do ficheiro
size_kb = len(content.encode('utf-8')) / 1024
if size_kb > 500:
    warnings.append(f"Ficheiro grande: {size_kb:.1f}KB (limite GitHub Pages: 100MB)")
else:
    warnings.append(f"Tamanho: {size_kb:.1f}KB - OK")

# Resultado
print("\n=== VALIDACAO MENU.HTML ===\n")
if errors:
    print(f"ERROS ({len(errors)}):")
    for e in errors:
        print(f"  x {e}")
else:
    print("  Sem erros - seguro para deploy")

if warnings:
    print(f"\nINFO:")
    for w in warnings:
        print(f"  i {w}")

print(f"""
NOTA: Se o codigo estiver limpo e o deploy continuar a falhar com
'Deployment failed, try again later', o problema e o custom domain.
Solucao: Settings -> Pages -> remover dominio -> guardar -> adicionar
de volta -> aguardar DNS check verde -> novo push.
""")
sys.exit(1 if errors else 0)