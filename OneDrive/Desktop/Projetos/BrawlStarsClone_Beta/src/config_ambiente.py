"""
Configurações do Sistema de Ambiente Dinâmico.
Este arquivo centraliza todos os parâmetros configuráveis do ambiente.
"""

# ===== CONFIGURAÇÕES GERAIS =====
LARGURA_MAPA_PADRAO = 1200
ALTURA_MAPA_PADRAO = 800

# ===== CICLO DIA/NOITE =====
CICLO_DIA_DURACAO = 120.0  # Duração em segundos (2 minutos)
TRANSICAO_ATIVA_PADRAO = True

# ===== SISTEMA DE VENTO =====
INTENSIDADE_VENTO_BASE = 0.5
VELOCIDADE_OSCILACAO_VENTO = 0.5
AMPLITUDE_DIRECAO_VENTO = 0.3

# ===== PARTÍCULAS AMBIENTAIS =====
INTERVALO_SPAWN_PARTICULA_MIN = 2.0  # segundos
INTERVALO_SPAWN_PARTICULA_MAX = 5.0  # segundos
VIDA_PARTICULA_FOLHA_MIN = 8.0  # segundos
VIDA_PARTICULA_FOLHA_MAX = 15.0  # segundos

# ===== PARTÍCULAS DE CLIMA =====
MAX_PARTICULAS_CHUVA = 100
MAX_PARTICULAS_NEVE = 80
MAX_PARTICULAS_TEMPESTADE = 120

SPAWN_RATE_CHUVA = 5
SPAWN_RATE_NEVE = 3
SPAWN_RATE_TEMPESTADE = 8

# Velocidades das partículas de chuva
CHUVA_VEL_X_MIN = -5
CHUVA_VEL_X_MAX = 5
CHUVA_VEL_Y_MIN = 200
CHUVA_VEL_Y_MAX = 400
CHUVA_VIDA = 3.0

# Velocidades das partículas de neve
NEVE_VEL_X_MIN = -20
NEVE_VEL_X_MAX = 20
NEVE_VEL_Y_MIN = 30
NEVE_VEL_Y_MAX = 80
NEVE_TAMANHO_MIN = 2
NEVE_TAMANHO_MAX = 5
NEVE_VIDA = 8.0

# Velocidades das partículas de tempestade
TEMPESTADE_VEL_X_MIN = -50
TEMPESTADE_VEL_X_MAX = 50
TEMPESTADE_VEL_Y_MIN = 300
TEMPESTADE_VEL_Y_MAX = 600
TEMPESTADE_VIDA = 2.0

# ===== SISTEMA DE MUDANÇA DE CLIMA =====
TEMPO_MUDANCA_CLIMA_MIN = 30.0  # segundos
TEMPO_MUDANCA_CLIMA_MAX = 60.0  # segundos
CHANCE_CLIMA_LIMPO = 0.6  # 60% de chance de ficar limpo

# ===== CORES AMBIENTE POR TIPO DE MAPA =====
CORES_AMBIENTE = {
    "cidade": {
        "dia": (255, 255, 240),
        "noite": (60, 60, 100),
        "amanhecer": (100, 80, 50),
        "entardecer": (200, 100, 60)
    },
    "deserto": {
        "dia": (255, 240, 200),
        "noite": (80, 70, 100),
        "amanhecer": (120, 90, 60),
        "entardecer": (220, 120, 80)
    },
    "floresta": {
        "dia": (240, 255, 240),
        "noite": (40, 60, 40),
        "amanhecer": (80, 100, 60),
        "entardecer": (160, 140, 80)
    },
    "gelo": {
        "dia": (240, 250, 255),
        "noite": (60, 80, 120),
        "amanhecer": (120, 140, 180),
        "entardecer": (140, 160, 200)
    }
}

# ===== ALPHA DOS OVERLAYS DE ILUMINAÇÃO =====
ALPHA_NOITE_MAX = 120  # Transparência máxima da noite
ALPHA_DIA_MIN = 0      # Transparência mínima do dia
ALPHA_TRANSICAO_MAX = 90  # Transparência máxima das transições

# ===== SISTEMA DE SOMBRAS =====
INTENSIDADE_SOMBRA_PADRAO = 1.0
SOMBRA_OFFSET_MULTIPLICADOR = 10
SOMBRA_ALTURA_MULTIPLICADOR = 5
SOMBRA_ESCALA_LARGURA = 0.8
SOMBRA_ESCALA_ALTURA = 0.6
SOMBRA_ALPHA = 80

# ===== CORES DAS PARTÍCULAS =====
CORES_FOLHAS = [
    (139, 69, 19),   # Marrom
    (160, 82, 45),   # Marrom claro
    (205, 133, 63),  # Peru
    (210, 180, 140), # Tan
    (34, 139, 34),   # Verde floresta
]

COR_CHUVA = (180, 200, 255)
COR_NEVE = (255, 255, 255)
COR_TEMPESTADE = (150, 180, 255)

# ===== CONFIGURAÇÕES DE DEBUG =====
DEBUG_ATIVO_PADRAO = False
MOSTRAR_INFO_DEBUG_PADRAO = False
CONTROLE_MANUAL_TEMPO_PADRAO = False

# Posição das informações de debug na tela
DEBUG_POS_X = 10
DEBUG_POS_Y = 10
DEBUG_LINHA_ALTURA = 20
DEBUG_COR_TEXTO = (255, 255, 255)
DEBUG_COR_FUNDO = (0, 0, 0, 180)

# ===== CONFIGURAÇÕES DE ARBUSTOS COM VENTO =====
BALANCO_MULTIPLICADOR_BASE = 3
BALANCO_ALTURA_MULTIPLICADOR = 1.5
BALANCO_FREQUENCIA_BASE = 2
BALANCO_FREQUENCIA_ALTURA = 1.5
VENTO_DIRECIONAL_MULTIPLICADOR = 2
VENTO_ALTURA_MULTIPLICADOR = 1

# Fator de borda para intensidade do vento
DISTANCIA_BORDA_MAXIMA = 200.0
INTENSIDADE_VENTO_MINIMA = 0.5
INTENSIDADE_VENTO_MAXIMA = 1.0

# ===== CONFIGURAÇÕES POR TIPO DE MAPA =====
EFEITOS_MAPA_CONFIG = {
    "cidade": {
        "particulas_base": ["poeira", "folhas"],
        "intensidade_vento_base": 0.3,
        "som_ambiente": "cidade_ambiente",
        "climas_permitidos": ["limpo", "chuva", "tempestade"]
    },
    "deserto": {
        "particulas_base": ["areia", "poeira"],
        "intensidade_vento_base": 0.7,
        "som_ambiente": "vento_deserto",
        "climas_permitidos": ["limpo", "tempestade"]
    },
    "floresta": {
        "particulas_base": ["folhas", "polen"],
        "intensidade_vento_base": 0.4,
        "som_ambiente": "floresta_ambiente",
        "climas_permitidos": ["limpo", "chuva", "neve", "tempestade"]
    },
    "gelo": {
        "particulas_base": ["flocos_neve", "cristais"],
        "intensidade_vento_base": 0.6,
        "som_ambiente": "vento_gelido",
        "climas_permitidos": ["limpo", "neve"]
    }
}
