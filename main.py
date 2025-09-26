"""
Arquivo principal do Brawl Stars Clone.
Este módulo contém o ponto de entrada do jogo, inicializando o pygame,
configurando a tela principal e executando o loop principal do jogo.
Responsável por gerenciar estados e controlar o fluxo geral da aplicação.
"""

import sys
import pygame
from src.gerenciador_estados import GerenciadorEstados
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
# Importar constantes do pygame
from src.pygame_constants import QUIT, KEYDOWN, K_F12, SRCALPHA


def main():
    """Função principal do jogo"""
    pygame.init()  # pylint: disable=no-member

    # Configurar tela
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # Sistema de FPS simples e confiável
    font_fps = pygame.font.Font(None, 24)
    show_fps = True
    fps_timer = 0
    fps_display_interval = 0.2

    # Inicializar gerenciador de estados
    gerenciador = GerenciadorEstados(screen)

    # Loop principal
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time em segundos
        fps_timer += dt
        
        # Eventos
        for event in pygame.event.get():
            if event.type == QUIT:  # Usar constante centralizada
                running = False
            elif event.type == KEYDOWN and event.key == K_F12:  # Usar constante centralizada
                show_fps = not show_fps
            else:
                # Passar evento para o gerenciador
                continuar = gerenciador.handle_event(event)
                if not continuar:
                    running = False

        # Atualizar
        gerenciador.update(dt)

        # Renderizar
        gerenciador.render()
        
        # Mostrar FPS simples
        if show_fps and fps_timer >= fps_display_interval:
            fps_atual = clock.get_fps()
            fps_color = (100, 255, 100) if fps_atual >= 45 else (255, 255, 0) if fps_atual >= 25 else (255, 100, 100)
            fps_text = font_fps.render(f"FPS: {fps_atual:.1f}", True, fps_color)
            # Fundo para o texto
            fps_bg = pygame.Surface((100, 30), SRCALPHA)  # Usar constante centralizada
            fps_bg.fill((0, 0, 0, 128))
            screen.blit(fps_bg, (SCREEN_WIDTH - 110, 10))
            screen.blit(fps_text, (SCREEN_WIDTH - 100, 15))
            fps_timer = 0
        pygame.display.flip()
    pygame.quit()  # Não há constante para pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
