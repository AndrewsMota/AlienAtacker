import random
import arcade
from PIL import  ImageFilter


#Nome do jogo: Alien Atack

SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_enemy = 0.5
SPRITE_SCALING_LASER = 0.8

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Alien Atack"

BULLET_SPEED = 5
ENEMY_SPEED = 2

MAX_PLAYER_BULLETS = 15

# This margin controls how close the enemy gets to the left or right side
# before reversing direction.
ENEMY_VERTICAL_MARGIN = 15
RIGHT_ENEMY_BORDER = SCREEN_WIDTH - ENEMY_VERTICAL_MARGIN
LEFT_ENEMY_BORDER = ENEMY_VERTICAL_MARGIN

# How many pixels to move the enemy down when reversing
ENEMY_MOVE_DOWN_AMOUNT = 30

# Game state
GAME_OVER = 1
PLAY_GAME = 0


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Variables that will hold sprite lists
        self.player_list = None
        self.enemy_list = None
        self.player_bullet_list = None
        self.enemy_bullet_list = None
        self.shield_list = None

        # Textures for the enemy
        self.enemy_textures = None

        # State of the game
        self.game_state = PLAY_GAME

        # Set up the player info
        self.player_sprite = None
        self.score = 0

        # Enemy movement
        self.enemy_change_x = -ENEMY_SPEED

        # Don't show the mouse cursor
        self.set_mouse_visible(False)

        # Load sounds. Sounds from kenney.nl
        self.gun_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.hit_sound = arcade.load_sound(":resources:sounds/hit5.wav")

        arcade.set_background_color(arcade.color.AMAZON)
        
        self.background = None

        # arcade.configure_logging()

    def setup_level_one(self):
        # Carrega as texturas dos inimigos
        self.enemy_textures = []
        texture = arcade.load_texture("images/et3.png", mirrored=True)
        self.enemy_textures.append(texture)
        texture = arcade.load_texture("images/et3.png")
        self.enemy_textures.append(texture)

        # Cria as colunas de inimigos
        x_count = 7
        x_start = 380
        x_spacing = 65
        y_count = 5
        y_start = 420
        y_spacing = 45
        for x in range(x_start, x_spacing * x_count + x_start, x_spacing):
            for y in range(y_start, y_spacing * y_count + y_start, y_spacing):

                # Create the enemy instance
                enemy = arcade.Sprite()
                enemy.scale = SPRITE_SCALING_enemy
                enemy.texture = self.enemy_textures[1]

                # Posição do inimigo
                enemy.center_x = x
                enemy.center_y = y

                # Adiciona o inimigo a lista de inimigos
                self.enemy_list.append(enemy)

    def make_shield(self, x_start):

        shield_block_width = 5
        shield_block_height = 10
        shield_width_count = 20
        shield_height_count = 5
        y_start = 150
        for x in range(x_start,
                       x_start + shield_width_count * shield_block_width,
                       shield_block_width):
            for y in range(y_start,
                           y_start + shield_height_count * shield_block_height,
                           shield_block_height):
                shield_sprite = arcade.SpriteSolidColor(shield_block_width,
                                                        shield_block_height,
                                                        arcade.color.WHITE)
                shield_sprite.center_x = x
                shield_sprite.center_y = y
                self.shield_list.append(shield_sprite)

    def setup(self):
        self.background = arcade.load_texture("images/space_background.jpg")

        self.game_state = PLAY_GAME

        # Lista de sprites
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player_bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.shield_list = arcade.SpriteList(is_static=True)

        # Pontuação
        self.score = 0

        # Image from kenney.nl
        self.player_sprite = arcade.Sprite(":resources:images/space_shooter/"
                                           "playerShip3_orange.png", SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 40
        self.player_list.append(self.player_sprite)

        for x in range(85, 700, 190):
            self.make_shield(x)

        arcade.set_background_color(arcade.color.AMAZON)

        self.setup_level_one()

    def on_draw(self):
        arcade.start_render()
        
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)

        self.player_list.draw()
        self.enemy_list.draw()
        self.player_bullet_list.draw()
        self.enemy_bullet_list.draw()
        self.shield_list.draw()

        arcade.draw_text(f"Score: {self.score}", 10, 20, arcade.color.WHITE, 14)
        # Render the text

        if self.game_state == GAME_OVER:
            output = arcade.get_image()
            blurred_output = output.filter(ImageFilter.GaussianBlur(radius=2))
            blurred_texture = arcade.Texture(":memory:", blurred_output)
            arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT,
                                        blurred_texture)
            arcade.draw_text("GAME OVER", 250, 300, arcade.color.WHITE, 55)
            arcade.draw_text(f"Score: {self.score}", 10, 20, arcade.color.WHITE, 14)
    def on_mouse_motion(self, x, y, dx, dy):

        #Trava a tela caso seja game over
        if self.game_state == GAME_OVER:
            return

        self.player_sprite.center_x = x

    def on_mouse_press(self, x, y, button, modifiers):

        # Limita os projéteis do usuário
        if len(self.player_bullet_list) < MAX_PLAYER_BULLETS:

            # Som de tiro
            if self.game_state != GAME_OVER:
                arcade.play_sound(self.gun_sound)

            # Projétil
            bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", SPRITE_SCALING_LASER)

            # Angulo do projétil
            bullet.angle = 90

            # Velocidade do projétil
            bullet.change_y = BULLET_SPEED

            # Posição do projétil
            bullet.center_x = self.player_sprite.center_x
            bullet.bottom = self.player_sprite.top
            
            self.player_bullet_list.append(bullet)

    def update_enemies(self):

        # Move o inimigo verticalmente
        for enemy in self.enemy_list:
            enemy.center_x += self.enemy_change_x

        # Caso o inimigo atinja a borda, faz com que ele se mova pra baixo
        move_down = False
        for enemy in self.enemy_list:
            if enemy.right > RIGHT_ENEMY_BORDER and self.enemy_change_x > 0:
                self.enemy_change_x *= -1
                move_down = True
            if enemy.left < LEFT_ENEMY_BORDER and self.enemy_change_x < 0:
                self.enemy_change_x *= -1
                move_down = True


        if move_down:
            for enemy in self.enemy_list:
                enemy.center_y -= ENEMY_MOVE_DOWN_AMOUNT
                if self.enemy_change_x > 0:
                    enemy.texture = self.enemy_textures[0]
                else:
                    enemy.texture = self.enemy_textures[1]

    def allow_enemies_to_fire(self):
        x_spawn = []
        for enemy in self.enemy_list:
            # Ajusta a chance de disparo dos inimigos -> - inimigos = + projéteis
            chance = 4 + len(self.enemy_list) * 4

            # Fire if we roll a zero, and no one else in this column has had
            # a chance to fire.
            if random.randrange(chance) == 0 and enemy.center_x not in x_spawn:
                bullet = arcade.Sprite(":resources:images/space_shooter/laserRed01.png", SPRITE_SCALING_LASER)
                bullet.angle = 180
                bullet.change_y = -BULLET_SPEED
                bullet.center_x = enemy.center_x
                bullet.top = enemy.bottom

                self.enemy_bullet_list.append(bullet)

            x_spawn.append(enemy.center_x)

    def process_enemy_bullets(self):

        # Move os projéteis
        self.enemy_bullet_list.update()

        # Percore a lista de projéteis
        for bullet in self.enemy_bullet_list:
            # Checa se o projétil acertou o escudo
            hit_list = arcade.check_for_collision_with_list(bullet, self.shield_list)

            # Se sim, remove o projétil e o escudo
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()
                for shield in hit_list:
                    shield.remove_from_sprite_lists()
                continue

            # Checa se o jogador foi atingido
            if arcade.check_for_collision_with_list(self.player_sprite, self.enemy_bullet_list):
                self.game_state = GAME_OVER

            # Caso o projétil saia da tela, remove
            if bullet.top < 0:
                bullet.remove_from_sprite_lists()

    def process_player_bullets(self):

        # Move os projéteis
        self.player_bullet_list.update()

        # Percore os projéteis
        for bullet in self.player_bullet_list:

            # Checa se o projétil atingiu o escudo
            hit_list = arcade.check_for_collision_with_list(bullet, self.shield_list)
            # Caso tenha atingido, remove o projétil
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()
                for shield in hit_list:
                    shield.remove_from_sprite_lists()
                continue

            # Checa se o projétil acertou o inimigo
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)

            # Caso tenha acertado, remove o projétil
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            # Aumenta a pontuação ao acertar um inimigo
            for enemy in hit_list:
                enemy.remove_from_sprite_lists()
                self.score += 1

                # Hit Sound
                arcade.play_sound(self.hit_sound)

            # Remove os projeteis que sairem da tela
            if bullet.bottom > SCREEN_HEIGHT:
                bullet.remove_from_sprite_lists()

    def on_update(self, delta_time):
        """ Movement and game logic """

        if self.game_state == GAME_OVER:
            return

        self.update_enemies()
        self.allow_enemies_to_fire()
        self.process_enemy_bullets()
        self.process_player_bullets()

        if len(self.enemy_list) == 0:
            self.setup_level_one()


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()