"""
Sistema de obstáculos do Brawl Stars Clone.

Este módulo implementa os obstáculos do mapa que bloqueiam movimento
e projéteis, criando elementos táticos no gameplay. Inclui obstáculos
estáticos e destrutíveis que podem ser quebrados com tiros.
"""

import random
import pygame
from src.config import TAMANHO_OBSTACULO, COR_OBSTACULO

class Obstacle(pygame.sprite.Sprite):
    """Classe dos obstáculos com suporte a destrutibilidade"""

    def __init__(self, x, y, destrutivel=False, vida_maxima=100):
        super().__init__()
        self.destrutivel = destrutivel
        self.vida_maxima = vida_maxima if destrutivel else float('inf')
        self.vida_atual = self.vida_maxima

        # Criar surface baseado no tipo
        self.image = pygame.Surface((TAMANHO_OBSTACULO, TAMANHO_OBSTACULO))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        # Definir cor baseada no tipo
        if destrutivel:
            self.cor_base = (139, 69, 19)  # Marrom para madeira
            self.cor_dano = (205, 133, 63)  # Marrom claro quando danificado
        else:
            self.cor_base = COR_OBSTACULO
            self.cor_dano = COR_OBSTACULO
        self.atualizar_visual()

    def atualizar_visual(self):
        """Atualizar visual baseado na vida atual"""
        if not self.destrutivel:
            self.image.fill(self.cor_base)
            return

        # Calcular porcentagem de vida
        percentual_vida = self.vida_atual / self.vida_maxima
        if percentual_vida > 0.7:
            # Obstáculo intacto
            self.image.fill(self.cor_base)
        elif percentual_vida > 0.4:
            # Obstáculo levemente danificado
            self.image.fill(self.cor_dano)
            # Adicionar algumas "rachaduras"
            for _ in range(3):
                x = random.randint(0, TAMANHO_OBSTACULO)
                y = random.randint(0, TAMANHO_OBSTACULO)
                pygame.draw.circle(self.image, (101, 67, 33), (x, y), 2)
        elif percentual_vida > 0.1:
            # Obstáculo muito danificado
            self.image.fill((160, 82, 45))  # Marrom mais claro
            # Mais rachaduras
            for _ in range(6):
                x = random.randint(0, TAMANHO_OBSTACULO)
                y = random.randint(0, TAMANHO_OBSTACULO)
                pygame.draw.circle(self.image, (101, 67, 33), (x, y), 3)
        else:
            # Quase destruído
            self.image.fill((205, 133, 63))
            # Muitas rachaduras
            for _ in range(10):
                x = random.randint(0, TAMANHO_OBSTACULO)
                y = random.randint(0, TAMANHO_OBSTACULO)
                pygame.draw.circle(self.image, (139, 69, 19), (x, y), 2)

    def receber_dano(self, dano):
        """Recebe dano e retorna True se foi destruído"""
        if not self.destrutivel:
            return False

        self.vida -= dano
        if self.vida <= 0:
            return True
        return False

    def render(self, surface):
        """Renderiza o obstáculo"""
        # Cor baseada na vida
        if self.destrutivel:
            percent_vida = self.vida / self.vida_maxima
            r = int(139 * percent_vida + 60 * (1 - percent_vida))
            g = int(69 * percent_vida + 60 * (1 - percent_vida))
            b = int(19 * percent_vida + 60 * (1 - percent_vida))
            cor = (r, g, b)
        else:
            cor = self.cor

        pygame.draw.rect(surface, cor,
                        (self.x, self.y, self.largura, self.altura))

        # Borda
        pygame.draw.rect(surface, (0, 0, 0),
                        (self.x, self.y, self.largura, self.altura), 2)

    def get_rect(self):
        """Retorna rect para colisão"""
        return pygame.Rect(self.x, self.y, self.largura, self.altura)

    def colide_com(self, rect):
        """Verifica colisão com um rect"""
        return self.get_rect().colliderect(rect)

class Wall(Obstacle):
    """Parede indestrutível"""
    def __init__(self, x, y, largura=40, altura=40):
        super().__init__(x, y, largura, altura, vida=0)
        self.cor = (100, 100, 100)

class Box(Obstacle):
    """Caixa destrutível"""
    def __init__(self, x, y, largura=40, altura=40):
        super().__init__(x, y, largura, altura, vida=50)
        self.cor = (160, 82, 45)
