"""
Classe dos inimigos do Brawl Stars Clone.
Este módulo implementa a inteligência artificial dos inimigos, incluindo
comportamento de perseguição, combate, movimento tático e sistema de tiro.
Os inimigos agora são Brawlers aleatórios com suas próprias características
e renderização 3D, como no jogo original.
"""

import math
import random
import pygame
from src.config import (SCREEN_WIDTH, SCREEN_HEIGHT)
from src.bullet import Bullet
from src.efeitos_visuais import gerenciador_efeitos
from src.feedback_combate import obter_feedback_combate
from src.characters.personagens import listar_personagens, obter_personagem
from src.pygame_constants import SRCALPHA

class Enemy(pygame.sprite.Sprite):
    """Classe do inimigo - agora são Brawlers aleatórios"""
    def __init__(self, x, y, jogador, velocidade=None, multiplicador_tiro=1.0, personagem_forcado=None):
        super().__init__()

        # Escolher um Brawler específico ou aleatório para ser este inimigo
        personagens_disponiveis = listar_personagens()
        if personagem_forcado and personagem_forcado in personagens_disponiveis:
            self.nome_personagem = personagem_forcado
        else:
            # Evitar repetir o mesmo personagem do jogador se possível
            personagens_diferentes = [p for p in personagens_disponiveis
                                    if hasattr(jogador, 'personagem') and
                                    p != getattr(jogador.personagem, 'nome', None)]
            if personagens_diferentes:
                self.nome_personagem = random.choice(personagens_diferentes)
            else:
                self.nome_personagem = random.choice(personagens_disponiveis)

        self.personagem = obter_personagem(self.nome_personagem)        # Criar sprite invisível para renderização 3D (o visual será feito pelo renderer_3d)
        # Manter o rect com tamanho adequado para colisões
        tamanho_colisao = 30  # Tamanho de colisão
        self.image = pygame.Surface((tamanho_colisao, tamanho_colisao), SRCALPHA)
        self.image.set_alpha(0)  # Garantir transparência total
        self.rect = pygame.Rect(x - tamanho_colisao//2, y - tamanho_colisao//2, tamanho_colisao, tamanho_colisao)        # Ajustar tamanho para renderização 3D (proporcional ao mapa)
        self.personagem.tamanho_render = 40  # Mesmo tamanho do jogador

        # Atributos do inimigo baseados no personagem
        self.vida = int(self.personagem.vida_maxima * 0.8)  # Inimigos um pouco mais fracos
        self.vida_maxima = self.vida
        self.velocidade = velocidade if velocidade is not None else self.personagem.velocidade * 0.8
        self.dano_base = int(self.personagem.dano * 0.9)  # Dano um pouco menor
        self.jogador = jogador
        self.ultimo_tiro = 0

        # Cooldown de tiro baseado no personagem
        self.cooldown_tiro = (self.personagem.cooldown * 1.2) / multiplicador_tiro# IA
        self.distancia_ideal = 80  # Distância reduzida para combate mais agressivo
        self.tempo_mudanca_direcao = 0
        self.direcao_aleatoria = (0, 0)

        # Posição para cálculos
        self.pos_x = float(x)
        self.pos_y = float(y)        # Referência para sistema de arbustos (será definida pelo jogo)
        self.gerenciador_arbustos = None  # Tipo: Optional[GerenciadorArbustos]

    def update(self, dt, obstaculos):
        """Atualizar inimigo"""
        if self.vida <= 0:
            # Adicionar efeito de explosão quando inimigo morre
            feedback = obter_feedback_combate()
            if feedback:
                feedback.processar_explosao(self.rect.centerx, self.rect.centery, "normal")
            self.kill()
            return

        # IA de movimento
        self.atualizar_movimento(dt, obstaculos)

        # Atualizar cooldown do tiro
        if self.ultimo_tiro > 0:
            self.ultimo_tiro -= dt

    def atualizar_movimento(self, dt, obstaculos):
        """Atualizar movimento do inimigo com IA"""
        # Calcular distância até o jogador
        dx_jogador = self.jogador.rect.centerx - self.rect.centerx
        dy_jogador = self.jogador.rect.centery - self.rect.centery
        distancia_jogador = math.sqrt(dx_jogador * dx_jogador + dy_jogador * dy_jogador)

        # Verificar se pode ver o jogador
        pode_ver_jogador = self._pode_ver_jogador(distancia_jogador)

        # Determinar comportamento baseado na distância e visibilidade
        dx = dy = 0

        if distancia_jogador > 0 and pode_ver_jogador:
            # Normalizar direção para o jogador
            dx_norm = dx_jogador / distancia_jogador
            dy_norm = dy_jogador / distancia_jogador

            if distancia_jogador > self.distancia_ideal * 1.5:
                # Muito longe - se aproximar agressivamente
                dx = dx_norm * self.velocidade * dt
                dy = dy_norm * self.velocidade * dt
            elif distancia_jogador < self.distancia_ideal * 0.6:
                # Muito perto - se afastar um pouco
                dx = -dx_norm * self.velocidade * dt * 0.5
                dy = -dy_norm * self.velocidade * dt * 0.5
            else:
                # Distância boa - movimento lateral mais agressivo
                self.tempo_mudanca_direcao -= dt
                if self.tempo_mudanca_direcao <= 0:
                    # Escolher nova direção - mais movimento para o jogador
                    if random.random() < 0.4:  # 40% chance de ir direto pro jogador
                        self.direcao_aleatoria = (dx_norm * 0.7, dy_norm * 0.7)
                    else:
                        # Movimento perpendicular
                        perpendicular_1 = (-dy_norm, dx_norm)
                        perpendicular_2 = (dy_norm, -dx_norm)
                        self.direcao_aleatoria = (perpendicular_1 if random.choice([True, False])
                                                else perpendicular_2)
                    self.tempo_mudanca_direcao = random.uniform(0.5, 2.0)  # Mudança mais frequente

                dx = self.direcao_aleatoria[0] * self.velocidade * dt * 0.8
                dy = self.direcao_aleatoria[1] * self.velocidade * dt * 0.8
        else:
            # Não pode ver o jogador - comportamento de patrulha/busca
            self.tempo_mudanca_direcao -= dt
            if self.tempo_mudanca_direcao <= 0:
                # Movimento aleatório de patrulha
                angulo = random.uniform(0, 2 * math.pi)
                self.direcao_aleatoria = (math.cos(angulo), math.sin(angulo))
                self.tempo_mudanca_direcao = random.uniform(1.0, 3.0)

            # Movimento de patrulha mais lento
            dx = self.direcao_aleatoria[0] * self.velocidade * dt * 0.3
            dy = self.direcao_aleatoria[1] * self.velocidade * dt * 0.3        # Aplicar movimento com verificação de colisão
        self.mover(dx, dy, obstaculos)

        # Atualizar estado de movimento para animações
        self.personagem.em_movimento = abs(dx) > 0.1 or abs(dy) > 0.1
        self.personagem.poder_ativo = False  # Inimigos normalmente não usam poder especial visualmente

    def mover(self, dx, dy, obstaculos):
        """Mover inimigo com verificação de colisão"""
        # Mover horizontalmente
        self.pos_x += dx
        if self.rect is not None:
            self.rect.centerx = int(self.pos_x)

        # Verificar colisões horizontais
        if self.rect is not None and self.rect.left < 0:
            self.rect.left = 0
            self.pos_x = self.rect.centerx
        elif self.rect is not None and self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.pos_x = self.rect.centerx

        # Mover verticalmente
        self.pos_y += dy
        if self.rect.top < 0:
            self.rect.top = 0
            if self.rect is not None:
                self.pos_y = self.rect.centery
        elif self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            if self.rect is not None:
                self.pos_y = self.rect.centery
        elif self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            if self.rect is not None:
                self.pos_y = self.rect.centery

    def tentar_atirar(self, dt):  # pylint: disable=unused-argument
        """Tentar atirar no jogador"""
        if self.ultimo_tiro <= 0:
            # Calcular distância até o jogador
            dx = self.jogador.rect.centerx - self.rect.centerx
            dy = self.jogador.rect.centery - self.rect.centery
            distancia = math.sqrt(dx * dx + dy * dy)

            # Verificar se pode ver o jogador (considerando arbustos)
            pode_ver = self._pode_ver_jogador(distancia)

            # Atirar mais agressivamente - aumentar alcance e frequência
            if 0 < distancia < 400 and pode_ver:  # Aumentado de 300 para 400
                # Normalizar direção
                dx /= distancia
                dy /= distancia

                # Adicionar pequena variação para simular imprecisão
                precisao = 0.95  # 95% de precisão
                dx += random.uniform(-0.1, 0.1) * (1 - precisao)
                dy += random.uniform(-0.1, 0.1) * (1 - precisao)

                # Normalizar novamente
                magnitude = math.sqrt(dx * dx + dy * dy)
                if magnitude > 0:
                    dx /= magnitude
                    dy /= magnitude

                # Criar tiro com dano baseado no personagem
                tiro = Bullet(self.rect.centerx, self.rect.centery, dx, dy,
                             de_inimigo=True, dano=self.dano_base, tipo_tiro=self.personagem.tipo_tiro)
                self.ultimo_tiro = self.cooldown_tiro
                # Debug: imprimir quando inimigo atira
                # print(f"Inimigo {self.nome_personagem} atirou! Distância: {distancia:.1f}")
                return tiro

        return None

    def _pode_ver_jogador(self, distancia):
        """Verificar se o inimigo pode ver o jogador considerando arbustos"""
        # Se não há sistema de arbustos, pode ver normalmente
        if not self.gerenciador_arbustos:
            return True
        # Se o jogador está em arbusto, reduzir alcance de visão drasticamente
        if self.gerenciador_arbustos.entidade_esta_em_arbusto(self.jogador):
            # Só pode ver se estiver muito próximo (dentro do arbusto ou quase)
            return distancia < 50
        return True

    def receber_dano(self, dano, tiro_especial=False):
        """Receber dano"""
        self.vida -= dano
        self.vida = max(self.vida, 0)

        # Criar efeitos visuais de dano
        centro_x = self.rect.centerx
        centro_y = self.rect.centery - 15  # Acima do inimigo

        # Determinar tipo de dano para escolher cor e efeito
        tipo_dano = "critico" if tiro_especial else "normal"
        tipo_impacto = "super" if tiro_especial else "inimigo"

        # Número de dano flutuante
        gerenciador_efeitos.criar_numero_dano(centro_x, centro_y, dano, tipo_dano)

        # Efeito de impacto
        gerenciador_efeitos.criar_efeito_impacto(self.rect.centerx, self.rect.centery, tipo_impacto)

    def draw_vida(self, screen):
        """Desenhar barra de vida"""
        if self.vida < self.vida_maxima:
            barra_width = 40
            barra_height = 5
            x = self.rect.centerx - barra_width // 2
            y = self.rect.top - 10

            # Fundo da barra
            pygame.draw.rect(screen, (255, 0, 0), (x, y, barra_width, barra_height))

            # Vida atual
            vida_width = int((self.vida / self.vida_maxima) * barra_width)
            pygame.draw.rect(screen, (0, 255, 0), (x, y, vida_width, barra_height))
