"""
Sistema de animação 3D para personagens do Brawl Stars Clone.
Gerencia animações de movimento, idle, ataque e expressões faciais.
"""

import math
import pygame

class AnimadorPersonagem3D:
    """Gerencia animações para renderização 3D de personagens"""

    def __init__(self):
        self.tempo_animacao = 0.0
        self.velocidade_animacao = 1.0
        self.estado_animacao = "idle"  # idle, andando, atacando
        self.ultimo_movimento_x = 0
        self.ultimo_movimento_y = 0

    def atualizar(self, dt, velocidade_x=0, velocidade_y=0, atacando=False):
        """Atualizar estado da animação"""
        self.tempo_animacao += dt * self.velocidade_animacao

        # Determinar estado baseado no movimento
        if atacando:
            self.estado_animacao = "atacando"
        elif abs(velocidade_x) > 10 or abs(velocidade_y) > 10:
            self.estado_animacao = "andando"
        else:
            self.estado_animacao = "idle"

        self.ultimo_movimento_x = velocidade_x
        self.ultimo_movimento_y = velocidade_y

    def obter_offset_braco_esquerdo(self):
        """Calcular offset do braço esquerdo baseado na animação"""
        if self.estado_animacao == "andando":
            # Movimento de balanço durante caminhada
            balanco = math.sin(self.tempo_animacao * 6) * 3
            return (balanco, math.cos(self.tempo_animacao * 6) * 2)
        if self.estado_animacao == "atacando":
            # Movimento de ataque
            fase_ataque = (self.tempo_animacao * 8) % (2 * math.pi)
            if fase_ataque < math.pi:
                return (math.sin(fase_ataque) * 8, -math.cos(fase_ataque) * 4)
            else:
                return (0, 0)
        else:
            # Idle - respiração sutil
            respiracao = math.sin(self.tempo_animacao * 2) * 1
            return (0, respiracao)

    def obter_offset_braco_direito(self):
        """Calcular offset do braço direito (oposto ao esquerdo)"""
        offset_esq = self.obter_offset_braco_esquerdo()
        if self.estado_animacao == "andando":
            return (-offset_esq[0], offset_esq[1])
        elif self.estado_animacao == "atacando":
            # Braço direito segura a arma
            fase_ataque = (self.tempo_animacao * 8) % (2 * math.pi)
            if fase_ataque < math.pi:
                return (math.sin(fase_ataque) * 12, -math.cos(fase_ataque) * 6)
            else:
                return (0, 0)
        else:
            return (offset_esq[0], offset_esq[1])

    def obter_offset_perna_esquerda(self):
        """Calcular offset da perna esquerda"""
        if self.estado_animacao == "andando":
            # Movimento de caminhada
            passo = math.sin(self.tempo_animacao * 5) * 4
            return (passo, abs(math.cos(self.tempo_animacao * 5)) * 2)
        else:
            return (0, 0)

    def obter_offset_perna_direita(self):
        """Calcular offset da perna direita (oposta à esquerda)"""
        offset_esq = self.obter_offset_perna_esquerda()
        if self.estado_animacao == "andando":
            return (-offset_esq[0], offset_esq[1])
        else:
            return (0, 0)

    def obter_rotacao_cabeca(self):
        """Calcular rotação da cabeça baseada no movimento"""
        if self.ultimo_movimento_x != 0:
            # Virar cabeça na direção do movimento
            return math.atan2(self.ultimo_movimento_y, self.ultimo_movimento_x) * 0.1
        return 0

    def obter_expressao_facial(self):
        """Calcular expressão facial atual"""
        if self.estado_animacao == "atacando":
            return "determinado"
        elif self.estado_animacao == "andando":
            return "focado"
        else:
            return "normal"

    def obter_piscada(self):
        """Calcular se deve piscar"""
        # Piscar a cada 3-4 segundos aproximadamente
        ciclo_piscada = self.tempo_animacao % 3.5
        return 3.2 < ciclo_piscada < 3.4

    def obter_balanco_corpo(self):
        """Calcular balanço sutil do corpo"""
        if self.estado_animacao == "andando":
            return math.sin(self.tempo_animacao * 5) * 2
        else:
            # Respiração idle
            return math.sin(self.tempo_animacao * 1.5) * 0.5

class UtilsFormasOrganicas:
    """Utilidades para criar formas mais orgânicas e naturais"""

    @staticmethod
    def desenhar_elipse_organica(superficie, cor, rect, variacao=0.1):
        """Desenha uma elipse com bordas mais orgânicas"""
        # Criar vários pontos ao redor da elipse com pequenas variações
        centro_x = rect.centerx
        centro_y = rect.centery
        raio_x = rect.width // 2
        raio_y = rect.height // 2
        pontos = []

        # Usar mais pontos para suavidade máxima e variação mais complexa
        num_pontos = 24  # Aumentado de 16 para 24 para mais suavidade
        for i in range(num_pontos):
            angulo = (i / num_pontos) * 2 * math.pi

            # Variação complexa usando múltiplas frequências para criar formato natural
            variacao_base = 1.0 + (math.sin(angulo * 3) * variacao)
            variacao_extra = 1.0 + (math.sin(angulo * 7) * variacao * 0.3)
            variacao_micro = 1.0 + (math.cos(angulo * 11) * variacao * 0.1)

            variacao_final = variacao_base * variacao_extra * variacao_micro

            x = centro_x + math.cos(angulo) * raio_x * variacao_final
            y = centro_y + math.sin(angulo) * raio_y * variacao_final
            pontos.append((int(x), int(y)))

        if len(pontos) >= 3:
            pygame.draw.polygon(superficie, cor, pontos)
            # Adicionar anti-aliasing simples desenhando uma versão levemente menor
            if variacao > 0.05:  # Só para formas com variação significativa
                pontos_aa = []
                for i in range(num_pontos):
                    angulo = (i / num_pontos) * 2 * math.pi
                    variacao_aa = 0.95  # Levemente menor para suavizar bordas
                    x = centro_x + math.cos(angulo) * raio_x * variacao_aa
                    y = centro_y + math.sin(angulo) * raio_y * variacao_aa
                    pontos_aa.append((int(x), int(y)))

                # Cor levemente mais clara para suavizar
                cor_aa = (
                    min(255, cor[0] + 5),
                    min(255, cor[1] + 5),
                    min(255, cor[2] + 5)
                )
                pygame.draw.polygon(superficie, cor_aa, pontos_aa)

    @staticmethod
    def desenhar_retangulo_arredondado_organico(superficie, cor, rect, border_radius=5):
        """Desenha um retângulo arredondado com bordas mais naturais"""
        # Para simplicidade, usar o pygame.draw.rect normal com border_radius
        # mas adicionar pequenos detalhes orgânicos
        pygame.draw.rect(superficie, cor, rect, border_radius=border_radius)

        # Adicionar pequenas variações nas bordas
        pontos_detalhe = [
            (rect.left + rect.width // 4, rect.top),
            (rect.right - rect.width // 4, rect.top),
            (rect.left + rect.width // 4, rect.bottom - 1),
            (rect.right - rect.width // 4, rect.bottom - 1)
        ]

        for ponto in pontos_detalhe:
            cor_detalhe = (
                min(255, cor[0] + 10),
                min(255, cor[1] + 10),
                min(255, cor[2] + 10)
            )
            pygame.draw.circle(superficie, cor_detalhe, ponto, 1)

    @staticmethod
    def aplicar_gradiente_suave(superficie, rect, cor_base, cor_highlight, direcao="vertical"):
        """Aplica um gradiente suave para dar volume"""
        for i in range(rect.height if direcao == "vertical" else rect.width):
            if direcao == "vertical":
                fator = i / rect.height
                y = rect.top + i
                linha_rect = pygame.Rect(rect.left, y, rect.width, 1)
            else:
                fator = i / rect.width
                x = rect.left + i
                linha_rect = pygame.Rect(x, rect.top, 1, rect.height)

            # Interpolar cores
            r = int(cor_base[0] + (cor_highlight[0] - cor_base[0]) * (1 - fator))
            g = int(cor_base[1] + (cor_highlight[1] - cor_base[1]) * (1 - fator))
            b = int(cor_base[2] + (cor_highlight[2] - cor_base[2]) * (1 - fator))

            cor_atual = (r, g, b)
            pygame.draw.rect(superficie, cor_atual, linha_rect)

# Instância global do animador
animador_global = AnimadorPersonagem3D()
