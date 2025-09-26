"""
Sistema de gerenciamento de áudio do Brawl Stars Clone.
Este módulo implementa um gerenciador completo de áudio utilizando pygame.mixer,
incluindo reprodução de efeitos sonoros, música de fundo, controle de volume,
geração procedural de sons e processamento de áudio em tempo real.
"""

import os
from typing import Dict, Optional, List
import numpy as np
import pygame
from src.config import VOLUME_MASTER, VOLUME_SFX, VOLUME_MUSIC

class AudioManager:
    """Gerenciador de áudio do jogo"""

    def __init__(self):
        """Inicializar sistema de áudio"""
        # Inicializar mixer do pygame
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.init()

        # Dicionários para armazenar sons
        self.sound_effects: Dict[str, pygame.mixer.Sound] = {}
        self.music_tracks: Dict[str, str] = {}

        # Configurações de volume
        self.volume_master = VOLUME_MASTER
        self.volume_sfx = VOLUME_SFX
        self.volume_music = VOLUME_MUSIC

        # Estado da música
        self.current_music = None
        self.music_paused = False

        # Canais reservados para diferentes tipos de som
        self.channels = {
            'tiros': pygame.mixer.Channel(0),
            'impactos': pygame.mixer.Channel(1),
            'power_ups': pygame.mixer.Channel(2),
            'habilidades': pygame.mixer.Channel(3),
            'ui': pygame.mixer.Channel(4),
            'ambiente': pygame.mixer.Channel(5)
        }

        # Carregar sons
        self.carregar_sons()
        self.gerar_sons_procedurais()

    def carregar_sons(self):
        """Carregar arquivos de som se existirem"""
        pasta_audio = os.path.join("assets", "audio")

        # Tentar carregar sons de arquivo se a pasta existir
        if os.path.exists(pasta_audio):
            self._carregar_sons_arquivo(pasta_audio)
        else:
            print("Pasta de áudio não encontrada, usando sons procedurais")

    def _carregar_sons_arquivo(self, pasta_audio: str):
        """Carregar sons de arquivos"""
        # Estrutura esperada de pastas
        estrutura_sons = {
            'tiros': ['tiro_normal.wav', 'tiro_shotgun.wav', 'tiro_sniper.wav'],
            'impactos': ['impacto_inimigo.wav', 'impacto_obstaculo.wav', 'explosao.wav'],
            'power_ups': ['coleta_velocidade.wav', 'coleta_vida.wav', 'coleta_tiro_rapido.wav'],
            'habilidades': ['super_shell.wav', 'rajada_balas.wav', 'investida.wav'],
            'ui': ['botao_click.wav', 'selecao_personagem.wav', 'game_over.wav'],
            'musica': ['menu.ogg', 'gameplay.ogg', 'boss_fight.ogg']
        }

        for categoria, arquivos in estrutura_sons.items():
            pasta_categoria = os.path.join(pasta_audio, categoria)
            if os.path.exists(pasta_categoria):
                for arquivo in arquivos:
                    caminho_arquivo = os.path.join(pasta_categoria, arquivo)
                    if os.path.exists(caminho_arquivo):
                        try:
                            if categoria == 'musica':
                                nome_musica = arquivo.split('.', maxsplit=1)[0]
                                self.music_tracks[nome_musica] = caminho_arquivo
                            else:
                                nome_som = arquivo.split('.', maxsplit=1)[0]
                                som = pygame.mixer.Sound(caminho_arquivo)
                                self.sound_effects[nome_som] = som
                        except pygame.error as e:
                            print(f"Erro ao carregar {arquivo}: {e}")

    def gerar_sons_procedurais(self):
        """Gerar sons proceduralmente usando pygame"""
        # Focar em sons de batalha ao invés de música
        self._gerar_sons_batalha()
        self._gerar_sons_ui()
        self._gerar_sons_ambiente()

    def _gerar_sons_batalha(self):
        """Gerar sons de batalha proceduralmente"""
        try:
            sample_rate = 22050

            # Som de tiro básico
            self._criar_som_tiro_basico(sample_rate)

            # Som de impacto
            self._criar_som_impacto(sample_rate)

            # Som de explosão
            self._criar_som_explosao(sample_rate)

            # Sons de power-ups
            self._criar_sons_powerups(sample_rate)            # Sons de habilidades especiais
            self._criar_sons_habilidades(sample_rate)

        except (ValueError, TypeError, AttributeError, OSError) as e:
            print(f"Erro ao gerar sons de batalha: {e}")

    def _criar_som_tiro_basico(self, sample_rate):
        """Criar som de tiro básico"""
        duracao = 0.08
        t = np.linspace(0, duracao, int(sample_rate * duracao), False)

        # Ruído branco filtrado para simular tiro
        ruido = np.random.normal(0, 0.3, len(t))
        # Envelope exponencial decrescente
        envelope = np.exp(-t * 30)
        # Filtro passa-alta simulado
        freq_corte = 2000
        som_tiro = ruido * envelope * (1 + np.sin(2 * np.pi * freq_corte * t) * 0.2)
        som_tiro = np.clip(som_tiro * 0.6, -1, 1)
        som_tiro_stereo = np.array([som_tiro, som_tiro]).T
        som_tiro_int = (som_tiro_stereo * 32767).astype(np.int16)
        self.sound_effects['tiro_shelly'] = pygame.sndarray.make_sound(som_tiro_int)
        self.sound_effects['tiro_colt'] = pygame.sndarray.make_sound(som_tiro_int)
        self.sound_effects['tiro_bull'] = pygame.sndarray.make_sound(som_tiro_int)

    def _criar_som_impacto(self, sample_rate):
        """Criar som de impacto"""
        duracao = 0.15
        t = np.linspace(0, duracao, int(sample_rate * duracao), False)

        # Combinação de ruído e tom baixo
        ruido = np.random.normal(0, 0.4, len(t))
        tom_baixo = np.sin(2 * np.pi * 120 * t) * 0.5
        envelope = np.exp(-t * 15)
        som_impacto = (ruido + tom_baixo) * envelope
        som_impacto = np.clip(som_impacto * 0.7, -1, 1)
        som_impacto_stereo = np.array([som_impacto, som_impacto]).T
        som_impacto_int = (som_impacto_stereo * 32767).astype(np.int16)
        self.sound_effects['impacto_inimigo'] = pygame.sndarray.make_sound(som_impacto_int)
        self.sound_effects['impacto_jogador'] = pygame.sndarray.make_sound(som_impacto_int)

    def _criar_som_explosao(self, sample_rate):
        """Criar som de explosão"""
        duracao = 0.3
        t = np.linspace(0, duracao, int(sample_rate * duracao), False)

        # Explosão = ruído + tons baixos
        ruido = np.random.normal(0, 0.5, len(t))
        tom1 = np.sin(2 * np.pi * 80 * t) * 0.6
        tom2 = np.sin(2 * np.pi * 150 * t) * 0.4
        envelope = np.exp(-t * 8)
        som_explosao = (ruido + tom1 + tom2) * envelope
        som_explosao = np.clip(som_explosao * 0.8, -1, 1)
        som_explosao_stereo = np.array([som_explosao, som_explosao]).T
        som_explosao_int = (som_explosao_stereo * 32767).astype(np.int16)
        self.sound_effects['explosao'] = pygame.sndarray.make_sound(som_explosao_int)

    def _criar_sons_powerups(self, sample_rate):
        """Criar sons de power-ups"""
        # Power-up de velocidade
        duracao = 0.2
        t = np.linspace(0, duracao, int(sample_rate * duracao), False)
        freq = 800
        som_velocidade = 0.4 * np.sin(2 * np.pi * freq * t) * (1 + 0.5 * np.sin(2 * np.pi * 15 * t))
        som_velocidade = np.clip(som_velocidade, -1, 1)
        som_velocidade_stereo = np.array([som_velocidade, som_velocidade]).T
        som_velocidade_int = (som_velocidade_stereo * 32767).astype(np.int16)

        self.sound_effects['powerup_velocidade'] = pygame.sndarray.make_sound(som_velocidade_int)

        # Power-up de vida
        duracao = 0.25
        t = np.linspace(0, duracao, int(sample_rate * duracao), False)
        freq1, freq2 = 600, 900
        som_vida = 0.3 * (np.sin(2 * np.pi * freq1 * t) + np.sin(2 * np.pi * freq2 * t))

        som_vida = np.clip(som_vida, -1, 1)
        som_vida_stereo = np.array([som_vida, som_vida]).T
        som_vida_int = (som_vida_stereo * 32767).astype(np.int16)

        self.sound_effects['powerup_vida'] = pygame.sndarray.make_sound(som_vida_int)

    def _criar_sons_habilidades(self, sample_rate):
        """Criar sons de habilidades especiais"""
        # Super Shot
        duracao = 0.12
        t = np.linspace(0, duracao, int(sample_rate * duracao), False)

        # Som mais poderoso que o tiro normal
        ruido = np.random.normal(0, 0.4, len(t))
        tom_grave = np.sin(2 * np.pi * 150 * t) * 0.6
        envelope = np.exp(-t * 20)

        som_super = (ruido + tom_grave) * envelope
        som_super = np.clip(som_super * 0.8, -1, 1)
        som_super_stereo = np.array([som_super, som_super]).T
        som_super_int = (som_super_stereo * 32767).astype(np.int16)

        self.sound_effects['super_shelly'] = pygame.sndarray.make_sound(som_super_int)
        self.sound_effects['habilidade_shelly'] = pygame.sndarray.make_sound(som_super_int)

    def _gerar_sons_ambiente(self):
        """Gerar sons ambientes sutis ao invés de música"""
        try:
            sample_rate = 22050

            # Som ambiente sutil para menu
            self._criar_ambiente_menu(sample_rate)
              # Som ambiente para jogo
            self._criar_ambiente_jogo(sample_rate)

        except (ValueError, TypeError, AttributeError, OSError) as e:
            print(f"Erro ao gerar sons ambiente: {e}")

    def _criar_ambiente_menu(self, sample_rate):
        """Criar som ambiente sutil para menu"""
        duracao = 0.5
        t = np.linspace(0, duracao, int(sample_rate * duracao), False)

        # Tom muito suave e baixo
        freq = 200
        som_ambiente = 0.05 * np.sin(2 * np.pi * freq * t)

        som_ambiente = np.clip(som_ambiente, -1, 1)
        som_ambiente_stereo = np.array([som_ambiente, som_ambiente]).T
        som_ambiente_int = (som_ambiente_stereo * 32767).astype(np.int16)

        self.sound_effects['ambiente_menu'] = pygame.sndarray.make_sound(som_ambiente_int)

    def _criar_ambiente_jogo(self, sample_rate):
        """Criar som ambiente sutil para jogo"""
        duracao = 1.0
        t = np.linspace(0, duracao, int(sample_rate * duracao), False)

        # Som de vento suave
        ruido_suave = np.random.normal(0, 0.02, len(t))
        filtro = np.sin(2 * np.pi * 0.5 * t) * 0.01

        som_ambiente = ruido_suave + filtro
        som_ambiente = np.clip(som_ambiente, -1, 1)
        som_ambiente_stereo = np.array([som_ambiente, som_ambiente]).T
        som_ambiente_int = (som_ambiente_stereo * 32767).astype(np.int16)

        self.sound_effects['ambiente_jogo'] = pygame.sndarray.make_sound(som_ambiente_int)

    def tocar_som(self, nome_som: str, volume: float = 1.0, canal: Optional[str] = None):
        """Tocar um efeito sonoro"""
        if nome_som in self.sound_effects:
            try:
                som = self.sound_effects[nome_som]
                volume_final = volume * self.volume_sfx * self.volume_master
                volume_final = max(0.0, min(1.0, volume_final))  # Garantir range válido
                som.set_volume(volume_final)
                if canal and canal in self.channels:
                    # Se o canal já está tocando, parar antes de tocar novo som
                    if self.channels[canal].get_busy():
                        self.channels[canal].stop()
                    self.channels[canal].play(som)
                else:
                    som.play()
            except (OSError, AttributeError, RuntimeError) as e:
                print(f"Erro ao tocar som '{nome_som}': {e}")
        else:
            pass

    def tocar_musica(self, nome_musica: str, loop: bool = True, fade_in: float = 0.0):
        """Tocar música de fundo"""
        if nome_musica in self.music_tracks:
            try:
                if self.current_music != nome_musica:
                    # Parar música atual se houver
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.stop()

                    pygame.mixer.music.load(self.music_tracks[nome_musica])
                    volume_final = self.volume_music * self.volume_master
                    volume_final = max(0.0, min(1.0, volume_final))  # Garantir range válido

                    pygame.mixer.music.set_volume(volume_final)
                    loops = -1 if loop else 0

                    if fade_in > 0:
                        fade_ms = int(fade_in * 1000)  # Converter segundos para milissegundos
                        pygame.mixer.music.play(loops, fade_ms=fade_ms)
                    else:
                        pygame.mixer.music.play(loops)

                    self.current_music = nome_musica
                    self.music_paused = False
            except (OSError, FileNotFoundError, RuntimeError) as e:
                print(f"Erro ao tocar música '{nome_musica}': {e}")
                self.current_music = None

    def pausar_musica(self):
        """Pausar música de fundo"""
        if not self.music_paused:
            pygame.mixer.music.pause()
            self.music_paused = True

    def retomar_musica(self):
        """Retomar música de fundo"""
        if self.music_paused:
            pygame.mixer.music.unpause()
            self.music_paused = False

    def parar_musica(self, fade_out: float = 0):
        """Parar música de fundo"""
        if fade_out > 0:
            pygame.mixer.music.fadeout(int(fade_out * 1000))  # Converter para milissegundos
        else:
            pygame.mixer.music.stop()
        self.current_music = None
        self.music_paused = False

    def parar_todos_sons(self):
        """Parar todos os sons em execução"""
        try:
            # Parar todos os canais
            for canal in self.channels.values():
                if canal.get_busy():
                    canal.stop()

            # Parar qualquer som que esteja tocando nos canais padrão
            pygame.mixer.stop()
        except (AttributeError, RuntimeError) as e:
            print(f"Erro ao parar sons: {e}")

    def limpar_estado_audio(self):
        """Limpar completamente o estado do áudio"""
        try:
            # Parar tudo
            self.parar_todos_sons()
            # Parar música
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()

          # Resetar estado
            self.current_music = None
            self.music_paused = False
            print("Estado de áudio limpo com sucesso")
        except (AttributeError, RuntimeError) as e:
            print(f"Erro ao limpar estado de áudio: {e}")

    def verificar_canais_ocupados(self):
        """Verificar quantos canais estão ocupados"""
        canais_ocupados = 0
        for canal in self.channels.values():
            if canal.get_busy():
                canais_ocupados += 1
        return canais_ocupados

    def tocar_som_controlado(self, nome_som: str, volume: float = 1.0, canal: Optional[str] = None):
        """Tocar som com controle de volume baseado no número de canais ocupados"""
        canais_ocupados = self.verificar_canais_ocupados()

        # Reduzir volume se muitos sons estão tocando
        if canais_ocupados > 2:
            volume *= 0.6  # Reduzir para 60% se muitos sons
        elif canais_ocupados > 4:
            volume *= 0.4  # Reduzir para 40% se muitos sons

        self.tocar_som(nome_som, volume, canal)

    def definir_volume_master(self, volume: float):
        """Definir volume master (0.0 a 1.0)"""
        self.volume_master = max(0.0, min(1.0, volume))
        # Atualizar volume da música atual
        if self.current_music:
            volume_final = self.volume_music * self.volume_master
            pygame.mixer.music.set_volume(volume_final)

    def definir_volume_sfx(self, volume: float):
        """Definir volume dos efeitos sonoros (0.0 a 1.0)"""
        self.volume_sfx = max(0.0, min(1.0, volume))

    def definir_volume_musica(self, volume: float):
        """Definir volume da música (0.0 a 1.0)"""
        self.volume_music = max(0.0, min(1.0, volume))
        if self.current_music:
            volume_final = self.volume_music * self.volume_master
            pygame.mixer.music.set_volume(volume_final)

    def obter_volumes(self) -> Dict[str, float]:
        """Obter configurações atuais de volume"""
        return {
            'master': self.volume_master,
            'sfx': self.volume_sfx,
            'music': self.volume_music
        }

    def som_disponivel(self, nome_som: str) -> bool:
        """Verificar se um som está disponível"""
        return nome_som in self.sound_effects

    def musica_disponivel(self, nome_musica: str) -> bool:
        """Verificar se uma música está disponível"""
        return nome_musica in self.music_tracks

    def listar_sons(self) -> List[str]:
        """Listar todos os sons disponíveis"""
        return list(self.sound_effects.keys())

    def listar_musicas(self) -> List[str]:
        """Listar todas as músicas disponíveis"""
        return list(self.music_tracks.keys())

    def _gerar_sons_ui(self):
        """Gerar sons de interface proceduralmente"""
        try:
            sample_rate = 22050

            # Som de seleção (ui_select) - tom suave
            duracao = 0.1
            t = np.linspace(0, duracao, int(sample_rate * duracao), False)
            freq = 800  # Frequência agradável
            amplitude = 0.3

            # Tom simples com fade out
            som_select = amplitude * np.sin(2 * np.pi * freq * t)
            fade_samples = int(sample_rate * 0.05)  # 50ms de fade
            som_select[-fade_samples:] *= np.linspace(1, 0, fade_samples)

            # Converter para pygame Sound
            som_select = np.clip(som_select, -1, 1)
            som_select_stereo = np.array([som_select, som_select]).T
            som_select_int = (som_select_stereo * 32767).astype(np.int16)

            self.sound_effects['ui_select'] = pygame.sndarray.make_sound(som_select_int)

            # Som de clique (ui_click) - mais percussivo
            duracao = 0.08
            t = np.linspace(0, duracao, int(sample_rate * duracao), False)
            freq = 1200
            amplitude = 0.4

            som_click = amplitude * np.sin(2 * np.pi * freq * t) * np.exp(-t * 20)
            som_click = np.clip(som_click, -1, 1)
            som_click_stereo = np.array([som_click, som_click]).T
            som_click_int = (som_click_stereo * 32767).astype(np.int16)

            self.sound_effects['ui_click'] = pygame.sndarray.make_sound(som_click_int)

            # Som de confirmação (ui_confirm) - mais alegre
            duracao = 0.15
            t = np.linspace(0, duracao, int(sample_rate * duracao), False)

            # Duas frequências para soar mais musical
            freq1, freq2 = 600, 800
            amplitude = 0.3

            som_confirm = amplitude * (
                np.sin(2 * np.pi * freq1 * t) +
                0.5 * np.sin(2 * np.pi * freq2 * t)
            )
            fade_samples = int(sample_rate * 0.1)
            som_confirm[-fade_samples:] *= np.linspace(1, 0, fade_samples)

            som_confirm = np.clip(som_confirm, -1, 1)
            som_confirm_stereo = np.array([som_confirm, som_confirm]).T
            som_confirm_int = (som_confirm_stereo * 32767).astype(np.int16)

            self.sound_effects['ui_confirm'] = pygame.sndarray.make_sound(som_confirm_int)

            # Som de voltar (ui_back) - tom descendente
            duracao = 0.12
            t = np.linspace(0, duracao, int(sample_rate * duracao), False)
            freq_inicial = 600
            freq_final = 400
            amplitude = 0.3

            # Frequência que desce
            freq_t = freq_inicial + (freq_final - freq_inicial) * (t / duracao)
            som_back = amplitude * np.sin(2 * np.pi * freq_t * t)

            fade_samples = int(sample_rate * 0.05)
            som_back[-fade_samples:] *= np.linspace(1, 0, fade_samples)

            som_back = np.clip(som_back, -1, 1)
            som_back_stereo = np.array([som_back, som_back]).T
            som_back_int = (som_back_stereo * 32767).astype(np.int16)

            self.sound_effects['ui_back'] = pygame.sndarray.make_sound(som_back_int)

        except (OSError, ImportError, ValueError, AttributeError) as e:
            print(f"Erro ao gerar sons de UI: {e}")

# Instância global do gerenciador de áudio
gerenciador_audio = AudioManager()
