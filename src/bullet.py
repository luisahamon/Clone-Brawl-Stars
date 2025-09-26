"""
Sistema de projéteis do Brawl Stars Clone.
Este módulo implementa a lógica dos projéteis (tiros) do jogo, incluindo
movimento, detecção de colisão com obstáculos, diferenciação entre tiros
de jogador e inimigos, sistema de dano e efeitos visuais com renderização 3D.
"""

import random
import pygame
import time
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, TAMANHO_TIRO, COR_TIRO, VELOCIDADE_TIRO
from src.pygame_constants import SRCALPHA
from src.renderer_3d import renderer_3d

# Importar gerenciador de efeitos uma vez no topo para melhor performance
try:
    from src.efeitos_visuais import gerenciador_efeitos
    EFEITOS_DISPONIVEL = True
except ImportError:
    EFEITOS_DISPONIVEL = False

class Bullet(pygame.sprite.Sprite):
    """Classe dos projéteis com renderização 3D"""

    def __init__(self, x, y, dx, dy, de_inimigo=False, dano=25, velocidade_mult=1.0, delay=0, tipo_tiro="normal"):
        super().__init__()
        # Criar superfície com transparência para renderização 3D
        self.image = pygame.Surface((TAMANHO_TIRO * 4, TAMANHO_TIRO * 4), SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)        # Propriedades do tiro
        self.velocidade_x = dx * VELOCIDADE_TIRO * velocidade_mult
        self.velocidade_y = dy * VELOCIDADE_TIRO * velocidade_mult
        self.de_inimigo = de_inimigo
        self.dano = dano
        self.delay = delay
        self.ativo = delay <= 0
        self.tipo_tiro = tipo_tiro

        # Posição para cálculos precisos
        self.pos_x = float(x)
        self.pos_y = float(y)

        # Propriedades para rastro e efeitos
        self.cor_base = (255, 0, 0) if de_inimigo else COR_TIRO
        self.posicoes_anteriores = []
        self.tempo_criacao = time.time()
        
        # Tempo de vida limitado - tiros duram 3 segundos (alcance de 1500 pixels)
        self.tempo_vida_maximo = 3.0
        self.tempo_vida_atual = 0.0

        # Renderizar projétil inicial
        self._renderizar_projetil()

    def _renderizar_projetil(self):
        """Renderiza o projétil usando o sistema 3D"""
        self.image.fill((0, 0, 0, 0))  # Limpar superfície

        # Calcular tempo para animações
        tempo_jogo = time.time() - self.tempo_criacao
          # Usar renderer 3D para desenhar o projétil
        renderer_3d.desenhar_projetil_3d(
            self.image,
            (self.image.get_width() // 2, self.image.get_height() // 2),            self.cor_base,
            TAMANHO_TIRO,
            self.tipo_tiro,
            self.de_inimigo,
            tempo_jogo
        )

    def update(self, dt, obstaculos):
        """Atualizar posição do tiro"""
        # Verificar delay
        if self.delay > 0:
            self.delay -= dt
            if self.delay <= 0:
                self.ativo = True
            return

        if not self.ativo:
            return

        # Atualizar tempo de vida
        self.tempo_vida_atual += dt
        if self.tempo_vida_atual >= self.tempo_vida_maximo:
            self.kill()
            return

        # Mover
        self.pos_x += self.velocidade_x * dt
        self.pos_y += self.velocidade_y * dt

        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)

        # Atualizar rastro
        self.posicoes_anteriores.append((self.rect.centerx, self.rect.centery))
        if len(self.posicoes_anteriores) > 8:  # Limitar o tamanho do histórico
            self.posicoes_anteriores.pop(0)

        # Re-renderizar projétil com animação atualizada
        self._renderizar_projetil()

        # Criar efeito de rastro se disponível
        if EFEITOS_DISPONIVEL and len(self.posicoes_anteriores) > 2:
            # Criar rastro apenas ocasionalmente para performance
            if random.random() < 0.3:  # 30% de chance
                try:
                    gerenciador_efeitos.criar_rastro_projetil(
                        self.rect.centerx, self.rect.centery,
                        self.cor_base, 3
                    )
                except AttributeError:
                    pass  # Método não disponível

        # Verificar se saiu da tela (apenas para projéteis muito distantes)
        if self.fora_da_tela_distante():
            self.kill()
        
        # Verificar colisão com obstáculos
        for obstaculo in obstaculos:
            if self.rect.colliderect(obstaculo.rect):
                self.kill()
                break

    def reset(self, x, y, dx, dy, velocidade_mult=1.0, dano=25, de_inimigo=False, tipo_tiro="normal"):
        """
        Resetar projétil para reutilização no object pool.
        Args:
            x: Nova posição X
            y: Nova posição Y
            dx: Nova direção X
            dy: Nova direção Y
            velocidade_mult: Multiplicador de velocidade
            dano: Dano do projétil
            de_inimigo: Se o tiro é de um inimigo
            tipo_tiro: Tipo de projétil
        """
        self.rect.center = (x, y)
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.velocidade_x = dx * VELOCIDADE_TIRO * velocidade_mult
        self.velocidade_y = dy * VELOCIDADE_TIRO * velocidade_mult
        self.dano = dano
        self.de_inimigo = de_inimigo
        self.tipo_tiro = tipo_tiro
        self.ativo = True
        self.delay = 0
        self.tempo_vida_atual = 0.0  # Resetar tempo de vida

        # Atualizar cor baseada no tipo e origem
        self.cor_base = (255, 0, 0) if de_inimigo else COR_TIRO
        self.tempo_criacao = time.time()        # Limpar rastro anterior
        self.posicoes_anteriores.clear()

        # Re-renderizar com novos parâmetros
        self._renderizar_projetil()

    def fora_da_tela(self):
        """
        Verificar se o projétil está fora da tela.
        Returns:
            True se estiver fora da tela
        """
        return (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
                self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT)

    def fora_da_tela_distante(self):
        """
        Verificar se o projétil está muito longe da tela (margem de segurança).
        Returns:
            True se estiver muito distante da tela
        """
        margem = 200  # Pixels de margem além da tela
        return (self.rect.right < -margem or self.rect.left > SCREEN_WIDTH + margem or
                self.rect.bottom < -margem or self.rect.top > SCREEN_HEIGHT + margem)

    def desativar(self):
        """Desativar projétil (para object pooling)."""
        self.ativo = False
