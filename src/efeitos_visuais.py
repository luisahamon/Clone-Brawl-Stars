"""
Sistema de efeitos visuais do Brawl Stars Clone.
Este módulo implementa diversos efeitos visuais para melhorar a experiência
do jogo, incluindo partículas, explosões, ondas de impacto, rastros e
outros efeitos que tornam o gameplay mais dinâmico e visualmente atrativo.
"""

import math
import random
import pygame
from src.pygame_constants import SRCALPHA

class EfeitoVisual(pygame.sprite.Sprite):
    """Classe base para efeitos visuais"""

    def __init__(self, x, y, duracao=1.0):
        super().__init__()
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.duracao_total = duracao
        self.tempo_vida = duracao
        self.alpha = 255
        # Inicializar surface e rect vazios para evitar erros
        self.image = pygame.Surface((1, 1), SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect()
        if self.rect is not None:
            self.rect.center = (int(self.pos_x), int(self.pos_y))

    def update(self, dt):
        """Atualizar efeito"""
        self.tempo_vida -= dt
        if self.tempo_vida <= 0:
            self.kill()
            return

        # Fade out progressivo
        progresso = self.tempo_vida / self.duracao_total
        self.alpha = int(255 * progresso)

        # Atualizar posição do rect
        self.rect.center = (int(self.pos_x), int(self.pos_y))

class EfeitoExplosao(EfeitoVisual):
    """Efeito de explosão circular"""

    def __init__(self, x, y, cor=(255, 255, 0), tamanho_max=100, duracao=0.5):
        super().__init__(x, y, duracao)
        self.cor = cor
        self.tamanho_max = tamanho_max
        self.tamanho_atual = 0

        # Criar surface inicial
        self.image = pygame.Surface((tamanho_max * 2, tamanho_max * 2), SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

    def atualizar_efeito(self, dt, progresso):
        """Atualizar explosão"""
        # Crescer rapidamente no início, depois diminuir
        if progresso > 0.7:
            self.tamanho_atual = self.tamanho_max * (1 - progresso) * 3.33
        else:
            self.tamanho_atual = self.tamanho_max * (1 - progresso)

        # Redesenhar círculo
        if self.image is None:
            self.image = pygame.Surface((self.tamanho_max * 2, self.tamanho_max * 2), SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        if self.tamanho_atual > 0:
            cor_com_alpha = (*self.cor, self.alpha)
            pygame.draw.circle(self.image, cor_com_alpha,
                             (self.image.get_width()//2, self.image.get_height()//2),
                             int(self.tamanho_atual))

class EfeitoParticulas(EfeitoVisual):
    """Sistema de partículas"""

    def __init__(self, x, y, cor=(255, 255, 255), quantidade=20, duracao=1.0, raio=50):
        super().__init__(x, y, duracao)
        self.cor = cor
        self.raio = raio
        self.particulas = []

        # Criar partículas
        for _ in range(quantidade):
            angulo = random.uniform(0, 2 * math.pi)
            velocidade = random.uniform(50, 150)
            self.particulas.append({
                'x': 0,
                'y': 0,
                'vx': math.cos(angulo) * velocidade,
                'vy': math.sin(angulo) * velocidade,
                'vida': random.uniform(0.5, duracao),
                'tamanho': random.randint(2, 6)
            })

        # Criar surface
        self.image = pygame.Surface((raio * 4, raio * 4), SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

    def atualizar_efeito(self, dt, progresso):
        """Atualizar partículas"""
        if self.image is None:
            # Garante que self.image está inicializada
            self.image = pygame.Surface((self.raio * 4, self.raio * 4), SRCALPHA)
        if self.image is not None:
            self.image.fill((0, 0, 0, 0))
            centro_x = self.image.get_width() // 2
            centro_y = self.image.get_height() // 2
        else:
            centro_x = 0
            centro_y = 0

        for particula in self.particulas[:]:
            particula['x'] += particula['vx'] * dt
            particula['y'] += particula['vy'] * dt
            particula['vida'] -= dt

            if particula['vida'] <= 0:
                self.particulas.remove(particula)
                continue

            # Desenhar partícula
            pos_x = int(centro_x + particula['x'])
            pos_y = int(centro_y + particula['y'])

            if 0 <= pos_x < self.image.get_width() and 0 <= pos_y < self.image.get_height():
                alpha = int(255 * (particula['vida'] / self.duracao_total))
                cor_com_alpha = (*self.cor, alpha)
                pygame.draw.circle(self.image, cor_com_alpha,
                                 (pos_x, pos_y), particula['tamanho'])

class EfeitoOndas(EfeitoVisual):
    """Efeito de ondas concêntricas"""

    def __init__(self, x, y, cor=(0, 255, 255), quantidade_ondas=3, duracao=1.5):
        super().__init__(x, y, duracao)
        self.cor = cor
        self.quantidade_ondas = quantidade_ondas
        self.raio_max = 150

        # Criar surface
        self.image = pygame.Surface((self.raio_max * 2, self.raio_max * 2), SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

    def atualizar_efeito(self, dt, progresso):
        """Atualizar ondas"""
        if self.image is None:
            self.image = pygame.Surface((self.raio_max * 2, self.raio_max * 2), SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        centro = (self.image.get_width() // 2, self.image.get_height() // 2)

        for i in range(self.quantidade_ondas):
            # Cada onda começa em momentos diferentes
            fase = (1 - progresso + i * 0.3) % 1.0
            if fase > 0.9:
                continue

            raio = int(self.raio_max * (1 - fase))
            alpha = int(255 * fase)

            if raio > 0 and alpha > 0:
                cor_com_alpha = (*self.cor, alpha)
                pygame.draw.circle(self.image, cor_com_alpha, centro, raio, 3)

class EfeitoRaio(EfeitoVisual):
    """Efeito de raio/relâmpago"""

    def __init__(self, x1, y1, x2, y2, cor=(255, 255, 0), duracao=0.3, largura=5):
        meio_x = (x1 + x2) / 2
        meio_y = (y1 + y2) / 2
        super().__init__(meio_x, meio_y, duracao)

        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.cor = cor
        self.largura = largura

        # Calcular tamanho da surface
        width = abs(x2 - x1) + largura * 2
        height = abs(y2 - y1) + largura * 2
        self.image = pygame.Surface((width, height), SRCALPHA)
        self.rect = self.image.get_rect(center=(meio_x, meio_y))

        # Calcular offset para desenho
        self.offset_x = width // 2 - (x2 - x1) // 2
        self.offset_y = height // 2 - (y2 - y1) // 2

    def atualizar_efeito(self, dt, progresso):
        """Atualizar raio"""
        self.image.fill((0, 0, 0, 0))

        # Desenhar linha principal
        start_pos = (self.offset_x, self.offset_y)
        end_pos = (self.offset_x + (self.x2 - self.x1), self.offset_y + (self.y2 - self.y1))

        cor_com_alpha = (*self.cor, self.alpha)
        if self.image is not None:
            pygame.draw.line(self.image, cor_com_alpha, start_pos, end_pos, self.largura)

        # Adicionar linhas de energia (efeito tremulante)
        if progresso > 0.3:
            for _ in range(3):
                offset_x = random.randint(-2, 2)
                offset_y = random.randint(-2, 2)
                start_tremulo = (start_pos[0] + offset_x, start_pos[1] + offset_y)
                end_tremulo = (end_pos[0] + offset_x, end_pos[1] + offset_y)
                pygame.draw.line(self.image, cor_com_alpha, start_tremulo, end_tremulo, 2)

class EfeitoArea(EfeitoVisual):
    """Efeito de área/zona"""

    def __init__(self, x, y, raio=80, cor=(255, 0, 255), duracao=3.0):
        super().__init__(x, y, duracao)
        self.cor = cor
        self.raio = raio
        self.pulso = 0

        # Criar surface
        self.image = pygame.Surface((raio * 2, raio * 2), SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

    def atualizar_efeito(self, dt, progresso):
        """Atualizar área de efeito"""
        self.image.fill((0, 0, 0, 0))
        centro = (self.image.get_width() // 2, self.image.get_height() // 2)

        # Efeito de pulso
        self.pulso += dt * 8
        pulso_atual = (math.sin(self.pulso) + 1) / 2  # 0 a 1

        # Círculo interno (área de dano)
        raio_interno = int(self.raio * 0.8)
        alpha_interno = int(100 * progresso * pulso_atual)
        cor_interna = (*self.cor, alpha_interno)
        pygame.draw.circle(self.image, cor_interna, centro, raio_interno)

        # Borda pulsante
        alpha_borda = int(200 * progresso)
        cor_borda = (*self.cor, alpha_borda)
        pygame.draw.circle(self.image, cor_borda, centro, self.raio, 3)

class EfeitoShockwave(EfeitoVisual):
    """Efeito de onda de choque expansiva"""
    def __init__(self, x, y, cor=(255,255,255), velocidade_expansao=200, espessura=10, duracao=1.5):
        super().__init__(x, y, duracao)
        self.cor = cor
        self.velocidade_expansao = velocidade_expansao
        self.espessura = espessura
        self.raio_atual = 0
        self.raio_maximo = velocidade_expansao * duracao
        # Criar surface grande o suficiente
        tamanho = int(self.raio_maximo * 2 + 50)
        self.image = pygame.Surface((tamanho, tamanho), SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

    def atualizar_efeito(self, dt, progresso):
        """Atualizar onda de choque"""
        self.raio_atual += self.velocidade_expansao * dt
        self.image.fill((0, 0, 0, 0))

        centro = (self.image.get_width() // 2, self.image.get_height() // 2)

        if self.raio_atual <= self.raio_maximo:
            # Desenhar anel expansivo
            cor_com_alpha = (*self.cor, self.alpha)
            if self.raio_atual > self.espessura:
                pygame.draw.circle(self.image, cor_com_alpha, centro, int(self.raio_atual), self.espessura)
            else:
                pygame.draw.circle(self.image, cor_com_alpha, centro, int(self.raio_atual))

class EfeitoLaser(EfeitoVisual):
    """Efeito de laser/raio"""

    def __init__(self, x_inicio, y_inicio, x_fim, y_fim, cor=(255, 50, 50), largura=8, duracao=0.8):
        # Calcular centro entre início e fim
        centro_x = (x_inicio + x_fim) / 2
        centro_y = (y_inicio + y_fim) / 2
        super().__init__(centro_x, centro_y, duracao)

        self.x_inicio = x_inicio
        self.y_inicio = y_inicio
        self.x_fim = x_fim
        self.y_fim = y_fim
        self.cor = cor
        self.largura = largura
        self.intensidade = 1.0

        # Calcular dimensões da surface
        largura_total = abs(x_fim - x_inicio) + largura * 2 + 20
        altura_total = abs(y_fim - y_inicio) + largura * 2 + 20

        self.image = pygame.Surface((int(largura_total), int(altura_total)), SRCALPHA)
        self.rect = self.image.get_rect(center=(centro_x, centro_y))

        # Offset para desenhar corretamente na surface
        self.offset_x = largura_total // 2 - (x_fim - x_inicio) // 2
        self.offset_y = altura_total // 2 - (y_fim - y_inicio) // 2

    def atualizar_efeito(self, dt, progresso):
        """Atualizar laser"""
        self.image.fill((0, 0, 0, 0))

        # Intensidade diminui com o tempo
        self.intensidade = progresso

        # Calcular posições relativas na surface
        x1 = self.offset_x
        y1 = self.offset_y
        x2 = self.offset_x + (self.x_fim - self.x_inicio)
        y2 = self.offset_y + (self.y_fim - self.y_inicio)

        # Desenhar múltiplas linhas para efeito de brilho
        for i in range(3):
            largura_atual = max(1, int(self.largura * self.intensidade * (3 - i) / 3))
            alpha = int(self.alpha * (3 - i) / 3)
            cor_com_alpha = (*self.cor, alpha)

            if largura_atual > 0:
                pygame.draw.line(self.image, cor_com_alpha, (x1, y1), (x2, y2), largura_atual)

class EfeitoEscudo(EfeitoVisual):
    """Efeito de escudo protetor"""

    def __init__(self, x, y, raio=60, cor=(100, 200, 255), duracao=3.0):
        super().__init__(x, y, duracao)
        self.cor = cor
        self.raio = raio
        self.rotacao = 0
        self.pulso = 0

        # Criar surface
        tamanho = raio * 2 + 20
        self.image = pygame.Surface((tamanho, tamanho), SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

    def atualizar_efeito(self, dt, progresso):
        """Atualizar escudo"""
        self.rotacao += dt * 90  # Rotação por segundo
        self.pulso += dt * 4

        self.image.fill((0, 0, 0, 0))
        centro = (self.image.get_width() // 2, self.image.get_height() // 2)

        # Efeito de pulso
        pulso_atual = (math.sin(self.pulso) + 1) / 2
        raio_atual = int(self.raio * (0.8 + 0.2 * pulso_atual))

        # Desenhar hexágono rotativo
        pontos = []
        for i in range(6):
            angulo = math.radians(60 * i + self.rotacao)
            x = centro[0] + raio_atual * math.cos(angulo)
            y = centro[1] + raio_atual * math.sin(angulo)
            pontos.append((x, y))

        # Desenhar escudo com transparência
        cor_com_alpha = (*self.cor, int(self.alpha * 0.6))
        if len(pontos) >= 3:
            pygame.draw.polygon(self.image, cor_com_alpha, pontos)
            pygame.draw.polygon(self.image, (*self.cor, self.alpha), pontos, 3)

class NumeroDano(EfeitoVisual):
    """Efeito de número de dano flutuante"""

    def __init__(self, x, y, dano, cor=(255, 50, 50), duracao=1.5):
        super().__init__(x, y, duracao)
        self.dano = dano
        self.cor = cor
        self.vel_y = -50  # Velocidade para subir
        self.fonte = pygame.font.Font(None, 36)
        self.tamanho_inicial = 36
        self.criar_surface()

    def criar_surface(self):
        """Criar surface do texto"""
        texto = str(int(self.dano))
        self.image = self.fonte.render(texto, True, self.cor)
        self.rect = self.image.get_rect()
        self.rect.center = (int(self.pos_x), int(self.pos_y))

    def atualizar_efeito(self, dt, progresso):
        """Atualizar movimento e escala do número"""
        # Movimento para cima
        self.pos_y += self.vel_y * dt

        # Efeito de escala (cresce no início, depois diminui)
        if progresso > 0.7:
            escala = progresso * 1.5
        else:
            escala = 1.0 + (1.0 - progresso) * 0.3        # Recriar surface com nova escala
        tamanho_fonte = int(self.tamanho_inicial * escala)
        fonte_escalada = pygame.font.Font(None, max(tamanho_fonte, 12))
        texto = str(int(self.dano))

        # Aplicar transparência
        surface_temp = fonte_escalada.render(texto, True, self.cor)

        # Criar surface com alpha
        self.image = pygame.Surface(surface_temp.get_size(), SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        surface_temp.set_alpha(self.alpha)
        self.image.blit(surface_temp, (0, 0))

        self.rect = self.image.get_rect()
        self.rect.center = (int(self.pos_x), int(self.pos_y))

class EfeitoImpacto(EfeitoVisual):
    """Efeito de impacto colorido com círculos concêntricos"""

    def __init__(self, x, y, cor=(255, 255, 0), tamanho_max=60, duracao=0.4):
        super().__init__(x, y, duracao)
        self.cor = cor
        self.tamanho_max = tamanho_max
        self.criar_surface()

    def criar_surface(self):
        """Criar surface inicial"""
        self.image = pygame.Surface((self.tamanho_max * 2, self.tamanho_max * 2), SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (int(self.pos_x), int(self.pos_y))

    def atualizar_efeito(self, dt, progresso):
        """Desenhar círculos concêntricos com fade"""
        self.image.fill((0, 0, 0, 0))
        centro = (self.tamanho_max, self.tamanho_max)

        # Desenhar múltiplos círculos
        for i in range(3):
            raio = int(self.tamanho_max * (1.0 - progresso) * (0.3 + i * 0.35))
            if raio > 0:
                alpha = int(self.alpha * (0.8 - i * 0.2))
                cor_com_alpha = (*self.cor, alpha)

                # Criar surface temporária para o círculo
                circle_surface = pygame.Surface((raio * 2, raio * 2), SRCALPHA)
                pygame.draw.circle(circle_surface, cor_com_alpha, (raio, raio), raio, 3)

                # Posicionar no centro
                pos_x = centro[0] - raio
                pos_y = centro[1] - raio
                self.image.blit(circle_surface, (pos_x, pos_y))

class ParticulaGema(EfeitoVisual):
    """Partícula individual para coleta de gemas"""

    def __init__(self, x, y, vel_x, vel_y, cor=(0, 255, 150), tamanho=4):
        super().__init__(x, y, 1.0)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.cor = cor
        self.tamanho = tamanho
        self.gravidade = 200
        self.criar_surface()

    def criar_surface(self):
        """Criar surface da partícula"""
        self.image = pygame.Surface((self.tamanho * 2, self.tamanho * 2), SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, self.cor, (self.tamanho, self.tamanho), self.tamanho)
        self.rect = self.image.get_rect()
        self.rect.center = (int(self.pos_x), int(self.pos_y))

    def atualizar_efeito(self, dt, progresso):
        """Atualizar movimento da partícula"""
        # Aplicar velocidade
        self.pos_x += self.vel_x * dt
        self.pos_y += self.vel_y * dt

        # Aplicar gravidade
        self.vel_y += self.gravidade * dt        # Diminuir tamanho com o tempo
        tamanho_atual = int(self.tamanho * progresso)
        if tamanho_atual > 0:
            self.image = pygame.Surface((tamanho_atual * 2, tamanho_atual * 2), SRCALPHA)
            self.image.fill((0, 0, 0, 0))
            pygame.draw.circle(self.image, self.cor, (tamanho_atual, tamanho_atual), tamanho_atual)
            self.image.set_alpha(self.alpha)
            self.rect = self.image.get_rect()

class EfeitoColetaGema(EfeitoVisual):
    """Efeito completo de coleta de gema com múltiplas partículas"""

    def __init__(self, x, y, num_particulas=12):
        super().__init__(x, y, 0.1)  # Duração muito curta, só para criar as partículas
        self.num_particulas = num_particulas
        self.particulas_criadas = False

        # Criar surface temporária para evitar erro
        self.image = pygame.Surface((1, 1), SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (int(self.pos_x), int(self.pos_y))

    def atualizar_efeito(self, dt, progresso):
        """Criar partículas uma única vez"""
        if not self.particulas_criadas:
            self.criar_particulas()
            self.particulas_criadas = True
            self.kill()  # Removes este efeito após criar as partículas

    def criar_particulas(self):
        """Criar partículas em todas as direções"""
        for i in range(self.num_particulas):
            angulo = (2 * math.pi * i) / self.num_particulas
            velocidade = random.uniform(100, 200)

            vel_x = math.cos(angulo) * velocidade
            vel_y = math.sin(angulo) * velocidade - 50  # Bias para cima

            # Cores variadas para as partículas de gema
            cores = [
                (0, 255, 150),    # Verde brilhante
                (50, 255, 200),   # Verde-azul
                (100, 255, 255),  # Ciano
                (0, 200, 255),    # Azul brilhante
            ]
            cor = random.choice(cores)

            particula = ParticulaGema(
                self.pos_x + random.uniform(-5, 5),
                self.pos_y + random.uniform(-5, 5),
                vel_x, vel_y, cor, random.randint(3, 6)
            )

            # Adicionar ao gerenciador de efeitos
            gerenciador_efeitos.adicionar_efeito(particula)

class GerenciadorEfeitos:
    """Gerencia todos os efeitos visuais do jogo"""

    def __init__(self):
        self.grupo_efeitos = pygame.sprite.Group()
        self.screen_shake = EfeitoScreenShake()

    def update(self, dt):
        """Atualizar todos os efeitos"""
        self.grupo_efeitos.update(dt)
        self.screen_shake.update(dt)

    def draw(self, surface):
        """Desenhar todos os efeitos"""
        self.grupo_efeitos.draw(surface)

    def adicionar_efeito(self, efeito):
        """Adicionar um efeito ao grupo"""
        self.grupo_efeitos.add(efeito)

    def ativar_screen_shake(self, intensidade, duracao):
        """Ativar efeito de tremor da tela"""
        self.screen_shake.ativar(intensidade, duracao)

    def obter_offset_camera(self):
        """Obter offset da câmera para screen shake"""
        return self.screen_shake.obter_offset()

    def criar_rastro_projetil(self, x, y, cor=(255, 255, 255), tamanho=5):
        """Criar rastro para projétil"""
        efeito = EfeitoRastroProjetil(x, y, cor, tamanho)
        self.adicionar_efeito(efeito)

    def criar_numero_flutuante(self, x, y, valor, tipo="dano"):
        """Criar número flutuante melhorado"""
        efeito = EfeitoNumeroFlutuante(x, y, valor, tipo)
        self.adicionar_efeito(efeito)

    def criar_efeito_habilidade(self, tipo, x, y):
        """Criar efeito específico para habilidades"""
        if tipo == "super_shell":
            efeito = EfeitoExplosao(x, y, (255, 165, 0), 80, 0.8)
        elif tipo == "bear_summon":
            efeito = EfeitoOndas(x, y, (139, 69, 19), 60, 1.0)
        elif tipo == "bullet_storm":
            efeito = EfeitoParticulas(x, y, (255, 255, 0), 20, 1.2, 80)
        elif tipo == "charge":
            efeito = EfeitoShockwave(x, y, (255, 0, 0), 100, 0.6)
        elif tipo == "bottle_rain":
            efeito = EfeitoArea(x, y, (0, 255, 0), 80, 2.0)
        elif tipo == "heal_song":
            efeito = EfeitoOndas(x, y, (0, 255, 255), 70, 1.5)
        else:
            efeito = EfeitoExplosao(x, y)

        self.adicionar_efeito(efeito)

    def criar_efeito_tiro_especial(self, tipo, x, y):
        """Criar efeito para tiros especiais"""
        if tipo == "super_shell":
            efeito = EfeitoExplosao(x, y, (255, 140, 0), 40, 0.4)
        else:
            efeito = EfeitoParticulas(x, y, (255, 255, 0), 8, 0.6, 30)

        self.adicionar_efeito(efeito)

    def criar_numero_dano(self, x, y, dano, tipo_dano="normal"):
        """Criar número de dano flutuante"""
        cores_dano = {
            "normal": (255, 50, 50),      # Vermelho para dano normal
            "critico": (255, 255, 0),     # Amarelo para dano crítico
            "super": (255, 100, 255),     # Magenta para dano de super
            "cura": (0, 255, 100),        # Verde para cura
        }

        cor = cores_dano.get(tipo_dano, cores_dano["normal"])
        duracao = 2.0 if tipo_dano == "critico" else 1.5
        efeito = NumeroDano(x, y, dano, cor, duracao)
        self.adicionar_efeito(efeito)

    def criar_efeito_impacto(self, x, y, tipo_impacto="normal"):
        """Criar efeito de impacto colorido"""
        cores_impacto = {
            "normal": (255, 255, 0),      # Amarelo para impacto normal
            "critico": (255, 150, 0),     # Laranja para crítico
            "super": (255, 0, 255),       # Magenta para super
            "inimigo": (255, 100, 100),   # Vermelho claro para inimigo
        }

        cor = cores_impacto.get(tipo_impacto, cores_impacto["normal"])
        tamanho = 80 if tipo_impacto == "critico" else 60
        efeito = EfeitoImpacto(x, y, cor, tamanho, 0.4)
        self.adicionar_efeito(efeito)

    def criar_particulas_gema(self, x, y, intensidade="normal"):
        """Criar partículas de coleta de gema"""
        num_particulas = {
            "pequena": 8,
            "normal": 12,
            "grande": 16
        }

        particulas = num_particulas.get(intensidade, num_particulas["normal"])
        efeito = EfeitoColetaGema(x, y, particulas)
        self.adicionar_efeito(efeito)

    def criar_efeito_vitoria(self, x, y, personagem):
        """Criar efeito de celebração de vitória específico por personagem"""
        if personagem == "Shelly":
            # Explosão dourada com estrelas
            efeito1 = EfeitoExplosao(x, y, (255, 215, 0), 120, 2.0)
            efeito2 = EfeitoParticulas(x, y, (255, 255, 0), 30, 3.0, 100)
            self.adicionar_efeito(efeito1)
            self.adicionar_efeito(efeito2)

        elif personagem == "Nita":
            # Ondas verdes naturais
            efeito1 = EfeitoOndas(x, y, (34, 139, 34), 100, 2.5)
            efeito2 = EfeitoParticulas(x, y, (0, 255, 0), 25, 3.0, 80)
            self.adicionar_efeito(efeito1)
            self.adicionar_efeito(efeito2)

        elif personagem == "Colt":
            # Explosão azul elegante
            efeito1 = EfeitoExplosao(x, y, (70, 130, 180), 90, 1.8)
            efeito2 = EfeitoShockwave(x, y, (25, 25, 112), 110, 1.5)
            self.adicionar_efeito(efeito1)
            self.adicionar_efeito(efeito2)

        elif personagem == "Bull":
            # Ondas de choque vermelhas
            efeito1 = EfeitoShockwave(x, y, (255, 0, 0), 150, 2.0)
            efeito2 = EfeitoExplosao(x, y, (128, 0, 0), 130, 2.2)
            self.adicionar_efeito(efeito1)
            self.adicionar_efeito(efeito2)

        elif personagem == "Barley":
            # Faíscas elétricas coloridas
            efeito1 = EfeitoParticulas(x, y, (255, 255, 0), 40, 2.5, 120)
            efeito2 = EfeitoParticulas(x, y, (0, 255, 0), 30, 2.8, 100)
            self.adicionar_efeito(efeito1)
            self.adicionar_efeito(efeito2)

        elif personagem == "Poco":
            # Ondas musicais multicoloridas
            cores = [(255, 0, 255), (0, 255, 255), (255, 255, 0)]
            for i, cor in enumerate(cores):
                efeito = EfeitoOndas(x + i * 10, y + i * 5, cor, 80 + i * 20, 2.0 + i * 0.3)
                self.adicionar_efeito(efeito)

        else:
            # Efeito padrão - explosão dourada
            efeito = EfeitoExplosao(x, y, (255, 215, 0), 100, 2.0)
            self.adicionar_efeito(efeito)

    def limpar(self):
        """Limpar todos os efeitos"""
        self.grupo_efeitos.empty()

class EfeitoScreenShake:
    """Classe para efeito de tremor da tela"""

    def __init__(self):
        self.intensidade = 0
        self.duracao = 0
        self.tempo_restante = 0
        self.offset_x = 0
        self.offset_y = 0

    def ativar(self, intensidade, duracao):
        """Ativar screen shake com intensidade e duração específicas"""
        self.intensidade = intensidade
        self.duracao = duracao
        self.tempo_restante = duracao

    def update(self, dt):
        """Atualizar screen shake"""
        if self.tempo_restante <= 0:
            self.offset_x = 0
            self.offset_y = 0
            return

        # Calcular intensidade atual baseada no tempo restante
        progresso = self.tempo_restante / self.duracao
        intensidade_atual = self.intensidade * progresso

        # Gerar offsets aleatórios
        self.offset_x = random.randint(-int(intensidade_atual), int(intensidade_atual))
        self.offset_y = random.randint(-int(intensidade_atual), int(intensidade_atual))
        self.tempo_restante -= dt

    def obter_offset(self):
        """Obter offset atual para aplicar à camera"""
        return (self.offset_x, self.offset_y)

class EfeitoRastroProjetil(EfeitoVisual):
    """Efeito de rastro para projéteis"""

    def __init__(self, x, y, cor=(255, 255, 255), tamanho=5):
        super().__init__(x, y, 0.3)  # Duração de 0.3 segundos
        self.cor = cor
        self.tamanho_inicial = tamanho
        self.tamanho_atual = tamanho

        # Criar surface para o rastro
        self.image = pygame.Surface((tamanho * 2, tamanho * 2), SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

    def atualizar_efeito(self, dt, progresso):
        """Atualizar rastro do projétil"""
        self.tamanho_atual = int(self.tamanho_inicial * progresso)

        # Limpar surface
        self.image.fill((0, 0, 0, 0))
        if self.tamanho_atual > 0:
            # Desenhar círculo com fade
            cor_com_alpha = (*self.cor, int(self.alpha))
            pygame.draw.circle(self.image, cor_com_alpha,
                             (self.tamanho_inicial, self.tamanho_inicial),
                             self.tamanho_atual)

class EfeitoNumeroFlutuante(EfeitoVisual):
    """Números de dano flutuantes melhorados"""

    def __init__(self, x, y, valor, tipo="dano"):
        super().__init__(x, y, 2.0)  # Duração de 2 segundos
        self.valor = valor
        self.tipo = tipo
        self.velocidade_y = -50  # Velocidade inicial para cima
        self.velocidade_x = random.randint(-20, 20)  # Movimento lateral aleatório

        # Definir cor baseada no tipo
        cores = {
            "dano": (255, 100, 100),
            "critico": (255, 255, 100),
            "super": (255, 100, 255),
            "cura": (100, 255, 100)
        }
        self.cor = cores.get(tipo, (255, 255, 255))

        # Criar fonte e renderizar texto
        self.font = pygame.font.Font(None, 32 if tipo == "critico" else 24)
        self.criar_surface()

    def criar_surface(self):
        """Criar surface com o texto do dano"""
        texto = f"-{self.valor}" if self.tipo != "cura" else f"+{self.valor}"
        self.image = self.font.render(texto, True, self.cor)
        self.rect = self.image.get_rect(center=(int(self.pos_x), int(self.pos_y)))

    def atualizar_efeito(self, dt, progresso):
        """Atualizar movimento e fade do número"""
        # Movimento parabólico
        self.pos_x += self.velocidade_x * dt
        self.pos_y += self.velocidade_y * dt
        self.velocidade_y += 100 * dt  # Gravidade

        # Aplicar fade
        alpha = int(255 * progresso)
        cor_com_alpha = (*self.cor, alpha)
        self.image = self.font.render(
            f"-{self.valor}" if self.tipo != "cura" else f"+{self.valor}",
            True, cor_com_alpha
        )

class EfeitoImpactoColorido(EfeitoVisual):
    """Efeito de impacto com círculos concêntricos coloridos"""
    def __init__(self, x, y, tipo_impacto="normal"):
        super().__init__(x, y, 0.6)
        self.tipo_impacto = tipo_impacto
        self.raio_max = 40

        # Definir cores baseadas no tipo
        self.cores_impacto = {
            "normal": (255, 255, 0),        # Amarelo
            "critico": (255, 165, 0),       # Laranja
            "super": (255, 0, 255),         # Magenta
            "inimigo": (255, 100, 100)      # Vermelho claro
        }
        self.cor = self.cores_impacto.get(tipo_impacto, (255, 255, 0))

        # Criar surface
        tamanho = self.raio_max * 2 + 20
        self.image = pygame.Surface((tamanho, tamanho), SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def atualizar_efeito(self, dt, progresso):
        """Atualizar impacto colorido"""
        # Limpar surface
        self.image.fill((0, 0, 0, 0))
        centro = (self.image.get_width()//2, self.image.get_height()//2)

        # Desenhar múltiplos círculos concêntricos
        for i in range(3):
            raio = int(self.raio_max * (1 - progresso) * (1 + i * 0.3))
            if raio > 0:
                alpha = max(0, self.alpha - (i * 80))
                cor_com_alpha = (*self.cor, alpha)
                # Desenhar círculo com borda
                pygame.draw.circle(self.image, cor_com_alpha, centro, raio, 3)

class EfeitoAnimacaoGema(EfeitoVisual):
    """Animação especial para coleta de gemas"""
    def __init__(self, x, y):
        super().__init__(x, y, 0.8)
        self.escala = 1.0
        self.rotacao = 0
        self.cor_gema = (0, 255, 200)  # Ciano brilhante

        # Criar surface
        self.image = pygame.Surface((60, 60), SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def atualizar_efeito(self, dt, progresso):
        """Atualizar animação de coleta de gema"""
        # Crescer rapidamente depois diminuir
        if progresso > 0.7:
            self.escala = 2.0 * progresso
        else:
            self.escala = 2.0 - progresso

        # Rotação contínua
        self.rotacao += 720 * dt  # 2 rotações por segundo

        # Redesenhar gema animada
        self.image.fill((0, 0, 0, 0))
        centro = (30, 30)
        # Desenhar gema com múltiplas camadas e brilho
        for i in range(3):
            raio = max(1, int(12 * self.escala) - i * 3)
            alpha = max(0, self.alpha - i * 50)
            cor = (*self.cor_gema, alpha)
            pygame.draw.circle(self.image, cor, centro, raio)

        # Efeito de brilho rotativo
        for i in range(4):
            angulo = self.rotacao + (i * 90)
            end_x = centro[0] + math.cos(math.radians(angulo)) * 20 * self.escala
            end_y = centro[1] + math.sin(math.radians(angulo)) * 20 * self.escala
            pygame.draw.line(self.image, (*self.cor_gema, self.alpha//2),
                           centro, (int(end_x), int(end_y)), 2)

# Instância global do gerenciador de efeitos
gerenciador_efeitos = GerenciadorEfeitos()
