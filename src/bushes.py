"""
Sistema de Arbustos (Bushes) do Brawl Stars Clone.
Este módulo implementa os arbustos que fornecem cobertura visual no jogo,
permitindo que jogadores se escondam estrategicamente dos inimigos.
Os arbustos reduzem a visibilidade e podem ser usados taticamente.
"""

import random
import math
import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.pygame_constants import SRCALPHA
from src.ambiente_dinamico import EfeitoVentoArbustos


class Arbusto(pygame.sprite.Sprite):
    """Classe individual para um arbusto"""

    def __init__(self, x, y, largura=80, altura=80):
        super().__init__()
        self.pos_x = x
        self.pos_y = y
        self.largura = largura
        self.altura = altura

        # Criar sprite do arbusto
        self.image = pygame.Surface((largura, altura), SRCALPHA)
        self.rect = pygame.Rect(x - largura//2, y - altura//2, largura, altura)

        # Propriedades do arbusto
        self.densidade = random.uniform(0.6, 0.9)  # Densidade da vegetação
        self.cor_base = (34, 139, 34)  # Verde floresta
        self.cor_escura = (0, 100, 0)  # Verde escuro
        self.cor_clara = (144, 238, 144)  # Verde claro

        # Animação sutil
        self.tempo_animacao = random.uniform(0, math.pi * 2)
        self.intensidade_animacao = random.uniform(0.02, 0.05) #Lista de entidades dentro do arbusto
        self.entidades_dentro = set()

        # Efeitos de balanço pelo vento
        self.balanco_x = 0.0
        self.balanco_y = 0.0
        self.gerar_sprite()

    def gerar_sprite(self):
        """Gerar sprite procedural do arbusto"""
        self.image.fill((0, 0, 0, 0))  # Transparente

        # Desenhar múltiplas camadas de folhagem
        for camada in range(3):
            alpha = int(255 * (0.4 + camada * 0.2))
            intensidade = 1.0 - camada * 0.15

            # Cor da camada
            cor_camada = (
                int(self.cor_base[0] * intensidade),
                int(self.cor_base[1] * intensidade),
                int(self.cor_base[2] * intensidade),
                alpha
            )

            # Desenhar círculos sobrepostos para simular folhagem
            num_circulos = 8 + camada * 3
            for i in range(num_circulos):
                # Posição dos círculos de folhagem
                angulo = (i * 2 * math.pi / num_circulos) + camada * 0.5
                raio_offset = (self.largura * 0.3) * (0.7 + camada * 0.15)
                cx = self.largura // 2 + int(math.cos(angulo) * raio_offset)
                cy = self.altura // 2 + int(math.sin(angulo) * raio_offset)

                # Tamanho do círculo
                raio_circulo = random.randint(12, 20) + camada * 5

                # Desenhar círculo de folhagem
                superficie_folha = pygame.Surface((raio_circulo * 2, raio_circulo * 2), SRCALPHA)
                pygame.draw.circle(superficie_folha, cor_camada,
                                 (raio_circulo, raio_circulo), raio_circulo)

                # Aplicar na superfície principal
                pos_x = max(0, min(self.largura - raio_circulo * 2, cx - raio_circulo))
                pos_y = max(0, min(self.altura - raio_circulo * 2, cy - raio_circulo))
                self.image.blit(superficie_folha, (pos_x, pos_y))  # Adicionar detalhes de textura
        for _ in range(15):
            x = random.randint(10, self.largura - 10)
            y = random.randint(10, self.altura - 10)
            tamanho = random.randint(2, 4)

            # Gerar cor de detalhe garantindo valores válidos
            r = max(0, min(255, self.cor_escura[0] + random.randint(-20, 20)))
            g = max(0, min(255, self.cor_escura[1] + random.randint(-20, 20)))
            b = max(0, min(255, self.cor_escura[2] + random.randint(-20, 20)))
            cor_detalhe = (r, g, b, 150)

            pygame.draw.circle(self.image, cor_detalhe, (x, y), tamanho)

    def update(self, dt, efeito_vento=None):
        """Atualizar animação do arbusto"""
        self.tempo_animacao += dt

        # Aplicar efeito de vento se disponível
        if efeito_vento:
            self.balanco_x, self.balanco_y = EfeitoVentoArbustos.aplicar_balanco(self, efeito_vento)
        else:
            # Animação padrão suave
            self.balanco_x = math.sin(self.tempo_animacao * 0.5 + self.pos_x * 0.01) * self.intensidade_animacao * 2
            self.balanco_y = math.cos(self.tempo_animacao * 0.3 + self.pos_y * 0.01) * self.intensidade_animacao * 1

        # Animação sutil de movimento (simulando vento)
        # Isso é apenas visual, não afeta a hitbox

    def verificar_entidade_dentro(self, entidade):
        """Verificar se uma entidade está dentro do arbusto"""
        # Verificar colisão com um pouco de margem
        margem = 10
        arbusto_rect = pygame.Rect(
            self.rect.x + margem,
            self.rect.y + margem,
            self.rect.width - margem * 2,
            self.rect.height - margem * 2
        )

        entidade_rect = pygame.Rect(
            entidade.pos_x - 15, entidade.pos_y - 15, 30, 30
        )

        return arbusto_rect.colliderect(entidade_rect)

    def adicionar_entidade(self, entidade):
        """Adicionar entidade à lista de entidades dentro do arbusto"""
        self.entidades_dentro.add(entidade)

    def remover_entidade(self, entidade):
        """Remover entidade da lista de entidades dentro do arbusto"""
        self.entidades_dentro.discard(entidade)

    def entidade_esta_escondida(self, entidade):
        """Verificar se a entidade está escondida no arbusto"""
        return entidade in self.entidades_dentro

    def draw(self, screen, camera_offset=(0, 0)):
        """Desenhar o arbusto na tela"""
        # Calcular posição na tela com efeito de balanço
        balanco_x = getattr(self, 'balanco_x', 0)
        balanco_y = getattr(self, 'balanco_y', 0)

        screen_x = self.rect.x - camera_offset[0] + balanco_x
        screen_y = self.rect.y - camera_offset[1] + balanco_y

        # Só desenhar se estiver visível na tela
        if (-100 <= screen_x <= SCREEN_WIDTH + 100 and
            -100 <= screen_y <= SCREEN_HEIGHT + 100):

            # Animação sutil de "respiração"
            escala = 1.0 + math.sin(self.tempo_animacao) * self.intensidade_animacao

            if abs(escala - 1.0) > 0.01:  # Só escalar se necessário
                largura_scaled = int(self.largura * escala)
                altura_scaled = int(self.altura * escala)
                image_scaled = pygame.transform.scale(self.image, (largura_scaled, altura_scaled))

                # Centralizar a imagem escalada
                pos_x = screen_x + (self.largura - largura_scaled) // 2
                pos_y = screen_y + (self.altura - altura_scaled) // 2
                screen.blit(image_scaled, (pos_x, pos_y))
            else:
                screen.blit(self.image, (screen_x, screen_y))


class GerenciadorArbustos:
    """Gerenciador principal do sistema de arbustos"""

    def __init__(self, largura_mapa=SCREEN_WIDTH, altura_mapa=SCREEN_HEIGHT):
        self.arbustos = pygame.sprite.Group()
        self.mapa_visibilidade = {}  # Cache de visibilidade
        self.largura_mapa = largura_mapa
        self.altura_mapa = altura_mapa

    def gerar_arbustos_aleatorios(self, quantidade=8):
        """Gerar arbustos em posições estratégicas do mapa"""
        self.arbustos.empty()        # Definir áreas onde arbustos podem aparecer (evitar bordas)
        margem = 100

        # Gerar arbustos com espaçamento mínimo
        arbustos_gerados = []
        tentativas = 0

        while len(arbustos_gerados) < quantidade and tentativas < 100:
            x = random.randint(margem, SCREEN_WIDTH - margem)
            y = random.randint(margem, SCREEN_HEIGHT - margem)

            # Verificar distância mínima de outros arbustos
            muito_proximo = False
            for arbusto_pos in arbustos_gerados:
                dist = math.sqrt((x - arbusto_pos[0])**2 + (y - arbusto_pos[1])**2)
                if dist < 120:  # Distância mínima entre arbustos
                    muito_proximo = True
                    break

            if not muito_proximo:
                # Tamanho variável dos arbustos
                largura = random.randint(70, 100)
                altura = random.randint(70, 100)

                arbusto = Arbusto(x, y, largura, altura)
                self.arbustos.add(arbusto)
                arbustos_gerados.append((x, y))

            tentativas += 1

    def gerar_arbustos_estrategicos(self, obstaculos=None):
        """Gerar arbustos em posições estratégicas como no Brawl Stars"""
        if obstaculos is None:
            obstaculos = []

        self.arbustos.empty()

        # Padrão inspirado nos mapas do Brawl Stars
        # Centro do mapa
        centro_x, centro_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

        # Muito mais arbustos para o mapa maior
        posicoes_candidatas = [
            # Arbustos centrais (área de gemas)
            (centro_x - 120, centro_y - 120),
            (centro_x + 120, centro_y - 120),
            (centro_x - 120, centro_y + 120),
            (centro_x + 120, centro_y + 120),
            (centro_x - 200, centro_y),
            (centro_x + 200, centro_y),
            (centro_x, centro_y - 150),
            (centro_x, centro_y + 150),

            # Arbustos nas laterais para flanqueamento
            (300, centro_y - 200),
            (300, centro_y + 200),
            (SCREEN_WIDTH - 300, centro_y - 200),
            (SCREEN_WIDTH - 300, centro_y + 200),

            # Arbustos superiores e inferiores
            (centro_x - 300, 200),
            (centro_x + 300, 200),
            (centro_x - 300, SCREEN_HEIGHT - 200),
            (centro_x + 300, SCREEN_HEIGHT - 200),

            # Arbustos nas bordas
            (150, 300),
            (150, SCREEN_HEIGHT - 300),
            (SCREEN_WIDTH - 150, 300),
            (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 300),

            # Arbustos adicionais para mais cobertura
            (centro_x - 400, centro_y - 300),
            (centro_x + 400, centro_y - 300),
            (centro_x - 400, centro_y + 300),
            (centro_x + 400, centro_y + 300),
        ]

        # Gerar arbustos aleatórios adicionais
        for _ in range(8):  # Reduzido de 15 para 8 arbustos extras
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            posicoes_candidatas.append((x, y))

        # Filtrar posições que não colidem com obstáculos
        for x, y in posicoes_candidatas:
            # Verificar se não está muito próximo de obstáculos
            posicao_valida = True
            for obstaculo in obstaculos:
                dist = math.sqrt((x - obstaculo.rect.centerx)**2 + (y - obstaculo.rect.centery)**2)
                if dist < 80:  # Distância mínima reduzida de obstáculos
                    posicao_valida = False
                    break

            # Verificar distância de outros arbustos
            if posicao_valida:
                for arbusto in self.arbustos:
                    dist = math.sqrt((x - arbusto.pos_x)**2 + (y - arbusto.pos_y)**2)
                    if dist < 90:  # Distância mínima entre arbustos
                        posicao_valida = False
                        break

            if posicao_valida:
                tamanho = random.randint(60, 100)  # Tamanhos mais variados
                arbusto = Arbusto(x, y, tamanho, tamanho)
                self.arbustos.add(arbusto)

    def atualizar(self, dt, entidades, efeito_vento=None):
        """Atualizar sistema de arbustos"""
        # Atualizar animações dos arbustos com efeito de vento
        for arbusto in self.arbustos:
            arbusto.update(dt, efeito_vento)

        # Verificar quais entidades estão em arbustos
        self._atualizar_visibilidade(entidades)

    def _atualizar_visibilidade(self, entidades):
        """Atualizar sistema de visibilidade nos arbustos"""
        # Limpar listas anteriores
        for arbusto in self.arbustos:
            arbusto.entidades_dentro.clear()

        # Verificar todas as entidades
        for entidade in entidades:
            for arbusto in self.arbustos:
                if arbusto.verificar_entidade_dentro(entidade):
                    arbusto.adicionar_entidade(entidade)

    def entidade_esta_escondida(self, entidade):
        """Verificar se uma entidade está escondida em algum arbusto"""
        for arbusto in self.arbustos:
            if arbusto.entidade_esta_escondida(entidade):
                return True
        return False

    def pode_ver_entidade(self, observador, alvo):
        """Verificar se o observador pode ver o alvo (considerando arbustos)"""
        # Se o alvo estiver em um arbusto, reduzir alcance de visão
        if self.entidade_esta_escondida(alvo):
            # Calcular distância
            dx = alvo.pos_x - observador.pos_x
            dy = alvo.pos_y - observador.pos_y
            distancia = math.sqrt(dx*dx + dy*dy)

            # Se estiver muito próximo, ainda pode ver
            return distancia < 60  # Alcance reduzido para ver entidades escondidas

        return True  # Pode ver normalmente se não estiver escondido

    def obter_cobertura_para_posicao(self, x, y):
        """Obter nível de cobertura para uma posição específica"""
        for arbusto in self.arbustos:
            if arbusto.rect.collidepoint(x, y):
                return arbusto.densidade
        return 0.0

    def draw(self, screen, camera_offset=(0, 0)):
        """Desenhar todos os arbustos"""
        for arbusto in self.arbustos:
            arbusto.draw(screen, camera_offset)

    def draw_debug_info(self, screen, font):
        """Desenhar informações de debug sobre os arbustos"""
        y_offset = 10
        for i, arbusto in enumerate(self.arbustos):
            info = f"Arbusto {i}: {len(arbusto.entidades_dentro)} entidades"
            text = font.render(info, True, (255, 255, 255))
            screen.blit(text, (10, y_offset))
            y_offset += 20

    def limpar_arbustos(self):
        """Limpar todos os arbustos"""
        self.arbustos.clear()

    def entidade_esta_em_arbusto(self, entidade):
        """Verificar se uma entidade específica está dentro de algum arbusto"""
        for arbusto in self.arbustos:
            if entidade in arbusto.entidades_dentro:
                return True
        return False

    def desenhar(self, screen):
        """Método de conveniência para desenhar (compatibilidade com game.py)"""
        self.draw(screen)
