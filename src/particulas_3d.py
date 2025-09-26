"""
Sistema de partículas 3D para efeitos visuais avançados.
Este módulo implementa um sistema completo de partículas com física realística,
incluindo diferentes tipos de partículas (brilho, detritos, energia) e
efeitos visuais específicos para diferentes ações do jogo.
"""

import math
import random
from typing import List, Tuple
import pygame
from src.pygame_constants import SRCALPHA

class Particula3D:
    def __init__(self, x: float, y: float, vel_x: float, vel_y: float,
                 cor: Tuple[int, int, int], tamanho: float, tempo_vida: float,
                 tipo: str = "normal"):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.cor = cor
        self.tamanho = tamanho
        self.tamanho_inicial = tamanho
        self.tempo_vida = tempo_vida
        self.tempo_vida_inicial = tempo_vida
        self.tipo = tipo
        self.angulo = random.uniform(0, 2 * math.pi)
        self.vel_angular = random.uniform(-5, 5)
        self.gravidade = 200 if tipo == "debris" else 50
        self.bounce = 0.7 if tipo == "debris" else 0.3

    def update(self, dt: float) -> bool:
        """Atualiza a partícula. Retorna False se deve ser removida"""
        # Movimento
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

        # Gravidade
        self.vel_y += self.gravidade * dt

        # Rotação
        self.angulo += self.vel_angular * dt

        # Reduzir tempo de vida
        self.tempo_vida -= dt

        # Diminuir tamanho com o tempo
        fator_vida = self.tempo_vida / self.tempo_vida_inicial
        self.tamanho = self.tamanho_inicial * fator_vida

        # Bounce no chão (simulado)
        if self.y > 600:  # Assumindo altura da tela
            self.y = 600
            self.vel_y *= -self.bounce
            self.vel_x *= 0.8  # Atrito

        return self.tempo_vida > 0 and self.tamanho > 0.5

    def render(self, superficie: pygame.Surface):
        """Renderiza a partícula com efeito 3D"""
        if self.tamanho < 1:
            return
        pos = (int(self.x), int(self.y))

        if self.tipo == "sparkle":
            self._render_sparkle(superficie, pos)
        elif self.tipo == "debris":
            self._render_debris(superficie, pos)
        elif self.tipo == "energy":
            self._render_energy(superficie, pos)
        else:
            self._render_normal(superficie, pos)

    def _render_sparkle(self, superficie: pygame.Surface, pos: Tuple[int, int]):
        """Renderiza partícula de brilho"""
        # Estrela brilhante
        raio = int(self.tamanho)
        cor_centro = (
            min(255, self.cor[0] + 100),
            min(255, self.cor[1] + 100),
            min(255, self.cor[2] + 100)
        )

        # Raios da estrela
        for i in range(8):
            angulo = (i * math.pi / 4) + self.angulo
            x_end = pos[0] + math.cos(angulo) * raio
            y_end = pos[1] + math.sin(angulo) * raio
            pygame.draw.line(superficie, cor_centro, pos, (int(x_end), int(y_end)), 2)
        # Centro brilhante
        pygame.draw.circle(superficie, cor_centro, pos, max(1, raio//3))

    def _render_debris(self, superficie: pygame.Surface, pos: Tuple[int, int]):
        """Renderiza detritos 3D"""
        tamanho = int(self.tamanho)
        if tamanho < 2:
            return

        # Criar superfície rotacionada
        debris_surf = pygame.Surface((tamanho * 2, tamanho * 2), SRCALPHA)
        centro = (tamanho, tamanho)

        # Formato irregular do detrito
        pontos = []
        for i in range(6):
            angulo = (i * math.pi / 3) + self.angulo
            variacao = random.uniform(0.7, 1.3)
            raio = tamanho * variacao
            x = centro[0] + math.cos(angulo) * raio
            y = centro[1] + math.sin(angulo) * raio
            pontos.append((int(x), int(y)))        # Gradiente no detrito
        cor_clara = (
            min(255, self.cor[0] + 40),
            min(255, self.cor[1] + 40),
            min(255, self.cor[2] + 40)
        )
        cor_escura = (
            max(0, self.cor[0] - 40),
            max(0, self.cor[1] - 40),
            max(0, self.cor[2] - 40)
        )
        pygame.draw.polygon(debris_surf, cor_clara, pontos)

        # Borda mais escura
        pygame.draw.polygon(debris_surf, cor_escura, pontos, 1)
        superficie.blit(debris_surf, (pos[0] - tamanho, pos[1] - tamanho))

    def _render_energy(self, superficie: pygame.Surface, pos: Tuple[int, int]):
        """Renderiza partícula de energia"""
        tamanho = int(self.tamanho)

        # Múltiplas camadas para efeito de energia
        for i in range(3):
            raio = tamanho - i * 2
            if raio <= 0:
                break
            alpha = int(255 * (1 - i * 0.3))
            cor_layer = (*self.cor, alpha)

            # Criar superfície com alpha
            energy_surf = pygame.Surface((raio * 4, raio * 4), SRCALPHA)
            pygame.draw.circle(energy_surf, cor_layer, (raio * 2, raio * 2), raio)
            superficie.blit(energy_surf, (pos[0] - raio * 2, pos[1] - raio * 2))

    def _render_normal(self, superficie: pygame.Surface, pos: Tuple[int, int]):
        """Renderiza partícula normal com gradiente"""
        tamanho = int(self.tamanho)
        if tamanho < 1:
            return

        # Gradiente radial
        for r in range(tamanho, 0, -1):
            fator = r / tamanho
            alpha = int(255 * fator * fator)  # Mais transparente nas bordas
            cor_atual = (*self.cor, alpha)

            # Criar superfície temporária para alpha
            temp_surf = pygame.Surface((r * 4, r * 4), SRCALPHA)
            pygame.draw.circle(temp_surf, cor_atual, (r * 2, r * 2), r)
            superficie.blit(temp_surf, (pos[0] - r * 2, pos[1] - r * 2))

class SistemaParticulas3D:
    def __init__(self):
        self.particulas: List[Particula3D] = []

    def adicionar_explosao(self, x: float, y: float, cor: Tuple[int, int, int],
                          intensidade: int = 10):
        """Adiciona explosão com partículas 3D"""
        for _ in range(intensidade):
            angulo = random.uniform(0, 2 * math.pi)
            velocidade = random.uniform(50, 200)
            vel_x = math.cos(angulo) * velocidade
            vel_y = math.sin(angulo) * velocidade
            self.particulas.append(Particula3D(
                x, y, vel_x, vel_y,
                cor, random.uniform(3, 8),
                random.uniform(0.5, 1.5), "sparkle"
            ))

    def adicionar_destruicao_obstaculo(self, x: float, y: float,
                                     cor: Tuple[int, int, int]):
        """Adiciona partículas de destruição de obstáculo"""
        for _ in range(10):
            angulo = random.uniform(0, 2 * math.pi)
            velocidade = random.uniform(100, 300)
            vel_x = math.cos(angulo) * velocidade
            vel_y = math.sin(angulo) * velocidade - 100  # Para cima

            self.particulas.append(Particula3D(
                x, y, vel_x, vel_y,
                cor, random.uniform(4, 12),
                random.uniform(1.0, 2.5), "debris"
            ))

    def adicionar_coleta_gema(self, x: float, y: float):
        """Adiciona partículas de coleta de gema"""
        for _ in range(12):
            angulo = random.uniform(0, 2 * math.pi)
            velocidade = random.uniform(30, 120)
            vel_x = math.cos(angulo) * velocidade
            vel_y = math.sin(angulo) * velocidade - 50
            cor = random.choice([
                (0, 255, 100), (100, 255, 200), (200, 255, 100)
            ])
            self.particulas.append(Particula3D(
                x, y, vel_x, vel_y,
                cor, random.uniform(2, 6),
                random.uniform(0.8, 1.5), "energy"
            ))

    def adicionar_impacto_tiro(self, x: float, y: float, cor: Tuple[int, int, int]):
        """Adiciona partículas de impacto de tiro"""
        for _ in range(8):
            angulo = random.uniform(0, 2 * math.pi)
            velocidade = random.uniform(80, 150)
            vel_x = math.cos(angulo) * velocidade
            vel_y = math.sin(angulo) * velocidade
            self.particulas.append(Particula3D(
                x, y, vel_x, vel_y,
                cor, random.uniform(2, 5),
                random.uniform(0.3, 0.8), "sparkle"
            ))

    def adicionar_powerup_coletado(self, x: float, y: float, tipo: str):
        """Adiciona partículas específicas do power-up coletado"""
        cores_powerup = {
            'velocidade': (0, 255, 100),
            'dano': (255, 100, 0),
            'vida': (255, 0, 100),
            'escudo': (100, 100, 255),
            'tiro_rapido': (255, 165, 0)
        }
        cor = cores_powerup.get(tipo, (255, 255, 255))
        for _ in range(15):
            angulo = random.uniform(0, 2 * math.pi)
            velocidade = random.uniform(40, 180)
            vel_x = math.cos(angulo) * velocidade
            vel_y = math.sin(angulo) * velocidade - 80
            self.particulas.append(Particula3D(
                x, y, vel_x, vel_y,
                cor, random.uniform(3, 7),
                random.uniform(1.0, 2.0), "energy"
            ))

    def update(self, dt: float):
        """Atualiza todas as partículas"""
        self.particulas = [p for p in self.particulas if p.update(dt)]

    def render(self, superficie: pygame.Surface):
        """Renderiza todas as partículas"""
        for particula in self.particulas:
            particula.render(superficie)

    def limpar(self):
        """Remove todas as partículas"""
        self.particulas.clear()

# Instância global
sistema_particulas_3d = SistemaParticulas3D()
