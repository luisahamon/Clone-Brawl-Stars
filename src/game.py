"""
Classe principal do jogo - Brawl Stars Clone.
Este módulo contém a lógica central do jogo, gerenciando estados (seleção de personagem,
gameplay, game over), sistema de dificuldade progressiva, spawn de inimigos e power-ups,
detecção de colisões e coordenação entre todos os componentes do jogo.
É o núcleo que orquestra toda a experiência de gameplay.
"""

import random
import math
import pygame

from src.efeitos_visuais import (
    EfeitoParticulas, EfeitoColetaGema, EfeitoExplosao, EfeitoOndas,
    gerenciador_efeitos
)
from src.renderer_3d import renderer_3d
from src.particulas_3d import sistema_particulas_3d
from src.characters.personagens import obter_personagem
from src.player import Player
from src.enemy import Enemy
from src.obstacle import Obstacle
from src.power_up import PowerUp
from src.ui import UI
from src.characters.seletor_personagem import SeletorPersonagem
from src.audio_manager import gerenciador_audio
from src.menu_audio import MenuAudio
from src.gem_system import GerenciadorGemas
from src.feedback_combate import inicializar_feedback_combate
from src.pygame_constants import KEYDOWN, K_ESCAPE, K_R, K_F1, K_F2, K_F3, K_F4, K_F5, K_F6
from src.sistema_progressao import sistema_progressao
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COR_FUNDO, TAMANHO_OBSTACULO,
    QUANTIDADE_OBSTACULOS, TAMANHO_POWER_UP, TAMANHO_JOGADOR,
    PONTOS_POR_NIVEL, VELOCIDADE_INIMIGO_BASE, QUANTIDADE_INIMIGOS_BASE,
    MULTIPLICADOR_VELOCIDADE_POR_NIVEL, MULTIPLICADOR_TIRO_POR_NIVEL,
    INIMIGOS_ADICIONAIS_POR_NIVEL, NIVEL_MAXIMO,
    GEMAS_PARA_VITORIA, PONTOS_POR_GEMA, TEMPO_RESPAWN, VIDA_RESPAWN_PERCENTUAL,
    AREA_RESPAWN_MARGEM, DISTANCIA_MINIMA_INIMIGOS_RESPAWN,
    TEMPO_COUNTDOWN_VITORIA, COOLDOWN_TIRO, VIDA_OBSTACULO_DESTRUTIVEL_MIN,
    VIDA_OBSTACULO_DESTRUTIVEL_MAX, PONTOS_DESTRUIR_OBSTACULO
)
from src.collision_system import ProjectilePool, CollisionOptimizer
from src.bullet import Bullet
from src.bushes import GerenciadorArbustos
from src.ambiente_dinamico import GerenciadorAmbiente
from src.achievement_system import SistemaConquistas, Conquista

class Game:
    """
    Classe principal do jogo Brawl Stars Clone.
    Gerencia todos os aspectos do jogo incluindo:
    - Estados do jogo (seleção de personagem, gameplay, game over, menu de áudio)
    - Sistema de dificuldade progressiva baseado em níveis
    - Spawn e gerenciamento de inimigos, obstáculos e power-ups
    - Detecção de colisões entre todos os sprites
    - Coordenação entre componentes (UI, áudio, efeitos visuais)
    - Loop principal de atualização e renderização
    Attributes:
        screen (pygame.Surface): Superfície principal de renderização
        estado (str): Estado atual do jogo
        jogador (Player): Instância do jogador atual
        nivel_atual (int): Nível atual de dificuldade
        pontuacao (int): Pontuação atual do jogador
        - "jogando": Gameplay principal
        - "game_over": Tela de fim de jogo
        - "menu_audio": Menu de configurações de áudio
    """
    def __init__(self, screen):
        self.screen = screen
        # Estados: selecao_personagem, jogando, game_over, menu_audio
        self.estado = "selecao_personagem"
        self.seletor_personagem = SeletorPersonagem(screen)
        self.menu_audio = MenuAudio(screen)
        self.personagem_selecionado = None
        self.feedback_combate = inicializar_feedback_combate(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.jogo_ativo = True
        self.pontuacao = 0
        self.jogador = None
        self.nivel_atual = 1
        self.pontos_proximo_nivel = PONTOS_POR_NIVEL
        self.velocidade_inimigos_atual = VELOCIDADE_INIMIGO_BASE
        self.quantidade_inimigos_atual = QUANTIDADE_INIMIGOS_BASE
        self.multiplicador_tiro_atual = 1.0  # Multiplicador de frequência de tiro

        # Sistema de gemas
        self.gemas_coletadas = 0
        self.gerenciador_gemas = None

        # Sistema de vitória por gemas
        self.vitoria_countdown_ativo = False
        self.tempo_vitoria_restante = 0.0
        self.vitoria_alcancada = False

        # Sistema de respawn
        self.jogador_morto = False
        self.tempo_respawn_restante = 0.0
        self.posicao_morte = None        # Sistema de conquistas
        self.sistema_conquistas = SistemaConquistas()

        # Sistema de progressão - estatísticas da partida
        self.tempo_inicio_partida = 0
        self.dano_total_causado = 0
        self.inimigos_eliminados = 0
        self.dano_total_recebido = 0
        self.resultado_progressao = None
        self._inicializar_conquistas()
        # Tempo de jogo para animações 3D
        self.tempo_jogo = 0.0
        # Variável de debug para fonte (inicializada aqui para evitar definição fora do __init__)
        self.debug_font = None

        # Sistema de debug de colisões (inicializado aqui para evitar definição fora do __init__)
        self.debug_collision_system = False

        self._inicializar_grupos_sprites()
        self._inicializar_sistemas_otimizados()
        self._inicializar_componentes_ui()
        self._inicializar_estado_jogo()
        self._inicializar_dificuldade()
        self._inicializar_audio()
        self._inicializar_arbustos()
        self._inicializar_ambiente()

    def _inicializar_conquistas(self):
        """Define as conquistas disponíveis no jogo."""
        self.sistema_conquistas.adicionar_conquista(
            Conquista(
                nome="Primeira Gema",
                descricao="Colete sua primeira gema.",
                criterio=lambda contexto: contexto['gemas_coletadas'] >= 1
            )
        )
        self.sistema_conquistas.adicionar_conquista(
            Conquista(
                nome="Caçador de Inimigos",
                descricao="Derrote 10 inimigos.",
                criterio=lambda contexto: contexto['inimigos_derrotados'] >= 10
            )
        )
        self.sistema_conquistas.adicionar_conquista(
            Conquista(
                nome="Super Usada",
                descricao="Use sua habilidade especial pela primeira vez.",
                criterio=lambda contexto: contexto['super_usada'] >= 1
            )
        )

    def _inicializar_grupos_sprites(self):
        """
        Inicializar todos os grupos de sprites do jogo.
        Cria grupos separados para organizar diferentes tipos de sprites:
        - todos_sprites: Grupo mestre contendo todos os sprites
        - jogadores: Sprites de jogadores
        - inimigos: Sprites de inimigos
        - tiros: Projéteis de jogadores e inimigos
        - obstaculos: Elementos estáticos do mapa
        - power_ups: Itens coletáveis
        """
        self.todos_sprites = pygame.sprite.Group()
        self.jogadores = pygame.sprite.Group()
        self.inimigos = pygame.sprite.Group()
        self.tiros = pygame.sprite.Group()
        self.obstaculos = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()

    def _inicializar_sistemas_otimizados(self):
        """
        Inicializar sistemas de otimização de performance.
        Configura QuadTree para detecção espacial de colisões e
        Object Pool para reutilização eficiente de projéteis.
        """
        # Configurar limites da tela para QuadTree
        bounds = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Inicializar sistema de colisões otimizado
        self.collision_optimizer = CollisionOptimizer(bounds, max_objects=15, max_levels=6)

        # Inicializar pool de projéteis
        self.projectile_pool = ProjectilePool(size=300)

    def _inicializar_componentes_ui(self):
        """Inicializar componentes de UI"""
        self.ui = UI()

    def _inicializar_estado_jogo(self):
        """Inicializar estado do jogo"""
        self.jogo_ativo = True
        self.pontuacao = 0
        self.jogador = None

    def _inicializar_dificuldade(self):
        """Inicializar sistema de dificuldade progressiva"""
        self.nivel_atual = 1
        self.pontos_proximo_nivel = PONTOS_POR_NIVEL
        self.velocidade_inimigos_atual = VELOCIDADE_INIMIGO_BASE
        self.quantidade_inimigos_atual = QUANTIDADE_INIMIGOS_BASE
        self.multiplicador_tiro_atual = 1.0

    def _inicializar_audio(self):
        """Inicializar sistema de áudio"""
        self.inicializar_jogo()
        gerenciador_audio.carregar_sons()

    def _inicializar_arbustos(self):
        """Inicializar sistema de arbustos"""
        self.gerenciador_arbustos = GerenciadorArbustos(SCREEN_WIDTH, SCREEN_HEIGHT)

    def _inicializar_ambiente(self):
        """Inicializar sistema de ambiente dinâmico"""
        self.gerenciador_ambiente = GerenciadorAmbiente(SCREEN_WIDTH, SCREEN_HEIGHT)

    def inicializar_jogo(self):
        """Limpar e resetar componentes do jogo"""
        # Limpar grupos existentes
        self.todos_sprites.empty()
        self.jogadores.empty()
        self.inimigos.empty()
        self.tiros.empty()
        self.obstaculos.empty()
        self.power_ups.empty()

        # Limpar sistemas otimizados
        if hasattr(self, 'collision_optimizer'):
            self.collision_optimizer.clear()
        if hasattr(self, 'projectile_pool'):
            self.projectile_pool.clear_all()

        # Limpar sistema de arbustos
        if hasattr(self, 'gerenciador_arbustos'):
            self.gerenciador_arbustos.limpar_arbustos()

        # Resetar estado
        self.jogo_ativo = True
        self.pontuacao = 0
        self.jogador = None

        # Resetar sistema de respawn
        self.jogador_morto = False
        self.tempo_respawn_restante = 0.0
        self.posicao_morte = None

        # Resetar estatísticas da partida
        self.tempo_inicio_partida = pygame.time.get_ticks()
        self.dano_total_causado = 0
        self.inimigos_eliminados = 0
        self.dano_total_recebido = 0

        # Resetar sistema de dificuldade
        self.nivel_atual = 1
        self.pontos_proximo_nivel = PONTOS_POR_NIVEL
        self.velocidade_inimigos_atual = VELOCIDADE_INIMIGO_BASE
        self.quantidade_inimigos_atual = QUANTIDADE_INIMIGOS_BASE
        self.multiplicador_tiro_atual = 1.0

    def iniciar_partida(self, nome_personagem):
        """
        Iniciar uma nova partida com o personagem selecionado.
        Args:
            nome_personagem (str): Nome do personagem escolhido pelo jogador
        Esta função:
        - Limpa todos os sprites existentes
        - Cria novo jogador com personagem selecionado
        - Gera obstáculos, inimigos e power-ups no mapa
        - Altera estado para "jogando"
        - Inicia música de batalha
        """
        # Obter o objeto personagem pelo nome
        personagem = obter_personagem(nome_personagem)
        self.personagem_selecionado = personagem

        # Limpar grupos
        self.todos_sprites.empty()
        self.jogadores.empty()
        self.inimigos.empty()
        self.tiros.empty()
        self.obstaculos.empty()
        self.power_ups.empty()

        # Criar jogador com personagem selecionado
        self.jogador = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, nome_personagem)
        self.todos_sprites.add(self.jogador)
        self.jogadores.add(self.jogador)

        # Criar elementos do jogo
        self.criar_obstaculos()
        self.criar_inimigos()
        self.criar_power_ups()

        # Gerar arbustos no mapa
        self.gerenciador_arbustos.gerar_arbustos_estrategicos(list(self.obstaculos))

        # Inicializar sistema de gemas
        self.gerenciador_gemas = GerenciadorGemas(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            list(self.obstaculos)
        )
        self.gemas_coletadas = 0

        # Resetar sistema de vitória
        self.vitoria_countdown_ativo = False
        self.tempo_vitoria_restante = 0.0
        self.vitoria_alcancada = False

        # Resetar sistema de respawn
        self.jogador_morto = False
        self.tempo_respawn_restante = 0.0
        self.posicao_morte = None

        # Mudar estado
        self.estado = "jogando"
        self.jogo_ativo = True
        self.pontuacao = 0        # Limpar estado de áudio antes de iniciar
        gerenciador_audio.limpar_estado_audio()

        # Som ambiente sutil para o jogo ao invés de música
        if gerenciador_audio.som_disponivel('ambiente_jogo'):
            gerenciador_audio.tocar_som('ambiente_jogo', volume=0.05)

    def _calcular_distancia_jogador(self, x, y):
        """Calcular distância de um ponto até o centro da tela (posição inicial do jogador)"""
        centro_x = SCREEN_WIDTH // 2
        centro_y = SCREEN_HEIGHT // 2
        return ((x - centro_x) ** 2 + (y - centro_y) ** 2) ** 0.5

    def criar_obstaculos(self):
        """Cria obstáculos no mapa (alguns destrutíveis) evitando sobreposições"""
        obstaculos_destruteis = QUANTIDADE_OBSTACULOS // 3  # 1/3 dos obstáculos são destrutíveis
        for i in range(QUANTIDADE_OBSTACULOS):
            obstaculo_criado = False
            tentativas = 0

            while not obstaculo_criado and tentativas < 100:
                x = random.randint(
                    TAMANHO_OBSTACULO,
                    SCREEN_WIDTH - TAMANHO_OBSTACULO
                )
                y = random.randint(
                    TAMANHO_OBSTACULO,
                    SCREEN_HEIGHT - TAMANHO_OBSTACULO
                )
                # Verificar se não está muito perto do jogador
                distancia_jogador = self._calcular_distancia_jogador(x, y)
                # Verificar se não está muito perto de outros obstáculos
                posicao_valida = True
                for obstaculo_existente in self.obstaculos:
                    dx = x - obstaculo_existente.rect.centerx
                    dy = y - obstaculo_existente.rect.centery
                    distancia = math.sqrt(dx*dx + dy*dy)
                    # Manter pelo menos 60 pixels de distância entre obstáculos
                    if distancia < 60:
                        posicao_valida = False
                        break

                if distancia_jogador > 100 and posicao_valida:
                    # Determinar se é destrutível
                    destrutivel = i < obstaculos_destruteis
                    vida_obstaculo = random.randint(VIDA_OBSTACULO_DESTRUTIVEL_MIN,
                                                  VIDA_OBSTACULO_DESTRUTIVEL_MAX) if destrutivel else 100
                    obstaculo = Obstacle(x, y, destrutivel, vida_obstaculo)
                    self.todos_sprites.add(obstaculo)
                    self.obstaculos.add(obstaculo)
                    obstaculo_criado = True

                tentativas += 1

    def criar_inimigos(self):
        """Cria inimigos no mapa baseado no nível atual"""
        for _ in range(self.quantidade_inimigos_atual):
            inimigo_criado = False
            tentativas = 0

            while not inimigo_criado and tentativas < 100:
                x = random.randint(50, SCREEN_WIDTH - 50)
                y = random.randint(50, SCREEN_HEIGHT - 50)

                # Verificar se não está muito perto do jogador
                distancia_jogador = self._calcular_distancia_jogador(x, y)
                if distancia_jogador > 150:
                    inimigo = Enemy(
                        x, y,
                        self.jogador,
                        self.velocidade_inimigos_atual,
                        self.multiplicador_tiro_atual
                    )
                    # Definir referência do sistema de arbustos
                    if hasattr(self, 'gerenciador_arbustos'):
                        inimigo.gerenciador_arbustos = self.gerenciador_arbustos
                    self.todos_sprites.add(inimigo)
                    self.inimigos.add(inimigo)
                    inimigo_criado = True

                tentativas += 1

    def _verificar_colisao_power_up_obstaculos(self, x, y):
        """Verificar se posição do power-up colide com obstáculos"""
        temp_rect = pygame.Rect(
            x - TAMANHO_POWER_UP // 2,
            y - TAMANHO_POWER_UP // 2,
            TAMANHO_POWER_UP,
            TAMANHO_POWER_UP
        )

        for obstaculo in self.obstaculos:
            if temp_rect.colliderect(obstaculo.rect):
                return True
        return False

    def criar_power_ups(self):
        """Cria power-ups no mapa"""
        for _ in range(5):
            power_up_criado = False
            tentativas = 0

            while not power_up_criado and tentativas < 100:
                x = random.randint(
                    TAMANHO_POWER_UP,
                    SCREEN_WIDTH - TAMANHO_POWER_UP
                )
                y = random.randint(
                    TAMANHO_POWER_UP,
                    SCREEN_HEIGHT - TAMANHO_POWER_UP
                )

                # Verificar colisão com obstáculos
                if not self._verificar_colisao_power_up_obstaculos(x, y):
                    power_up = PowerUp(x, y)
                    self.todos_sprites.add(power_up)
                    self.power_ups.add(power_up)
                    power_up_criado = True

                tentativas += 1

    def verificar_aumento_nivel(self):
        """Verificar se o jogador deve subir de nível"""
        if self.pontuacao >= self.pontos_proximo_nivel and self.nivel_atual < NIVEL_MAXIMO:
            self.subir_nivel()

    def subir_nivel(self):
        """Aumentar nível e ajustar dificuldade"""
        self.nivel_atual += 1
        self.pontos_proximo_nivel = self.nivel_atual * PONTOS_POR_NIVEL

        # Tocar som de level up
        gerenciador_audio.tocar_som('level_up', canal='ui')
        
        # Aumentar velocidade dos inimigos
        self.velocidade_inimigos_atual *= MULTIPLICADOR_VELOCIDADE_POR_NIVEL

        # Aumentar frequência de tiro dos inimigos
        self.multiplicador_tiro_atual *= MULTIPLICADOR_TIRO_POR_NIVEL

        # Aumentar quantidade de inimigos a cada 2 níveis
        if self.nivel_atual % 2 == 0:
            self.quantidade_inimigos_atual += INIMIGOS_ADICIONAIS_POR_NIVEL
        self.adicionar_inimigos_nivel()

    def adicionar_inimigos_nivel(self):
        """Adicionar inimigos quando o nível aumenta"""
        inimigos_atuais = len(self.inimigos)
        inimigos_necessarios = self.quantidade_inimigos_atual - inimigos_atuais
        for _ in range(inimigos_necessarios):
            self.criar_novo_inimigo()
        
        # Atualizar velocidade e tiro dos inimigos existentes
        for inimigo in self.inimigos:
            inimigo.velocidade = self.velocidade_inimigos_atual
            # Atualizar cooldown de tiro baseado no novo multiplicador
            inimigo.cooldown_tiro = (COOLDOWN_TIRO * 1.8) / self.multiplicador_tiro_atual

    def obter_info_nivel(self):
        """Obter informações do nível atual para a UI"""
        return {
            'nivel': self.nivel_atual,
            'pontuacao_atual': self.pontuacao,
            'pontuacao_proximo_nivel': self.pontos_proximo_nivel,
            'velocidade_inimigos': self.velocidade_inimigos_atual,
            'quantidade_inimigos': self.quantidade_inimigos_atual,
            'progresso': (min(1.0, self.pontuacao / self.pontos_proximo_nivel)
                         if self.nivel_atual < NIVEL_MAXIMO else 1.0)
        }

    def handle_game_event(self, event):
        """Gerenciar eventos do estado geral do jogo"""
        if self.estado == "selecao_personagem":
            resultado = self.seletor_personagem.handle_selection_event(event)
            if resultado == "voltar":
                return False  # Sair do jogo
            if resultado == "audio":  # Abrir menu de áudio
                self.estado = "menu_audio"
                return True
            if resultado:  # Personagem selecionado
                self.iniciar_partida(resultado)
                return True

        elif self.estado == "menu_audio":
            resultado = self.menu_audio.handle_event(event)
            if resultado == "voltar":
                self.estado = "selecao_personagem"
                return True
            return True

        elif self.estado == "jogando":
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.estado = "selecao_personagem"  # Voltar para seleção
                    return True
                if event.key == K_R and not self.jogo_ativo: # Reiniciar com mesmo personagem
                    if self.personagem_selecionado:
                        # Processar progressão como derrota antes de reiniciar
                        if hasattr(self, 'tempo_inicio_partida'):
                            self._processar_progressao_fim_partida(False)
                        self.iniciar_partida(self.personagem_selecionado)
                        return True

                # Controles de debug do ambiente
                if hasattr(self, 'gerenciador_ambiente'):
                    if event.key == K_F1:  # Toggle debug
                        self.gerenciador_ambiente.alternar_debug()
                    elif event.key == K_F2:  # Mudar tipo de mapa
                        tipos = ["cidade", "deserto", "floresta", "gelo"]
                        atual = self.gerenciador_ambiente.tipo_mapa
                        proximo_idx = (tipos.index(atual) + 1) % len(tipos)
                        self.gerenciador_ambiente.mudar_tipo_mapa(tipos[proximo_idx])
                    elif event.key == K_F3:  # Forçar clima
                        climas = ["limpo", "chuva", "neve", "tempestade"]
                        atual = self.gerenciador_ambiente.clima_atual
                        proximo_idx = (climas.index(atual) + 1) % len(climas)
                        self.gerenciador_ambiente.forcar_clima(climas[proximo_idx])
                    elif event.key == K_F4:  # Toggle transição dia/noite
                        self.gerenciador_ambiente.alternar_transicao_dia_noite()
                  # Controles extras de debug
                elif hasattr(self, 'debug_collision_system'):
                    if event.key == K_F5:  # Toggle debug de colisões
                        self.debug_collision_system = not self.debug_collision_system
                        print(f"Debug de colisões: {'ATIVADO' if self.debug_collision_system else 'DESATIVADO'}")
                    elif event.key == K_F6:  # Mostrar estatísticas de performance
                        self._mostrar_estatisticas_performance()

            # Processar input contínuo para debug
            if hasattr(self, 'gerenciador_ambiente') and self.gerenciador_ambiente.debug_ativo:
                teclas = pygame.key.get_pressed()
                self.gerenciador_ambiente.processar_input_debug(teclas)

            if self.jogo_ativo and self.jogador and not self.jogador_morto:
                # Processar eventos de controles virtuais
                resultado_touch = self.ui.processar_evento_touch(event)
                if resultado_touch == 'attack_press':
                    # Disparar usando botão de ataque virtual
                    self.jogador.atirar_botao_virtual(self.tiros, self.todos_sprites, self)
                # Processar eventos normais do jogador
                self.jogador.handle_event(event, self.tiros, self.todos_sprites, self)
            return True

        elif self.estado == "game_over":
            if event.type == KEYDOWN:
                if event.key == K_R:
                    if self.personagem_selecionado:
                        self.iniciar_partida(self.personagem_selecionado)
                        return True
                elif event.key == K_ESCAPE:
                    self.estado = "selecao_personagem"
                    return True

        elif self.estado == "vitoria":
            if event.type == KEYDOWN:
                if event.key == K_R:
                    if self.personagem_selecionado:
                        self.iniciar_partida(self.personagem_selecionado)
                        return True
                elif event.key == K_ESCAPE:
                    self.estado = "selecao_personagem"
                    return True

        return True

    def update(self, dt):
        """Atualizar lógica do jogo"""
        # Atualizar tempo de jogo para animações 3D
        self.tempo_jogo += dt

        # Aplicar slow motion se ativo
        if self.feedback_combate:
            dt_original = dt
            dt = dt * self.feedback_combate.obter_fator_tempo()

            # Atualizar sistema de feedback (sempre com dt original)
            self.feedback_combate.update(dt_original)

        if self.estado == "selecao_personagem":
            self.seletor_personagem.update(dt)
        elif self.estado == "menu_audio":
            self.menu_audio.update(dt)
        elif self.estado == "jogando" and self.jogo_ativo:
            self.atualizar_jogo(dt)

    def atualizar_jogo(self, dt):
        """Atualizar lógica principal do jogo"""
        if not self.jogador:
            return

        # Atualizar sistema de partículas 3D
        sistema_particulas_3d.update(dt)
        self._atualizar_sprites(dt)
        self._atualizar_sistema_gemas(dt)
        self._verificar_nivel_e_respawn()
        self._processar_colisoes_tiros()

        # Só processar colisões do jogador se ele não estiver morto
        if not self.jogador_morto:
            self._processar_colisoes_jogador(dt)

        self._verificar_game_over()
        self._fazer_inimigos_atirarem(dt)        # Verificar vitória por gemas
        self._verificar_vitoria_gemas()
        # Processar countdown de vitória se ativo
        self._processar_countdown_vitoria()

    def _atualizar_sprites(self, dt):
        """Atualizar sprites e efeitos visuais"""
        # Obter direção do joystick virtual
        joystick_direcao = self.ui.obter_direcao_joystick()

        # Se jogador está morto, não atualizar o jogador
        if self.jogador_morto:
            # Atualizar apenas sprites que não são o jogador
            for sprite in self.todos_sprites:
                if sprite != self.jogador:
                    sprite.update(dt, self.obstaculos)
        else:
            # Atualizar jogador com direção do joystick
            self.jogador.update(dt, self.obstaculos, joystick_direcao)

            # Atualizar outros sprites normalmente
            for sprite in self.todos_sprites:
                if sprite != self.jogador:
                    sprite.update(dt, self.obstaculos)
        gerenciador_efeitos.update(dt)

        # Atualizar sistema de ambiente dinâmico
        if hasattr(self, 'gerenciador_ambiente'):
            self.gerenciador_ambiente.atualizar(dt)

        # Atualizar sistema de arbustos com efeito de vento
        if hasattr(self, 'gerenciador_arbustos'):
            entidades_para_verificar = []
            if not self.jogador_morto and self.jogador:
                entidades_para_verificar.append(self.jogador)
            entidades_para_verificar.extend(self.inimigos)

            # Obter efeito de vento do sistema de ambiente
            efeito_vento = None
            if hasattr(self, 'gerenciador_ambiente'):
                efeito_vento = self.gerenciador_ambiente.obter_efeito_vento()
            self.gerenciador_arbustos.atualizar(dt, entidades_para_verificar, efeito_vento)

        # Atualizar pool de projéteis (limpar projéteis inativos)
        if hasattr(self, 'projectile_pool'):
            self.projectile_pool.update(dt)

    def _verificar_nivel_e_respawn(self):
        """Verificar aumento de nível e respawn de inimigos"""
        self.verificar_aumento_nivel()
        if len(self.inimigos) < self.quantidade_inimigos_atual:
            self.criar_novo_inimigo()

    def _processar_colisoes_tiros(self):
        """Processar colisões entre tiros do jogador e inimigos usando sistema otimizado"""
        # Limpar e popular QuadTree com sprites ativos
        self.collision_optimizer.clear()

        # Adicionar todos os inimigos vivos à QuadTree (inimigos não têm atributo 'ativo')
        inimigos_vivos = [inimigo for inimigo in self.inimigos if inimigo.vida > 0]
        self.collision_optimizer.add_objects(inimigos_vivos)        # Processar colisões para cada tiro do jogador
        tiros_jogador = [tiro for tiro in self.tiros if self._tiro_ativo_jogador(tiro)]

        for tiro in tiros_jogador:
            # Usar QuadTree para obter candidatos próximos
            candidatos_inimigos = self.collision_optimizer.get_collision_candidates(tiro)

            # Verificar colisões precisas apenas com candidatos próximos
            hit_target = False
            for inimigo in candidatos_inimigos:
                if inimigo in self.inimigos and tiro.rect.colliderect(inimigo.rect):
                    self._processar_dano_inimigo(tiro, inimigo)
                    hit_target = True
                    break  # Tiro só pode atingir um inimigo
            # Se não atingiu inimigo, verificar obstáculos destrutíveis
            if not hit_target:
                self._processar_colisoes_tiros_obstaculos(tiro)

    def _processar_colisoes_tiros_obstaculos(self, tiro):
        """Processar colisões entre tiros e obstáculos destrutíveis"""
        for obstaculo in self.obstaculos:
            if tiro.rect.colliderect(obstaculo.rect):
                if obstaculo.destrutivel:
                    dano = getattr(tiro, 'dano', 25)
                    destruido = obstaculo.receber_dano(dano)
                    # Efeito visual de impacto no obstáculo
                    gerenciador_efeitos.criar_efeito_impacto(
                        obstaculo.rect.centerx, obstaculo.rect.centery, "normal"
                    )
                    if destruido:
                        # Efeito de destruição
                        gerenciador_efeitos.grupo_efeitos.add(EfeitoExplosao(
                            obstaculo.rect.centerx, obstaculo.rect.centery,
                            (139, 69, 19), 50, 0.8
                        ))
                        # Partículas de madeira
                        gerenciador_efeitos.grupo_efeitos.add(EfeitoParticulas(
                            obstaculo.rect.centerx, obstaculo.rect.centery,
                            (160, 82, 45), 12, 1.0, 60
                        ))
                        # Partículas 3D de destruição
                        sistema_particulas_3d.adicionar_destruicao_obstaculo(
                            obstaculo.rect.centerx, obstaculo.rect.centery,
                            (139, 69, 19)
                        )
                        # Remover obstáculo
                        obstaculo.kill()
                        self.obstaculos.remove(obstaculo)
                        self.todos_sprites.remove(obstaculo)
                          # Pontuação por destruir obstáculo
                        self.pontuacao += PONTOS_DESTRUIR_OBSTACULO
                # Destruir tiro
                tiro.kill()
                break

    def _processar_colisoes_jogador(self, _dt):
        """Processar colisões entre jogador e outros elementos"""
        # Parâmetro _dt mantido para consistência com outros métodos, mas não usado aqui
        
        # Verificar se jogador existe e não está morto
        if not self.jogador or self.jogador_morto:
            return

        # Colisões jogador-inimigo (jogador não pode passar através de inimigos)
        for inimigo in self.inimigos:
            if pygame.sprite.collide_rect(self.jogador, inimigo):
                # Calcular direção para empurrar o jogador para longe do inimigo
                dx = self.jogador.rect.centerx - inimigo.rect.centerx
                dy = self.jogador.rect.centery - inimigo.rect.centery

                # Normalizar direção
                distancia = math.sqrt(dx*dx + dy*dy)
                if distancia > 0:
                    # Empurrar jogador para longe do inimigo
                    empurrao_x = (dx / distancia) * 5  # Força do empurrão
                    empurrao_y = (dy / distancia) * 5

                    # Aplicar empurrão respeitando limites da tela
                    nova_x = self.jogador.pos_x + empurrao_x
                    nova_y = self.jogador.pos_y + empurrao_y

                    # Verificar limites da tela
                    half_width = self.jogador.rect.width // 2
                    half_height = self.jogador.rect.height // 2
                    nova_x = max(half_width, min(nova_x, SCREEN_WIDTH - half_width))
                    nova_y = max(half_height, min(nova_y, SCREEN_HEIGHT - half_height))

                    # Aplicar nova posição
                    self.jogador.pos_x = nova_x
                    self.jogador.pos_y = nova_y
                    self.jogador.rect.centerx = int(nova_x)
                    self.jogador.rect.centery = int(nova_y)

        # Colisões tiro-jogador (tiros inimigos)
        tiros_inimigos = [tiro for tiro in self.tiros if hasattr(tiro, 'de_inimigo') and tiro.de_inimigo]
        for tiro in tiros_inimigos:
            if hasattr(tiro, 'ativo') and not tiro.ativo:
                continue

            if pygame.sprite.collide_rect(tiro, self.jogador):
                dano = getattr(tiro, 'dano', 25)                # Efeito visual de dano no jogador
                gerenciador_efeitos.grupo_efeitos.add(EfeitoExplosao(
                    self.jogador.rect.centerx, self.jogador.rect.centery,
                    (255, 255, 100), 30, 0.2
                ))

                # Feedback de combate quando jogador recebe dano
                if self.feedback_combate:
                    self.feedback_combate.iniciar_screen_shake(8.0, 0.2)
                    self.feedback_combate.criar_particulas_impacto(
                        self.jogador.rect.centerx, self.jogador.rect.centery, "normal", 10
                    )
                self.jogador.receber_dano(dano)
                tiro.kill()

        # Colisões jogador-power-up
        power_ups_coletados = pygame.sprite.spritecollide(self.jogador, self.power_ups, True)
        for power_up in power_ups_coletados:            # Efeito visual de coleta de power-up
            cor_efeito = (0, 255, 255) if power_up.tipo == 'velocidade' else \
                        (0, 255, 0) if power_up.tipo == 'vida' else \
                        (255, 150, 0)  # tiro_rapido
            gerenciador_efeitos.grupo_efeitos.add(EfeitoOndas(
                power_up.rect.centerx, power_up.rect.centery,
                cor_efeito, 2, 0.8
            ))

            # Partículas 3D de coleta de power-up
            sistema_particulas_3d.adicionar_powerup_coletado(
                power_up.rect.centerx, power_up.rect.centery,
                power_up.tipo
            )

            # Feedback de combate para coleta de power-up
            if self.feedback_combate:
                self.feedback_combate.iniciar_screen_shake(3.0, 0.1)
                self.feedback_combate.criar_luz_dinamica(
                    power_up.rect.centerx, power_up.rect.centery,
                    cor_efeito, 60, 0.5, "pulso"
                )
            power_up.aplicar_efeito(self.jogador)
            self.pontuacao += 50

    def _tiro_ativo_jogador(self, tiro):
        """Verificar se tiro está ativo e é do jogador"""
        if hasattr(tiro, 'ativo') and not tiro.ativo:
            return False
        if hasattr(tiro, 'de_inimigo') and tiro.de_inimigo:
            return False
        return True

    def _processar_dano_inimigo(self, tiro, inimigo):
        """Processar dano em inimigo com efeitos visuais melhorados"""
        dano = getattr(tiro, 'dano', 25)
        tiro_especial = getattr(tiro, 'especial', False)

        # Registrar dano causado para progressão
        self.registrar_dano_causado(dano)

        # Determinar tipo de dano para efeitos
        tipo_dano = "critico" if tiro_especial else "normal"
        tipo_impacto = "critico" if tiro_especial else "inimigo"

        # Número de dano flutuante melhorado
        gerenciador_efeitos.criar_numero_flutuante(
            inimigo.rect.centerx, inimigo.rect.centery, dano, tipo_dano
        )

        # Efeito de impacto colorido
        gerenciador_efeitos.criar_efeito_impacto(
            inimigo.rect.centerx, inimigo.rect.centery, tipo_impacto
        )

        # Adicionar partículas 3D de impacto
        cor_impacto = (255, 150, 0) if tiro_especial else (255, 100, 0)
        sistema_particulas_3d.adicionar_impacto_tiro(
            inimigo.rect.centerx, inimigo.rect.centery, cor_impacto
        )

        # Screen shake baseado no tipo de dano
        intensidade_shake = 8 if tiro_especial else 5
        gerenciador_efeitos.ativar_screen_shake(intensidade_shake, 0.2)

        # Som de impacto em inimigo
        gerenciador_audio.tocar_som('impacto_inimigo', canal='impactos')

        # Feedback de combate quando inimigo recebe dano
        if self.feedback_combate:
            self.feedback_combate.criar_particulas_impacto(
                inimigo.rect.centerx, inimigo.rect.centery, "normal", 8
            )

        inimigo.receber_dano(dano, tiro_especial)
        tiro.kill()
        if inimigo.vida <= 0:
            self._processar_morte_inimigo(inimigo)

    def _verificar_game_over(self):
        """Verificar se o jogador morreu e iniciar respawn"""
        if self.jogador and hasattr(self.jogador, 'vida') and self.jogador.vida <= 0 and not self.jogador_morto:
            # Jogador morreu, iniciar processo de respawn
            self.jogador_morto = True
            self.tempo_respawn_restante = TEMPO_RESPAWN
            
            # Armazenar posição da morte se jogador tem rect
            if hasattr(self.jogador, 'rect') and self.jogador.rect:
                self.posicao_morte = (self.jogador.rect.centerx, self.jogador.rect.centery)
                
                # Efeito visual de morte
                gerenciador_efeitos.grupo_efeitos.add(EfeitoExplosao(
                    self.jogador.rect.centerx, self.jogador.rect.centery,
                    (255, 255, 255), 60, 1.0
                ))

                # Partículas 3D de morte
                sistema_particulas_3d.adicionar_explosao(
                    self.jogador.rect.centerx, self.jogador.rect.centery,
                    (255, 100, 100), 20
                )

                # Fazer o jogador desaparecer temporariamente
                self.jogador.rect.center = (-100, -100)  # Mover para fora da tela
            else:
                # Fallback se jogador não tem rect válido
                self.posicao_morte = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

            # Som de morte
            gerenciador_audio.tocar_som('impacto_jogador', canal='impactos')  # Dropar gemas se tiver coletado
            if self.gemas_coletadas > 0:
                self._dropar_gemas_morte()

        elif self.jogador_morto:
            # Processar respawn
            self._processar_respawn()

    def _fazer_inimigos_atirarem(self, dt):
        """Fazer inimigos atirarem"""
        for inimigo in self.inimigos:
            tiro = inimigo.tentar_atirar(dt)
            if tiro:
                self.todos_sprites.add(tiro)
                self.tiros.add(tiro)

    def _processar_morte_inimigo(self, inimigo):
        """Processar morte de inimigo"""
        # Registrar eliminação para progressão
        self.registrar_inimigo_eliminado()

        # Efeitos de feedback de combate para abate
        if self.feedback_combate:
            self.feedback_combate.processar_abate(inimigo.rect.centerx, inimigo.rect.centery)

        # Som de explosão quando inimigo morre (usando canal específico)
        gerenciador_audio.tocar_som('explosao', canal='impactos')

        # Efeito visual de morte do inimigo
        gerenciador_efeitos.grupo_efeitos.add(EfeitoParticulas(
            inimigo.rect.centerx, inimigo.rect.centery,
            (255, 0, 0), 15, 1.0, 60
        ))

        # Partículas 3D de morte do inimigo
        sistema_particulas_3d.adicionar_explosao(
            inimigo.rect.centerx, inimigo.rect.centery,
            (255, 50, 50), 18
        )

        self.pontuacao += 100

    def render(self):
        """Renderizar o jogo"""
        if self.estado == "selecao_personagem":
            self.seletor_personagem.render()
        elif self.estado == "menu_audio":
            self.menu_audio.render()
        elif self.estado == "vitoria":
            self.renderizar_jogo()  # Renderizar o jogo com a tela de vitória sobreposta
        else:
            self.renderizar_jogo()

    def renderizar_jogo(self):
        """Renderizar jogo principal com efeitos visuais melhorados"""
        # Obter offset de screen shake dos novos efeitos
        offset_shake = gerenciador_efeitos.obter_offset_camera()

        # Aplicar screen shake se ativo (combinando com feedback de combate)
        camera_offset = (0, 0)
        if self.feedback_combate:
            feedback_offset = self.feedback_combate.obter_offset_camera()
            camera_offset = (feedback_offset[0] + offset_shake[0],
                           feedback_offset[1] + offset_shake[1])
        else:
            camera_offset = offset_shake
        self.screen.fill(COR_FUNDO)        # Desenhar sombras primeiro (atrás de tudo) - apenas obstáculos
        if hasattr(self, 'gerenciador_ambiente'):
            # Não incluir personagens/inimigos pois eles já têm sombras próprias no renderer_3d
            objetos_com_sombra = list(self.obstaculos)
            self.gerenciador_ambiente.desenhar_sombras(self.screen, objetos_com_sombra)

        # Aplicar offset de camera para screen shake
        if camera_offset != (0, 0):
            # Criar superfície temporária para aplicar shake
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            temp_surface.fill(COR_FUNDO)

            # Desenhar tudo na superfície temporária primeiro
            self._renderizar_sprites_com_shake(temp_surface, camera_offset)

            # Depois desenhar a superfície na tela com offset
            self.screen.blit(temp_surface, camera_offset)
        else:
            self._renderizar_sprites_normal()

        # Renderizar efeitos de feedback de combate (sempre por último)
        if self.feedback_combate:
            self.feedback_combate.renderizar_particulas(self.screen, camera_offset)
            self.feedback_combate.renderizar_luzes(self.screen, camera_offset)
            self.feedback_combate.renderizar_flash_screen(self.screen)

        # Desenhar UI (sempre sem shake)
        self._renderizar_ui()

    def _renderizar_countdown_vitoria(self):
        """Renderizar o countdown de vitória na interface"""
        if self.vitoria_countdown_ativo:
            # Configurar fonte e cor
            fonte = pygame.font.Font(None, 36)
            texto = f"Vitória em: {int(self.tempo_vitoria_restante)}s"
            cor = (255, 215, 0)  # Dourado

            # Renderizar texto
            superficie_texto = fonte.render(texto, True, cor)
            posicao = (SCREEN_WIDTH // 2 - superficie_texto.get_width() // 2, 50)
            self.screen.blit(superficie_texto, posicao)
    def _renderizar_ui(self):
        """Renderizar elementos da interface"""
        if self.jogador:
            info_nivel = self.obter_info_nivel()
            self.ui.desenhar(self.screen, self.jogador, self.pontuacao, self.jogo_ativo,
            self.estado, info_nivel, self.gemas_coletadas, self.jogador_morto,
            self.tempo_respawn_restante, self.vitoria_countdown_ativo, self.tempo_vitoria_restante)

    def _renderizar_sprites_normal(self):
        """Renderizar sprites normalmente com sistema 3D"""
        # Renderizar obstáculos com visual 3D primeiro
        for obstaculo in self.obstaculos:
            eh_destrutivel = hasattr(obstaculo, 'vida_atual')
            dano_percentual = 0

            if eh_destrutivel:
                dano_percentual = 1.0 - (obstaculo.vida_atual / obstaculo.vida_maxima)
            cor_obstaculo = getattr(obstaculo, 'cor', (139, 90, 43))  # Marrom padrão
            renderer_3d.desenhar_obstaculo_3d(
                self.screen, obstaculo.rect,
                cor_obstaculo, eh_destrutivel, dano_percentual
            )        # Renderizar personagem principal com visual 3D
        if self.jogador and not self.jogador_morto:
            if hasattr(self.jogador, 'personagem') and self.jogador.personagem:
                # Atualizar estados de animação do personagem
                self.jogador.personagem.em_movimento = self.jogador.esta_movendo
                self.jogador.personagem.poder_ativo = len(self.jogador.efeitos_especiais) > 0

                self.jogador.personagem.render_3d(
                    self.screen, (int(self.jogador.pos_x), int(self.jogador.pos_y)), self.tempo_jogo
                )
            else:
                # Fallback para jogador sem personagem específico
                renderer_3d.desenhar_personagem_3d(
                    self.screen, (int(self.jogador.pos_x), int(self.jogador.pos_y)),
                    (0, 100, 255), (150, 200, 255), 30
                )        # Renderizar inimigos com visual 3D específico de cada Brawler
        for inimigo in self.inimigos:
            if hasattr(inimigo, 'personagem') and inimigo.personagem:    # Estados de animação já são atualizados no enemy.py
                inimigo.personagem.render_3d(
                    self.screen, (int(inimigo.pos_x), int(inimigo.pos_y)), self.tempo_jogo
                )
            else:
                # Fallback para inimigo genérico
                renderer_3d.desenhar_personagem_3d(
                    self.screen, (int(inimigo.pos_x), int(inimigo.pos_y)),
                    (255, 50, 50), (200, 80, 80), 30
                )

        # Renderizar gemas com visual 3D
        if hasattr(self, 'gerenciador_gemas') and self.gerenciador_gemas:
            for gema in self.gerenciador_gemas.gemas:
                renderer_3d.desenhar_gema_3d(
                    self.screen, (int(gema.x), int(gema.y)),
                    (0, 255, 100), 15, self.tempo_jogo
                )

        # Renderizar power-ups com visual 3D
        for power_up in self.power_ups:
            tipo = getattr(power_up, 'tipo', 'velocidade')
            renderer_3d.desenhar_power_up_3d(
                self.screen, power_up.rect.center,
                tipo, 18, self.tempo_jogo
            )

        # Renderizar apenas projéteis (únicos sprites 2D mantidos)
        for tiro in self.tiros:
            self.screen.blit(tiro.image, tiro.rect)

        # Renderizar partículas 3D
        sistema_particulas_3d.render(self.screen)        # Renderizar efeitos visuais tradicionais
        gerenciador_efeitos.draw(self.screen)
        self._renderizar_elementos_jogo()

        # Desenhar debug de colisões se ativo
        if getattr(self, 'debug_collision_system', False):
            self.desenhar_debug_colisoes()

    def _renderizar_sprites_com_shake(self, surface, _camera_offset):
        """Renderizar sprites com screen shake usando sistema 3D"""
        # Renderizar obstáculos com visual 3D primeiro
        for obstaculo in self.obstaculos:
            eh_destrutivel = hasattr(obstaculo, 'vida_atual')
            dano_percentual = 0

            if eh_destrutivel:
                dano_percentual = 1.0 - (obstaculo.vida_atual / obstaculo.vida_maxima)
            cor_obstaculo = getattr(obstaculo, 'cor', (139, 90, 43))  # Marrom padrão
            renderer_3d.desenhar_obstaculo_3d(
                surface, obstaculo.rect,
                cor_obstaculo, eh_destrutivel, dano_percentual
            )        # Renderizar personagem principal com visual 3D
        if self.jogador and not self.jogador_morto:
            if hasattr(self.jogador, 'personagem') and self.jogador.personagem:
                # Atualizar estados de animação do personagem
                self.jogador.personagem.em_movimento = self.jogador.esta_movendo
                self.jogador.personagem.poder_ativo = len(self.jogador.efeitos_especiais) > 0

                self.jogador.personagem.render_3d(
                    surface, (int(self.jogador.pos_x), int(self.jogador.pos_y)), self.tempo_jogo
                )
            else:
                # Fallback para jogador sem personagem específico
                renderer_3d.desenhar_personagem_3d(
                    surface, (int(self.jogador.pos_x), int(self.jogador.pos_y)),
                    (0, 100, 255), (150, 200, 255), 30
                )

        # Renderizar inimigos com visual 3D específico de cada Brawler
        for inimigo in self.inimigos:
            if hasattr(inimigo, 'personagem') and inimigo.personagem:                # Estados de animação já são atualizados no enemy.py
                inimigo.personagem.render_3d(
                    surface, (int(inimigo.pos_x), int(inimigo.pos_y)), self.tempo_jogo
                )
            else:
                # Fallback para inimigo genérico
                renderer_3d.desenhar_personagem_3d(
                    surface, (int(inimigo.pos_x), int(inimigo.pos_y)),
                    (255, 50, 50), (200, 80, 80), 30
                )

        # Renderizar gemas com visual 3D
        if hasattr(self, 'gerenciador_gemas') and self.gerenciador_gemas:
            for gema in self.gerenciador_gemas.gemas:
                renderer_3d.desenhar_gema_3d(
                    surface, (int(gema.x), int(gema.y)),
                    (0, 255, 100), 15, self.tempo_jogo
                )

        # Renderizar power-ups com visual 3D
        for power_up in self.power_ups:
            tipo = getattr(power_up, 'tipo', 'velocidade')
            renderer_3d.desenhar_power_up_3d(
                surface, power_up.rect.center,
                tipo, 18, self.tempo_jogo
            )

        # Renderizar apenas projéteis (únicos sprites 2D mantidos)
        for tiro in self.tiros:
            surface.blit(tiro.image, tiro.rect)

        self._renderizar_elementos_jogo_em_surface(surface)

    def _renderizar_elementos_jogo(self):
        """Renderizar elementos do jogo (gemas, arbustos, efeitos, etc.)"""
        # Desenhar gemas
        if self.gerenciador_gemas:
            self.gerenciador_gemas.render(self.screen)        # Desenhar arbustos
        if hasattr(self, 'gerenciador_arbustos'):
            self.gerenciador_arbustos.desenhar(self.screen)

        # Desenhar efeitos visuais
        gerenciador_efeitos.draw(self.screen)

        # Desenhar partículas ambientais
        if hasattr(self, 'gerenciador_ambiente'):
            self.gerenciador_ambiente.desenhar_particulas_ambiente(self.screen)
            self.gerenciador_ambiente.desenhar_particulas_clima(self.screen)

        # Desenhar barras de vida dos inimigos
        for inimigo in self.inimigos:
            inimigo.draw_vida(self.screen)

        # Desenhar debug do sistema de colisões (se ativado)
        self.desenhar_debug_colisoes()

        # Desenhar informações de debug do ambiente (se ativado)
        if hasattr(self, 'gerenciador_ambiente') and self.gerenciador_ambiente.debug_ativo:
            fonte_debug = pygame.font.Font(None, 24)
            self.gerenciador_ambiente.desenhar_info_debug(self.screen, fonte_debug)

        # Aplicar overlay de iluminação (dia/noite)
        if hasattr(self, 'gerenciador_ambiente'):
            self.gerenciador_ambiente.aplicar_overlay_iluminacao(self.screen)

        # Desenhar UI
        if self.jogador:
            info_nivel = self.obter_info_nivel()
            self.ui.desenhar(self.screen, self.jogador, self.pontuacao, self.jogo_ativo,
            self.estado, info_nivel, self.gemas_coletadas, self.jogador_morto,
            self.tempo_respawn_restante, self.vitoria_countdown_ativo, self.tempo_vitoria_restante)

    def _desenhar_sprite_com_efeito_arbusto(self, sprite):
        """
        Desenhar sprite aplicando efeito de transparência se estiver em arbusto.
        Args:
            sprite: Sprite a ser desenhado
        """        # Verificar se está em arbusto e aplicar transparência
        if (hasattr(self, 'gerenciador_arbustos') and
            hasattr(sprite, 'rect') and
            sprite in self.inimigos and
            self.gerenciador_arbustos.entidade_esta_em_arbusto(sprite)):

            # Criar superfície temporária com transparência
            temp_surface = sprite.image.copy()
            temp_surface.set_alpha(100)  # 100/255 = ~39% de opacidade
            self.screen.blit(temp_surface, sprite.rect)
        else:
            # Desenhar normalmente
            self.screen.blit(sprite.image, sprite.rect)

    def _desenhar_sprite_com_efeito_arbusto_em_surface(self, sprite, surface):
        """Desenhar sprite com efeito de arbusto em uma superfície específica"""
        if hasattr(self, 'gerenciador_arbustos'):            # Por enquanto, apenas desenha o sprite normalmente na superfície
            surface.blit(sprite.image, sprite.rect)
        else:
            surface.blit(sprite.image, sprite.rect)

    def _renderizar_elementos_jogo_em_surface(self, surface):
        """Renderizar elementos do jogo em uma superfície específica"""
        if not surface:
            return

        # Renderizar todos os sprites na superfície fornecida
        if hasattr(self, 'todos_sprites') and self.todos_sprites:
            self.todos_sprites.draw(surface)

        # Note: UI não é renderizada em superfícies temporárias para evitar problemas de argumentos

    def criar_projetil_otimizado(self, x, y, direcao_x, direcao_y, dano=25, velocidade=400, de_inimigo=False, tipo_tiro="normal"):
        """
        Criar projétil usando object pool para melhor performance.
        Args:
            x: Posição X inicial
            y: Posição Y inicial
            direcao_x: Direção X do movimento
            direcao_y: Direção Y do movimento
            dano: Dano causado pelo projétil
            velocidade: Velocidade do projétil
            de_inimigo: Se o projétil é de um inimigo
            tipo_tiro: Tipo de projétil (normal, shotgun, sniper, etc.)
        Returns:
            Projétil criado ou None se pool estiver indisponível        """
        if hasattr(self, 'projectile_pool') and self.projectile_pool:
            bullet = self.projectile_pool.get_bullet(x, y, direcao_x, direcao_y, dano, velocidade, de_inimigo, tipo_tiro)
            if bullet:
                # Adicionar aos grupos necessários
                self.todos_sprites.add(bullet)
                self.tiros.add(bullet)
                return bullet  # Fallback para criação tradicional se pool não estiver disponível

        bullet = Bullet(x, y, direcao_x, direcao_y, de_inimigo, dano)
        self.todos_sprites.add(bullet)
        self.tiros.add(bullet)
        return bullet

    def desenhar_debug_colisoes(self):
        """Desenhar informações de debug do sistema de colisões."""
        if self.debug_collision_system and hasattr(self, 'collision_optimizer'):
            # Desenhar QuadTree para visualização
            self.collision_optimizer.quadtree.draw_debug(self.screen, (0, 255, 0), 1)

            # Mostrar estatísticas do pool na tela
            if hasattr(self, 'projectile_pool'):
                stats = self.projectile_pool.get_stats() # Criar fonte para debug se não existir
                if self.debug_font is None:
                    self.debug_font = pygame.font.Font(None, 20)

                # Mostrar estatísticas na tela
                y_pos = 50
                for key, value in stats.items():
                    text = f"{key}: {value}"
                    text_surface = self.debug_font.render(text, True, (255, 255, 255))
                    # Fundo escuro para legibilidade
                    bg_rect = pygame.Rect(10, y_pos - 2, text_surface.get_width() + 4, text_surface.get_height() + 4)
                    pygame.draw.rect(self.screen, (0, 0, 0, 128), bg_rect)
                    self.screen.blit(text_surface, (12, y_pos))
                    y_pos += 25

    def criar_novo_inimigo(self):
        """Criar um novo inimigo quando um for eliminado"""
        tentativas = 0
        max_tentativas = 20

        while tentativas < max_tentativas:
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)

            # Verificar se não está muito perto do jogador
            if self.jogador:
                distancia_jogador = ((x - self.jogador.rect.centerx) ** 2 + (y - self.jogador.rect.centery) ** 2) ** 0.5
                if distancia_jogador > 200:  # Distância mínima do jogador
                    # Verificar se não está colidindo com obstáculos
                    temp_rect = pygame.Rect(x - TAMANHO_JOGADOR // 2, y - TAMANHO_JOGADOR // 2,
                                          TAMANHO_JOGADOR, TAMANHO_JOGADOR)

                    colidiu = False
                    for obstaculo in self.obstaculos:
                        if temp_rect.colliderect(obstaculo.rect):
                            colidiu = True
                            break

                    if not colidiu:
                        inimigo = Enemy(
                            x, y,
                            self.jogador,
                            self.velocidade_inimigos_atual,
                            self.multiplicador_tiro_atual
                        )
                        # Definir referência do sistema de arbustos
                        if hasattr(self, 'gerenciador_arbustos'):
                            inimigo.gerenciador_arbustos = self.gerenciador_arbustos

                        self.todos_sprites.add(inimigo)
                        self.inimigos.add(inimigo)
                        return  # Inimigo criado com sucesso

            tentativas += 1

    def _atualizar_sistema_gemas(self, dt):
        """Atualizar sistema de gemas e verificar coletas"""
        if not self.gerenciador_gemas:
            return

        # Atualizar gerenciador de gemas
        self.gerenciador_gemas.update(dt)

        # Verificar coleta de gemas pelo jogador
        if self.jogador and hasattr(self.jogador, 'rect') and self.jogador.rect:
            gemas_coletadas = self.gerenciador_gemas.coletar_gemas(
                self.jogador.rect.centerx,
                self.jogador.rect.centery
            )

            if gemas_coletadas > 0:
                self.gemas_coletadas += gemas_coletadas
                self.pontuacao += gemas_coletadas * PONTOS_POR_GEMA

                # Criar efeito visual de coleta
                efeito = EfeitoColetaGema(
                    self.jogador.rect.centerx,
                    self.jogador.rect.centery
                )
                gerenciador_efeitos.adicionar_efeito(efeito)

                # Partículas 3D de coleta de gema
                sistema_particulas_3d.adicionar_coleta_gema(
                    self.jogador.rect.centerx,
                    self.jogador.rect.centery
                )

                # Som de coleta (quando implementado)
                # gerenciador_audio.tocar_som('gem_collect')

                # Verificar vitória
                if self.gemas_coletadas >= GEMAS_PARA_VITORIA:
                    self._processar_vitoria()

    def _processar_vitoria(self):
        """Processar vitória do jogador por coletar gemas suficientes"""
        # Ativar animação de celebração de vitória do jogador
        if self.jogador:
            self.jogador.celebrar_vitoria()

        # Transição para estado de vitória
        self.estado = "vitoria"
        self.vitoria_alcancada = True

        # Tocar música de vitória
        gerenciador_audio.tocar_som('vitoria_jogo')        # Criar efeitos especiais de vitória em toda a tela
        if self.jogador and hasattr(self.jogador, 'rect') and self.jogador.rect:
            gerenciador_efeitos.criar_efeito_vitoria(
                self.jogador.rect.centerx,
                self.jogador.rect.centery,
                getattr(self.jogador.personagem, 'nome', 'Jogador') if hasattr(self.jogador, 'personagem') else 'Jogador'
            )        # Registrar vitória na progressão
        try:
            if hasattr(sistema_progressao, 'processar_fim_partida') and self.personagem_selecionado:
                # Calcular tempo da partida em segundos
                tempo_partida = (pygame.time.get_ticks() - self.tempo_inicio_partida) / 1000.0 if hasattr(self, 'tempo_inicio_partida') else 0
                
                # Estatísticas da partida
                stats = {
                    'dano_causado': getattr(self, 'dano_total_causado', 0),
                    'dano_recebido': getattr(self, 'dano_total_recebido', 0),
                    'inimigos_eliminados': getattr(self, 'inimigos_eliminados', 0),
                    'gemas_coletadas': getattr(self, 'gemas_coletadas', 0),
                    'tempo_sobrevivencia_total': tempo_partida
                }
                
                sistema_progressao.processar_fim_partida(
                    self.personagem_selecionado.nome,
                    True,  # Vitória
                    tempo_partida,
                    **stats
                )
        except (AttributeError, NameError):
            pass  # Sistema de progressão não disponível

        # Por enquanto, apenas continua o jogo após uma pausa
        # Reset do contador para continuar jogando depois de mostrar celebração
        # self.gemas_coletadas = 0
        # if self.gerenciador_gemas:
        #     self.gerenciador_gemas.reset()

    def _dropar_gemas_morte(self):
        """Dropar gemas quando o jogador morre"""
        if self.gerenciador_gemas and self.posicao_morte:
            # Dropar gemas na posição da morte
            x, y = self.posicao_morte
            quantidade_dropar = min(self.gemas_coletadas, 5)  # Máximo 5 gemas

            for i in range(quantidade_dropar):
                # Espalhar gemas em círculo ao redor da posição de morte
                angulo = (i / quantidade_dropar) * 2 * 3.14159
                offset_x = 30 * math.cos(angulo)
                offset_y = 30 * math.sin(angulo)
                self.gerenciador_gemas.dropar_gema(x + offset_x, y + offset_y)

            # Reduzir gemas coletadas
            self.gemas_coletadas -= quantidade_dropar
            if self.gemas_coletadas < 0:
                self.gemas_coletadas = 0

    def _processar_respawn(self):
        """Processar timer de respawn e reaparecer jogador"""
        if self.tempo_respawn_restante > 0:
            self.tempo_respawn_restante -= 1/60.0  # Assumindo 60 FPS
            return

        # Tempo de respawn acabou, respawnar jogador
        self._respawnar_jogador()

    def _respawnar_jogador(self):
        """Respawnar o jogador em uma posição segura"""
        posicao_respawn = self._encontrar_posicao_respawn_segura()
        if posicao_respawn and self.jogador and hasattr(self.jogador, 'rect') and self.jogador.rect:
            # Restaurar jogador
            self.jogador.rect.center = posicao_respawn
            if hasattr(self.jogador, 'pos_x'):
                self.jogador.pos_x = float(posicao_respawn[0])
            if hasattr(self.jogador, 'pos_y'):
                self.jogador.pos_y = float(posicao_respawn[1])
            if hasattr(self.jogador, 'vida') and hasattr(self.jogador, 'vida_maxima'):
                self.jogador.vida = int(self.jogador.vida_maxima * VIDA_RESPAWN_PERCENTUAL)

            # Resetar estado
            self.jogador_morto = False
            self.tempo_respawn_restante = 0.0
            self.posicao_morte = None

            # Efeito visual de respawn
            gerenciador_efeitos.grupo_efeitos.add(EfeitoOndas(
                posicao_respawn[0], posicao_respawn[1],
                (0, 255, 255), 3, 1.0
            ))

            # Partículas 3D de respawn
            sistema_particulas_3d.adicionar_explosao(
                posicao_respawn[0], posicao_respawn[1],
                (0, 255, 255), 20
            )

            # Som de respawn
            gerenciador_audio.tocar_som('powerup_vida', canal='power_ups')

    def _encontrar_posicao_respawn_segura(self):
        """Encontrar uma posição segura para respawn"""

        # Definir áreas de respawn (cantos do mapa)
        areas_respawn = [
            (AREA_RESPAWN_MARGEM, AREA_RESPAWN_MARGEM),  # Canto superior esquerdo
            (SCREEN_WIDTH - AREA_RESPAWN_MARGEM, AREA_RESPAWN_MARGEM),  # Superior direito
            (AREA_RESPAWN_MARGEM, SCREEN_HEIGHT - AREA_RESPAWN_MARGEM),  # Inferior esquerdo
            (SCREEN_WIDTH - AREA_RESPAWN_MARGEM, SCREEN_HEIGHT - AREA_RESPAWN_MARGEM)  # Inferior direito
        ]

        # Tentar cada área de respawn
        for x, y in areas_respawn:
            if self._posicao_respawn_segura(x, y):
                return (x, y)

        # Se nenhuma área segura, usar centro do mapa como fallback
        return (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def _posicao_respawn_segura(self, x, y):
        """Verificar se uma posição é segura para respawn"""
        # Criar rect temporário para verificar colisões
        temp_rect = pygame.Rect(x - TAMANHO_JOGADOR // 2, y - TAMANHO_JOGADOR // 2,
                               TAMANHO_JOGADOR, TAMANHO_JOGADOR)
        # Verificar colisão com obstáculos
        for obstaculo in self.obstaculos:
            if temp_rect.colliderect(obstaculo.rect):
                return False

        # Verificar distância dos inimigos
        for inimigo in self.inimigos:
            distancia = math.sqrt((x - inimigo.rect.centerx) ** 2 + (y - inimigo.rect.centery) ** 2)
            if distancia < DISTANCIA_MINIMA_INIMIGOS_RESPAWN:
                return False
        return True

    def _verificar_vitoria_gemas(self):
        """Verificar condições de vitória por gemas"""
        if self.vitoria_alcancada:
            return

        # Verificar se tem gemas suficientes para vitória
        if self.gemas_coletadas >= GEMAS_PARA_VITORIA:
            if not self.vitoria_countdown_ativo:
                # Iniciar countdown de vitória
                self.vitoria_countdown_ativo = True
                self.tempo_vitoria_restante = TEMPO_COUNTDOWN_VITORIA
                gerenciador_audio.tocar_som('powerup_vida', canal='ui') # Som de início do countdown
        else:
            # Se perdeu gemas, cancelar countdown
            if self.vitoria_countdown_ativo:
                self.vitoria_countdown_ativo = False
                self.tempo_vitoria_restante = 0.0

    def _processar_countdown_vitoria(self):
        """Processar timer de countdown de vitória"""
        if not self.vitoria_countdown_ativo:
            return

        # Atualizar timer
        self.tempo_vitoria_restante -= 1/60.0  # Assumindo 60 FPS

        # Verificar se ainda tem gemas suficientes
        if self.gemas_coletadas < GEMAS_PARA_VITORIA:
            self.vitoria_countdown_ativo = False
            self.tempo_vitoria_restante = 0.0
            return

        # Verificar se countdown terminou
        if self.tempo_vitoria_restante <= 0:
            self._vitoria_alcancada()

    def _vitoria_alcancada(self):
        """Processar vitória do jogador"""
        self.vitoria_alcancada = True
        self.vitoria_countdown_ativo = False
        self.estado = "vitoria"

        # Processar progressão
        self._processar_progressao_fim_partida(True)

        # Parar música de batalha e tocar música de vitória
        gerenciador_audio.parar_musica()
        gerenciador_audio.tocar_som('powerup_vida', canal='ui')  # Som de vitória

        # Efeito visual de vitória
        if self.jogador and hasattr(self.jogador, 'rect') and self.jogador.rect:
            gerenciador_efeitos.grupo_efeitos.add(EfeitoExplosao(
                self.jogador.rect.centerx, self.jogador.rect.centery,
                (255, 215, 0), 5, 2.0  # Explosão dourada
            ))

            # Partículas 3D de vitória
            sistema_particulas_3d.adicionar_explosao(
                self.jogador.rect.centerx, self.jogador.rect.centery,
                (255, 215, 0), 30  # Explosão dourada intensa
            )
            sistema_particulas_3d.adicionar_explosao(
                self.jogador.rect.centerx, self.jogador.rect.centery,
                (255, 255, 0), 25  # Explosão amarela adicional
            )

    def verificar_conquistas(self):
        """Verifica e desbloqueia conquistas com base no estado atual do jogo."""
        if not self.jogador:
            return
            
        contexto = {
            'gemas_coletadas': self.gemas_coletadas,  # Usar atributo do game ao invés do jogador
            'inimigos_derrotados': self.inimigos_eliminados,  # Usar atributo do game
            'super_usada': getattr(self.jogador, 'super_usada', 0) if hasattr(self.jogador, 'super_usada') else 0
        }
        desbloqueadas = self.sistema_conquistas.verificar_conquistas(contexto)
        for conquista in desbloqueadas:
            print(f"Conquista desbloqueada: {conquista.nome} - {conquista.descricao}")
            if hasattr(self.ui, 'exibir_notificacao'):
                self.ui.exibir_notificacao(f"Conquista desbloqueada: {conquista.nome}")

    def _processar_progressao_fim_partida(self, vitoria):
        """Processa a progressão do Brawler ao fim da partida"""
        if not self.personagem_selecionado:
            return

        # Calcular tempo da partida em segundos
        tempo_partida = (pygame.time.get_ticks() - self.tempo_inicio_partida) / 1000.0

        # Estatísticas da partida
        stats = {
            'dano_causado': self.dano_total_causado,
            'dano_recebido': self.dano_total_recebido,
            'inimigos_eliminados': self.inimigos_eliminados,
            'gemas_coletadas': self.gemas_coletadas,
            'tempo_sobrevivencia_total': tempo_partida
        }

        # Processar progressão
        resultado = sistema_progressao.processar_fim_partida(
            self.personagem_selecionado.nome,
            vitoria,
            tempo_partida,
            **stats
        )

        # Armazenar resultado para mostrar na tela
        self.resultado_progressao = resultado

        print("\n=== FIM DE PARTIDA ===")
        print(f"Personagem: {self.personagem_selecionado.nome}")
        print(f"Resultado: {'VITÓRIA' if vitoria else 'DERROTA'}")
        print(f"Experiência ganha: +{resultado['exp_ganha']} EXP")
        print(f"Troféus: {resultado['trofeus_mudanca']:+d} (Total: {resultado['novos_trofeus']})")
        if resultado['subiu_nivel']:
            print(f"🎉 NÍVEL AUMENTOU! Agora é nível {resultado['novo_nivel']}")
        print(f"Tempo de partida: {tempo_partida:.1f}s")
        print(f"Dano causado: {self.dano_total_causado}")
        print(f"Inimigos eliminados: {self.inimigos_eliminados}")
        print(f"Gemas coletadas: {self.gemas_coletadas}")

    def registrar_dano_causado(self, dano):
        """Registra dano causado pelo jogador"""
        self.dano_total_causado += dano

    def registrar_inimigo_eliminado(self):
        """Registra eliminação de inimigo"""
        self.inimigos_eliminados += 1

    def registrar_dano_recebido(self, dano):
        """Registra dano recebido pelo jogador"""
        self.dano_total_recebido += dano

    def _mostrar_estatisticas_performance(self):
        """Mostrar estatísticas de performance do jogo na console"""
        print("\n=== ESTATÍSTICAS DE PERFORMANCE ===")

        # Estatísticas gerais
        print(f"Sprites ativos: {len(self.todos_sprites)}")
        print(f"Inimigos: {len(self.inimigos)}")
        print(f"Projéteis: {len(self.tiros)}")
        print(f"Power-ups: {len(self.power_ups)}")
        print(f"Obstáculos: {len(self.obstaculos)}")

        # Estatísticas do pool de projéteis
        if hasattr(self, 'projectile_pool'):
            stats = self.projectile_pool.get_stats()
            print("\n--- Pool de Projéteis ---")
            for key, value in stats.items():
                print(f"{key}: {value}")

        # Estatísticas do sistema de colisões
        if hasattr(self, 'collision_optimizer'):
            print("\n--- Sistema de Colisões ---")
            print(f"QuadTree inicializado: {self.collision_optimizer.quadtree is not None}")

        # Estatísticas do ambiente
        if hasattr(self, 'gerenciador_ambiente'):
            print("\n--- Sistema de Ambiente ---")
            print(f"Tipo de mapa: {self.gerenciador_ambiente.tipo_mapa}")
            print(f"Clima atual: {self.gerenciador_ambiente.clima_atual}")
            print(f"Período do dia: {getattr(self.gerenciador_ambiente, 'periodo_dia', 'N/A')}")

        # Estatísticas de gameplay
        print("\n--- Gameplay ---")
        print(f"Nível atual: {self.nivel_atual}")
        print(f"Pontuação: {self.pontuacao}")
        print(f"Gemas coletadas: {self.gemas_coletadas}")
        print(f"Tempo de jogo: {self.tempo_jogo:.1f}s")
        print("=====================================\n")
