"""
Sistema de Quadtree para otimização espacial de colisões.

Este módulo implementa uma estrutura de dados Quadtree que divide o espaço de jogo
em quadrantes menores, permitindo verificações de colisão mais eficientes ao
processar apenas objetos em regiões próximas.
"""
from typing import List
import pygame

class QuadTree:
    """
    Implementação de QuadTree para otimização espacial de colisões.

    Divide recursivamente o espaço em 4 quadrantes, armazenando objetos
    em folhas até atingir capacidade máxima ou profundidade máxima.
    """

    def __init__(self, bounds: pygame.Rect, max_objects: int = 10, max_levels: int = 5, level: int = 0):
        """
        Inicializar QuadTree.

        Args:
            bounds: Retângulo que define os limites deste nó
            max_objects: Número máximo de objetos antes de subdividir
            max_levels: Profundidade máxima da árvore
            level: Nível atual (0 = raiz)
        """
        self.bounds = bounds
        self.max_objects = max_objects
        self.max_levels = max_levels
        self.level = level
        self.objects = []
        self.nodes = []  # 4 sub-nós: [NE, NW, SW, SE]

    def clear(self):
        """Limpar todos os objetos e sub-nós."""
        self.objects.clear()
        for node in self.nodes:
            if node:
                node.clear()
        self.nodes.clear()

    def split(self):
        """Dividir este nó em 4 sub-quadrantes."""
        sub_width = self.bounds.width // 2
        sub_height = self.bounds.height // 2
        x = self.bounds.x
        y = self.bounds.y

        # Criar 4 sub-nós: NE, NW, SW, SE
        self.nodes = [
            QuadTree(pygame.Rect(x + sub_width, y, sub_width, sub_height),
                    self.max_objects, self.max_levels, self.level + 1),  # NE
            QuadTree(pygame.Rect(x, y, sub_width, sub_height),
                    self.max_objects, self.max_levels, self.level + 1),  # NW
            QuadTree(pygame.Rect(x, y + sub_height, sub_width, sub_height),
                    self.max_objects, self.max_levels, self.level + 1),  # SW
            QuadTree(pygame.Rect(x + sub_width, y + sub_height, sub_width, sub_height),
                    self.max_objects, self.max_levels, self.level + 1)   # SE
        ]

    def get_index(self, sprite) -> int:
        """
        Determinar em qual quadrante um sprite se encaixa.

        Args:
            sprite: Sprite com atributo rect

        Returns:
            Índice do quadrante (0-3) ou -1 se não couber completamente em um
        """
        rect = sprite.rect
        vertical_midpoint = self.bounds.x + (self.bounds.width // 2)
        horizontal_midpoint = self.bounds.y + (self.bounds.height // 2)

        # Verificar se o objeto cabe completamente no quadrante superior
        top_quadrant = (rect.y < horizontal_midpoint and
                       rect.y + rect.height < horizontal_midpoint)

        # Verificar se o objeto cabe completamente no quadrante inferior
        bottom_quadrant = rect.y > horizontal_midpoint

        # Objeto está no lado direito
        if rect.x > vertical_midpoint and rect.x + rect.width < self.bounds.x + self.bounds.width:
            if top_quadrant:
                return 0  # NE
            if bottom_quadrant:
                return 3  # SE

        # Objeto está no lado esquerdo
        elif rect.x < vertical_midpoint and rect.x + rect.width < vertical_midpoint:
            if top_quadrant:
                return 1  # NW
            if bottom_quadrant:
                return 2  # SW

        return -1  # Não cabe completamente em nenhum quadrante

    def insert(self, sprite):
        """
        Inserir um sprite na QuadTree.

        Args:
            sprite: Sprite com atributo rect
        """
        # Se já temos sub-nós, tentar inserir no sub-nó apropriado
        if self.nodes:
            index = self.get_index(sprite)
            if index != -1:
                self.nodes[index].insert(sprite)
                return

        # Adicionar objeto a este nó
        self.objects.append(sprite)

        # Se excedemos capacidade e ainda podemos subdividir
        if (len(self.objects) > self.max_objects and
            self.level < self.max_levels and
            not self.nodes):

            # Subdividir
            self.split()

            # Redistribuir objetos existentes
            i = 0
            while i < len(self.objects):
                obj = self.objects[i]
                index = self.get_index(obj)
                if index != -1:
                    self.nodes[index].insert(self.objects.pop(i))
                else:
                    i += 1

    def retrieve(self, sprite) -> List:
        """
        Recuperar todos os objetos que podem colidir com o sprite dado.

        Args:
            sprite: Sprite com atributo rect

        Returns:
            Lista de sprites que podem colidir
        """
        return_objects = []
        index = self.get_index(sprite)

        # Se temos sub-nós e o sprite cabe em um quadrante específico
        if self.nodes and index != -1:
            return_objects.extend(self.nodes[index].retrieve(sprite))

        # Adicionar objetos deste nó
        return_objects.extend(self.objects)

        # Se o sprite abrange múltiplos quadrantes, verificar todos
        if self.nodes and index == -1:
            for node in self.nodes:
                return_objects.extend(node.retrieve(sprite))

        return return_objects

    def get_all_objects(self) -> List:
        """Recuperar todos os objetos na árvore."""
        all_objects = self.objects.copy()
        for node in self.nodes:
            if node:
                all_objects.extend(node.get_all_objects())
        return all_objects

    def draw_debug(self, surface, color=(255, 0, 0), width=1):
        """
        Desenhar limites da QuadTree para debug.

        Args:
            surface: Superfície pygame para desenhar
            color: Cor das linhas
            width: Espessura das linhas
        """
        pygame.draw.rect(surface, color, self.bounds, width)
        for node in self.nodes:
            if node:
                node.draw_debug(surface, color, width)
