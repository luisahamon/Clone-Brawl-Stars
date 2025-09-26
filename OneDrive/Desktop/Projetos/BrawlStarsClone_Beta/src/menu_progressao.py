"""
Interface do Sistema de Progressão do Brawl Stars Clone.
Telas para visualizar progressão, Star Powers e estatísticas dos Brawlers.
"""

import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, COR_TEXTO, COR_FUNDO
from src.sistema_progressao import sistema_progressao
from src.pygame_constants import MOUSEBUTTONDOWN, MOUSEWHEEL, KEYDOWN, K_ESCAPE

class MenuProgressao:
    """Menu principal do sistema de progressão"""
    def __init__(self):
        self._font_titulo = None
        self._font_texto = None
        self._font_pequeno = None
        self.brawler_selecionado = None
        self.scroll_y = 0
        self.botoes = []
        self.mostrar_star_powers = False

    @property
    def font_titulo(self):
        if self._font_titulo is None:
            pygame.font.init()
            self._font_titulo = pygame.font.Font(None, 48)
        return self._font_titulo

    @property
    def font_texto(self):
        if self._font_texto is None:
            pygame.font.init()
            self._font_texto = pygame.font.Font(None, 32)
        return self._font_texto

    @property
    def font_pequeno(self):
        if self._font_pequeno is None:
            pygame.font.init()
            self._font_pequeno = pygame.font.Font(None, 24)
        return self._font_pequeno

    def desenhar(self, screen, personagens_disponiveis):
        """Desenha o menu de progressão"""
        screen.fill(COR_FUNDO)

        # Título
        titulo = self.font_titulo.render("PROGRESSÃO DOS BRAWLERS", True, COR_TEXTO)
        titulo_rect = titulo.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(titulo, titulo_rect)

        # Lista de Brawlers
        y_start = 120
        card_height = 150
        cards_por_linha = 3
        card_width = (SCREEN_WIDTH - 100) // cards_por_linha
        self.botoes.clear()

        for i, nome_brawler in enumerate(personagens_disponiveis.keys()):
            row = i // cards_por_linha
            col = i % cards_por_linha

            x = 50 + col * card_width + col * 20
            y = y_start + row * (card_height + 20) - self.scroll_y

            # Pular se estiver fora da tela
            if y < -card_height or y > SCREEN_HEIGHT:
                continue

            brawler = sistema_progressao.get_brawler(nome_brawler)
            self.desenhar_card_brawler(screen, brawler, x, y, card_width, card_height)

            # Adicionar botão
            self.botoes.append({
                'rect': pygame.Rect(x, y, card_width, card_height),
                'brawler': nome_brawler,
                'action': 'selecionar'
            })

        # Instruções
        instrucoes = [
            "Clique em um Brawler para ver detalhes",
            "ESC: Voltar ao menu principal",
            "Scroll: Rolar lista"
        ]

        for i, instrucao in enumerate(instrucoes):
            texto = self.font_pequeno.render(instrucao, True, COR_TEXTO)
            screen.blit(texto, (20, SCREEN_HEIGHT - 80 + i * 25))

    def desenhar_card_brawler(self, screen, brawler, x, y, width, height):
        """Desenha um card com informações do Brawler"""
        # Fundo do card
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, (40, 40, 60), card_rect)
        pygame.draw.rect(screen, (100, 100, 120), card_rect, 3)

        # Nome do Brawler
        nome_texto = self.font_texto.render(brawler.nome, True, COR_TEXTO)
        nome_rect = nome_texto.get_rect()
        nome_rect.centerx = x + width // 2
        nome_rect.y = y + 10
        screen.blit(nome_texto, nome_rect)

        # Nível
        nivel_texto = f"Nível {brawler.nivel}"
        nivel_render = self.font_pequeno.render(nivel_texto, True, (255, 215, 0))
        screen.blit(nivel_render, (x + 10, y + 45))

        # Troféus
        trofeus_texto = f"🏆 {brawler.trofeus}"
        trofeus_render = self.font_pequeno.render(trofeus_texto, True, (255, 215, 0))
        screen.blit(trofeus_render, (x + width - 80, y + 45))

        # Barra de experiência
        if brawler.nivel < 10:
            exp_atual = brawler.experiencia - ((brawler.nivel - 1) ** 2 * 100)
            exp_necessaria = (brawler.nivel ** 2 * 100) - ((brawler.nivel - 1) ** 2 * 100)
            progresso = exp_atual / exp_necessaria if exp_necessaria > 0 else 1
        else:
            progresso = 1

        barra_width = width - 20
        barra_height = 8
        barra_x = x + 10
        barra_y = y + 70

        # Fundo da barra
        pygame.draw.rect(screen, (60, 60, 60),
                        (barra_x, barra_y, barra_width, barra_height))

        # Progresso da barra
        if progresso > 0:
            pygame.draw.rect(screen, (0, 255, 100),
                            (barra_x, barra_y, int(barra_width * progresso), barra_height))

        # Estatísticas básicas
        stats_y = y + 85
        win_rate = brawler.get_win_rate()

        stats_texto = [
            f"Partidas: {brawler.partidas_jogadas}",
            f"Vitórias: {brawler.vitorias}",
            f"Win Rate: {win_rate:.1f}%"
        ]

        for i, stat in enumerate(stats_texto):
            stat_render = self.font_pequeno.render(stat, True, COR_TEXTO)
            screen.blit(stat_render, (x + 10, stats_y + i * 18))          # Star Power ativo
        if brawler.star_power_ativo:
            sp_texto = f"⭐ {brawler.star_power_ativo.nome}"
            sp_render = self.font_pequeno.render(sp_texto, True, (255, 215, 0))
            screen.blit(sp_render, (x + 10, y + height - 25))

    def processar_evento(self, evento):
        """Processa eventos do menu"""
        if evento.type == MOUSEBUTTONDOWN:
            if evento.button == 1:  # Clique esquerdo
                mouse_pos = evento.pos
                for botao in self.botoes:
                    if botao['rect'].collidepoint(mouse_pos):
                        if botao['action'] == 'selecionar':
                            self.brawler_selecionado = botao['brawler']
                            self.mostrar_star_powers = True
                            return 'detalhes'
        elif evento.type == MOUSEWHEEL:
            self.scroll_y -= evento.y * 30
            self.scroll_y = max(0, self.scroll_y)
        elif evento.type == KEYDOWN:
            if evento.key == K_ESCAPE:
                return 'voltar'

        return None

    def update(self, dt):
        """Atualiza o menu de progressão (método padrão para compatibilidade)"""
        # O MenuProgressao não tem animações que precisam de update contínuo
        # mas mantemos o método para compatibilidade com outros menus
        return

    def draw(self, screen):
        """Desenha o menu de progressão (método padrão para compatibilidade)"""
        # Chama o método existente com uma lista vazia de personagens por padrão
        personagens_disponiveis = ['SHELLY', 'NITA', 'COLT', 'BULL', 'JESSIE']
        self.desenhar(screen, personagens_disponiveis)

    def handle_event(self, event):
        """Processa eventos do menu (método padrão para compatibilidade)"""
        return self.processar_evento(event)

class MenuDetalhesBrawler:
    """Menu detalhado de um Brawler específico"""

    def __init__(self):
        self._font_titulo = None
        self._font_subtitulo = None
        self._font_texto = None
        self._font_pequeno = None
        self.botoes = []
        self.tab_ativa = 'stats'  # 'stats' ou 'star_powers'

    @property
    def font_titulo(self):
        if self._font_titulo is None:
            pygame.font.init()
            self._font_titulo = pygame.font.Font(None, 48)
        return self._font_titulo

    @property
    def font_subtitulo(self):
        if self._font_subtitulo is None:
            pygame.font.init()
            self._font_subtitulo = pygame.font.Font(None, 36)
        return self._font_subtitulo

    @property
    def font_texto(self):
        if self._font_texto is None:
            pygame.font.init()
            self._font_texto = pygame.font.Font(None, 28)
        return self._font_texto

    @property
    def font_pequeno(self):
        if self._font_pequeno is None:
            pygame.font.init()
            self._font_pequeno = pygame.font.Font(None, 24)
        return self._font_pequeno

    def desenhar(self, screen, nome_brawler):
        """Desenha os detalhes do Brawler"""
        screen.fill(COR_FUNDO)
        brawler = sistema_progressao.get_brawler(nome_brawler)

        # Cabeçalho
        self.desenhar_cabecalho(screen, brawler)

        # Tabs
        self.desenhar_tabs(screen)

        # Conteúdo baseado na tab ativa
        if self.tab_ativa == 'stats':
            self.desenhar_estatisticas(screen, brawler)
        elif self.tab_ativa == 'star_powers':
            self.desenhar_star_powers(screen, brawler)

    def desenhar_cabecalho(self, screen, brawler):
        """Desenha o cabeçalho com informações principais"""
        # Nome
        nome_texto = self.font_titulo.render(brawler.nome, True, COR_TEXTO)
        nome_rect = nome_texto.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(nome_texto, nome_rect)

        # Informações principais em linha
        info_y = 100
        info_items = [
            f"Nível {brawler.nivel}",
            f"🏆 {brawler.trofeus}",
            f"Melhor: {brawler.melhor_trofeus}",
            f"Partidas: {brawler.partidas_jogadas}"
        ]

        total_width = sum(self.font_texto.size(item)[0] for item in info_items) + 60
        start_x = (SCREEN_WIDTH - total_width) // 2

        for i, item in enumerate(info_items):
            cor = (255, 215, 0) if i < 2 else COR_TEXTO
            texto = self.font_texto.render(item, True, cor)
            screen.blit(texto, (start_x + i * (total_width // len(info_items)), info_y))

        # Barra de experiência
        if brawler.nivel < 10:
            self.desenhar_barra_experiencia(screen, brawler, info_y + 40)

    def desenhar_barra_experiencia(self, screen, brawler, y):
        """Desenha a barra de experiência detalhada"""
        exp_atual = brawler.experiencia - ((brawler.nivel - 1) ** 2 * 100)
        exp_necessaria = (brawler.nivel ** 2 * 100) - ((brawler.nivel - 1) ** 2 * 100)
        progresso = exp_atual / exp_necessaria if exp_necessaria > 0 else 1

        barra_width = 400
        barra_height = 20
        barra_x = (SCREEN_WIDTH - barra_width) // 2

        # Fundo da barra
        pygame.draw.rect(screen, (60, 60, 60), (barra_x, y, barra_width, barra_height))

        # Progresso
        if progresso > 0:
            pygame.draw.rect(screen, (0, 255, 100),
                            (barra_x, y, int(barra_width * progresso), barra_height))

        # Texto da experiência
        exp_texto = f"{exp_atual}/{exp_necessaria} EXP"
        exp_render = self.font_pequeno.render(exp_texto, True, COR_TEXTO)
        exp_rect = exp_render.get_rect(center=(SCREEN_WIDTH // 2, y + barra_height + 15))
        screen.blit(exp_render, exp_rect)

    def desenhar_tabs(self, screen):
        """Desenha as tabs de navegação"""
        tab_y = 190
        tab_width = 150
        tab_height = 40

        tabs = [
            ('stats', 'Estatísticas'),
            ('star_powers', 'Star Powers')
        ]

        self.botoes.clear()

        start_x = (SCREEN_WIDTH - len(tabs) * tab_width) // 2

        for i, (tab_id, nome) in enumerate(tabs):
            x = start_x + i * tab_width
            ativa = tab_id == self.tab_ativa

            # Fundo da tab
            cor_fundo = (80, 80, 100) if ativa else (50, 50, 70)
            pygame.draw.rect(screen, cor_fundo, (x, tab_y, tab_width, tab_height))
            pygame.draw.rect(screen, COR_TEXTO, (x, tab_y, tab_width, tab_height), 2)

            # Texto da tab
            texto = self.font_texto.render(nome, True, COR_TEXTO)
            texto_rect = texto.get_rect(center=(x + tab_width // 2, tab_y + tab_height // 2))
            screen.blit(texto, texto_rect)

            # Adicionar botão
            self.botoes.append({
                'rect': pygame.Rect(x, tab_y, tab_width, tab_height),
                'action': 'tab',
                'tab': tab_id
            })

    def desenhar_estatisticas(self, screen, brawler):
        """Desenha as estatísticas detalhadas"""
        stats_y = 250

        # Estatísticas de combate
        stats_combate = [
            ("Vitórias", brawler.vitorias, (0, 255, 0)),
            ("Derrotas", brawler.derrotas, (255, 100, 100)),
            ("Win Rate", f"{brawler.get_win_rate():.1f}%", (255, 215, 0)),
            ("Dano Causado", brawler.estatisticas['dano_total_causado'], (255, 150, 0)),
            ("Dano Recebido", brawler.estatisticas['dano_total_recebido'], (255, 100, 100)),
            ("Inimigos Eliminados", brawler.estatisticas['inimigos_eliminados'], (255, 0, 0)),
            ("Gemas Coletadas", brawler.estatisticas['gemas_coletadas'], (0, 255, 255)),
        ]

        # Dividir em duas colunas
        col1_x = SCREEN_WIDTH // 4
        col2_x = 3 * SCREEN_WIDTH // 4

        for i, (nome, valor, cor) in enumerate(stats_combate):
            x = col1_x if i % 2 == 0 else col2_x
            y = stats_y + (i // 2) * 50

            # Nome da estatística
            nome_texto = self.font_texto.render(f"{nome}:", True, COR_TEXTO)
            nome_rect = nome_texto.get_rect()
            nome_rect.centerx = x
            nome_rect.y = y
            screen.blit(nome_texto, nome_rect)

            # Valor da estatística
            valor_texto = self.font_titulo.render(str(valor), True, cor)
            valor_rect = valor_texto.get_rect()
            valor_rect.centerx = x
            valor_rect.y = y + 25
            screen.blit(valor_texto, valor_rect)

    def desenhar_star_powers(self, screen, brawler):
        """Desenha os Star Powers disponíveis"""
        sp_y = 260

        if not brawler.star_powers:
            sem_sp = self.font_texto.render("Nenhum Star Power disponível", True, COR_TEXTO)
            sem_sp_rect = sem_sp.get_rect(center=(SCREEN_WIDTH // 2, sp_y + 100))
            screen.blit(sem_sp, sem_sp_rect)
            return

        for i, star_power in enumerate(brawler.star_powers):
            y = sp_y + i * 120
            self.desenhar_card_star_power(screen, star_power, brawler, y)

    def desenhar_card_star_power(self, screen, star_power, brawler, y):
        """Desenha um card de Star Power"""
        card_width = SCREEN_WIDTH - 100
        card_height = 100
        card_x = 50

        # Verificar se está disponível
        disponivel = brawler.pode_usar_star_power(star_power)
        ativo = star_power == brawler.star_power_ativo

        # Cor do fundo baseada no status
        if ativo:
            cor_fundo = (80, 120, 80)
        elif disponivel:
            cor_fundo = (80, 80, 120)
        else:
            cor_fundo = (60, 60, 60)

        # Desenhar card
        card_rect = pygame.Rect(card_x, y, card_width, card_height)
        pygame.draw.rect(screen, cor_fundo, card_rect)
        pygame.draw.rect(screen, COR_TEXTO, card_rect, 2)

        # Nome do Star Power
        nome_texto = self.font_subtitulo.render(star_power.nome, True, COR_TEXTO)
        screen.blit(nome_texto, (card_x + 20, y + 10))

        # Descrição
        desc_texto = self.font_texto.render(star_power.descricao, True, COR_TEXTO)
        screen.blit(desc_texto, (card_x + 20, y + 40))

        # Status
        if ativo:
            status = "ATIVO"
            cor_status = (0, 255, 0)
        elif disponivel:
            status = "DISPONÍVEL"
            cor_status = (255, 215, 0)
        else:
            status = f"Nível {star_power.nivel_necessario} necessário"
            cor_status = (150, 150, 150)

        status_texto = self.font_pequeno.render(status, True, cor_status)
        status_rect = status_texto.get_rect()
        status_rect.right = card_x + card_width - 20
        status_rect.centery = y + card_height // 2
        screen.blit(status_texto, status_rect)

        # Botão de ativar se disponível e não ativo
        if disponivel and not ativo:
            botao_width = 100
            botao_height = 30
            botao_x = card_x + card_width - botao_width - 20
            botao_y = y + card_height - botao_height - 10

            pygame.draw.rect(screen, (0, 150, 0), (botao_x, botao_y, botao_width, botao_height))
            pygame.draw.rect(screen, (0, 255, 0), (botao_x, botao_y, botao_width, botao_height), 2)

            ativar_texto = self.font_pequeno.render("ATIVAR", True, COR_TEXTO)
            ativar_rect = ativar_texto.get_rect(center=(botao_x + botao_width // 2, botao_y + botao_height // 2))
            screen.blit(ativar_texto, ativar_rect)
            # Adicionar botão
            self.botoes.append({
                'rect': pygame.Rect(botao_x, botao_y, botao_width, botao_height),
                'action': 'ativar_star_power',
                'star_power': star_power
            })

    def processar_evento(self, evento, nome_brawler):
        """Processa eventos do menu de detalhes"""
        if evento.type == MOUSEBUTTONDOWN:
            if evento.button == 1:  # Clique esquerdo
                mouse_pos = evento.pos
                for botao in self.botoes:
                    if botao['rect'].collidepoint(mouse_pos):
                        if botao['action'] == 'tab':
                            self.tab_ativa = botao['tab']
                            return None
                        elif botao['action'] == 'ativar_star_power':
                            brawler = sistema_progressao.get_brawler(nome_brawler)
                            brawler.ativar_star_power(botao['star_power'])
                            sistema_progressao.salvar_progressao()
                            return None
        elif evento.type == KEYDOWN:
            if evento.key == K_ESCAPE:
                return 'voltar'

        return None
    def update(self, dt):
        """Atualiza o menu de detalhes (método padrão para compatibilidade)"""
        # O MenuDetalhesBrawler não tem animações que precisam de update contínuo
        # mas mantemos o método para compatibilidade com outros menus
        return

    def draw(self, screen):
        """Desenha o menu de detalhes (método padrão para compatibilidade)"""
        # Chama o método existente com nome padrão de brawler
        self.desenhar(screen, 'SHELLY')

    def handle_event(self, event):
        """Processa eventos do menu (método padrão para compatibilidade)"""
        return self.processar_evento(event, 'SHELLY')

# Instâncias globais
menu_progressao = MenuProgressao()
menu_detalhes = MenuDetalhesBrawler()
