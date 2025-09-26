"""
Sistema de Conquistas do Brawl Stars Clone.
Este módulo implementa objetivos e recompensas que os jogadores podem desbloquear
com base em ações realizadas durante o jogo.
"""

class Conquista:
    """Representa uma conquista no jogo."""

    def __init__(self, nome, descricao, criterio):
        """
        Inicializa uma nova conquista.
        Args:
            nome (str): Nome da conquista
            descricao (str): Descrição da conquista
            criterio (callable): Função que verifica se a conquista foi alcançada
        """
        self.nome = nome
        self.descricao = descricao
        self.criterio = criterio
        self.alcancada = False

    def verificar(self, contexto):
        """
        Verifica se a conquista foi alcançada.
        Args:
            contexto (dict): Informações do estado atual do jogo
        """
        if not self.alcancada and self.criterio(contexto):
            self.alcancada = True
            return True
        return False

class SistemaConquistas:
    """Gerencia todas as conquistas do jogo."""

    def __init__(self):
        self.conquistas = []

    def adicionar_conquista(self, conquista):
        """Adiciona uma nova conquista ao sistema."""
        self.conquistas.append(conquista)

    def verificar_conquistas(self, contexto):
        """Verifica todas as conquistas com base no contexto atual."""
        desbloqueadas = []
        for conquista in self.conquistas:
            if conquista.verificar(contexto):
                desbloqueadas.append(conquista)
        return desbloqueadas
