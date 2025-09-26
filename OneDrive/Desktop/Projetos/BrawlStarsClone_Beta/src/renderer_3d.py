"""
Sistema de renderização 3D para o Brawl Stars Clone.
Este módulo implementa um sistema completo de gráficos 3D que transforma
o visual do jogo de pixelado para um estilo moderno similar ao original.
Inclui iluminação, sombras, gradientes e efeitos visuais avançados.
"""

import math
import types
from typing import Tuple, List
import pygame
from src.pygame_constants import SRCALPHA
from src.animacao_3d import animador_global, UtilsFormasOrganicas

class Renderer3D:
    """Sistema de renderização com efeitos 3D para personagens e cenário"""

    def __init__(self):
        self.luz_ambiente = 0.3
        self.luz_direcional = pygame.Vector2(0.5, -0.8).normalize()
        # Removido altura_camera (não utilizada) e convertida em método para economia de memória
        self._personagem_atual = None  # Inicializar atributo para evitar erros
        self._debug_info = {}  # Cache para informações de debug quando necessário

        # Inicializar métodos específicos dos personagens após definir a classe
        # Isso será feito externamente após a definição da função

    def criar_gradiente_radial(self, superficie: pygame.Surface, cor_centro: Tuple[int, int, int],
                              cor_borda: Tuple[int, int, int], centro: Tuple[int, int], raio: int):
        """Cria um gradiente radial para simular iluminação 3D"""
        for r in range(raio, 0, -1):
            # Interpola entre as cores
            fator = r / raio
            cor_atual = (
                int(cor_centro[0] * (1 - fator) + cor_borda[0] * fator),
                int(cor_centro[1] * (1 - fator) + cor_borda[1] * fator),
                int(cor_centro[2] * (1 - fator) + cor_borda[2] * fator)
            )
            pygame.draw.circle(superficie, cor_atual, centro, r)

    def desenhar_sombra(self, superficie: pygame.Surface, pos: Tuple[int, int],
                       tamanho: Tuple[int, int], alpha: int = 60):
        """Desenha sombra projetada no chão (versão otimizada)"""
        # Usar círculos concêntricos ao invés de pixel - by - pixel para melhor performance
        raio_maior = min(tamanho) // 2
        center_x = pos[0] + tamanho[0] // 2
        center_y = pos[1] + tamanho[1] // 2

        # Offset da sombra baseado na direção da luz
        offset_x = int(self.luz_direcional.x * 15)
        offset_y = int(self.luz_direcional.y * 8)

        # Desenhar círculos concêntricos para criar gradiente de sombra
        for i in range(5, 0, -1):
            raio = (raio_maior * i) // 5
            alpha_atual = (alpha * i) // 10  # Gradiente de transparência
            cor_sombra = (*[0, 0, 0], alpha_atual)

            # Criar superfície temporária para a sombra com alpha
            temp_surf = pygame.Surface((raio * 2, raio * 2), SRCALPHA)
            pygame.draw.circle(temp_surf, cor_sombra, (raio, raio), raio)
            # Aplicar a sombra na posição final com offset
            superficie.blit(temp_surf,
                          (center_x + offset_x - raio, center_y + offset_y - raio))

    def aplicar_iluminacao_3d(self, cor_base: Tuple[int, int, int],
                             normal: pygame.Vector2) -> Tuple[int, int, int]:
        """Aplica iluminação baseada na normal da superfície"""
        intensidade = max(0, normal.dot(self.luz_direcional))
        iluminacao_total = self.luz_ambiente + intensidade * (1 - self.luz_ambiente)

        return (
            min(255, int(cor_base[0] * iluminacao_total)),
            min(255, int(cor_base[1] * iluminacao_total)),
            min(255, int(cor_base[2] * iluminacao_total))
        )

    def desenhar_personagem_3d(self, superficie: pygame.Surface, pos: Tuple[int, int],
                              cor_primaria: Tuple[int,int,int], cor_secundaria: Tuple[int,int,int],
                              tamanho: int = 30, angulo_rotacao: float = 0):
        """Desenha personagem com visual 3D estilo Brawl Stars"""
        # Usar o mesmo sistema de superficie que os personagens específicos
        char_surf, centro = self._criar_superficie_personagem(tamanho)

        # Corpo principal - formato básico usando elipse orgânica diretamente
        corpo_rect = pygame.Rect(centro[0] - tamanho//2, centro[1] - tamanho//3,
                                tamanho, int(tamanho * 0.8))
        UtilsFormasOrganicas.desenhar_elipse_organica(char_surf, cor_primaria, corpo_rect, 0.1)

        # Cabeça simples
        cabeca_pos = (centro[0], centro[1] - tamanho // 4)
        cabeca_raio = tamanho // 3
        pygame.draw.circle(char_surf, cor_primaria, cabeca_pos, cabeca_raio)

        # Detalhes do personagem
        self._desenhar_detalhes_personagem(char_surf, centro, cor_secundaria, tamanho)

        # Rotacionar se necessário
        if angulo_rotacao != 0:
            char_surf = pygame.transform.rotate(char_surf, math.degrees(angulo_rotacao))

        # Desenhar na superfície principal
        rect = char_surf.get_rect(center=pos)
        superficie.blit(char_surf, rect)

    def _desenhar_detalhes_personagem(self, superficie: pygame.Surface, centro: Tuple[int, int],
                                    cor_secundaria: Tuple[int, int, int], tamanho: int):
        """Desenha detalhes 3D do personagem ajustados para o novo formato"""

        # Posição da cabeça ajustada
        cabeca_centro = (centro[0], centro[1] - tamanho // 4)

        # Olhos com brilho - posicionados na cabeça
        olho_esq = (cabeca_centro[0] - tamanho // 6, cabeca_centro[1] - tamanho // 8)
        olho_dir = (cabeca_centro[0] + tamanho // 6, cabeca_centro[1] - tamanho // 8)

        # Base dos olhos
        pygame.draw.circle(superficie, (255, 255, 255), olho_esq, tamanho // 8)
        pygame.draw.circle(superficie, (255, 255, 255), olho_dir, tamanho // 8)

        # Pupilas
        pygame.draw.circle(superficie, (0, 0, 0), olho_esq, tamanho // 12)
        pygame.draw.circle(superficie, (0, 0, 0), olho_dir, tamanho // 12)

        # Brilho nos olhos
        brilho_esq = (olho_esq[0] - 1, olho_esq[1] - 1)
        brilho_dir = (olho_dir[0] - 1, olho_dir[1] - 1)
        pygame.draw.circle(superficie, (255, 255, 255), brilho_esq, 1)
        pygame.draw.circle(superficie, (255, 255, 255), brilho_dir, 1)

        # Detalhes do equipamento
        self._desenhar_equipamento_3d(superficie, centro, cor_secundaria, tamanho)

    def _desenhar_equipamento_3d(self, superficie: pygame.Surface, centro: Tuple[int, int],
                                cor: Tuple[int, int, int], tamanho: int):
        """Desenha equipamentos com efeito 3D"""
        # Arma / equipamento na lateral direita
        arma_pos = (centro[0] + tamanho // 2, centro[1])
        arma_tamanho = (tamanho // 3, tamanho // 6)

        # Gradiente para a arma
        arma_surf = pygame.Surface(arma_tamanho, SRCALPHA)
        self.criar_gradiente_radial(arma_surf,
                                   self.cor_mais_clara(cor, 30),
                                   self._cor_mais_escura(cor, 20),
                                   (arma_tamanho[0]//2, arma_tamanho[1]//2),
                                   min(arma_tamanho) // 2)
        superficie.blit(arma_surf, arma_pos)

    def desenhar_obstaculo_3d(self, superficie: pygame.Surface, rect: pygame.Rect,
                             cor_base: Tuple[int, int, int], eh_destrutivel: bool = False,
                             dano_percentual: float = 0.0):
        """Desenha obstáculo com visual 3D e estado de dano"""
        # Desenhar sombra
        self.desenhar_sombra(superficie, rect.topleft, rect.size, alpha=80) # Ajustar cor baseada no dano
        if eh_destrutivel and dano_percentual > 0:
            cor_base = self._aplicar_dano_visual(cor_base, dano_percentual)

        # Criar superfície do obstáculo
        obs_surf = pygame.Surface(rect.size, SRCALPHA)

        # Face superior (mais clara)
        face_superior = pygame.Rect(0, 0, rect.width, rect.height // 3)
        cor_superior = self.cor_mais_clara(cor_base, 50)
        pygame.draw.rect(obs_surf, cor_superior, face_superior)

        # Face frontal (cor normal)
        face_frontal = pygame.Rect(0, rect.height // 3, rect.width, rect.height // 3)
        pygame.draw.rect(obs_surf, cor_base, face_frontal)

        # Face inferior (mais escura)
        face_inferior = pygame.Rect(0, 2 * rect.height // 3, rect.width, rect.height // 3)
        cor_inferior = self._cor_mais_escura(cor_base, 30)
        pygame.draw.rect(obs_surf, cor_inferior, face_inferior)

        # Bordas para efeito 3D
        self._desenhar_bordas_3d(obs_surf, rect.size, cor_base)

        # Rachaduras se destrutível e danificado
        if eh_destrutivel and dano_percentual > 0.3:
            self._desenhar_rachaduras(obs_surf, rect.size, dano_percentual)
        superficie.blit(obs_surf, rect)

    def desenhar_gema_3d(self, superficie: pygame.Surface, pos: Tuple[int, int],
                        cor: Tuple[int, int, int], tamanho: int = 12, tempo: float = 0):
        """Desenha gema com efeito 3D estilo Brawl Stars"""
        # Animação de flutuação
        offset_y = int(math.sin(tempo * 4) * 3)
        pos_real = (pos[0], pos[1] + offset_y)  # Desenhar sombra
        self.desenhar_sombra(superficie, pos_real, (tamanho * 2, tamanho), alpha=40)

        # Criar superfície da gema
        gema_surf = pygame.Surface((tamanho * 2, tamanho * 2), SRCALPHA)
        centro = (tamanho, tamanho)

        # Forma de diamante 3D - mais definida
        self._desenhar_diamante_brawl_stars(gema_surf, centro, cor, tamanho)

        # Rotação suave
        angulo = tempo * 50
        gema_surf = pygame.transform.rotate(gema_surf, angulo)
        rect = gema_surf.get_rect(center=pos_real)
        superficie.blit(gema_surf, rect)


    def desenhar_power_up_3d(self, superficie: pygame.Surface, pos: Tuple[int, int],
                             tipo: str, tamanho: int = 20, tempo: float = 0):
        """Desenha power - up com visual 3D"""
        cores_powerup = {
            'velocidade': (0, 255, 100),
            'dano': (255, 100, 0),
            'vida': (255, 0, 100),
            'escudo': (100, 100, 255),
            'tiro_rapido': (255, 165, 0)
        }
        cor = cores_powerup.get(tipo, (255, 255, 255))

        # Animação de pulsação
        escala = 1.0 + math.sin(tempo * 6) * 0.1
        tamanho_real = int(tamanho * escala)

        # Desenhar aura
        self._desenhar_aura_powerup(superficie, pos, cor, tamanho_real * 2, tempo)

        # Desenhar power - up principal
        self.desenhar_gema_3d(superficie, pos, cor, tamanho_real, tempo)

        # Ícone do tipo
        self._desenhar_icone_powerup(superficie, pos, tipo, tamanho_real)
    def desenhar_projetil_3d(self, superficie: pygame.Surface, pos: Tuple[int, int],
                           cor: Tuple[int, int, int], tamanho: int = 8,
                           tipo_tiro: str = "normal", de_inimigo: bool = False,
                           tempo_jogo: float = 0):
        """Desenha projétil com efeitos 3D modernos e visuais únicos por tipo"""
        x, y = pos        # Ajustar cor baseado no tipo e origem
        if de_inimigo:
            cor_base = (255, 100, 100)  # Vermelho para inimigos
            cor_brilho = (255, 200, 200)
        else:
            cor_base = cor
            cor_brilho = self.cor_mais_clara(cor, 100)

        # Criar superfície maior para efeitos
        tamanho_surface = tamanho * 8
        proj_surface = pygame.Surface((tamanho_surface, tamanho_surface), SRCALPHA)
        centro = (tamanho_surface // 2, tamanho_surface // 2)

        # DESENHAR PROJÉTIL ÚNICO POR TIPO
        if tipo_tiro == "bull" or tipo_tiro == "shotgun":
            # PROJÉTIL DE SHOTGUN BULL - Múltiplos cartuchos metálicos
            for i in range(4):  # 4 projéteis de shotgun
                offset_x = int(math.sin(tempo_jogo * 10 + i * 1.5) * 6)
                offset_y = int(math.cos(tempo_jogo * 10 + i * 1.5) * 6)
                pos_cartucho = (centro[0] + offset_x + (i - 2) * 4, centro[1] + offset_y)

                # Cartucho dourado metálico
                for j in range(4, 0, -1):
                    cor_cartucho = self._interpolar_cor((255,215,0), (200,170,0), j/4)  # Dourado
                    pygame.draw.ellipse(proj_surface, cor_cartucho,
                                      (pos_cartucho[0]-j, pos_cartucho[1]-j // 2, j * 2, j))

                # Borda metálica
                pygame.draw.ellipse(proj_surface, (150, 120, 0),
                                  (pos_cartucho[0]-3, pos_cartucho[1]-2, 6, 4), 1)

        elif tipo_tiro == "shelly":
            # PROJÉTIL DE SHELLY - Múltiplos bagos de chumbo
            for i in range(3):
                offset_x = int(math.sin(tempo_jogo * 8 + i * 2) * 4)
                offset_y = int(math.cos(tempo_jogo * 8 + i * 2) * 4)
                pos_bago = (centro[0] + offset_x + (i - 1) * 5, centro[1] + offset_y) # Bago de chumbo brilhante
                for j in range(tamanho//2, 0, -1):
                    cor_bago = self._interpolar_cor((200,200,255), (100,100,150), j/(tamanho//2))
                    pygame.draw.circle(proj_surface, cor_bago, pos_bago, j)
                pygame.draw.circle(proj_surface, (255, 255, 255), pos_bago, 1)

        elif tipo_tiro == "colt":
            # PROJÉTIL DE COLT - Bala de revólver clássica
            # Gradiente metálico dourado
            for i in range(tamanho, 0, -1):
                cor_bala = self._interpolar_cor((255, 215, 0), (200, 170, 0), i / tamanho)
                pygame.draw.ellipse(proj_surface, cor_bala,
                                  (centro[0] - i // 2, centro[1] - i, i, i * 2))

            # Ponta da bala (cobre)
            pygame.draw.ellipse(proj_surface, (184, 115, 51),
            (centro[0] - tamanho//3, centro[1] - tamanho, tamanho//1.5, tamanho//2))

            # Brilho metálico
            pygame.draw.ellipse(proj_surface, (255, 255, 255),
                              (centro[0] - 1, centro[1] - tamanho // 2, 2, tamanho // 3))

        elif tipo_tiro == "nita":
            # PROJÉTIL DE NITA - Gema mágica tribal
            # Base da gema (hexagonal)
            pontos_gema = []
            for i in range(6):
                angulo = i * math.pi / 3
                px = centro[0] + int(math.cos(angulo + tempo_jogo * 5) * tamanho)
                py = centro[1] + int(math.sin(angulo + tempo_jogo * 5) * tamanho)
                pontos_gema.append((px, py))

            # Gema com gradiente púrpura
            for i in range(tamanho, 0, -1):
                cor_gema = self._interpolar_cor((147, 0, 211), (75, 0, 130), i / tamanho)
                pontos_inner = []
                for j in range(6):
                    angulo = j * math.pi / 3
                    px = centro[0] + int(math.cos(angulo + tempo_jogo * 5) * i)
                    py = centro[1] + int(math.sin(angulo + tempo_jogo * 5) * i)
                    pontos_inner.append((px, py))
                if len(pontos_inner) >= 3:
                    pygame.draw.polygon(proj_surface, cor_gema, pontos_inner)

            # Brilho mágico no centro
            pygame.draw.circle(proj_surface, (255, 255, 255), centro, max(1, tamanho // 3))

        else:
            # PROJÉTIL PADRÃO - Energia pura
            # Efeito pulsante externo
            pulso = int(math.sin(tempo_jogo * 15) * 3)
            for i in range(4):
                raio_pulso = tamanho + pulso + i * 2
                cor_pulso = self._interpolar_cor(cor_brilho, cor_base, i / 4)
                pygame.draw.circle(proj_surface, cor_pulso, centro, raio_pulso, 2)

            # NÚCLEO PRINCIPAL com gradiente dramático
            for i in range(tamanho + 4, 0, -1):
                if i > tamanho:
                    fator = (i - tamanho) / 4
                    cor_atual = self._interpolar_cor(cor_brilho, cor_base, fator)
                else:
                    fator = i / tamanho
                    cor_atual = self._interpolar_cor(cor_base, cor_brilho, fator)
                pygame.draw.circle(proj_surface, cor_atual, centro, i)

            # Centro super brilhante
            pygame.draw.circle(proj_surface, (255, 255, 255), centro, max(1, tamanho // 3))

        # Blit na superfície principal
        proj_rect = proj_surface.get_rect(center=(x, y))
        superficie.blit(proj_surface, proj_rect)

    def _interpolar_cor(self, cor1: Tuple[int, int, int], cor2: Tuple[int, int, int],
                        fator: float) -> Tuple[int, int, int]:
        """Interpola entre duas cores"""
        return (
            int(cor1[0] * (1 - fator) + cor2[0] * fator),
            int(cor1[1] * (1 - fator) + cor2[1] * fator),
            int(cor1[2] * (1 - fator) + cor2[2] * fator)
        )

    def cor_mais_clara(self, cor: Tuple[int, int, int], incremento: int) -> Tuple[int, int, int]:
        """Retorna uma versão mais clara da cor"""
        return (
            min(255, cor[0] + incremento),
            min(255, cor[1] + incremento),
            min(255, cor[2] + incremento)
        )

    def _cor_mais_escura(self, cor: Tuple[int, int, int], decremento: int) -> Tuple[int, int, int]:
        """Retorna uma versão mais escura da cor"""
        return (
            max(0, cor[0] - decremento),
            max(0, cor[1] - decremento),
            max(0, cor[2] - decremento)
        )

    def _aplicar_dano_visual(self, cor_base: Tuple[int, int, int],
                           dano_percentual: float) -> Tuple[int, int, int]:
        """Aplica efeito visual de dano à cor"""
        # Escurecer e avermelhar conforme o dano
        fator = 1.0 - (dano_percentual * 0.4)
        vermelho_extra = int(dano_percentual * 50)

        return (
            min(255, int(cor_base[0] * fator) + vermelho_extra),
            int(cor_base[1] * fator),
            int(cor_base[2] * fator)
        )

    def _desenhar_bordas_3d(self, superficie: pygame.Surface, tamanho: Tuple[int, int],
                           cor_base: Tuple[int, int, int]):
        """Desenha bordas para efeito 3D"""
        # Borda superior clara
        pygame.draw.line(superficie, self.cor_mais_clara(cor_base, 80),
                        (0, 0), (tamanho[0], 0), 2)

        # Borda esquerda clara
        pygame.draw.line(superficie, self.cor_mais_clara(cor_base, 60),
                        (0, 0), (0, tamanho[1]), 2)

        # Borda inferior escura
        pygame.draw.line(superficie, self._cor_mais_escura(cor_base, 60),
                        (0, tamanho[1]-1), (tamanho[0], tamanho[1]-1), 2)

        # Borda direita escura
        pygame.draw.line(superficie, self._cor_mais_escura(cor_base, 40),
                        (tamanho[0]-1, 0), (tamanho[0]-1, tamanho[1]), 2)

    def _desenhar_rachaduras(self, superficie: pygame.Surface, tamanho: Tuple[int, int],
                           dano_percentual: float):
        """Desenha rachaduras baseadas no dano"""
        if dano_percentual < 0.3:
            return
        cor_rachadura = (60, 60, 60)
        largura = max(1, int(dano_percentual * 3))

        # Rachadura diagonal principal
        if dano_percentual > 0.5:
            pygame.draw.line(superficie, cor_rachadura,
                           (tamanho[0]//4, tamanho[1]//4),
                           (3*tamanho[0]//4, 3*tamanho[1]//4), largura)
        # Rachaduras secundárias
        if dano_percentual > 0.8:
            pygame.draw.line(superficie, cor_rachadura,
                           (3*tamanho[0]//4, tamanho[1]//4),
                           (tamanho[0]//4, 3*tamanho[1]//4), largura)

    def _desenhar_diamante_brawl_stars(self, superficie: pygame.Surface, centro: Tuple[int, int],
                                      cor: Tuple[int, int, int], tamanho: int):
        """Desenha diamante estilo Brawl Stars sem gradientes circulares"""
        # Forma básica do diamante
        pontos_diamante = self._calcular_pontos_diamante(centro, tamanho)
        # Desenhar faces do diamante
        for i, face in enumerate(pontos_diamante):
            cor_face = self._cor_face_diamante(cor, i)
            pygame.draw.polygon(superficie, cor_face, face)

        # Brilho central pequeno (não um gradiente radial grande)
        brilho_tamanho = max(2, tamanho // 4)
        pygame.draw.circle(superficie, (255, 255, 255), centro, brilho_tamanho)

        # Contorno do diamante
        pygame.draw.polygon(superficie, self._cor_mais_escura(cor, 40),
                           pontos_diamante[0], 2)

    def _calcular_pontos_diamante(self, centro: Tuple[int, int],
                                tamanho: int) -> List[List[Tuple[int, int]]]:
        """Calcula pontos para desenhar diamante 3D"""
        x, y = centro
        faces = []
        # Face superior
        faces.append([
            (x, y - tamanho),
            (x - tamanho//2, y - tamanho//2),
            (x, y),
            (x + tamanho//2, y - tamanho//2)
        ])

        # Faces laterais
        faces.append([
            (x - tamanho//2, y - tamanho//2),
            (x - tamanho, y),
            (x, y + tamanho//2),
            (x, y)
        ])
        faces.append([
            (x + tamanho//2, y - tamanho//2),
            (x, y),
            (x, y + tamanho//2),
            (x + tamanho, y)        ])
        return faces

    def _cor_face_diamante(self, cor_base: Tuple[int, int, int],
                          indice_face: int) -> Tuple[int, int, int]:
        """Calcula cor da face do diamante baseada na iluminação"""
        if indice_face == 0:  # Face superior
            return self.cor_mais_clara(cor_base, 60)
        elif indice_face == 1:  # Face esquerda
            return self._cor_mais_escura(cor_base, 30)
        else:  # Face direita
            return cor_base

    def _desenhar_aura_powerup(self, superficie: pygame.Surface, pos: Tuple[int, int],
                              cor: Tuple[int, int, int], tamanho: int, tempo: float):
        """Desenha aura pulsante do power - up"""
        alpha = int(100 + math.sin(tempo * 8) * 50)
        aura_surf = pygame.Surface((tamanho, tamanho), SRCALPHA)
        # Múltiplos círculos concêntricos para efeito de aura
        for i in range(3, 0, -1):
            raio = tamanho // (2 * i)
            cor_aura = (*cor, alpha // i)
            pygame.draw.circle(aura_surf, cor_aura, (tamanho // 2, tamanho // 2), raio)

        rect = aura_surf.get_rect(center=pos)
        superficie.blit(aura_surf, rect)

    def _desenhar_icone_powerup(self, superficie: pygame.Surface, pos: Tuple[int, int],
                               tipo: str, tamanho: int):
        """Desenha ícone específico do power - up"""
        cor_icone = (255, 255, 255)

        if tipo == 'velocidade':
            # Setas para cima
            pontos = [
                (pos[0], pos[1] - tamanho//3),
                (pos[0] - tamanho//6, pos[1]),
                (pos[0] + tamanho//6, pos[1])
            ]
            pygame.draw.polygon(superficie, cor_icone, pontos)

        elif tipo in ['dano', 'tiro_rapido']:
            # Raio / explosão
            for angulo in range(0, 360, 45):
                rad = math.radians(angulo)
                x1 = pos[0] + math.cos(rad) * tamanho // 6
                y1 = pos[1] + math.sin(rad) * tamanho // 6
                x2 = pos[0] + math.cos(rad) * tamanho // 3
                y2 = pos[1] + math.sin(rad) * tamanho // 3
                pygame.draw.line(superficie, cor_icone, (x1, y1), (x2, y2), 2)

        elif tipo == 'vida':
            # Cruz de cura
            pygame.draw.line(superficie, cor_icone,
                           (pos[0] - tamanho // 4, pos[1]),
                           (pos[0] + tamanho // 4, pos[1]), 3)
            pygame.draw.line(superficie, cor_icone,
                           (pos[0], pos[1] - tamanho // 4),
                           (pos[0], pos[1] + tamanho // 4), 3)

    def desenhar_shelly_3d(self, superficie, pos, _cor_primaria, _cor_secundaria, tamanho, _tempo):
        """Desenha Shelly com animações e formas orgânicas autênticas do Brawl Stars"""
        # Configuração básica
        offsets_animacao = self._configurar_animacao_personagem()
        char_surf, centro = self._criar_superficie_personagem(tamanho)

        # Configurações específicas da Shelly
        corpo_altura = int(tamanho * 0.8)
        corpo_largura = int(tamanho * 0.6)
        corpo_pos_y = centro[1] - int(tamanho * 0.3) + int(offsets_animacao['balanco_corpo'])
        cor_pele = (255, 220, 177)

        # CORPO - Jaqueta AMARELA com formato mais anatômico
        torso_rect = pygame.Rect(centro[0] - corpo_largura // 2, corpo_pos_y,
                                 corpo_largura, int(corpo_altura * 0.7))
        cor_jaqueta_shelly = (255, 200, 0)
        pygame.draw.rect(char_surf, cor_jaqueta_shelly, torso_rect, border_radius=6)

        # Cintura com calça azul
        cintura_largura = int(corpo_largura * 0.8)
        cintura_rect = pygame.Rect(centro[0] - cintura_largura // 2,
                                  corpo_pos_y + int(corpo_altura * 0.5),
                                  cintura_largura, int(corpo_altura * 0.3))
        pygame.draw.rect(char_surf, (50, 50, 150), cintura_rect, border_radius=4)  # Calça azul
        cabeca_pos = (centro[0] + int(offsets_animacao['rotacao_cabeca'] * 2),
                     centro[1] - int(tamanho * 0.6) + int(offsets_animacao['balanco_corpo']))
        cabeca_largura = int(tamanho * 0.4)
        cabeca_altura = int(tamanho * 0.5)

        self._desenhar_cabeca_oval(char_surf, cabeca_pos, cabeca_largura, cabeca_altura, cor_pele,
                                   corpo_pos_y, corpo_largura)
        # Cabelo loiro da Shelly com estilo mais realista
        # Base do cabelo (camada principal)
        cabelo_base_rect = pygame.Rect(cabeca_pos[0] - cabeca_largura//2 - 2,
                                      cabeca_pos[1] - cabeca_altura//2 - 8,
                                      cabeca_largura + 4, int(cabeca_altura * 0.9))
        pygame.draw.ellipse(char_surf, (220, 180, 0), cabelo_base_rect)  # Tom mais escuro

        # Mechas de cabelo (camada superior com tom mais claro)
        mecha_rect = pygame.Rect(cabeca_pos[0] - cabeca_largura//2 + 2,
                                cabeca_pos[1] - cabeca_altura//2 - 6,
                                cabeca_largura - 4, int(cabeca_altura * 0.7))
        pygame.draw.ellipse(char_surf, (255, 215, 0), mecha_rect)  # Tom mais claro

        # Franja estilizada
        franja_largura = cabeca_largura // 3
        for i in range(3):
            franja_x = cabeca_pos[0] - franja_largura//2 + (i * franja_largura//3) - franja_largura//6
            franja_y = cabeca_pos[1] - cabeca_altura//2 - 4
            # Desenhar pequenos triângulos para simular mechões de franja
            franja_points = [
                (franja_x, franja_y),
                (franja_x - 3, franja_y - 6),
                (franja_x + 3, franja_y - 6)
            ]
            pygame.draw.polygon(char_surf, (255, 215, 0), franja_points)

        # Reflexos no cabelo (para dar volume)
        reflexo_rect = pygame.Rect(cabeca_pos[0] - cabeca_largura//4,
                                  cabeca_pos[1] - cabeca_altura//2 - 3,
                                  cabeca_largura//3, cabeca_altura//4)
        pygame.draw.ellipse(char_surf, (255, 235, 50), reflexo_rect)  # Reflexo brilhante

        # Olhos
        self._desenhar_olhos_basicos(char_surf, cabeca_pos, cabeca_largura, cabeca_altura)

        # Bandana vermelha no pescoço
        bandana_rect = pygame.Rect(cabeca_pos[0] - 8, cabeca_pos[1] + cabeca_altura//3, 16, 6)
        pygame.draw.ellipse(char_surf, (200, 0, 0), bandana_rect)

        # Detalhes da jaqueta (zíper central)
        pygame.draw.line(char_surf, (180, 160, 0),
                        (centro[0], corpo_pos_y + 5),
                        (centro[0], corpo_pos_y + int(corpo_altura * 0.6)), 2)

        # Cartucheira no cinto
        cartucheira_rect = pygame.Rect(centro[0] + 8, corpo_pos_y + int(corpo_altura * 0.5), 8, 12)
        pygame.draw.rect(char_surf, (100, 50, 0), cartucheira_rect, border_radius=2)
        # Cartuchos individuais
        for i in range(3):
            cartucho_y = corpo_pos_y + int(corpo_altura * 0.52) + i * 3
            pygame.draw.circle(char_surf, (255, 215, 0), (centro[0] + 12, cartucho_y), 1)

        # BRAÇOS com shotgun
        mao_esq, mao_dir = self._desenhar_anatomia_bracos(char_surf, centro, corpo_largura,
        corpo_pos_y, corpo_altura, offsets_animacao, cor_pele)

        # Shotgun da Shelly (segurada com ambas as mãos) - posicionada entre as mãos
        shotgun_centro_x = (mao_esq[0] + mao_dir[0]) // 2  # Centro entre as duas mãos
        shotgun_pos = (shotgun_centro_x, mao_dir[1])
        shotgun_rect = pygame.Rect(shotgun_pos[0] - 12, shotgun_pos[1] - 3, 25, 6)
        pygame.draw.rect(char_surf, (60, 60, 60), shotgun_rect, border_radius=2)
        pygame.draw.rect(char_surf, (40, 40, 40), (shotgun_pos[0] + 8, shotgun_pos[1] - 2, 8, 4))# PERNAS com botas
        pe_esq, pe_dir = self._desenhar_anatomia_pernas(char_surf, centro, corpo_largura,
        corpo_pos_y, corpo_altura, offsets_animacao, (50, 50, 150)) # Botas marrons
        pygame.draw.ellipse(char_surf, (100, 50, 0), (pe_esq[0] - 8, pe_esq[1] - 5, 16, 10))
        pygame.draw.ellipse(char_surf, (100, 50, 0), (pe_dir[0] - 8, pe_dir[1] - 5, 16, 10))
        rect = char_surf.get_rect(center=pos)
        superficie.blit(char_surf, rect)

    def desenhar_nita_3d(self, superficie, pos, _cor_primaria, _cor_secundaria, tamanho, _tempo):
        """Desenha Nita com estilo tribal autêntico do Brawl Stars"""
        # Configuração básica usando métodos auxiliares
        offsets_animacao = self._configurar_animacao_personagem()
        char_surf, centro = self._criar_superficie_personagem(tamanho)

        # Configurações específicas da Nita
        corpo_altura = int(tamanho * 0.8)
        corpo_largura = int(tamanho * 0.6)
        corpo_pos_y = centro[1] - int(tamanho * 0.3) + int(offsets_animacao['balanco_corpo'])
        cor_pele = (205, 133, 63)  # Pele nativa

        # CORPO TRIBAL - Vestido marrom
        torso_rect = pygame.Rect(centro[0] - corpo_largura // 2, corpo_pos_y,
                                 corpo_largura, int(corpo_altura * 0.7))
        pygame.draw.rect(char_surf, (139, 69, 19), torso_rect, border_radius=6)

        # Saia tribal
        saia_largura = int(corpo_largura * 1.2)
        saia_rect = pygame.Rect(centro[0] - saia_largura // 2,
                               corpo_pos_y + int(corpo_altura * 0.5),
                               saia_largura, int(corpo_altura * 0.4))
        pygame.draw.rect(char_surf, (120, 60, 15), saia_rect, border_radius=4)

        # Detalhes tribais no vestido
        for i in range(3):
            detalhe_y = corpo_pos_y + 10 + i * 8
            pygame.draw.line(char_surf, (255, 215, 0),
            (centro[0] - corpo_largura//3, detalhe_y),
            (centro[0] + corpo_largura//3, detalhe_y), 2)

        # CABEÇA usando método auxiliar
        cabeca_pos = (centro[0] + int(offsets_animacao['rotacao_cabeca'] * 2),
                     centro[1] - int(tamanho * 0.6) + int(offsets_animacao['balanco_corpo']))
        cabeca_largura = int(tamanho * 0.4)
        cabeca_altura = int(tamanho * 0.5)

        self._desenhar_cabeca_oval(char_surf, cabeca_pos, cabeca_largura, cabeca_altura, cor_pele,
                                   corpo_pos_y, corpo_largura)

        # Cabelo preto com tranças específico da Nita
        cabelo_rect = pygame.Rect(cabeca_pos[0] - cabeca_largura//2,
        cabeca_pos[1] - cabeca_altura//2 - 5, cabeca_largura, int(cabeca_altura * 0.8))
        pygame.draw.ellipse(char_surf, (20, 20, 20), cabelo_rect)

        # Tranças laterais mais visíveis
        tranca_esq = pygame.Rect(cabeca_pos[0] - cabeca_largura//2 - 3, cabeca_pos[1], 4, 15)
        tranca_dir = pygame.Rect(cabeca_pos[0] + cabeca_largura//2 - 1, cabeca_pos[1], 4, 15)
        pygame.draw.rect(char_surf, (20, 20, 20), tranca_esq, border_radius=2)
        pygame.draw.rect(char_surf, (20, 20, 20), tranca_dir, border_radius=2)

        # Penas no cabelo
        pena_pos = (cabeca_pos[0] + cabeca_largura//3, cabeca_pos[1] - cabeca_altura//2 - 3)
        pygame.draw.line(char_surf, (255, 100, 0), pena_pos, (pena_pos[0], pena_pos[1] - 8), 2)
        pygame.draw.line(char_surf, (255, 200, 0),
        (pena_pos[0] + 2, pena_pos[1]), (pena_pos[0] + 2, pena_pos[1] - 6), 1)

        # Pintura facial tribal (listras nas bochechas)
        pygame.draw.line(char_surf, (255, 215, 0),
                        (cabeca_pos[0] - cabeca_largura//3, cabeca_pos[1]),
                        (cabeca_pos[0] - cabeca_largura//4, cabeca_pos[1] + 3), 2)
        pygame.draw.line(char_surf, (255, 215, 0),
                        (cabeca_pos[0] + cabeca_largura//4, cabeca_pos[1]),
                        (cabeca_pos[0] + cabeca_largura//3, cabeca_pos[1] + 3), 2)
        self._desenhar_olhos_basicos(char_surf, cabeca_pos, cabeca_largura, cabeca_altura)
        _, mao_dir = self._desenhar_anatomia_bracos(char_surf, centro, corpo_largura, corpo_pos_y, corpo_altura,
                                                          offsets_animacao, cor_pele) # Cajado mágico da Nita
        cajado_topo = (mao_dir[0] + 2, mao_dir[1] - 20)  # Posição do topo do cajado
        pygame.draw.line(char_surf, (139, 69, 19), mao_dir, cajado_topo, 3)
        # Cristal no topo
        pygame.draw.circle(char_surf, (147, 0, 211), cajado_topo, 4)
        pygame.draw.circle(char_surf, (200, 100, 255), cajado_topo, 2)

        # PERNAS usando método auxiliar (adaptado para saia)
        quadril_y = corpo_pos_y + int(corpo_altura * 0.8)
        saia_largura_conectada = int(corpo_largura * 0.8)
        quadril_esq_x = centro[0] - saia_largura_conectada//4
        quadril_dir_x = centro[0] + saia_largura_conectada//4

        # Coxas conectadas aos quadris (sob a saia) - específico para Nita
        coxa_esq_pos = (quadril_esq_x + int(offsets_animacao['offset_perna_esq'][0]), quadril_y)
        coxa_dir_pos = (quadril_dir_x + int(offsets_animacao['offset_perna_dir'][0]), quadril_y)

        # Conexão quadril-coxa
        pygame.draw.circle(char_surf, cor_pele, (quadril_esq_x, quadril_y), 4)
        pygame.draw.circle(char_surf, cor_pele, (quadril_dir_x, quadril_y), 4)

        # Coxas (pele)
        coxa_altura = 16
        pygame.draw.rect(char_surf, cor_pele, (coxa_esq_pos[0] - 5, coxa_esq_pos[1], 10, coxa_altura), border_radius=4)
        pygame.draw.rect(char_surf, cor_pele, (coxa_dir_pos[0] - 5, coxa_dir_pos[1], 10, coxa_altura), border_radius=4)

        # Joelhos e pernas
        joelho_esq = (coxa_esq_pos[0], coxa_esq_pos[1] + coxa_altura)
        joelho_dir = (coxa_dir_pos[0], coxa_dir_pos[1] + coxa_altura)
        cor_joelho = self._cor_mais_escura(cor_pele, 20)
        pygame.draw.circle(char_surf, cor_joelho, joelho_esq, 4)
        pygame.draw.circle(char_surf, cor_joelho, joelho_dir, 4)

        # Pernas (canelas)
        perna_altura = 14
        pygame.draw.rect(char_surf, cor_pele, (joelho_esq[0] - 4, joelho_esq[1], 8, perna_altura), border_radius=3)
        pygame.draw.rect(char_surf, cor_pele, (joelho_dir[0] - 4, joelho_dir[1], 8, perna_altura), border_radius=3)

        # Posições dos pés
        perna_esq_pos = (joelho_esq[0], joelho_esq[1] + perna_altura)
        perna_dir_pos = (joelho_dir[0], joelho_dir[1] + perna_altura)        # Sandálias tribais
        pygame.draw.ellipse(char_surf, (139, 69, 19), (perna_esq_pos[0] - 7, perna_esq_pos[1] - 2, 14, 8))
        pygame.draw.ellipse(char_surf, (139, 69, 19), (perna_dir_pos[0] - 7, perna_dir_pos[1] - 2, 14, 8))

        rect = char_surf.get_rect(center=pos)
        superficie.blit(char_surf, rect)

    def desenhar_colt_3d(self, superficie, pos, _cor_primaria, _cor_secundaria, tamanho, _tempo):
        """Desenha Colt - Xerife cowboy autêntico do Brawl Stars"""
        # Configuração básica usando métodos auxiliares
        offsets_animacao = self._configurar_animacao_personagem()
        char_surf, centro = self._criar_superficie_personagem(tamanho)

        # Configurações específicas do Colt
        corpo_altura = int(tamanho * 0.8)
        corpo_largura = int(tamanho * 0.7)
        corpo_pos_y = centro[1] - int(tamanho * 0.3) + int(offsets_animacao['balanco_corpo'])
        cor_pele = (255, 220, 177)  # Pele clara

        # CORPO COWBOY - Colete azul
        torso_rect = pygame.Rect(centro[0] - corpo_largura // 2, corpo_pos_y,
                                 corpo_largura, int(corpo_altura * 0.7))
        pygame.draw.rect(char_surf, (30, 144, 255), torso_rect, border_radius=6)

        # Distintivo de xerife dourado
        distintivo_pos = (centro[0] - 8, corpo_pos_y + 8)
        pygame.draw.polygon(char_surf, (255, 215, 0), [
            (distintivo_pos[0], distintivo_pos[1] - 5),
            (distintivo_pos[0] - 5, distintivo_pos[1]),
            (distintivo_pos[0], distintivo_pos[1] + 5),
            (distintivo_pos[0] + 5, distintivo_pos[1])])

        # MELHORIAS COLT:
        # Coldre duplo no cinto
        coldre_esq_rect = pygame.Rect(centro[0] - corpo_largura//3, corpo_pos_y + int(corpo_altura * 0.6), 6, 8)
        coldre_dir_rect = pygame.Rect(centro[0] + corpo_largura//4, corpo_pos_y + int(corpo_altura * 0.6), 6, 8)
        pygame.draw.rect(char_surf, (100, 50, 0), coldre_esq_rect, border_radius=2)
        pygame.draw.rect(char_surf, (100, 50, 0), coldre_dir_rect, border_radius=2)
        # Cinto de couro com fivela
        cinto_rect = pygame.Rect(centro[0] - corpo_largura//2, corpo_pos_y + int(corpo_altura * 0.58), corpo_largura, 4)
        pygame.draw.rect(char_surf, (139, 69, 19), cinto_rect)
        # Fivela dourada
        pygame.draw.rect(char_surf, (255, 215, 0), (centro[0] - 4,
        corpo_pos_y + int(corpo_altura * 0.58), 8, 4))

        # CABEÇA usando método auxiliar
        cabeca_pos = (centro[0] + int(offsets_animacao['rotacao_cabeca'] * 2),
                     centro[1] - int(tamanho * 0.6) + int(offsets_animacao['balanco_corpo']))
        cabeca_largura = int(tamanho * 0.4)
        cabeca_altura = int(tamanho * 0.5)

        self._desenhar_cabeca_oval(char_surf, cabeca_pos, cabeca_largura, cabeca_altura, cor_pele,
                                   corpo_pos_y, corpo_largura)

        # Chapéu cowboy marrom específico do Colt
        chapeu_rect = pygame.Rect(cabeca_pos[0] - cabeca_largura//2 - 5, cabeca_pos[1] - cabeca_altura//2 - 8,
                                  cabeca_largura + 10, cabeca_altura//2 + 3)
        pygame.draw.ellipse(char_surf, (139, 69, 19), chapeu_rect)

        # Copa do chapéu
        copa_rect = pygame.Rect(cabeca_pos[0] - cabeca_largura//3,
        cabeca_pos[1] - cabeca_altura//2 - 5, cabeca_largura//1.5, cabeca_altura//1.5)
        pygame.draw.ellipse(char_surf, (160, 82, 45), copa_rect)

        # Olhos usando método auxiliar
        self._desenhar_olhos_basicos(char_surf, cabeca_pos, cabeca_largura, cabeca_altura)        # BRAÇOS usando método auxiliar
        mao_esq, mao_dir = self._desenhar_anatomia_bracos(char_surf, centro, corpo_largura, corpo_pos_y, corpo_altura,
                                                          offsets_animacao, cor_pele)

        # Pistolas duplas do Colt - posicionadas exatamente nas mãos
        pistola1_pos = mao_dir  # Pistola direita na mão direita
        pistola2_pos = mao_esq  # Pistola esquerda na mão esquerda

        # Pistola direita - centrada na mão
        pygame.draw.rect(char_surf, (60, 60, 60), (pistola1_pos[0] - 6, pistola1_pos[1] - 2, 12, 4))
        pygame.draw.circle(char_surf, (40, 40, 40), (pistola1_pos[0] + 6, pistola1_pos[1]), 2)

        # Pistola esquerda - centrada na mão
        pygame.draw.rect(char_surf, (60, 60, 60), (pistola2_pos[0] - 6, pistola2_pos[1] - 2, 12, 4))
        pygame.draw.circle(char_surf, (40, 40, 40), (pistola2_pos[0] - 6, pistola2_pos[1]), 2)

        # PERNAS usando método auxiliar
        pe_esq, pe_dir = self._desenhar_anatomia_pernas(char_surf, centro, corpo_largura,
        corpo_pos_y, corpo_altura, offsets_animacao, (139, 69, 19))

        # Botas cowboy pretas específicas do Colt
        pygame.draw.ellipse(char_surf, (0, 0, 0), (pe_esq[0] - 8, pe_esq[1] - 5, 16, 10))
        pygame.draw.ellipse(char_surf, (0, 0, 0), (pe_dir[0] - 8, pe_dir[1] - 5, 16, 10))
        # Esporas douradas
        pygame.draw.circle(char_surf, (255, 215, 0), (pe_esq[0] + 8, pe_esq[1] + 2), 2)
        pygame.draw.circle(char_surf, (255, 215, 0), (pe_dir[0] + 8, pe_dir[1] + 2), 2)

        rect = char_surf.get_rect(center=pos)
        superficie.blit(char_surf, rect)

    def desenhar_bull_3d(self, superficie, pos, _cor_primaria, _cor_secundaria, tamanho, _tempo):
        """Desenha Bull - Tank robusto com shotgun"""
        # Atualizar animador
        offsets_animacao = self._configurar_animacao_personagem()

        char_surf, centro = self._criar_superficie_personagem(tamanho)

        # CORPO ROBUSTO - Jaqueta de couro preta
        corpo_altura = int(tamanho * 0.9)
        corpo_largura = int(tamanho * 0.8)
        corpo_pos_y = centro[1] - int(tamanho * 0.3) + int(offsets_animacao['balanco_corpo'])

        # Jaqueta de couro preta
        torso_rect = pygame.Rect(centro[0] - corpo_largura // 2, corpo_pos_y,
                                 corpo_largura, int(corpo_altura * 0.7))
        cor_jaqueta = (30, 30, 30)  # Preto
        pygame.draw.rect(char_surf, cor_jaqueta, torso_rect, border_radius=8) # Detalhes metálicos na jaqueta
        for i in range(3):
            botao_x = centro[0] - 5 + i * 5
            botao_y = corpo_pos_y + 10 + i * 8
            pygame.draw.circle(char_surf, (200, 200, 200), (botao_x, botao_y), 2)

        # Correntes metálicas na jaqueta
        pygame.draw.line(char_surf, (200, 200, 200),
                        (centro[0] - corpo_largura//3, corpo_pos_y + 5),
                        (centro[0] + corpo_largura//3, corpo_pos_y + 5), 2)
        # Elos da corrente
        for i in range(5):
            elo_x = centro[0] - corpo_largura//3 + i * (corpo_largura//6)
            pygame.draw.circle(char_surf, (180, 180, 180), (elo_x, corpo_pos_y + 5), 2, 1)

        # Tachas na jaqueta
        for i in range(2):
            for j in range(3):
                tacha_x = centro[0] - corpo_largura//4 + j * (corpo_largura//4)
                tacha_y = corpo_pos_y + 15 + i * 12
                pygame.draw.circle(char_surf, (150, 150, 150), (tacha_x, tacha_y), 1)

        # CABEÇA oval mais realista - careca e robusta
        cabeca_pos = (centro[0] + int(offsets_animacao['rotacao_cabeca'] * 2), centro[1] - int(tamanho * 0.6) + int(offsets_animacao['balanco_corpo']))
        cabeca_largura = int(tamanho * 0.45)  # Mais largo
        cabeca_altura = int(tamanho * 0.55)   # Mais alto

        # Desenhar cabeça com pescoço usando método auxiliar
        self._desenhar_cabeca_oval(char_surf, cabeca_pos, cabeca_largura, cabeca_altura, (255, 220, 177),
                                   corpo_pos_y, corpo_largura)

        # Careca brilhante (sem cabelo)
        brilho_rect = pygame.Rect(cabeca_pos[0] - cabeca_largura//4, cabeca_pos[1] - cabeca_altura//2 + 3,
                                 cabeca_largura//2, cabeca_altura//4)
        pygame.draw.ellipse(char_surf, (255, 240, 200), brilho_rect)

        # Olhos pequenos e sérios usando método auxiliar
        self._desenhar_olhos_basicos(char_surf, cabeca_pos, cabeca_largura, cabeca_altura)

        # Bigode grosso
        bigode_rect = pygame.Rect(cabeca_pos[0] - 8, cabeca_pos[1], 16, 4)
        pygame.draw.ellipse(char_surf, (100, 50, 0), bigode_rect)        # BRAÇOS usando método auxiliar
        _, mao_dir = self._desenhar_anatomia_bracos(char_surf, centro, corpo_largura, corpo_pos_y, corpo_altura,
        offsets_animacao, (255, 220, 177))# Shotgun grande do Bull - posicionada na mão direita
        shotgun_pos = mao_dir  # Shotgun na mão direita
        shotgun_rect = pygame.Rect(shotgun_pos[0] - 5, shotgun_pos[1] - 4, 25, 8)
        pygame.draw.rect(char_surf, (40, 40, 40), shotgun_rect, border_radius=3)

        # Cano duplo - ajustado para a nova posição
        pygame.draw.circle(char_surf, (20, 20, 20), (shotgun_pos[0] + 18, shotgun_pos[1] - 2), 2)
        pygame.draw.circle(char_surf, (20, 20, 20), (shotgun_pos[0] + 18, shotgun_pos[1] + 2), 2)

        # PERNAS conectadas ao tronco - robustas
        # Quadris conectados ao torso
        quadril_y = corpo_pos_y + int(corpo_altura * 0.7)
        quadril_esq_x = centro[0] - corpo_largura//4
        quadril_dir_x = centro[0] + corpo_largura//4

        # Coxas conectadas aos quadris
        coxa_esq_pos = (quadril_esq_x + int(offsets_animacao['offset_perna_esq'][0]), quadril_y)
        coxa_dir_pos = (quadril_dir_x + int(offsets_animacao['offset_perna_dir'][0]), quadril_y)

        # Conexão quadril-coxa
        pygame.draw.circle(char_surf, (255, 220, 177), (quadril_esq_x, quadril_y), 5)
        pygame.draw.circle(char_surf, (255, 220, 177), (quadril_dir_x, quadril_y), 5)

        # Coxas grossas (parte superior das pernas)
        coxa_esq_rect = pygame.Rect(coxa_esq_pos[0] - 8, coxa_esq_pos[1], 16, 18)
        coxa_dir_rect = pygame.Rect(coxa_dir_pos[0] - 8, coxa_dir_pos[1], 16, 18)
        pygame.draw.rect(char_surf, (20, 20, 20), coxa_esq_rect, border_radius=5)
        pygame.draw.rect(char_surf, (20, 20, 20), coxa_dir_rect, border_radius=5)

        # Joelhos
        joelho_esq = (coxa_esq_pos[0], coxa_esq_pos[1] + 18)
        joelho_dir = (coxa_dir_pos[0], coxa_dir_pos[1] + 18)
        pygame.draw.circle(char_surf, (40, 40, 40), joelho_esq, 4)
        pygame.draw.circle(char_surf, (40, 40, 40), joelho_dir, 4)
          # Panturrilhas
        panturrilha_esq_rect = pygame.Rect(joelho_esq[0] - 7, joelho_esq[1], 14, 15)
        panturrilha_dir_rect = pygame.Rect(joelho_dir[0] - 7, joelho_dir[1], 14, 15)
        pygame.draw.rect(char_surf, (20, 20, 20), panturrilha_esq_rect, border_radius=4)
        pygame.draw.rect(char_surf, (20, 20, 20), panturrilha_dir_rect, border_radius=4)

        # Posições dos pés
        perna_esq_pos = (joelho_esq[0], joelho_esq[1] + 15)
        perna_dir_pos = (joelho_dir[0], joelho_dir[1] + 15) # Botas pesadas pretas
        pygame.draw.ellipse(char_surf, (0, 0, 0),
                           (perna_esq_pos[0] - 10, perna_esq_pos[1] - 2, 20, 12))
        pygame.draw.ellipse(char_surf, (0, 0, 0),
                           (perna_dir_pos[0] - 10, perna_dir_pos[1] - 2, 20, 12))

        # Detalhes metálicos nas botas
        pygame.draw.rect(char_surf, (150, 150, 150),
                        (perna_esq_pos[0] - 8, perna_esq_pos[1], 16, 2))
        pygame.draw.rect(char_surf, (150, 150, 150),
                        (perna_dir_pos[0] - 8, perna_dir_pos[1], 16, 2))

        rect = char_surf.get_rect(center=pos)
        superficie.blit(char_surf, rect)

    def desenhar_barley_3d(self, superficie, pos, _cor_primaria, _cor_secundaria, tamanho, _tempo):
        """Desenha Barley - Bartender com garrafas explosivas"""
        # Atualizar animador
        offsets_animacao = self._configurar_animacao_personagem()

        char_surf, centro = self._criar_superficie_personagem(tamanho)
        # CORPO - Tronco de bartender mais anatômico
        corpo_altura = int(tamanho * 0.8)
        corpo_largura = int(tamanho * 0.7)
        corpo_pos_y = centro[1] - int(tamanho * 0.25) + int(offsets_animacao['balanco_corpo'])  # Ajustado para baixar as pernas

        # Tronco principal oval (não circular)
        tronco_rect = pygame.Rect(centro[0] - corpo_largura // 2, corpo_pos_y,
                                 corpo_largura, int(corpo_altura * 0.7))
        pygame.draw.ellipse(char_surf, (255, 255, 255), tronco_rect)

        # Avental marrom por cima
        avental_rect = pygame.Rect(centro[0] - corpo_largura // 3, corpo_pos_y + 5,
                                   corpo_largura // 1.5, int(corpo_altura * 0.8))
        pygame.draw.rect(char_surf, (139, 69, 19), avental_rect, border_radius=4)

        # Bolso no avental com detalhes
        bolso_rect = pygame.Rect(centro[0] - 6, corpo_pos_y + 15, 12, 8)
        pygame.draw.rect(char_surf, (120, 60, 15), bolso_rect, border_radius=2)
        pygame.draw.line(char_surf, (100, 50, 10), (centro[0] - 6, corpo_pos_y + 15),
        (centro[0] + 6, corpo_pos_y + 15), 1)
        # Gravata borboleta
        gravata_rect = pygame.Rect(centro[0] - 5, corpo_pos_y - 2, 10, 4)
        pygame.draw.ellipse(char_surf, (200, 0, 0), gravata_rect)
        pygame.draw.rect(char_surf, (150, 0, 0), (centro[0] - 1, corpo_pos_y - 2, 2, 4))

        # Botões da camisa
        for i in range(3):
            botao_y = corpo_pos_y + 8 + i * 6
            pygame.draw.circle(char_surf, (240, 240, 240), (centro[0] + 8, botao_y), 1)

        # CABEÇA mais oval com bigode característico
        cabeca_pos = (centro[0] + int(offsets_animacao['rotacao_cabeca'] * 2), centro[1] - int(tamanho * 0.6) + int(offsets_animacao['balanco_corpo']))
        cabeca_largura = int(tamanho * 0.45)
        cabeca_altura = int(tamanho * 0.5)

        # Desenhar cabeça com pescoço usando método auxiliar
        self._desenhar_cabeca_oval(char_surf, cabeca_pos, cabeca_largura, cabeca_altura, (255, 220, 177),
                                   corpo_pos_y, corpo_largura)

        # Cabelo grisalho lateral
        cabelo_rect = pygame.Rect(cabeca_pos[0] - cabeca_largura//2,
        cabeca_pos[1] - cabeca_altura//2, cabeca_largura, int(cabeca_altura * 0.7))
        pygame.draw.ellipse(char_surf, (150, 150, 150), cabelo_rect)

        # Careca no topo
        calva_rect = pygame.Rect(cabeca_pos[0] - cabeca_largura//3,
        cabeca_pos[1] - cabeca_altura//2, cabeca_largura//1.5, cabeca_altura//2)
        pygame.draw.ellipse(char_surf, (255, 220, 177), calva_rect)

        # Olhos usando método auxiliar
        self._desenhar_olhos_basicos(char_surf, cabeca_pos, cabeca_largura, cabeca_altura)

        # Bigode característico mais realista do Barley
        bigode_rect = pygame.Rect(cabeca_pos[0] - 12, cabeca_pos[1] + cabeca_altura//6, 24, 8)
        pygame.draw.ellipse(char_surf, (150, 150, 150), bigode_rect)
        _, mao_dir = self._desenhar_anatomia_bracos(char_surf, centro, corpo_largura, corpo_pos_y, corpo_altura,
                                                          offsets_animacao, (255, 220, 177))

        # Garrafa explosiva do Barley - posicionada exatamente na mão direita
        garrafa_pos = mao_dir  # Garrafa na mão direita

        # Corpo da garrafa - centrada na mão
        pygame.draw.rect(char_surf, (0, 100, 0), (garrafa_pos[0] - 3, garrafa_pos[1] - 7, 6, 15), border_radius=3)

        # Gargalo
        pygame.draw.rect(char_surf, (0, 80, 0), (garrafa_pos[0] - 2, garrafa_pos[1] - 12, 4, 8))

        # Líquido dentro
        pygame.draw.rect(char_surf, (255, 165, 0), (garrafa_pos[0] - 2, garrafa_pos[1] - 5, 4, 10))        # Pavio aceso - ajustado para a nova posição
        pygame.draw.line(char_surf, (255, 0, 0),
                        (garrafa_pos[0], garrafa_pos[1] - 12),
                        (garrafa_pos[0] + 3, garrafa_pos[1] - 15), 2)

        # PERNAS usando método auxiliar
        pe_esq, pe_dir = self._desenhar_anatomia_pernas(char_surf, centro, corpo_largura,
        corpo_pos_y, corpo_altura, offsets_animacao, (101, 67, 33)) # Sapatos mais detalhados
        pygame.draw.ellipse(char_surf, (0, 0, 0),
                           (pe_esq[0] - 8, pe_esq[1] - 5, 16, 10))
        pygame.draw.ellipse(char_surf, (0, 0, 0),
                           (pe_dir[0] - 8, pe_dir[1] - 5, 16, 10))

        # Detalhes dos sapatos
        pygame.draw.ellipse(char_surf, (60, 60, 60),
                           (pe_esq[0] - 6, pe_esq[1] - 3, 12, 6))
        pygame.draw.ellipse(char_surf, (60, 60, 60),
                           (pe_dir[0] - 6, pe_dir[1] - 3, 12, 6))

        rect = char_surf.get_rect(center=pos)
        superficie.blit(char_surf, rect)

    def desenhar_poco_3d(self, superficie, pos, _cor_primaria, _cor_secundaria, tamanho, _tempo):
        """Desenha Poco - Esqueleto músico mexicano"""
        # Atualizar animador
        offsets_animacao = self._configurar_animacao_personagem()
        char_surf, centro = self._criar_superficie_personagem(tamanho)

        # CORPO ESQUELÉTICO - Tronco mais anatômico
        corpo_altura = int(tamanho * 0.8)
        corpo_largura = int(tamanho * 0.6)  # Mais magro
        corpo_pos_y = centro[1] - int(tamanho * 0.3) + int(offsets_animacao['balanco_corpo'])

        # Tronco oval elegante (não retangular)
        torso_rect = pygame.Rect(centro[0] - corpo_largura // 2, corpo_pos_y,
                                 corpo_largura, int(corpo_altura * 0.7))
        cor_terno = (50, 100, 150)  # Azul escuro
        pygame.draw.ellipse(char_surf, cor_terno, torso_rect)

        # Conectar tronco às pernas com quadris
        quadris_rect = pygame.Rect(centro[0] - corpo_largura // 3,
        corpo_pos_y + int(corpo_altura * 0.55), corpo_largura // 1.5, int(corpo_altura * 0.25))
        pygame.draw.ellipse(char_surf, (50, 100, 150), quadris_rect)

        # Gravata vermelha
        gravata_rect = pygame.Rect(centro[0] - 3, corpo_pos_y + 5, 6, 20)
        pygame.draw.rect(char_surf, (200, 0, 0), gravata_rect)

        # Nó da gravata mais detalhado
        no_gravata = pygame.Rect(centro[0] - 4, corpo_pos_y + 3, 8, 5)
        pygame.draw.rect(char_surf, (180, 0, 0), no_gravata)

        # Colete por baixo da gravata
        colete_rect = pygame.Rect(centro[0] - corpo_largura//3, corpo_pos_y + 3, corpo_largura//1.5, int(corpo_altura * 0.4))
        pygame.draw.ellipse(char_surf, (40, 80, 120), colete_rect)

        # CABEÇA DE CAVEIRA mais oval com sombrero
        cabeca_pos = (centro[0] + int(offsets_animacao['rotacao_cabeca'] * 2), centro[1] - int(tamanho * 0.6) + int(offsets_animacao['balanco_corpo']))
        cabeca_largura = int(tamanho * 0.45)
        cabeca_altura = int(tamanho * 0.5)

        # Desenhar cabeça caveira com pescoço usando método auxiliar
        self._desenhar_cabeca_oval(char_surf, cabeca_pos, cabeca_largura, cabeca_altura, (255, 255, 255),
                                   corpo_pos_y, corpo_largura)

        # Sombrero mexicano
        sombrero_rect = pygame.Rect(cabeca_pos[0] - cabeca_largura//2 - 8, cabeca_pos[1] - cabeca_altura//2 - 6,
                                    cabeca_largura + 16, cabeca_altura // 3)
        pygame.draw.ellipse(char_surf, (200, 0, 0), sombrero_rect)  # Aba vermelha

        # Copa do sombrero
        copa_rect = pygame.Rect(cabeca_pos[0] - cabeca_largura//3, cabeca_pos[1] - cabeca_altura//2 - 8,
                                cabeca_largura//1.5, cabeca_altura//1.2)
        pygame.draw.ellipse(char_surf, (220, 20, 20), copa_rect)

        # Detalhes dourados no sombrero
        pygame.draw.ellipse(char_surf, (255, 215, 0),
                           (cabeca_pos[0] - cabeca_largura//2 - 6, cabeca_pos[1] - cabeca_altura//2 - 4,
                           cabeca_largura + 12, 4))

        # Olhos de caveira (buracos negros)
        olho_esq = (cabeca_pos[0] - cabeca_largura//4, cabeca_pos[1] - cabeca_altura//5)
        olho_dir = (cabeca_pos[0] + cabeca_largura//4, cabeca_pos[1] - cabeca_altura//5)
        pygame.draw.circle(char_surf, (0, 0, 0), olho_esq, 5)
        pygame.draw.circle(char_surf, (0, 0, 0), olho_dir, 5)

        # Brilho sobrenatural nos olhos
        pygame.draw.circle(char_surf, (0, 255, 255), olho_esq, 2)
        pygame.draw.circle(char_surf, (0, 255, 255), olho_dir, 2)

        # Nariz de caveira triangular
        nariz_points = [
            (cabeca_pos[0], cabeca_pos[1] - 2),
            (cabeca_pos[0] - 4, cabeca_pos[1] + 4),
            (cabeca_pos[0] + 4, cabeca_pos[1] + 4)
        ]
        pygame.draw.polygon(char_surf, (0,  0, 0), nariz_points)        # Boca sorridente de caveira
        pygame.draw.arc(char_surf, (0, 0, 0),
                       (cabeca_pos[0] - 10, cabeca_pos[1] + 4, 20, 12), 0, math.pi, 3)        # BRAÇOS usando método auxiliar (cor esqueletal)
        mao_esq, _ = self._desenhar_anatomia_bracos(char_surf, centro, corpo_largura, corpo_pos_y, corpo_altura,
                                                          offsets_animacao, (255, 255, 255))

        # Guitarra do Poco - posicionada na mão esquerda
        guitarra_pos = (mao_esq[0] - 8, mao_esq[1] - 10)  # Ajustado para melhor posicionamento

        # Corpo da guitarra
        guitarra_rect = pygame.Rect(guitarra_pos[0], guitarra_pos[1], 16, 24)
        pygame.draw.ellipse(char_surf, (139, 69, 19), guitarra_rect)

        # Buraco no meio
        pygame.draw.circle(char_surf, (0, 0, 0),
                          (guitarra_pos[0] + 8, guitarra_pos[1] + 12), 4)

        # Braço da guitarra
        pygame.draw.rect(char_surf, (101, 67, 33),
                        (guitarra_pos[0] + 6, guitarra_pos[1] - 15, 4, 20))        # Cordas
        for i in range(3):
            corda_x = guitarra_pos[0] + 6 + i
            pygame.draw.line(char_surf, (200, 200, 200),
                           (corda_x, guitarra_pos[1] - 10),
                           (corda_x, guitarra_pos[1] + 20), 1) # PERNAS E PÉS usando método auxiliar (cor esqueletal)
        self._desenhar_anatomia_pernas(char_surf, centro, corpo_largura, corpo_pos_y, corpo_altura,
                                       offsets_animacao, (255, 255, 255))

        rect = char_surf.get_rect(center=pos)
        superficie.blit(char_surf, rect)

    def calcular_altura_camera(self, zoom_level: float = 1.0, modo_jogo: str = "normal") -> int:
        """
        Calcula altura da câmera dinamicamente baseada no contexto do jogo.
        Substitui a variável altura_camera fixa por um cálculo dinâmico.
        """
        altura_base = 100
        # Ajustar baseado no modo de jogo
        if modo_jogo == "combate":
            altura_base *= 0.8  # Câmera mais baixa para combate intenso
        elif modo_jogo == "exploracao":
            altura_base *= 1.2  # Câmera mais alta para visão ampla
        # Ajustar baseado no zoom
        altura_ajustada = altura_base / zoom_level
        return int(altura_ajustada)

    def obter_info_debug(self) -> dict:
        """
        Retorna informações de debug do renderer para ferramentas de desenvolvimento.
        Aproveita o cache _debug_info para otimização.
        """
        if not self._debug_info:
            self._debug_info = {
                "luz_ambiente": self.luz_ambiente,
                "luz_direcional": (self.luz_direcional.x, self.luz_direcional.y),
                "personagem_ativo": self._personagem_atual is not None,
                "metodos_personagem": [attr for attr in dir(self) if attr.startswith("desenhar_") and attr.endswith("_3d")]
            }
        return self._debug_info.copy()

    def limpar_cache_debug(self):
        """Limpa cache de debug para forçar atualização nas próximas consultas"""
        self._debug_info.clear()

    def definir_personagem_atual(self, personagem):
        """Define o personagem atual para uso nas animações"""
        self._personagem_atual = personagem

    def obter_personagem_atual(self):
        """Obtém o personagem atual"""
        return self._personagem_atual

    def _configurar_animacao_personagem(self):
        """Configura os offsets de animação para personagens"""
        # Obter estados reais do personagem atual se disponível
        em_movimento = False
        poder_ativo = False

        # Verificar se temos um personagem atual com estados
        if hasattr(self, '_personagem_atual') and self._personagem_atual:
            em_movimento = getattr(self._personagem_atual, 'em_movimento', False)
            poder_ativo = getattr(self._personagem_atual, 'poder_ativo', False)

        # Ajustar velocidades com base nos estados
        vel_x = 50 if em_movimento else 0
        vel_y = 30 if em_movimento else 0

        # Atualizar animador global com os estados reais
        animador_global.atualizar(0.016, vel_x, vel_y, poder_ativo)

        # Retornar todos os offsets necessários
        return {
            'balanco_corpo': animador_global.obter_balanco_corpo(),
            'offset_braco_esq': animador_global.obter_offset_braco_esquerdo(),
            'offset_braco_dir': animador_global.obter_offset_braco_direito(),
            'offset_perna_esq': animador_global.obter_offset_perna_esquerda(),
            'offset_perna_dir': animador_global.obter_offset_perna_direita(),
            'rotacao_cabeca': animador_global.obter_rotacao_cabeca()
        }

    def _criar_superficie_personagem(self, tamanho: int) -> Tuple[pygame.Surface, Tuple[int, int]]:
        """Cria a superfície base para desenho de personagem - método auxiliar"""
        # Aumentar a superfície para garantir espaço para pernas, especialmente em tamanhos pequenos
        largura_surf = max(tamanho * 2, 80)
        altura_surf = max(int(tamanho * 2.5), 100)
        char_surf = pygame.Surface((largura_surf, altura_surf), SRCALPHA)
        centro = (largura_surf // 2, int(altura_surf * 0.4))  # Centro ajustado para dar espaço às pernas

        # Desenhar sombra próxima aos pés (não na base absoluta da superfície)
        sombra_largura = max(20, int(tamanho * 0.9))  # Sombra proporcional
        sombra_altura = 6  # Sombra um pouco mais alta para visibilidade
        sombra_x = largura_surf // 2 - sombra_largura // 2
        # Posicionar sombra onde os pés ficam (aproximadamente 85% da altura da superfície)
        sombra_y = int(altura_surf * 0.85)

        # Criar uma elipse sutil para a sombra no chão
        sombra_rect = pygame.Rect(sombra_x, sombra_y, sombra_largura, sombra_altura)
        pygame.draw.ellipse(char_surf, (0, 0, 0, 50), sombra_rect)
        return char_surf, centro

    def _desenhar_cabeca_oval(self, char_surf: pygame.Surface, cabeca_pos: Tuple[int, int],
                             largura: int, altura: int, cor_pele: Tuple[int, int, int],
                             corpo_pos_y: int = None, corpo_largura: int = None) -> pygame.Rect:
        """Desenha cabeça oval básica com pescoço - método auxiliar para reduzir duplicação"""
        # Desenhar pescoço conectando cabeça ao corpo
        if corpo_pos_y is not None and corpo_largura is not None:
            pescoço_largura = largura // 3
            pescoço_altura = abs(cabeca_pos[1] + altura//2 - corpo_pos_y) + 5
            pescoço_rect = pygame.Rect(cabeca_pos[0] - pescoço_largura//2,
                                     cabeca_pos[1] + altura//2 - 3,
                                     pescoço_largura, pescoço_altura)
            pygame.draw.rect(char_surf, cor_pele, pescoço_rect, border_radius=3)

        # Desenhar cabeça oval
        cabeca_rect = pygame.Rect(cabeca_pos[0] - largura//2,
        cabeca_pos[1] - altura//2, largura, altura)
        pygame.draw.ellipse(char_surf, cor_pele, cabeca_rect)
        return cabeca_rect

    def _desenhar_olhos_basicos(self, char_surf: pygame.Surface, cabeca_pos: Tuple[int, int],
                               largura: int, altura: int):
        """Desenha olhos básicos - método auxiliar para reduzir duplicação"""
        olho_esq = (cabeca_pos[0] - largura//4, cabeca_pos[1] - altura//6)
        olho_dir = (cabeca_pos[0] + largura//4, cabeca_pos[1] - altura//6)
        pygame.draw.circle(char_surf, (255, 255, 255), olho_esq, 3)
        pygame.draw.circle(char_surf, (255, 255, 255), olho_dir, 3)
        # Pupilas
        pygame.draw.circle(char_surf, (0, 0, 0), olho_esq, 2)
        pygame.draw.circle(char_surf, (0, 0, 0), olho_dir, 2)

    def _desenhar_anatomia_bracos(self, char_surf: pygame.Surface, centro: Tuple[int, int],
        corpo_largura: int, corpo_pos_y: int, corpo_altura: int, offsets_animacao: dict,
        cor_pele: Tuple[int, int, int]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Desenha anatomia completa dos braços - método auxiliar usando proporções relativas"""
        # Tamanhos baseados em proporções do corpo para garantir consistência
        tamanho_ombro = max(3, int(corpo_altura * 0.12))  # 12% da altura do corpo
        altura_braco_superior = max(8, int(corpo_altura * 0.25))  # 25% da altura do corpo
        largura_braco = max(4, int(corpo_altura * 0.1))  # 10% da altura do corpo
        altura_antebraco = max(6, int(corpo_altura * 0.2))  # 20% da altura do corpo
        largura_antebraco = max(3, int(corpo_altura * 0.08))  # 8% da altura do corpo
        tamanho_mao = max(2, int(corpo_altura * 0.08))  # 8% da altura do corpo

        # Posições dos ombros baseadas no corpo
        offset_ombro = max(3, int(corpo_largura * 0.1))
        ombro_esq_pos = (centro[0] - corpo_largura//2 - offset_ombro, corpo_pos_y + int(corpo_altura * 0.15))
        ombro_dir_pos = (centro[0] + corpo_largura//2 + offset_ombro, corpo_pos_y + int(corpo_altura * 0.15))

        # Ombros
        pygame.draw.circle(char_surf, cor_pele, ombro_esq_pos, tamanho_ombro)
        pygame.draw.circle(char_surf, cor_pele, ombro_dir_pos, tamanho_ombro)

        # Braços superiores (cotovelos)
        braco_sup_esq = (ombro_esq_pos[0] + int(offsets_animacao['offset_braco_esq'][0]),
                        ombro_esq_pos[1] + altura_braco_superior + int(offsets_animacao['offset_braco_esq'][1]))
        braco_sup_dir = (ombro_dir_pos[0] + int(offsets_animacao['offset_braco_dir'][0]),
                        ombro_dir_pos[1] + altura_braco_superior + int(offsets_animacao['offset_braco_dir'][1]))

        # Desenhar braços superiores conectando ombros aos cotovelos
        pygame.draw.rect(char_surf, cor_pele, (braco_sup_esq[0] - largura_braco//2, ombro_esq_pos[1], largura_braco, altura_braco_superior), border_radius=2)
        pygame.draw.rect(char_surf, cor_pele, (braco_sup_dir[0] - largura_braco//2, ombro_dir_pos[1], largura_braco, altura_braco_superior), border_radius=2)

        # Cotovelos
        cor_cotovelo = self._cor_mais_escura(cor_pele, 20)
        tamanho_cotovelo = max(2, int(corpo_altura * 0.08))
        pygame.draw.circle(char_surf, cor_cotovelo, braco_sup_esq, tamanho_cotovelo)
        pygame.draw.circle(char_surf, cor_cotovelo, braco_sup_dir, tamanho_cotovelo)

        # Antebraços conectados aos cotovelos
        antebraco_esq = (braco_sup_esq[0], braco_sup_esq[1] + altura_antebraco)
        antebraco_dir = (braco_sup_dir[0], braco_sup_dir[1] + altura_antebraco)

        # Desenhar antebraços conectando cotovelos às mãos
        pygame.draw.rect(char_surf, cor_pele, (antebraco_esq[0] - largura_antebraco//2, braco_sup_esq[1], largura_antebraco, altura_antebraco), border_radius=2)
        pygame.draw.rect(char_surf, cor_pele, (antebraco_dir[0] - largura_antebraco//2, braco_sup_dir[1], largura_antebraco, altura_antebraco), border_radius=2)

        # Mãos conectadas aos antebraços
        mao_esq = (antebraco_esq[0], antebraco_esq[1])
        mao_dir = (antebraco_dir[0], antebraco_dir[1])
        pygame.draw.circle(char_surf, cor_pele, mao_esq, tamanho_mao)
        pygame.draw.circle(char_surf, cor_pele, mao_dir, tamanho_mao)
        return mao_esq, mao_dir

    def _desenhar_anatomia_pernas(self, char_surf: pygame.Surface, centro: Tuple[int, int],
                                 corpo_largura: int, corpo_pos_y: int, corpo_altura: int,
                                 offsets_animacao: dict, cor_roupa: Tuple[int, int, int]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Desenha anatomia completa das pernas - método auxiliar usando proporções relativas"""
        # Todos os tamanhos baseados em proporções do corpo_altura para garantir consistência

        # Quadris conectados ao torso - proporção relativa
        quadril_y = corpo_pos_y + int(corpo_altura * 0.65)  # 65% da altura do corpo
        quadril_esq_x = centro[0] - corpo_largura//4
        quadril_dir_x = centro[0] + corpo_largura//4

        # Coxas conectadas aos quadris
        coxa_esq_pos = (quadril_esq_x + int(offsets_animacao['offset_perna_esq'][0]), quadril_y)
        coxa_dir_pos = (quadril_dir_x + int(offsets_animacao['offset_perna_dir'][0]), quadril_y)

        # Tamanhos dos elementos baseados em proporções do corpo
        tamanho_quadril = max(2, int(corpo_altura * 0.08))  # 8% da altura do corpo
        espessura_conexao = max(2, int(corpo_altura * 0.1))  # 10% da altura do corpo
        largura_coxa = max(4, int(corpo_altura * 0.15))  # 15% da altura do corpo

        # Conexão quadril-coxa mais proeminente
        pygame.draw.circle(char_surf, cor_roupa, (quadril_esq_x, quadril_y), tamanho_quadril)
        pygame.draw.circle(char_surf, cor_roupa, (quadril_dir_x, quadril_y), tamanho_quadril)

        # Conexão visual entre torso e pernas
        pygame.draw.line(char_surf, cor_roupa,
                        (centro[0] - corpo_largura//3, corpo_pos_y + int(corpo_altura * 0.55)),
                        (quadril_esq_x, quadril_y), espessura_conexao)
        pygame.draw.line(char_surf, cor_roupa,
                        (centro[0] + corpo_largura//3, corpo_pos_y + int(corpo_altura * 0.55)),
                        (quadril_dir_x, quadril_y), espessura_conexao)

        # Coxas - altura proporcional (25% da altura do corpo)
        coxa_altura = max(6, int(corpo_altura * 0.25))
        pygame.draw.rect(char_surf, cor_roupa, (coxa_esq_pos[0] - largura_coxa//2, coxa_esq_pos[1], largura_coxa, coxa_altura), border_radius=2)
        pygame.draw.rect(char_surf, cor_roupa, (coxa_dir_pos[0] - largura_coxa//2, coxa_dir_pos[1], largura_coxa, coxa_altura), border_radius=2)

        # Joelhos
        joelho_esq = (coxa_esq_pos[0], coxa_esq_pos[1] + coxa_altura)
        joelho_dir = (coxa_dir_pos[0], coxa_dir_pos[1] + coxa_altura)
        cor_joelho = self._cor_mais_escura(cor_roupa, 15)
        tamanho_joelho = max(2, int(corpo_altura * 0.06))  # 6% da altura do corpo
        pygame.draw.circle(char_surf, cor_joelho, joelho_esq, tamanho_joelho)
        pygame.draw.circle(char_surf, cor_joelho, joelho_dir, tamanho_joelho)

        # Pernas (canelas) - altura calculada para que os pés toquem a sombra
        # Calcular altura da superfície para posicionar os pés corretamente
        superficie_altura = char_surf.get_height()
        altura_disponivel_para_pernas = superficie_altura - joelho_esq[1] - 15  # 15 pixels para os pés
        perna_altura = max(4, min(int(corpo_altura * 0.2), altura_disponivel_para_pernas))
        largura_perna = max(3, int(corpo_altura * 0.12))  # 12% da altura do corpo
        pygame.draw.rect(char_surf, cor_roupa, (joelho_esq[0] - largura_perna//2, joelho_esq[1], largura_perna, perna_altura), border_radius=2)
        pygame.draw.rect(char_surf, cor_roupa, (joelho_dir[0] - largura_perna//2, joelho_dir[1], largura_perna, perna_altura), border_radius=2)        # Posições dos pés - mais próximos da base da superfície
        pe_esq = (joelho_esq[0], joelho_esq[1] + perna_altura + 5)
        pe_dir = (joelho_dir[0], joelho_dir[1] + perna_altura + 5)

        return pe_esq, pe_dir


# Criar instância global do renderer
renderer_3d = Renderer3D()

def _criar_metodos_personagens(renderer_instance):
    """Anexa dinamicamente todos os métodos desenhar_*_3d da classe Renderer3D à instância global."""
    nomes = [
        'desenhar_shelly_3d',
        'desenhar_nita_3d',
        'desenhar_colt_3d',
        'desenhar_bull_3d',
        'desenhar_barley_3d',
        'desenhar_poco_3d',
    ]
    for nome in nomes:
        metodo = getattr(Renderer3D, nome, None)
        if metodo is not None:
            setattr(renderer_instance, nome, types.MethodType(metodo, renderer_instance))

# Anexar métodos dinamicamente
_criar_metodos_personagens(renderer_3d)
