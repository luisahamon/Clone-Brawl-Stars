"""
Classe do jogador do Brawl Stars Clone.
Este módulo implementa a lógica do jogador controlável, incluindo movimento,
sistema de tiro, integração com personagens selecionáveis, power-ups temporários,
controles de entrada e mecânicas de combate. Gerencia também os efeitos visuais
e sonoros das ações do jogador.
"""

import math
import pygame
from src.config import (SCREEN_WIDTH, SCREEN_HEIGHT, DURACAO_POWER_UP, TAMANHO_JOGADOR)
from src.pygame_constants import (SRCALPHA, K_SPACE, MOUSEBUTTONDOWN, KEYDOWN, K_Q, K_W,
                                 K_UP, K_S, K_DOWN, K_A, K_LEFT, K_D, K_RIGHT)
from src.bullet import Bullet
from src.characters.personagens import obter_personagem
from src.efeitos_visuais import gerenciador_efeitos
from src.audio_manager import gerenciador_audio
from src.animacao_personagem import AnimacaoPersonagem, EstadoAnimacao
from src.feedback_combate import obter_feedback_combate
from src.super_system import SuperSystem

class Player(pygame.sprite.Sprite):
    """Classe do jogador principal"""

    def __init__(self, x, y, personagem_nome=None):
        super().__init__()        # Carregar dados do personagem
        self.personagem = obter_personagem(personagem_nome)

        # Verificar se o personagem foi carregado corretamente
        if not self.personagem:
            raise ValueError(f"Não foi possível carregar o personagem: {personagem_nome}")
        self.super_system = SuperSystem(self.personagem)

        # Sistema de animações
        self.animacao = AnimacaoPersonagem(self.personagem)

        self.image = pygame.Surface((TAMANHO_JOGADOR, TAMANHO_JOGADOR), SRCALPHA)
        self.image.fill((0, 0, 0, 0))  # Totalmente transparente
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        # Atributos baseados no personagem
        self.vida = self.personagem.vida_maxima
        self.vida_maxima = self.personagem.vida_maxima
        self.velocidade = self.personagem.velocidade
        self.dano_base = self.personagem.dano
        self.cooldown_tiro = self.personagem.cooldown
        self.tipo_tiro = self.personagem.tipo_tiro
        self.ultimo_tiro = 0

        # Power-ups ativos
        self.power_ups_ativos = []        # Habilidades especiais
        self.cooldown_habilidade = 0
        self.efeitos_especiais = {}

        # Controle de animações
        self.esta_movendo = False
        self.recebeu_dano_recente = False
        self.tempo_sem_dano = 0.0
        self.venceu_jogo = False        # Posição para cálculos
        self.pos_x = float(x)
        self.pos_y = float(y)

    def handle_event(self, event, grupo_tiros, grupo_todos, game_instance=None):
        """Gerenciar eventos do jogador"""
        # Verificar se o jogador não está morto (verificação extra de segurança)
        if game_instance and hasattr(game_instance,'jogador_morto') and game_instance.jogador_morto:
            return

        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Botão esquerdo do mouse
                self.atirar(pygame.mouse.get_pos(), grupo_tiros, grupo_todos, game_instance)
        elif event.type == KEYDOWN:
            if event.key == K_Q:  # Habilidade especial (sistema antigo)
                self.usar_habilidade_especial()
            elif event.key == K_SPACE:  # Super (sistema novo autêntico)
                self.usar_super()

    def usar_habilidade_especial(self):
        """Usar habilidade especial do personagem"""
        if self.cooldown_habilidade <= 0:
            resultado = self.personagem.usar_habilidade_especial()
            if resultado:                # Tocar som da habilidade especial
                nome_personagem = getattr(self.personagem, 'nome', 'Shelly').lower()
                som_habilidade = f'habilidade_{nome_personagem}'
                gerenciador_audio.tocar_som(som_habilidade)

                self.cooldown_habilidade = self.personagem.cooldown_habilidade_max
                self.aplicar_efeito_especial(resultado)
                return True
        return False

    def aplicar_efeito_especial(self, efeito):
        """Aplicar efeito da habilidade especial"""
        tipo = efeito.get('tipo')

        # Criar efeito visual na posição do jogador
        gerenciador_efeitos.criar_efeito_habilidade(tipo, self.pos_x, self.pos_y)

        if tipo == 'super_shell':
            self.efeitos_especiais['super_shell'] = 1  # Próximo tiro será super
        elif tipo == 'rajada_balas':
            self.efeitos_especiais['rajada_balas'] = efeito.get('quantidade', 6)
        elif tipo == 'investida':
            self.efeitos_especiais['investida_tempo'] = efeito.get('duracao', 2.0)
            self.velocidade *= efeito.get('velocidade_bonus', 2.0)
        elif tipo == 'melodia_curativa':
            self.curar(efeito.get('cura', 60))
    def update(self, dt, obstaculos, joystick_direcao=None):
        """Atualizar jogador"""
        # Atualizar sistema de Super
        self.super_system.update(dt)

        # Atualizar cooldowns
        if self.ultimo_tiro > 0:
            self.ultimo_tiro -= dt
        if self.cooldown_habilidade > 0:
            self.cooldown_habilidade -= dt

        # Atualizar timer de dano
        if self.tempo_sem_dano > 0:
            self.tempo_sem_dano -= dt
            if self.tempo_sem_dano <= 0:
                self.recebeu_dano_recente = False

        # Atualizar efeitos especiais
        self.atualizar_efeitos_especiais(dt)

        # Input do teclado
        keys = pygame.key.get_pressed()
        dx = dy = 0

        # Priorizar joystick virtual se ativo
        if joystick_direcao and (joystick_direcao[0] != 0 or joystick_direcao[1] != 0):
            dx = joystick_direcao[0] * self.velocidade * dt
            dy = joystick_direcao[1] * self.velocidade * dt
        else:
            # Input do teclado tradicional
            if keys[K_W] or keys[K_UP]:
                dy -= self.velocidade * dt
            if keys[K_S] or keys[K_DOWN]:
                dy += self.velocidade * dt
            if keys[K_A] or keys[K_LEFT]:
                dx -= self.velocidade * dt
            if keys[K_D] or keys[K_RIGHT]:
                dx += self.velocidade * dt

        # Determinar se está se movendo
        self.esta_movendo = abs(dx) > 0.1 or abs(dy) > 0.1

        # Aplicar movimento com verificação de colisão
        self.mover(dx, dy, obstaculos)

        # Atualizar animações
        self.animacao.update(dt, self.esta_movendo, self.recebeu_dano_recente, self.venceu_jogo)

        # Atualizar sprite baseado na animação atual
        sprite_anterior = self.image
        self.image = self.animacao.obter_sprite_atual()

        # Manter a posição do centro mesmo se o sprite mudou de tamanho
        if sprite_anterior.get_size() != self.image.get_size():
            centro_anterior = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = centro_anterior

        # Atualizar power-ups
        self.atualizar_power_ups(dt)

    def atualizar_efeitos_especiais(self, dt):
        """Atualizar efeitos especiais ativos"""
        # Efeito de investida (Bull Super)
        if 'investida' in self.efeitos_especiais:
            self.efeitos_especiais['investida'] -= dt
            if self.efeitos_especiais['investida'] <= 0:
                self.velocidade = self.personagem.velocidade  # Resetar velocidade
                del self.efeitos_especiais['investida']

        # Efeito de chuva de garrafas (Barley Super)
        if 'chuva_garrafas' in self.efeitos_especiais:
            self.efeitos_especiais['chuva_garrafas'] -= dt
            if self.efeitos_especiais['chuva_garrafas'] <= 0:
                del self.efeitos_especiais['chuva_garrafas']

        # Compatibilidade com sistema antigo
        if 'investida_tempo' in self.efeitos_especiais:
            self.efeitos_especiais['investida_tempo'] -= dt
            if self.efeitos_especiais['investida_tempo'] <= 0:
                self.velocidade = self.personagem.velocidade  # Resetar velocidade
                del self.efeitos_especiais['investida_tempo']

    def mover(self, dx, dy, obstaculos):
        """Mover jogador com verificação de colisão"""
        # Calcular nova posição
        nova_pos_x = self.pos_x + dx
        nova_pos_y = self.pos_y + dy

        # Aplicar limites da tela ANTES de mover (prevenção)
        half_width = self.rect.width // 2
        half_height = self.rect.height // 2

        nova_pos_x = max(half_width, min(nova_pos_x, SCREEN_WIDTH - half_width))
        nova_pos_y = max(half_height, min(nova_pos_y, SCREEN_HEIGHT - half_height))

        # Mover horizontalmente
        self.pos_x = nova_pos_x
        self.rect.centerx = int(self.pos_x)

        # Verificar colisão com obstáculos horizontalmente
        for obstaculo in obstaculos:
            if self.rect.colliderect(obstaculo.rect):
                if dx > 0:  # Movendo para direita
                    self.rect.right = obstaculo.rect.left
                else:  # Movendo para esquerda
                    self.rect.left = obstaculo.rect.right
                self.pos_x = self.rect.centerx
                break

        # Mover verticalmente
        self.pos_y = nova_pos_y
        self.rect.centery = int(self.pos_y)

        # Verificar colisão com obstáculos verticalmente
        for obstaculo in obstaculos:
            if self.rect.colliderect(obstaculo.rect):
                if dy > 0:  # Movendo para baixo
                    self.rect.bottom = obstaculo.rect.top
                else:  # Movendo para cima
                    self.rect.top = obstaculo.rect.bottom
                self.pos_y = self.rect.centery
                break        # Verificação final de segurança (caso algo tenha falhado)
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos_x = self.rect.centerx
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.pos_x = self.rect.centerx

        if self.rect.top < 0:
            self.rect.top = 0
            self.pos_y = self.rect.centery
        elif self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.pos_y = self.rect.centery

    def atirar(self, pos_mouse, grupo_tiros, grupo_todos, game_instance=None):
        """Atirar projétil (com suporte a object pool otimizado)"""
        # Verificar se o jogador não está morto (se game_instance disponível)
        if game_instance and hasattr(game_instance,'jogador_morto') and game_instance.jogador_morto:
            return

        if self.ultimo_tiro <= 0:
            # Iniciar animação de ataque
            self.animacao.iniciar_animacao_ataque()
            # Calcular direção
            dx = pos_mouse[0] - self.rect.centerx
            dy = pos_mouse[1] - self.rect.centery

            # Normalizar
            distancia = math.sqrt(dx*dx + dy*dy)
            if distancia > 0:
                dx /= distancia
                dy /= distancia

            # Verificar se é tiro especial
            dano = self.dano_base
            especial = False

            if 'super_shell' in self.efeitos_especiais and self.efeitos_especiais['super_shell'] > 0:
                dano *= 2
                especial = True
                self.efeitos_especiais['super_shell'] -= 1
                if self.efeitos_especiais['super_shell'] <= 0:
                    del self.efeitos_especiais['super_shell'] # Tocar som de tiro baseado no personagem
            nome_personagem = getattr(self.personagem, 'nome', 'Shelly').lower()
            som_tiro = f'tiro_{nome_personagem}'
            gerenciador_audio.tocar_som(som_tiro)  # Criar projétil
            if game_instance and hasattr(game_instance, 'criar_projetil_otimizado'):
                bullet = game_instance.criar_projetil_otimizado(
                    self.rect.centerx + dx * 30,
                    self.rect.centery + dy * 30,
                    dx, dy,
                    dano=dano,
                    velocidade=500,  # Usar mesma velocidade do sistema tradicional
                    de_inimigo=False,
                    tipo_tiro=self.tipo_tiro
                )

                # Marcar se é tiro especial para efeitos visuais
                if bullet and especial:
                    bullet.especial = True
                    bullet.tipo_especial = "super"
            else:
                # Fallback para sistema tradicional
                bullet = Bullet(
                    self.rect.centerx + dx * 30,
                    self.rect.centery + dy * 30,
                    dx, dy,
                    de_inimigo=False,
                    dano=dano,
                    tipo_tiro=self.tipo_tiro
                )

                # Marcar se é tiro especial para efeitos visuais
                if especial:
                    bullet.especial = True
                    bullet.tipo_especial = "super"

                grupo_tiros.add(bullet)
                grupo_todos.add(bullet)

            # Efeito visual para tiro especial
            if especial and bullet:
                gerenciador_efeitos.criar_efeito_tiro_especial('super_shell',
                bullet.rect.centerx, bullet.rect.centery)

            # Verificar rajada de balas
            if 'rajada_balas' in self.efeitos_especiais and self.efeitos_especiais['rajada_balas'] > 0:
                self.ultimo_tiro = 0.1  # Tiro rápido para rajada
                self.efeitos_especiais['rajada_balas'] -= 1
                if self.efeitos_especiais['rajada_balas'] <= 0:
                    del self.efeitos_especiais['rajada_balas']
            else:
                self.ultimo_tiro = self.cooldown_tiro

    def atirar_botao_virtual(self, grupo_tiros, grupo_todos, game_instance=None):
        """Atirar usando o botão virtual com Auto-Aim Inteligente"""
        if self.ultimo_tiro <= 0:
            inimigo_prioritario = None
            maior_prioridade = float('-inf')

            if game_instance and hasattr(game_instance, 'inimigos'):
                for inimigo in game_instance.inimigos:
                    # Verificar se inimigo está vivo
                    vida_inimigo = getattr(inimigo, 'vida', 1)
                    if vida_inimigo <= 0:
                        continue

                    # Predição de movimento (posição futura) - mais eficiente
                    velocidade_x = getattr(inimigo, 'velocidade_x', 0)
                    velocidade_y = getattr(inimigo, 'velocidade_y', 0)
                    tempo_predicao = 0.3  # Reduzido para melhor precisão
                    pos_futura_x = inimigo.rect.centerx + velocidade_x * tempo_predicao
                    pos_futura_y = inimigo.rect.centery + velocidade_y * tempo_predicao

                    # Calcular distância futura diretamente (mais eficiente)
                    dx_futuro = pos_futura_x - self.rect.centerx
                    dy_futuro = pos_futura_y - self.rect.centery
                    distancia_futura_squared = dx_futuro*dx_futuro + dy_futuro*dy_futuro

                    # Calcular prioridade otimizada (evitar divisão por zero)
                    prioridade = 1000000 / (distancia_futura_squared + 1) + 100 / (vida_inimigo + 1)

                    if prioridade > maior_prioridade:
                        maior_prioridade = prioridade
                        inimigo_prioritario = inimigo

            # Se encontrou um inimigo, mirar na posição futura dele (corrigido)
            if inimigo_prioritario:
                # Usar posição futura para melhor precisão
                velocidade_x = getattr(inimigo_prioritario, 'velocidade_x', 0)
                velocidade_y = getattr(inimigo_prioritario, 'velocidade_y', 0)
                tempo_predicao = 0.3

                pos_futura_x = inimigo_prioritario.rect.centerx + velocidade_x * tempo_predicao
                pos_futura_y = inimigo_prioritario.rect.centery + velocidade_y * tempo_predicao

                dx = pos_futura_x - self.rect.centerx
                dy = pos_futura_y - self.rect.centery
            else:
                # Mirar para a direita como padrão
                dx = 1
                dy = 0

            # Normalizar direção
            distancia = math.sqrt(dx*dx + dy*dy)
            if distancia > 0:
                dx /= distancia
                dy /= distancia

            # Criar projétil com dano e efeitos especiais
            dano = self.dano_base
            especial = False

            if 'super_shell' in self.efeitos_especiais and self.efeitos_especiais['super_shell'] > 0:
                dano *= 2
                especial = True
                self.efeitos_especiais['super_shell'] -= 1
                if self.efeitos_especiais['super_shell'] <= 0:
                    del self.efeitos_especiais['super_shell'] # Criar projétil otimizado ou padrão
            if game_instance and hasattr(game_instance, 'criar_projetil_otimizado'):
                bullet = game_instance.criar_projetil_otimizado(
                    self.rect.centerx + dx * 30,
                    self.rect.centery + dy * 30,
                    dx, dy,
                    dano=dano,
                    velocidade=500,  # Usar mesma velocidade do sistema tradicional
                    de_inimigo=False,
                    tipo_tiro=self.tipo_tiro
                )
            else:
                bullet = Bullet(
                    self.rect.centerx + dx * 30,
                    self.rect.centery + dy * 30,
                    dx, dy,
                    de_inimigo=False,
                    dano=dano,
                    tipo_tiro=self.tipo_tiro
                )

            # Marcar se é tiro especial para efeitos visuais
            if especial:
                bullet.especial = True
                bullet.tipo_especial = "super"

            grupo_tiros.add(bullet)
            grupo_todos.add(bullet)

            # Atualizar cooldown
            self.ultimo_tiro = self.cooldown_tiro

    def receber_dano(self, dano, jogo=None):
        """Receber dano"""
        self.vida -= dano

        # Registrar dano recebido na progressão se jogo foi passado
        if jogo and hasattr(jogo, 'registrar_dano_recebido'):
            jogo.registrar_dano_recebido(dano)

        # Carregar Super ao receber dano (sistema autêntico)
        self.super_system.adicionar_carga_hit(dano)

        # Ativar animação de dano específica do personagem
        self.recebeu_dano_recente = True
        self.tempo_sem_dano = 0.5  # Duração da animação de dano
        self.animacao.definir_estado(EstadoAnimacao.DANO)

        # Criar efeitos visuais de dano
        centro_x = self.rect.centerx
        centro_y = self.rect.centery - 20  # Acima do jogador
        # Número de dano flutuante
        gerenciador_efeitos.criar_numero_dano(centro_x, centro_y, dano, "normal")
        # Efeito de impacto
        gerenciador_efeitos.criar_efeito_impacto(self.rect.centerx, self.rect.centery, "normal")

        # Tocar som de dano
        gerenciador_audio.tocar_som('impacto_jogador')

        if self.vida <= 0:
            self.vida = 0
            # Adicionar efeito de explosão quando jogador morre
            feedback = obter_feedback_combate()
            if feedback:
                feedback.processar_explosao(self.rect.centerx, self.rect.centery, "grande")
            return True  # Morreu
        return False

    def curar(self, quantidade):
        """Curar jogador"""
        self.vida = min(self.vida + quantidade, self.vida_maxima)        # Tocar som de cura
        gerenciador_audio.tocar_som('powerup_vida')

    def aplicar_power_up(self, tipo_power_up):
        """Aplicar efeito de power-up"""        # Tocar som de power-up baseado no tipo
        som_powerup = f'powerup_{tipo_power_up}'
        gerenciador_audio.tocar_som(som_powerup)
        if tipo_power_up == 'velocidade':
            self.power_ups_ativos.append({
                'tipo': 'velocidade',
                'multiplicador': 1.5,
                'tempo_restante': DURACAO_POWER_UP
            })
            self.velocidade = int(self.personagem.velocidade * 1.5)

        elif tipo_power_up == 'vida':
            self.curar(50)

        elif tipo_power_up == 'tiro_rapido':
            self.power_ups_ativos.append({
                'tipo': 'tiro_rapido',
                'multiplicador': 0.5,
                'tempo_restante': DURACAO_POWER_UP
            })
            self.cooldown_tiro = self.personagem.cooldown * 0.5

    def atualizar_power_ups(self, dt):
        """Atualizar power-ups ativos"""
        for power_up in self.power_ups_ativos[:]:
            power_up['tempo_restante'] -= dt
            if power_up['tempo_restante'] <= 0:
                # Remover power-up
                if power_up['tipo'] == 'velocidade':
                    self.velocidade = self.personagem.velocidade
                elif power_up['tipo'] == 'tiro_rapido':
                    self.cooldown_tiro = self.personagem.cooldown
                self.power_ups_ativos.remove(power_up)

    def obter_power_ups_ativos(self):
        """Retornar lista de power-ups ativos"""
        return self.power_ups_ativos

    def get_cooldown_habilidade_percentual(self):
        """Retornar percentual do cooldown da habilidade"""
        if self.personagem.cooldown_habilidade_max <= 0:
            return 0
        return max(0, self.cooldown_habilidade / self.personagem.cooldown_habilidade_max)

    def obter_info_habilidade(self):
        """Obter informações da habilidade especial para a UI"""
        pronta = self.cooldown_habilidade <= 0

        # Definir informações baseadas no tipo de personagem
        info_habilidades = {
            'Shelly': {
                'nome': 'Super Shell',
                'descricao': 'Disparo devastador com dano duplo'
            },
            'Nita': {
                'nome': 'Invocar Urso',
                'descricao': 'Invoca um urso para ajudar na batalha'
            },
            'Colt': {
                'nome': 'Rajada de Balas',
                'descricao': 'Dispara múltiplas balas em sequência'
            },
            'Bull': {
                'nome': 'Investida',
                'descricao': 'Carga poderosa que atropela inimigos'
            },
            'Jessie': {
                'nome': 'Torreta Scrappy',
                'descricao': 'Constrói uma torreta que atira nos inimigos'
            }
        }

        nome_personagem = getattr(self.personagem, 'nome', 'Desconhecido')
        habilidade_info = info_habilidades.get(nome_personagem, {
            'nome': 'Habilidade Especial',
            'descricao': 'Habilidade única do personagem'
        })
        return {
            'nome': habilidade_info['nome'],
            'descricao': habilidade_info['descricao'],
            'pronta': pronta,
            'cooldown_atual': max(0, self.cooldown_habilidade),
            'cooldown_max': getattr(self.personagem, 'cooldown_habilidade_max', 5.0)
        }

    def reportar_dano_causado(self, dano):
        """Reporta dano causado para carregar Super"""
        self.super_system.adicionar_carga_dano(dano)

    def usar_super(self):
        """Usa o Super se disponível"""
        if self.super_system.usar_super():
            # Tocar som de Super específico do personagem
            nome_personagem = getattr(self.personagem, 'nome', 'Shelly').lower()
            som_super = f'super_{nome_personagem}'
            gerenciador_audio.tocar_som(som_super)
            # Executar habilidade específica do personagem
            self._executar_super_personagem()
            return True
        return False

    def _executar_super_personagem(self):
        """Executa a habilidade Super específica do personagem"""
        nome = self.personagem.nome
        if nome == "Shelly":
            # Super Shell - próximo tiro com dano duplo
            self.efeitos_especiais['super_shell'] = 1
            # Efeito visual dourado
            gerenciador_efeitos.criar_efeito_tiro_especial('super_shell',
                                                         self.rect.centerx,
                                                         self.rect.centery)
        elif nome == "Nita":
            # Invocar urso (já implementado)
            self.efeitos_especiais['urso_invocado'] = True
        elif nome == "Colt":
            # Rajada de 6 tiros
            self.efeitos_especiais['rajada_balas'] = 6
        elif nome == "Bull":
            # Investida (temporariamente aumenta velocidade)
            self.efeitos_especiais['investida'] = 1.0  # Duração em segundos
            self.velocidade = int(self.personagem.velocidade * 2.5)
        elif nome == "Barley":
            # Chuva de garrafas (área de dano)
            self.efeitos_especiais['chuva_garrafas'] = 3.0  # Duração
        elif nome == "Poco":
            # Cura completa
            self.curar(self.vida_maxima)
            # Efeito visual de cura
            gerenciador_efeitos.criar_numero_dano(self.rect.centerx, self.rect.centery - 30,
                                                self.vida_maxima, "cura")

    def celebrar_vitoria(self):
        """Ativa a animação de celebração de vitória única do personagem"""
        self.venceu_jogo = True
        self.animacao.iniciar_celebracao_vitoria()

        # Tocar som de vitória específico do personagem
        nome_personagem = getattr(self.personagem, 'nome', 'Shelly').lower()
        som_vitoria = f'vitoria_{nome_personagem}'
        gerenciador_audio.tocar_som(som_vitoria)

        # Criar efeito visual de celebração
        gerenciador_efeitos.criar_efeito_vitoria(self.rect.centerx,
        self.rect.centery, self.personagem.nome)

    def resetar_estado_animacao(self):
        """Reseta o estado de animação do personagem"""
        self.venceu_jogo = False
        self.recebeu_dano_recente = False
        self.tempo_sem_dano = 0.0
        self.animacao.resetar_animacoes()
