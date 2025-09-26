"""
Sistema de personagens do Brawl Stars Clone.
Este módulo define todos os personagens jogáveis do jogo, suas características
únicas, habilidades especiais, tipos de tiro e estatísticas. Cada personagem
possui mecânicas distintas que afetam o gameplay e estratégia.
"""

import math
import random
import pygame
from src.config import TAMANHO_JOGADOR, VELOCIDADE_JOGADOR, COOLDOWN_TIRO
from src.sprite_renderer import SpriteRenderer
from src.renderer_3d import renderer_3d  # pylint: disable=import-error
from src.pygame_constants import SRCALPHA


class PersonagemBase:
    """Classe base para todos os personagens"""
    def __init__(self, nome, vida, velocidade, dano, cooldown, tipo_tiro, cor_principal, cor_secundaria):
        self.nome = nome
        self.vida_maxima = vida
        self.vida = vida
        self.velocidade = velocidade
        self.dano = dano
        self.cooldown = cooldown
        self.tipo_tiro = tipo_tiro
        self.cor_principal = cor_principal
        self.cor_secundaria = cor_secundaria

        # Criar sprite do personagem
        self.sprite = SpriteRenderer.criar_sprite_personagem(
            nome, cor_principal, cor_secundaria, TAMANHO_JOGADOR
        )        # Propriedades para renderização 3D
        self.tamanho_render = 40  # Aumentado para melhor visibilidade e consistência com o menu
        self.angulo_visual = 0        # Habilidade especial será definida nas subclasses
        self.habilidade_especial = lambda: None
        self.cooldown_habilidade = 0
        self.duracao_habilidade = 0

        # Atributos opcionais para efeitos visuais
        self.em_movimento = False
        self.poder_ativo = False

    def render_3d(self, superficie, pos, tempo_jogo=0, tamanho_customizado=None):
        """Renderiza o personagem com visual 3D personalizado e efeitos avançados"""        # Usar tamanho customizado se fornecido
        tamanho_antigo = self.tamanho_render
        if tamanho_customizado:
            self.tamanho_render = tamanho_customizado

        # Efeitos de movimento e respiração
        offset_respiracao = math.sin(tempo_jogo * 3) * 1.5

        # Aplicar offset de respiração
        pos_com_efeitos = (pos[0], pos[1] + offset_respiracao)

        # Chamar método específico de renderização para cada personagem
        self._render_personagem_especifico(superficie, pos_com_efeitos, tempo_jogo)

        # Efeitos de partículas se em movimento ou ação
        if hasattr(self, 'em_movimento') and self.em_movimento:
            self._desenhar_particulas_movimento(superficie, pos_com_efeitos, tempo_jogo)

        # Efeito de poder ativo
        if hasattr(self, 'poder_ativo') and self.poder_ativo:
            self._desenhar_aura_poder(superficie, pos_com_efeitos, tempo_jogo)

        # Restaurar tamanho original
        if tamanho_customizado:
            self.tamanho_render = tamanho_antigo        # Barra de vida 3D se necessário
        if self.vida < self.vida_maxima:
            self._desenhar_barra_vida_3d(superficie, pos_com_efeitos)

    def _render_personagem_especifico(self, superficie, pos, _tempo_jogo):
        """Método base para renderização - será sobrescrito nas subclasses"""
        # Preparar contexto de renderização
        self._preparar_renderizacao()
        renderer_3d.desenhar_personagem_3d(
            superficie, pos,
            self.cor_principal, self.cor_secundaria,
            self.tamanho_render, self.angulo_visual
        )

    def _desenhar_barra_vida_3d(self, superficie, pos):
        """Desenha barra de vida com efeito 3D"""
        barra_largura = 40
        barra_altura = 6

        # Posição da barra (acima do personagem)
        barra_pos = (pos[0] - barra_largura // 2, pos[1] - self.tamanho_render - 10)

        # Fundo da barra (escuro)
        pygame.draw.rect(superficie, (40, 40, 40),
                         (barra_pos[0] - 1, barra_pos[1] - 1, barra_largura + 2, barra_altura + 2))

        # Vida atual (verde a vermelho baseado na porcentagem)
        porcentagem_vida = self.vida / self.vida_maxima
        largura_vida = int(barra_largura * porcentagem_vida)

        # Cor baseada na vida restante
        if porcentagem_vida > 0.6:
            cor_vida = (0, 255, 0)  # Verde
        elif porcentagem_vida > 0.3:
            cor_vida = (255, 255, 0)  # Amarelo
        else:
            cor_vida = (255, 0, 0)  # Vermelho

        # Gradiente na barra de vida
        for i in range(largura_vida):
            fator = i / barra_largura
            # Calcular cor mais clara manualmente
            incremento = int(20 * (1 - fator))
            cor_atual = (
                min(255, cor_vida[0] + incremento),
                min(255, cor_vida[1] + incremento),
                min(255, cor_vida[2] + incremento)            )
            pygame.draw.line(superficie, cor_atual,
                             (barra_pos[0] + i, barra_pos[1]),
                             (barra_pos[0] + i, barra_pos[1] + barra_altura))

    def usar_habilidade_especial(self):
        """Usar habilidade especial do personagem"""
        if self.cooldown_habilidade <= 0 and callable(self.habilidade_especial):
            return self.habilidade_especial()
        return None

    def atualizar_cooldowns(self, dt):
        """Atualizar cooldowns das habilidades"""
        if self.cooldown_habilidade > 0:
            self.cooldown_habilidade -= dt
        if self.duracao_habilidade > 0:
            self.duracao_habilidade -= dt

    def _desenhar_sombra_3d(self, superficie, pos):
        """Desenha sombra 3D abaixo do personagem"""
        sombra_size = self.tamanho_render * 1.2
        sombra_pos = (pos[0] - sombra_size // 2, pos[1] + self.tamanho_render - 5)
        # Criar surface para sombra com transparência
        sombra_surf = pygame.Surface((sombra_size, sombra_size // 2), SRCALPHA)
        pygame.draw.ellipse(sombra_surf, (0, 0, 0, 60), (0, 0, sombra_size, sombra_size // 2))
        superficie.blit(sombra_surf, sombra_pos)

    def _desenhar_particulas_movimento(self, superficie, pos, tempo_jogo):  # pylint: disable=unused-argument
        """Desenha partículas de movimento atrás do personagem"""
        for i in range(3):
            offset_x = -15 - i * 8 + random.randint(-3, 3)
            offset_y = random.randint(-5, 5)
            particula_pos = (pos[0] + offset_x, pos[1] + offset_y)
            alpha = 100 - i * 30
            tamanho = 3 - i

            if tamanho > 0:
                particula_surf = pygame.Surface((tamanho * 2, tamanho * 2), SRCALPHA)
                cor_particula = (*self.cor_principal, alpha)
                pygame.draw.circle(particula_surf, cor_particula, (tamanho, tamanho), tamanho)
                superficie.blit(particula_surf, (particula_pos[0] - tamanho, particula_pos[1] - tamanho))

    def _desenhar_aura_poder(self, superficie, pos, tempo_jogo):
        """Desenha aura de poder especial ativo"""
        for i in range(3):
            raio = self.tamanho_render + 10 + i * 5 + int(3 * math.sin(tempo_jogo * 4 + i))
            alpha = 80 - i * 25

            aura_surf = pygame.Surface((raio * 2, raio * 2), SRCALPHA)
            cor_aura = (*self.cor_secundaria, alpha)
            pygame.draw.circle(aura_surf, cor_aura, (raio, raio), raio, 2)
            superficie.blit(aura_surf, (pos[0] - raio, pos[1] - raio))

    def _preparar_renderizacao(self):
        """Prepara o personagem para renderização definindo contexto no renderer"""
        renderer_3d.definir_personagem_atual(self)


class Shelly(PersonagemBase):
    """Personagem Shelly - Especialista em combate de perto"""
    def __init__(self):
        super().__init__(
            nome="Shelly",
            vida=120,
            velocidade=VELOCIDADE_JOGADOR,
            dano=35,
            cooldown=COOLDOWN_TIRO * 1.2,
            tipo_tiro="shelly",
            cor_principal=(160, 82, 45),   # Marrom couro cowboy
            cor_secundaria=(139, 90, 43)  # Marrom escuro detalhes
        )
        self.habilidade_especial = self.super_shell
        self.cooldown_habilidade_max = 8.0

    def _render_personagem_especifico(self, superficie, pos, tempo_jogo):
        """Renderização específica para Shelly - Cowgirl com efeitos avançados"""
        # Preparar contexto de renderização
        self._preparar_renderizacao()
        
        if hasattr(renderer_3d, 'desenhar_shelly_3d'):
            renderer_3d.desenhar_shelly_3d(superficie, pos, self.cor_principal,
                                         self.cor_secundaria, self.tamanho_render, tempo_jogo)
        else:
            # Fallback para método genérico com efeitos 3D aprimorados
            renderer_3d.desenhar_personagem_3d(superficie, pos, self.cor_principal,
                                              self.cor_secundaria, self.tamanho_render)

    def super_shell(self):
        """Habilidade especial: Disparo devastador"""
        if self.cooldown_habilidade <= 0:
            self.cooldown_habilidade = self.cooldown_habilidade_max
            return {
                'tipo': 'super_shell',
                'dano': self.dano * 2,
                'alcance': 1.5,
                'descricao': 'Super Shell ativado!'
            }
        return None


class Nita(PersonagemBase):
    """Personagem Nita - Invocadora de urso"""
    def __init__(self):
        super().__init__(
            nome="Nita",
            vida=140,
            velocidade=VELOCIDADE_JOGADOR * 0.9,
            dano=28,
            cooldown=COOLDOWN_TIRO * 0.8,
            tipo_tiro="nita",
            cor_principal=(101, 67, 33),    # Marrom tribal
            cor_secundaria=(160, 82, 45)   # Marrom detalhes
        )

        self.habilidade_especial = self.invocar_urso
        self.cooldown_habilidade_max = 12.0
        self.urso_ativo = False

    def _render_personagem_especifico(self, superficie, pos, tempo_jogo):
        """Renderização específica para Nita - Xamã tribal com efeitos mágicos"""
        if hasattr(renderer_3d, 'desenhar_nita_3d'):
            renderer_3d.desenhar_nita_3d(superficie, pos, self.cor_principal,
                                        self.cor_secundaria, self.tamanho_render, tempo_jogo)
        else:
            # Fallback para método genérico com efeitos 3D aprimorados
            renderer_3d.desenhar_personagem_3d(superficie, pos, self.cor_principal,
                                              self.cor_secundaria, self.tamanho_render)

    def invocar_urso(self):
        """Habilidade especial: Invocar urso"""
        if self.cooldown_habilidade <= 0 and not self.urso_ativo:
            self.cooldown_habilidade = self.cooldown_habilidade_max
            self.urso_ativo = True
            return {
                'tipo': 'invocar_urso',
                'duracao': 15.0,                'descricao': 'Urso invocado!'
            }
        return None


class Colt(PersonagemBase):
    """Personagem Colt - Atirador de precisão"""
    def __init__(self):
        super().__init__(
            nome="Colt",
            vida=100,
            velocidade=VELOCIDADE_JOGADOR * 1.1,
            dano=32,
            cooldown=COOLDOWN_TIRO * 0.6,
            tipo_tiro="colt",
            cor_principal=(25, 25, 112),    # Azul marinho (jaqueta)
            cor_secundaria=(70, 130, 180)  # Azul aço (detalhes)
        )
        self.habilidade_especial = self.rajada_balas
        self.cooldown_habilidade_max = 10.0

    def _render_personagem_especifico(self, superficie, pos, tempo_jogo):
        """Renderização específica para Colt - Atirador elegante com efeitos de precisão"""
        if hasattr(renderer_3d, 'desenhar_colt_3d'):
            renderer_3d.desenhar_colt_3d(superficie, pos, self.cor_principal,
                                        self.cor_secundaria, self.tamanho_render, tempo_jogo)
        else:
            # Fallback para método genérico com efeitos 3D aprimorados
            renderer_3d.desenhar_personagem_3d(superficie, pos, self.cor_principal,
                                              self.cor_secundaria, self.tamanho_render)

    def rajada_balas(self):
        """Habilidade especial: Rajada de balas"""
        if self.cooldown_habilidade <= 0:
            self.cooldown_habilidade = self.cooldown_habilidade_max
            return {
                'tipo': 'rajada_balas',
                'quantidade': 6,
                'intervalo': 0.1,                'descricao': 'Rajada de balas!'
            }
        return None


class Bull(PersonagemBase):
    """Personagem Bull - Tanque resistente"""
    def __init__(self):
        super().__init__(
            nome="Bull",
            vida=180,
            velocidade=VELOCIDADE_JOGADOR * 0.8,
            dano=40,
            cooldown=COOLDOWN_TIRO * 1.4,
            tipo_tiro="bull",
            cor_principal=(25, 25, 25),      # Preto (jaqueta couro)
            cor_secundaria=(64, 64, 64)     # Cinza escuro (detalhes)
        )
        self.habilidade_especial = self.investida
        self.cooldown_habilidade_max = 8.0

    def _render_personagem_especifico(self, superficie, pos, tempo_jogo):
        """Renderização específica para Bull - Motoqueiro resistente com efeitos de força"""
        if hasattr(renderer_3d, 'desenhar_bull_3d'):
            renderer_3d.desenhar_bull_3d(superficie, pos, self.cor_principal,
                                        self.cor_secundaria, self.tamanho_render, tempo_jogo)
        else:
            renderer_3d.desenhar_personagem_3d(superficie, pos, self.cor_principal,
                                              self.cor_secundaria, self.tamanho_render)

    def investida(self):
        """Habilidade especial: Investida demolidora"""
        if self.cooldown_habilidade <= 0:
            self.cooldown_habilidade = self.cooldown_habilidade_max
            return {
                'tipo': 'investida',
                'velocidade_bonus': 2.0,
                'duracao': 2.0,
                'dano_contato': 80,                'descricao': 'Investida!'
            }
        return None


class Barley(PersonagemBase):
    """Personagem Barley - Especialista em área"""
    def __init__(self):
        super().__init__(
            nome="Barley",
            vida=90,
            velocidade=VELOCIDADE_JOGADOR * 0.9,
            dano=25,
            cooldown=COOLDOWN_TIRO * 1.1,
            tipo_tiro="arco",
            cor_principal=(192, 192, 192),  # Prata (corpo robótico)
            cor_secundaria=(64, 64, 64)    # Cinza escuro (detalhes)
        )

        self.habilidade_especial = self.chuva_garrafas
        self.cooldown_habilidade_max = 9.0

    def _render_personagem_especifico(self, superficie, pos, tempo_jogo):
        """Renderização específica para Barley - Bartender robótico com efeitos alquímicos"""
        if hasattr(renderer_3d, 'desenhar_barley_3d'):
            renderer_3d.desenhar_barley_3d(superficie, pos, self.cor_principal,
                                          self.cor_secundaria, self.tamanho_render, tempo_jogo)
        else:
            renderer_3d.desenhar_personagem_3d(superficie, pos, self.cor_principal,
                                              self.cor_secundaria, self.tamanho_render)

    def chuva_garrafas(self):
        """Habilidade especial: Chuva de garrafas"""
        if self.cooldown_habilidade <= 0:
            self.cooldown_habilidade = self.cooldown_habilidade_max
            return {
                'tipo': 'chuva_garrafas',
                'quantidade': 5,
                'area_dano': 80,
                'duracao_area': 4.0,                'descricao': 'Chuva de garrafas!'
            }
        return None


class Poco(PersonagemBase):
    """Personagem Poco - Suporte curandeiro"""
    def __init__(self):
        super().__init__(
            nome="Poco",
            vida=110,
            velocidade=VELOCIDADE_JOGADOR * 0.95,
            dano=20,
            cooldown=COOLDOWN_TIRO * 0.9,
            tipo_tiro="ondas",
            cor_principal=(160, 82, 45),    # Marrom (sombrero)
            cor_secundaria=(255, 255, 240) # Branco osso (esqueleto)
        )
        self.habilidade_especial = self.melodia_curativa
        self.cooldown_habilidade_max = 7.0

    def _render_personagem_especifico(self, superficie, pos, tempo_jogo):
        """Renderização específica para Poco - Músico esqueleto com efeitos musicais"""
        if hasattr(renderer_3d, 'desenhar_poco_3d'):
            renderer_3d.desenhar_poco_3d(superficie, pos, self.cor_principal,
                                        self.cor_secundaria, self.tamanho_render, tempo_jogo)
        else:
            renderer_3d.desenhar_personagem_3d(superficie, pos, self.cor_principal,
                                              self.cor_secundaria, self.tamanho_render)

    def melodia_curativa(self):
        """Habilidade especial: Melodia curativa"""
        if self.cooldown_habilidade <= 0:
            self.cooldown_habilidade = self.cooldown_habilidade_max
            return {
                'tipo': 'melodia_curativa',
                'cura': 60,
                'alcance': 150,
                'descricao': 'Melodia curativa!'
            }
        return None

# Dicionário de personagens disponíveis
PERSONAGENS_DISPONIVEIS = {
    'Shelly': Shelly,
    'Nita': Nita,
    'Colt': Colt,
    'Bull': Bull,
    'Barley': Barley,
    'Poco': Poco
}

def obter_personagem(nome):
    """Criar instância de um personagem pelo nome"""
    if nome in PERSONAGENS_DISPONIVEIS:
        return PERSONAGENS_DISPONIVEIS[nome]()
    return PERSONAGENS_DISPONIVEIS['Shelly']()  # Padrão

def listar_personagens():
    """Retorna lista de nomes dos personagens disponíveis"""
    return list(PERSONAGENS_DISPONIVEIS.keys())
