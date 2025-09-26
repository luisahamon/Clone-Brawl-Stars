"""
Sistema de interface do usuário (UI) do Brawl Stars Clone.
Este módulo gerencia toda a interface gráfica do jogo, incluindo HUD durante
o gameplay (barra de vida, pontuação, nível), tela de game over, informações
de power-ups ativos e elementos visuais da interface.
"""

import math
import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COR_UI, GEMAS_PARA_VITORIA,
    COR_GEMA, TEMPO_RESPAWN, TEMPO_COUNTDOWN_VITORIA, COR_COUNTDOWN_VITORIA
)
from src.pygame_constants import MOUSEBUTTONDOWN, SRCALPHA

MOUSEBUTTONUP = 1026  # pygame.MOUSEBUTTONUP
MOUSEMOTION = 1024   # pygame.MOUSEMOTION

class UI:
    """Classe da interface do usuário"""
    def __init__(self):
        self.font_grande = pygame.font.Font(None, 36)
        self.font_media = pygame.font.Font(None, 24)
        self.font_pequena = pygame.font.Font(None, 18)

        # Controles touch/mobile
        self.joystick_ativo = False
        self.joystick_centro = (100, SCREEN_HEIGHT - 120)
        self.joystick_raio = 50
        self.joystick_knob_pos = self.joystick_centro
        self.joystick_pressionado = False

        self.botao_ataque_pos = (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 120)
        self.botao_ataque_raio = 40
        self.botao_ataque_pressionado = False
        self.notificacoes = []

    def desenhar(self, screen, jogador, pontuacao, jogo_ativo, estado="jogando",
                 info_nivel=None, gemas_coletadas=0, jogador_morto=False,
                 tempo_respawn=0.0, vitoria_countdown_ativo=False,
                 tempo_vitoria_restante=0.0):
        """Desenhar elementos da UI"""
        if estado == "jogando" and jogo_ativo:
            self.desenhar_hud(screen, jogador, pontuacao, info_nivel,
                            gemas_coletadas, jogador_morto, tempo_respawn,
                            vitoria_countdown_ativo, tempo_vitoria_restante)
        elif estado == "game_over" or not jogo_ativo:
            self.desenhar_game_over(screen, pontuacao, info_nivel, gemas_coletadas)
        elif estado == "vitoria":
            self.desenhar_vitoria(screen, pontuacao, info_nivel, gemas_coletadas)

    def desenhar_hud(self, screen, jogador, pontuacao, info_nivel=None,
                     gemas_coletadas=0, jogador_morto=False, tempo_respawn=0.0,
                     vitoria_countdown_ativo=False, tempo_vitoria_restante=0.0):
        """Desenhar HUD durante o jogo"""
        # Minimap no canto superior direito
        self.desenhar_minimap_melhorado(screen, jogador)

        # Contador de gemas grande e visível (centralizado no topo)
        self.desenhar_contador_gemas_melhorado(screen, gemas_coletadas)

        # Barra de vida colorida (parte inferior esquerda)
        self.desenhar_barra_vida_melhorada(screen, jogador)

        # Pontuação e nível
        texto_pontuacao = self.font_media.render(f"Pontuação: {pontuacao}", True, COR_UI)
        screen.blit(texto_pontuacao, (10, SCREEN_HEIGHT - 90))

        # Informações do nível
        if info_nivel:
            self.desenhar_info_nivel_compacta(screen, info_nivel)

        # Power-ups ativos
        self.desenhar_power_ups_ativos_melhorados(screen, jogador)

        # Botão de Super brilhante com barra de carga (canto inferior direito)
        self.desenhar_botao_super_melhorado(screen, jogador)

        # Controles touch/mobile
        self.desenhar_joystick_virtual(screen)
        self.desenhar_botao_ataque(screen)

        # Instruções compactas
        instrucoes = ["WASD: Mover", "Mouse: Mirar", "Q: Super", "Colete gemas!"]
        for i, instrucao in enumerate(instrucoes):
            texto = self.font_pequena.render(instrucao, True, COR_UI)
            screen.blit(texto, (SCREEN_WIDTH - 150, 120 + i * 15))

        # Indicador de respawn
        if jogador_morto and tempo_respawn > 0:
            self.desenhar_indicador_respawn(screen, tempo_respawn)

        # Indicador de countdown de vitória
        if vitoria_countdown_ativo and tempo_vitoria_restante > 0:
            self.desenhar_countdown_vitoria(screen, tempo_vitoria_restante)

        # Atualizar notificações
        self.atualizar_notificacoes(screen)

    def desenhar_barra_vida(self, screen, jogador):
        """Desenhar barra de vida do jogador (lado esquerdo)"""
        barra_width = 200
        barra_height = 20
        x = 10
        y = 60  # Movido para baixo para dar espaço ao contador do topo

        # Fundo da barra
        pygame.draw.rect(screen, (100, 0, 0), (x, y, barra_width, barra_height))        # Vida atual
        vida_percent = jogador.vida / jogador.vida_maxima
        vida_width = int(vida_percent * barra_width)

        # Cor da barra baseada na vida
        if vida_percent > 0.6:
            cor_vida = (0, 255, 0)  # Verde
        elif vida_percent > 0.3:
            cor_vida = (255, 255, 0)  # Amarelo
        else:
            cor_vida = (255, 0, 0)  # Vermelho

        pygame.draw.rect(screen, cor_vida, (x, y, vida_width, barra_height))        # Borda
        pygame.draw.rect(screen, COR_UI, (x, y, barra_width, barra_height), 2)

        # Texto da vida
        texto_vida = self.font_pequena.render(f"{int(jogador.vida)}/{int(jogador.vida_maxima)}",
                                              True, COR_UI)
        screen.blit(texto_vida, (x + barra_width + 10, y + 2))

    def desenhar_info_nivel(self, screen, info_nivel):
        """Desenhar informações do nível atual"""
        if not info_nivel:
            return

        # Posição da informação do nível (ajustada)
        x = 10
        y = 115  # Ajustado para dar espaço à pontuação        # Nível atual
        texto_nivel = self.font_media.render(f"Nível: {info_nivel['nivel']}", True, COR_UI)
        screen.blit(texto_nivel, (x, y))

        # Barra de progresso para o próximo nível
        if info_nivel['nivel'] < 20:  # Se não chegou no nível máximo
            barra_width = 200
            barra_height = 10
            progresso_x = x
            progresso_y = y + 25

            # Fundo da barra de progresso
            pygame.draw.rect(screen, (50, 50, 50),
                           (progresso_x, progresso_y, barra_width, barra_height))

            # Progresso atual
            progresso_width = int(info_nivel['progresso'] * barra_width)
            pygame.draw.rect(screen, (0, 255, 255),
                           (progresso_x, progresso_y, progresso_width, barra_height))

            # Borda
            pygame.draw.rect(screen, COR_UI,
                           (progresso_x, progresso_y, barra_width, barra_height), 1)

            # Texto do progresso
            texto_progresso = self.font_pequena.render(
                f"{info_nivel['pontuacao_atual']}/{info_nivel['pontuacao_proximo_nivel']}",
                True, COR_UI
            )
            screen.blit(texto_progresso, (progresso_x + barra_width + 10, progresso_y - 2))
        else:
            # Nível máximo alcançado
            texto_max = self.font_pequena.render("NÍVEL MÁXIMO!", True, (255, 215, 0))
            screen.blit(texto_max, (x, y + 25))

        # Informações adicionais do nível
        info_adicional = [
            f"Velocidade inimigos: {info_nivel['velocidade_inimigos']:.0f}",
            f"Quantidade inimigos: {info_nivel['quantidade_inimigos']}"
        ]

        for i, info in enumerate(info_adicional):
            texto = self.font_pequena.render(info, True, COR_UI)
            screen.blit(texto, (x, y + 45 + i * 15))

    def desenhar_power_ups_ativos(self, screen, jogador):
        """Desenhar power-ups ativos"""
        y_offset = 80

        for i, power_up in enumerate(jogador.power_ups_ativos):
            # Escolher cor e nome baseado no tipo
            cor = (255, 255, 255)  # Cor padrão
            nome = "Desconhecido"  # Nome padrão

            if power_up['tipo'] == 'velocidade':
                cor = (0, 255, 255)
                nome = "Velocidade"
            elif power_up['tipo'] == 'vida':
                cor = (0, 255, 0)
                nome = "Vida"
            elif power_up['tipo'] == 'tiro_rapido':
                cor = (255, 165, 0)
                nome = "Tiro Rápido"

            # Desenhar indicador
            pygame.draw.circle(screen, cor, (20, y_offset + i * 30), 8)

            # Texto do power-up
            tempo_restante = int(power_up['tempo_restante'])
            texto = self.font_pequena.render(f"{nome}: {tempo_restante}s", True, COR_UI)
            screen.blit(texto, (35, y_offset + i * 30 - 8))

    def desenhar_habilidade_especial(self, screen, jogador):
        """Desenhar indicador da habilidade especial"""
        if not hasattr(jogador, 'obter_info_habilidade'):
            return

        info = jogador.obter_info_habilidade()
        x = SCREEN_WIDTH - 280
        y = 80

        # Fundo do indicador (maior para mais informações)
        rect_fundo = pygame.Rect(x, y, 260, 85)
        pygame.draw.rect(screen, (40, 40, 60), rect_fundo)
        pygame.draw.rect(screen, (200, 200, 200), rect_fundo, 2)

        # Título com nome da habilidade
        titulo = self.font_media.render(f"{info['nome']} (Q)", True, COR_UI)
        screen.blit(titulo, (x + 10, y + 5))

        # Descrição da habilidade (primeira linha)
        if info.get('descricao'):
            descricao_palavras = info['descricao'].split()
            if len(descricao_palavras) > 8:
                descricao_linha1 = ' '.join(descricao_palavras[:8])
                descricao_linha2 = ' '.join(descricao_palavras[8:16])
            else:
                descricao_linha1 = info['descricao']
                descricao_linha2 = ""

            desc1 = self.font_pequena.render(descricao_linha1, True, (200, 200, 200))
            screen.blit(desc1, (x + 10, y + 25))

            if descricao_linha2:
                desc2 = self.font_pequena.render(descricao_linha2, True, (200, 200, 200))
                screen.blit(desc2, (x + 10, y + 38))

        # Status da habilidade
        if info['pronta']:
            status_texto = "PRONTA!"
            cor_status = (0, 255, 0)
            # Efeito de brilho quando pronta
            pygame.draw.rect(screen, (0, 255, 0, 50), rect_fundo)
        else:
            tempo_restante = info['cooldown_atual']
            status_texto = f"Cooldown: {tempo_restante:.1f}s"
            cor_status = (255, 100, 100)

        status = self.font_pequena.render(status_texto, True, cor_status)
        screen.blit(status, (x + 10, y + 53))        # Barra de cooldown
        if not info['pronta']:
            barra_largura = 240
            barra_altura = 8
            progresso = 1.0 - (info['cooldown_atual'] / info['cooldown_max']) if info['cooldown_max'] > 0 else 1.0

            # Fundo da barra
            pygame.draw.rect(screen, (60, 60, 60), (x + 10, y + 70, barra_largura, barra_altura))

            # Progresso com gradiente de cor
            largura_progresso = int(barra_largura * progresso)

            if progresso < 0.3:
                cor_progresso = (255, 0, 0)  # Vermelho
            elif progresso < 0.7:
                cor_progresso = (255, 255, 0)  # Amarelo
            else:
                cor_progresso = (0, 255, 0)  # Verde

            pygame.draw.rect(screen, cor_progresso, (x+10, y+70, largura_progresso, barra_altura))

    def desenhar_game_over(self, screen, pontuacao, info_nivel=None,
                          gemas_coletadas=0):
        """Desenhar tela de game over"""
        # Fundo semi-transparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Texto de Game Over
        texto_game_over = self.font_grande.render("GAME OVER", True, (255, 0, 0))
        rect_game_over = texto_game_over.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
        screen.blit(texto_game_over, rect_game_over)

        # Informações do nível alcançado
        if info_nivel:
            texto_nivel = self.font_media.render(f"Nível Alcançado: {info_nivel['nivel']}", True, (255, 215, 0))
            rect_nivel = texto_nivel.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
            screen.blit(texto_nivel, rect_nivel)

        # Pontuação final
        texto_pontuacao = self.font_media.render(f"Pontuação Final: {pontuacao}", True, COR_UI)
        rect_pontuacao = texto_pontuacao.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(texto_pontuacao, rect_pontuacao)

        # Gemas coletadas
        texto_gemas = self.font_media.render(f"Gemas Coletadas: {gemas_coletadas}/{GEMAS_PARA_VITORIA}", True, COR_GEMA)
        rect_gemas = texto_gemas.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        screen.blit(texto_gemas, rect_gemas)
        # Estatísticas adicionais
        if info_nivel:
            stats = [
                f"Velocidade dos inimigos: {info_nivel['velocidade_inimigos']:.0f}",
                f"Quantidade de inimigos: {info_nivel['quantidade_inimigos']}"
            ]
            for i, stat in enumerate(stats):
                texto_stat = self.font_pequena.render(stat, True, COR_UI)
                rect_stat = texto_stat.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60 + i * 20))
                screen.blit(texto_stat, rect_stat)

        # Instruções para reiniciar
        texto_reiniciar = self.font_pequena.render("Pressione R para reiniciar ou ESC para sair", True, COR_UI)
        rect_reiniciar = texto_reiniciar.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 120))
        screen.blit(texto_reiniciar, rect_reiniciar)

    def desenhar_indicador_respawn(self, screen, tempo_respawn):
        """Desenhar indicador de respawn no centro da tela"""
        # Fundo semi-transparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Texto principal
        texto_principal = self.font_grande.render("RESPAWN", True, (255, 255, 255))
        rect_principal = texto_principal.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(texto_principal, rect_principal)

        # Contador de tempo
        tempo_int = int(tempo_respawn) + 1
        texto_tempo = self.font_grande.render(str(tempo_int), True, (255, 255, 0))
        rect_tempo = texto_tempo.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(texto_tempo, rect_tempo)

        # Barra de progresso
        barra_width = 200
        barra_height = 20
        barra_x = SCREEN_WIDTH // 2 - barra_width // 2
        barra_y = SCREEN_HEIGHT // 2 + 40

        # Fundo da barra
        pygame.draw.rect(screen, (100, 100, 100), (barra_x, barra_y, barra_width, barra_height))

        # Progresso (invertido - diminui com o tempo)
        progresso = 1.0 - (tempo_respawn / TEMPO_RESPAWN)
        progresso_width = int(barra_width * progresso)
        pygame.draw.rect(screen, (0, 255, 0), (barra_x, barra_y, progresso_width, barra_height))

        # Borda
        pygame.draw.rect(screen, (255, 255, 255), (barra_x, barra_y, barra_width, barra_height), 2)

    def desenhar_countdown_vitoria(self, screen, tempo_vitoria_restante):
        """Desenhar indicador de countdown de vitória"""
        # Fundo semi-transparente dourado
        overlay = pygame.Surface((SCREEN_WIDTH, 120))
        overlay.set_alpha(180)
        overlay.fill(COR_COUNTDOWN_VITORIA)
        screen.blit(overlay, (0, SCREEN_HEIGHT // 2 - 60))

        # Texto principal
        texto_principal = self.font_grande.render("🏆 VITÓRIA EM...", True, (255, 255, 255))
        rect_principal = texto_principal.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
        screen.blit(texto_principal, rect_principal)

        # Contador de tempo
        tempo_int = int(tempo_vitoria_restante) + 1
        texto_tempo = self.font_grande.render(str(tempo_int), True, (255, 255, 255))
        rect_tempo = texto_tempo.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(texto_tempo, rect_tempo)

        # Barra de progresso
        barra_width = 300
        barra_height = 15
        barra_x = SCREEN_WIDTH // 2 - barra_width // 2
        barra_y = SCREEN_HEIGHT // 2 + 50

        # Fundo da barra
        pygame.draw.rect(screen, (100, 100, 100), (barra_x, barra_y, barra_width, barra_height))

        # Progresso
        progresso = tempo_vitoria_restante / TEMPO_COUNTDOWN_VITORIA
        progresso_width = int(barra_width * progresso)
        pygame.draw.rect(screen, COR_COUNTDOWN_VITORIA,
        (barra_x, barra_y, progresso_width, barra_height))

        # Borda
        pygame.draw.rect(screen, (255, 255, 255), (barra_x, barra_y, barra_width, barra_height), 2)

    def desenhar_vitoria(self, screen, pontuacao, info_nivel=None,
                        gemas_coletadas=0):
        """Desenhar tela de vitória"""
        # Fundo escuro semi-transparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Título principal
        texto_vitoria = self.font_grande.render("🏆 VITÓRIA! 🏆", True, COR_COUNTDOWN_VITORIA)
        rect_vitoria = texto_vitoria.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(texto_vitoria, rect_vitoria)        # Estatísticas
        estatisticas = [
            f"Pontuação Final: {pontuacao}",
            f"Gemas Coletadas: {gemas_coletadas}",
            f"Objetivo Alcançado: {GEMAS_PARA_VITORIA} gemas!"
        ]
        if info_nivel:
            estatisticas.append(f"Nível Alcançado: {info_nivel.get('nivel', 1)}")

        for i, stat in enumerate(estatisticas):
            texto_stat = self.font_media.render(stat, True, (255, 255, 255))
            rect_stat = texto_stat.get_rect(center=(SCREEN_WIDTH // 2,
                                                   SCREEN_HEIGHT // 2 - 20 + i * 40))
            screen.blit(texto_stat, rect_stat)        # Instruções
        instrucoes = [
            "Pressione R para jogar novamente",
            "Pressione ESC para voltar ao menu"
        ]
        for i, instrucao in enumerate(instrucoes):
            texto_instrucao = self.font_media.render(instrucao, True, (200, 200, 200))
            rect_instrucao = texto_instrucao.get_rect(center=(SCREEN_WIDTH // 2,
                                                             SCREEN_HEIGHT // 2 + 120 + i * 30))
            screen.blit(texto_instrucao, rect_instrucao)

    def desenhar_contador_topo(self, screen, jogador, gemas_coletadas):
        """Desenhar contador de gemas e vida no topo da tela (estilo Brawl Stars)"""
        # Posição centralizada no topo
        centro_x = SCREEN_WIDTH // 2
        y = 10

        # Fundo do contador (retângulo arredondado)
        contador_width = 200
        contador_height = 35
        contador_x = centro_x - contador_width // 2
        contador_rect = pygame.Rect(contador_x, y, contador_width, contador_height)

        # Fundo escuro com transparência
        superficie_fundo = pygame.Surface((contador_width, contador_height))
        superficie_fundo.set_alpha(180)
        superficie_fundo.fill((20, 20, 40))
        screen.blit(superficie_fundo, (contador_x, y))

        # Borda dourada
        pygame.draw.rect(screen, (255, 215, 0), contador_rect, 2)        # Ícone e contador de gemas (lado esquerdo)
        gemas_x = contador_x + 15
        texto_gemas = self.font_media.render(f"💎 {gemas_coletadas}/{GEMAS_PARA_VITORIA}",
                                           True, COR_GEMA)
        screen.blit(texto_gemas, (gemas_x, y + 8))

        # Separador vertical
        sep_x = centro_x - 5
        pygame.draw.line(screen, (100, 100, 100), (sep_x, y + 5),
                        (sep_x, y + contador_height - 5), 1)
        # Ícone e contador de vida (lado direito)
        vida_x = centro_x + 10
        vida_percentual = int((jogador.vida / jogador.vida_maxima) * 100)
        cor_vida = (0, 255, 0) if vida_percentual > 60 else (
            (255, 255, 0) if vida_percentual > 30 else (255, 0, 0)
        )
        texto_vida = self.font_media.render(f"❤️ {vida_percentual}%", True, cor_vida)
        screen.blit(texto_vida, (vida_x, y + 8))

    def desenhar_botao_super(self, screen, jogador):
        """Desenhar botão de Super com barra de carga (estilo Brawl Stars)"""
        if not hasattr(jogador, 'obter_info_habilidade'):
            return

        info = jogador.obter_info_habilidade()

        # Posição no canto inferior direito
        botao_size = 80
        margin = 20
        botao_x = SCREEN_WIDTH - botao_size - margin
        botao_y = SCREEN_HEIGHT - botao_size - margin

        # Círculo principal do botão
        centro_botao = (botao_x + botao_size // 2, botao_y + botao_size // 2)
        raio_botao = botao_size // 2

        # Cor do botão baseada no status
        if info['pronta']:
            cor_botao = (255, 215, 0)  # Dourado quando pronto
            cor_borda = (255, 255, 255)  # Branco brilhante
            alpha_brilho = 150
        else:
            cor_botao = (60, 60, 80)  # Cinza escuro quando em cooldown
            cor_borda = (100, 100, 120)
            alpha_brilho = 80

        # Desenhar círculo de fundo
        pygame.draw.circle(screen, cor_botao, centro_botao, raio_botao)
        pygame.draw.circle(screen, cor_borda, centro_botao, raio_botao, 3)

        # Efeito de brilho quando pronta
        if info['pronta']:
            superficie_brilho = pygame.Surface((botao_size * 2, botao_size * 2))
            superficie_brilho.set_alpha(alpha_brilho)
            pygame.draw.circle(superficie_brilho, (255, 255, 0),
            (botao_size, botao_size), raio_botao + 10)
            screen.blit(superficie_brilho, (botao_x - botao_size // 2, botao_y - botao_size // 2))

        # Texto "SUPER" ou "Q" no centro
        if info['pronta']:
            texto_super = self.font_media.render("SUPER", True, (0, 0, 0))
            texto_rect = texto_super.get_rect(center=centro_botao)
            screen.blit(texto_super, texto_rect)
        else:
            texto_q = self.font_grande.render("Q", True, cor_borda)
            texto_rect = texto_q.get_rect(center=centro_botao)
            screen.blit(texto_q, texto_rect)

        # Barra de carga circular (apenas quando em cooldown)
        if not info['pronta'] and info['cooldown_max'] > 0:
            progresso = 1.0 - (info['cooldown_atual'] / info['cooldown_max'])
            self.desenhar_barra_circular(screen, centro_botao, raio_botao + 5,
                                       progresso, (0, 255, 255), 4)
        # Texto do cooldown abaixo do botão
        if not info['pronta']:
            tempo_restante = info['cooldown_atual']
            texto_cooldown = self.font_pequena.render(f"{tempo_restante:.1f}s",
                                                     True, (255, 255, 255))
            texto_rect = texto_cooldown.get_rect(center=(centro_botao[0],
                                                        botao_y + botao_size + 15))
            screen.blit(texto_cooldown, texto_rect)

    def desenhar_barra_circular(self, screen, centro, raio, progresso, cor, espessura):
        """Desenhar uma barra de progresso circular"""

        # Ângulo inicial (topo do círculo)
        angulo_inicial = -math.pi / 2
        # Ângulo final baseado no progresso
        angulo_final = angulo_inicial + (2 * math.pi * progresso)

        # Desenhar arco
        if progresso > 0:
            # Criar lista de pontos para o arco
            pontos = []
            num_segmentos = max(3, int(progresso * 32))  # Mais segmentos para suavidade

            for i in range(num_segmentos + 1):
                angulo = angulo_inicial + (angulo_final - angulo_inicial) * (i / num_segmentos)
                x = centro[0] + raio * math.cos(angulo)
                y = centro[1] + raio * math.sin(angulo)
                pontos.append((x, y))            # Desenhar segmentos da barra circular
            for i in range(len(pontos) - 1):
                pygame.draw.line(screen, cor, pontos[i], pontos[i + 1], espessura)

    def desenhar_joystick_virtual(self, screen):
        """Desenhar joystick virtual melhorado para movimento (estilo mobile)"""

        # Base do joystick com gradiente
        base_surface = pygame.Surface((self.joystick_raio *2.2, self.joystick_raio *2.2), SRCALPHA)
        # Gradiente da base
        for i in range(int(self.joystick_raio * 1.1)):
            alpha = int(120 - (i * 0.8))
            cor_gradiente = (60, 80, 120, alpha)
            pygame.draw.circle(base_surface, cor_gradiente,
                             (int(self.joystick_raio * 1.1), int(self.joystick_raio * 1.1)),
                             self.joystick_raio - i)

        screen.blit(base_surface, (self.joystick_centro[0] - self.joystick_raio * 1.1,
                                  self.joystick_centro[1] - self.joystick_raio * 1.1))        # Borda da base
        pygame.draw.circle(screen, (100, 150, 200), self.joystick_centro, self.joystick_raio, 3)

        # Knob do joystick com efeito 3D
        knob_raio = 22
        cor_knob = (180, 200, 240) if not self.joystick_pressionado else (220, 240, 255)

        # Sombra do knob
        pygame.draw.circle(screen, (0, 0, 0, 100),
                         (self.joystick_knob_pos[0] + 2, self.joystick_knob_pos[1] + 2),
                         knob_raio)

        # Knob principal
        pygame.draw.circle(screen, cor_knob, self.joystick_knob_pos, knob_raio)
        pygame.draw.circle(screen, (120, 150, 180), self.joystick_knob_pos, knob_raio, 2)

        # Brilho no knob
        pygame.draw.circle(screen, (255, 255, 255, 150),
                         (self.joystick_knob_pos[0] - 5, self.joystick_knob_pos[1] - 5),
                         knob_raio // 3)        # Indicador de direção melhorado
        if self.joystick_pressionado:
            dx = self.joystick_knob_pos[0] - self.joystick_centro[0]
            dy = self.joystick_knob_pos[1] - self.joystick_centro[1]
            if dx != 0 or dy != 0:
                distancia = math.sqrt(dx*dx + dy*dy)
                if distancia > 0:
                    dx /= distancia
                    dy /= distancia
                      # Linha de direção com gradiente
                    ponta_x = self.joystick_knob_pos[0] + dx * 18
                    ponta_y = self.joystick_knob_pos[1] + dy * 18
                    pygame.draw.line(screen, (255, 255, 255), self.joystick_knob_pos,
                                   (ponta_x, ponta_y), 4)
                    pygame.draw.line(screen, (100, 200, 255), self.joystick_knob_pos,
                                   (ponta_x, ponta_y), 2)

    def desenhar_botao_ataque(self, screen):
        """Desenhar botão de ataque melhorado (estilo mobile)"""
        # Base do botão com gradiente
        base_surface = pygame.Surface((self.botao_ataque_raio * 2.5, self.botao_ataque_raio * 2.5),
                                     SRCALPHA)
          # Gradiente da base
        for i in range(int(self.botao_ataque_raio * 1.2)):
            alpha = int(100 - (i * 0.6))
            cor_gradiente = (120, 60, 60, alpha)
            pygame.draw.circle(base_surface, cor_gradiente,
                             (int(self.botao_ataque_raio *1.25), int(self.botao_ataque_raio *1.25)),
                             self.botao_ataque_raio - i)

        screen.blit(base_surface, (self.botao_ataque_pos[0] - self.botao_ataque_raio * 1.25,
                                  self.botao_ataque_pos[1] - self.botao_ataque_raio * 1.25))

        # Círculo principal do botão com efeito 3D
        cor_botao = (220, 120, 120) if not self.botao_ataque_pressionado else (255, 150, 150)

        # Sombra do botão
        pygame.draw.circle(screen, (0, 0, 0, 120),
                         (self.botao_ataque_pos[0] + 3, self.botao_ataque_pos[1] + 3),
                         self.botao_ataque_raio)

        # Botão principal
        pygame.draw.circle(screen, cor_botao, self.botao_ataque_pos, self.botao_ataque_raio)
        pygame.draw.circle(screen, (150, 80, 80), self.botao_ataque_pos, self.botao_ataque_raio, 3)

        # Brilho no botão
        pygame.draw.circle(screen, (255, 200, 200, 180),
                         (self.botao_ataque_pos[0] - 8, self.botao_ataque_pos[1] - 8),
                         self.botao_ataque_raio // 2)

        # Ícone de ataque (cruz ou mira)
        centro = self.botao_ataque_pos
        tamanho_icone = self.botao_ataque_raio // 2
        cor_icone = (255, 255, 255) if not self.botao_ataque_pressionado else (255, 255, 100)
          # Cruz de mira
        pygame.draw.line(screen, cor_icone,
                        (centro[0] - tamanho_icone, centro[1]),
                        (centro[0] + tamanho_icone, centro[1]), 4)
        pygame.draw.line(screen, cor_icone,
                        (centro[0], centro[1] - tamanho_icone),
                        (centro[0], centro[1] + tamanho_icone), 4)

        # Efeito pulsante quando pressionado
        if self.botao_ataque_pressionado:
            pulso_surface = pygame.Surface((self.botao_ataque_raio * 4, self.botao_ataque_raio * 4),
                                         SRCALPHA)
            pygame.draw.circle(pulso_surface, (255, 200, 200, 80),
                             (self.botao_ataque_raio * 2, self.botao_ataque_raio * 2),
                             self.botao_ataque_raio + 15)
            screen.blit(pulso_surface, (self.botao_ataque_pos[0] - self.botao_ataque_raio * 2,
                                       self.botao_ataque_pos[1] - self.botao_ataque_raio * 2))

    def processar_evento_touch(self, event):
        """Processar eventos de toque para controles virtuais"""
        if event.type == MOUSEBUTTONDOWN:
            mouse_pos = event.pos            # Verificar toque no joystick
            dist_joystick = math.sqrt((mouse_pos[0] - self.joystick_centro[0])**2 +
                                    (mouse_pos[1] - self.joystick_centro[1])**2)
            if dist_joystick <= self.joystick_raio:
                self.joystick_pressionado = True
                self.joystick_ativo = True
                self.joystick_knob_pos = mouse_pos
                return 'joystick_press'

            # Verificar toque no botão de ataque
            dist_ataque = math.sqrt((mouse_pos[0] - self.botao_ataque_pos[0])**2 +
                                  (mouse_pos[1] - self.botao_ataque_pos[1])**2)
            if dist_ataque <= self.botao_ataque_raio:
                self.botao_ataque_pressionado = True
                return 'attack_press'

        elif event.type == MOUSEBUTTONUP:
            self.joystick_pressionado = False
            self.joystick_ativo = False
            self.joystick_knob_pos = self.joystick_centro
            self.botao_ataque_pressionado = False
            return 'release'
        elif event.type == MOUSEMOTION and self.joystick_pressionado:
            mouse_pos = event.pos
            # Limitar o knob dentro do raio do joystick
            dx = mouse_pos[0] - self.joystick_centro[0]
            dy = mouse_pos[1] - self.joystick_centro[1]
            distancia = math.sqrt(dx*dx + dy*dy)

            if distancia <= self.joystick_raio:
                self.joystick_knob_pos = mouse_pos
            else:
                # Limitar na borda do joystick
                angulo = math.atan2(dy, dx)
                self.joystick_knob_pos = (
                    self.joystick_centro[0] + math.cos(angulo) * self.joystick_raio,
                    self.joystick_centro[1] + math.sin(angulo) * self.joystick_raio
                )
            return 'joystick_move'
        return None

    def obter_direcao_joystick(self):
        """Obter direção normalizada do joystick virtual"""
        if not self.joystick_ativo:
            return (0, 0)

        dx = self.joystick_knob_pos[0] - self.joystick_centro[0]
        dy = self.joystick_knob_pos[1] - self.joystick_centro[1]
        distancia = math.sqrt(dx*dx + dy*dy)

        if distancia > 5:  # Zona morta
            return (dx / self.joystick_raio, dy / self.joystick_raio)
        return (0, 0)

    def exibir_notificacao(self, mensagem):
        """Exibe uma notificação na tela."""
        self.notificacoes.append(mensagem)

    def atualizar_notificacoes(self, screen):
        """Atualiza e renderiza notificações na tela."""
        for i, mensagem in enumerate(self.notificacoes):
            # Renderizar notificações com fade-out
            pos_y = 50 + i * 30
            self.renderizar_texto(screen, mensagem, (10, pos_y))
        # Remover notificações antigas
        if len(self.notificacoes) > 5:
            self.notificacoes.pop(0)

    def renderizar_texto(self, screen, texto, posicao):
        """Renderiza texto na tela."""
        fonte = pygame.font.Font(None, 24)
        texto_renderizado = fonte.render(texto, True, (255, 255, 255))
        screen.blit(texto_renderizado, posicao)

    def desenhar_minimap_melhorado(self, screen, jogador):
        """Desenhar minimap melhorado no canto superior direito"""
        # Posição e tamanho do minimap
        map_size = 120
        map_x = SCREEN_WIDTH - map_size - 10
        map_y = 10

        # Fundo com gradiente
        superficie_fundo = pygame.Surface((map_size, map_size), SRCALPHA)
        pygame.draw.rect(superficie_fundo, (0, 0, 0, 150), (0, 0, map_size, map_size))
        pygame.draw.rect(superficie_fundo, (50, 50, 80, 100), (2, 2, map_size-4, map_size-4))
        screen.blit(superficie_fundo, (map_x, map_y))

        # Borda brilhante
        pygame.draw.rect(screen, (100, 150, 255), (map_x, map_y, map_size, map_size), 2)

        # Título do minimap
        titulo = self.font_pequena.render("MAPA", True, (255, 255, 255))
        titulo_rect = titulo.get_rect(center=(map_x + map_size//2, map_y - 12))
        screen.blit(titulo, titulo_rect)

        # Escala para converter coordenadas do jogo para o minimap
        scale_x = (map_size - 20) / SCREEN_WIDTH
        scale_y = (map_size - 20) / SCREEN_HEIGHT

        # Área útil do mapa (com margem)
        area_x = map_x + 10
        area_y = map_y + 10

        # Desenhar centro do mapa (onde gemas aparecem)
        centro_map_x = area_x + (map_size - 20) // 2
        centro_map_y = area_y + (map_size - 20) // 2
        pygame.draw.circle(screen, (255, 215, 0, 100), (centro_map_x, centro_map_y), 8)
        pygame.draw.circle(screen, (255, 215, 0), (centro_map_x, centro_map_y), 8, 1)

        # Desenhar jogador como ponto pulsante
        if jogador:
            player_x = int(jogador.rect.centerx * scale_x) + area_x
            player_y = int(jogador.rect.centery * scale_y) + area_y

            # Efeito pulsante
            pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.01)) * 3) + 3
            pygame.draw.circle(screen, (0, 255, 0), (player_x, player_y), pulse)
            pygame.draw.circle(screen, (255, 255, 255), (player_x, player_y), 2)

    def desenhar_contador_gemas_melhorado(self, screen, gemas_coletadas):
        """Desenhar contador de gemas grande e visível no topo central"""
        # Posição centralizada
        centro_x = SCREEN_WIDTH // 2
        y = 15

        # Tamanho do contador baseado na proximidade da vitória
        proximidade_vitoria = gemas_coletadas / GEMAS_PARA_VITORIA
        tamanho_base = 50
        tamanho_extra = int(proximidade_vitoria * 20)
        contador_width = tamanho_base + tamanho_extra + 100
        contador_height = 45

        contador_x = centro_x - contador_width // 2

        # Cor de fundo baseada no progresso
        if gemas_coletadas >= GEMAS_PARA_VITORIA:
            cor_fundo = (50, 150, 50, 200)  # Verde brilhante
            cor_borda = (100, 255, 100)
        elif gemas_coletadas >= GEMAS_PARA_VITORIA * 0.7:
            cor_fundo = (150, 150, 50, 200)  # Amarelo
            cor_borda = (255, 255, 100)
        else:
            cor_fundo = (50, 50, 100, 200)  # Azul
            cor_borda = (100, 150, 255)

        # Superfície com transparência
        superficie = pygame.Surface((contador_width, contador_height), SRCALPHA)
        pygame.draw.rect(superficie, cor_fundo, (0, 0, contador_width, contador_height), border_radius=10)
        pygame.draw.rect(superficie, cor_borda, (0, 0, contador_width, contador_height), 3, border_radius=10)
        screen.blit(superficie, (contador_x, y))

        # Ícone de gema grande
        gema_x = contador_x + 15
        gema_y = y + contador_height // 2
        pygame.draw.circle(screen, COR_GEMA, (gema_x, gema_y), 12)
        pygame.draw.circle(screen, (255, 255, 255), (gema_x, gema_y), 8)
        pygame.draw.circle(screen, COR_GEMA, (gema_x, gema_y), 5)

        # Texto grande e destacado
        texto_principal = f"{gemas_coletadas}"
        texto_meta = f"/{GEMAS_PARA_VITORIA}"

        fonte_grande = pygame.font.Font(None, 36)
        fonte_media = pygame.font.Font(None, 28)

        superficie_num = fonte_grande.render(texto_principal, True, (255, 255, 255))
        superficie_meta = fonte_media.render(texto_meta, True, (200, 200, 200))

        texto_x = gema_x + 25
        texto_y = y + 8
        screen.blit(superficie_num, (texto_x, texto_y))
        screen.blit(superficie_meta, (texto_x + superficie_num.get_width(), texto_y + 5))

        # Barra de progresso
        if gemas_coletadas < GEMAS_PARA_VITORIA:
            barra_x = contador_x + 10
            barra_y = y + contador_height - 8
            barra_width = contador_width - 20
            barra_height = 4

            # Fundo da barra
            pygame.draw.rect(screen, (50, 50, 50), (barra_x, barra_y, barra_width, barra_height))

            # Progresso
            progresso_width = int((gemas_coletadas / GEMAS_PARA_VITORIA) * barra_width)
            pygame.draw.rect(screen, cor_borda, (barra_x, barra_y, progresso_width, barra_height))

    def desenhar_barra_vida_melhorada(self, screen, jogador):
        """Desenhar barra de vida colorida na parte inferior esquerda"""
        # Posição na parte inferior
        x = 20
        y = SCREEN_HEIGHT - 60
        barra_width = 200
        barra_height = 25

        # Calcular percentual de vida
        vida_percent = jogador.vida / jogador.vida_maxima
        vida_width = int(vida_percent * barra_width)

        # Fundo da barra com sombra
        sombra_rect = pygame.Rect(x + 2, y + 2, barra_width, barra_height)
        pygame.draw.rect(screen, (0, 0, 0, 100), sombra_rect, border_radius=5)

        fundo_rect = pygame.Rect(x, y, barra_width, barra_height)
        pygame.draw.rect(screen, (40, 40, 40), fundo_rect, border_radius=5)

        # Cor da vida com gradiente baseado no percentual
        if vida_percent > 0.7:
            cor_vida = (50, 200, 50)  # Verde vibrante
        elif vida_percent > 0.4:
            cor_vida = (255, 200, 50)  # Amarelo/laranja
        elif vida_percent > 0.2:
            cor_vida = (255, 150, 50)  # Laranja
        else:
            cor_vida = (255, 50, 50)  # Vermelho crítico

        # Barra de vida principal
        vida_rect = pygame.Rect(x, y, vida_width, barra_height)
        pygame.draw.rect(screen, cor_vida, vida_rect, border_radius=5)

        # Efeito de brilho quando vida baixa
        if vida_percent <= 0.3:
            pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.015)) * 50) + 50
            cor_pulse = (255, pulse, pulse)
            pygame.draw.rect(screen, (*cor_pulse, 100), vida_rect, 2, border_radius=5)

        # Borda externa
        pygame.draw.rect(screen, (200, 200, 200), fundo_rect, 2, border_radius=5)

        # Texto da vida
        texto_vida = f"{int(jogador.vida)}/{int(jogador.vida_maxima)}"
        fonte_vida = pygame.font.Font(None, 20)
        superficie_texto = fonte_vida.render(texto_vida, True, (255, 255, 255))
        texto_rect = superficie_texto.get_rect(center=(x + barra_width//2, y + barra_height//2))
        screen.blit(superficie_texto, texto_rect)

        # Ícone de coração
        coracao_x = x - 25
        coracao_y = y + barra_height // 2
        pygame.draw.circle(screen, cor_vida, (coracao_x, coracao_y), 10)
        pygame.draw.circle(screen, (255, 255, 255), (coracao_x, coracao_y), 6)

    def desenhar_info_nivel_compacta(self, screen, info_nivel):
        """Desenhar informações do nível de forma compacta"""
        x = 20
        y = SCREEN_HEIGHT - 120

        # Fundo compacto
        superficie = pygame.Surface((180, 50), SRCALPHA)
        pygame.draw.rect(superficie, (20, 20, 40, 150), (0, 0, 180, 50), border_radius=8)
        screen.blit(superficie, (x, y))

        # Nível atual
        texto_nivel = self.font_media.render(f"Nível {info_nivel['nivel']}", True, COR_UI)
        screen.blit(texto_nivel, (x + 10, y + 5))

        # Progresso compacto
        if info_nivel['nivel'] < 20:
            barra_x = x + 10
            barra_y = y + 28
            barra_width = 160
            barra_height = 6

            pygame.draw.rect(screen, (60, 60, 60), (barra_x, barra_y, barra_width, barra_height))
            progresso_width = int(info_nivel['progresso'] * barra_width)
            pygame.draw.rect(screen, (0, 255, 255), (barra_x, barra_y, progresso_width, barra_height))

            # Texto do progresso
            texto_prog = self.font_pequena.render(f"{info_nivel['pontuacao_atual']}/{info_nivel['pontuacao_proximo_nivel']}", True, COR_UI)
            screen.blit(texto_prog, (x + 10, y + 36))

    def desenhar_power_ups_ativos_melhorados(self, screen, jogador):
        """Desenhar power-ups ativos de forma melhorada"""
        if not jogador.power_ups_ativos:
            return

        # Posição inicial (lado esquerdo, meio da tela)
        start_x = 20
        start_y = SCREEN_HEIGHT // 2 - 50

        for i, power_up in enumerate(jogador.power_ups_ativos):
            y_pos = start_y + i * 50

            # Definir cor e ícone do power-up
            if power_up['tipo'] == 'velocidade':
                cor = (0, 255, 255)
                icone = "⚡"
                nome = "Velocidade"
            elif power_up['tipo'] == 'vida':
                cor = (0, 255, 0)
                icone = "❤️"
                nome = "Vida"
            elif power_up['tipo'] == 'tiro_rapido':
                cor = (255, 165, 0)
                icone = "🔥"
                nome = "Tiro Rápido"
            else:
                cor = (255, 255, 255)
                icone = "?"
                nome = "Desconhecido"

            # Fundo do power-up
            superficie = pygame.Surface((120, 35), SRCALPHA)
            pygame.draw.rect(superficie, (*cor[:3], 100), (0, 0, 120, 35), border_radius=8)
            pygame.draw.rect(superficie, cor, (0, 0, 120, 35), 2, border_radius=8)
            screen.blit(superficie, (start_x, y_pos))

            # Ícone
            icone_surf = self.font_media.render(icone, True, cor)
            screen.blit(icone_surf, (start_x + 8, y_pos + 5))

            # Nome e tempo
            tempo_restante = int(power_up['tempo_restante'])
            texto_nome = self.font_pequena.render(nome, True, (255, 255, 255))
            texto_tempo = self.font_pequena.render(f"{tempo_restante}s", True, cor)

            screen.blit(texto_nome, (start_x + 35, y_pos + 3))
            screen.blit(texto_tempo, (start_x + 35, y_pos + 18))

            # Barra de tempo restante
            tempo_total = 10.0  # Assumindo 10 segundos de duração
            progresso = power_up['tempo_restante'] / tempo_total
            barra_width = int(80 * progresso)

            pygame.draw.rect(screen, (100, 100, 100), (start_x + 35, y_pos + 32, 80, 2))
            pygame.draw.rect(screen, cor, (start_x + 35, y_pos + 32, barra_width, 2))

    def desenhar_botao_super_melhorado(self, screen, jogador):
        """Desenhar botão de Super brilhante e melhorado"""
        if not hasattr(jogador, 'obter_info_habilidade'):
            return

        info = jogador.obter_info_habilidade()

        # Posição (canto inferior direito, acima do botão de ataque)
        botao_size = 70
        margin = 25
        botao_x = SCREEN_WIDTH - botao_size - margin
        botao_y = SCREEN_HEIGHT - botao_size - margin - 100  # Acima do botão de ataque

        centro_botao = (botao_x + botao_size // 2, botao_y + botao_size // 2)
        raio_botao = botao_size // 2

        # Efeitos visuais baseados no status
        if info['pronta']:
            # Super pronto - efeitos brilhantes
            cor_botao = (255, 215, 0)  # Dourado
            cor_borda = (255, 255, 100)

            # Aura pulsante
            pulse_time = pygame.time.get_ticks() * 0.01
            pulse_radius = raio_botao + int(abs(math.sin(pulse_time)) * 15) + 5
            pulse_alpha = int(abs(math.sin(pulse_time)) * 150) + 50

            superficie_aura = pygame.Surface((botao_size * 3, botao_size * 3), SRCALPHA)
            pygame.draw.circle(superficie_aura, (*cor_borda, pulse_alpha),
                             (botao_size * 3 // 2, botao_size * 3 // 2), pulse_radius)
            screen.blit(superficie_aura, (botao_x - botao_size, botao_y - botao_size))

            # Partículas brilhantes
            for i in range(8):
                angle = (pulse_time + i * 45) % 360
                particle_x = centro_botao[0] + math.cos(math.radians(angle)) * (raio_botao + 20)
                particle_y = centro_botao[1] + math.sin(math.radians(angle)) * (raio_botao + 20)
                pygame.draw.circle(screen, (255, 255, 200), (int(particle_x), int(particle_y)), 2)
        else:
            # Super em cooldown
            cor_botao = (80, 80, 120)
            cor_borda = (120, 120, 160)

        # Círculo principal
        pygame.draw.circle(screen, cor_botao, centro_botao, raio_botao)
        pygame.draw.circle(screen, cor_borda, centro_botao, raio_botao, 4)

        # Gradiente interno
        superficie_gradiente = pygame.Surface((botao_size, botao_size), SRCALPHA)
        for i in range(raio_botao):
            alpha = int(150 * (1 - i / raio_botao))
            pygame.draw.circle(superficie_gradiente, (*cor_borda, alpha),
                             (botao_size // 2, botao_size // 2), i)
        screen.blit(superficie_gradiente, (botao_x, botao_y))

        # Texto no centro
        if info['pronta']:
            fonte_super = pygame.font.Font(None, 24)
            texto = fonte_super.render("SUPER", True, (0, 0, 0))
            texto_rect = texto.get_rect(center=centro_botao)
            screen.blit(texto, texto_rect)
        else:
            fonte_q = pygame.font.Font(None, 32)
            texto = fonte_q.render("Q", True, cor_borda)
            texto_rect = texto.get_rect(center=centro_botao)
            screen.blit(texto, texto_rect)

        # Barra de progresso circular
        if not info['pronta'] and info['cooldown_max'] > 0:
            progresso = 1.0 - (info['cooldown_atual'] / info['cooldown_max'])
            self.desenhar_barra_circular_melhorada(screen, centro_botao, raio_botao + 8,
                                                 progresso, (100, 255, 100), 6)

            # Texto do cooldown
            tempo_text = self.font_pequena.render(f"{info['cooldown_atual']:.1f}s",
                                                True, (255, 255, 255))
            tempo_rect = tempo_text.get_rect(center=(centro_botao[0], botao_y + botao_size + 15))
            screen.blit(tempo_text, tempo_rect)

    def desenhar_barra_circular_melhorada(self, screen, centro, raio, progresso, cor, espessura):
        """Desenhar barra de progresso circular melhorada"""
        if progresso <= 0:
            return

        # Ângulo inicial (topo)
        angulo_inicial = -math.pi / 2
        angulo_final = angulo_inicial + (2 * math.pi * progresso)

        # Número de segmentos para suavidade
        num_segmentos = max(3, int(progresso * 64))

        pontos_externos = []
        pontos_internos = []

        for i in range(num_segmentos + 1):
            angulo = angulo_inicial + (angulo_final - angulo_inicial) * (i / num_segmentos)

            # Pontos da borda externa
            x_ext = centro[0] + math.cos(angulo) * raio
            y_ext = centro[1] + math.sin(angulo) * raio
            pontos_externos.append((x_ext, y_ext))

            # Pontos da borda interna
            x_int = centro[0] + math.cos(angulo) * (raio - espessura)
            y_int = centro[1] + math.sin(angulo) * (raio - espessura)
            pontos_internos.append((x_int, y_int))

        # Desenhar o arco como polígono
        if len(pontos_externos) >= 3:
            # Criar lista de pontos para o polígono
            pontos_poligono = pontos_externos + pontos_internos[::-1]
            pygame.draw.polygon(screen, cor, pontos_poligono)

            # Bordas suaves
            if len(pontos_externos) > 1:
                pygame.draw.lines(screen, cor, False, pontos_externos, 2)
                pygame.draw.lines(screen, cor, False, pontos_internos, 2)
