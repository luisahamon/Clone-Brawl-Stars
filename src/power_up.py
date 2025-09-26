"""
Sistema de power-ups do Brawl Stars Clone.

Este módulo implementa os power-ups coletáveis do jogo, incluindo diferentes
tipos (velocidade, vida, tiro rápido), efeitos visuais de animação e
aplicação temporária de melhorias ao jogador.
"""

import math
import random
import pygame
from src.config import TAMANHO_POWER_UP

class PowerUp(pygame.sprite.Sprite):
    """Classe dos power-ups"""

    TIPOS = ['velocidade', 'vida', 'tiro_rapido']

    def __init__(self, x, y):
        super().__init__()
        self.tipo = random.choice(self.TIPOS)

        # Criar visual baseado no tipo
        self.image = pygame.Surface((TAMANHO_POWER_UP, TAMANHO_POWER_UP))

        if self.tipo == 'velocidade':
            self.image.fill((0, 255, 255))  # Ciano
        elif self.tipo == 'vida':
            self.image.fill((0, 255, 0))    # Verde
        elif self.tipo == 'tiro_rapido':
            self.image.fill((255, 165, 0))  # Laranja

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        # Efeito visual
        self.tempo_animacao = 0
        self.escala_original = TAMANHO_POWER_UP

    def update(self, dt, obstaculos=None):  # pylint: disable=unused-argument
        """Atualizar animação do power-up"""
        # O parâmetro obstaculos é necessário para compatibilidade com o grupo de sprites
        # mas não é usado pelos power-ups
        self.tempo_animacao += dt * 3  # Velocidade da animação

        # Efeito de pulsação
        escala = self.escala_original + int(5 * abs(math.sin(self.tempo_animacao)))
        centro = self.rect.center

        # Definir cor baseada no tipo
        cores = {
            'velocidade': (0, 255, 255),    # Ciano
            'vida': (0, 255, 0),           # Verde
            'tiro_rapido': (255, 165, 0)   # Laranja
        }

        cor = cores.get(self.tipo, (255, 255, 255))  # Cor padrão branca

        # Recriar surface com nova escala
        self.image = pygame.Surface((escala, escala))
        self.image.fill(cor)
        self.rect = self.image.get_rect()
        self.rect.center = centro

    def aplicar_efeito(self, jogador):
        """Aplicar efeito no jogador"""
        jogador.aplicar_power_up(self.tipo)
