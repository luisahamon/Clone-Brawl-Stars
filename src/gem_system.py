"""
Sistema de Gemas para o modo Gem Grab do Brawl Stars Clone.
Este módulo implementa as gemas que são o objetivo principal do modo de jogo,
incluindo spawn aleatório, coleta pelo jogador e renderização visual.
"""

import random
import math
import pygame
from src.config import (
    TAMANHO_GEMA, COR_GEMA, INTERVALO_SPAWN_GEMA,
    GEMAS_SIMULTANEAS_MAX, RAIO_COLETA_GEMA
)
from src.efeitos_visuais import gerenciador_efeitos


class Gema:
    """
    Representa uma gema coletável no jogo.
    As gemas são o objetivo principal do modo Gem Grab, onde o jogador
    deve coletar 10 gemas para vencer. Elas spawnam aleatoriamente no
    mapa e podem ser coletadas pelo jogador.
    """

    def __init__(self, x, y):
        """
        Inicializa uma nova gema.
        Args:
            x (float): Posição X da gema
            y (float): Posição Y da gema
        """
        self.x = x
        self.y = y
        self.tamanho = TAMANHO_GEMA
        self.cor = COR_GEMA
        self.coletada = False
        self.tempo_animacao = 0
        self.brilho_offset = random.uniform(0, 2 * math.pi)

        # Efeito visual de spawn
        self.spawn_time = 0
        self.spawn_duration = 0.5  # Duração da animação de spawn

    def update(self, dt):
        """
        Atualiza a gema (animações visuais).
        Args:
            dt (float): Delta time em segundos
        """
        self.tempo_animacao += dt
        if self.spawn_time < self.spawn_duration:
            self.spawn_time += dt

    def get_rect(self):
        """
        Retorna o retângulo de colisão da gema.
        Returns:
            pygame.Rect: Retângulo de colisão
        """
        return pygame.Rect(
            self.x - self.tamanho // 2,
            self.y - self.tamanho // 2,
            self.tamanho,
            self.tamanho
        )

    def pode_ser_coletada(self, jogador_x, jogador_y):
        """
        Verifica se a gema pode ser coletada pelo jogador.
        Args:
            jogador_x (float): Posição X do jogador
            jogador_y (float): Posição Y do jogador
        Returns:
            bool: True se a gema pode ser coletada
        """
        if self.coletada:
            return False

        distancia = math.sqrt((self.x - jogador_x)**2 + (self.y - jogador_y)**2)
        return distancia <= RAIO_COLETA_GEMA

    def coletar(self):
        """
        Marca a gema como coletada.
        """
        # Criar efeito visual de coleta de gema
        gerenciador_efeitos.criar_particulas_gema(self.x, self.y, "normal")
        self.coletada = True

    def render(self, screen):
        """
        Renderiza a gema na tela.
        Args:
            screen (pygame.Surface): Superfície de renderização
        """
        if self.coletada:
            return

        # Efeito de brilho/pulsação
        brilho = 0.3 * math.sin(self.tempo_animacao * 4 + self.brilho_offset) + 0.7

        # Efeito de spawn (escala)
        escala = 1.0
        if self.spawn_time < self.spawn_duration:
            escala = self.spawn_time / self.spawn_duration
            escala = escala * escala  # Efeito quadrático para suavidade

        tamanho_atual = int(self.tamanho * escala)

        if tamanho_atual <= 0:
            return

        # Cor com brilho
        cor_atual = tuple(int(c * brilho) for c in self.cor)

        # Desenhar gema (formato de diamante)
        pontos = [
            (self.x, self.y - tamanho_atual),  # Topo
            (self.x + tamanho_atual, self.y),  # Direita
            (self.x, self.y + tamanho_atual),  # Baixo
            (self.x - tamanho_atual, self.y)   # Esquerda
        ]

        pygame.draw.polygon(screen, cor_atual, pontos)

        # Contorno mais escuro
        cor_contorno = tuple(max(0, c - 50) for c in cor_atual)
        pygame.draw.polygon(screen, cor_contorno, pontos, 2)

        # Brilho central
        if brilho > 0.8:
            centro_size = max(1, tamanho_atual // 3)
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), centro_size)

class GerenciadorGemas:
    """
    Gerencia o spawn, coleta e renderização de todas as gemas no jogo.
    """

    def __init__(self, largura_mapa, altura_mapa, obstaculos):
        """
        Inicializa o gerenciador de gemas.
        Args:
            largura_mapa (int): Largura do mapa
            altura_mapa (int): Altura do mapa
            obstaculos (list): Lista de obstáculos para evitar spawn sobre eles
        """
        self.largura_mapa = largura_mapa
        self.altura_mapa = altura_mapa
        self.obstaculos = obstaculos
        self.gemas = []
        self.tempo_proximo_spawn = INTERVALO_SPAWN_GEMA

        # Estatísticas
        self.total_gemas_spawned = 0
        self.gemas_coletadas = 0

    def update(self, dt):
        """
        Atualiza o sistema de gemas.
        Args:
            dt (float): Delta time em segundos
        """
        # Atualizar gemas existentes
        for gema in self.gemas[:]:
            gema.update(dt)
            if gema.coletada:
                self.gemas.remove(gema)
                self.gemas_coletadas += 1

        # Spawn de novas gemas
        self.tempo_proximo_spawn -= dt
        if (self.tempo_proximo_spawn <= 0 and
            len(self.gemas) < GEMAS_SIMULTANEAS_MAX):
            self._spawnar_gema()
            self.tempo_proximo_spawn = INTERVALO_SPAWN_GEMA

    def _spawnar_gema(self):
        """
        Cria uma nova gema em posição aleatória válida.
        """
        tentativas = 50  # Máximo de tentativas para encontrar posição válida

        for _ in range(tentativas):
            # Posição aleatória no mapa (com margem das bordas)
            margem = 50
            x = random.randint(margem, self.largura_mapa - margem)
            y = random.randint(margem, self.altura_mapa - margem)
            posicao_valida = True
            gema_rect = pygame.Rect(x - TAMANHO_GEMA, y - TAMANHO_GEMA,
                                  TAMANHO_GEMA * 2, TAMANHO_GEMA * 2)

            for obstaculo in self.obstaculos:
                if gema_rect.colliderect(obstaculo.rect):
                    posicao_valida = False
                    break

            # Verificar se não está muito próxima de outras gemas
            if posicao_valida:
                for gema_existente in self.gemas:
                    distancia = math.sqrt((x - gema_existente.x)**2 + (y - gema_existente.y)**2)
                    if distancia < TAMANHO_GEMA * 3:  # Distância mínima entre gemas
                        posicao_valida = False
                        break

            if posicao_valida:
                nova_gema = Gema(x, y)
                self.gemas.append(nova_gema)
                self.total_gemas_spawned += 1
                break

    def coletar_gemas(self, jogador_x, jogador_y):
        """
        Verifica e coleta gemas próximas ao jogador.
        Args:
            jogador_x (float): Posição X do jogador
            jogador_y (float): Posição Y do jogador
        Returns:
            int: Número de gemas coletadas
        """
        gemas_coletadas = 0

        for gema in self.gemas:
            if gema.pode_ser_coletada(jogador_x, jogador_y):
                gema.coletar()
                gemas_coletadas += 1

        return gemas_coletadas

    def render(self, screen):
        """
        Renderiza todas as gemas na tela.
        Args:
            screen (pygame.Surface): Superfície de renderização
        """
        for gema in self.gemas:
            gema.render(screen)

    def get_total_gemas_ativas(self):
        """
        Retorna o número de gemas ativas no mapa.
        Returns:
            int: Número de gemas ativas
        """
        return len(self.gemas)

    def reset(self):
        """
        Reseta o sistema de gemas.
        """
        self.gemas.clear()
        self.tempo_proximo_spawn = INTERVALO_SPAWN_GEMA
        self.total_gemas_spawned = 0
        self.gemas_coletadas = 0

    def dropar_gema(self, x, y):
        """
        Força o spawn de uma gema em uma posição específica.
        Usado principalmente quando o jogador morre e precisa dropar gemas.
        Args:
            x (float): Posição X onde dropar a gema
            y (float): Posição Y onde dropar a gema
        """
        # Verificar se a posição está dentro dos limites do mapa
        margem = TAMANHO_GEMA
        x = max(margem, min(x, self.largura_mapa - margem))
        y = max(margem, min(y, self.altura_mapa - margem))

        # Verificar se não está sobre obstáculo
        gema_rect = pygame.Rect(x - TAMANHO_GEMA, y - TAMANHO_GEMA,
                              TAMANHO_GEMA * 2, TAMANHO_GEMA * 2)

        posicao_valida = True
        for obstaculo in self.obstaculos:
            if gema_rect.colliderect(obstaculo.rect):
                # Se está sobre obstáculo, tentar encontrar posição próxima válida
                for tentativa_x in range(int(x) - 20, int(x) + 21, 10):
                    for tentativa_y in range(int(y) - 20, int(y) + 21, 10):
                        if (tentativa_x >= margem and tentativa_x <= self.largura_mapa - margem and
                            tentativa_y >= margem and tentativa_y <= self.altura_mapa - margem):
                            test_rect = pygame.Rect(tentativa_x - TAMANHO_GEMA,
                            tentativa_y - TAMANHO_GEMA,
                            TAMANHO_GEMA * 2, TAMANHO_GEMA * 2)
                            if not any(test_rect.colliderect(obs.rect) for obs in self.obstaculos):
                                x, y = tentativa_x, tentativa_y
                                posicao_valida = True
                                break
                    if posicao_valida:
                        break
                break

        # Criar e adicionar a gema
        nova_gema = Gema(x, y)
        self.gemas.append(nova_gema)
        self.total_gemas_spawned += 1
