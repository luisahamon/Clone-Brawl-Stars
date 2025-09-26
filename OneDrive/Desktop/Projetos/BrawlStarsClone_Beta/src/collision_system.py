"""
Sistema de Object Pooling para projéteis.
Este módulo implementa um pool de objetos para reutilização de projéteis,
reduzindo a criação/destruição frequente de objetos e melhorando a performance.
"""

from typing import List, Optional
from src.bullet import Bullet
from src.quadtree import QuadTree


class ProjectilePool:
    """
    Pool de objetos para projéteis.
    Mantém um conjunto de projéteis pré-criados que podem ser reutilizados,
    evitando a criação e destruição constante de objetos durante o jogo.
    """

    def __init__(self, size: int = 200):
        """
        Inicializar pool de projéteis.
        Args:
            size: Tamanho inicial do pool
        """
        self.size = size
        self.pool = []
        self.active_bullets = []
        self.inactive_bullets = []

        # Criar projéteis iniciais
        self._create_initial_bullets()

    def _create_initial_bullets(self):
        """Criar projéteis iniciais para o pool."""
        for _ in range(self.size):
            bullet = Bullet(0, 0, 0, 0)  # Posição e direção serão definidas depois
            bullet.ativo = False  # Marcar como inativo
            self.pool.append(bullet)
            self.inactive_bullets.append(bullet)

    def get_bullet(self, x: float, y: float, direcao_x: float, direcao_y: float,
                   dano: int = 25, velocidade: float = 400, de_inimigo: bool = False, tipo_tiro: str = "normal") -> Optional[Bullet]:
        """
        Obter um projétil do pool.
        Args:
            x: Posição X inicial
            y: Posição Y inicial
            direcao_x: Direção X do movimento
            direcao_y: Direção Y do movimento            dano: Dano causado pelo projétil
            velocidade: Velocidade do projétil
            de_inimigo: Se o projétil é de um inimigo
            tipo_tiro: Tipo do tiro (normal, shotgun, sniper, etc.)
        Returns:
            Projétil configurado ou None se pool estiver vazio
        """
        if not self.inactive_bullets:
            # Se pool estiver vazio, criar novo projétil
            bullet = Bullet(x, y, direcao_x, direcao_y, de_inimigo=de_inimigo, tipo_tiro=tipo_tiro)
            self.pool.append(bullet)
        else:
            # Reutilizar projétil existente
            bullet = self.inactive_bullets.pop()
            bullet.reset(x, y, direcao_x, direcao_y)

        # Configurar propriedades
        bullet.dano = dano
        bullet.velocidade = velocidade
        bullet.de_inimigo = de_inimigo
        bullet.tipo_tiro = tipo_tiro
        bullet.ativo = True

        # Mover para lista de ativos
        self.active_bullets.append(bullet)

        return bullet

    def return_bullet(self, bullet: Bullet):
        """
        Retornar um projétil para o pool.
          Args:
            bullet: Projétil a ser retornado
        """
        if bullet in self.active_bullets:
            self.active_bullets.remove(bullet)
            bullet.ativo = False
            bullet.kill()  # Remover de grupos pygame
            self.inactive_bullets.append(bullet)

    def update(self, _dt: float):
        """
        Atualizar projéteis ativos e retornar os inativos.
        Args:
            _dt: Delta time (não usado nesta versão)
        """
        # Lista de projéteis para retornar ao pool
        bullets_to_return = []

        for bullet in self.active_bullets[:]:  # Cópia para modificar durante iteração
            if not bullet.ativo or bullet.fora_da_tela():
                bullets_to_return.append(bullet)

        # Retornar projéteis inativos ao pool
        for bullet in bullets_to_return:
            self.return_bullet(bullet)

    def get_active_bullets(self) -> List[Bullet]:
        """
        Obter lista de projéteis ativos.
        Returns:
            Lista de projéteis ativos
        """
        return self.active_bullets.copy()

    def clear_all(self):
        """Limpar todos os projéteis ativos."""
        for bullet in self.active_bullets[:]:
            self.return_bullet(bullet)

    def get_stats(self) -> dict:
        """
        Obter estatísticas do pool.
        Returns:
            Dicionário com estatísticas
        """
        return {
            'total_bullets': len(self.pool),
            'active_bullets': len(self.active_bullets),
            'inactive_bullets': len(self.inactive_bullets),
            'pool_usage': len(self.active_bullets) / len(self.pool) * 100
        }


class CollisionOptimizer:
    """
    Sistema otimizado de detecção de colisões.
    Combina QuadTree com Object Pooling para otimizar o processamento
    de colisões entre muitos objetos.
    """

    def __init__(self, bounds, max_objects: int = 10, max_levels: int = 5):
        """
        Inicializar otimizador de colisões.
        Args:
            bounds: Limites da área de jogo
            max_objects: Objetos máximos por nó da QuadTree
            max_levels: Níveis máximos da QuadTree        """
        self.quadtree = QuadTree(bounds, max_objects, max_levels)
        self.collision_pairs = []

    def clear(self):
        """Limpar estruturas de dados."""
        self.quadtree.clear()
        self.collision_pairs.clear()

    def add_objects(self, objects):
        """
        Adicionar objetos à QuadTree.
        Args:
            objects: Lista de objetos com atributo rect
        """
        for obj in objects:
            if hasattr(obj, 'rect'):
                # Verificar se objeto está ativo (se tiver o atributo)
                # Caso contrário, assumir que está ativo
                if hasattr(obj, 'ativo'):
                    if obj.ativo:
                        self.quadtree.insert(obj)
                else:
                    # Objeto não tem atributo 'ativo', inserir diretamente
                    self.quadtree.insert(obj)

    def get_collision_candidates(self, sprite) -> List:
        """
        Obter candidatos de colisão para um sprite.
        Args:
            sprite: Sprite para verificar colisões
        Returns:
            Lista de sprites que podem colidir
        """
        return self.quadtree.retrieve(sprite)

    def broad_phase_collision(self, group1, group2) -> List:
        """
        Fase ampla de detecção de colisão.
        Args:
            group1: Primeiro grupo de sprites
            group2: Segundo grupo de sprites
        Returns:
            Lista de pares que podem colidir
        """
        collision_candidates = []

        for sprite1 in group1:
            if not (hasattr(sprite1, 'ativo') and sprite1.ativo):
                continue

            nearby_sprites = self.get_collision_candidates(sprite1)

            for sprite2 in nearby_sprites:
                if (sprite2 in group2 and
                    hasattr(sprite2, 'ativo') and sprite2.ativo and
                    sprite1 != sprite2):
                    collision_candidates.append((sprite1, sprite2))

        return collision_candidates

    def narrow_phase_collision(self, collision_candidates) -> List:
        """
        Fase estreita de detecção de colisão.
        Args:
            collision_candidates: Lista de pares candidatos
        Returns:
            Lista de pares que realmente colidem
        """
        actual_collisions = []

        for sprite1, sprite2 in collision_candidates:
            if sprite1.rect.colliderect(sprite2.rect):
                actual_collisions.append((sprite1, sprite2))

        return actual_collisions
