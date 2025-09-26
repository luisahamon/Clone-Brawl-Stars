"""
Menu de Conquistas do Brawl Stars Clone.
Este módulo implementa a interface gráfica para exibir as conquistas
do jogador com estilo cartoon fiel ao Brawl Stars.
"""

import math
import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COR_TEXTO,
    COR_BOTAO_NORMAL, COR_BOTAO_HOVER
)
from src.audio_manager import gerenciador_audio
from src.pygame_constants import MOUSEBUTTONDOWN, MOUSEMOTION, SRCALPHA, K_UP, K_DOWN

class BotaoVoltar:
    """Botão de voltar estilizado"""

    def __init__(self, x, y, largura, altura):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.hover = False
        self.animacao_scale = 1.0
        self.cor_atual = COR_BOTAO_NORMAL
        self.font = pygame.font.Font(None, 32)  # Ajustado para resolução 1280x720

    def update(self, dt):
        """Atualizar animações do botão"""
        if self.hover:
            self.animacao_scale = min(self.animacao_scale + dt * 3, 1.1)
            self.cor_atual = COR_BOTAO_HOVER
        else:
            self.animacao_scale = max(self.animacao_scale - dt * 3, 1.0)
            self.cor_atual = COR_BOTAO_NORMAL

    def handle_event(self, event):
        """Processar eventos do botão"""
        if event.type == MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                gerenciador_audio.tocar_som('ui_click', canal='ui')
                return "voltar"
        return None

    def draw(self, screen):
        """Desenhar botão"""
        # Calcular posição com animação
        scale = self.animacao_scale
        largura_scaled = int(self.rect.width * scale)
        altura_scaled = int(self.rect.height * scale)
        pos_x = self.rect.centerx - largura_scaled // 2
        pos_y = self.rect.centery - altura_scaled // 2

        # Sombra
        sombra_rect = pygame.Rect(pos_x + 4, pos_y + 4, largura_scaled, altura_scaled)
        sombra_surface = pygame.Surface((largura_scaled, altura_scaled), SRCALPHA)
        pygame.draw.rect(sombra_surface, (0,0,0,100), sombra_surface.get_rect(), border_radius=15)
        screen.blit(sombra_surface, sombra_rect)

        # Botão principal
        botao_rect = pygame.Rect(pos_x, pos_y, largura_scaled, altura_scaled)
        pygame.draw.rect(screen, self.cor_atual, botao_rect, border_radius=15)
        pygame.draw.rect(screen, (255, 255, 255), botao_rect, 3, border_radius=15)

        # Texto
        texto = self.font.render("← Voltar", True, COR_TEXTO)
        texto_rect = texto.get_rect(center=botao_rect.center)
        screen.blit(texto, texto_rect)


class ItemConquista:
    """Item de conquista na lista"""
    def __init__(self, conquista, x, y, largura, altura):
        self.conquista = conquista
        self.rect = pygame.Rect(x, y, largura, altura)
        self.animacao_bounce = 0.0
        self.tempo_animacao = 0.0

        # Fontes ajustadas para resolução 1280x720
        self.font_titulo = pygame.font.Font(None, 32)
        self.font_descricao = pygame.font.Font(None, 22)

        # Cores
        self.cor_fundo = (40, 50, 70) if conquista.alcancada else (60, 60, 60)
        self.cor_borda = (255, 215, 0) if conquista.alcancada else (120, 120, 120)
        self.cor_titulo = (255, 255, 255) if conquista.alcancada else (180, 180, 180)
        self.cor_descricao = (200, 200, 200) if conquista.alcancada else (140, 140, 140)

    def update(self, dt):
        """Atualizar animações"""
        self.tempo_animacao += dt
        if self.conquista.alcancada:
            self.animacao_bounce = math.sin(self.tempo_animacao * 2) * 0.02

    def draw(self, screen):
        """Desenhar item de conquista"""
        # Calcular posição com animação
        offset_y = int(self.animacao_bounce * 10)

        # Sombra
        sombra_rect = pygame.Rect(self.rect.x + 4, self.rect.y + 4 + offset_y,
                                 self.rect.width, self.rect.height)
        sombra_surface = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        pygame.draw.rect(sombra_surface, (0, 0, 0, 80), sombra_surface.get_rect(), border_radius=10)
        screen.blit(sombra_surface, sombra_rect)

        # Fundo da conquista
        item_rect = pygame.Rect(self.rect.x, self.rect.y + offset_y,
                               self.rect.width, self.rect.height)
        pygame.draw.rect(screen, self.cor_fundo, item_rect, border_radius=10)
        pygame.draw.rect(screen, self.cor_borda, item_rect, 3, border_radius=10)

        # Ícone de status com tamanho ajustado para resolução HD
        icone_x = item_rect.x + 20
        icone_y = item_rect.centery
        icone_raio = 15  # Tamanho adequado para HD

        if self.conquista.alcancada:
            # Ícone de check dourado
            pygame.draw.circle(screen, (255, 215, 0), (icone_x, icone_y), icone_raio)
            pygame.draw.circle(screen, (255, 255, 255), (icone_x, icone_y), icone_raio, 2)

            # Desenhar check com tamanho adequado para HD
            check_points = [
                (icone_x - 6, icone_y),
                (icone_x - 2, icone_y + 4),
                (icone_x + 6, icone_y - 4)
            ]
            pygame.draw.lines(screen, (255, 255, 255), False, check_points, 3)
        else:
            # Ícone de lock cinza
            pygame.draw.circle(screen, (100, 100, 100), (icone_x, icone_y), icone_raio)
            pygame.draw.circle(screen, (150, 150, 150), (icone_x, icone_y), icone_raio, 2)

            # Desenhar cadeado com tamanho adequado para HD
            pygame.draw.rect(screen, (200, 200, 200),
                           (icone_x - 4, icone_y - 2, 8, 6), border_radius=2)
            pygame.draw.arc(screen, (200, 200, 200),
                          (icone_x - 3, icone_y - 8, 6, 8), 0, math.pi, 2)

        # Título da conquista com espaçamento adequado para HD
        titulo = self.font_titulo.render(self.conquista.nome, True, self.cor_titulo)
        titulo_rect = pygame.Rect(icone_x + 40, item_rect.y + 10,
                                 item_rect.width - 80, 25)
        screen.blit(titulo, titulo_rect)

        # Descrição da conquista com espaçamento adequado para HD
        descricao = self.font_descricao.render(self.conquista.descricao, True, self.cor_descricao)
        descricao_rect = pygame.Rect(icone_x + 40, item_rect.y + 40,
                                   item_rect.width - 80, 20)
        screen.blit(descricao, descricao_rect)

        # Progresso (se disponível) com posição adequada para HD
        if hasattr(self.conquista, 'progresso_atual') and hasattr(self.conquista, 'progresso_total'):
            progresso_texto = f"{self.conquista.progresso_atual}/{self.conquista.progresso_total}"
            progresso_surface=self.font_descricao.render(progresso_texto, True, self.cor_descricao)
            progresso_rect = progresso_surface.get_rect()
            progresso_rect.right = item_rect.right - 20
            progresso_rect.centery = item_rect.centery
            screen.blit(progresso_surface, progresso_rect)


class MenuConquistas:
    """Menu para exibir conquistas"""
    def __init__(self, screen, sistema_conquistas):
        self.screen = screen
        self.sistema_conquistas = sistema_conquistas
        self.tempo_entrada = 0.0
        self.animacao_entrada = True

        # Botão voltar ajustado para resolução 1280x720
        self.botao_voltar = BotaoVoltar(50, SCREEN_HEIGHT - 70, 120, 50)

        # Lista de conquistas
        self.itens_conquistas = []
        self.scroll_y = 0
        self.max_scroll = 0
        self.criar_lista_conquistas()

        # Estatísticas
        self.conquistas_alcancadas = sum(1 for c in sistema_conquistas.conquistas if c.alcancada)
        self.total_conquistas = len(sistema_conquistas.conquistas)

        # Fontes ajustadas para resolução 1280x720
        self.font_titulo = pygame.font.Font(None, 56)
        self.font_estatisticas = pygame.font.Font(None, 32)

    def criar_lista_conquistas(self):
        """Criar lista visual de conquistas ajustada para resolução 1280x720"""
        self.itens_conquistas = []

        inicio_y = 150  # Posição adequada para HD
        altura_item = 80  # Altura adequada
        espaco_entre_itens = 10
        largura_item = SCREEN_WIDTH - 100

        for i, conquista in enumerate(self.sistema_conquistas.conquistas):
            y = inicio_y + i * (altura_item + espaco_entre_itens)
            item = ItemConquista(conquista, 50, y, largura_item, altura_item)
            self.itens_conquistas.append(item)

        # Calcular scroll máximo
        ultima_conquista_y = self.itens_conquistas[-1].rect.bottom if self.itens_conquistas else 0
        self.max_scroll = max(0, ultima_conquista_y - SCREEN_HEIGHT + 100)

    def update(self, dt):
        """Atualizar menu"""
        self.tempo_entrada += dt

        # Atualizar botão
        self.botao_voltar.update(dt)

        # Atualizar itens de conquistas
        for item in self.itens_conquistas:
            item.update(dt)

        # Controle de scroll com mouse
        keys = pygame.key.get_pressed()
        if keys[K_UP] and self.scroll_y > 0:
            self.scroll_y = max(0, self.scroll_y - 300 * dt)
        elif keys[K_DOWN] and self.scroll_y < self.max_scroll:
            self.scroll_y = min(self.max_scroll, self.scroll_y + 300 * dt)

    def handle_event(self, event):
        """Processar eventos"""
        # Botão voltar
        acao = self.botao_voltar.handle_event(event)
        if acao:
            return acao

        # Scroll com roda do mouse
        if event.type == 1027:  # Valor padrão de pygame.MOUSEWHEEL
            if event.y > 0 and self.scroll_y > 0:
                self.scroll_y = max(0, self.scroll_y - 50)
            elif event.y < 0 and self.scroll_y < self.max_scroll:
                self.scroll_y = min(self.max_scroll, self.scroll_y + 50)
        return None

    def draw(self, screen):
        """Desenhar menu de conquistas"""
        # Fundo gradiente
        for y in range(SCREEN_HEIGHT):
            progresso = y / SCREEN_HEIGHT
            cor_r = int(15 + progresso * 20)
            cor_g = int(20 + progresso * 25)
            cor_b = int(40 + progresso * 30)
            pygame.draw.line(screen, (cor_r, cor_g, cor_b), (0, y), (SCREEN_WIDTH, y))

        # Título centralizado
        titulo = self.font_titulo.render("CONQUISTAS", True, (255, 215, 0))
        titulo_rect = titulo.get_rect(center=(SCREEN_WIDTH // 2, 50))

        # Sombra do título
        titulo_sombra = self.font_titulo.render("CONQUISTAS", True, (0, 0, 0))
        sombra_rect = titulo_sombra.get_rect(center=(SCREEN_WIDTH // 2 + 2, 52))
        screen.blit(titulo_sombra, sombra_rect)
        screen.blit(titulo, titulo_rect)

        # Estatísticas centralizadas
        estatisticas_texto = f"{self.conquistas_alcancadas}/{self.total_conquistas} Desbloqueadas"
        estatisticas = self.font_estatisticas.render(estatisticas_texto, True, (200, 200, 200))
        estatisticas_rect = estatisticas.get_rect(center=(SCREEN_WIDTH // 2, 90))
        screen.blit(estatisticas, estatisticas_rect)

        # Criar surface para scroll
        lista_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - 140), SRCALPHA)

        # Desenhar conquistas com offset de scroll
        for item in self.itens_conquistas:
            item_rect_ajustado = item.rect.copy()
            item_rect_ajustado.y -= self.scroll_y

            # Só desenhar se estiver visível
            if -item.rect.height <= item_rect_ajustado.y <= SCREEN_HEIGHT:
                # Criar surface temporária para o item
                item_surface = pygame.Surface((item.rect.width, item.rect.height), SRCALPHA)

                # Ajustar rect do item para desenhar na surface temporária
                item_temp = ItemConquista(item.conquista, 0, 0, item.rect.width, item.rect.height)
                item_temp.tempo_animacao = item.tempo_animacao
                item_temp.update(0)  # Não avançar tempo, só aplicar estado atual
                item_temp.draw(item_surface)

                # Blit na surface da lista
                lista_surface.blit(item_surface, (item.rect.x, item_rect_ajustado.y))

        # Blit a lista na tela
        screen.blit(lista_surface, (0, 140))

        # Indicador de scroll ajustado
        if self.max_scroll > 0:
            altura_base = SCREEN_HEIGHT - 140
            scroll_altura = max(20, int(altura_base*altura_base / (self.max_scroll + altura_base)))
            scroll_y = int(140 + (altura_base - scroll_altura) * (self.scroll_y / self.max_scroll))
            pygame.draw.rect(screen, (100,100,100), (SCREEN_WIDTH-15, 140, 10, altura_base))
            pygame.draw.rect(screen, (200,200,200), (SCREEN_WIDTH-15, scroll_y, 10, scroll_altura))

        # Botão voltar
        self.botao_voltar.draw(screen)

        # Efeito de entrada
        if self.animacao_entrada:
            alpha = int(255 * (1.0 - min(self.tempo_entrada / 1.0, 1.0)))
            if alpha > 0:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), SRCALPHA)
                overlay.fill((0, 0, 0, alpha))
                screen.blit(overlay, (0, 0))
