"""
Sistema de Super Autêntico do Brawl Stars Clone.
Este módulo implementa o sistema de carregamento de Super idêntico ao jogo original:
- Super carrega causando dano nos inimigos
- Super carrega recebendo dano (menor quantidade)
- Barra visual de progresso
- Diferentes taxas de carga por Brawler
- Efeitos visuais únicos por personagem
"""

import math
import pygame
from src.pygame_constants import SRCALPHA

def rotacionar_vetor(x, y, angulo_graus):
    """Rotaciona um vetor 2D pelo ângulo especificado em graus"""
    angulo_rad = math.radians(angulo_graus)
    cos_a = math.cos(angulo_rad)
    sin_a = math.sin(angulo_rad)

    novo_x = x * cos_a - y * sin_a
    novo_y = x * sin_a + y * cos_a

    return novo_x, novo_y

class SuperSystem:
    """Gerenciador do sistema de Super autêntico"""
    def __init__(self, personagem):
        self.personagem = personagem
        self.carga_atual = 0.0
        self.carga_maxima = 100.0
        self.super_disponivel = False
        self.super_ativo = False
        self.tempo_super = 0.0

        # Configurações específicas por Brawler
        self._configurar_taxas_carga()

        # Efeitos visuais
        self.barra_brilho = 0.0
        self.tempo_brilho = 0.0
        self.particulas_carga = []

    def _configurar_taxas_carga(self):
        """Configura taxas de carga específicas por Brawler"""
        config_brawlers = {
            'Shelly': {
                'carga_por_dano': 18,      # Por hit causado
                'carga_por_hit': 12,       # Por hit recebido
                'duracao_super': 0.0,      # Super instantânea
                'cor_super': (255, 215, 0)  # Dourado
            },
            'Nita': {
                'carga_por_dano': 15,
                'carga_por_hit': 10,
                'duracao_super': 15.0,     # Urso dura 15s
                'cor_super': (139, 69, 19)  # Marrom
            },
            'Colt': {
                'carga_por_dano': 12,
                'carga_por_hit': 8,
                'duracao_super': 0.0,      # Super instantânea
                'cor_super': (0, 191, 255)  # Ciano
            },
            'Bull': {
                'carga_por_dano': 20,
                'carga_por_hit': 15,
                'duracao_super': 0.5,      # Dash rápido
                'cor_super': (255, 69, 0)   # Vermelho
            },
            'Barley': {
                'carga_por_dano': 14,
                'carga_por_hit': 9,
                'duracao_super': 3.0,      # Área persiste 3s
                'cor_super': (50, 205, 50)  # Verde
            },
            'Poco': {
                'carga_por_dano': 16,
                'carga_por_hit': 11,
                'duracao_super': 0.0,      # Cura instantânea
                'cor_super': (255, 20, 147) # Rosa
            }
        }

        nome = self.personagem.nome
        config = config_brawlers.get(nome, config_brawlers['Shelly'])
        self.carga_por_dano = config['carga_por_dano']
        self.carga_por_hit = config['carga_por_hit']
        self.duracao_super = config['duracao_super']
        self.cor_super = config['cor_super']

    def adicionar_carga_dano(self, dano_causado):
        """Adiciona carga baseada no dano causado"""
        if self.super_disponivel:
            return
        # Carga baseada no dano (mais eficiente)
        carga_ganha = (dano_causado / 100.0) * self.carga_por_dano
        self._adicionar_carga(carga_ganha)

    def adicionar_carga_hit(self, dano_recebido):
        """Adiciona carga baseada no dano recebido"""
        if self.super_disponivel:
            return
        # Carga baseada no hit recebido (menos eficiente)
        carga_ganha = (dano_recebido / 100.0) * self.carga_por_hit
        self._adicionar_carga(carga_ganha)

    def _adicionar_carga(self, quantidade):
        """Adiciona carga ao Super com efeitos visuais"""
        antiga_carga = self.carga_atual
        self.carga_atual = min(self.carga_atual + quantidade, self.carga_maxima)
        # Efeitos visuais de ganho de carga
        if self.carga_atual > antiga_carga:
            self._criar_particula_carga()        # Super ficou disponível
        if not self.super_disponivel and self.carga_atual >= self.carga_maxima:
            self.super_disponivel = True
            self.barra_brilho = 1.0
            self._criar_efeito_super_pronto()

    def _criar_particula_carga(self):
        """Cria partícula visual de ganho de carga"""
        angulo = pygame.time.get_ticks() % 360
        vel_x, vel_y = rotacionar_vetor(0, -50, angulo)

        particula = {
            'x': 0,
            'y': 0,
            'vel_x': vel_x,
            'vel_y': vel_y,
            'vida': 0.5,
            'vida_max': 0.5,
            'cor': self.cor_super,
            'tamanho': 3        }
        self.particulas_carga.append(particula)

    def _criar_efeito_super_pronto(self):
        """Cria efeito quando Super fica disponível"""
        # Múltiplas partículas douradas
        for i in range(12):
            angulo = (360 / 12) * i
            vel_x, vel_y = rotacionar_vetor(0, -60, angulo)
            particula = {
                'x': 0,
                'y': 0,
                'vel_x': vel_x,
                'vel_y': vel_y,
                'vida': 1.0,
                'vida_max': 1.0,
                'cor': (255, 215, 0),
                'tamanho': 5
            }
            self.particulas_carga.append(particula)

    def usar_super(self):
        """Usa o Super se disponível"""
        if not self.super_disponivel:
            return False
        # Consumir Super
        self.super_disponivel = False
        self.super_ativo = True
        self.carga_atual = 0.0
        self.tempo_super = self.duracao_super
        # Efeito visual de ativação        self._criar_efeito_ativacao_super()

        return True

    def _criar_efeito_ativacao_super(self):
        """Cria efeito visual de ativação do Super"""
        # Explosão de partículas com cor do Brawler
        for i in range(20):
            angulo = (360 / 20) * i
            vel_x, vel_y = rotacionar_vetor(0, -80, angulo)
            particula = {
                'x': 0,
                'y': 0,
                'vel_x': vel_x,
                'vel_y': vel_y,
                'vida': 1.5,
                'vida_max': 1.5,
                'cor': self.cor_super,
                'tamanho': 6
            }
            self.particulas_carga.append(particula)

    def update(self, dt):
        """Atualiza o sistema de Super"""
        # Atualizar tempo do Super ativo
        if self.super_ativo and self.tempo_super > 0:
            self.tempo_super -= dt
            if self.tempo_super <= 0:
                self.super_ativo = False

        # Atualizar brilho da barra
        if self.barra_brilho > 0:
            self.barra_brilho -= dt * 2  # Fade em 0.5s
            self.barra_brilho = max(0, self.barra_brilho)
        # Atualizar partículas
        for particula in self.particulas_carga[:]:
            particula['vida'] -= dt
            if particula['vida'] <= 0:
                self.particulas_carga.remove(particula)
                continue
            # Movimento
            particula['x'] += particula['vel_x'] * dt
            particula['y'] += particula['vel_y'] * dt
            # Resistência do ar
            particula['vel_x'] *= 0.98
            particula['vel_y'] *= 0.98

    def obter_progresso(self):
        """Retorna progresso da carga (0.0 a 1.0)"""
        return self.carga_atual / self.carga_maxima

    def esta_disponivel(self):
        """Verifica se Super está disponível"""
        return self.super_disponivel

    def esta_ativo(self):
        """Verifica se Super está ativo"""
        return self.super_ativo

    def obter_info_hud(self):
        """Retorna informações para o HUD"""
        return {
            'progresso': self.obter_progresso(),
            'disponivel': self.super_disponivel,
            'ativo': self.super_ativo,
            'cor': self.cor_super,
            'brilho': self.barra_brilho,
            'tempo_restante': self.tempo_super if self.super_ativo else 0
        }

    def renderizar_particulas(self, screen, offset_x, offset_y):
        """Renderiza partículas de carga do Super"""
        for particula in self.particulas_carga:
            # Calcular posição na tela
            x = offset_x + particula['x']
            y = offset_y + particula['y']
            # Fade baseado na vida
            fade = particula['vida'] / particula['vida_max']
            alpha = int(255 * fade)
            tamanho = int(particula['tamanho'] * fade)
            if tamanho > 0:
                # Criar surface com alpha
                surf = pygame.Surface((tamanho * 2, tamanho * 2), SRCALPHA)
                cor_com_alpha = (*particula['cor'], alpha)
                pygame.draw.circle(surf, cor_com_alpha, (tamanho, tamanho), tamanho)
                screen.blit(surf, (x - tamanho, y - tamanho))
