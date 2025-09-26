"""
Tela de seleção de personagens do Brawl Stars Clone.

Este módulo implementa a interface avançada de seleção de personagens, com cards 3D,
preview de stats em barras, animações suaves e descrições detalhadas das habilidades.
Proporciona uma experiência visual rica e informativa para a escolha do personagem.
"""

import math
import random
import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, COR_UI
from src.characters.personagens import PERSONAGENS_DISPONIVEIS, obter_personagem
from src.audio_manager import gerenciador_audio
from src.pygame_constants import (SRCALPHA, KEYDOWN, K_LEFT, K_RIGHT, K_A, K_D,
                                 K_RETURN, K_SPACE, K_ESCAPE, K_C)

class SeletorPersonagem:
    """Tela de seleção de personagens com interface 3D e animações avançadas"""

    def __init__(self, screen):
        self.screen = screen
        self.font_titulo = pygame.font.Font(None, 56)
        self.font_nome = pygame.font.Font(None, 36)
        self.font_stats = pygame.font.Font(None, 28)
        self.font_desc = pygame.font.Font(None, 22)
        self.font_habilidade = pygame.font.Font(None, 24)

        self.personagens = list(PERSONAGENS_DISPONIVEIS.keys())
        self.personagem_selecionado = 0
        self.tempo_animacao = 0
        self.tempo_transicao = 0
        self.animacao_selecao = 0        # Criar instâncias para mostrar stats
        self.instancias_personagens = {}
        for nome in self.personagens:
            self.instancias_personagens[nome] = obter_personagem(nome)

        # Animações e efeitos
        self.particulas_fundo = []
        self.ultimo_selecionado = 0
        self.card_rotation = 0
        self.card_scale = 1.0        # Inicializar partículas de fundo
        self.gerar_particulas_fundo()

    def update(self, dt):
        """Atualizar animações e efeitos visuais"""
        self.tempo_animacao += dt * 2

        # Atualizar partículas de fundo
        self.atualizar_particulas(dt)

        # Animação de transição quando muda personagem
        if self.personagem_selecionado != self.ultimo_selecionado:
            self.tempo_transicao = 0.5
            self.ultimo_selecionado = self.personagem_selecionado

        if self.tempo_transicao > 0:
            self.tempo_transicao -= dt

        # Animação do card principal
        self.card_rotation = math.sin(self.tempo_animacao) * 2
        self.card_scale = 1.0 + 0.05 * math.sin(self.tempo_animacao * 3)
          # Animação de seleção pulsante
        self.animacao_selecao += dt * 4

    def render(self):
        """Renderizar tela de seleção com efeitos visuais avançados"""
        # Fundo gradiente
        self.desenhar_fundo_gradiente()

        # Partículas de fundo
        self.desenhar_particulas_fundo()

        # Título com efeito brilhante
        self.desenhar_titulo_animado()

        # Desenhar personagem principal central grande (estilo Brawl Stars)
        self.desenhar_personagem_central()

        # Desenhar cards de personagens 3D
        self.desenhar_cards_personagens()

        # Desenhar informações detalhadas do personagem selecionado
        self.desenhar_painel_informacoes()

        # Instruções
        self.desenhar_instrucoes()

    def desenhar_fundo_gradiente(self):
        """Desenhar fundo com gradiente animado"""
        # Gradiente vertical do azul escuro para roxo
        for y in range(SCREEN_HEIGHT):
            progresso = y / SCREEN_HEIGHT
            # Animação sutil de cor
            offset = math.sin(self.tempo_animacao * 0.5 + progresso * 2) * 10
            r = int(20 + offset + progresso * 30)
            g = int(20 + offset + progresso * 10)
            b = int(40 + offset + progresso * 80)
            pygame.draw.line(self.screen, (max(0, min(255, r)),
                                         max(0, min(255, g)),
                                         max(0, min(255, b))),
                           (0, y), (SCREEN_WIDTH, y))

    def desenhar_titulo_animado(self):
        """Desenhar título com efeito brilhante animado"""
        titulo_texto = "SELECIONE SEU BRAWLER"        # Efeito de brilho pulsante
        brilho = int(50 + 30 * math.sin(self.tempo_animacao * 2))
        cor_brilho = (255, 255, max(0, min(255, 200 + brilho)))

        # Posição proporcional à altura da tela
        titulo_y = SCREEN_HEIGHT // 8  # 12.5% da altura da tela

        # Sombra ajustada proporcionalmente
        titulo_sombra = self.font_titulo.render(titulo_texto, True, (0, 0, 0))
        titulo_rect_sombra = titulo_sombra.get_rect(center=(SCREEN_WIDTH // 2 + 3, titulo_y + 3))
        self.screen.blit(titulo_sombra, titulo_rect_sombra)        # Título principal ajustado
        titulo = self.font_titulo.render(titulo_texto, True, cor_brilho)
        titulo_rect = titulo.get_rect(center=(SCREEN_WIDTH // 2, titulo_y))
        self.screen.blit(titulo, titulo_rect)

    def desenhar_personagem_central(self):
        """Desenha o personagem selecionado grande no centro da tela (estilo Brawl Stars)"""
        nome = self.personagens[self.personagem_selecionado]
        personagem = self.instancias_personagens[nome]

        # Posição central ajustada - um pouco mais para cima
        centro_x = SCREEN_WIDTH // 2
        centro_y = SCREEN_HEIGHT // 3  # 33% da altura para dar espaço aos cards

        # Efeito de aura brilhante
        self.desenhar_aura_selecao(centro_x, centro_y, personagem.cor_principal)

        # Partículas especiais
        self.desenhar_particulas_personagem(centro_x, centro_y, personagem.cor_principal)        # Renderizar personagem 3D em tamanho grande com animações
        tamanho_grande = 40 + int(5 * math.sin(self.tempo_animacao * 2))  # Menor para dar espaço

        # Ativar movimento para animações no menu - SEMPRE ativo no menu
        personagem.em_movimento = True  # Sempre True para movimento contínuo
        personagem.poder_ativo = self.animacao_selecao % 2 > 1  # Alternar aura

        personagem.render_3d(self.screen, (centro_x, centro_y), self.tempo_animacao * 1000, tamanho_grande)

    def desenhar_instrucoes(self):
        """Desenhar instruções na parte inferior da tela"""
        # Instruções
        instrucoes = [
            "← → ou A D: Navegar",
            "ENTER ou ESPAÇO: Selecionar",
            "C: Configurações de Áudio",
            "ESC: Voltar"
        ]

        y_instrucoes = SCREEN_HEIGHT - (SCREEN_HEIGHT//10) #10% da altura da tela da parte inferior
        for i, instrucao in enumerate(instrucoes):
            cor_instrucao = (200, 200, 200) if i % 2 == 0 else (180, 180, 180)
            instrucao_surface = self.font_desc.render(instrucao, True, cor_instrucao)
            x_pos = (SCREEN_WIDTH // 2) - (instrucao_surface.get_width() // 2)
            y_pos = y_instrucoes + i * 20
            self.screen.blit(instrucao_surface, (x_pos, y_pos))

    def desenhar_painel_informacoes(self):
        """Desenhar painel com informações detalhadas do personagem selecionado"""
        nome = self.personagens[self.personagem_selecionado]
        personagem = self.instancias_personagens[nome]

        # Debug: verificar se está sendo chamado
        # Desenhar painel de personagem (removido debug print)

        # Painel de informações ajustado proporcionalmente
        altura_painel = SCREEN_HEIGHT // 4  # 25% da altura da tela
        margem = SCREEN_WIDTH // 40  # 2.5% da largura da tela
        painel_rect = pygame.Rect(margem, SCREEN_HEIGHT - altura_painel - margem,
                                 SCREEN_WIDTH - (margem * 2), altura_painel)

        pygame.draw.rect(self.screen, (40, 40, 60, 180), painel_rect)
        pygame.draw.rect(self.screen, personagem.cor_principal, painel_rect, 3)

        # Nome grande
        nome_y = SCREEN_HEIGHT - altura_painel - margem + 20
        nome_grande = self.font_nome.render(nome, True, personagem.cor_principal)
        self.screen.blit(nome_grande, (margem + 20, nome_y))

        # Stats em texto ajustados proporcionalmente
        stats_x = margem + 20
        stats_y = nome_y + 50

        stats = [
            f"❤️ Vida: {personagem.vida_maxima}",
            f"⚡ Velocidade: {int(personagem.velocidade)}",
            f"⚔️ Dano: {personagem.dano}",
            f"🔄 Cadência: {personagem.cooldown:.1f}s",
            f"🎯 Tipo de Tiro: {personagem.tipo_tiro.title()}"
        ]

        for i, stat in enumerate(stats):
            cor_stat = COR_UI if i < 2 else (200, 200, 200)
            stat_surface = self.font_stats.render(stat, True, cor_stat)
            y_pos = stats_y + (i % 3) * 30
            x_pos = stats_x + (i // 3) * 300
            self.screen.blit(stat_surface, (x_pos, y_pos))

        # Habilidade especial
        habilidade_y = stats_y + 80  # Mais próximo das stats
        habilidade_titulo = self.font_nome.render("🌟 Habilidade Especial:", True, (255, 215, 0))
        self.screen.blit(habilidade_titulo, (stats_x, habilidade_y))

        # Descrição da habilidade baseada no personagem
        descricoes_habilidades = {
            'Shelly': 'Super Shell - Disparo devastador com dano duplo',
            'Nita': 'Invocar Urso - Invoca um urso aliado por 15 segundos',
            'Colt': 'Rajada de Balas - Dispara 6 tiros em sequência rápida',
            'Bull': 'Investida - Corre velozmente causando dano por contato',
            'Barley': 'Chuva de Garrafas - Lança 5 garrafas que criam áreas de dano',
            'Poco': 'Melodia Curativa - Cura aliados próximos com música'
        }

        desc_habilidade = descricoes_habilidades.get(nome, 'Habilidade especial única')
        habilidade_desc = self.font_desc.render(desc_habilidade, True, (220, 220, 220))
        self.screen.blit(habilidade_desc, (stats_x, habilidade_y + 30))

        # Barras visuais de stats ajustadas
        barras_x = SCREEN_WIDTH - 400  # Posição à direita
        self.desenhar_barras_stats(personagem, barras_x, stats_y)

    def desenhar_particulas_fundo(self):
        """Desenhar partículas decorativas no fundo"""
        for particula in self.particulas_fundo:
            surface = pygame.Surface((particula['tamanho'] * 2, particula['tamanho'] * 2), SRCALPHA)
            cor_com_alpha = (*particula['cor'], particula['alpha'])
            pygame.draw.circle(surface, cor_com_alpha,
                             (particula['tamanho'], particula['tamanho']),
                             particula['tamanho'])
            self.screen.blit(surface, (particula['x'] - particula['tamanho'],
                                     particula['y'] - particula['tamanho']))

    def desenhar_personagens(self):
        """Desenhar os personagens disponíveis - MÉTODO LEGADO (mantido para compatibilidade)"""
        self.desenhar_cards_personagens()

    def desenhar_cards_personagens(self):
        """Desenhar cards 3D dos personagens com animações avançadas"""
        centro_x = SCREEN_WIDTH // 2
        centro_y = SCREEN_HEIGHT // 2 - 50  # Mais para cima, entre o personagem central e o painel
        raio = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 6  # Menor para ficar mais próximo

        for i, nome in enumerate(self.personagens):
            personagem = self.instancias_personagens[nome]

            # Calcular posição em elipse com movimento suave
            angulo = (i * 2 * math.pi / len(self.personagens)) + self.tempo_animacao * 0.3
            offset_x = raio * math.cos(angulo)
            offset_y = raio * math.sin(angulo) * 0.4  # Elipse mais achatada

            x = centro_x + offset_x
            y = centro_y + offset_y

            # Calcular profundidade para efeito 3D
            profundidade = math.sin(angulo) * 0.5 + 0.5  # 0 a 1
            escala_base = 0.6 + profundidade * 0.4  # 0.6 a 1.0

            # Efeito especial para o personagem selecionado
            if i == self.personagem_selecionado:
                # Card selecionado fica maior e com efeitos especiais
                escala_selecao = 1.3 + 0.1 * math.sin(self.animacao_selecao)
                escala_final = escala_base * escala_selecao

                # Desenhar aura brilhante
                self.desenhar_aura_selecao(x, y, personagem.cor_principal)

                # Partículas ao redor do personagem selecionado
                self.desenhar_particulas_personagem(x, y, personagem.cor_principal)
            else:
                escala_final = escala_base * 0.8

            # Desenhar card 3D
            self.desenhar_card_3d(x, y, personagem, escala_final, profundidade, i == self.personagem_selecionado)

    def desenhar_card_3d(self, x, y, personagem, escala, profundidade, selecionado):
        """Desenhar um card 3D individual do personagem"""
        # Tamanho do card baseado na escala
        largura_card = int(100 * escala)
        altura_card = int(120 * escala)

        # Cor do card com base na profundidade
        intensidade = int(150 + profundidade * 105)  # 150 a 255
        cor_card = (intensidade, intensidade, intensidade)

        if selecionado:
            cor_card = personagem.cor_principal

        # Desenhar sombra do card
        sombra_offset = int(8 * escala)
        pygame.draw.rect(self.screen, (0, 0, 0, 100),
                        (x - largura_card // 2 + sombra_offset,
                         y - altura_card // 2 + sombra_offset,
                         largura_card, altura_card))

        # Desenhar card principal
        card_rect = pygame.Rect(x - largura_card // 2, y - altura_card // 2,
                               largura_card, altura_card)
        pygame.draw.rect(self.screen, cor_card, card_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), card_rect, 3)        # Desenhar personagem 3D no card em vez do sprite 2D
        tamanho_3d = int(15 * escala)  # Tamanho menor para os cards

        # Ativar animações leves nos cards - TODOS os personagens devem ter movimento
        personagem.em_movimento = True  # Sempre True para animação contínua no menu
        personagem.poder_ativo = selecionado  # Apenas o selecionado tem aura especial

        personagem.render_3d(self.screen, (x, y - 10), self.tempo_animacao * 500, tamanho_3d)

        # Nome do personagem
        font_size = max(16, int(24 * escala))
        font_nome_card = pygame.font.Font(None, font_size)
        cor_nome = (255, 255, 255) if selecionado else (200, 200, 200)
        nome_surface = font_nome_card.render(personagem.nome, True, cor_nome)
        nome_rect = nome_surface.get_rect(center=(x, y + 35))
        self.screen.blit(nome_surface, nome_rect)

    def desenhar_aura_selecao(self, x, y, cor_principal):
        """Desenhar aura brilhante ao redor do personagem selecionado"""
        for i in range(5):
            raio = 80 + i * 15 + int(10 * math.sin(self.animacao_selecao * 2 + i))
            alpha = 255 - i * 50
            cor_aura = (*cor_principal, alpha)

            surface_aura = pygame.Surface((raio * 2, raio * 2), SRCALPHA)
            pygame.draw.circle(surface_aura, cor_aura, (raio, raio), raio, 3)
            self.screen.blit(surface_aura, (x - raio, y - raio))

    def desenhar_particulas_personagem(self, x, y, cor_principal):
        """Desenhar partículas especiais ao redor do personagem selecionado"""
        for i in range(8):
            angulo = (i * math.pi / 4) + self.tempo_animacao
            raio_particula = 60 + 20 * math.sin(self.tempo_animacao * 2 + i)
            px = x + raio_particula * math.cos(angulo)
            py = y + raio_particula * math.sin(angulo)

            tamanho = 4 + int(2 * math.sin(self.tempo_animacao * 3 + i))
            alpha = int(100 + 50 * math.sin(self.tempo_animacao + i))
            cor_particula = (*cor_principal, alpha)

            surface_particula = pygame.Surface((tamanho * 2, tamanho * 2), SRCALPHA)
            pygame.draw.circle(surface_particula, cor_particula, (tamanho, tamanho), tamanho)
            self.screen.blit(surface_particula, (px - tamanho, py - tamanho))

    def desenhar_info_personagem(self):
        """Desenhar informações detalhadas do personagem selecionado"""
        nome = self.personagens[self.personagem_selecionado]
        personagem = self.instancias_personagens[nome]

        # Painel de informações
        painel_rect = pygame.Rect(50, 450, SCREEN_WIDTH - 100, 250)
        pygame.draw.rect(self.screen, (40, 40, 60), painel_rect)
        pygame.draw.rect(self.screen, personagem.cor_principal, painel_rect, 3)

        # Nome grande
        nome_grande = self.font_titulo.render(nome, True, personagem.cor_principal)
        nome_y = 470
        self.screen.blit(nome_grande, (70, nome_y))

        # Stats
        stats_x = 70
        stats_y = 520

        stats = [
            f"❤️ Vida: {personagem.vida_maxima}",
            f"⚡ Velocidade: {int(personagem.velocidade)}",
            f"⚔️ Dano: {personagem.dano}",
            f"🔄 Cadência: {personagem.cooldown:.1f}s",
            f"🎯 Tipo de Tiro: {personagem.tipo_tiro.title()}"
        ]

        for i, stat in enumerate(stats):
            cor_stat = COR_UI if i < 2 else (200, 200, 200)
            stat_surface = self.font_stats.render(stat, True, cor_stat)
            y_pos = stats_y + (i % 3) * 30
            x_pos = stats_x + (i // 3) * 300
            self.screen.blit(stat_surface, (x_pos, y_pos))

        # Habilidade especial
        habilidade_y = nome_y + 130  # Proporcional ao painel
        habilidade_titulo = self.font_nome.render("🌟 Habilidade Especial:", True, (255, 215, 0))
        self.screen.blit(habilidade_titulo, (stats_x, habilidade_y))

        # Descrição da habilidade baseada no personagem
        descricoes_habilidades = {
            'Shelly': 'Super Shell - Disparo devastador com dano duplo',
            'Nita': 'Invocar Urso - Invoca um urso aliado por 15 segundos',
            'Colt': 'Rajada de Balas - Dispara 6 tiros em sequência rápida',
            'Bull': 'Investida - Corre velozmente causando dano por contato',
            'Barley': 'Chuva de Garrafas - Lança 5 garrafas que criam áreas de dano',
            'Poco': 'Melodia Curativa - Cura aliados próximos com música'
        }

        desc_habilidade = descricoes_habilidades.get(nome, 'Habilidade especial única')
        habilidade_desc = self.font_desc.render(desc_habilidade, True, (220, 220, 220))
        self.screen.blit(habilidade_desc, (70, habilidade_y + 30))

        # Barras visuais de stats
        self.desenhar_barras_stats(personagem, 400, 520)

    def desenhar_barras_stats(self, personagem, x, y):
        """Desenhar barras visuais das estatísticas"""
        # Valores máximos para normalização
        max_vida = 200
        max_velocidade = 400
        max_dano = 50

        stats_barras = [
            ("Vida", personagem.vida_maxima, max_vida, (255, 100, 100)),
            ("Velocidade", personagem.velocidade, max_velocidade, (100, 255, 100)),
            ("Dano", personagem.dano, max_dano, (255, 255, 100))        ]

        largura_barra = 200
        altura_barra = 20

        for i, (_, valor, max_valor, cor) in enumerate(stats_barras):
            y_barra = y + i * 35

            # Fundo da barra
            pygame.draw.rect(self.screen, (60, 60, 60), (x, y_barra, largura_barra, altura_barra))

            # Barra preenchida
            preenchimento = min(valor / max_valor, 1.0)
            largura_preenchida = int(largura_barra * preenchimento)
            pygame.draw.rect(self.screen, cor, (x, y_barra, largura_preenchida, altura_barra))
            # Borda
            pygame.draw.rect(self.screen, (200, 200, 200), (x, y_barra, largura_barra, altura_barra), 2)
            # Texto do valor
            texto_valor = self.font_desc.render(f"{int(valor)}", True, COR_UI)
            self.screen.blit(texto_valor, (x + largura_barra + 10, y_barra + 2))

    def gerar_particulas_fundo(self):
        """Gerar partículas decorativas para o fundo"""
        self.particulas_fundo = []
        for _ in range(30):
            particula = {
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'vel_x': random.uniform(-20, 20),
                'vel_y': random.uniform(-20, 20),
                'tamanho': random.randint(2, 8),
                'cor': (random.randint(50, 150), random.randint(50, 150), random.randint(100, 255)),
                'alpha': random.randint(30, 100)
            }
            self.particulas_fundo.append(particula)

    def atualizar_particulas(self, dt):
        """Atualizar movimento das partículas de fundo"""
        for particula in self.particulas_fundo:
            particula['x'] += particula['vel_x'] * dt
            particula['y'] += particula['vel_y'] * dt

            # Wrap around screen
            if particula['x'] < 0:
                particula['x'] = SCREEN_WIDTH
            elif particula['x'] > SCREEN_WIDTH:
                particula['x'] = 0
            if particula['y'] < 0:
                particula['y'] = SCREEN_HEIGHT
            elif particula['y'] > SCREEN_HEIGHT:
                particula['y'] = 0

    def handle_selection_event(self, event):
        """Processar eventos de input do usuário na seleção de personagens"""
        if event.type == KEYDOWN:
            if event.key in [K_LEFT, K_A]:  # Navegar para esquerda
                gerenciador_audio.tocar_som('ui_select')
                self.personagem_selecionado = (self.personagem_selecionado - 1) % len(self.personagens)
                return None

            elif event.key in [K_RIGHT, K_D]:  # Navegar para direita
                gerenciador_audio.tocar_som('ui_select')
                self.personagem_selecionado = (self.personagem_selecionado + 1) % len(self.personagens)
                return None

            elif event.key in [K_RETURN, K_SPACE]:  # Selecionar personagem
                gerenciador_audio.tocar_som('ui_confirm')
                nome_personagem = self.personagens[self.personagem_selecionado]
                return nome_personagem

            elif event.key == K_ESCAPE:  # Voltar/Sair
                gerenciador_audio.tocar_som('ui_back')
                return "voltar"

            elif event.key == K_C:  # Configurações de áudio
                gerenciador_audio.tocar_som('ui_select')
                return "audio"

        return None
