"""
Menu Principal do Brawl Stars Clone.
Este módulo implementa o menu principal do jogo com estilo cartoon fiel ao Brawl Stars,
incluindo logo, botões animados, efeitos visuais e música de fundo energética.
"""

import math
import random
import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,  COR_TEXTO,
    COR_BOTAO_NORMAL, COR_BOTAO_HOVER, COR_BOTAO_SELECIONADO
)
from src.audio_manager import gerenciador_audio
from src.pygame_constants import MOUSEBUTTONDOWN, MOUSEMOTION, SRCALPHA

class BotaoMenu:
    """Botão animado estilo cartoon para o menu"""

    def __init__(self, x, y, largura, altura, texto, acao=None):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.acao = acao
        self.hover = False
        self.selecionado = False
        self.animacao_scale = 1.0
        self.animacao_bounce = 0.0
        self.cor_atual = COR_BOTAO_NORMAL
        self.tempo_animacao = 0.0

        # Fontes proporcionais
        tamanho_fonte = max(24, SCREEN_HEIGHT // 40)
        self.font = pygame.font.Font(None, tamanho_fonte)
        self.font_sombra = pygame.font.Font(None, tamanho_fonte + 2)

    def update(self, dt):
        """Atualizar animações do botão"""
        self.tempo_animacao += dt        # Animação de bounce
        self.animacao_bounce = math.sin(self.tempo_animacao * 3) * 0.05        # Animação de escala
        if self.hover or self.selecionado:
            self.animacao_scale = min(self.animacao_scale + dt * 3, 1.1)
            self.cor_atual = COR_BOTAO_HOVER if self.hover else COR_BOTAO_SELECIONADO
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
                if self.acao:
                    return self.acao()
        return None

    def draw(self, screen):
        """Desenhar botão com efeitos"""
        # Calcular posição com animação
        scale = self.animacao_scale + self.animacao_bounce
        largura_scaled = int(self.rect.width * scale)
        altura_scaled = int(self.rect.height * scale)

        pos_x = self.rect.centerx - largura_scaled // 2
        pos_y = self.rect.centery - altura_scaled // 2

        # Sombra múltipla para profundidade
        for i, offset in enumerate([(8, 8), (6, 6), (4, 4)]):
            alpha = 50 - i * 10
            sombra_rect = pygame.Rect(pos_x + offset[0], pos_y + offset[1],
            largura_scaled, altura_scaled)
            sombra_surface = pygame.Surface((largura_scaled, altura_scaled), SRCALPHA)
            pygame.draw.rect(sombra_surface, (0, 0, 0, alpha),
            sombra_surface.get_rect(), border_radius=20)
            screen.blit(sombra_surface, sombra_rect)

        # Botão principal com gradiente
        botao_rect = pygame.Rect(pos_x, pos_y, largura_scaled, altura_scaled)

        # Simular gradiente desenhando retângulos
        for i in range(altura_scaled):
            cor_gradiente = []
            for j in range(3):  # RGB
                cor_base = self.cor_atual[j]
                intensidade = 1.0 - (i / altura_scaled) * 0.3  # Gradiente de cima para baixo
                cor_gradiente.append(int(cor_base * intensidade))

            linha_rect = pygame.Rect(pos_x, pos_y + i, largura_scaled, 1)
            pygame.draw.rect(screen, cor_gradiente, linha_rect)

        # Borda dupla estilo cartoon
        pygame.draw.rect(screen, (255, 255, 255), botao_rect, 4, border_radius=20)
        pygame.draw.rect(screen, (0, 0, 0), botao_rect, 2, border_radius=20)

        # Destaque se hover/selecionado
        if self.hover or self.selecionado:
            destaque_rect = pygame.Rect(pos_x + 4, pos_y + 4, largura_scaled - 8, altura_scaled - 8)
            destaque_surface = pygame.Surface((largura_scaled - 8, altura_scaled - 8), SRCALPHA)
            pygame.draw.rect(destaque_surface, (255, 255, 255, 30), destaque_surface.get_rect(), border_radius=16)
            screen.blit(destaque_surface, destaque_rect)

        # Texto com múltiplas sombras
        for offset in [(3, 3), (2, 2), (1, 1)]:
            texto_sombra = self.font_sombra.render(self.texto, True, (0, 0, 0))
            sombra_rect = texto_sombra.get_rect(center=(botao_rect.centerx + offset[0], botao_rect.centery + offset[1]))
            screen.blit(texto_sombra, sombra_rect)

        # Texto principal
        texto_main = self.font.render(self.texto, True, COR_TEXTO)
        texto_rect = texto_main.get_rect(center=botao_rect.center)
        screen.blit(texto_main, texto_rect)


class LogoAnimado:
    """Logo animado para o menu principal"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tempo_animacao = 0.0
        self.escala_base = 1.0
        self.rotacao = 0.0
        self.brilho = 0.0
        self.particulas_logo = []

        # Criar partículas especiais para o logo
        for _ in range(15):
            self.particulas_logo.append({
                'x': random.uniform(-30, 30),
                'y': random.uniform(-20, 20),
                'vel': random.uniform(0.5, 2.0),
                'fase': random.uniform(0, math.pi * 2),
                'raio': random.uniform(20, 40),
                'cor': random.choice([(255, 215, 0), (255, 100, 100), (100, 255, 100), (100, 100, 255)])
            })        # Criar logo como texto estilizado
        self.tamanho_logo = max(60, SCREEN_HEIGHT // 18)
        self.tamanho_subtitulo = max(20, SCREEN_HEIGHT // 50)
        self.font_logo = pygame.font.Font(None, self.tamanho_logo)
        self.font_subtitulo = pygame.font.Font(None, self.tamanho_subtitulo)

    def update(self, dt):
        """Atualizar animações do logo"""
        self.tempo_animacao += dt

        # Animação de respiração mais suave
        self.escala_base = 1.0 + math.sin(self.tempo_animacao * 1.5) * 0.08

        # Animação de brilho mais dinâmica
        self.brilho = (math.sin(self.tempo_animacao * 2) + 1) * 0.5

        # Rotação mais sutil
        self.rotacao = math.sin(self.tempo_animacao * 0.3) * 1.5
        # Atualizar partículas do logo
        for particula in self.particulas_logo:
            particula['fase'] += dt * particula['vel']

    def draw(self, screen):
        """Desenhar logo animado"""
        # Desenhar partículas de fundo do logo primeiro
        for particula in self.particulas_logo:
            px = self.x + particula['x'] + math.cos(particula['fase']) * particula['raio']
            py = self.y + particula['y'] + math.sin(particula['fase']) * particula['raio'] * 0.3

            # Tamanho da partícula varia com o tempo
            tamanho = 3 + int(2 * math.sin(particula['fase'] * 2))

            if 0 <= px <= SCREEN_WIDTH and 0 <= py <= SCREEN_HEIGHT:
                alpha = int(100 + 50 * math.sin(particula['fase']))
                cor_particula = (*particula['cor'], alpha)

                surface = pygame.Surface((tamanho * 2, tamanho * 2), SRCALPHA)
                pygame.draw.circle(surface, cor_particula, (tamanho, tamanho), tamanho)
                screen.blit(surface, (px - tamanho, py - tamanho))

        # Título principal
        titulo = "BRAWL STARS"
        subtitulo = "CLONE"

        # Cores mais vibrantes
        cor_titulo = (255, 215, 0)  # Dourado
        cor_subtitulo = (255, 100, 100)  # Vermelho claro
        cor_borda = (139, 69, 19)  # Marrom para borda

        # Renderizar textos
        texto_titulo = self.font_logo.render(titulo, True, cor_titulo)
        texto_subtitulo = self.font_subtitulo.render(subtitulo, True, cor_subtitulo)

        # Aplicar escala
        largura_titulo = int(texto_titulo.get_width() * self.escala_base)
        altura_titulo = int(texto_titulo.get_height() * self.escala_base)
        texto_titulo_scaled = pygame.transform.scale(texto_titulo, (largura_titulo, altura_titulo))

        # Posicionar
        titulo_rect = texto_titulo_scaled.get_rect(center=(self.x, self.y))
        subtitulo_rect = texto_subtitulo.get_rect(center=(self.x, self.y + self.tamanho_logo))

        # Sombra múltipla para profundidade
        for offset in [(5, 5), (3, 3), (1, 1)]:
            sombra_titulo = pygame.transform.scale(
                self.font_logo.render(titulo, True, (0, 0, 0)),
                (largura_titulo, altura_titulo)
            )
            sombra_rect = sombra_titulo.get_rect(center=(self.x + offset[0], self.y + offset[1]))
            screen.blit(sombra_titulo, sombra_rect)

        # Borda do texto
        borda_titulo = pygame.transform.scale(
            self.font_logo.render(titulo, True, cor_borda),
            (largura_titulo + 4, altura_titulo + 4)
        )
        borda_rect = borda_titulo.get_rect(center=(self.x, self.y))
        screen.blit(borda_titulo, borda_rect)

        # Desenhar texto principal
        screen.blit(texto_titulo_scaled, titulo_rect)

        # Sombra do subtítulo
        sombra_subtitulo = self.font_subtitulo.render(subtitulo, True, (0, 0, 0))
        sombra_sub_rect = sombra_subtitulo.get_rect(center=(self.x + 2, self.y + self.tamanho_logo + 2))
        screen.blit(sombra_subtitulo, sombra_sub_rect)
        screen.blit(texto_subtitulo, subtitulo_rect)

        # Efeito de brilho mais intenso
        if self.brilho > 0.6:
            overlay = pygame.Surface((largura_titulo, altura_titulo), SRCALPHA)
            overlay.fill((255, 255, 255, int((self.brilho - 0.6) * 255)))
            screen.blit(overlay, titulo_rect)


class MenuPrincipal:
    """Menu principal do jogo"""

    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.ativo = True
        self.opcao_selecionada = 0
        self.tempo_entrada = 0.0
        self.animacao_entrada = True

        # Criar logo
        self.logo = LogoAnimado(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)  # 25% da altura (mais para baixo)

        # Criar botões
        self.botoes = []
        largura_botao = SCREEN_WIDTH // 8  # Um pouco maior
        altura_botao = SCREEN_HEIGHT // 20  # Um pouco maior
        espaco_entre_botoes = altura_botao + 10  # Mais espaço entre botões
        pos_x = (SCREEN_WIDTH - largura_botao) // 2
        pos_y_inicial = SCREEN_HEIGHT // 2 - 50  # Mais para cima

        opcoes_menu = ["Iniciar Jogo", "Progressão", "Configurações", "Conquistas", "Sair"]
        for i, opcao in enumerate(opcoes_menu):
            pos_y = pos_y_inicial + i * espaco_entre_botoes
            botao = BotaoMenu(pos_x, pos_y, largura_botao, altura_botao, opcao, acao=self._criar_acao(opcao))
            self.botoes.append(botao)        # Som ambiente sutil ao invés de música
        if gerenciador_audio.som_disponivel('ambiente_menu'):
            gerenciador_audio.tocar_som('ambiente_menu', volume=0.1)

    def _criar_acao(self, opcao):
        """Cria uma função de ação para o botão."""
        def acao():
            return self.selecionar_opcao(opcao)
        return acao

    def update(self, dt):
        """Atualizar menu"""
        self.tempo_entrada += dt

        # Atualizar logo
        self.logo.update(dt)        # Atualizar botões
        for i, botao in enumerate(self.botoes):
            botao.selecionado = i == self.opcao_selecionada
            botao.update(dt)

    def handle_event(self, event):
        """Processa eventos do menu principal."""
        for botao in self.botoes:
            acao = botao.handle_event(event)
            if acao:
                return acao

    def selecionar_opcao(self, opcao):
        """Executa a ação correspondente à opção selecionada."""
        if opcao == "Conquistas":
            return "conquistas"
        elif opcao == "Progressão":
            return "progressao"
        elif opcao == "Iniciar Jogo":
            return "jogar"
        elif opcao == "Configurações":
            return "configuracoes"
        elif opcao == "Sair":
            return "sair"

    def exibir_conquistas(self):
        """Exibe a lista de conquistas desbloqueadas."""
        print("Conquistas Desbloqueadas:")
        for conquista in self.game.sistema_conquistas.conquistas:
            status = "[✔]" if conquista.alcancada else "[ ]"
            print(f"{status} {conquista.nome} - {conquista.descricao}")

    def draw(self, screen):
        """Desenha o menu principal na tela."""
        # Fundo gradiente animado mais complexo
        for y in range(SCREEN_HEIGHT):
            progresso = y / SCREEN_HEIGHT
            # Animação de ondas no fundo
            onda = math.sin(self.tempo_entrada * 2 + progresso * 4) * 0.1

            cor_r = int(20 + progresso * 25 + onda * 10)
            cor_g = int(25 + progresso * 35 + onda * 15)
            cor_b = int(50 + progresso * 45 + onda * 20)

            # Garantir que as cores estejam no intervalo válido
            cor_r = max(0, min(255, cor_r))
            cor_g = max(0, min(255, cor_g))
            cor_b = max(0, min(255, cor_b))

            pygame.draw.line(screen, (cor_r, cor_g, cor_b), (0, y), (SCREEN_WIDTH, y))

        # Desenhar logo
        self.logo.draw(screen)

        # Desenhar botões
        for botao in self.botoes:
            botao.draw(screen)

        # Efeito de entrada suave
        if self.animacao_entrada:
            alpha = int(255 * (1.0 - min(self.tempo_entrada / 1.5, 1.0)))  # Transição mais lenta
            if alpha > 0:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), SRCALPHA)
                overlay.fill((0, 0, 0, alpha))
                screen.blit(overlay, (0, 0))
