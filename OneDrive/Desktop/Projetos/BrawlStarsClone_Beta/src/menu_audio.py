"""
Menu de configurações de áudio para o Brawl Stars Clone.

Este módulo implementa a interface de configuração de áudio do jogo,
permitindo ao jogador ajustar volume geral, efeitos sonoros, música
e testar configurações de áudio em tempo real.
"""

import pygame
from src.config import SCREEN_WIDTH, COR_UI, COR_FUNDO
from src.audio_manager import gerenciador_audio
from src.pygame_constants import (KEYDOWN, K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_RETURN,
MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP)

class MenuAudio:
    """Menu para configurar áudio do jogo"""

    def __init__(self, screen):
        self.screen = screen
        # Fontes ajustadas para resolução 1280x720
        self.font_titulo = pygame.font.Font(None, 48)
        self.font_opcao = pygame.font.Font(None, 32)
        self.font_valor = pygame.font.Font(None, 24)

        self.opcao_selecionada = 0
        self.opcoes = [
            {'nome': 'Volume Geral', 'tipo': 'slider', 'valor': 'master', 'rect': None, 'slider_rect': None},
            {'nome': 'Efeitos Sonoros', 'tipo': 'slider', 'valor': 'sfx', 'rect': None, 'slider_rect': None},
            {'nome': 'Música', 'tipo': 'slider', 'valor': 'music', 'rect': None, 'slider_rect': None},
            {'nome': 'Testar Som', 'tipo': 'botao', 'acao': 'test_sound', 'rect': None},
            {'nome': 'Voltar', 'tipo': 'botao', 'acao': 'back', 'rect': None}
        ]

        # Configurações atuais
        self.volumes = gerenciador_audio.obter_volumes()

        # Mouse
        self.mouse_pos = (0, 0)
        self.mouse_pressed = False
        self.dragging_slider = None

        # Cores
        self.cor_texto = (255, 255, 255)
        self.cor_selecionado = (255, 215, 0)
        self.cor_slider = (100, 100, 100)
        self.cor_slider_preenchido = (0, 255, 0)

    def handle_event(self, event):
        """Processar eventos do menu"""
        if event.type == MOUSEMOTION:
            self.mouse_pos = event.pos

            # Se estamos arrastando um slider, atualizar o volume
            if self.mouse_pressed and self.dragging_slider:
                self._ajustar_volume_mouse(self.dragging_slider, event.pos)

            # Verificar hover nos itens
            for i, opcao in enumerate(self.opcoes):
                if opcao['rect'] and opcao['rect'].collidepoint(event.pos):
                    if self.opcao_selecionada != i:
                        gerenciador_audio.tocar_som('ui_select')
                        self.opcao_selecionada = i

        elif event.type == MOUSEBUTTONDOWN:
            self.mouse_pressed = True

            # Verificar clique nos sliders
            for i, opcao in enumerate(self.opcoes):
                if opcao['tipo'] == 'slider' and opcao.get('slider_rect'):
                    if opcao['slider_rect'].collidepoint(event.pos):
                        self.dragging_slider = opcao
                        self._ajustar_volume_mouse(opcao, event.pos)
                        break
                elif opcao['rect'] and opcao['rect'].collidepoint(event.pos):
                    if opcao['tipo'] == 'botao':
                        gerenciador_audio.tocar_som('ui_confirm')
                        return self._executar_acao(opcao['acao'])

        elif event.type == MOUSEBUTTONUP:
            self.mouse_pressed = False
            self.dragging_slider = None

        elif event.type == KEYDOWN:
            if event.key == K_UP:
                gerenciador_audio.tocar_som('ui_select')
                self.opcao_selecionada = (self.opcao_selecionada - 1) % len(self.opcoes)

            elif event.key == K_DOWN:
                gerenciador_audio.tocar_som('ui_select')
                self.opcao_selecionada = (self.opcao_selecionada + 1) % len(self.opcoes)

            elif event.key == K_LEFT:
                opcao = self.opcoes[self.opcao_selecionada]
                if opcao['tipo'] == 'slider':
                    gerenciador_audio.tocar_som('ui_select')
                    self._ajustar_volume(opcao['valor'], -0.05)

            elif event.key == K_RIGHT:
                opcao = self.opcoes[self.opcao_selecionada]
                if opcao['tipo'] == 'slider':
                    gerenciador_audio.tocar_som('ui_select')
                    self._ajustar_volume(opcao['valor'], 0.05)

            elif event.key == K_RETURN:
                opcao = self.opcoes[self.opcao_selecionada]
                if opcao['tipo'] == 'botao':
                    gerenciador_audio.tocar_som('ui_confirm')
                    return self._executar_acao(opcao['acao'])

            elif event.key == K_ESCAPE:
                gerenciador_audio.tocar_som('ui_back')
                return 'voltar'

        return None

    def _ajustar_volume_mouse(self, opcao, pos_mouse):
        """Ajustar volume baseado na posição do mouse"""
        if opcao.get('slider_rect'):
            # Calcular percentual baseado na posição X do mouse no slider
            slider_rect = opcao['slider_rect']
            pos_relativa = pos_mouse[0] - slider_rect.x
            percentual = max(0.0, min(1.0, pos_relativa / slider_rect.width))

            if opcao['valor'] == 'master':
                gerenciador_audio.definir_volume_master(percentual)
            elif opcao['valor'] == 'sfx':
                gerenciador_audio.definir_volume_sfx(percentual)
            elif opcao['valor'] == 'music':
                gerenciador_audio.definir_volume_musica(percentual)

            # Atualizar volumes locais
            self.volumes = gerenciador_audio.obter_volumes()

            # Som de feedback apenas se não estiver arrastando
            if not self.mouse_pressed or not self.dragging_slider:
                gerenciador_audio.tocar_som('ui_select')

    def update(self, dt):
        """Atualizar menu (placeholder para consistência)"""
        # Parâmetro dt mantido para consistência da interface, mas não usado
        _ = dt  # Indica que o parâmetro é intencionalmente não utilizado

        # Atualizar volumes locais caso tenham sido alterados externamente
        self.volumes = gerenciador_audio.obter_volumes()

    def _ajustar_volume(self, tipo_volume, delta):
        """Ajustar volume de um tipo específico"""
        volume_atual = self.volumes[tipo_volume]
        novo_volume = max(0.0, min(1.0, volume_atual + delta))

        if tipo_volume == 'master':
            gerenciador_audio.definir_volume_master(novo_volume)
        elif tipo_volume == 'sfx':
            gerenciador_audio.definir_volume_sfx(novo_volume)
        elif tipo_volume == 'music':
            gerenciador_audio.definir_volume_musica(novo_volume)

        # Atualizar valores locais
        self.volumes = gerenciador_audio.obter_volumes()

    def _executar_acao(self, acao):
        """Executar ação do botão"""
        if acao == 'test_sound':
            # Tocar sons de teste
            gerenciador_audio.tocar_som('tiro_shelly')
            return None
        elif acao == 'back':
            return 'voltar'

        return None

    def _verificar_clique_mouse(self):
        """Verificar clique do mouse nas opções"""
        for i, opcao in enumerate(self.opcoes):
            if opcao['rect'] and opcao['rect'].collidepoint(self.mouse_pos):
                self.opcao_selecionada = i
                gerenciador_audio.tocar_som('ui_confirm')
                if opcao['tipo'] == 'botao':
                    return self._executar_acao(opcao['acao'])
                break

    def render(self):
        """Renderizar menu de áudio"""
        self.screen.fill(COR_FUNDO)

        # Título centralizado e ajustado para resolução
        titulo = self.font_titulo.render("Configurações de Áudio", True, COR_UI)
        titulo_rect = titulo.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(titulo, titulo_rect)

        # Instruções centralizadas
        instrucoes = [
            "Use as setas para navegar",
            "← → para ajustar volumes",
            "ENTER para selecionar",
            "ESC para voltar"
        ]

        y_instrucao = 140
        for instrucao in instrucoes:
            texto = self.font_valor.render(instrucao, True, COR_UI)
            texto_rect = texto.get_rect(center=(SCREEN_WIDTH // 2, y_instrucao))
            self.screen.blit(texto, texto_rect)
            y_instrucao += 25

        # Opções centralizadas com espaçamento adequado
        y_opcao = 250
        for i, opcao in enumerate(self.opcoes):
            cor = (255, 255, 0) if i == self.opcao_selecionada else COR_UI

            if opcao['tipo'] == 'slider':
                # Renderizar slider de volume
                nome = self.font_opcao.render(opcao['nome'], True, cor)
                nome_rect = nome.get_rect(center=(SCREEN_WIDTH // 2 - 200, y_opcao))
                self.screen.blit(nome, nome_rect)

                # Barra de volume
                volume = self.volumes[opcao['valor']]
                self._desenhar_barra_volume(SCREEN_WIDTH // 2 - 75, y_opcao - 10, volume, cor)

                # Valor numérico
                valor_texto = f"{int(volume * 100)}%"
                valor = self.font_valor.render(valor_texto, True, cor)
                valor_rect = valor.get_rect(center=(SCREEN_WIDTH // 2 + 150, y_opcao))
                self.screen.blit(valor, valor_rect)

            else:
                # Renderizar botão
                texto = self.font_opcao.render(opcao['nome'], True, cor)
                texto_rect = texto.get_rect(center=(SCREEN_WIDTH // 2, y_opcao))
                self.screen.blit(texto, texto_rect)

            # Atualizar retângulo da opção para detecção de clique
            self.opcoes[i]['rect'] = pygame.Rect(SCREEN_WIDTH // 2 - 250, y_opcao - 20, 500, 40)

            y_opcao += 80

    def _desenhar_barra_volume(self, x, y, volume, cor):
        """Desenhar barra de volume ajustada para resolução 1280x720"""
        largura_total = 150  # Tamanho adequado para HD
        altura = 25          # Altura adequada

        # Fundo da barra
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, largura_total, altura))

        # Barra de volume preenchida
        largura_preenchida = int(largura_total * volume)
        if largura_preenchida > 0:
            pygame.draw.rect(self.screen, cor, (x, y, largura_preenchida, altura))

        # Borda
        pygame.draw.rect(self.screen, COR_UI, (x, y, largura_total, altura), 2)

    def draw(self):
        """Desenhar menu de configurações ajustado para resolução 1280x720"""
        # Fundo
        self.screen.fill((30, 30, 60))

        # Título centralizado
        titulo = self.font_titulo.render("CONFIGURAÇÕES DE ÁUDIO", True, self.cor_texto)
        titulo_rect = titulo.get_rect(center=(self.screen.get_width() // 2, 80))
        self.screen.blit(titulo, titulo_rect)

        # Desenhar opções centralizadas
        y_inicial = 200
        espaco_opcoes = 80  # Espaçamento adequado para HD

        for i, opcao in enumerate(self.opcoes):
            y_pos = y_inicial + i * espaco_opcoes
            cor = self.cor_selecionado if i == self.opcao_selecionada else self.cor_texto

            # Nome da opção centralizado à esquerda
            texto_opcao = self.font_opcao.render(opcao['nome'], True, cor)
            texto_rect = texto_opcao.get_rect(center=(self.screen.get_width() // 2 - 150, y_pos))
            self.screen.blit(texto_opcao, texto_rect)

            # Atualizar rect da opção para detecção de mouse
            opcao['rect'] = pygame.Rect(self.screen.get_width() // 2 - 300, y_pos - 25, 600, 50)

            if opcao['tipo'] == 'slider':
                # Desenhar slider centralizado
                self._desenhar_slider(opcao, self.screen.get_width() // 2 - 50, y_pos)
            elif opcao['tipo'] == 'botao':
                # Desenhar botão centralizado
                self._desenhar_botao(opcao, self.screen.get_width() // 2 + 100, y_pos, cor)

        # Instruções centralizadas na parte inferior
        instrucoes = [
            "Use as setas ← → ou clique para ajustar",
            "Enter ou clique para confirmar",
            "ESC para voltar"
        ]

        y_instrucoes = 600
        for instrucao in instrucoes:
            texto = self.font_valor.render(instrucao, True, (200, 200, 200))
            texto_rect = texto.get_rect(center=(self.screen.get_width() // 2, y_instrucoes))
            self.screen.blit(texto, texto_rect)
            y_instrucoes += 30

    def _desenhar_slider(self, opcao, x, y):
        """Desenhar slider de volume ajustado para resolução 1280x720"""
        largura_slider = 200  # Tamanho adequado para HD
        altura_slider = 25    # Altura adequada

        # Fundo do slider
        slider_rect = pygame.Rect(x, y - altura_slider // 2, largura_slider, altura_slider)
        opcao['slider_rect'] = slider_rect  # Armazenar para detecção de mouse

        pygame.draw.rect(self.screen, self.cor_slider, slider_rect)

        # Preenchimento do slider
        valor_atual = self.volumes[opcao['valor']]
        largura_preenchimento = int(largura_slider * valor_atual)
        if largura_preenchimento > 0:
            preenchimento_rect = pygame.Rect(x, y - altura_slider // 2,
            largura_preenchimento, altura_slider)
            pygame.draw.rect(self.screen, self.cor_slider_preenchido, preenchimento_rect)

        # Borda do slider
        cor_borda = self.cor_selecionado if self.dragging_slider == opcao else self.cor_texto
        pygame.draw.rect(self.screen, cor_borda, slider_rect, 2)

        # Indicador de posição (handle)
        handle_x = x + int(largura_slider * valor_atual)
        handle_y = y
        handle_radius = altura_slider // 2 + 2
        pygame.draw.circle(self.screen, cor_borda, (handle_x, handle_y), handle_radius)
        pygame.draw.circle(self.screen, (255, 255, 255), (handle_x, handle_y), handle_radius - 2)

        # Valor como texto
        texto_valor = f"{int(valor_atual * 100)}%"
        texto = self.font_valor.render(texto_valor, True, self.cor_texto)
        texto_rect = texto.get_rect(center=(x + largura_slider + 50, y))
        self.screen.blit(texto, texto_rect)

    def _desenhar_botao(self, opcao, x, y, cor):
        """Desenhar botão ajustado para resolução 1280x720"""
        largura_botao = 150  # Tamanho adequado para HD
        altura_botao = 35    # Altura adequada

        # Fundo do botão
        botao_rect = pygame.Rect(x - largura_botao // 2, y - altura_botao // 2, largura_botao, altura_botao)
        cor_botao = (100, 100, 100) if cor == self.cor_texto else (150, 150, 0)
        pygame.draw.rect(self.screen, cor_botao, botao_rect)
        pygame.draw.rect(self.screen, cor, botao_rect, 2)

        # Texto do botão
        texto_botao = "Clique aqui" if opcao['acao'] == 'test_sound' else opcao['nome']
        texto = self.font_valor.render(texto_botao, True, cor)  # Usando font_valor para botões
        texto_rect = texto.get_rect(center=botao_rect.center)
        self.screen.blit(texto, texto_rect)
