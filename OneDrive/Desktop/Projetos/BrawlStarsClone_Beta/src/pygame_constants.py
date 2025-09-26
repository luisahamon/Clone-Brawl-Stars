"""
Constantes do pygame para o Brawl Stars Clone.
Este arquivo centraliza todas as constantes do pygame utilizadas
no projeto, facilitando a manutenção e evitando imports diretos
do pygame em todos os arquivos.
"""

# Eventos do pygame (valores obtidos do pygame-ce 2.5.5)
QUIT = 256
KEYDOWN = 768
KEYUP = 769
MOUSEBUTTONDOWN = 1025
MOUSEBUTTONUP = 1026
MOUSEMOTION = 1024
MOUSEWHEEL = 1027

# Teclas especiais
K_ESCAPE = 27
K_SPACE = 32
K_RETURN = 13

# Teclas direcionais
K_UP = 1073741906
K_DOWN = 1073741905
K_LEFT = 1073741904
K_RIGHT = 1073741903

# Teclas WASD e outras letras (usando convenção maiúscula do pygame)
# Nota: O pygame usa a mesma constante para teclas maiúsculas e minúsculas
# Por exemplo: K_W = K_w = 119 (case-insensitive)
K_W = 119
K_A = 97
K_S = 115
K_D = 100
K_R = 114
K_Q = 113
K_C = 99

# Teclas minúsculas (aliases para compatibilidade - REMOVIDAS para evitar redundância)
# As teclas de letra no pygame são case-insensitive, então K_w = K_W = 119

# Teclas de função
K_F1 = 1073741882
K_F2 = 1073741883
K_F3 = 1073741884
K_F4 = 1073741885
K_F5 = 1073741886
K_F6 = 1073741887
K_F12 = 1073741893

# Teclas numéricas
K_1 = 49
K_2 = 50
K_3 = 51
K_4 = 52
K_5 = 53

# Surface flags
SRCALPHA = 65536

# Blend modes (para efeitos visuais avançados)
BLEND_ADD = 1
BLEND_MULT = 8
BLEND_RGBA_MIN = 11
BLEND_RGBA_ADD = 6

# Botões do mouse
BUTTON_LEFT = 1
BUTTON_MIDDLE = 2
BUTTON_RIGHT = 3
