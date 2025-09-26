"""
Sistema de Interface Moderna estilo Brawl Stars.
Este módulo implementa elementos de UI com animações suaves,
micro-interações e o visual característico do Brawl Stars.
"""

import math
import random
from typing import Tuple, List, Optional, Callable
import pygame
from src.pygame_constants import SRCALPHA

class ElementoUIAnimado:
    """Classe base para elementos de UI com animações"""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.enabled = True

        # Sistema de animação
        self.escala_atual = 1.0
        self.escala_target = 1.0
        self.rotacao_atual = 0.0
        self.alpha_atual = 255
        self.alpha_target = 255

        # Estados de interação
        self.hover = False
        self.pressed = False
        self.animacao_hover_tempo = 0.0

        # Efeitos visuais
        self.brilho_intensidade = 0.0
        self.particulas_ativas = []

    def atualizar(self, dt: float):
        """Atualiza animações do elemento"""
        # Suavizar transições
        self.escala_atual += (self.escala_target - self.escala_atual) * dt * 8
        self.alpha_atual += (self.alpha_target - self.alpha_atual) * dt * 10

        # Animação de hover
        if self.hover:
            self.animacao_hover_tempo += dt * 6
        else:
            self.animacao_hover_tempo = max(0, self.animacao_hover_tempo - dt * 8)

        # Atualizar partículas
        self.particulas_ativas = [p for p in self.particulas_ativas if p['vida'] > 0]
        for particula in self.particulas_ativas:
            particula['vida'] -= dt
            particula['y'] -= particula['vel_y'] * dt
            particula['vel_y'] += 100 * dt  # Gravidade

    def obter_rect(self) -> pygame.Rect:
        """Retorna rect considerando escala atual"""
        w_scaled = int(self.width * self.escala_atual)
        h_scaled = int(self.height * self.escala_atual)
        x_centered = self.x - (w_scaled - self.width) // 2
        y_centered = self.y - (h_scaled - self.height) // 2
        return pygame.Rect(x_centered, y_centered, w_scaled, h_scaled)

    def detectar_hover(self, mouse_pos: Tuple[int, int]) -> bool:
        """Detecta se o mouse está sobre o elemento"""
        rect = self.obter_rect()
        novo_hover = rect.collidepoint(mouse_pos)
        if novo_hover and not self.hover:
            self.on_hover_enter()
        elif not novo_hover and self.hover:
            self.on_hover_exit()

        self.hover = novo_hover
        return self.hover

    def on_hover_enter(self):
        """Callback quando mouse entra no elemento"""
        self.escala_target = 1.05
        self.criar_particulas_hover()

    def on_hover_exit(self):
        """Callback quando mouse sai do elemento"""
        self.escala_target = 1.0

    def criar_particulas_hover(self):
        """Cria partículas quando hover é ativado"""
        for _ in range(5):
            self.particulas_ativas.append({
                'x': self.x + random.randint(0, self.width),
                'y': self.y + self.height,
                'vel_y': random.randint(50, 100),
                'cor': (255, 255, 255),
                'vida': 0.5,
                'tamanho': random.randint(2, 4)
            })

class BotaoBrawlStars(ElementoUIAnimado):
    """Botão estilo Brawl Stars com animações e efeitos"""

    def __init__(self, x: int, y: int, width: int, height: int, texto: str,
                 cor_fundo: Tuple[int, int, int] = (255, 165, 0),
                 cor_texto: Tuple[int, int, int] = (255, 255, 255),
                 callback: Optional[Callable] = None):
        super().__init__(x, y, width, height)
        self.texto = texto
        self.cor_fundo = cor_fundo
        self.cor_texto = cor_texto
        self.callback = callback

        # Cores para diferentes estados
        self.cor_fundo_normal = cor_fundo
        self.cor_fundo_hover = self._cor_mais_clara(cor_fundo, 30)
        self.cor_fundo_pressed = self._cor_mais_escura(cor_fundo, 20)

        # Font
        self.font = pygame.font.Font(None, int(height * 0.5))

        # Efeitos especiais
        self.outline_thickness = 3
        self.sombra_offset = 4
        self.brilho_rotacao = 0.0

    def _cor_mais_clara(self, cor: Tuple[int, int, int], incremento: int) -> Tuple[int, int, int]:
        return (min(255, cor[0] + incremento), min(255, cor[1] + incremento), min(255, cor[2] + incremento))

    def _cor_mais_escura(self, cor: Tuple[int, int, int], decremento: int) -> Tuple[int, int, int]:
        return (max(0, cor[0] - decremento), max(0, cor[1] - decremento), max(0, cor[2] - decremento))

    def atualizar(self, dt: float):
        super().atualizar(dt)
        self.brilho_rotacao += dt * 180  # Rotação do brilho

    def on_hover_enter(self):
        super().on_hover_enter()
        self.escala_target = 1.08

    def on_click(self):
        """Chama callback quando clicado"""
        self.pressed = True
        self.escala_target = 0.95

        # Efeito de explosão de partículas
        for _ in range(15):
            angulo = random.uniform(0, 2 * math.pi)
            velocidade = random.uniform(80, 150)
            self.particulas_ativas.append({
                'x': self.x + self.width // 2,
                'y': self.y + self.height // 2,
                'vel_x': math.cos(angulo) * velocidade,
                'vel_y': math.sin(angulo) * velocidade,
                'cor': (255, 255, 0),
                'vida': 0.8,
                'tamanho': random.randint(3, 6)
            })

        if self.callback:
            self.callback()

    def on_release(self):
        """Callback quando botão é solto"""
        self.pressed = False
        self.escala_target = 1.05 if self.hover else 1.0

    def desenhar(self, surface: pygame.Surface):
        """Desenha o botão com todos os efeitos"""
        if not self.visible:
            return

        rect = self.obter_rect()

        # Determinar cor baseada no estado
        if self.pressed:
            cor_atual = self.cor_fundo_pressed
        elif self.hover:
            cor_atual = self.cor_fundo_hover
        else:
            cor_atual = self.cor_fundo_normal

        # Desenhar sombra
        sombra_rect = pygame.Rect(rect.x + self.sombra_offset, rect.y + self.sombra_offset,
                                 rect.width, rect.height)
        pygame.draw.rect(surface, (0, 0, 0, 100), sombra_rect, border_radius=rect.height//4)

        # Desenhar fundo do botão com gradiente
        self._desenhar_botao_gradiente(surface, rect, cor_atual)

        # Desenhar outline
        outline_rect = pygame.Rect(rect.x - self.outline_thickness, rect.y - self.outline_thickness,
                                  rect.width + self.outline_thickness*2, rect.height + self.outline_thickness*2)
        pygame.draw.rect(surface, (40, 40, 40), outline_rect, self.outline_thickness,
                        border_radius=rect.height//4)

        # Desenhar brilho animado se hover
        if self.hover:
            self._desenhar_brilho_animado(surface, rect)

        # Desenhar texto
        self._desenhar_texto(surface, rect)

        # Desenhar partículas
        self._desenhar_particulas(surface)

    def _desenhar_botao_gradiente(self, surface: pygame.Surface, rect: pygame.Rect,
                                 cor_base: Tuple[int, int, int]):
        """Desenha botão com gradiente vertical"""
        # Criar superfície temporária para o gradiente
        grad_surf = pygame.Surface((rect.width, rect.height), SRCALPHA)

        cor_top = self._cor_mais_clara(cor_base, 40)
        cor_bottom = self._cor_mais_escura(cor_base, 20)

        # Gradiente vertical
        for y in range(rect.height):
            ratio = y / rect.height
            r = int(cor_top[0] * (1 - ratio) + cor_bottom[0] * ratio)
            g = int(cor_top[1] * (1 - ratio) + cor_bottom[1] * ratio)
            b = int(cor_top[2] * (1 - ratio) + cor_bottom[2] * ratio)
            pygame.draw.line(grad_surf, (r, g, b), (0, y), (rect.width, y))

        # Criar máscara circular
        mask_surf = pygame.Surface((rect.width, rect.height), SRCALPHA)
        pygame.draw.rect(mask_surf, (255, 255, 255), (0, 0, rect.width, rect.height),
                        border_radius=rect.height//4)

        # Aplicar máscara
        grad_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        # Desenhar na superfície principal
        surface.blit(grad_surf, rect.topleft)

    def _desenhar_brilho_animado(self, surface: pygame.Surface, rect: pygame.Rect):
        """Desenha brilho animado que percorre o botão"""
        brilho_surf = pygame.Surface((rect.width, rect.height), SRCALPHA)

        # Posição do brilho baseada na rotação
        pos_x = int((math.sin(math.radians(self.brilho_rotacao)) + 1) * rect.width / 2)

        # Gradiente do brilho
        for i in range(20):
            alpha = max(0, 100 - i * 5)
            x = pos_x + i - 10
            if 0 <= x < rect.width:
                pygame.draw.line(brilho_surf, (255, 255, 255, alpha),
                               (x, 0), (x, rect.height))

        surface.blit(brilho_surf, rect.topleft, special_flags=pygame.BLEND_ADD)

    def _desenhar_texto(self, surface: pygame.Surface, rect: pygame.Rect):
        """Desenha texto com outline"""
        # Renderizar texto
        texto_surface = self.font.render(self.texto, True, self.cor_texto)
        texto_rect = texto_surface.get_rect(center=rect.center)

        # Desenhar outline do texto
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            outline_surface = self.font.render(self.texto, True, (0, 0, 0))
            outline_rect = outline_surface.get_rect(center=(rect.centerx + dx, rect.centery + dy))
            surface.blit(outline_surface, outline_rect)

        # Desenhar texto principal
        surface.blit(texto_surface, texto_rect)

    def _desenhar_particulas(self, surface: pygame.Surface):
        """Desenha partículas ativas"""
        for particula in self.particulas_ativas:
            alpha = int(255 * particula['vida'])
            cor_com_alpha = (*particula['cor'], alpha)

            pos_x = int(particula['x'])
            pos_y = int(particula['y'])

            if hasattr(particula, 'vel_x'):
                particula['x'] += particula['vel_x'] * 0.016  # 60 FPS estimate
                particula['y'] += particula['vel_y'] * 0.016

            # Desenhar partícula como círculo brilhante
            pygame.draw.circle(surface, particula['cor'], (pos_x, pos_y), particula['tamanho'])

            # Adicionar brilho
            brilho_surf = pygame.Surface((particula['tamanho'] * 4, particula['tamanho'] * 4), SRCALPHA)
            pygame.draw.circle(brilho_surf, (*particula['cor'], alpha//3),
                             (particula['tamanho'] * 2, particula['tamanho'] * 2), particula['tamanho'] * 2)
            surface.blit(brilho_surf, (pos_x - particula['tamanho'] * 2, pos_y - particula['tamanho'] * 2),
                        special_flags=pygame.BLEND_ADD)

class BarraProgressoAnimada(ElementoUIAnimado):
    """Barra de progresso com animações estilo Brawl Stars"""

    def __init__(self, x: int, y: int, width: int, height: int,
                 cor_fundo: Tuple[int, int, int] = (60, 60, 60),
                 cor_preenchimento: Tuple[int, int, int] = (0, 255, 100)):
        super().__init__(x, y, width, height)
        self.cor_fundo = cor_fundo
        self.cor_preenchimento = cor_preenchimento

        self.valor_atual = 0.0
        self.valor_target = 0.0
        self.valor_maximo = 1.0

        # Efeitos visuais
        self.brilho_progresso = 0.0
        self.particulas_energia = []

    def definir_valor(self, valor: float, maximo: float = 1.0):
        """Define valor da barra com animação suave"""
        self.valor_target = min(valor, maximo)
        self.valor_maximo = maximo

        # Criar partículas se valor aumentou
        if valor > self.valor_atual:
            self._criar_particulas_progresso()

    def _criar_particulas_progresso(self):
        """Cria partículas de energia quando progresso aumenta"""
        for _ in range(8):
            self.particulas_energia.append({
                'x': self.x + random.randint(0, self.width),
                'y': self.y + random.randint(0, self.height),
                'vel_x': random.uniform(-30, 30),
                'vel_y': random.uniform(-50, -20),
                'cor': self.cor_preenchimento,
                'vida': 0.6,
                'tamanho': random.randint(2, 5)
            })

    def atualizar(self, dt: float):
        super().atualizar(dt)

        # Suavizar mudança de valor
        self.valor_atual += (self.valor_target - self.valor_atual) * dt * 5

        # Animação de brilho
        self.brilho_progresso += dt * 300

        # Atualizar partículas de energia
        self.particulas_energia = [p for p in self.particulas_energia if p['vida'] > 0]
        for particula in self.particulas_energia:
            particula['vida'] -= dt
            particula['x'] += particula['vel_x'] * dt
            particula['y'] += particula['vel_y'] * dt

    def desenhar(self, surface: pygame.Surface):
        """Desenha barra de progresso com efeitos"""
        if not self.visible:
            return

        rect = self.obter_rect()
        # Desenhar sombra
        sombra_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width, rect.height)
        pygame.draw.rect(surface, (0, 0, 0, 80), sombra_rect, border_radius=rect.height//2)

        # Desenhar fundo
        pygame.draw.rect(surface, self.cor_fundo, rect, border_radius=rect.height//2)

        # Desenhar outline
        pygame.draw.rect(surface, (200, 200, 200), rect, 2, border_radius=rect.height//2)

        # Desenhar progresso
        if self.valor_atual > 0:
            progresso_width = int((self.valor_atual / self.valor_maximo) * (rect.width - 4))
            progresso_rect = pygame.Rect(rect.x + 2, rect.y + 2, progresso_width, rect.height - 4)

            # Gradiente no preenchimento
            self._desenhar_progresso_gradiente(surface, progresso_rect)

            # Brilho animado
            self._desenhar_brilho_progresso(surface, progresso_rect)

        # Desenhar partículas
        self._desenhar_particulas_energia(surface)

    def _desenhar_progresso_gradiente(self, surface: pygame.Surface, rect: pygame.Rect):
        """Desenha progresso com gradiente"""
        if rect.width <= 0:
            return

        grad_surf = pygame.Surface((rect.width, rect.height), SRCALPHA)

        cor_left = self._cor_mais_clara(self.cor_preenchimento, 50)
        cor_right = self.cor_preenchimento

        for x in range(rect.width):
            ratio = x / rect.width
            r = int(cor_left[0] * (1 - ratio) + cor_right[0] * ratio)
            g = int(cor_left[1] * (1 - ratio) + cor_right[1] * ratio)
            b = int(cor_left[2] * (1 - ratio) + cor_right[2] * ratio)
            pygame.draw.line(grad_surf, (r, g, b), (x, 0), (x, rect.height))

        # Máscara arredondada
        mask = pygame.Surface((rect.width, rect.height), SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255), (0, 0, rect.width, rect.height),
                        border_radius=rect.height//2)
        grad_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        surface.blit(grad_surf, rect.topleft)

    def _desenhar_brilho_progresso(self, surface: pygame.Surface, rect: pygame.Rect):
        """Desenha brilho animado no progresso"""
        if rect.width <= 10:
            return

        # Posição do brilho
        pos_x = int((math.sin(math.radians(self.brilho_progresso)) + 1) * (rect.width - 10) / 2)

        brilho_surf = pygame.Surface((10, rect.height), SRCALPHA)
        for i in range(10):
            alpha = 80 - i * 8
            pygame.draw.line(brilho_surf, (255, 255, 255, alpha), (i, 0), (i, rect.height))

        surface.blit(brilho_surf, (rect.x + pos_x, rect.y), special_flags=pygame.BLEND_ADD)

    def _desenhar_particulas_energia(self, surface: pygame.Surface):
        """Desenha partículas de energia"""
        for particula in self.particulas_energia:
            alpha = int(255 * particula['vida'])
            if alpha > 0:
                pos = (int(particula['x']), int(particula['y']))
                pygame.draw.circle(surface, particula['cor'], pos, particula['tamanho'])

    def _cor_mais_clara(self, cor: Tuple[int, int, int], incremento: int) -> Tuple[int, int, int]:
        return (min(255, cor[0] + incremento), min(255, cor[1] + incremento), min(255, cor[2] + incremento))

class NotificacaoPopup(ElementoUIAnimado):
    """Sistema de notificações pop-up estilo Brawl Stars"""

    def __init__(self, x: int, y: int, texto: str, tipo: str = "info", duracao: float = 3.0):
        # Calcular tamanho baseado no texto
        font = pygame.font.Font(None, 36)
        text_width, text_height = font.size(texto)
        width = text_width + 40
        height = text_height + 20
        super().__init__(x - width//2, y - height//2, width, height)
        self.texto = texto
        self.tipo = tipo
        self.duracao = duracao
        self.tempo_vida = duracao

        # Cores por tipo
        cores_tipo = {
            "info": (100, 150, 255),
            "sucesso": (100, 255, 100),
            "aviso": (255, 200, 100),
            "erro": (255, 100, 100),
            "gema": (255, 100, 255)
        }
        self.cor_fundo = cores_tipo.get(tipo, cores_tipo["info"])

        # Animação de entrada
        self.escala_atual = 0.0
        self.escala_target = 1.0
        self.alpha_atual = 0
        self.alpha_target = 255

        # Efeitos especiais
        self.particulas_explosao = []
        self._criar_particulas_entrada()

    def _criar_particulas_entrada(self):
        """Cria partículas quando notificação aparece"""
        for _ in range(12):
            angulo = random.uniform(0, 2 * math.pi)
            velocidade = random.uniform(50, 100)
            self.particulas_explosao.append({
                'x': self.x + self.width // 2,
                'y': self.y + self.height // 2,
                'vel_x': math.cos(angulo) * velocidade,
                'vel_y': math.sin(angulo) * velocidade,
                'cor': self.cor_fundo,
                'vida': 0.8,
                'tamanho': random.randint(3, 7)
            })

    def atualizar(self, dt: float):
        super().atualizar(dt)

        self.tempo_vida -= dt

        # Animação de saída
        if self.tempo_vida < 0.5:
            self.escala_target = 0.8
            self.alpha_target = int(255 * (self.tempo_vida / 0.5))

        # Atualizar partículas
        self.particulas_explosao = [p for p in self.particulas_explosao if p['vida'] > 0]
        for particula in self.particulas_explosao:
            particula['vida'] -= dt
            particula['x'] += particula['vel_x'] * dt
            particula['y'] += particula['vel_y'] * dt

    def esta_viva(self) -> bool:
        """Verifica se notificação ainda deve ser exibida"""
        return self.tempo_vida > 0

    def desenhar(self, surface: pygame.Surface):
        """Desenha notificação com efeitos"""
        if not self.visible or self.alpha_atual < 10:
            return

        rect = self.obter_rect()

        # Criar superfície com alpha
        notif_surf = pygame.Surface((rect.width, rect.height), SRCALPHA)

        # Desenhar fundo com gradiente
        cor_fundo_alpha = (*self.cor_fundo, int(self.alpha_atual * 0.9))
        cor_borda_alpha = (*self._cor_mais_clara(self.cor_fundo, 50), int(self.alpha_atual))

        pygame.draw.rect(notif_surf, cor_fundo_alpha, (0, 0, rect.width, rect.height),
                        border_radius=15)
        pygame.draw.rect(notif_surf, cor_borda_alpha, (0, 0, rect.width, rect.height),
                        3, border_radius=15)

        # Desenhar texto
        font = pygame.font.Font(None, 36)
        texto_surface = font.render(self.texto, True, (255, 255, 255))
        texto_rect = texto_surface.get_rect(center=(rect.width//2, rect.height//2))
        notif_surf.blit(texto_surface, texto_rect)

        # Aplicar na tela
        surface.blit(notif_surf, rect.topleft)

        # Desenhar partículas
        for particula in self.particulas_explosao:
            if particula['vida'] > 0:
                alpha = int(255 * particula['vida'])
                pos = (int(particula['x']), int(particula['y']))
                pygame.draw.circle(surface, particula['cor'], pos, particula['tamanho'])

    def _cor_mais_clara(self, cor: Tuple[int, int, int], incremento: int) -> Tuple[int, int, int]:
        return (min(255, cor[0] + incremento), min(255, cor[1] + incremento), min(255, cor[2] + incremento))

class GerenciadorUIModerna:
    """Gerenciador de interface moderna estilo Brawl Stars"""

    def __init__(self):
        self.elementos = []
        self.notificacoes = []
        self.transicoes_ativas = []

    def adicionar_elemento(self, elemento: ElementoUIAnimado):
        """Adiciona elemento à interface"""
        self.elementos.append(elemento)

    def remover_elemento(self, elemento: ElementoUIAnimado):
        """Remove elemento da interface"""
        if elemento in self.elementos:
            self.elementos.remove(elemento)

    def mostrar_notificacao(self, x: int, y: int, texto: str, tipo: str = "info", duracao: float = 3.0):
        """Mostra notificação pop-up"""
        notificacao = NotificacaoPopup(x, y, texto, tipo, duracao)
        self.notificacoes.append(notificacao)

    def atualizar(self, dt: float, mouse_pos: Tuple[int, int]):
        """Atualiza todos os elementos"""
        # Atualizar elementos
        for elemento in self.elementos:
            elemento.atualizar(dt)
            if hasattr(elemento, 'detectar_hover'):
                elemento.detectar_hover(mouse_pos)

        # Atualizar notificações
        self.notificacoes = [n for n in self.notificacoes if n.esta_viva()]
        for notificacao in self.notificacoes:
            notificacao.atualizar(dt)

    def processar_evento(self, evento: pygame.event.Event):
        """Processa eventos para os elementos"""
        if evento.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for elemento in reversed(self.elementos):  # Processar de cima para baixo
                if isinstance(elemento, BotaoBrawlStars) and elemento.enabled:
                    if elemento.obter_rect().collidepoint(mouse_pos):
                        elemento.on_click()
                        break

        elif evento.type == pygame.MOUSEBUTTONUP:
            for elemento in self.elementos:
                if isinstance(elemento, BotaoBrawlStars) and elemento.pressed:
                    elemento.on_release()

    def desenhar(self, surface: pygame.Surface):
        """Desenha todos os elementos"""
        # Desenhar elementos
        for elemento in self.elementos:
            elemento.desenhar(surface)

        # Desenhar notificações por último
        for notificacao in self.notificacoes:
            notificacao.desenhar(surface)

# Instância global
ui_manager = GerenciadorUIModerna()
