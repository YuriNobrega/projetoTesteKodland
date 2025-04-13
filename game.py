import pgzrun
from math import sin # Função seno para movimentos suaves
import random 
from pygame import Rect # Para criar retângulos (usado em colisões)



# Classe que gerencia o fundo do jogo
class Background:
    def __init__(self):
        # Criando nuvens com posições aleatórias
        self.clouds = [
            Actor('cloud', (random.randint(0, WIDTH), random.randint(50, 200)))
            for _ in range(5)
        ]
        
        # Configurando velocidade e tamanho aleatório para cada nuvem
        for cloud in self.clouds:
            cloud.speed = random.uniform(25, 40)
            cloud.scale = random.uniform(0.5, 1.0)

        # Definindo as cores do céu para criar um gradiente
        self.sky_colors = [
            (135, 206, 235), 
            (100, 149, 237),  
            (42, 170, 138)    
        ]
        # Criando as camadas do cenário (montanhas e chão)
        self.layers = [
            Actor('bg_mountains', (WIDTH/2, HEIGHT-150)),
            Actor('bg_ground', (WIDTH/2, HEIGHT-50))
        ]

    # Método que atualiza a posição das nuvens
    def update(self, dt):
        for cloud in self.clouds:
            # Movimenta a nuvem para a direita
            cloud.x += cloud.speed * dt
            # Se a nuvem sair da tela pela direita
            if cloud.x > WIDTH + 100:
                cloud.x = -100
                cloud.y = random.randint(50, 200)
                cloud.speed = random.uniform(25, 40)
                cloud.scale = random.uniform(0.5, 1.0)
    # Método que desenha todos os elementos do fundo
    def draw(self):
        # Desenha o gradiente do céu
        for i in range(HEIGHT):
            t = i / HEIGHT
            color = [
                int(self.sky_colors[0][j] * (1-t) + self.sky_colors[2][j] * t)
                for j in range(3)
            ]
            screen.draw.line((0, i), (WIDTH, i), color)

        # Desenha o sol
        screen.draw.filled_circle((WIDTH-100, 100), 40, (255, 255, 190))

        # Desenha as nuvens
        for cloud in self.clouds:
            cloud.draw()

        # Desenha as camadas do cenário
        for layer in self.layers:
            layer.draw()

# Configurações gerais do jogo
TITLE = "Kodland"
WIDTH = 800
HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Classe que representa as plataformas do jogo
class Platform(Actor):
    def __init__(self, image, pos, moving=False, move_range=0, is_final=False):
        super().__init__(image, pos) # Inicializa a classe pai (Actor)
        self.moving = moving # Indica se a plataforma se move
        self.move_range = move_range # Alcance do movimento
        self.start_x = pos[0] # Posição inicial X
        self.direction = 1 # Direção do movimento (1 = direita, -1 = esquerda)
        self.is_final = is_final # Indica se é a plataforma final
        
        
# Atualiza a posição da plataforma se ela for móvel
    def update(self, dt):
        if self.moving:
            self.x += self.direction * 100 * dt # Move a plataforma
            # Inverte a direção se atingir o limite do alcance
            if abs(self.x - self.start_x) > self.move_range:
                self.direction *= -1

# Classe que representa as moedas coletáveis
class Coin(Actor):
    def __init__(self, pos):
        super().__init__('coin_1', pos) # Inicializa com o primeiro frame da moeda
        self.frames = ['coin_1', 'coin_2', 'coin_3'] # Frames da animação
        self.current_frame = 0 # Frame atual
        self.animation_timer = 0 # Temporizador da animação
        self.animation_delay = 0.1 # Tempo entre frames


    # Atualiza a animação da moeda
    def update(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_delay:
            self.animation_timer = 0
            # Avança para o próximo frame da animação
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

# Classe que representa o jogador
class Player:
    def __init__(self):
        self.actor = Actor('hero_idle_1') # Cria o ator com a primeira imagem do personagem
        self.actor.pos = (100, HEIGHT - 100) # Posição inicial
        self.velocity_y = 0 # Velocidade vertical
        self.jumping = False # Estado de pulo
        self.facing_right = True # Direção que o personagem está olhando
        
        # Define os frames de animação para cada estado
        self.idle_frames_right = ['hero_idle_1', 'hero_idle_2', 'hero_idle_3', 'hero_idle_4'] # Parado olhando direita
        self.idle_frames_left = ['hero_idle_1_flip', 'hero_idle_2_flip', 'hero_idle_3_flip', 'hero_idle_4_flip', ] # Parado olhando esquerda
        self.run_frames_right = ['hero_run_1', 'hero_run_2', 'hero_run_3', 'hero_run_4'] # Correndo para direita
        self.run_frames_left = ['hero_run_1_flip', 'hero_run_2_flip', 'hero_run_3_flip', 'hero_run_4_flip'] # Correndo para esquerda
        self.current_frame = 0 # Frame atual da animação
        self.animation_timer = 0 # Temporizador da animação
        self.animation_delay = 0.2 # Tempo entre frames
        self.health = 3 # Vida do jogador
        self.score = 0 # Pontuação
        self.on_ground = False # Indica se está no chão
        self.jump_strength = -500 # Força do pulo
        self.gravity = 1300 # Gravidade
        self.jump_sound = 'jump' # Som do pulo
        self.hurt_sound = 'hurt' # Som de dano
        
        # Frames para a animação de pulo
        self.jump_frames_right = ['hero_jump']
        self.jump_frames_left = ['hero_jump_flip']


    # Atualiza a posição e estado do jogador
    def update(self, dt, platforms):
        prev_y = self.actor.y # Guarda posição Y anterior
        
        # Aplica gravidade
        self.velocity_y += self.gravity * dt
        self.actor.y += self.velocity_y * dt

        # Atualiza direção do sprite baseado no input
        if keyboard.left:
            self.facing_right = False
        elif keyboard.right:
            self.facing_right = True

        self.on_ground = False
        
        # Verifica colisão com plataformas
        for platform in platforms:
            if self.actor.colliderect(platform):
                if self.velocity_y > 0 and prev_y <= platform.top:
                    self.actor.bottom = platform.top
                    self.velocity_y = 0
                    self.jumping = False
                    self.on_ground = True
                    
                    
        # Mantém o jogador dentro dos limites da tela
        if self.actor.bottom > HEIGHT - 100:
            self.actor.bottom = HEIGHT - 100
            self.actor.x = max(50, min(WIDTH-50, self.actor.x))
            self.velocity_y = 0
            self.jumping = False
            self.on_ground = True

        # Lógica da animação
        self.animation_timer += dt
        if self.animation_timer >= self.animation_delay:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % 4  # Changed from 2 to 4 for proper frame cycling

       # Seleciona a animação apropriada baseada no estado
        if self.jumping:
            if self.facing_right:
                self.actor.image = self.jump_frames_right[0]
            else:
                self.actor.image = self.jump_frames_left[0]
                
        # Caso esteja correndo, muda a animação para a de corrida
        elif keyboard.left or keyboard.right:
            if self.facing_right:
                self.actor.image = self.run_frames_right[self.current_frame]
            else:
                self.actor.image = self.run_frames_left[self.current_frame]
        # Animação parada (idle)
        else:
            if self.facing_right:
                self.actor.image = self.idle_frames_right[self.current_frame]
            else:
                self.actor.image = self.idle_frames_left[self.current_frame]


# Classe que representa os inimigos terrestres
class Enemy:
    def __init__(self, x, y):
        self.actor = Actor('enemy_idle_1') # Cria o ator com a primeira imagem do inimigo
        self.actor.pos = (x, y) # Posição inicial
        self.direction = 1 # Direção do movimento
        self.patrol_time = 0 # Tempo de patrulha
        self.idle_frames = ['enemy_idle_1', 'enemy_idle_2', 'enemy_idle_3'] # Frames de animação
        self.current_frame = 0 # Frame atual
        self.animation_timer = 0 # Temporizador da animação
        self.animation_delay = 0.15 # Tempo entre frames
        self.patrol_range = 200 # Alcance da patrulha
        self.speed = 150 # Velocidade de movimento
        self.start_x = x # Posição inicial X
        self.direction = random.choice([-1, 1]) # Direção inicial aleatória
        self.active = True # Estado do inimigo

    # Atualiza posição e animação do inimigo
    def update(self, dt, platforms):
        if not self.active:
            return

        # Move o inimigo
        new_x = self.actor.x + self.direction * self.speed * dt

        # Verifica se atingiu o limite da patrulha
        if abs(new_x - self.start_x) > self.patrol_range:
            self.direction *= -1
        else:
            self.actor.x = new_x

        # Inverte o sprite baseado na direção
        self.actor.flip_x = (self.direction < 0)

        # Atualiza animação
        self.animation_timer += dt
        if self.animation_timer >= self.animation_delay:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
            self.actor.image = self.idle_frames[self.current_frame]


# Classe que representa os inimigos voadores
class FlyingEnemy:
    def __init__(self, x, y):
        self.actor = Actor('flying_enemy_1') # Cria o ator com a primeira imagem do inimigo voador
        self.actor.pos = (x, y) # Posição inicial
        self.start_y = y # Posição Y inicial (para movimento ondular)
        self.time = 0 # Tempo para movimento senoidal
        self.speed = 100 # Velocidade de movimento
        self.amplitude = 50 # Amplitude do movimento vertical
        self.direction = 1 # Direção do movimento
        
        # Frames de animação para cada direção
        self.frames_left = ['flying_enemy_1', 'flying_enemy_2', 'flying_enemy_3']
        self.frames_right = ['flying_enemy_1_flip', 'flying_enemy_2_flip', 'flying_enemy_3_flip']
        self.current_frame = 0 # Frame atual
        self.animation_timer = 0 # Temporizador da animação
        self.animation_delay = 0.15 # Tempo entre frames
        self.patrol_range = 200 # Alcance da patrulha
        self.start_x = x # Posição X inicial
        self.active = True # Estado do inimigo (ativo/derrotado)


    # Atualiza posição e animação do inimigo voado
    def update(self, dt):
        if not self.active:
            return

        # Atualiza posição horizontal
        new_x = self.actor.x + self.direction * self.speed * dt

        # Verifica se atingiu o limite da patrulha
        if abs(new_x - self.start_x) > self.patrol_range:
            self.direction *= -1
        else:
            self.actor.x = new_x

       # Atualiza posição vertical usando função seno
        self.time += dt
        self.actor.y = self.start_y + sin(self.time * 3) * self.amplitude

        # Atualiza animação baseada na direção
        self.animation_timer += dt
        if self.animation_timer >= self.animation_delay:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames_right)
            # Usa os frames apropriados baseado na direçãon
            if self.direction > 0:
                self.actor.image = self.frames_right[self.current_frame]
            else:
                self.actor.image = self.frames_left[self.current_frame]


# Classe principal que gerencia todo o jogo
class Game:
    def __init__(self, keep_music_state=False, keep_sound_state=False):
        self.state = 'MENU' # Estado inicial do jogo (MENU, PLAYING, GAME_OVER, WIN)
        # Inicializa os elementos do jogo
        self.player = Player()
        self.enemies = [Enemy(300, HEIGHT - 100), Enemy(500, HEIGHT - 100)]
        self.flying_enemies = [
            FlyingEnemy(300, HEIGHT - 400),
            FlyingEnemy(500, HEIGHT - 350)
        ]
        self.background = Background()

        # Configura o estado do áudio
        self.music_on = True if not keep_music_state else self.music_on
        self.sound_effects_on = True if not keep_sound_state else self.sound_effects_on

        # Cria as plataformas do jogo
        self.platforms = [
            # Plataformas do nível do chão
            Platform('platform', (400, HEIGHT - 200)),
            Platform('platform_moving', (200, HEIGHT - 300), moving=True, move_range=100),

            # Plataformas do meio do estágio
            Platform('platform', (600, HEIGHT - 320)),
            Platform('platform_moving', (400, HEIGHT - 430), moving=True, move_range=150),
            Platform('platform', (200, HEIGHT - 400)),

            # Plataforma final com a grama
            Platform('platform_win', (200, HEIGHT - 500), is_final=True)  # Make sure you have a platform image with grass
        ]
        # Cria as moedas coletávei
        self.coins = [
            Coin((300, HEIGHT - 250)),
            Coin((500, HEIGHT - 400)),
            Coin((200, HEIGHT - 550)),
            Coin((600, HEIGHT - 650)),
            Coin((300, HEIGHT - 850))  # Moeda acima da plataforma final
        ]

        # Inicia a música se estiver habilitada
        if hasattr(self, 'music_on') and self.music_on:
            try:
                music.play('background_music')
                music.set_volume(0.5)
            except Exception as e:
                print(f"Could not play background music: {e}")
                self.music_on = False
                
    # Métodos para controle de música
    def toggle_music(self):
        self.music_on = not self.music_on
        if self.music_on:
            try:
                music.unpause()
                music.set_volume(0.5)
            except:
                self.music_on = False
        else:
            music.pause()

    # Métodos para controle de efeitos sonoros
    def toggle_sound_effects(self):
        self.sound_effects_on = not self.sound_effects_on


    # Atualiza todos os elementos do jogo
    def update(self, dt):
        if self.state == 'PLAYING':
            self.player.update(dt, self.platforms)

            # Atualiza plataformas
            for platform in self.platforms:
                platform.update(dt)

            # Atualiza moedas e verifica coleta
            for coin in self.coins[:]:
                coin.update(dt)
                if self.player.actor.colliderect(coin):
                    self.coins.remove(coin)
                    self.player.score += 10
                    if self.sound_effects_on:
                        try:
                            sounds.coin.play()
                        except:
                            pass
            # Atualiza inimigos voadores e verifica colisões
            for flying_enemy in self.flying_enemies:
                flying_enemy.update(dt)
                if flying_enemy.active and self.player.actor.colliderect(flying_enemy.actor):
                    if self.player.velocity_y > 0 and self.player.actor.bottom < flying_enemy.actor.top + 20:
                        # Jogador pulou em cima do inimigo
                        flying_enemy.active = False
                        self.player.velocity_y = -300
                        if self.sound_effects_on:
                            try:
                                sounds.hurt.play()
                            except:
                                pass
                    
                    else:
                        # Jogador colidiu com o inimigo  
                        self.player.health -= 1
                        if self.sound_effects_on:
                            try:
                                sounds.hurt.play()
                            except:
                                pass
                        if self.player.health <= 0:
                            self.state = 'GAME_OVER'
                            try:
                                music.stop()
                                if self.sound_effects_on:
                                    sounds.game_over.play()
                            except:
                                pass
            # Atualiza inimigos terrestres e verifica colisões
            for enemy in self.enemies:
                enemy.update(dt, self.platforms)
                if enemy.active and self.player.actor.colliderect(enemy.actor):
                    if self.player.velocity_y > 0 and self.player.actor.bottom < enemy.actor.top + 20:
                        # Jogador pulou em cima do inimigo
                        enemy.active = False
                        self.player.velocity_y = -300
                        if self.sound_effects_on:
                            try:
                                sounds.hurt.play()
                            except:
                                pass
                    else:
                        # Jogador colidiu com o inimigo
                        self.player.health -= 1
                        if self.sound_effects_on:
                            try:
                                sounds.hurt.play()
                            except:
                                pass
                        if self.player.health <= 0:
                            self.state = 'GAME_OVER'
                            try:
                                music.stop()
                                if self.sound_effects_on:
                                    sounds.game_over.play()
                            except:
                                pass

            # Verifica condição de vitória   
            for platform in self.platforms:
                if platform.is_final and self.player.actor.colliderect(platform):
                    if self.player.actor.bottom <= platform.top + 10:  # Make sure player is on top
                        self.state = 'WIN'
                        try:
                            music.stop()
                            if self.sound_effects_on:
                                sounds.victory.play()  # You'll need to add a victory sound
                        except:
                            pass

# Instância global do jogo
game = Game()

# Função que desenha todos os elementos na tela
def draw():
    screen.clear()
    game.background.draw()

    if game.state == 'MENU':
        screen.draw.text("Kodland", center=(WIDTH/2, HEIGHT/4), fontsize=60, color=WHITE)
        screen.draw.text("Começar jogo", center=(WIDTH/2, HEIGHT/2), fontsize=30, color=WHITE)
        screen.draw.text(f"Ligar/desligar música: {'ON' if game.music_on else 'OFF'}",
                        center=(WIDTH/2, HEIGHT/2 + 50), fontsize=30, color=WHITE)
        screen.draw.text(f"Ligar/desligar efeitos sonoros: {'ON' if game.sound_effects_on else 'OFF'}",
                        center=(WIDTH/2, HEIGHT/2 + 100), fontsize=30, color=WHITE)
        screen.draw.text("Sair", center=(WIDTH/2, HEIGHT/2 + 150), fontsize=30, color=WHITE)
        pass

    elif game.state == 'PLAYING':
        for platform in game.platforms:
            platform.draw()
        for coin in game.coins:
            coin.draw()
        game.player.actor.draw()
        for enemy in game.enemies:
            if enemy.active:
                enemy.actor.draw()
        for flying_enemy in game.flying_enemies:
            if flying_enemy.active:
                flying_enemy.actor.draw()
        screen.draw.text(f"Vida: {game.player.health}", topleft=(10, 10), fontsize=30, color=WHITE)
        screen.draw.text(f"Pontos: {game.player.score}", topleft=(10, 40), fontsize=30, color=WHITE)
        pass

    elif game.state == 'GAME_OVER':
        # Desenha tela de game over
        screen.draw.text("Game Over!", center=(WIDTH/2, HEIGHT/2), fontsize=60, color=WHITE)
        screen.draw.text(f"Pontuação final: {game.player.score}", center=(WIDTH/2, HEIGHT/2 + 50), fontsize=30, color=WHITE)
        screen.draw.text("Clique para voltar para o menu", center=(WIDTH/2, HEIGHT/2 + 100), fontsize=30, color=WHITE)
        pass
    
    elif game.state == 'WIN':
        screen.draw.text("You Win!", center=(WIDTH/2, HEIGHT/2), fontsize=60, color=WHITE)
        screen.draw.text(f"Final Score: {game.player.score}", center=(WIDTH/2, HEIGHT/2 + 50), fontsize=30, color=WHITE)
        screen.draw.text("Click to return to menu", center=(WIDTH/2, HEIGHT/2 + 100), fontsize=30, color=WHITE)


# Função que atualiza a lógica do jogo
def update(dt):
    game.update(dt)

    if game.state == 'PLAYING':
        if keyboard.left:
            game.player.actor.x -= 200 * dt
            game.player.facing_right = False
        if keyboard.right:
            game.player.actor.x += 200 * dt
            game.player.facing_right = True
        if keyboard.space and not game.player.jumping and game.player.on_ground:
            game.player.velocity_y = game.player.jump_strength
            game.player.jumping = True
            if game.sound_effects_on:
                try:
                    sounds.jump.play()
                except:
                    pass


# Função que gerencia cliques do mouse
def on_mouse_down(pos):
    if game.state == 'MENU':
        # Botão Iniciar Jogo
        if WIDTH/2-100 <= pos[0] <= WIDTH/2+100 and HEIGHT/2-20 <= pos[1] <= HEIGHT/2+20:
            game.state = 'PLAYING'
            if game.music_on:
                try:
                    music.play('background_music')
                    music.set_volume(0.5)
                except:
                    game.music_on = False

       # Botão que alterna Música
        elif WIDTH/2-100 <= pos[0] <= WIDTH/2+100 and HEIGHT/2+30 <= pos[1] <= HEIGHT/2+70:
            game.toggle_music()

        # Botão que alterna efeitos sonoros
        elif WIDTH/2-100 <= pos[0] <= WIDTH/2+100 and HEIGHT/2+80 <= pos[1] <= HEIGHT/2+120:
            game.toggle_sound_effects()

        # Botão de sair
        elif WIDTH/2-100 <= pos[0] <= WIDTH/2+100 and HEIGHT/2+130 <= pos[1] <= HEIGHT/2+170:
            quit()
        pass
    
    elif game.state in ['GAME_OVER', 'WIN']:  # função elif que lida com a derrota ou vitória do jogador
        # Reinicia o jogo mantendo as configurações de áudio
        current_music_state = game.music_on
        current_sound_state = game.sound_effects_on
        game.state = 'MENU'
        game.__init__(keep_music_state=True, keep_sound_state=True)
        game.music_on = current_music_state
        game.sound_effects_on = current_sound_state
            

pgzrun.go()