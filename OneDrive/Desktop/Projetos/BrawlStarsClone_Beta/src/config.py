"""
Configurações principais do Brawl Stars Clone.
Este arquivo contém todas as constantes e configurações utilizadas
no jogo, incluindo dimensões da tela, cores, velocidades, e parâmetros
de gameplay que definem o comportamento do jogo.
"""

# Configurações da tela
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Brawl Stars Clone"

# Cores
COR_FUNDO = (34, 139, 34)  # Verde escuro
COR_OBSTACULO = (139, 69, 19)  # Marrom
COR_JOGADOR = (65, 105, 225)  # Azul real
COR_INIMIGO = (220, 20, 60)  # Vermelho carmesim
COR_TIRO = (255, 255, 0)  # Amarelo
COR_POWER_UP = (255, 20, 147)  # Rosa choque
COR_UI = (255, 255, 255)  # Branco
COR_UI_FUNDO = (0, 0, 0, 128)  # Preto transparente

# Cores do Menu
COR_TEXTO = (255, 255, 255)  # Branco
COR_BOTAO_NORMAL = (255, 165, 0)  # Laranja
COR_BOTAO_HOVER = (255, 215, 0)  # Dourado
COR_BOTAO_SELECIONADO = (255, 100, 100)  # Vermelho claro

# Configurações do jogador
VELOCIDADE_JOGADOR = 300  # pixels por segundo
VIDA_JOGADOR = 100  # Vida inicial do jogador
VIDA_MAXIMA_JOGADOR = 100
TAMANHO_JOGADOR = 20  # Reduzido para melhor proporção com o mapa maior

# Configurações de tiro
VELOCIDADE_TIRO = 500
DANO_TIRO = 25
TAMANHO_TIRO = 5
COOLDOWN_TIRO = 0.3  # segundos

# Configurações do mapa
TAMANHO_OBSTACULO = 60
QUANTIDADE_OBSTACULOS = 20
VIDA_OBSTACULO_DESTRUTIVEL_MIN = 80
VIDA_OBSTACULO_DESTRUTIVEL_MAX = 120
PONTOS_DESTRUIR_OBSTACULO = 10

# Configurações dos power-ups
TAMANHO_POWER_UP = 20
DURACAO_POWER_UP = 10.0  # Duração dos power-ups em segundos
TAMANHO_TIRO = 8

# Configurações de dificuldade progressiva
PONTOS_POR_NIVEL = 100  # Pontos necessários para subir de nível
VELOCIDADE_INIMIGO_BASE = 80  # Velocidade base dos inimigos (reduzida)
QUANTIDADE_INIMIGOS_BASE = 2  # Quantidade base de inimigos (reduzida)
MULTIPLICADOR_VELOCIDADE_POR_NIVEL = 1.20  # Aumento de 20% na velocidade por nível
MULTIPLICADOR_TIRO_POR_NIVEL = 1.15  # Aumento de 15% na frequência de tiro por nível
INIMIGOS_ADICIONAIS_POR_NIVEL = 1  # +1 inimigo a cada 2 níveis
NIVEL_MAXIMO = 20  # Nível máximo para balanceamento

# Configurações das gemas (Gem Grab)
TAMANHO_GEMA = 15  # Tamanho da gema
COR_GEMA = (128, 0, 128)  # Roxo - cor característica das gemas
GEMAS_PARA_VITORIA = 10  # Número de gemas necessárias para vencer
INTERVALO_SPAWN_GEMA = 7.0  # Segundos entre spawns de gemas
GEMAS_SIMULTANEAS_MAX = 3  # Máximo de gemas no mapa ao mesmo tempo
RAIO_COLETA_GEMA = 25  # Distância para coletar gema
PONTOS_POR_GEMA = 10  # Pontos ganhos por gema coletada

# Sistema de vitória por gemas
TEMPO_COUNTDOWN_VITORIA = 15.0  # Segundos para manter 10+ gemas para vencer
COR_COUNTDOWN_VITORIA = (255, 215, 0)  # Dourado para o countdown

# Sistema de respawn
TEMPO_RESPAWN = 3.0
VIDA_RESPAWN_PERCENTUAL = 0.7
AREA_RESPAWN_MARGEM = 100
DISTANCIA_MINIMA_INIMIGOS_RESPAWN = 150

# Pontuação
PONTOS_DESTRUIR_OBSTACULO = 25

# Configurações de áudio
VOLUME_MASTER = 0.7  # Volume geral (0.0 a 1.0)
VOLUME_SFX = 0.8     # Volume dos efeitos sonoros
VOLUME_MUSIC = 0.5   # Volume da música de fundo

# Configurações de áudio avançadas
AUDIO_FREQUENCY = 22050  # Frequência de amostragem
AUDIO_BUFFER_SIZE = 512  # Tamanho do buffer de áudio
AUDIO_CHANNELS = 2       # Número de canais (mono=1, stereo=2)
