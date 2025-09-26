"""
Sistema de Progressão do Brawl Stars Clone.
Gerencia experiência, níveis, Star Powers e troféus dos Brawlers.
"""

import math
import json
import os
from typing import Dict, List, Optional, Tuple

class StarPower:
    """Representa um Star Power que pode ser desbloqueado"""
    def __init__(self, nome: str, descricao: str, efeito: str, nivel_necessario: int):
        self.nome = nome
        self.descricao = descricao
        self.efeito = efeito  # Tipo de efeito (damage, speed, health, etc.)
        self.nivel_necessario = nivel_necessario
        self.ativo = False
        self.valor_bonus = 0

class BrawlerProgressao:
    """Gerencia a progressão individual de um Brawler"""
    def __init__(self, nome: str):
        self.nome = nome
        self.experiencia = 0
        self.nivel = 1
        self.trofeus = 0
        self.melhor_trofeus = 0
        self.partidas_jogadas = 0
        self.vitorias = 0
        self.derrotas = 0
        self.star_powers: List[StarPower] = []
        self.star_power_ativo: Optional[StarPower] = None
        self.estatisticas = {
            'dano_total_causado': 0,
            'dano_total_recebido': 0,
            'inimigos_eliminados': 0,
            'gemas_coletadas': 0,
            'tempo_sobrevivencia_total': 0
        }
        self._inicializar_star_powers()

    def _inicializar_star_powers(self):
        """Inicializa os Star Powers específicos para cada Brawler"""
        star_powers_por_brawler = {
            'Shelly': [
                StarPower('Shell Shock', 'Inimigos atingidos pelo Super ficam mais lentos', 'slow', 7),
                StarPower('Band-Aid', 'Regenera vida quando abaixo de 40%', 'heal', 9)
            ],
            'Nita': [
                StarPower('Bear With Me', 'Nita e seu urso se curam mutuamente', 'heal', 7),
                StarPower('Hyper Bear', 'O urso ataca mais rapidamente', 'attack_speed', 9)
            ],
            'Colt': [
                StarPower('Slick Boots', 'Aumenta a velocidade de movimento', 'speed', 7),
                StarPower('Magnum Special', 'Aumenta o alcance dos ataques', 'range', 9)
            ],
            'Bull': [
                StarPower('Berserker', 'Aumenta velocidade quando com pouca vida', 'rage', 7),
                StarPower('Tough Guy', 'Reduz dano recebido quando com pouca vida', 'defense', 9)
            ],
            'Barley': [
                StarPower('Medical Use', 'Ataques também curam Barley', 'heal', 7),
                StarPower('Extra Noxious', 'Aumenta duração do dano da área', 'duration', 9)
            ],
            'Poco': [
                StarPower('Da Capo!', 'Ataques também curam aliados', 'heal', 7),
                StarPower('Screeching Solo', 'Super causa dano além de curar', 'damage', 9)
            ]
        }

        if self.nome in star_powers_por_brawler:
            self.star_powers = star_powers_por_brawler[self.nome]

    def ganhar_experiencia(self, exp: int):
        """Adiciona experiência e verifica se subiu de nível"""
        self.experiencia += exp
        nivel_anterior = self.nivel
        self.nivel = self._calcular_nivel()

        if self.nivel > nivel_anterior:
            return True  # Subiu de nível
        return False

    def _calcular_nivel(self) -> int:
        """Calcula o nível baseado na experiência total"""
        # Fórmula: nível = floor(sqrt(exp / 100)) + 1
        # Níveis: 1=0exp, 2=100exp, 3=400exp, 4=900exp, 5=1600exp, etc.
        if self.experiencia < 100:
            return 1
        return min(10, int(math.sqrt(self.experiencia / 100)) + 1)

    def experiencia_necessaria_proximo_nivel(self) -> int:
        """Retorna experiência necessária para o próximo nível"""
        if self.nivel >= 10:
            return 0
        proximo_nivel = self.nivel + 1
        exp_necessaria = (proximo_nivel - 1) ** 2 * 100
        return max(0, exp_necessaria - self.experiencia)

    def ganhar_trofeus(self, trofeus: int):
        """Adiciona troféus e atualiza recorde"""
        self.trofeus += trofeus
        if self.trofeus > self.melhor_trofeus:
            self.melhor_trofeus = self.trofeus

    def perder_trofeus(self, trofeus: int):
        """Remove troféus (mínimo 0)"""
        self.trofeus = max(0, self.trofeus - trofeus)

    def pode_usar_star_power(self, star_power: StarPower) -> bool:
        """Verifica se pode usar um Star Power"""
        return self.nivel >= star_power.nivel_necessario

    def ativar_star_power(self, star_power: StarPower) -> bool:
        """Ativa um Star Power se possível"""
        if self.pode_usar_star_power(star_power):
            self.star_power_ativo = star_power
            star_power.ativo = True
            return True
        return False

    def registrar_partida(self, vitoria: bool, **kwargs):
        """Registra estatísticas da partida"""
        self.partidas_jogadas += 1
        if vitoria:
            self.vitorias += 1
        else:
            self.derrotas += 1

        # Atualizar estatísticas específicas
        for stat, valor in kwargs.items():
            if stat in self.estatisticas:
                self.estatisticas[stat] += valor

    def get_win_rate(self) -> float:
        """Retorna a taxa de vitória em porcentagem"""
        if self.partidas_jogadas == 0:
            return 0.0
        return (self.vitorias / self.partidas_jogadas) * 100

    def get_stats_resumo(self) -> Dict:
        """Retorna resumo das estatísticas"""
        return {
            'nivel': self.nivel,
            'experiencia': self.experiencia,
            'trofeus': self.trofeus,
            'melhor_trofeus': self.melhor_trofeus,
            'partidas': self.partidas_jogadas,
            'vitorias': self.vitorias,
            'derrotas': self.derrotas,
            'win_rate': round(self.get_win_rate(), 1),
            'star_power_ativo': self.star_power_ativo.nome if self.star_power_ativo else None
        }

class SistemaProgressao:
    """Sistema principal de progressão"""
    def __init__(self):
        self.brawlers: Dict[str, BrawlerProgressao] = {}
        self.arquivo_save = 'progressao.json'
        self.carregar_progressao()

    def get_brawler(self, nome: str) -> BrawlerProgressao:
        """Obtém ou cria progressão para um Brawler"""
        if nome not in self.brawlers:
            self.brawlers[nome] = BrawlerProgressao(nome)
        return self.brawlers[nome]

    def calcular_experiencia_partida(self, vitoria: bool, tempo_partida: float,
                                   dano_causado: int, inimigos_eliminados: int,
                                   gemas_coletadas: int) -> int:
        """Calcula experiência ganha em uma partida"""
        exp_base = 50 if vitoria else 25
        exp_tempo = int(tempo_partida / 10)  # 1 exp por 10 segundos
        exp_dano = int(dano_causado / 50)    # 1 exp por 50 de dano
        exp_kills = inimigos_eliminados * 10  # 10 exp por kill
        exp_gemas = gemas_coletadas * 5       # 5 exp por gema
        return exp_base + exp_tempo + exp_dano + exp_kills + exp_gemas

    def calcular_trofeus_partida(self, vitoria: bool, nivel_brawler: int) -> int:
        """Calcula troféus ganhos/perdidos em uma partida"""
        if vitoria:
            return max(8, 15 - nivel_brawler)  # Mais troféus em níveis baixos
        else:
            return max(5, 10 - nivel_brawler // 2)  # Perde menos troféus em níveis altos

    def processar_fim_partida(self, nome_brawler: str, vitoria: bool,
                            tempo_partida: float, **stats):
        """Processa o fim de uma partida e atualiza progressão"""
        brawler = self.get_brawler(nome_brawler)

        # Calcular experiência
        exp_ganha = self.calcular_experiencia_partida(
            vitoria, tempo_partida,
            stats.get('dano_causado', 0),
            stats.get('inimigos_eliminados', 0),
            stats.get('gemas_coletadas', 0)
        )

        # Calcular troféus
        trofeus = self.calcular_trofeus_partida(vitoria, brawler.nivel)

        # Aplicar mudanças
        subiu_nivel = brawler.ganhar_experiencia(exp_ganha)
        if vitoria:
            brawler.ganhar_trofeus(trofeus)
        else:
            brawler.perder_trofeus(trofeus)

        # Registrar estatísticas
        brawler.registrar_partida(vitoria, **stats)

        # Salvar progresso
        self.salvar_progressao()

        return {
            'exp_ganha': exp_ganha,
            'trofeus_mudanca': trofeus if vitoria else -trofeus,
            'subiu_nivel': subiu_nivel,
            'novo_nivel': brawler.nivel,
            'novos_trofeus': brawler.trofeus
        }

    def get_star_powers_disponiveis(self, nome_brawler: str) -> List[StarPower]:
        """Retorna Star Powers disponíveis para um Brawler"""
        brawler = self.get_brawler(nome_brawler)
        return [sp for sp in brawler.star_powers if brawler.pode_usar_star_power(sp)]

    def get_ranking_brawlers(self) -> List[Tuple[str, int]]:
        """Retorna ranking dos Brawlers por troféus"""
        ranking = [(nome, brawler.trofeus) for nome, brawler in self.brawlers.items()]
        return sorted(ranking, key=lambda x: x[1], reverse=True)

    def salvar_progressao(self):
        """Salva progressão em arquivo JSON"""
        try:
            dados = {}
            for nome, brawler in self.brawlers.items():
                dados[nome] = {
                    'experiencia': brawler.experiencia,
                    'nivel': brawler.nivel,
                    'trofeus': brawler.trofeus,
                    'melhor_trofeus': brawler.melhor_trofeus,
                    'partidas_jogadas': brawler.partidas_jogadas,
                    'vitorias': brawler.vitorias,
                    'derrotas': brawler.derrotas,
                    'star_power_ativo': brawler.star_power_ativo.nome if brawler.star_power_ativo else None,
                    'estatisticas': brawler.estatisticas
                }

            with open(self.arquivo_save, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
        except (OSError, IOError, json.JSONDecodeError) as e:
            print(f"Erro ao salvar progressão: {e}")

    def carregar_progressao(self):
        """Carrega progressão do arquivo JSON"""
        try:
            if os.path.exists(self.arquivo_save):
                with open(self.arquivo_save, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                for nome, info in dados.items():
                    brawler = BrawlerProgressao(nome)
                    brawler.experiencia = info.get('experiencia', 0)
                    brawler.nivel = info.get('nivel', 1)
                    brawler.trofeus = info.get('trofeus', 0)
                    brawler.melhor_trofeus = info.get('melhor_trofeus', 0)
                    brawler.partidas_jogadas = info.get('partidas_jogadas', 0)
                    brawler.vitorias = info.get('vitorias', 0)
                    brawler.derrotas = info.get('derrotas', 0)
                    brawler.estatisticas = info.get('estatisticas', brawler.estatisticas)

                    # Reativar Star Power se existir
                    star_power_ativo = info.get('star_power_ativo')
                    if star_power_ativo:
                        for sp in brawler.star_powers:
                            if sp.nome == star_power_ativo:
                                brawler.ativar_star_power(sp)
                                break

                    self.brawlers[nome] = brawler
        except (OSError, IOError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar progressão: {e}")

    def resetar_progressao(self):
        """Reseta toda a progressão"""
        self.brawlers.clear()
        if os.path.exists(self.arquivo_save):
            os.remove(self.arquivo_save)

# Instância global do sistema
sistema_progressao = SistemaProgressao()
