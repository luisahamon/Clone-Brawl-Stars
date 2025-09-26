"""
Gerenciador de Estados do Brawl Stars Clone.
Este módulo implementa um sistema de estados para controlar diferentes telas
do jogo (menu principal, jogo, configurações, etc.) e transições suaves entre elas.
"""

import inspect
import pygame
from src.menu_principal import MenuPrincipal
from src.game import Game
from src.menu_audio import MenuAudio
from src.menu_conquistas import MenuConquistas
from src.menu_progressao import menu_progressao, menu_detalhes
from src.audio_manager import gerenciador_audio

class EstadoJogo:
    """Estados possíveis do jogo"""
    MENU_PRINCIPAL = "menu_principal"
    JOGO = "jogo"
    CONFIGURACOES = "configuracoes"
    CONQUISTAS = "conquistas"
    PROGRESSAO = "progressao"
    DETALHES_BRAWLER = "detalhes_brawler"
    PAUSADO = "pausado"
    GAME_OVER = "game_over"


class GerenciadorEstados:
    """Gerenciador de estados do jogo"""
    def __init__(self, screen):
        self.screen = screen
        self.estado_atual = EstadoJogo.MENU_PRINCIPAL
        self.estados = {}
        self.transicao_ativa = False
        self.tempo_transicao = 0.0
        self.duracao_transicao = 0.5
        self.brawler_detalhes = None  # Para armazenar qual brawler está sendo visualizado        # Inicializar estados
        self.inicializar_estados()

    def inicializar_estados(self):
        """Inicializar todos os estados do jogo"""
        # Criar um jogo temporário para acessar o sistema de conquistas
        jogo_temp = Game(self.screen)
        self.estados[EstadoJogo.MENU_PRINCIPAL] = MenuPrincipal(self.screen, jogo_temp)
        self.estados[EstadoJogo.JOGO] = None  # Será criado quando necessário
        self.estados[EstadoJogo.CONFIGURACOES] = MenuAudio(self.screen)
        self.estados[EstadoJogo.CONQUISTAS] = MenuConquistas(self.screen, jogo_temp.sistema_conquistas)
        self.estados[EstadoJogo.PROGRESSAO] = menu_progressao
        self.estados[EstadoJogo.DETALHES_BRAWLER] = menu_detalhes

    def mudar_estado(self, novo_estado):
        """Mudar para um novo estado"""
        if novo_estado == self.estado_atual:
            return

        # Efeitos de saída do estado atual
        if self.estado_atual == EstadoJogo.MENU_PRINCIPAL:
            gerenciador_audio.parar_musica()
        elif self.estado_atual == EstadoJogo.JOGO:
            # Pausar música do jogo se houver
            pass

        # Criar novo estado se necessário
        if novo_estado == EstadoJogo.JOGO and self.estados[EstadoJogo.JOGO] is None:
            self.estados[EstadoJogo.JOGO] = Game(self.screen)
        elif novo_estado == EstadoJogo.JOGO and self.estados[EstadoJogo.JOGO] is not None:
            # Reiniciar jogo existente
            self.estados[EstadoJogo.JOGO] = Game(self.screen) # Efeitos de entrada do novo estado
        if novo_estado == EstadoJogo.MENU_PRINCIPAL:
            # Som ambiente sutil para menu
            if gerenciador_audio.som_disponivel('ambiente_menu'):
                gerenciador_audio.tocar_som('ambiente_menu', volume=0.1)
        elif novo_estado == EstadoJogo.JOGO:
            # Parar todos os sons ao iniciar jogo
            gerenciador_audio.parar_todos_sons()
            gerenciador_audio.parar_musica()

        # Mudar estado
        self.estado_atual = novo_estado
        self.iniciar_transicao()

    def iniciar_transicao(self):
        """Iniciar efeito de transição"""
        self.transicao_ativa = True
        self.tempo_transicao = 0.0

    def update(self, dt):
        """Atualizar estado atual"""
        # Atualizar transição
        if self.transicao_ativa:
            self.tempo_transicao += dt
            if self.tempo_transicao >= self.duracao_transicao:
                self.transicao_ativa = False        # Atualizar estado atual
        estado = self.estados.get(self.estado_atual)
        if estado:
            if hasattr(estado, 'update'):
                estado.update(dt)

    def handle_event(self, event):
        """Processar eventos do estado atual"""
        estado = self.estados.get(self.estado_atual)
        if not estado:
            return True

        # Menu principal
        if self.estado_atual == EstadoJogo.MENU_PRINCIPAL:
            acao = estado.handle_event(event)
            if acao:
                if acao == "jogar":
                    self.mudar_estado(EstadoJogo.JOGO)
                elif acao == "configuracoes":
                    self.mudar_estado(EstadoJogo.CONFIGURACOES)
                elif acao == "conquistas":
                    self.mudar_estado(EstadoJogo.CONQUISTAS)
                elif acao == "progressao":
                    self.mudar_estado(EstadoJogo.PROGRESSAO)
                elif acao == "sair":
                    pygame.display.quit()
                    exit()

        # Jogo
        elif self.estado_atual == EstadoJogo.JOGO:
            continuar = estado.handle_game_event(event)
            if not continuar:
                self.mudar_estado(EstadoJogo.MENU_PRINCIPAL)

        # Menu de configurações
        elif self.estado_atual == EstadoJogo.CONFIGURACOES:
            resultado = estado.handle_event(event)
            if resultado == "voltar":
                self.mudar_estado(EstadoJogo.MENU_PRINCIPAL)

        # Menu de conquistas
        elif self.estado_atual == EstadoJogo.CONQUISTAS:
            resultado = estado.handle_event(event)
            if resultado == "voltar":
                self.mudar_estado(EstadoJogo.MENU_PRINCIPAL)

        # Menu de progressão
        elif self.estado_atual == EstadoJogo.PROGRESSAO:
            resultado = estado.processar_evento(event)
            if resultado == "voltar":
                self.mudar_estado(EstadoJogo.MENU_PRINCIPAL)
            elif resultado == "detalhes":
                self.brawler_detalhes = estado.brawler_selecionado
                self.mudar_estado(EstadoJogo.DETALHES_BRAWLER)

        # Detalhes do Brawler
        elif self.estado_atual == EstadoJogo.DETALHES_BRAWLER:
            resultado = estado.processar_evento(event, self.brawler_detalhes)
            if resultado == "voltar":
                self.mudar_estado(EstadoJogo.PROGRESSAO)

        return True

    def render(self):
        """Renderizar estado atual"""
        estado = self.estados.get(self.estado_atual)
        if estado:
            # Estados especiais de progressão
            if self.estado_atual == EstadoJogo.PROGRESSAO:
                from src.characters.personagens import PERSONAGENS_DISPONIVEIS
                estado.desenhar(self.screen, PERSONAGENS_DISPONIVEIS)
            elif self.estado_atual == EstadoJogo.DETALHES_BRAWLER:
                estado.desenhar(self.screen, self.brawler_detalhes)
            elif hasattr(estado, 'draw'):
                # Verificar se o método draw aceita parâmetros
                sig = inspect.signature(estado.draw)
                if len(sig.parameters) > 0:
                    estado.draw(self.screen)
                else:
                    estado.draw()
            elif hasattr(estado, 'render'):
                estado.render()

        # Efeito de transição
        if self.transicao_ativa:
            self.desenhar_transicao()

    def desenhar_transicao(self):
        """Desenhar efeito de transição"""
        # Fade in/out simples
        progresso = self.tempo_transicao / self.duracao_transicao

        if progresso < 0.5:
            # Fade out (escurecendo)
            alpha = int(255 * (progresso * 2))
        else:
            # Fade in (clareando)
            alpha = int(255 * (2 - progresso * 2))

        if alpha > 0:
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(alpha)
            self.screen.blit(overlay, (0, 0))

    def get_estado_atual(self):
        """Obter estado atual"""
        return self.estado_atual
