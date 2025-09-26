"""
Sistema de Shaders e Pós-Processamento para o Brawl Stars Clone.
Este módulo implementa efeitos visuais avançados incluindo bloom, outline,
blur gaussiano, distorções e outros efeitos de pós-processamento que
transformam o visual do jogo para se aproximar do Brawl Stars original.
"""

import math
import pygame
import numpy as np
from typing import Tuple, List, Optional, Dict, Any
from enum import Enum
from src.pygame_constants import SRCALPHA
from src.material_system import gerenciador_materiais


class TipoShader(Enum):
    """Tipos de shaders disponíveis"""
    BLOOM = "bloom"
    OUTLINE = "outline"
    BLUR_GAUSSIANO = "blur_gaussiano"
    DISTORCAO_CALOR = "distorcao_calor"
    ABERRACAO_CROMATICA = "aberracao_cromatica"
    VINHETA = "vinheta"
    CORRETOR_COR = "corretor_cor"
    ILUMINACAO_VOLUMETRICA = "iluminacao_volumetrica"


class ParametrosShader:
    """Parâmetros configuráveis para shaders"""

    def __init__(self, **kwargs):
        # Parâmetros do Bloom
        self.bloom_threshold = kwargs.get('bloom_threshold', 0.7)
        self.bloom_intensity = kwargs.get('bloom_intensity', 1.5)
        self.bloom_radius = kwargs.get('bloom_radius', 5)

        # Parâmetros do Outline
        self.outline_width = kwargs.get('outline_width', 2)
        self.outline_color = kwargs.get('outline_color', (255, 255, 255))
        self.outline_intensity = kwargs.get('outline_intensity', 1.0)

        # Parâmetros do Blur
        self.blur_radius = kwargs.get('blur_radius', 3)
        self.blur_samples = kwargs.get('blur_samples', 9)

        # Parâmetros da Distorção
        self.distorcao_amplitude = kwargs.get('distorcao_amplitude', 5.0)
        self.distorcao_frequencia = kwargs.get('distorcao_frequencia', 0.1)
        self.distorcao_tempo = kwargs.get('distorcao_tempo', 0.0)

        # Parâmetros da Aberração Cromática
        self.aberracao_intensidade = kwargs.get('aberracao_intensidade', 2.0)

        # Parâmetros da Vinheta
        self.vinheta_intensidade = kwargs.get('vinheta_intensidade', 0.5)
        self.vinheta_raio = kwargs.get('vinheta_raio', 0.8)

        # Parâmetros do Corretor de Cor
        self.saturacao = kwargs.get('saturacao', 1.0)
        self.contraste = kwargs.get('contraste', 1.0)
        self.brilho = kwargs.get('brilho', 0.0)
        self.temperatura_cor = kwargs.get('temperatura_cor', 0.0)

        # Parâmetros da Iluminação Volumétrica
        self.vol_light_intensity = kwargs.get('vol_light_intensity', 0.5)
        self.vol_light_steps = kwargs.get('vol_light_steps', 16)


class Shader:
    """Classe base para shaders"""

    def __init__(self, tipo: TipoShader, parametros: ParametrosShader):
        self.tipo = tipo
        self.parametros = parametros
        self.ativo = True
        self.cache_enabled = True
        self._cache = {}

    def aplicar(self, superficie: pygame.Surface, **kwargs) -> pygame.Surface:
        """Aplica o shader à superfície"""
        if not self.ativo:
            return superficie

        # Verificar cache
        cache_key = self._gerar_cache_key(superficie, kwargs)
        if self.cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]

        # Aplicar shader específico
        resultado = self._processar_shader(superficie, **kwargs)

        # Armazenar no cache
        if self.cache_enabled:
            self._cache[cache_key] = resultado

        return resultado

    def _gerar_cache_key(self, superficie: pygame.Surface, kwargs: Dict) -> str:
        """Gera chave para cache baseada nos parâmetros"""
        return f"{self.tipo.value}_{superficie.get_size()}_{hash(str(kwargs))}"

    def _processar_shader(self, superficie: pygame.Surface, **kwargs) -> pygame.Surface:
        """Método para ser sobrescrito pelas subclasses"""
        raise NotImplementedError("Subclasses devem implementar _processar_shader")

    def limpar_cache(self):
        """Limpa o cache do shader"""
        self._cache.clear()


class BloomShader(Shader):
    """Shader de bloom para efeitos de brilho"""

    def __init__(self, parametros: ParametrosShader):
        super().__init__(TipoShader.BLOOM, parametros)

    def _processar_shader(self, superficie: pygame.Surface, **kwargs) -> pygame.Surface:
        """Aplica efeito de bloom"""
        w, h = superficie.get_size()

        # 1. Extrair pixels brilhantes
        bright_surface = self._extrair_pixels_brilhantes(superficie)

        # 2. Aplicar blur múltiplas vezes
        blurred = self._aplicar_blur_multiple(bright_surface)

        # 3. Combinar com a imagem original
        resultado = pygame.Surface((w, h), SRCALPHA)
        resultado.blit(superficie, (0, 0))

        # Aplicar bloom com blend mode
        self._aplicar_bloom_blend(resultado, blurred)

        return resultado

    def _extrair_pixels_brilhantes(self, superficie: pygame.Surface) -> pygame.Surface:
        """Extrai apenas os pixels que excedem o threshold de brilho"""
        w, h = superficie.get_size()
        bright_surface = pygame.Surface((w, h), SRCALPHA)

        # Converter para array numpy para processamento rápido
        array = pygame.surfarray.array3d(superficie)

        # Calcular luminância
        luminancia = np.dot(array[..., :3], [0.299, 0.587, 0.114])

        # Aplicar threshold
        mask = luminancia > (self.parametros.bloom_threshold * 255)

        # Criar nova imagem apenas com pixels brilhantes
        bright_array = array.copy()
        bright_array[~mask] = [0, 0, 0]

        pygame.surfarray.blit_array(bright_surface, bright_array)
        return bright_surface

    def _aplicar_blur_multiple(self, superficie: pygame.Surface) -> pygame.Surface:
        """Aplica blur gaussiano múltiplas vezes para efeito suave"""
        resultado = superficie.copy()

        for i in range(3):  # Múltiplas passadas de blur
            radius = self.parametros.bloom_radius * (i + 1)
            resultado = self._blur_gaussiano(resultado, radius)

        return resultado

    def _blur_gaussiano(self, superficie: pygame.Surface, radius: int) -> pygame.Surface:
        """Aplica blur gaussiano"""
        w, h = superficie.get_size()
        if radius <= 0:
            return superficie.copy()

        # Blur horizontal
        h_blur = pygame.Surface((w, h), SRCALPHA)
        for y in range(h):
            for x in range(w):
                r, g, b, a = 0, 0, 0, 0
                peso_total = 0

                for i in range(-radius, radius + 1):
                    sample_x = max(0, min(w - 1, x + i))
                    peso = math.exp(-(i * i) / (2.0 * radius * radius))
                    pixel = superficie.get_at((sample_x, y))

                    r += pixel[0] * peso
                    g += pixel[1] * peso
                    b += pixel[2] * peso
                    a += pixel[3] * peso
                    peso_total += peso

                if peso_total > 0:
                    h_blur.set_at((x, y), (
                        int(r / peso_total),
                        int(g / peso_total),
                        int(b / peso_total),
                        int(a / peso_total)
                    ))

        # Blur vertical
        v_blur = pygame.Surface((w, h), SRCALPHA)
        for x in range(w):
            for y in range(h):
                r, g, b, a = 0, 0, 0, 0
                peso_total = 0

                for i in range(-radius, radius + 1):
                    sample_y = max(0, min(h - 1, y + i))
                    peso = math.exp(-(i * i) / (2.0 * radius * radius))
                    pixel = h_blur.get_at((x, sample_y))

                    r += pixel[0] * peso
                    g += pixel[1] * peso
                    b += pixel[2] * peso
                    a += pixel[3] * peso
                    peso_total += peso

                if peso_total > 0:
                    v_blur.set_at((x, y), (
                        int(r / peso_total),
                        int(g / peso_total),
                        int(b / peso_total),
                        int(a / peso_total)
                    ))

        return v_blur

    def _aplicar_bloom_blend(self, base: pygame.Surface, bloom: pygame.Surface):
        """Combina bloom com a imagem base usando additive blending"""
        w, h = base.get_size()

        for x in range(w):
            for y in range(h):
                pixel_base = base.get_at((x, y))
                pixel_bloom = bloom.get_at((x, y))

                # Additive blending com intensidade
                novo_r = min(255, pixel_base[0] + int(pixel_bloom[0] * self.parametros.bloom_intensity))
                novo_g = min(255, pixel_base[1] + int(pixel_bloom[1] * self.parametros.bloom_intensity))
                novo_b = min(255, pixel_base[2] + int(pixel_bloom[2] * self.parametros.bloom_intensity))

                base.set_at((x, y), (novo_r, novo_g, novo_b, pixel_base[3]))


class OutlineShader(Shader):
    """Shader de outline para contornos dinâmicos"""

    def __init__(self, parametros: ParametrosShader):
        super().__init__(TipoShader.OUTLINE, parametros)

    def _processar_shader(self, superficie: pygame.Surface, **kwargs) -> pygame.Surface:
        """Aplica efeito de outline"""
        w, h = superficie.get_size()
        resultado = pygame.Surface((w, h), SRCALPHA)

        # Criar máscara de bordas
        mask_bordas = self._detectar_bordas(superficie)

        # Desenhar outline
        outline_surface = self._criar_outline(mask_bordas)

        # Combinar outline com imagem original
        resultado.blit(outline_surface, (0, 0))
        resultado.blit(superficie, (0, 0))

        return resultado

    def _detectar_bordas(self, superficie: pygame.Surface) -> pygame.Surface:
        """Detecta bordas usando filtro Sobel"""
        w, h = superficie.get_size()
        bordas = pygame.Surface((w, h), SRCALPHA)

        # Operadores Sobel
        sobel_x = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
        sobel_y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]

        for x in range(1, w - 1):
            for y in range(1, h - 1):
                gx = gy = 0

                for i in range(-1, 2):
                    for j in range(-1, 2):
                        pixel = superficie.get_at((x + i, y + j))
                        luminancia = 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]

                        gx += luminancia * sobel_x[i + 1][j + 1]
                        gy += luminancia * sobel_y[i + 1][j + 1]

                magnitude = math.sqrt(gx * gx + gy * gy)
                intensity = min(255, int(magnitude))

                if intensity > 50:  # Threshold para detectar bordas
                    bordas.set_at((x, y), (255, 255, 255, 255))
                else:
                    bordas.set_at((x, y), (0, 0, 0, 0))

        return bordas

    def _criar_outline(self, mask_bordas: pygame.Surface) -> pygame.Surface:
        """Cria outline colorido a partir da máscara de bordas"""
        w, h = mask_bordas.get_size()
        outline = pygame.Surface((w, h), SRCALPHA)

        width = self.parametros.outline_width
        cor = self.parametros.outline_color

        for x in range(w):
            for y in range(h):
                if mask_bordas.get_at((x, y))[0] > 0:  # Se é uma borda
                    # Desenhar círculo pequeno para criar espessura
                    for dx in range(-width, width + 1):
                        for dy in range(-width, width + 1):
                            if dx * dx + dy * dy <= width * width:
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < w and 0 <= ny < h:
                                    alpha = int(255 * self.parametros.outline_intensity)
                                    outline.set_at((nx, ny), (*cor, alpha))

        return outline


class DistorcaoCalorShader(Shader):
    """Shader de distorção de calor para efeitos atmosféricos"""

    def __init__(self, parametros: ParametrosShader):
        super().__init__(TipoShader.DISTORCAO_CALOR, parametros)

    def _processar_shader(self, superficie: pygame.Surface, **kwargs) -> pygame.Surface:
        """Aplica efeito de distorção de calor"""
        w, h = superficie.get_size()
        resultado = pygame.Surface((w, h), SRCALPHA)

        tempo = kwargs.get('tempo', 0.0)

        for x in range(w):
            for y in range(h):
                # Calcular distorção usando funções senoidais
                offset_x = self.parametros.distorcao_amplitude * math.sin(
                    y * self.parametros.distorcao_frequencia + tempo
                )
                offset_y = self.parametros.distorcao_amplitude * math.sin(
                    x * self.parametros.distorcao_frequencia * 0.7 + tempo * 1.3
                )

                # Posição de origem com distorção
                orig_x = x + int(offset_x)
                orig_y = y + int(offset_y)

                # Verificar limites
                if 0 <= orig_x < w and 0 <= orig_y < h:
                    pixel = superficie.get_at((orig_x, orig_y))
                    resultado.set_at((x, y), pixel)
                else:
                    resultado.set_at((x, y), (0, 0, 0, 0))

        return resultado


class CorretorCorShader(Shader):
    """Shader para correção de cor e ajustes visuais"""

    def __init__(self, parametros: ParametrosShader):
        super().__init__(TipoShader.CORRETOR_COR, parametros)

    def _processar_shader(self, superficie: pygame.Surface, **kwargs) -> pygame.Surface:
        """Aplica correções de cor"""
        w, h = superficie.get_size()
        resultado = pygame.Surface((w, h), SRCALPHA)

        for x in range(w):
            for y in range(h):
                pixel = superficie.get_at((x, y))
                r, g, b, a = pixel

                # Aplicar brilho
                r = max(0, min(255, r + self.parametros.brilho))
                g = max(0, min(255, g + self.parametros.brilho))
                b = max(0, min(255, b + self.parametros.brilho))

                # Aplicar contraste
                r = max(0, min(255, int((r - 128) * self.parametros.contraste + 128)))
                g = max(0, min(255, int((g - 128) * self.parametros.contraste + 128)))
                b = max(0, min(255, int((b - 128) * self.parametros.contraste + 128)))

                # Aplicar saturação
                luminancia = 0.299 * r + 0.587 * g + 0.114 * b
                r = max(0, min(255, int(luminancia + (r - luminancia) * self.parametros.saturacao)))
                g = max(0, min(255, int(luminancia + (g - luminancia) * self.parametros.saturacao)))
                b = max(0, min(255, int(luminancia + (b - luminancia) * self.parametros.saturacao)))

                # Aplicar temperatura de cor
                if self.parametros.temperatura_cor > 0:  # Mais quente
                    r = min(255, int(r * (1 + self.parametros.temperatura_cor * 0.1)))
                    b = max(0, int(b * (1 - self.parametros.temperatura_cor * 0.1)))
                elif self.parametros.temperatura_cor < 0:  # Mais frio
                    r = max(0, int(r * (1 + self.parametros.temperatura_cor * 0.1)))
                    b = min(255, int(b * (1 - self.parametros.temperatura_cor * 0.1)))

                resultado.set_at((x, y), (r, g, b, a))

        return resultado


class ProcessadorShaders:
    """Gerenciador principal do sistema de shaders"""

    def __init__(self):
        self.shaders: List[Shader] = []
        self.shaders_ativos: Dict[TipoShader, bool] = {}
        self.performance_mode = False
        self._inicializar_shaders_padrao()

    def _inicializar_shaders_padrao(self):
        """Inicializa shaders padrão com configurações otimizadas para Brawl Stars"""

        # Parâmetros otimizados para estilo Brawl Stars
        params_bloom = ParametrosShader(
            bloom_threshold=0.6,
            bloom_intensity=1.2,
            bloom_radius=3
        )

        params_outline = ParametrosShader(
            outline_width=2,
            outline_color=(255, 255, 255),
            outline_intensity=0.8
        )

        params_corretor = ParametrosShader(
            saturacao=1.2,
            contraste=1.1,
            brilho=5,
            temperatura_cor=0.1
        )

        params_distorcao = ParametrosShader(
            distorcao_amplitude=2.0,
            distorcao_frequencia=0.05
        )

        # Adicionar shaders
        self.adicionar_shader(BloomShader(params_bloom))
        self.adicionar_shader(OutlineShader(params_outline))
        self.adicionar_shader(CorretorCorShader(params_corretor))
        self.adicionar_shader(DistorcaoCalorShader(params_distorcao))

        # Ativar shaders principais
        self.ativar_shader(TipoShader.BLOOM)
        self.ativar_shader(TipoShader.CORRETOR_COR)

    def adicionar_shader(self, shader: Shader):
        """Adiciona um shader ao pipeline"""
        self.shaders.append(shader)
        self.shaders_ativos[shader.tipo] = False

    def ativar_shader(self, tipo: TipoShader):
        """Ativa um shader específico"""
        self.shaders_ativos[tipo] = True
        for shader in self.shaders:
            if shader.tipo == tipo:
                shader.ativo = True

    def desativar_shader(self, tipo: TipoShader):
        """Desativa um shader específico"""
        self.shaders_ativos[tipo] = False
        for shader in self.shaders:
            if shader.tipo == tipo:
                shader.ativo = False

    def processar_frame(self, superficie: pygame.Surface, **kwargs) -> pygame.Surface:
        """
        Processa um frame através de todos os shaders ativos

        Args:
            superficie: Surface a ser processada
            **kwargs: Parâmetros adicionais (tempo, posições, etc.)

        Returns:
            Surface processada
        """
        resultado = superficie.copy()

        # Aplicar shaders em ordem específica para melhor resultado
        ordem_shaders = [
            TipoShader.DISTORCAO_CALOR,
            TipoShader.CORRETOR_COR,
            TipoShader.OUTLINE,
            TipoShader.BLOOM
        ]

        for tipo_shader in ordem_shaders:
            if self.shaders_ativos.get(tipo_shader, False):
                shader = self._obter_shader(tipo_shader)
                if shader and shader.ativo:
                    resultado = shader.aplicar(resultado, **kwargs)

        return resultado

    def _obter_shader(self, tipo: TipoShader) -> Optional[Shader]:
        """Obtém shader por tipo"""
        for shader in self.shaders:
            if shader.tipo == tipo:
                return shader
        return None

    def ativar_modo_performance(self):
        """Ativa modo de performance (menos shaders)"""
        self.performance_mode = True
        # Desativar shaders pesados
        self.desativar_shader(TipoShader.DISTORCAO_CALOR)

        # Reduzir qualidade dos shaders ativos
        bloom_shader = self._obter_shader(TipoShader.BLOOM)
        if bloom_shader:
            bloom_shader.parametros.bloom_radius = 2
            bloom_shader.cache_enabled = True

    def desativar_modo_performance(self):
        """Desativa modo de performance"""
        self.performance_mode = False
        self._inicializar_shaders_padrao()

    def limpar_caches(self):
        """Limpa todos os caches dos shaders"""
        for shader in self.shaders:
            shader.limpar_cache()

    def atualizar_parametros_shader(self, tipo: TipoShader, **novos_params):
        """Atualiza parâmetros de um shader específico"""
        shader = self._obter_shader(tipo)
        if shader:
            for param, valor in novos_params.items():
                if hasattr(shader.parametros, param):
                    setattr(shader.parametros, param, valor)
            shader.limpar_cache()  # Limpar cache quando parâmetros mudam


# Instância global do processador
processador_shaders = ProcessadorShaders()
