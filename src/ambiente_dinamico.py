"""
Sistema de Ambiente Dinâmico do Brawl Stars Clone.
Este módulo implementa efeitos ambientais como arbustos que balançam,
sombras realistas, efeitos específicos por mapa e transições dia/noite.
Adiciona vida e imersão ao ambiente de jogo.
"""

import math
import random
import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.pygame_constants import SRCALPHA, K_LEFT, K_RIGHT
from src.config_ambiente import (
    CICLO_DIA_DURACAO, TRANSICAO_ATIVA_PADRAO, INTENSIDADE_SOMBRA_PADRAO,
    INTENSIDADE_VENTO_BASE, DEBUG_ATIVO_PADRAO, MOSTRAR_INFO_DEBUG_PADRAO,
    CONTROLE_MANUAL_TEMPO_PADRAO, CORES_AMBIENTE, EFEITOS_MAPA_CONFIG
)

class GerenciadorAmbiente:
    """Gerenciador principal do sistema de ambiente dinâmico"""
    def __init__(self, largura_mapa=SCREEN_WIDTH, altura_mapa=SCREEN_HEIGHT):
        self.largura_mapa = largura_mapa
        self.altura_mapa = altura_mapa

        # Sistema de iluminação
        self.tempo_dia = 0.0  # 0.0 = meia-noite, 0.5 = meio-dia
        self.ciclo_dia_duracao = CICLO_DIA_DURACAO
        self.transicao_ativa = TRANSICAO_ATIVA_PADRAO

        # Sistema de sombras
        self.angulo_sol = 0.0  # Ângulo do sol para cálculo de sombras
        self.intensidade_sombra = INTENSIDADE_SOMBRA_PADRAO

        # Efeitos de vento para arbustos
        self.intensidade_vento = INTENSIDADE_VENTO_BASE
        self.direcao_vento = 0.0  # Radianos
        self.tempo_vento = 0.0

        # Partículas ambientais
        self.particulas_ambiente = []
        self.ultimo_spawn_particula = 0.0

        # Sistema de clima
        self.clima_atual = "limpo"  # limpo, chuva, neve, tempestade
        self.particulas_clima = []
        self.tempo_mudanca_clima = 0.0

        # Tipos de mapa e efeitos específicos
        self.tipo_mapa = "cidade"  # cidade, deserto, floresta, gelo
        self.efeitos_mapa = {}
        self._configurar_efeitos_mapa()

        # Overlay de iluminação
        self.overlay_iluminacao = pygame.Surface((largura_mapa, altura_mapa), SRCALPHA)

        # Controles de debug
        self.debug_ativo = DEBUG_ATIVO_PADRAO
        self.mostrar_info_debug = MOSTRAR_INFO_DEBUG_PADRAO
        self.controle_manual_tempo = CONTROLE_MANUAL_TEMPO_PADRAO

    def atualizar(self, dt):
        """Atualizar todos os sistemas ambientais"""
        self._atualizar_ciclo_dia_noite(dt)
        self._atualizar_vento(dt)
        self._atualizar_particulas_ambiente(dt)
        self._atualizar_clima(dt)
        self._calcular_angulo_sol()
        self._atualizar_overlay_iluminacao()

    def _configurar_efeitos_mapa(self):
        """Configurar efeitos específicos por tipo de mapa"""
        self.efeitos_mapa = {}
        for tipo_mapa, config in EFEITOS_MAPA_CONFIG.items():
            self.efeitos_mapa[tipo_mapa] = {
                "cor_ambiente_dia": CORES_AMBIENTE[tipo_mapa]["dia"],
                "cor_ambiente_noite": CORES_AMBIENTE[tipo_mapa]["noite"],
                "cor_ambiente_amanhecer": CORES_AMBIENTE[tipo_mapa]["amanhecer"],
                "cor_ambiente_entardecer": CORES_AMBIENTE[tipo_mapa]["entardecer"],
                "particulas_base": config["particulas_base"],
                "intensidade_vento_base": config["intensidade_vento_base"],
                "som_ambiente": config["som_ambiente"],
                "climas_permitidos": config["climas_permitidos"]
            }

    def _atualizar_ciclo_dia_noite(self, dt):
        """Atualizar ciclo dia/noite"""
        if self.transicao_ativa:
            self.tempo_dia += dt / self.ciclo_dia_duracao
            if self.tempo_dia > 1.0:
                self.tempo_dia = 0.0

    def _atualizar_vento(self, dt):
        """Atualizar sistema de vento"""
        self.tempo_vento += dt

        # Vento oscila suavemente
        self.intensidade_vento = 0.3 + 0.4 * math.sin(self.tempo_vento * 0.5)
        self.direcao_vento = math.sin(self.tempo_vento * 0.2) * 0.3

    def _atualizar_particulas_ambiente(self, dt):
        """Atualizar partículas ambientais (folhas, poeira, etc)"""
        self.ultimo_spawn_particula += dt

        # Spawnar nova partícula ocasionalmente
        if self.ultimo_spawn_particula > random.uniform(2.0, 5.0):
            self._criar_particula_folha()
            self.ultimo_spawn_particula = 0.0

        # Atualizar partículas existentes
        for particula in self.particulas_ambiente[:]:
            particula.atualizar(dt)
            if particula.deve_remover():
                self.particulas_ambiente.remove(particula)

    def _criar_particula_folha(self):
        """Criar partícula de folha voando"""
        x = random.randint(-50, self.largura_mapa + 50)
        y = random.randint(-50, self.altura_mapa + 50)

        # Escolher lado da tela para spawn
        lado = random.choice(['esquerda', 'direita', 'cima', 'baixo'])
        if lado == 'esquerda':
            x = -20
        elif lado == 'direita':
            x = self.largura_mapa + 20
        elif lado == 'cima':
            y = -20
        else:
            y = self.altura_mapa + 20
        particula = ParticulaFolha(x, y, self.direcao_vento, self.intensidade_vento)
        self.particulas_ambiente.append(particula)

    def _calcular_angulo_sol(self):
        """Calcular ângulo do sol baseado no tempo do dia"""
        # Sol nasce no leste (0°), meio-dia no sul (90°), poente no oeste (180°)
        self.angulo_sol = self.tempo_dia * math.pi * 2

    def _atualizar_overlay_iluminacao(self):
        """Atualizar overlay de iluminação para simular dia/noite"""
        self.overlay_iluminacao.fill((0, 0, 0, 0))

        # Calcular cor ambiente baseada no tempo
        if self.tempo_dia < 0.25:  # Noite -> Amanhecer
            progress = self.tempo_dia / 0.25
            # Noite mais clara: azul menos escuro
            cor_ambiente = self._interpolar_cor((45, 45, 80), (100, 80, 50), progress)
            # Alpha reduzido para noite menos escura
            alpha = int(120 - progress * 90)
        elif self.tempo_dia < 0.5:  # Amanhecer -> Meio-dia
            progress = (self.tempo_dia - 0.25) / 0.25
            cor_ambiente = self._interpolar_cor((100, 80, 50), (255, 255, 240), progress)
            alpha = int(30 - progress * 30)
        elif self.tempo_dia < 0.75:  # Meio-dia -> Entardecer
            progress = (self.tempo_dia - 0.5) / 0.25
            cor_ambiente = self._interpolar_cor((255, 255, 240), (200, 100, 60), progress)
            alpha = int(progress * 60)
        else:  # Entardecer -> Noite
            progress = (self.tempo_dia - 0.75) / 0.25
            # Noite mais clara
            cor_ambiente = self._interpolar_cor((200, 100, 60), (45, 45, 80), progress)
            alpha = int(60 + progress * 60)

        # Aplicar overlay se houver transparência
        if alpha > 0:
            overlay_temp = pygame.Surface((self.largura_mapa, self.altura_mapa), SRCALPHA)
            overlay_temp.fill((*cor_ambiente, alpha))
            self.overlay_iluminacao.blit(overlay_temp, (0, 0))

    def _interpolar_cor(self, cor1, cor2, t):
        """Interpolar entre duas cores"""
        return (
            int(cor1[0] + (cor2[0] - cor1[0]) * t),
            int(cor1[1] + (cor2[1] - cor1[1]) * t),
            int(cor1[2] + (cor2[2] - cor1[2]) * t)
        )

    def calcular_sombra_objeto(self, x, y, largura, altura):
        """Calcular posição e tamanho da sombra de um objeto"""
        # Calcular offset da sombra baseado no ângulo do sol
        offset_x = math.cos(self.angulo_sol) * 10 * self.intensidade_sombra
        offset_y = math.sin(self.angulo_sol) * 5 * self.intensidade_sombra

        # Posição da sombra
        sombra_x = x + offset_x
        sombra_y = y + offset_y

        # Tamanho da sombra (ligeiramente menor que o objeto)
        sombra_largura = largura * 0.8
        sombra_altura = altura * 0.6
        return sombra_x, sombra_y, sombra_largura, sombra_altura

    def obter_efeito_vento(self):
        """Obter efeito atual do vento para arbustos"""
        return {
            'intensidade': self.intensidade_vento,
            'direcao': self.direcao_vento,
            'tempo': self.tempo_vento
        }

    def obter_info_iluminacao(self):
        """Obter informações da iluminação atual"""
        if self.tempo_dia < 0.25 or self.tempo_dia > 0.75:
            periodo = "noite"
        elif self.tempo_dia < 0.5:
            periodo = "amanhecer"
        else:
            periodo = "dia"

        return {
            'periodo': periodo,
            'tempo_dia': self.tempo_dia,
            'angulo_sol': self.angulo_sol,
            'intensidade_sombra': self.intensidade_sombra
        }

    def desenhar_sombras(self, screen, objetos):
        """Desenhar sombras de objetos"""
        for obj in objetos:
            if hasattr(obj, 'rect'):
                sombra_x, sombra_y, sombra_w, sombra_h = self.calcular_sombra_objeto(
                    obj.rect.x, obj.rect.y, obj.rect.width, obj.rect.height
                )
                # Criar superfície de sombra com transparência
                sombra_surface = pygame.Surface((sombra_w, sombra_h), SRCALPHA)
                pygame.draw.ellipse(sombra_surface, (0, 0, 0, 80),
                                  (0, 0, sombra_w, sombra_h))
                screen.blit(sombra_surface, (sombra_x, sombra_y))

    def desenhar_particulas_ambiente(self, screen):
        """Desenhar partículas ambientais"""
        for particula in self.particulas_ambiente:
            particula.desenhar(screen)

    def desenhar_particulas_clima(self, screen):
        """Desenhar partículas de clima"""
        for particula in self.particulas_clima:
            particula.desenhar(screen)

    def aplicar_overlay_iluminacao(self, screen):
        """Aplicar overlay de iluminação à tela"""
        screen.blit(self.overlay_iluminacao, (0, 0))

    def alternar_debug(self):
        """Alternar modo debug"""
        self.debug_ativo = not self.debug_ativo
        self.mostrar_info_debug = self.debug_ativo
        return self.debug_ativo

    def alternar_transicao_dia_noite(self):
        """Alternar sistema de transição dia/noite"""
        self.transicao_ativa = not self.transicao_ativa
        return self.transicao_ativa

    def desenhar_info_debug(self, screen, fonte):
        """Desenhar informações de debug na tela"""
        if not self.mostrar_info_debug:
            return

        info_lines = [
            f"Tempo do Dia: {self.tempo_dia:.2f}",
            f"Período: {self.obter_info_iluminacao()['periodo']}",
            f"Clima: {self.clima_atual}",
            f"Vento: {self.intensidade_vento:.2f}",
            f"Partículas Ambiente: {len(self.particulas_ambiente)}",
            f"Partículas Clima: {len(self.particulas_clima)}",
            f"Tipo Mapa: {self.tipo_mapa}",
            f"Transição Ativa: {self.transicao_ativa}"
        ]

        y_offset = 10
        for line in info_lines:
            text_surface = fonte.render(line, True, (255, 255, 255))
            # Fundo preto para melhor legibilidade
            bg_rect = text_surface.get_rect()
            bg_rect.x = 10
            bg_rect.y = y_offset
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
            screen.blit(text_surface, (10, y_offset))
            y_offset += 20

    def processar_input_debug(self, teclas):
        """Processar input para controles de debug"""
        if not self.debug_ativo:
            return
        # Controle manual do tempo
        if teclas[K_LEFT]:
            self.tempo_dia = (self.tempo_dia - 0.01) % 1.0
            self.controle_manual_tempo = True
        elif teclas[K_RIGHT]:
            self.tempo_dia = (self.tempo_dia + 0.01) % 1.0
            self.controle_manual_tempo = True

    def mudar_tipo_mapa(self, novo_tipo):
        """Mudar tipo de mapa"""
        if novo_tipo in self.efeitos_mapa:
            self.tipo_mapa = novo_tipo
            # Limpar partículas para reiniciar com novo estilo
            self.particulas_ambiente.clear()
            self.particulas_clima.clear()

    def forcar_clima(self, clima):
        """Forçar clima específico (para debug)"""
        if clima in ["limpo", "chuva", "neve", "tempestade"]:
            self.clima_atual = clima
            self.particulas_clima.clear()

    def _atualizar_clima(self, dt):
        """Atualizar sistema de clima"""
        self.tempo_mudanca_clima += dt

        # Mudança de clima ocasional
        if self.tempo_mudanca_clima > random.uniform(30.0, 60.0):
            self._mudar_clima()
            self.tempo_mudanca_clima = 0.0

        # Atualizar partículas de clima
        self._atualizar_particulas_clima(dt)

    def _mudar_clima(self):
        """Mudar clima aleatoriamente"""
        climas_disponiveis = ["limpo", "chuva", "neve", "tempestade"]

        # Filtrar climas baseado no tipo de mapa
        if self.tipo_mapa == "deserto":
            climas_disponiveis = ["limpo", "tempestade"]
        elif self.tipo_mapa == "gelo":
            climas_disponiveis = ["limpo", "neve"]

        # Chance maior de ficar limpo
        if random.random() < 0.6:
            novo_clima = "limpo"
        else:
            novo_clima = random.choice([c for c in climas_disponiveis if c != "limpo"])

        if novo_clima != self.clima_atual:
            self.clima_atual = novo_clima

    def _atualizar_particulas_clima(self, dt):
        """Atualizar partículas de clima (chuva, neve, etc)"""
        # Remover partículas antigas
        self.particulas_clima = [p for p in self.particulas_clima if not p.deve_remover()]

        # Adicionar novas partículas baseado no clima
        if self.clima_atual == "chuva":
            self._criar_particulas_chuva()
        elif self.clima_atual == "neve":
            self._criar_particulas_neve()
        elif self.clima_atual == "tempestade":
            self._criar_particulas_tempestade()

        # Atualizar partículas existentes
        for particula in self.particulas_clima:
            particula.atualizar(dt)

    def _criar_particulas_chuva(self):
        """Criar partículas de chuva"""
        if len(self.particulas_clima) < 100:
            for _ in range(5):
                x = random.randint(-20, self.largura_mapa + 20)
                y = -10
                particula = ParticulaChuva(x, y)
                self.particulas_clima.append(particula)

    def _criar_particulas_neve(self):
        """Criar partículas de neve"""
        if len(self.particulas_clima) < 80:
            for _ in range(3):
                x = random.randint(-20, self.largura_mapa + 20)
                y = -10
                particula = ParticulaNeve(x, y, self.intensidade_vento)
                self.particulas_clima.append(particula)

    def _criar_particulas_tempestade(self):
        """Criar partículas de tempestade"""
        if len(self.particulas_clima) < 120:
            for _ in range(8):
                x = random.randint(-50, self.largura_mapa + 50)
                y = -10
                particula = ParticulaTempestade(x, y, self.intensidade_vento)
                self.particulas_clima.append(particula)

class ParticulaFolha:
    """Partícula de folha voando pelo ambiente"""
    def __init__(self, x, y, direcao_vento, intensidade_vento):
        self.x = float(x)
        self.y = float(y)
        self.vel_x = random.uniform(-30, 30) + math.cos(direcao_vento) * intensidade_vento * 20
        self.vel_y = random.uniform(10, 40) + math.sin(direcao_vento) * intensidade_vento * 10

        # Propriedades visuais
        self.tamanho = random.randint(3, 7)
        self.cor = random.choice([
            (139, 69, 19),   # Marrom
            (160, 82, 45),   # Marrom claro
            (205, 133, 63),  # Peru
            (210, 180, 140), # Tan
            (34, 139, 34),   # Verde floresta
        ])

        # Animação
        self.rotacao = random.uniform(0, math.pi * 2)
        self.vel_rotacao = random.uniform(-2, 2)
        self.vida = random.uniform(8.0, 15.0)
        self.vida_maxima = self.vida

        # Movimento oscilante
        self.oscilacao_tempo = random.uniform(0, math.pi * 2)
        self.oscilacao_amplitude = random.uniform(10, 20)

    def atualizar(self, dt):
        """Atualizar partícula"""
        # Movimento principal
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

        # Oscilação lateral
        self.oscilacao_tempo += dt * 2
        oscilacao_x = math.sin(self.oscilacao_tempo) * self.oscilacao_amplitude * dt
        self.x += oscilacao_x

        # Rotação
        self.rotacao += self.vel_rotacao * dt

        # Reduzir vida
        self.vida -= dt

        # Gravidade suave
        self.vel_y += 20 * dt

    def desenhar(self, screen):
        """Desenhar partícula"""
        if self.vida <= 0:
            return

        # Calcular alpha baseado na vida restante
        alpha = int(255 * (self.vida / self.vida_maxima))
        alpha = max(0, min(255, alpha))

        # Criar superfície rotacionada
        size = self.tamanho * 2
        surface = pygame.Surface((size, size), SRCALPHA)

        # Desenhar folha como elipse rotacionada
        cor_com_alpha = (*self.cor, alpha)
        pygame.draw.ellipse(surface, cor_com_alpha, (0, 0, size, size//2))

        # Rotacionar
        if self.rotacao != 0:
            surface = pygame.transform.rotate(surface, math.degrees(self.rotacao))

        # Desenhar na tela
        rect = surface.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(surface, rect)

    def deve_remover(self):
        """Verificar se partícula deve ser removida"""
        return (self.vida <= 0 or
                self.x < -100 or self.x > SCREEN_WIDTH + 100 or
                self.y < -100 or self.y > SCREEN_HEIGHT + 100)


class EfeitoVentoArbustos:
    """Efeito de vento específico para arbustos"""
    @staticmethod
    def aplicar_balanco(arbusto, efeito_vento):
        """Aplicar efeito de balanço do vento em um arbusto"""
        if not hasattr(arbusto, 'tempo_animacao'):
            return

        intensidade = efeito_vento['intensidade']
        direcao = efeito_vento['direcao']
        tempo = efeito_vento['tempo']

        # Calcular offset de balanço
        balanco_x = math.sin(tempo * 2 + arbusto.pos_x * 0.01) * intensidade * 3
        balanco_y = math.cos(tempo * 1.5 + arbusto.pos_y * 0.01) * intensidade * 1.5

        # Aplicar direção do vento
        balanco_x += math.cos(direcao) * intensidade * 2
        balanco_y += math.sin(direcao) * intensidade * 1
        return balanco_x, balanco_y

    @staticmethod
    def calcular_intensidade_balanco(distancia_do_centro, intensidade_vento):
        """Calcular intensidade do balanço baseado na distância do centro da tela"""
        # Arbustos mais próximos das bordas balançam mais
        fator_borda = min(1.0, distancia_do_centro / 200.0)
        return intensidade_vento * (0.5 + fator_borda * 0.5)

class ParticulaChuva:
    """Partícula de chuva"""
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vel_x = random.uniform(-5, 5)
        self.vel_y = random.uniform(200, 400)
        self.vida = 3.0

    def atualizar(self, dt):
        """Atualizar partícula de chuva"""
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.vida -= dt

    def desenhar(self, screen):
        """Desenhar gota de chuva"""
        if self.vida > 0:
            pygame.draw.line(screen, (180, 200, 255),
                           (int(self.x), int(self.y)),
                           (int(self.x - self.vel_x * 0.02), int(self.y - 10)), 2)

    def deve_remover(self):
        return self.vida <= 0 or self.y > SCREEN_HEIGHT + 50


class ParticulaNeve:
    """Partícula de neve"""
    def __init__(self, x, y, intensidade_vento):
        self.x = float(x)
        self.y = float(y)
        self.vel_x = random.uniform(-20, 20) + intensidade_vento * 10
        self.vel_y = random.uniform(30, 80)
        self.tamanho = random.randint(2, 5)
        self.vida = 8.0
        self.oscilacao = random.uniform(0, math.pi * 2)

    def atualizar(self, dt):
        """Atualizar partícula de neve"""
        self.oscilacao += dt * 2
        oscilacao_x = math.sin(self.oscilacao) * 15
        self.x += (self.vel_x + oscilacao_x) * dt
        self.y += self.vel_y * dt
        self.vida -= dt

    def desenhar(self, screen):
        """Desenhar floco de neve"""
        if self.vida > 0:
            pygame.draw.circle(screen, (255, 255, 255),
                             (int(self.x), int(self.y)), self.tamanho)

    def deve_remover(self):
        return self.vida <= 0 or self.y > SCREEN_HEIGHT + 50


class ParticulaTempestade:
    """Partícula de tempestade (chuva intensa com vento)"""
    def __init__(self, x, y, intensidade_vento):
        self.x = float(x)
        self.y = float(y)
        self.vel_x = random.uniform(-50, 50) + intensidade_vento * 30
        self.vel_y = random.uniform(300, 600)
        self.vida = 2.0
        self.alpha = random.randint(150, 255)

    def atualizar(self, dt):
        """Atualizar partícula de tempestade"""
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.vida -= dt
        # Fade out
        self.alpha = int(255 * (self.vida / 2.0))

    def desenhar(self, screen):
        """Desenhar chuva de tempestade"""
        if self.vida > 0 and self.alpha > 0:
            cor = (150, 180, 255, max(0, self.alpha))
            start_pos = (int(self.x), int(self.y))
            end_pos = (int(self.x - self.vel_x * 0.03), int(self.y - 15))

            # Criar superfície temporária para alpha
            temp_surface = pygame.Surface((abs(end_pos[0] - start_pos[0]) + 10,
                                         abs(end_pos[1] - start_pos[1]) + 10), SRCALPHA)
            pygame.draw.line(temp_surface, cor, (5, 5), (5, 20), 3)
            screen.blit(temp_surface, (start_pos[0] - 5, start_pos[1] - 5))

    def deve_remover(self):
        return self.vida <= 0 or self.y > SCREEN_HEIGHT + 50
