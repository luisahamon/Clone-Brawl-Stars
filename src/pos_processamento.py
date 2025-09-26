"""
Sistema de Pós-Processamento Avançado para o Brawl Stars Clone.
Este módulo integra todos os efeitos visuais, shaders e materiais para
criar um pipeline de renderização completo que transforma o visual básico
do jogo em algo próximo ao Brawl Stars original.
"""

import math
import random
from typing import Tuple, List, Optional
import pygame
from src.pygame_constants import SRCALPHA
from src.shader_system import processador_shaders, TipoShader, ParametrosShader
from src.material_system import gerenciador_materiais
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT


class EfeitosPosProcessamento:
    """Gerenciador de efeitos de pós-processamento"""
    def __init__(self):
        self.buffer_principal = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), SRCALPHA)
        self.buffer_temporario = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), SRCALPHA)
        self.buffer_bloom = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), SRCALPHA)
        # Configurações de qualidade
        self.qualidade_alta = True
        self.anti_aliasing = True
        self.vsync = True
        # Efeitos dinâmicos
        self.tempo_global = 0.0
        self.intensidade_acao = 0.0  # 0.0 = calmo, 1.0 = ação intensa
        self.modo_cinematico = False
        # Cache de efeitos
        self._cache_vinheta = None
        self._cache_grade_luz = None
        # Parâmetros dinâmicos
        self.saturacao_dinamica = 1.0
        self.contraste_dinamico = 1.0
        self.temperatura_cor_dinamica = 0.0

    def processar_frame_completo(self, superficie_jogo: pygame.Surface,
                               elementos_ui: List[pygame.Surface] = None,
                               **kwargs) -> pygame.Surface:
        """
        Processa um frame completo com todos os efeitos de pós-processamento
        Args:
            superficie_jogo: Surface principal do jogo
            elementos_ui: Lista de elementos de UI para renderizar por último
            **kwargs: Parâmetros adicionais (posicoes_luz, intensidade_acao, etc.)
        Returns:
            Frame final processado
        """
        # Atualizar parâmetros dinâmicos
        self._atualizar_parametros_dinamicos(**kwargs)

        # Buffer principal
        self.buffer_principal.fill((0, 0, 0, 0))
        self.buffer_principal.blit(superficie_jogo, (0, 0))

        # 1. Aplicar efeitos de material e iluminação
        if self.qualidade_alta:
            self.buffer_principal = self._aplicar_iluminacao_global(self.buffer_principal, **kwargs)

        # 2. Aplicar shaders principais
        self.buffer_principal = processador_shaders.processar_frame(
            self.buffer_principal,
            tempo=self.tempo_global,
            intensidade_acao=self.intensidade_acao,
            **kwargs
        )

        # 3. Efeitos atmosféricos
        if self.qualidade_alta:
            self.buffer_principal = self._aplicar_efeitos_atmosfericos(self.buffer_principal, **kwargs)

        # 4. Efeitos cinemáticos se ativo
        if self.modo_cinematico:
            self.buffer_principal = self._aplicar_efeitos_cinematicos(self.buffer_principal, **kwargs)

        # 5. Efeitos de tela final
        self.buffer_principal = self._aplicar_efeitos_finais(self.buffer_principal, **kwargs)

        # 6. Renderizar UI por último (sem pós-processamento)
        if elementos_ui:
            for elemento in elementos_ui:
                self.buffer_principal.blit(elemento, (0, 0))

        # 7. Anti-aliasing se ativado
        if self.anti_aliasing and self.qualidade_alta:
            self.buffer_principal = self._aplicar_anti_aliasing(self.buffer_principal)

        return self.buffer_principal

    def _atualizar_parametros_dinamicos(self, **kwargs):
        """Atualiza parâmetros baseados no estado do jogo"""
        # Atualizar tempo
        dt = kwargs.get('dt', 1/60)
        self.tempo_global += dt

        # Atualizar intensidade de ação
        nova_intensidade = kwargs.get('intensidade_acao', 0.0)
        # Suavizar mudanças de intensidade
        self.intensidade_acao += (nova_intensidade - self.intensidade_acao) * dt * 5

        # Ajustar parâmetros de shader baseado na intensidade
        if self.intensidade_acao > 0.5:
            # Em combate intenso - cores mais vibrantes
            self.saturacao_dinamica = 1.0 + self.intensidade_acao * 0.3
            self.contraste_dinamico = 1.0 + self.intensidade_acao * 0.2
            processador_shaders.atualizar_parametros_shader(
                TipoShader.BLOOM,
                bloom_intensity=1.2 + self.intensidade_acao * 0.5
            )
        else:
            # Em momentos calmos - cores mais naturais
            self.saturacao_dinamica = 1.0
            self.contraste_dinamico = 1.0
            processador_shaders.atualizar_parametros_shader(
                TipoShader.BLOOM,
                bloom_intensity=1.0
            )

        # Atualizar corretor de cor
        processador_shaders.atualizar_parametros_shader(
            TipoShader.CORRETOR_COR,
            saturacao=self.saturacao_dinamica,
            contraste=self.contraste_dinamico,
            temperatura_cor=self.temperatura_cor_dinamica
        )

    def _aplicar_iluminacao_global(self, superficie: pygame.Surface, **kwargs) -> pygame.Surface:
        """Aplica iluminação global dinâmica"""
        posicoes_luz = kwargs.get('posicoes_luz', [])
        intensidade_ambiente = kwargs.get('intensidade_ambiente', 0.3)

        if not posicoes_luz:
            return superficie

        w, h = superficie.get_size()
        superficie_iluminada = pygame.Surface((w, h), SRCALPHA)
        superficie_iluminada.blit(superficie, (0, 0))

        # Aplicar luzes pontuais
        for luz in posicoes_luz:
            x_luz = luz.get('x', SCREEN_WIDTH // 2)
            y_luz = luz.get('y', SCREEN_HEIGHT // 2)
            intensidade = luz.get('intensidade', 1.0)
            cor_luz = luz.get('cor', (255, 255, 255))
            raio = luz.get('raio', 200)
            self._aplicar_luz_pontual(superficie_iluminada, x_luz, y_luz,
                                    intensidade, cor_luz, raio)
        return superficie_iluminada

    def _aplicar_luz_pontual(self, superficie: pygame.Surface, x_luz: int, y_luz: int,
                           intensidade: float, cor_luz: Tuple[int, int, int], raio: int):
        """Aplica uma luz pontual à superfície"""
        w, h = superficie.get_size()

        # Criar máscara de luz
        luz_surface = pygame.Surface((raio * 2, raio * 2), SRCALPHA)

        for y in range(raio * 2):
            for x in range(raio * 2):
                dx = x - raio
                dy = y - raio
                distancia = math.sqrt(dx * dx + dy * dy)

                if distancia <= raio:
                    # Atenuação quadrática
                    atenuacao = max(0.0, 1.0 - (distancia / raio) ** 2)
                    alpha = int(255 * atenuacao * intensidade * 0.3)

                    cor_final = (*cor_luz, alpha)
                    luz_surface.set_at((x, y), cor_final)

        # Aplicar luz à superfície principal
        pos_x = x_luz - raio
        pos_y = y_luz - raio

        # Usar blend mode aditivo para iluminação
        superficie.blit(luz_surface, (pos_x, pos_y), special_flags=pygame.BLEND_ADD)

    def _aplicar_efeitos_atmosfericos(self, superficie: pygame.Surface, **kwargs) -> pygame.Surface:
        """Aplica efeitos atmosféricos como névoa, partículas de ar, etc."""
        ambiente = kwargs.get('ambiente', 'normal')

        if ambiente == 'nevoa':
            superficie = self._aplicar_nevoa(superficie, **kwargs)
        elif ambiente == 'tempestade':
            superficie = self._aplicar_chuva_atmosferica(superficie, **kwargs)
        elif ambiente == 'calor':
            # Ativar distorção de calor
            processador_shaders.ativar_shader(TipoShader.DISTORCAO_CALOR)
        return superficie

    def _aplicar_nevoa(self, superficie: pygame.Surface, **kwargs) -> pygame.Surface:
        """Aplica efeito de névoa"""
        intensidade_nevoa = kwargs.get('intensidade_nevoa', 0.3)
        cor_nevoa = kwargs.get('cor_nevoa', (200, 200, 220))
        w, h = superficie.get_size()
        nevoa_surface = pygame.Surface((w, h), SRCALPHA)
        # Névoa com gradiente vertical
        for y in range(h):
            # Mais névoa na parte inferior
            densidade = intensidade_nevoa * (1.0 + y / h * 0.5)
            alpha = int(255 * densidade * 0.4)
            cor_final = (*cor_nevoa, alpha)
            pygame.draw.line(nevoa_surface, cor_final, (0, y), (w, y))

        # Aplicar névoa com blend multiplicativo
        superficie.blit(nevoa_surface, (0, 0), special_flags=pygame.BLEND_MULT)
        return superficie

    def _aplicar_chuva_atmosferica(self, superficie: pygame.Surface, **kwargs) -> pygame.Surface:
        """Aplica efeito atmosférico de chuva"""
        # Escurecer ligeiramente a cena
        overlay = pygame.Surface(superficie.get_size(), SRCALPHA)
        overlay.fill((50, 50, 70, 30))
        superficie.blit(overlay, (0, 0))

        # Adicionar riscos de chuva
        w, h = superficie.get_size()
        for _ in range(50):
            x = int(self.tempo_global * 200 + _ * 13) % w
            y = int(self.tempo_global * 400 + _ * 7) % h
            pygame.draw.line(superficie, (180, 190, 200, 100),
                           (x, y), (x - 3, y + 8), 1)
        return superficie

    def _aplicar_efeitos_cinematicos(self, superficie: pygame.Surface, **kwargs) -> pygame.Surface:
        """Aplica efeitos cinemáticos especiais"""
        # Barras cinemáticas
        superficie = self._aplicar_barras_cinematicas(superficie)

        # Vinheta mais intensa
        superficie = self._aplicar_vinheta_cinematica(superficie)

        # Correção de cor mais dramática
        processador_shaders.atualizar_parametros_shader(
            TipoShader.CORRETOR_COR,
            contraste=1.3,
            saturacao=0.8,
            temperatura_cor=-0.1
        )
        return superficie

    def _aplicar_barras_cinematicas(self, superficie: pygame.Surface) -> pygame.Surface:
        """Aplica barras pretas cinemáticas"""
        w, h = superficie.get_size()
        altura_barra = h // 8

        # Barra superior
        pygame.draw.rect(superficie, (0, 0, 0), (0, 0, w, altura_barra))

        # Barra inferior
        pygame.draw.rect(superficie, (0, 0, 0), (0, h - altura_barra, w, altura_barra))

        return superficie

    def _aplicar_vinheta_cinematica(self, superficie: pygame.Surface) -> pygame.Surface:
        """Aplica vinheta cinematográfica"""
        if not self._cache_vinheta:
            self._cache_vinheta = self._criar_vinheta_cinematica()
        superficie.blit(self._cache_vinheta, (0, 0), special_flags=pygame.BLEND_MULT)
        return superficie

    def _criar_vinheta_cinematica(self) -> pygame.Surface:
        """Cria textura de vinheta cinemática"""
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT
        vinheta = pygame.Surface((w, h), SRCALPHA)
        centro_x, centro_y = w // 2, h // 2
        raio_max = math.sqrt(centro_x * centro_x + centro_y * centro_y)
        for x in range(w):
            for y in range(h):
                dx = x - centro_x
                dy = y - centro_y
                distancia = math.sqrt(dx * dx + dy * dy)

                # Vinheta mais suave
                fator = min(1.0, distancia / (raio_max * 0.7))
                escurecimento = int(255 * (0.3 + fator * 0.7))
                vinheta.set_at((x, y), (escurecimento, escurecimento, escurecimento))

        return vinheta

    def _aplicar_efeitos_finais(self, superficie: pygame.Surface, **kwargs) -> pygame.Surface:
        """Aplica efeitos finais de acabamento"""
        # Noise sutil para quebrar gradientes
        if self.qualidade_alta:
            superficie = self._aplicar_noise_sutil(superficie)

        # Sharpen sutil para definição
        superficie = self._aplicar_sharpen_sutil(superficie)
        return superficie

    def _aplicar_noise_sutil(self, superficie: pygame.Surface) -> pygame.Surface:
        """Aplica noise sutil para quebrar bandas de gradiente"""
        w, h = superficie.get_size()
        for _ in range(w * h // 100):  # Poucos pixels aleatórios
            x = random.randint(0, w - 1)
            y = random.randint(0, h - 1)
            pixel = superficie.get_at((x, y))
            noise = random.randint(-3, 3)
            novo_pixel = (
                max(0, min(255, pixel[0] + noise)),
                max(0, min(255, pixel[1] + noise)),
                max(0, min(255, pixel[2] + noise)),
                pixel[3]
            )
            superficie.set_at((x, y), novo_pixel)
        return superficie
    def _aplicar_sharpen_sutil(self, superficie: pygame.Surface) -> pygame.Surface:
        """Aplica sharpening sutil para maior definição"""
        w, h = superficie.get_size()
        resultado = superficie.copy()

        # Kernel de sharpening
        kernel = [
            [0, -0.1, 0],
            [-0.1, 1.4, -0.1],
            [0, -0.1, 0]
        ]

        # Aplicar apenas em alguns pixels para performance
        for x in range(1, w - 1, 2):  # Skip pixels para performance
            for y in range(1, h - 1, 2):
                r = g = b = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        pixel = superficie.get_at((x + i, y + j))
                        peso = kernel[i + 1][j + 1]
                        r += pixel[0] * peso
                        g += pixel[1] * peso
                        b += pixel[2] * peso

                # Clamping
                r = max(0, min(255, int(r)))
                g = max(0, min(255, int(g)))
                b = max(0, min(255, int(b)))
                pixel_original = superficie.get_at((x, y))
                resultado.set_at((x, y), (r, g, b, pixel_original[3]))
        return resultado

    def _aplicar_anti_aliasing(self, superficie: pygame.Surface) -> pygame.Surface:
        """Aplica anti-aliasing básico por software"""
        # Para performance, usar scaling simples
        w, h = superficie.get_size()
        # Scale up e depois down para suavizar
        temp_surface = pygame.transform.scale(superficie, (w * 2, h * 2))
        resultado = pygame.transform.smoothscale(temp_surface, (w, h))
        return resultado

    def ativar_modo_cinematico(self):
        """Ativa modo cinemático"""
        self.modo_cinematico = True
    def desativar_modo_cinematico(self):
        """Desativa modo cinemático"""
        self.modo_cinematico = False
    def ajustar_qualidade(self, alta_qualidade: bool):
        """Ajusta nível de qualidade dos efeitos"""
        self.qualidade_alta = alta_qualidade
        if alta_qualidade:
            processador_shaders.desativar_modo_performance()
        else:
            processador_shaders.ativar_modo_performance()

    def limpar_caches(self):
        """Limpa todos os caches"""
        self._cache_vinheta = None
        self._cache_grade_luz = None
        processador_shaders.limpar_caches()

# Instância global do processador de pós-processamento
processador_pos = ProcessadorPos()
