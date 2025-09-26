"""
Sistema de Feedback de Combate do Brawl Stars Clone.
Este módulo implementa efeitos visuais e táteis de combate para melhorar
a experiência do jogador, incluindo screen shake, slow motion, partículas
de impacto e efeitos de luz dinâmicos durante confrontos.
"""

import math
import random
import pygame
from src.pygame_constants import SRCALPHA

class FeedbackCombate:
    """Gerenciador de feedback visual e tátil de combate"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Screen Shake
        self.shake_intensidade = 0.0
        self.shake_duracao = 0.0
        self.shake_tempo = 0.0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0

        # Slow Motion
        self.slow_motion_ativo = False
        self.slow_motion_fator = 1.0
        self.slow_motion_duracao = 0.0
        self.slow_motion_tempo = 0.0
        self.slow_motion_target = 1.0

        # Partículas de Impacto
        self.particulas_impacto = []
        self.particulas_sangue = []

        # Efeitos de Luz
        self.luzes_dinamicas = []
        self.flash_screen = 0.0
        self.tempo_flash = 0.0

        # Cache de superfícies para otimização
        self.cache_particulas = {}

    def iniciar_screen_shake(self, intensidade, duracao):
        """Inicia efeito de screen shake"""
        self.shake_intensidade = max(self.shake_intensidade, intensidade)
        self.shake_duracao = max(self.shake_duracao, duracao)
        self.shake_tempo = 0.0

    def iniciar_slow_motion(self, fator, duracao):
        """Inicia efeito de slow motion"""
        self.slow_motion_ativo = True
        self.slow_motion_target = fator
        self.slow_motion_duracao = duracao
        self.slow_motion_tempo = 0.0

    def criar_particulas_impacto(self, x, y, tipo="normal", quantidade=15):
        """Cria partículas de impacto na posição especificada"""
        cores_base = {
            "normal": [(255, 255, 0), (255, 200, 0), (255, 150, 0)],  # Amarelo/Laranja
            "critico": [(255, 0, 0), (255, 100, 100), (200, 0, 0)],   # Vermelho
            "explosao": [(255, 255, 255), (255, 200, 0), (255, 100, 0)] # Branco/Laranja
        }
        cores = cores_base.get(tipo, cores_base["normal"])
        for _ in range(quantidade):
            particula = {
                'x': x + random.uniform(-5, 5),
                'y': y + random.uniform(-5, 5),
                'vel_x': random.uniform(-100, 100),
                'vel_y': random.uniform(-100, -20),
                'cor': random.choice(cores),
                'tamanho': random.uniform(2, 6),
                'vida': random.uniform(0.3, 0.8),
                'vida_max': random.uniform(0.3, 0.8),
                'gravidade': random.uniform(150, 300),
                'tipo': tipo
            }
            particula['vida_max'] = particula['vida']
            self.particulas_impacto.append(particula)

    def criar_particulas_sangue(self, x, y, direcao_x=0, direcao_y=0, quantidade=8):
        """Cria partículas de sangue (efeito estilizado, não gráfico)"""
        cores_sangue = [(139, 0, 0), (165, 42, 42), (128, 0, 0)]
        for _ in range(quantidade):
            angulo = random.uniform(0, 2 * math.pi)
            velocidade = random.uniform(50, 150)
            particula = {
                'x': x,
                'y': y,
                'vel_x': math.cos(angulo) * velocidade + direcao_x * 50,
                'vel_y': math.sin(angulo) * velocidade + direcao_y * 50,
                'cor': random.choice(cores_sangue),
                'tamanho': random.uniform(1, 3),
                'vida': random.uniform(0.5, 1.2),
                'vida_max': random.uniform(0.5, 1.2),
                'gravidade': random.uniform(100, 200)
            }
            particula['vida_max'] = particula['vida']
            self.particulas_sangue.append(particula)

    def criar_luz_dinamica(self, x, y, cor, intensidade, duracao, tipo="pulso"):
        """Cria uma luz dinâmica"""
        luz = {
            'x': x,
            'y': y,
            'cor': cor,
            'intensidade': intensidade,
            'intensidade_max': intensidade,
            'duracao': duracao,
            'tempo': 0.0,
            'tipo': tipo,
            'raio': intensidade * 2
        }
        self.luzes_dinamicas.append(luz)

    def criar_flash_screen(self, intensidade, duracao):
        """Cria um flash na tela inteira"""
        self.flash_screen = max(self.flash_screen, intensidade)
        self.tempo_flash = max(self.tempo_flash, duracao)

    def processar_abate(self, x, y):
        """Processa efeitos especiais de abate"""
        # Screen shake intenso
        self.iniciar_screen_shake(15.0, 0.4)
        # Slow motion dramático
        self.iniciar_slow_motion(0.3, 0.6)
        # Partículas de impacto crítico
        self.criar_particulas_impacto(x, y, "critico", 25)
        # Flash branco
        self.criar_flash_screen(0.6, 0.3)
        # Luz dinâmica dourada
        self.criar_luz_dinamica(x, y, (255, 215, 0), 100, 0.8, "explosion")

    def processar_explosao(self, x, y, tamanho="normal"):
        """Processa efeitos de explosão"""
        intensidades = {
            "pequeno": (8.0, 0.2, 15),
            "normal": (12.0, 0.3, 20),
            "grande": (20.0, 0.5, 30)
        }
        shake_int, shake_dur, particulas = intensidades.get(tamanho, intensidades["normal"])
        # Screen shake baseado no tamanho
        self.iniciar_screen_shake(shake_int, shake_dur)
        # Partículas de explosão
        self.criar_particulas_impacto(x, y, "explosao", particulas)
        # Flash baseado no tamanho
        flash_intensidade = 0.3 if tamanho == "pequeno" else 0.5 if tamanho == "normal" else 0.7
        self.criar_flash_screen(flash_intensidade, 0.2)
        # Luz de explosão
        cor_luz = (255, 255, 200) if tamanho == "pequeno" else (255, 200, 100)
        self.criar_luz_dinamica(x, y, cor_luz, 80, 0.4, "explosion")

    def update(self, dt):
        """Atualiza todos os efeitos de feedback"""
        # Ajustar dt baseado no slow motion
        dt_real = dt
        if self.slow_motion_ativo:
            dt = dt * self.slow_motion_fator
        # Atualizar screen shake
        if self.shake_duracao > 0:
            self.shake_tempo += dt_real
            progresso = self.shake_tempo / self.shake_duracao
            if progresso >= 1.0:
                self.shake_duracao = 0.0
                self.shake_intensidade = 0.0
                self.shake_offset_x = 0.0
                self.shake_offset_y = 0.0
            else:
                # Shake com decay exponencial
                intensidade_atual = self.shake_intensidade * (1.0 - progresso)
                self.shake_offset_x = random.uniform(-intensidade_atual, intensidade_atual)
                self.shake_offset_y = random.uniform(-intensidade_atual, intensidade_atual)
        # Atualizar slow motion
        if self.slow_motion_ativo:
            self.slow_motion_tempo += dt_real
            if self.slow_motion_tempo >= self.slow_motion_duracao:
                self.slow_motion_ativo = False
                self.slow_motion_fator = 1.0
            else:
                # Transição suave de volta ao normal
                progresso = self.slow_motion_tempo / self.slow_motion_duracao
                if progresso > 0.7:  # Começar a voltar ao normal após 70% do tempo
                    fade_progresso = (progresso - 0.7) / 0.3
                    self.slow_motion_fator = self.slow_motion_target + (1.0 - self.slow_motion_target) * fade_progresso
                else:
                    self.slow_motion_fator = self.slow_motion_target
        # Atualizar partículas de impacto
        for particula in self.particulas_impacto[:]:
            particula['vida'] -= dt
            if particula['vida'] <= 0:
                self.particulas_impacto.remove(particula)
                continue

            # Física da partícula
            particula['vel_y'] += particula['gravidade'] * dt
            particula['x'] += particula['vel_x'] * dt
            particula['y'] += particula['vel_y'] * dt

            # Fade baseado na vida restante
            fade = particula['vida'] / particula['vida_max']
            particula['alpha'] = int(255 * fade)
            particula['tamanho_atual'] = particula['tamanho'] * fade
        # Atualizar partículas de sangue
        for particula in self.particulas_sangue[:]:
            particula['vida'] -= dt
            if particula['vida'] <= 0:
                self.particulas_sangue.remove(particula)
                continue

            # Física da partícula
            particula['vel_y'] += particula['gravidade'] * dt
            particula['x'] += particula['vel_x'] * dt
            particula['y'] += particula['vel_y'] * dt

            # Fade
            fade = particula['vida'] / particula['vida_max']
            particula['alpha'] = int(255 * fade)
            particula['tamanho_atual'] = particula['tamanho'] * fade

        # Atualizar luzes dinâmicas
        for luz in self.luzes_dinamicas[:]:
            luz['tempo'] += dt
            if luz['tempo'] >= luz['duracao']:
                self.luzes_dinamicas.remove(luz)
                continue
            progresso = luz['tempo'] / luz['duracao']
            if luz['tipo'] == "pulso":
                luz['intensidade'] = luz['intensidade_max'] * (1.0 - progresso)
            elif luz['tipo'] == "explosion":
                # Explosão rápida seguida de fade lento
                if progresso < 0.2:
                    luz['intensidade'] = luz['intensidade_max'] * (1.0 + progresso * 2)
                else:
                    fade = (progresso - 0.2) / 0.8
                    luz['intensidade'] = luz['intensidade_max'] * (1.0 - fade * 0.8)

        # Atualizar flash screen
        if self.tempo_flash > 0:
            self.tempo_flash -= dt_real
            if self.tempo_flash <= 0:
                self.flash_screen = 0.0
            else:
                # Fade out suave
                self.flash_screen *= 0.95

    def obter_offset_camera(self):
        """Retorna o offset da câmera para screen shake"""
        return (self.shake_offset_x, self.shake_offset_y)

    def obter_fator_tempo(self):
        """Retorna o fator de tempo atual (para slow motion)"""
        return self.slow_motion_fator

    def renderizar_particulas(self, screen, camera_offset=(0, 0)):
        """Renderiza todas as partículas na tela"""
        # Renderizar partículas de impacto
        for particula in self.particulas_impacto:
            if hasattr(particula, 'alpha') and particula['alpha'] > 0:
                x = int(particula['x'] - camera_offset[0])
                y = int(particula['y'] - camera_offset[1])
                tamanho = max(1, int(particula['tamanho_atual']))

                # Criar superfície com alpha para a partícula
                surf = pygame.Surface((tamanho * 2, tamanho * 2), SRCALPHA)
                cor_com_alpha = (*particula['cor'], particula['alpha'])
                pygame.draw.circle(surf, cor_com_alpha, (tamanho, tamanho), tamanho)
                screen.blit(surf, (x - tamanho, y - tamanho))

        # Renderizar partículas de sangue
        for particula in self.particulas_sangue:
            if hasattr(particula, 'alpha') and particula['alpha'] > 0:
                x = int(particula['x'] - camera_offset[0])
                y = int(particula['y'] - camera_offset[1])
                tamanho = max(1, int(particula['tamanho_atual']))

                surf = pygame.Surface((tamanho * 2, tamanho * 2), SRCALPHA)
                cor_com_alpha = (*particula['cor'], particula['alpha'])
                pygame.draw.circle(surf, cor_com_alpha, (tamanho, tamanho), tamanho)
                screen.blit(surf, (x - tamanho, y - tamanho))

    def renderizar_luzes(self, screen, camera_offset=(0, 0)):
        """Renderiza efeitos de luz dinâmicos"""
        for luz in self.luzes_dinamicas:
            if luz['intensidade'] > 0:
                x = int(luz['x'] - camera_offset[0])
                y = int(luz['y'] - camera_offset[1])
                raio = int(luz['raio'])
                intensidade = min(255, int(luz['intensidade'])) # Criar gradiente radial para a luz
                tamanho = raio * 2
                surf_luz = pygame.Surface((tamanho, tamanho), SRCALPHA)
                for r in range(raio, 0, -2):
                    alpha = int(intensidade * (r / raio) * 0.3)
                    if alpha > 0:
                        cor_luz = (*luz['cor'], alpha)
                        pygame.draw.circle(surf_luz, cor_luz, (raio, raio), r)
                screen.blit(surf_luz, (x - raio, y - raio))

    def renderizar_flash_screen(self, screen):
        """Renderiza o flash da tela"""
        if self.flash_screen > 0:
            alpha = int(255 * self.flash_screen)
            if alpha > 0:
                flash_surf = pygame.Surface((self.screen_width, self.screen_height), SRCALPHA)
                flash_surf.fill((255, 255, 255, alpha))
                screen.blit(flash_surf, (0, 0))

    def limpar_efeitos(self):
        """Limpa todos os efeitos ativos"""
        self.particulas_impacto.clear()
        self.particulas_sangue.clear()
        self.luzes_dinamicas.clear()
        self.shake_duracao = 0.0
        self.slow_motion_ativo = False
        self.slow_motion_fator = 1.0
        self.flash_screen = 0.0

class _FeedbackCombateManager:
    """Gerenciador singleton para o sistema de feedback de combate"""

    def __init__(self):
        self._instance = None

    def inicializar(self, screen_width, screen_height):
        """Inicializa o sistema de feedback de combate"""
        self._instance = FeedbackCombate(screen_width, screen_height)
        return self._instance

    def obter_instancia(self):
        """Obtém a instância do sistema de feedback"""
        return self._instance

# Instância do gerenciador
_manager = _FeedbackCombateManager()

def inicializar_feedback_combate(screen_width, screen_height):
    """Inicializa o sistema de feedback de combate"""
    return _manager.inicializar(screen_width, screen_height)

def obter_feedback_combate():
    """Obtém a instância do sistema de feedback"""
    return _manager.obter_instancia()
