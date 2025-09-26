"""
Sistema de Materiais para Brawl Stars Clone.
Implementa diferentes tipos de materiais e shaders para criar
o visual cartoon 3D característico do Brawl Stars original.
"""

import math
import pygame
import numpy as np
from typing import Dict, Tuple, Optional, List
from enum import Enum
from src.pygame_constants import SRCALPHA


class TipoMaterial(Enum):
    """Tipos de materiais disponíveis"""
    METAL = "metal"
    MADEIRA = "madeira"
    CRISTAL = "cristal"
    PLASTICO = "plastico"
    PEDRA = "pedra"
    AGUA = "agua"
    ENERGIA = "energia"
    ORGANICO = "organico"


class PropriedadesMaterial:
    """Define as propriedades físicas e visuais de um material"""
    def __init__(self,
                 reflexao: float = 0.0,
                 especularidade: float = 0.0,
                 rugosidade: float = 0.5,
                 metalico: float = 0.0,
                 transparencia: float = 0.0,
                 emissor: float = 0.0,
                 cor_ambiente: Tuple[int, int, int] = (128, 128, 128),
                 cor_especular: Tuple[int, int, int] = (255, 255, 255)):
        """
        Inicializa propriedades do material
        Args:
            reflexao: Intensidade da reflexão (0.0 - 1.0)
            especularidade: Intensidade do brilho especular (0.0 - 1.0)
            rugosidade: Rugosidade da superfície (0.0 - 1.0)
            metalico: Se é metálico (0.0 - 1.0)
            transparencia: Nível de transparência (0.0 - 1.0)
            emissor: Se emite luz própria (0.0 - 1.0)
            cor_ambiente: Cor base do material
            cor_especular: Cor dos reflexos especulares
        """
        self.reflexao = max(0.0, min(1.0, reflexao))
        self.especularidade = max(0.0, min(1.0, especularidade))
        self.rugosidade = max(0.0, min(1.0, rugosidade))
        self.metalico = max(0.0, min(1.0, metalico))
        self.transparencia = max(0.0, min(1.0, transparencia))
        self.emissor = max(0.0, min(1.0, emissor))
        self.cor_ambiente = cor_ambiente
        self.cor_especular = cor_especular

class Material:
    """Classe base para materiais"""

    def __init__(self, nome: str):
        self.nome = nome
        self.cor_base = (255, 255, 255)
        self.metalico = 0.0
        self.rugosidade = 1.0
        self.emissao = 0.0
        self.transparencia = 255

    def aplicar_iluminacao(self, cor_base: Tuple[int, int, int],
                          normal: pygame.Vector2, luz_dir: pygame.Vector2,
                          luz_ambiente: float) -> Tuple[int, int, int]:
        """Aplica iluminação baseada no material"""
        return cor_base

class MaterialCartoon(Material):
    """Material com shading cartoon estilo Brawl Stars"""

    def __init__(self, cor_base: Tuple[int, int, int], brilho: float = 0.3):
        super().__init__("cartoon")
        self.cor_base = cor_base
        self.brilho = brilho
        self.cor_highlight = tuple(min(255, int(c * 1.5)) for c in cor_base)
        self.cor_sombra = tuple(max(0, int(c * 0.6)) for c in cor_base)

    def aplicar_iluminacao(self, cor_base: Tuple[int, int, int],
                          normal: pygame.Vector2, luz_dir: pygame.Vector2,
                          luz_ambiente: float) -> Tuple[int, int, int]:
        """Toon shading com transições suaves"""
        # Produto escalar para intensidade
        dot_product = normal.dot(luz_dir)

        # Quantização cartoon com suavização
        if dot_product > 0.7:
            # Área iluminada
            fator = 0.8 + (dot_product - 0.7) * 0.7  # 0.8 a 1.5
            return tuple(min(255, int(c * fator)) for c in self.cor_highlight)
        elif dot_product > 0.2:
            # Área neutra (cor base)
            return cor_base
        else:
            # Materiais dielétricos
            cor_final = self._aplicar_dieletrico(cor_base, intensidade_difusa, intensidade_especular)

        # Aplicar emissão se o material emite luz
        if self.propriedades.emissor > 0:
            cor_final = self._aplicar_emissao(cor_final)
        return cor_final

    def _aplicar_metalico(self, cor_base: Tuple[int, int, int],
                         difusa: float, especular: float) -> Tuple[int, int, int]:
        """Aplica iluminação para materiais metálicos"""
        # Metais têm pouca reflexão difusa mas muita especular
        fator_difuso = 0.1 + difusa * 0.3
        fator_especular = especular * 0.8

        r = min(255, int(cor_base[0] * fator_difuso + self.propriedades.cor_especular[0] * fator_especular))
        g = min(255, int(cor_base[1] * fator_difuso + self.propriedades.cor_especular[1] * fator_especular))
        b = min(255, int(cor_base[2] * fator_difuso + self.propriedades.cor_especular[2] * fator_especular))
        return (r, g, b)

    def _aplicar_dieletrico(self, cor_base: Tuple[int, int, int],
                           difusa: float, especular: float) -> Tuple[int, int, int]:
        """Aplica iluminação para materiais dielétricos (não-metálicos)"""
        # Dielétricos têm boa reflexão difusa e especular branca
        fator_difuso = 0.2 + difusa * 0.6
        fator_especular = especular * 0.4

        r = min(255, int(cor_base[0] * fator_difuso + 255 * fator_especular))
        g = min(255, int(cor_base[1] * fator_difuso + 255 * fator_especular))
        b = min(255, int(cor_base[2] * fator_difuso + 255 * fator_especular))
        return (r, g, b)

    def _aplicar_emissao(self, cor_base: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Aplica emissão de luz do material"""
        intensidade = self.propriedades.emissor

        r = min(255, int(cor_base[0] + self.propriedades.cor_ambiente[0] * intensidade))
        g = min(255, int(cor_base[1] + self.propriedades.cor_ambiente[1] * intensidade))
        b = min(255, int(cor_base[2] + self.propriedades.cor_ambiente[2] * intensidade))

        return (r, g, b)

    def gerar_textura_procedural(self, tamanho: Tuple[int, int],
                                cor_base: Tuple[int, int, int],
                                seed: int = 0) -> pygame.Surface:
        """
        Gera uma textura procedural baseada no tipo de material
        Args:
            tamanho: Dimensões da textura (largura, altura)
            cor_base: Cor base do material
            seed: Seed para geração procedural
        Returns:
            Surface com a textura gerada
        """
        cache_key = (tamanho, cor_base, seed)
        if cache_key in self._cache_texturas:
            return self._cache_texturas[cache_key]
        textura = pygame.Surface(tamanho, SRCALPHA)
        if self.tipo == TipoMaterial.METAL:
            textura = self._gerar_textura_metal(tamanho, cor_base, seed)
        elif self.tipo == TipoMaterial.MADEIRA:
            textura = self._gerar_textura_madeira(tamanho, cor_base, seed)
        elif self.tipo == TipoMaterial.CRISTAL:
            textura = self._gerar_textura_cristal(tamanho, cor_base, seed)
        elif self.tipo == TipoMaterial.PLASTICO:
            textura = self._gerar_textura_plastico(tamanho, cor_base, seed)
        elif self.tipo == TipoMaterial.PEDRA:
            textura = self._gerar_textura_pedra(tamanho, cor_base, seed)
        elif self.tipo == TipoMaterial.AGUA:
            textura = self._gerar_textura_agua(tamanho, cor_base, seed)
        elif self.tipo == TipoMaterial.ENERGIA:
            textura = self._gerar_textura_energia(tamanho, cor_base, seed)
        else:  # ORGANICO
            textura = self._gerar_textura_organica(tamanho, cor_base, seed)
        self._cache_texturas[cache_key] = textura
        return textura

    def _gerar_textura_metal(self, tamanho: Tuple[int, int],
                           cor_base: Tuple[int, int, int], seed: int) -> pygame.Surface:
        """Gera textura metálica com reflexos e arranhões"""
        superficie = pygame.Surface(tamanho, SRCALPHA)
        w, h = tamanho

        # Base metálica
        superficie.fill(cor_base)

        # Arranhões aleatórios
        np.random.seed(seed)
        for _ in range(w // 4):
            x1 = np.random.randint(0, w)
            y1 = np.random.randint(0, h)
            x2 = x1 + np.random.randint(-20, 20)
            y2 = y1 + np.random.randint(-5, 5)

            cor_arranhao = (
                min(255, cor_base[0] + 30),
                min(255, cor_base[1] + 30),
                min(255, cor_base[2] + 30)
            )

            if 0 <= x2 < w and 0 <= y2 < h:
                pygame.draw.line(superficie, cor_arranhao, (x1, y1), (x2, y2), 1)

        # Reflexos especulares
        for y in range(0, h, 4):
            alpha = int(50 + 30 * math.sin(y * 0.1))
            cor_reflexo = (*self.propriedades.cor_especular, alpha)
            linha_surf = pygame.Surface((w, 2), SRCALPHA)
            linha_surf.fill(cor_reflexo)
            superficie.blit(linha_surf, (0, y))
        return superficie

    def _gerar_textura_madeira(self, tamanho: Tuple[int, int],
                             cor_base: Tuple[int, int, int], seed: int) -> pygame.Surface:
        """Gera textura de madeira com veios"""
        superficie = pygame.Surface(tamanho, SRCALPHA)
        w, h = tamanho

        # Base da madeira
        superficie.fill(cor_base)

        # Veios da madeira
        np.random.seed(seed)
        for y in range(0, h, 3):
            for x in range(w):
                # Criar padrão de veios usando seno
                intensidade = math.sin(x * 0.1 + y * 0.05) * 0.3 + 0.7
                noise = np.random.uniform(0.9, 1.1)
                intensidade *= noise
                cor_veio = (
                    int(cor_base[0] * intensidade),
                    int(cor_base[1] * intensidade),
                    int(cor_base[2] * intensidade)
                )

                superficie.set_at((x, y), cor_veio)

        return superficie

    def _gerar_textura_cristal(self, tamanho: Tuple[int, int],
                             cor_base: Tuple[int, int, int], seed: int) -> pygame.Surface:
        """Gera textura cristalina com facetas e brilhos"""
        superficie = pygame.Surface(tamanho, SRCALPHA)
        w, h = tamanho

        # Base cristalina semi-transparente
        cor_base_alpha = (*cor_base, int(255 * (1 - self.propriedades.transparencia)))
        superficie.fill(cor_base_alpha)

        # Facetas cristalinas
        np.random.seed(seed)
        for _ in range(w // 8):
            centro_x = np.random.randint(w // 4, 3 * w // 4)
            centro_y = np.random.randint(h // 4, 3 * h // 4)
            tamanho_faceta = np.random.randint(5, 15)

            # Criar pontos da faceta
            pontos = []
            for i in range(6):  # Hexágono
                angulo = i * 60
                x = centro_x + tamanho_faceta * math.cos(math.radians(angulo))
                y = centro_y + tamanho_faceta * math.sin(math.radians(angulo))
                pontos.append((x, y))

            # Desenhar faceta com brilho
            cor_faceta = (
                min(255, cor_base[0] + 50),
                min(255, cor_base[1] + 50),
                min(255, cor_base[2] + 50)
            )

            pygame.draw.polygon(superficie, cor_faceta, pontos)
            pygame.draw.polygon(superficie, self.propriedades.cor_especular, pontos, 1)

        return superficie

    def _gerar_textura_plastico(self, tamanho: Tuple[int, int],
                              cor_base: Tuple[int, int, int], seed: int) -> pygame.Surface:
        """Gera textura plástica lisa com reflexos suaves"""
        superficie = pygame.Surface(tamanho, SRCALPHA)
        w, h = tamanho

        # Base plástica
        superficie.fill(cor_base)

        # Reflexos suaves e uniformes
        for y in range(0, h, 8):
            alpha = int(20 + 10 * math.sin(y * 0.2))
            cor_reflexo = (*self.propriedades.cor_especular, alpha)

            reflexo_surf = pygame.Surface((w, 4), SRCALPHA)
            reflexo_surf.fill(cor_reflexo)
            superficie.blit(reflexo_surf, (0, y))

        return superficie

    def _gerar_textura_pedra(self, tamanho: Tuple[int, int],
                           cor_base: Tuple[int, int, int], seed: int) -> pygame.Surface:
        """Gera textura de pedra rugosa"""
        superficie = pygame.Surface(tamanho, SRCALPHA)
        w, h = tamanho

        # Base da pedra
        superficie.fill(cor_base)

        # Rugosidade da pedra
        np.random.seed(seed)
        for _ in range(w * h // 4):
            x = np.random.randint(0, w)
            y = np.random.randint(0, h)

            variacao = np.random.uniform(0.7, 1.3)
            cor_rugosa = (
                int(min(255, max(0, cor_base[0] * variacao))),
                int(min(255, max(0, cor_base[1] * variacao))),
                int(min(255, max(0, cor_base[2] * variacao)))
            )

            superficie.set_at((x, y), cor_rugosa)

        return superficie

    def _gerar_textura_agua(self, tamanho: Tuple[int, int],
                          cor_base: Tuple[int, int, int], seed: int) -> pygame.Surface:
        """Gera textura de água com ondulações"""
        superficie = pygame.Surface(tamanho, SRCALPHA)
        w, h = tamanho

        # Base da água semi-transparente
        cor_agua = (*cor_base, 180)
        superficie.fill(cor_agua)

        # Ondulações
        for y in range(h):
            for x in range(0, w, 2):
                ondulacao = math.sin(x * 0.2 + y * 0.1) * 0.3 + 0.7
                alpha = int(100 * ondulacao)

                cor_onda = (*self.propriedades.cor_especular, alpha)
                superficie.set_at((x, y), cor_onda)

        return superficie

    def _gerar_textura_energia(self, tamanho: Tuple[int, int],
                             cor_base: Tuple[int, int, int], seed: int) -> pygame.Surface:
        """Gera textura energética com pulsos e brilhos"""
        superficie = pygame.Surface(tamanho, SRCALPHA)
        w, h = tamanho

        # Base energética brilhante
        superficie.fill(cor_base)

        # Pulsos de energia
        np.random.seed(seed)
        centro_x, centro_y = w // 2, h // 2

        for raio in range(5, min(w, h) // 2, 8):
            alpha = int(100 * (1 - raio / (min(w, h) // 2)))
            cor_pulso = (*cor_base, alpha)

            # Criar surface para o pulso
            pulso_surf = pygame.Surface((raio * 2, raio * 2), SRCALPHA)
            pygame.draw.circle(pulso_surf, cor_pulso, (raio, raio), raio, 2)

            superficie.blit(pulso_surf, (centro_x - raio, centro_y - raio))

        return superficie

    def _gerar_textura_organica(self, tamanho: Tuple[int, int],
                              cor_base: Tuple[int, int, int], seed: int) -> pygame.Surface:
        """Gera textura orgânica com padrões naturais"""
        superficie = pygame.Surface(tamanho, SRCALPHA)
        w, h = tamanho

        # Base orgânica
        superficie.fill(cor_base)

        # Padrões celulares
        np.random.seed(seed)
        for _ in range(w // 6):
            centro_x = np.random.randint(w // 4, 3 * w // 4)
            centro_y = np.random.randint(h // 4, 3 * h // 4)
            raio = np.random.randint(3, 8)

            intensidade = np.random.uniform(0.6, 1.4)
            cor_celula = (
                int(min(255, max(0, cor_base[0] * intensidade))),
                int(min(255, max(0, cor_base[1] * intensidade))),
                int(min(255, max(0, cor_base[2] * intensidade)))
            )

            pygame.draw.circle(superficie, cor_celula, (centro_x, centro_y), raio)

        return superficie


class GerenciadorMateriais:
    """Gerencia todos os materiais do jogo"""

    def __init__(self):
        self.materiais: Dict[str, Material] = {}
        self._inicializar_materiais_padrao()

    def _inicializar_materiais_padrao(self):
        """Inicializa materiais padrão do jogo"""

        # Metal brilhante (para robots como Barley)
        metal_props = PropriedadesMaterial(
            reflexao=0.8,
            especularidade=0.9,
            rugosidade=0.1,
            metalico=1.0,
            cor_especular=(200, 220, 255)
        )
        self.materiais["metal_brilhante"] = Material("Metal Brilhante", TipoMaterial.METAL, metal_props)

        # Madeira natural (para personagens orgânicos)
        madeira_props = PropriedadesMaterial(
            reflexao=0.2,
            especularidade=0.1,
            rugosidade=0.8,
            metalico=0.0,
            cor_ambiente=(139, 90, 43)
        )
        self.materiais["madeira_natural"] = Material("Madeira Natural", TipoMaterial.MADEIRA, madeira_props)

        # Cristal mágico (para gemas e power-ups)
        cristal_props = PropriedadesMaterial(
            reflexao=0.6,
            especularidade=0.8,
            rugosidade=0.1,
            metalico=0.0,
            transparencia=0.3,
            emissor=0.4,
            cor_especular=(255, 255, 255)
        )
        self.materiais["cristal_magico"] = Material("Cristal Mágico", TipoMaterial.CRISTAL, cristal_props)

        # Plástico colorido (para personagens cartoon)
        plastico_props = PropriedadesMaterial(
            reflexao=0.4,
            especularidade=0.6,
            rugosidade=0.3,
            metalico=0.0,
            cor_especular=(255, 255, 255)
        )
        self.materiais["plastico_colorido"] = Material("Plástico Colorido", TipoMaterial.PLASTICO, plastico_props)

        # Pedra antiga (para obstáculos)
        pedra_props = PropriedadesMaterial(
            reflexao=0.1,
            especularidade=0.05,
            rugosidade=0.9,
            metalico=0.0,
            cor_ambiente=(100, 100, 100)
        )
        self.materiais["pedra_antiga"] = Material("Pedra Antiga", TipoMaterial.PEDRA, pedra_props)

        # Energia pura (para projéteis e efeitos especiais)
        energia_props = PropriedadesMaterial(
            reflexao=0.0,
            especularidade=0.0,
            rugosidade=0.0,
            metalico=0.0,
            transparencia=0.2,
            emissor=1.0,
            cor_especular=(255, 255, 255)
        )
        self.materiais["energia_pura"] = Material("Energia Pura", TipoMaterial.ENERGIA, energia_props)

        # Pele orgânica (para personagens biológicos)
        organico_props = PropriedadesMaterial(
            reflexao=0.3,
            especularidade=0.2,
            rugosidade=0.6,
            metalico=0.0,
            cor_ambiente=(255, 220, 177)
        )
        self.materiais["pele_organica"] = Material("Pele Orgânica", TipoMaterial.ORGANICO, organico_props)

    def obter_material(self, nome: str) -> Optional[Material]:
        """Obtém um material pelo nome"""
        return self.materiais.get(nome)

    def adicionar_material(self, material: Material):
        """Adiciona um novo material"""
        self.materiais[material.nome] = material

    def listar_materiais(self) -> List[str]:
        """Lista todos os materiais disponíveis"""
        return list(self.materiais.keys())


# Instância global do gerenciador de materiais
gerenciador_materiais = GerenciadorMateriais()
