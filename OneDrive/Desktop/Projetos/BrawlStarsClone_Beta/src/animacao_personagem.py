"""
Sistema de animações de personagem do Brawl Stars Clone.
Este módulo implementa um sistema completo de animações para personagens,
incluindo animações idle, movimento, dano e celebrações de vitória.
Cada personagem possui animações únicas baseadas em suas características.
"""

import math
import pygame
from src.config import TAMANHO_JOGADOR
from src.sprite_renderer import SpriteRenderer
from src.pygame_constants import SRCALPHA

class EstadoAnimacao:
    """Estados possíveis de animação do personagem"""
    IDLE = "idle"
    MOVIMENTO = "movimento"
    DANO = "dano"
    VITORIA = "vitoria"
    ATAQUE = "ataque"

class AnimacaoPersonagem:
    """Gerenciador de animações para personagens"""

    def __init__(self, personagem):
        self.personagem = personagem
        self.estado_atual = EstadoAnimacao.IDLE
        self.tempo_animacao = 0.0
        self.tempo_estado = 0.0
        self.frame_atual = 0
        self.duracao_frame = 0.15  # Duração de cada frame em segundos

        # Sprites base para diferentes estados
        self.sprites_originais = {}
        self.sprites_animados = {}

        # Parâmetros de animação únicos por personagem
        self._definir_parametros_personagem()

        # Efeitos de dano
        self.tempo_dano = 0.0
        self.duracao_dano = 0.5

        # Efeitos de vitória
        self.tempo_vitoria = 0.0
        self.duracao_vitoria = 3.0

        # Sistema de frames de animação únicos
        self.frames_idle = []
        self.frames_movimento = []
        self.animacao_dano_especial = {}
        self.animacao_vitoria_especial = {}
        self.ciclo_atual = 0

        # Estados de controle
        self.venceu_jogo = False
        self.recebeu_dano_recente = False

        # Cache de sprites
        self.cache_sprites = {}

        # Gerar sprites para todos os estados
        self._gerar_sprites_base()

    def _gerar_sprites_base(self):
        """Gera sprites base para todos os estados de animação"""
        nome = self.personagem.nome
        cor_principal = self.personagem.cor_principal
        cor_secundaria = self.personagem.cor_secundaria

        # Sprite original
        self.sprites_originais[EstadoAnimacao.IDLE] = SpriteRenderer.criar_sprite_personagem(
            nome, cor_principal, cor_secundaria, TAMANHO_JOGADOR
        )

        # Variações para movimento
        self.sprites_originais[EstadoAnimacao.MOVIMENTO] = self._criar_sprite_movimento(
            nome, cor_principal, cor_secundaria
        )

        # Sprite de dano (com efeito vermelho)
        self.sprites_originais[EstadoAnimacao.DANO] = self._criar_sprite_dano(
            nome, cor_principal, cor_secundaria
        )

        # Sprite de vitória (com brilho)
        self.sprites_originais[EstadoAnimacao.VITORIA] = self._criar_sprite_vitoria(
            nome, cor_principal, cor_secundaria
        )

        # Sprite de ataque
        self.sprites_originais[EstadoAnimacao.ATAQUE] = self._criar_sprite_ataque(
            nome, cor_principal, cor_secundaria
        )

    def _criar_sprite_movimento(self, nome, cor_principal, cor_secundaria):
        """Cria sprite com pequenas modificações para movimento"""
        sprite_base = SpriteRenderer.criar_sprite_personagem(
            nome, cor_principal, cor_secundaria, TAMANHO_JOGADOR
        )
        # Adicionar linhas de movimento
        sprite_movimento = pygame.Surface((TAMANHO_JOGADOR, TAMANHO_JOGADOR), SRCALPHA)
        sprite_movimento.blit(sprite_base, (0, 0))

        # Adicionar efeito de movimento (linhas atrás)
        for i in range(3):
            alpha = 100 - i * 30
            cor_linha = (*cor_principal, alpha)
            pygame.draw.line(sprite_movimento, cor_linha,
                           (2 + i, TAMANHO_JOGADOR // 2),
                           (8 + i, TAMANHO_JOGADOR // 2), 2)

        return sprite_movimento

    def _criar_sprite_dano(self, nome, cor_principal, cor_secundaria):
        """Cria sprite com efeito de dano (vermelho)"""
        sprite_base = SpriteRenderer.criar_sprite_personagem(
            nome, cor_principal, cor_secundaria, TAMANHO_JOGADOR
        )        # Aplicar overlay vermelho
        sprite_dano = pygame.Surface((TAMANHO_JOGADOR, TAMANHO_JOGADOR), SRCALPHA)
        sprite_dano.blit(sprite_base, (0, 0))
        overlay = pygame.Surface((TAMANHO_JOGADOR, TAMANHO_JOGADOR), SRCALPHA)
        overlay.fill((255, 0, 0, 80))
        sprite_dano.blit(overlay, (0, 0))
        return sprite_dano

    def _criar_sprite_vitoria(self, nome, cor_principal, cor_secundaria):
        """Cria sprite com efeito de vitória (brilho dourado)"""
        sprite_base = SpriteRenderer.criar_sprite_personagem(
            nome, cor_principal, cor_secundaria, TAMANHO_JOGADOR
        )

        # Adicionar brilho dourado
        sprite_vitoria = pygame.Surface((TAMANHO_JOGADOR + 8, TAMANHO_JOGADOR + 8), SRCALPHA)

        # Halo dourado
        centro = (TAMANHO_JOGADOR + 8) // 2
        pygame.draw.circle(sprite_vitoria, (255, 215, 0, 100),
                         (centro, centro), TAMANHO_JOGADOR // 2 + 4)
        pygame.draw.circle(sprite_vitoria, (255, 255, 0, 60),
                         (centro, centro), TAMANHO_JOGADOR // 2 + 6)

        # Sprite base no centro
        sprite_vitoria.blit(sprite_base, (4, 4))
        return sprite_vitoria

    def _criar_sprite_ataque(self, nome, cor_principal, cor_secundaria):
        """Cria sprite com efeito de ataque"""
        sprite_base = SpriteRenderer.criar_sprite_personagem(
            nome, cor_principal, cor_secundaria, TAMANHO_JOGADOR
        )

        # Adicionar efeito de energia
        sprite_ataque = pygame.Surface((TAMANHO_JOGADOR, TAMANHO_JOGADOR), SRCALPHA)
        sprite_ataque.blit(sprite_base, (0, 0))

        # Adicionar aura de energia
        centro = TAMANHO_JOGADOR // 2
        pygame.draw.circle(sprite_ataque, (*cor_principal, 120),
                         (centro, centro), centro + 2, 2)
        return sprite_ataque

    def _definir_parametros_personagem(self):
        """Define parâmetros únicos de animação baseados no personagem"""
        nome = self.personagem.nome

        if nome == "Shelly":
            # Cowgirl confiante - movimentos firmes
            self.amplitude_idle = 1.5
            self.velocidade_idle = 1.8
            self.amplitude_movimento = 3.0
            self.velocidade_movimento = 6.0
            self.estilo_idle = "confiante"
            self.estilo_movimento = "determinado"
            self.reacao_dano = "resistente"
            self.celebracao = "vitoriosa"

        elif nome == "Nita":
            # Xamã tribal - movimentos naturais
            self.amplitude_idle = 2.5
            self.velocidade_idle = 1.5
            self.amplitude_movimento = 4.5
            self.velocidade_movimento = 5.0
            self.estilo_idle = "tribal"
            self.estilo_movimento = "selvagem"
            self.reacao_dano = "feroz"
            self.celebracao = "ritual"

        elif nome == "Colt":
            # Atirador elegante - movimentos precisos
            self.amplitude_idle = 1.0
            self.velocidade_idle = 2.2
            self.amplitude_movimento = 2.5
            self.velocidade_movimento = 7.0
            self.estilo_idle = "elegante"
            self.estilo_movimento = "preciso"
            self.reacao_dano = "elegante"
            self.celebracao = "estilosa"

        elif nome == "Bull":
            # Motoqueiro pesado - movimentos robustos
            self.amplitude_idle = 3.0
            self.velocidade_idle = 1.2
            self.amplitude_movimento = 5.0
            self.velocidade_movimento = 4.0
            self.estilo_idle = "imponente"
            self.estilo_movimento = "pesado"
            self.reacao_dano = "inabalavel"
            self.celebracao = "dominante"

        elif nome == "Barley":
            # Robô bartender - movimentos mecânicos
            self.amplitude_idle = 1.8
            self.velocidade_idle = 3.0
            self.amplitude_movimento = 3.2
            self.velocidade_movimento = 8.5
            self.estilo_idle = "mecanico"
            self.estilo_movimento = "robotico"
            self.reacao_dano = "sparks"
            self.celebracao = "computational"

        elif nome == "Poco":
            # Músico esqueleto - movimentos rítmicos
            self.amplitude_idle = 2.8
            self.velocidade_idle = 2.5
            self.amplitude_movimento = 4.8
            self.velocidade_movimento = 6.5
            self.estilo_idle = "ritmico"
            self.estilo_movimento = "danca"
            self.reacao_dano = "ossos"
            self.celebracao = "musical"
        else:
            # Padrão
            self.amplitude_idle = 2.0
            self.velocidade_idle = 2.0
            self.amplitude_movimento = 4.0
            self.velocidade_movimento = 8.0
            self.estilo_idle = "padrao"
            self.estilo_movimento = "padrao"
            self.reacao_dano = "padrao"
            self.celebracao = "padrao"

    def definir_estado(self, novo_estado):
        """Define o estado atual da animação"""
        if novo_estado != self.estado_atual:
            self.estado_atual = novo_estado
            self.tempo_estado = 0.0
            self.frame_atual = 0

            # Estados especiais
            if novo_estado == EstadoAnimacao.DANO:
                self.tempo_dano = self.duracao_dano
            elif novo_estado == EstadoAnimacao.VITORIA:
                self.tempo_vitoria = self.duracao_vitoria

    def update(self, dt, esta_movendo=False, recebeu_dano=False, venceu=False):
        """Atualiza a animação baseada no estado atual"""
        self.tempo_animacao += dt
        self.tempo_estado += dt

        # Determinar estado baseado nas condições
        if recebeu_dano and self.tempo_dano <= 0:
            self.definir_estado(EstadoAnimacao.DANO)
        elif venceu:
            self.definir_estado(EstadoAnimacao.VITORIA)
        elif esta_movendo:
            self.definir_estado(EstadoAnimacao.MOVIMENTO)
        else:
            # Voltar ao idle se não há ações especiais
            if self.estado_atual in [EstadoAnimacao.DANO, EstadoAnimacao.ATAQUE]:
                if self.tempo_dano <= 0:
                    self.definir_estado(EstadoAnimacao.IDLE)
            elif self.estado_atual == EstadoAnimacao.MOVIMENTO and not esta_movendo:
                self.definir_estado(EstadoAnimacao.IDLE)

        # Atualizar timers
        if self.tempo_dano > 0:
            self.tempo_dano -= dt

        if self.tempo_vitoria > 0:
            self.tempo_vitoria -= dt

    def obter_sprite_atual(self):
        """Obtém o sprite atual baseado na animação"""
        cache_key = f"{self.estado_atual}_{int(self.tempo_animacao * 10)}"

        if cache_key in self.cache_sprites:
            return self.cache_sprites[cache_key]

        sprite_base = self.sprites_originais.get(self.estado_atual,
                                               self.sprites_originais[EstadoAnimacao.IDLE])

        # Aplicar transformações baseadas no estado
        sprite_final = self._aplicar_animacao_estado(sprite_base)

        # Cache o resultado
        self.cache_sprites[cache_key] = sprite_final

        # Limpar cache periodicamente
        if len(self.cache_sprites) > 50:
            self.cache_sprites.clear()
        return sprite_final

    def _aplicar_animacao_estado(self, sprite_base):
        """Aplica transformações específicas baseadas no estado atual"""
        if self.estado_atual == EstadoAnimacao.IDLE:
            return self._animar_idle(sprite_base)
        elif self.estado_atual == EstadoAnimacao.MOVIMENTO:
            return self._animar_movimento(sprite_base)
        elif self.estado_atual == EstadoAnimacao.DANO:
            return self._animar_dano(sprite_base)
        elif self.estado_atual == EstadoAnimacao.VITORIA:
            return self._animar_vitoria(sprite_base)
        elif self.estado_atual == EstadoAnimacao.ATAQUE:
            return self._animar_ataque(sprite_base)
        return sprite_base

    def _animar_idle(self, sprite_base):
        """Animação idle única para cada personagem"""
        estilo = getattr(self, 'estilo_idle', 'padrao')

        if estilo == "confiante":  # Shelly
            # Movimento de respiração confiante + balanço de quadril
            offset_y = math.sin(self.tempo_animacao * self.velocidade_idle) * self.amplitude_idle
            offset_x = math.sin(self.tempo_animacao * self.velocidade_idle * 0.5) * 0.8

        elif estilo == "tribal":  # Nita
            # Movimento tribal - balanço como árvore no vento
            offset_y = math.sin(self.tempo_animacao * self.velocidade_idle) * self.amplitude_idle
            offset_x = math.cos(self.tempo_animacao * self.velocidade_idle * 0.7) * 1.2

        elif estilo == "elegante":  # Colt
            # Movimento elegante - postura ereta com leve balanço
            offset_y = math.sin(self.tempo_animacao * self.velocidade_idle) * self.amplitude_idle * 0.6
            offset_x = 0  # Mantém postura ereta

        elif estilo == "imponente":  # Bull
            # Movimento imponente - respiração pesada
            offset_y = math.sin(self.tempo_animacao * self.velocidade_idle) * self.amplitude_idle * 1.2
            offset_x = math.sin(self.tempo_animacao * self.velocidade_idle * 0.3) * 0.5

        elif estilo == "mecanico":  # Barley
            # Movimento mecânico - oscilação precisa
            offset_y = math.sin(self.tempo_animacao * self.velocidade_idle) * self.amplitude_idle * 0.8
            offset_x = math.sin(self.tempo_animacao * self.velocidade_idle * 2) * 0.3

        elif estilo == "ritmico":  # Poco
            # Movimento rítmico - balanço musical
            offset_y = math.sin(self.tempo_animacao * self.velocidade_idle) * self.amplitude_idle * 1.1
            offset_x = math.sin(self.tempo_animacao * self.velocidade_idle * 1.5) * 1.5

        else:  # Padrão
            offset_y = math.sin(self.tempo_animacao * self.velocidade_idle) * self.amplitude_idle
            offset_x = 0

        # Criar sprite com movimento personalizado
        sprite_animado = pygame.Surface((TAMANHO_JOGADOR + 8, TAMANHO_JOGADOR + 8), SRCALPHA)
        sprite_animado.blit(sprite_base, (4 + int(offset_x), 4 + int(offset_y)))

        # Adicionar efeitos especiais baseados no personagem
        self._adicionar_efeitos_idle(sprite_animado, estilo)

        return sprite_animado

    def _animar_movimento(self, sprite_base):
        """Animação de movimento única para cada personagem"""
        estilo = getattr(self, 'estilo_movimento', 'padrao')

        if estilo == "determinado":  # Shelly
            # Movimento determinado - passos firmes
            offset_x = math.sin(self.tempo_animacao * self.velocidade_movimento) * self.amplitude_movimento
            offset_y = abs(math.cos(self.tempo_animacao * self.velocidade_movimento * 2)) * 3
            inclinacao = math.sin(self.tempo_animacao * self.velocidade_movimento) * 5

        elif estilo == "selvagem":  # Nita
            # Movimento selvagem - corrida tribal
            offset_x = math.sin(self.tempo_animacao * self.velocidade_movimento) * self.amplitude_movimento * 1.2
            offset_y = abs(math.sin(self.tempo_animacao * self.velocidade_movimento * 1.5)) * 4
            inclinacao = math.sin(self.tempo_animacao * self.velocidade_movimento * 0.8) * 8

        elif estilo == "preciso":  # Colt
            # Movimento preciso - passos controlados
            offset_x = math.sin(self.tempo_animacao * self.velocidade_movimento) * self.amplitude_movimento * 0.8
            offset_y = abs(math.cos(self.tempo_animacao * self.velocidade_movimento * 2.5)) * 2
            inclinacao = 0  # Mantém postura

        elif estilo == "pesado":  # Bull
            # Movimento pesado - pisadas fortes
            offset_x = math.sin(self.tempo_animacao * self.velocidade_movimento * 0.8) * self.amplitude_movimento * 0.7
            offset_y = abs(math.cos(self.tempo_animacao * self.velocidade_movimento)) * 5
            inclinacao = math.sin(self.tempo_animacao * self.velocidade_movimento * 0.6) * 4

        elif estilo == "robotico":  # Barley
            # Movimento robótico - mecânico preciso
            offset_x = math.sin(self.tempo_animacao * self.velocidade_movimento) * self.amplitude_movimento * 0.9
            offset_y = abs(math.sin(self.tempo_animacao * self.velocidade_movimento * 3)) * 2.5
            inclinacao = math.sin(self.tempo_animacao * self.velocidade_movimento * 2) * 3

        elif estilo == "danca":  # Poco
            # Movimento de dança - rítmico e fluido
            offset_x = math.sin(self.tempo_animacao * self.velocidade_movimento) * self.amplitude_movimento * 1.3
            offset_y = abs(math.sin(self.tempo_animacao * self.velocidade_movimento * 1.2)) * 4
            inclinacao = math.sin(self.tempo_animacao * self.velocidade_movimento * 1.8) * 10

        else:  # Padrão
            offset_x = math.sin(self.tempo_animacao * self.velocidade_movimento) * self.amplitude_movimento
            offset_y = abs(math.cos(self.tempo_animacao * self.velocidade_movimento)) * 2
            inclinacao = 0

        # Criar sprite com movimento personalizado
        sprite_animado = pygame.Surface((TAMANHO_JOGADOR + 16, TAMANHO_JOGADOR + 8), SRCALPHA)

        # Aplicar rotação se necessário
        if inclinacao != 0:
            sprite_rotacionado = pygame.transform.rotate(sprite_base, inclinacao)
            sprite_animado.blit(sprite_rotacionado, (8 + int(offset_x), 4 + int(offset_y)))
        else:
            sprite_animado.blit(sprite_base, (8 + int(offset_x), 4 + int(offset_y)))

        # Adicionar efeitos especiais de movimento
        self._adicionar_efeitos_movimento(sprite_animado, estilo)

        return sprite_animado

    def _animar_dano(self, sprite_base):
        """Animação de dano única para cada personagem"""
        if self.tempo_dano <= 0:
            return sprite_base

        estilo = getattr(self, 'reacao_dano', 'padrao')
        intensidade = self.tempo_dano / self.duracao_dano

        if estilo == "resistente":  # Shelly
            # Reação resistente - recua levemente mas mantém postura
            offset_x = intensidade * 3 * math.sin(self.tempo_animacao * 25)
            offset_y = intensidade * 1 * math.cos(self.tempo_animacao * 20)
            flash_intensidade = 120

        elif estilo == "feroz":  # Nita
            # Reação feroz - movimento selvagem de dor
            offset_x = intensidade * 6 * math.sin(self.tempo_animacao * 35)
            offset_y = intensidade * 4 * math.cos(self.tempo_animacao * 30)
            flash_intensidade = 140

        elif estilo == "elegante":  # Colt
            # Reação elegante - recua com estilo
            offset_x = intensidade * 2 * math.sin(self.tempo_animacao * 20)
            offset_y = intensidade * 1 * math.cos(self.tempo_animacao * 18)
            flash_intensidade = 100

        elif estilo == "inabalavel":  # Bull
            # Reação inabalável - quase não se move
            offset_x = intensidade * 1 * math.sin(self.tempo_animacao * 15)
            offset_y = intensidade * 0.5 * math.cos(self.tempo_animacao * 12)
            flash_intensidade = 80

        elif estilo == "sparks":  # Barley
            # Reação mecânica - faíscas e trepidação
            offset_x = intensidade * 5 * math.sin(self.tempo_animacao * 40)
            offset_y = intensidade * 3 * math.cos(self.tempo_animacao * 45)
            flash_intensidade = 160

        elif estilo == "ossos":  # Poco
            # Reação de esqueleto - ossos chacoalhando
            offset_x = intensidade * 7 * math.sin(self.tempo_animacao * 50)
            offset_y = intensidade * 5 * math.cos(self.tempo_animacao * 60)
            flash_intensidade = 130

        else:  # Padrão
            offset_x = intensidade * 4 * math.sin(self.tempo_animacao * 20)
            offset_y = intensidade * 2 * math.cos(self.tempo_animacao * 15)
            flash_intensidade = 120

        sprite_animado = pygame.Surface((TAMANHO_JOGADOR + 16, TAMANHO_JOGADOR + 12), SRCALPHA)
        sprite_animado.blit(sprite_base, (8 + int(offset_x), 6 + int(offset_y)))

        # Adicionar flash de dano personalizado
        self._adicionar_flash_dano(sprite_animado, estilo, flash_intensidade, intensidade)

        return sprite_animado

    def _animar_vitoria(self, sprite_base):
        """Animação de vitória única para cada personagem"""
        if self.tempo_vitoria <= 0:
            return sprite_base

        estilo = getattr(self, 'celebracao', 'padrao')
        progresso = 1.0 - (self.tempo_vitoria / self.duracao_vitoria)

        if estilo == "vitoriosa":  # Shelly
            # Celebração vitoriosa - pose de cowgirl
            angulo = math.sin(self.tempo_animacao * 3) * 15
            escala = 1.0 + 0.3 * math.sin(self.tempo_animacao * 2)
            movimento_y = math.sin(self.tempo_animacao * 4) * 8

        elif estilo == "ritual":  # Nita
            # Celebração ritual - dança tribal
            angulo = math.sin(self.tempo_animacao * 4) * 25
            escala = 1.0 + 0.4 * math.sin(self.tempo_animacao * 3)
            movimento_y = math.sin(self.tempo_animacao * 5) * 12

        elif estilo == "estilosa":  # Colt
            # Celebração estilosa - pose elegante
            angulo = math.sin(self.tempo_animacao * 2) * 8
            escala = 1.0 + 0.2 * math.sin(self.tempo_animacao * 2.5)
            movimento_y = math.sin(self.tempo_animacao * 3) * 5

        elif estilo == "dominante":  # Bull
            # Celebração dominante - flexão de músculos
            angulo = math.sin(self.tempo_animacao * 1.5) * 5
            escala = 1.0 + 0.5 * math.sin(self.tempo_animacao * 1.8)
            movimento_y = math.sin(self.tempo_animacao * 2) * 3

        elif estilo == "computational":  # Barley
            # Celebração computacional - rotação mecânica
            angulo = self.tempo_animacao * 90  # Rotação contínua
            escala = 1.0 + 0.2 * math.sin(self.tempo_animacao * 6)
            movimento_y = math.sin(self.tempo_animacao * 8) * 4

        elif estilo == "musical":  # Poco
            # Celebração musical - dança rítmica
            angulo = math.sin(self.tempo_animacao * 6) * 30
            escala = 1.0 + 0.6 * math.sin(self.tempo_animacao * 4)
            movimento_y = math.sin(self.tempo_animacao * 7) * 15

        else:  # Padrão
            angulo = math.sin(self.tempo_animacao * 2) * 10
            escala = 1.0 + 0.2 * math.sin(self.tempo_animacao * 4)
            movimento_y = math.sin(self.tempo_animacao * 3) * 6

        # Aplicar transformações
        sprite_rotacionado = pygame.transform.rotate(sprite_base, angulo)
        sprite_escalado = pygame.transform.scale(sprite_rotacionado,
                                               (int(sprite_rotacionado.get_width() * escala),
                                                int(sprite_rotacionado.get_height() * escala)))

        # Criar sprite final com movimento vertical
        sprite_final = pygame.Surface((sprite_escalado.get_width() + 20,
                                     sprite_escalado.get_height() + 40), SRCALPHA)

        sprite_final.blit(sprite_escalado, (10, 20 + int(movimento_y)))

        # Adicionar efeitos especiais de vitória
        self._adicionar_efeitos_vitoria(sprite_final, estilo, progresso)

        return sprite_final

    def _animar_ataque(self, sprite_base):
        """Animação de ataque - impulso para frente"""
        # Movimento para frente rápido
        progresso = min(self.tempo_estado / 0.3, 1.0)  # 0.3 segundos de duração
        offset_x = math.sin(progresso * math.pi) * 6
        sprite_animado = pygame.Surface((TAMANHO_JOGADOR + 12, TAMANHO_JOGADOR), SRCALPHA)
        sprite_animado.blit(sprite_base, (6 + int(offset_x), 0))
        return sprite_animado

    def iniciar_animacao_ataque(self):
        """Inicia a animação de ataque"""
        self.definir_estado(EstadoAnimacao.ATAQUE)

    def iniciar_celebracao_vitoria(self):
        """Inicia a animação de celebração de vitória"""
        self.definir_estado(EstadoAnimacao.VITORIA)
        self.venceu_jogo = True

    def resetar_animacoes(self):
        """Reseta todas as animações para o estado inicial"""
        self.estado_atual = EstadoAnimacao.IDLE
        self.tempo_animacao = 0.0
        self.tempo_estado = 0.0
        self.tempo_dano = 0.0
        self.tempo_vitoria = 0.0
        self.venceu_jogo = False
        self.recebeu_dano_recente = False

    def obter_animacao_ativa(self):
        """Retorna informações sobre a animação atualmente ativa"""
        return {
            'estado': self.estado_atual,
            'estilo_idle': getattr(self, 'estilo_idle', 'padrao'),
            'estilo_movimento': getattr(self, 'estilo_movimento', 'padrao'),
            'reacao_dano': getattr(self, 'reacao_dano', 'padrao'),
            'celebracao': getattr(self, 'celebracao', 'padrao'),
            'progresso_animacao': self.tempo_estado,
            'personagem': self.personagem.nome
        }

    def pode_executar_acao(self):
        """Verifica se o personagem pode executar ações (não está em animação de dano/vitória)"""
        return self.estado_atual not in [EstadoAnimacao.DANO, EstadoAnimacao.VITORIA] or \
               (self.tempo_dano <= 0 and self.tempo_vitoria <= 0)

    def obter_info_animacao(self):
        """Retorna informações sobre a animação atual"""
        return {
            'estado': self.estado_atual,
            'tempo_animacao': self.tempo_animacao,
            'tempo_estado': self.tempo_estado,
            'frame_atual': self.frame_atual
        }

    def _adicionar_efeitos_idle(self, sprite_animado, estilo):
        """Adiciona efeitos visuais especiais para animação idle"""
        if estilo == "confiante":  # Shelly
            # Brilho sutil de confiança
            if math.sin(self.tempo_animacao * 2) > 0.7:
                overlay = pygame.Surface(sprite_animado.get_size(), SRCALPHA)
                overlay.fill((255, 255, 200, 20))
                sprite_animado.blit(overlay, (0, 0))

        elif estilo == "tribal":  # Nita
            # Partículas naturais
            if int(self.tempo_animacao * 5) % 3 == 0:
                for i in range(2):
                    x = sprite_animado.get_width() // 2 + (i - 0.5) * 10
                    y = sprite_animado.get_height() // 2 + math.sin(self.tempo_animacao * 3 + i) * 5
                    pygame.draw.circle(sprite_animado, (34, 139, 34, 50), (int(x), int(y)), 2)

        elif estilo == "mecanico":  # Barley
            # Indicadores LED
            if int(self.tempo_animacao * 8) % 2 == 0:
                led_x = sprite_animado.get_width() // 2 + 8
                led_y = sprite_animado.get_height() // 2 - 5
                pygame.draw.circle(sprite_animado, (0, 255, 0), (led_x, led_y), 2)

        elif estilo == "ritmico":  # Poco
            # Notas musicais flutuantes
            if int(self.tempo_animacao * 4) % 2 == 0:
                nota_x = sprite_animado.get_width() // 2 + math.sin(self.tempo_animacao * 6) * 15
                nota_y = sprite_animado.get_height() // 2 - 15
                pygame.draw.circle(sprite_animado, (138, 43, 226, 80), (int(nota_x), int(nota_y)), 3)

    def _adicionar_efeitos_movimento(self, sprite_animado, estilo):
        """Adiciona efeitos visuais especiais para animação de movimento"""
        if estilo == "determinado":  # Shelly
            # Rastro de poeira
            for i in range(3):
                x = 5 + i * 3
                y = sprite_animado.get_height() - 5
                alpha = 80 - i * 25
                pygame.draw.circle(sprite_animado, (139, 69, 19, alpha), (x, y), 3 - i)

        elif estilo == "selvagem":  # Nita
            # Folhas voando
            for i in range(4):
                x = 8 + i * 2 + math.sin(self.tempo_animacao * 10 + i) * 3
                y = sprite_animado.get_height() - 8 + math.cos(self.tempo_animacao * 8 + i) * 4
                pygame.draw.ellipse(sprite_animado, (34, 139, 34, 60), (int(x), int(y), 4, 2))

        elif estilo == "robotico":  # Barley
            # Faíscas mecânicas
            if int(self.tempo_animacao * 12) % 3 == 0:
                for i in range(2):
                    x = sprite_animado.get_width() // 2 + (i - 0.5) * 8
                    y = sprite_animado.get_height() - 3
                    pygame.draw.circle(sprite_animado, (255, 255, 0, 120), (int(x), int(y)), 1)

        elif estilo == "danca":  # Poco
            # Rastro musical colorido
            cores = [(255, 0, 255), (0, 255, 255), (255, 255, 0)]
            for i, cor in enumerate(cores):
                x = 6 + i * 4
                y = sprite_animado.get_height() // 2 + math.sin(self.tempo_animacao * 5 + i) * 6
                pygame.draw.circle(sprite_animado, (*cor, 60), (x, int(y)), 2)

    def _adicionar_flash_dano(self, sprite_animado, estilo, flash_intensidade, intensidade):
        """Adiciona flash de dano personalizado por personagem"""
        if estilo == "sparks":  # Barley
            # Faíscas elétricas
            overlay = pygame.Surface(sprite_animado.get_size(), SRCALPHA)
            overlay.fill((255, 255, 0, int(flash_intensidade * intensidade)))
            sprite_animado.blit(overlay, (0, 0))

            # Faíscas pontuais
            for i in range(5):
                x = sprite_animado.get_width() // 2 + math.sin(self.tempo_animacao * 30 + i) * 10
                y = sprite_animado.get_height() // 2 + math.cos(self.tempo_animacao * 25 + i) * 8
                pygame.draw.circle(sprite_animado, (255, 255, 255), (int(x), int(y)), 2)

        elif estilo == "ossos":  # Poco
            # Flash branco de ossos
            overlay = pygame.Surface(sprite_animado.get_size(), SRCALPHA)
            overlay.fill((255, 255, 255, int(flash_intensidade * intensidade * 0.8)))
            sprite_animado.blit(overlay, (0, 0))

        else:
            # Flash vermelho padrão
            overlay = pygame.Surface(sprite_animado.get_size(), SRCALPHA)
            overlay.fill((255, 0, 0, int(flash_intensidade * intensidade * 0.6)))
            sprite_animado.blit(overlay, (0, 0))

    def _adicionar_efeitos_vitoria(self, sprite_final, estilo, _progresso):
        """Adiciona efeitos especiais de vitória por personagem"""
        if estilo == "vitoriosa":  # Shelly
            # Estrelas douradas
            for i in range(6):
                angulo = (self.tempo_animacao * 2 + i * 60) % 360
                raio = 25 + math.sin(self.tempo_animacao * 3) * 5
                x = sprite_final.get_width() // 2 + math.cos(math.radians(angulo)) * raio
                y = sprite_final.get_height() // 2 + math.sin(math.radians(angulo)) * raio
                pygame.draw.circle(sprite_final, (255, 215, 0), (int(x), int(y)), 3)

        elif estilo == "ritual":  # Nita
            # Círculo mágico verde
            centro = (sprite_final.get_width() // 2, sprite_final.get_height() // 2)
            raio = 30 + math.sin(self.tempo_animacao * 4) * 8
            pygame.draw.circle(sprite_final, (34, 139, 34, 80), centro, int(raio), 3)

        elif estilo == "computational":  # Barley
            # Código binário flutuante
            if int(self.tempo_animacao * 6) % 2 == 0:
                for i in range(8):
                    x = 15 + (i % 4) * 10
                    y = 15 + (i // 4) * 15 + math.sin(self.tempo_animacao * 5 + i) * 3
                    texto = "1" if i % 2 == 0 else "0"
                    # Simular texto com retângulos pequenos
                    if texto == "1":
                        pygame.draw.rect(sprite_final, (0, 255, 0), (x, int(y), 6, 8))
                    else:
                        pygame.draw.circle(sprite_final, (0, 255, 0), (x + 3, int(y) + 4), 3, 1)

        elif estilo == "musical":  # Poco
            # Ondas musicais coloridas
            cores = [(255, 0, 255), (0, 255, 255), (255, 255, 0), (255, 0, 0)]
            for i, cor in enumerate(cores):
                raio = 20 + i * 8 + math.sin(self.tempo_animacao * 3 + i) * 5
                centro = (sprite_final.get_width() // 2, sprite_final.get_height() // 2)
                pygame.draw.circle(sprite_final, (*cor, 60), centro, int(raio), 2)