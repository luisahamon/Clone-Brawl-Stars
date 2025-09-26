"""
Sistema avançado de renderização de sprites do Brawl Stars Clone.

Este módulo implementa a criação de sprites detalhados e efeitos visuais
avançados, incluindo gradientes, sombras, texturas e sprites específicos
para personagens, inimigos e elementos do jogo com alta qualidade visual.
"""

import math
import random
import pygame
from src.pygame_constants import SRCALPHA

class SpriteRenderer:
    """Sistema de renderização de sprites avançado com gráficos detalhados"""

    @staticmethod
    def criar_gradiente(superficie, cor1, cor2, direcao='vertical'):
        """Cria um gradiente entre duas cores"""
        w, h = superficie.get_size()
        if direcao == 'vertical':
            for y in range(h):
                ratio = y / h
                r = int(cor1[0] * (1 - ratio) + cor2[0] * ratio)
                g = int(cor1[1] * (1 - ratio) + cor2[1] * ratio)
                b = int(cor1[2] * (1 - ratio) + cor2[2] * ratio)
                pygame.draw.line(superficie, (r, g, b), (0, y), (w, y))
        else:  # horizontal
            for x in range(w):
                ratio = x / w
                r = int(cor1[0] * (1 - ratio) + cor2[0] * ratio)
                g = int(cor1[1] * (1 - ratio) + cor2[1] * ratio)
                b = int(cor1[2] * (1 - ratio) + cor2[2] * ratio)
                pygame.draw.line(superficie, (r, g, b), (x, 0), (x, h))

    @staticmethod
    def criar_sombra(superficie, offset=2):
        """Cria um efeito de sombra para o sprite"""
        w, h = superficie.get_size()
        sombra = pygame.Surface((w + offset, h + offset), SRCALPHA)

        # Criar sombra escura
        for x in range(w):
            for y in range(h):
                pixel = superficie.get_at((x, y))
                if pixel.a > 0:  # Se o pixel não é transparente
                    sombra.set_at((x + offset, y + offset), (0, 0, 0, 100))
          # Blit o sprite original por cima
        sombra.blit(superficie, (0, 0))
        return sombra

    @staticmethod
    def criar_sprite_personagem(nome, cor_principal, cor_secundaria, tamanho=40):
        """Cria sprite de personagem com design detalhado e realista"""
        sprite = pygame.Surface((tamanho, tamanho), SRCALPHA)
        centro = tamanho // 2

        if nome == "Shelly":
            # === SHELLY - Cowgirl com Shotgun ===

            # Chapéu cowboy
            chapeu_cor = (101, 67, 33)
            pygame.draw.ellipse(sprite, chapeu_cor, (centro-16, centro-20, 32, 12))  # Aba
            pygame.draw.ellipse(sprite, (139, 90, 43), (centro-12, centro-22, 24, 16))  # Copa
            pygame.draw.ellipse(sprite, (160, 110, 60), (centro-12, centro-24, 24, 8))  # Topo

            # Rosto
            rosto_cor = (255, 220, 177)  # Tom de pele
            pygame.draw.circle(sprite, rosto_cor, (centro, centro-2), 12)

            # Cabelo loiro (saindo do chapéu)
            cabelo_cor = (255, 215, 0)
            pygame.draw.arc(sprite, cabelo_cor, (centro-14, centro-8, 28, 16), 0, math.pi, 4)

            # Olhos detalhados
            olho_esq = (centro - 5, centro - 5)
            olho_dir = (centro + 5, centro - 5)
            # Brancos dos olhos
            pygame.draw.ellipse(sprite, (255, 255, 255), (olho_esq[0]-2, olho_esq[1]-1, 4, 3))
            pygame.draw.ellipse(sprite, (255, 255, 255), (olho_dir[0]-2, olho_dir[1]-1, 4, 3))
            # Íris azuis
            pygame.draw.circle(sprite, (70, 130, 180), olho_esq, 1)
            pygame.draw.circle(sprite, (70, 130, 180), olho_dir, 1)

            # Nariz e boca
            pygame.draw.circle(sprite, (255, 200, 160), (centro, centro), 1)
            pygame.draw.arc(sprite, (200, 100, 100), (centro-3, centro+2, 6, 4), 0, math.pi, 2)

            # Corpo/Roupa
            # Colete cowboy
            colete_cor = cor_principal
            pygame.draw.ellipse(sprite, colete_cor, (centro-10, centro+8, 20, 24))
            pygame.draw.ellipse(sprite, cor_secundaria, (centro-10, centro+8, 20, 24), 2)

            # Detalhes do colete
            for i in range(3):
                y = centro + 12 + i * 4
                pygame.draw.circle(sprite, (255, 215, 0), (centro, y), 1)  # Botões dourados

            # Braços
            pygame.draw.circle(sprite, rosto_cor, (centro-12, centro+12), 4)  # Braço esquerdo
            pygame.draw.circle(sprite, rosto_cor, (centro+12, centro+12), 4)  # Braço direito

            # Shotgun (arma característica)
            arma_cor = (64, 64, 64)
            pygame.draw.rect(sprite, arma_cor, (centro+14, centro+8, 8, 3))  # Cano
            pygame.draw.rect(sprite, (101, 67, 33), (centro+10, centro+6, 6, 6))  # Cabo

        elif nome == "Nita":
            # === NITA - Xamã Tribal ===

            # Cabelo escuro com tranças
            cabelo_cor = (101, 67, 33)
            pygame.draw.circle(sprite, cabelo_cor, (centro, centro-6), 14)

            # Tranças laterais
            pygame.draw.ellipse(sprite, cabelo_cor, (centro-18, centro-2, 8, 16))
            pygame.draw.ellipse(sprite, cabelo_cor, (centro+10, centro-2, 8, 16))

            # Rosto
            rosto_cor = (210, 180, 140)  # Tom mais moreno
            pygame.draw.circle(sprite, rosto_cor, (centro, centro-2), 10)

            # Pintura tribal no rosto
            pygame.draw.line(sprite, (255, 0, 0), (centro-8, centro-6), (centro-4, centro-2), 2)
            pygame.draw.line(sprite, (255, 0, 0), (centro+4, centro-2), (centro+8, centro-6), 2)

            # Olhos amendoados
            olho_esq = (centro - 4, centro - 4)
            olho_dir = (centro + 4, centro - 4)
            pygame.draw.ellipse(sprite, (255, 255, 255), (olho_esq[0]-2, olho_esq[1]-1, 4, 2))
            pygame.draw.ellipse(sprite, (255, 255, 255), (olho_dir[0]-2, olho_dir[1]-1, 4, 2))
            pygame.draw.circle(sprite, (139, 69, 19), olho_esq, 1)
            pygame.draw.circle(sprite, (139, 69, 19), olho_dir, 1)

            # Roupa tribal
            roupa_cor = cor_principal
            pygame.draw.ellipse(sprite, roupa_cor, (centro-12, centro+6, 24, 26))

            # Padrões tribais na roupa
            for i in range(3):
                y = centro + 10 + i * 4
                pygame.draw.line(sprite, cor_secundaria, (centro-8, y), (centro+8, y), 2)
                pygame.draw.circle(sprite, (255, 215, 0), (centro-6+i*6, y), 1)

            # Colar de ossos
            for i in range(5):
                x = centro - 8 + i * 4
                pygame.draw.circle(sprite, (255, 255, 255), (x, centro+4), 2)
                pygame.draw.circle(sprite, (200, 200, 200), (x, centro+4), 2, 1)

            # Bastão xamânico
            pygame.draw.line(sprite, (139, 69, 19), (centro-16, centro+16),
            (centro-16, centro+4), 3)
            pygame.draw.circle(sprite, (255, 0, 255), (centro-16, centro+4), 3)  # Cristal mágico

        elif nome == "Colt":
            # === COLT - Pistoleiro Estiloso ===

            # Cabelo gel penteado
            cabelo_cor = (255, 215, 0)
            pygame.draw.ellipse(sprite, cabelo_cor, (centro-12, centro-18, 24, 16))
            # Brilho do gel
            pygame.draw.ellipse(sprite, (255, 255, 150), (centro-8, centro-16, 16, 8))

            # Rosto
            rosto_cor = (255, 220, 177)
            pygame.draw.circle(sprite, rosto_cor, (centro, centro-2), 10)

            # Óculos escuros estilosos
            oculos_cor = (25, 25, 25)
            pygame.draw.ellipse(sprite, oculos_cor, (centro-8, centro-8, 6, 6))  # Lente esquerda
            pygame.draw.ellipse(sprite, oculos_cor, (centro+2, centro-8, 6, 6))   # Lente direita
            pygame.draw.line(sprite, oculos_cor, (centro-2, centro-5),
            (centro+2, centro-5), 2)  # Ponte

            # Reflexo nas lentes
            pygame.draw.circle(sprite, (100, 100, 255), (centro-6, centro-6), 1)
            pygame.draw.circle(sprite, (100, 100, 255), (centro+4, centro-6), 1)

            # Sorriso confiante
            pygame.draw.arc(sprite, (200, 100, 100), (centro-4, centro, 8, 6), 0, math.pi, 2)

            # Jaqueta de couro
            jaqueta_cor = cor_principal
            pygame.draw.ellipse(sprite, jaqueta_cor, (centro-12, centro+6, 24, 26))

            # Detalhes da jaqueta (zíper, bolsos)
            pygame.draw.line(sprite, (192, 192, 192), (centro, centro+8),
            (centro, centro+28), 2)  # Zíper
            pygame.draw.rect(sprite, cor_secundaria, (centro-8, centro+20, 6, 4))  # Bolso esquerdo
            pygame.draw.rect(sprite, cor_secundaria, (centro+2, centro+20, 6, 4))   # Bolso direito

            # Pistolas duplas
            pistola_cor = (64, 64, 64)
            # Pistola esquerda
            pygame.draw.rect(sprite, pistola_cor, (centro-18, centro+14, 6, 3))
            pygame.draw.rect(sprite, (139, 69, 19), (centro-20, centro+12, 4, 4))  # Cabo
            # Pistola direita
            pygame.draw.rect(sprite, pistola_cor, (centro+12, centro+14, 6, 3))
            pygame.draw.rect(sprite, (139, 69, 19), (centro+16, centro+12, 4, 4))  # Cabo

        elif nome == "Bull":
            # === BULL - Motoqueiro Pesado ===

            # Capacete de motoqueiro
            capacete_cor = (25, 25, 25)
            pygame.draw.ellipse(sprite, capacete_cor, (centro-14, centro-20, 28, 20))

            # Visor do capacete
            pygame.draw.ellipse(sprite, (50, 50, 100), (centro-10, centro-16, 20, 8))
            pygame.draw.ellipse(sprite, (100, 100, 200), (centro-10, centro-16, 20, 8), 2)

            # Rosto robusto (parcialmente visível)
            rosto_cor = (210, 180, 140)
            pygame.draw.ellipse(sprite, rosto_cor, (centro-8, centro-4, 16, 12))

            # Bigode característico
            pygame.draw.ellipse(sprite, (101, 67, 33), (centro-6, centro+2, 12, 4))

            # Jaqueta de couro pesada
            jaqueta_cor = cor_principal
            pygame.draw.ellipse(sprite, jaqueta_cor, (centro-14, centro+6, 28, 26))

            # Tachas na jaqueta
            for x in range(centro-10, centro+11, 5):
                for y in range(centro+10, centro+25, 5):
                    pygame.draw.circle(sprite, (192, 192, 192), (x, y), 1)
                    pygame.draw.circle(sprite, (255, 255, 255), (x, y), 1, 1)

            # Shotgun pesada
            shotgun_cor = (64, 64, 64)
            pygame.draw.rect(sprite, shotgun_cor, (centro+16, centro+10, 10, 4))  # Cano duplo
            pygame.draw.line(sprite, shotgun_cor, (centro+16, centro+11), (centro+26, centro+11), 2)
            pygame.draw.line(sprite, shotgun_cor, (centro+16, centro+13), (centro+26, centro+13), 2)
            pygame.draw.rect(sprite, (139, 69, 19), (centro+12, centro+8, 6, 8))  # Cabo

        elif nome == "Barley":
            # === BARLEY - Robô Bartender ===

            # Cabeça robótica
            cabeca_cor = (192, 192, 192)
            pygame.draw.ellipse(sprite, cabeca_cor, (centro-12, centro-16, 24, 20))
            pygame.draw.ellipse(sprite, (220, 220, 220), (centro-12, centro-16, 24, 20), 2)

            # Antenas
            pygame.draw.line(sprite, (64, 64, 64), (centro-6, centro-16), (centro-8, centro-22), 2)
            pygame.draw.line(sprite, (64, 64, 64), (centro+6, centro-16), (centro+8, centro-22), 2)
            pygame.draw.circle(sprite, (255, 0, 0), (centro-8, centro-22), 2)  # LED vermelho
            pygame.draw.circle(sprite, (0, 255, 0), (centro+8, centro-22), 2)  # LED verde

            # Olhos robóticos (LEDs)
            pygame.draw.circle(sprite, (0, 255, 255), (centro-5, centro-8), 3)
            pygame.draw.circle(sprite, (0, 255, 255), (centro+5, centro-8), 3)
            pygame.draw.circle(sprite, (255, 255, 255), (centro-5, centro-8), 3, 1)
            pygame.draw.circle(sprite, (255, 255, 255), (centro+5, centro-8), 3, 1)

            # Corpo robótico
            corpo_cor = cor_principal
            pygame.draw.rect(sprite, corpo_cor, (centro-10, centro+4, 20, 24))
            pygame.draw.rect(sprite, cor_secundaria, (centro-10, centro+4, 20, 24), 2)

            # Painel de controle no peito
            pygame.draw.rect(sprite, (64, 64, 64), (centro-6, centro+8, 12, 8))
            for i in range(3):
                cor_led = [(255, 0, 0), (255, 255, 0), (0, 255, 0)][i]
                pygame.draw.circle(sprite, cor_led, (centro-4+i*4, centro+10), 1)
                pygame.draw.circle(sprite, cor_led, (centro-4+i*4, centro+14), 1)

            # Braços mecânicos
            braco_cor = (160, 160, 160)
            pygame.draw.rect(sprite, braco_cor, (centro-16, centro+8, 6, 12))  # Braço esquerdo
            pygame.draw.rect(sprite, braco_cor, (centro+10, centro+8, 6, 12))  # Braço direito

            # Garrafas de coquetel molotov
            pygame.draw.ellipse(sprite, (0, 128, 0), (centro-18, centro+6, 4, 8))  #Garrafa esquerda
            pygame.draw.ellipse(sprite, (0, 128, 0), (centro+14, centro+6, 4, 8))  #Garrafa direita
            # Líquido dentro
            pygame.draw.ellipse(sprite, (255, 165, 0), (centro-17, centro+8, 2, 4))
            pygame.draw.ellipse(sprite, (255, 165, 0), (centro+15, centro+8, 2, 4))

        elif nome == "Poco":
            # === POCO - Esqueleto Músico ===

            # Sombrero mexicano
            sombrero_cor = (160, 82, 45)
            pygame.draw.ellipse(sprite, sombrero_cor, (centro-18, centro-22, 36, 12))  # Aba larga
            pygame.draw.ellipse(sprite, (139, 69, 19), (centro-10, centro-24, 20, 16))  # Copa

            # Decoração do sombrero
            for i in range(5):
                x = centro - 8 + i * 4
                pygame.draw.circle(sprite, (255, 215, 0), (x, centro-18), 1)

            # Cabeça de esqueleto
            caveira_cor = (255, 255, 240)
            pygame.draw.circle(sprite, caveira_cor, (centro, centro-4), 10)

            # Órbitas dos olhos
            pygame.draw.circle(sprite, (0, 0, 0), (centro-4, centro-8), 3)
            pygame.draw.circle(sprite, (0, 0, 0), (centro+4, centro-8), 3)
            # Chama nos olhos
            pygame.draw.circle(sprite, (255, 0, 255), (centro-4, centro-8), 2)
            pygame.draw.circle(sprite, (255, 0, 255), (centro+4, centro-8), 2)

            # Nariz de esqueleto
            pygame.draw.polygon(sprite, (0, 0, 0), [(centro, centro-2), (centro-2, centro+2), (centro+2, centro+2)])

            # Sorriso de esqueleto
            pygame.draw.arc(sprite, (0, 0, 0), (centro-6, centro-2, 12, 8), 0, math.pi, 3)
            # Dentes
            for i in range(6):
                x = centro - 5 + i * 2
                pygame.draw.line(sprite, (255, 255, 240), (x, centro+2), (x, centro+4), 1)

            # Corpo esquelético
            corpo_cor = cor_principal
            pygame.draw.ellipse(sprite, corpo_cor, (centro-10, centro+6, 20, 24))

            # Costelas visíveis
            for i in range(4):
                y = centro + 10 + i * 3
                pygame.draw.arc(sprite, (255, 255, 240), (centro-8, y-2, 16, 4), 0, math.pi, 2)

            # Guitarra
            guitarra_cor = (139, 69, 19)
            # Corpo da guitarra
            pygame.draw.ellipse(sprite, guitarra_cor, (centro+12, centro+8, 8, 16)) # Braço da guitarra
            pygame.draw.rect(sprite, guitarra_cor, (centro+16, centro+4, 3, 12))
            # Cordas
            for i in range(3):
                x = centro + 17 + i
                pygame.draw.line(sprite, (192, 192, 192), (x, centro+6), (x, centro+18), 1)

        else:
            # Fallback para personagens não implementados
            pygame.draw.circle(sprite, cor_principal, (centro, centro), centro - 2)
            pygame.draw.circle(sprite, cor_secundaria, (centro, centro), centro - 2, 3)

        # Adicionar sombra e retornar
        return SpriteRenderer.criar_sombra(sprite)

    @staticmethod
    def criar_sprite_tiro(tipo, cor, tamanho=8):
        """Cria diferentes tipos de projéteis com efeitos visuais avançados"""
        sprite = pygame.Surface((tamanho * 2, tamanho * 2), SRCALPHA)
        centro = tamanho

        if tipo == "normal":
            # Projétil esférico com gradiente e brilho
            for raio in range(centro, 0, -1):
                alpha = int(255 * (raio / centro))
                cor_gradiente = (
                    min(255, cor[0] + (255 - cor[0]) * (1 - raio/centro)),
                    min(255, cor[1] + (255 - cor[1]) * (1 - raio/centro)),
                    min(255, cor[2] + (255 - cor[2]) * (1 - raio/centro))
                )
                pygame.draw.circle(sprite, cor_gradiente, (centro, centro), raio)

            # Brilho central
            pygame.draw.circle(sprite, (255, 255, 255), (centro - 2, centro - 2), 2)

            # Rastro de energia
            for i in range(3):
                alpha = 150 - i * 50
                rastro_cor = (*cor, alpha)
                rastro_surf = pygame.Surface((tamanho//2, tamanho//2), SRCALPHA)
                pygame.draw.circle(rastro_surf, rastro_cor, (tamanho//4, tamanho//4), tamanho//4 - i)
                sprite.blit(rastro_surf, (centro + 6 + i*2, centro - tamanho//4))

        elif tipo == "shotgun":
            # Múltiplos fragmentos de projétil
            cores_fragmento = [
                (cor[0] + 30, cor[1], cor[2]),
                cor,
                (cor[0], cor[1] + 30, cor[2])
            ]

            for i in range(3):
                x = centro + (i - 1) * 4
                cor_frag = cores_fragmento[i]

                # Fragmento principal
                pygame.draw.circle(sprite, cor_frag, (x, centro), 3)
                pygame.draw.circle(sprite, (255, 255, 255), (x, centro), 1)

                # Faíscas ao redor
                for j in range(4):
                    angulo = j * 90
                    fx = x + 5 * math.cos(math.radians(angulo))
                    fy = centro + 5 * math.sin(math.radians(angulo))
                    pygame.draw.circle(sprite, (255, 255, 100), (int(fx), int(fy)), 1)

        elif tipo == "sniper":
            # Projétil alongado tipo bala
            comprimento = tamanho * 2

            # Corpo da bala
            pygame.draw.ellipse(sprite, cor, (centro - comprimento//2, centro - 2, comprimento, 4))

            # Ponta da bala
            pygame.draw.polygon(sprite, (255, 255, 255), [
                (centro + comprimento//2, centro),
                (centro + comprimento//2 - 4, centro - 2),
                (centro + comprimento//2 - 4, centro + 2)
            ])

            # Rastro de velocidade
            for i in range(5):
                x = centro - comprimento//2 - i * 3
                alpha = 200 - i * 40
                rastro_cor = (*cor, alpha)
                rastro_surf = pygame.Surface((6, 2), SRCALPHA)
                rastro_surf.fill(rastro_cor)
                sprite.blit(rastro_surf, (x, centro - 1))

        elif tipo == "arco":  # Para Barley
            # Projétil em arco (garrafa)
            garrafa_cor = (0, 128, 0)
            pygame.draw.ellipse(sprite, garrafa_cor, (centro - 3, centro - 4, 6, 8))
            pygame.draw.ellipse(sprite, (255, 165, 0), (centro - 2, centro - 2, 4, 4))  # Líquido

            # Pavio aceso
            pygame.draw.line(sprite, (255, 100, 0), (centro, centro - 4), (centro + 2, centro - 6), 2)
            pygame.draw.circle(sprite, (255, 255, 0), (centro + 2, centro - 6), 1)  # Chama

            # Faíscas
            for i in range(3):
                angulo = random.randint(0, 360)
                fx = centro + 8 * math.cos(math.radians(angulo))
                fy = centro + 8 * math.sin(math.radians(angulo))
                pygame.draw.circle(sprite, (255, 200, 0), (int(fx), int(fy)), 1)

        elif tipo == "ondas":  # Para Poco
            # Ondas sonoras
            for i in range(3):
                raio = 6 + i * 3
                alpha = 200 - i * 60
                onda_cor = (*cor, alpha)
                onda_surf = pygame.Surface((raio * 2, raio * 2), SRCALPHA)
                pygame.draw.circle(onda_surf, onda_cor, (raio, raio), raio, 2)
                sprite.blit(onda_surf, (centro - raio, centro - raio))
              # Notas musicais
            nota_cor = (255, 255, 255)
            pygame.draw.circle(sprite, nota_cor, (centro, centro - 6), 2)
            pygame.draw.line(sprite, nota_cor, (centro + 2, centro - 6), (centro + 2, centro - 2), 2)

        else:
            # Fallback para tipos não implementados
            pygame.draw.circle(sprite, cor, (centro, centro), centro // 2)
            pygame.draw.circle(sprite, (255, 255, 255), (centro, centro), centro // 4)

        return sprite

    @staticmethod
    def criar_sprite_obstaculo(tipo, tamanho=60):
        """Cria diferentes tipos de obstáculos"""
        sprite = pygame.Surface((tamanho, tamanho), SRCALPHA)

        if tipo == "caixa":
            # Caixa com detalhes
            pygame.draw.rect(sprite, (139, 69, 19), (0, 0, tamanho, tamanho))
            pygame.draw.rect(sprite, (160, 82, 45), (0, 0, tamanho, tamanho), 4)

            # Pregos
            for x in [10, tamanho-10]:
                for y in [10, tamanho-10]:
                    pygame.draw.circle(sprite, (105, 105, 105), (x, y), 3)

        elif tipo == "pedra":
            # Pedra irregular
            pontos = []
            for angulo in range(0, 360, 45):
                raio = tamanho // 2 + (tamanho // 6) * math.sin(angulo * 0.1)
                x = tamanho // 2 + raio * math.cos(math.radians(angulo))
                y = tamanho // 2 + raio * math.sin(math.radians(angulo))
                pontos.append((x, y))

            pygame.draw.polygon(sprite, (128, 128, 128), pontos)
            pygame.draw.polygon(sprite, (169, 169, 169), pontos, 3)

        elif tipo == "arbusto":
            # Arbusto verde
            pygame.draw.circle(sprite, (34, 139, 34), (tamanho//2, tamanho//2), tamanho//2)            # Detalhes das folhas
            for i in range(8):
                angulo = i * 45
                x = tamanho//2 + (tamanho//3) * math.cos(math.radians(angulo))
                y = tamanho//2 + (tamanho//3) * math.sin(math.radians(angulo))
                pygame.draw.circle(sprite, (0, 100, 0), (int(x), int(y)), tamanho//8)
        return sprite

    @staticmethod
    def criar_sprite_power_up(tipo, tamanho=24):
        """Cria power-ups com visual melhorado"""
        sprite = pygame.Surface((tamanho, tamanho), SRCALPHA)
        centro = tamanho // 2

        # Base do power-up (estrela)
        pontos_estrela = []
        for i in range(10):
            angulo = i * 36
            if i % 2 == 0:
                raio = centro - 2
            else:
                raio = centro // 2
            x = centro + raio * math.cos(math.radians(angulo - 90))
            y = centro + raio * math.sin(math.radians(angulo - 90))
            pontos_estrela.append((x, y))

        if tipo == 'velocidade':
            cor = (0, 255, 255)
            pygame.draw.polygon(sprite, cor, pontos_estrela)
            pygame.draw.polygon(sprite, (255, 255, 255), pontos_estrela, 2)
            # Símbolo de velocidade
            pygame.draw.lines(sprite, (255, 255, 255), False,
                            [(centro-6, centro), (centro+2, centro-4), (centro+2, centro+4)], 3)

        elif tipo == 'vida':
            cor = (0, 255, 0)
            pygame.draw.polygon(sprite, cor, pontos_estrela)
            pygame.draw.polygon(sprite, (255, 255, 255), pontos_estrela, 2)
            # Cruz vermelha
            pygame.draw.line(sprite, (255, 255, 255), (centro, centro-6), (centro, centro+6), 3)
            pygame.draw.line(sprite, (255, 255, 255), (centro-6, centro), (centro+6, centro), 3)

        elif tipo == 'tiro_rapido':
            cor = (255, 165, 0)
            pygame.draw.polygon(sprite, cor, pontos_estrela)
            pygame.draw.polygon(sprite, (255, 255, 255), pontos_estrela, 2)
            # Múltiplas setas
            for i in range(3):
                x_offset = (i - 1) * 4
                pygame.draw.polygon(sprite, (255, 255, 255), [
                    (centro + x_offset - 3, centro + 2),
                    (centro + x_offset, centro - 2),
                    (centro + x_offset + 3, centro + 2)
                ])
        return sprite

    @staticmethod
    def criar_sprite_inimigo(tamanho=30):
        """Cria sprite de inimigo com design ameaçador"""
        sprite = pygame.Surface((tamanho, tamanho), SRCALPHA)
        centro = tamanho // 2

        # Corpo robótico/alienígena
        corpo_cor = (120, 20, 20)  # Vermelho escuro
        pygame.draw.ellipse(sprite, corpo_cor, (centro-12, centro-8, 24, 20))

        # Detalhes metálicos
        pygame.draw.ellipse(sprite, (200, 50, 50), (centro-12, centro-8, 24, 20), 2)
        pygame.draw.ellipse(sprite, (150, 30, 30), (centro-8, centro-4, 16, 12))

        # Olhos vermelhos brilhantes
        pygame.draw.circle(sprite, (255, 0, 0), (centro - 4, centro - 2), 3)
        pygame.draw.circle(sprite, (255, 0, 0), (centro + 4, centro - 2), 3)
        pygame.draw.circle(sprite, (255, 100, 100), (centro - 4, centro - 2), 2)
        pygame.draw.circle(sprite, (255, 100, 100), (centro + 4, centro - 2), 2)
        pygame.draw.circle(sprite, (255, 255, 255), (centro - 4, centro - 3), 1)
        pygame.draw.circle(sprite, (255, 255, 255), (centro + 4, centro - 3), 1)

        # Antenas/sensores
        pygame.draw.line(sprite, (64, 64, 64), (centro - 6, centro - 8), (centro - 8, centro - 14), 2)
        pygame.draw.line(sprite, (64, 64, 64), (centro + 6, centro - 8), (centro + 8, centro - 14), 2)
        pygame.draw.circle(sprite, (255, 0, 0), (centro - 8, centro - 14), 1)
        pygame.draw.circle(sprite, (255, 0, 0), (centro + 8, centro - 14), 1)

        # Arma integrada
        pygame.draw.rect(sprite, (64, 64, 64), (centro + 12, centro - 2, 8, 4))
        pygame.draw.circle(sprite, (100, 100, 100), (centro + 20, centro), 2)

        # Detalhes de armadura
        for i in range(3):
            y = centro - 4 + i * 3
            pygame.draw.line(sprite, (200, 200, 200), (centro - 6, y), (centro + 6, y), 1)

        return SpriteRenderer.criar_sombra(sprite)

    @staticmethod
    def rotacionar_sprite(sprite, angulo):
        """Rotaciona um sprite mantendo a qualidade"""
        if angulo == 0:
            return sprite

        # Rotacionar e manter centro
        rotacionado = pygame.transform.rotate(sprite, angulo)
        return rotacionado

    @staticmethod
    def criar_efeito_impacto(tamanho=20):
        """Cria efeito visual de impacto"""
        sprite = pygame.Surface((tamanho, tamanho), SRCALPHA)
        centro = tamanho // 2

        # Círculos concêntricos de impacto
        cores = [(255, 255, 0), (255, 165, 0), (255, 69, 0), (255, 0, 0)]
        for i, cor in enumerate(cores):
            raio = centro - i * 2
            if raio > 0:
                pygame.draw.circle(sprite, cor, (centro, centro), raio, 2)
        # Raios de energia
        for angulo in range(0, 360, 45):
            x = centro + (centro - 5) * math.cos(math.radians(angulo))
            y = centro + (centro - 5) * math.sin(math.radians(angulo))
            x2 = centro + centro * math.cos(math.radians(angulo))
            y2 = centro + centro * math.sin(math.radians(angulo))
            pygame.draw.line(sprite, (255, 255, 255), (int(x), int(y)), (int(x2), int(y2)), 2)
        return sprite

    @staticmethod
    def criar_efeito_powerup_collect(tamanho=30):
        """Cria efeito visual de coleta de power-up"""
        sprite = pygame.Surface((tamanho, tamanho), SRCALPHA)
        centro = tamanho // 2

        # Estrela brilhante
        pontos = []
        for i in range(10):
            angulo = i * 36
            if i % 2 == 0:
                raio = centro - 3
            else:
                raio = centro // 2
            x = centro + raio * math.cos(math.radians(angulo - 90))
            y = centro + raio * math.sin(math.radians(angulo - 90))
            pontos.append((x, y))

        pygame.draw.polygon(sprite, (255, 255, 255), pontos)
        pygame.draw.polygon(sprite, (255, 215, 0), pontos, 3)

        # Partículas ao redor
        for i in range(8):
            angulo = i * 45
            distancia = centro + 5
            x = centro + distancia * math.cos(math.radians(angulo))
            y = centro + distancia * math.sin(math.radians(angulo))
            pygame.draw.circle(sprite, (255, 255, 0), (int(x), int(y)), 2)

        return sprite

class AnimationManager:
    """Gerenciador de animações"""

    def __init__(self):
        self.animacoes = {}

    def criar_animacao_movimento(self, sprite_base, frames=4):
        """Cria animação de movimento"""
        animacoes = []
        for i in range(frames):
            frame = sprite_base.copy()            # Efeito de balanço sutil
            offset_y = int(2 * math.sin(i * math.pi / 2))
            temp_surface = pygame.Surface((frame.get_width(), frame.get_height() + 4), SRCALPHA)
            temp_surface.blit(frame, (0, offset_y + 2))
            animacoes.append(temp_surface)
        return animacoes

    def criar_animacao_ataque(self, sprite_base, frames=3):
        """Cria animação de ataque"""
        animacoes = []
        for i in range(frames):
            frame = sprite_base.copy()
            # Efeito de flash branco
            if i == 1:  # Frame do meio
                # Overlay branco
                overlay = pygame.Surface(frame.get_size(), SRCALPHA)
                overlay.fill((255, 255, 255, 100))
                frame.blit(overlay, (0, 0))
            animacoes.append(frame)
        return animacoes
