import pygame
from pygame.locals import *
import pickle
from os import path

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 600
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_width))
pygame.display.set_caption('Platformer')

#definição das variaveis do Game
tile_size = 30
game_over = 0
main_menu = True
level = 1
max_levels = 3
scroll = 0

#Efeito Parallax
bg_images = []
for i in range(1, 5):
	bg_image = pygame.image.load(f"bg{i}.png").convert_alpha()
	bg_images.append(bg_image)
bg_width = bg_images[0].get_width()

def draw_bg():
	for x in range(4):
		speed = 0.3
		for i in bg_images:
			screen.blit(i, ((x* bg_width) - scroll * speed, 0))
			speed += 0.2

#carregar imagens

sol_img = pygame.image.load('sun.png')
bg_img = pygame.image.load('ceu.png')
restart_img = pygame.image.load('restart.png')
start_img = pygame.image.load('start.png')
quit_img = pygame.image.load('quit.png')

def reset_level(level):
	player.reset(50, screen_height - 130)
	lava_group.empty()
	exit_group.empty()

	if path.exists(f'level{level}_data'):
		pickle_in = open(f'level{level}_data', 'rb')
		world_data = pickle.load(pickle_in)
	world = World(world_data)

	return world

class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False

	def draw(self):
		action = False

		# pega posicao do mouse
		pos = pygame.mouse.get_pos()

		# checa mouse e condicaode click
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self .clicked == False:
				action = True
				self.clicked = True
		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False


		# Desenha o botao na tela
		screen.blit(self.image, self.rect)

		return action

class Player():
	def __init__(self, x, y):
		self.reset(x, y)

	def update(self, game_over):
		dx = 0
		dy = 0
		walk_cooldown = 2


		if game_over == 0:
			#Lê teclas acionadas
			key = pygame.key.get_pressed()
			if key[pygame.K_SPACE] and self.jumped == False and  self.in_air == False:
				self.vel_y = -15
				self.jumped = True
			if key[pygame.K_SPACE] == False:
				self.jumped = False
			if key[pygame.K_LEFT]:
				dx -= 3
				self.counter += 1
				self.direction = -1
				self.scroll -= 5
			if key[pygame.K_RIGHT]:
				dx += 3
				self.counter += 1
				self.direction = 1
				self.scroll += 5
			if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
				self.counter = 0
				self.index = 0
			if self.direction == 1:
				self.image = self.images_right[self.index]
			if self.direction == -1:
				self.image = self.images_left[self.index]

			#lidar com a animacao
			if self.counter > walk_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			#adiciona gravidade
			self.vel_y += 1
			if self.vel_y > 10:
				self.vel_y = 10
			dy += self.vel_y

			# check for collision
			self.in_air = True
			for tile in world.tile_list:
				# check for collision in x direction
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				# check for collision in y direction
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					# check if below the ground i.e. jumping
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
					# check if above the ground i.e. falling
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air = False

			#colisao com a lava
			if pygame.sprite.spritecollide(self, lava_group, False):
				game_over = -1
			#colisao com a saida
			if pygame.sprite.spritecollide(self, exit_group, False):
				game_over = 1

			#Atualiza as condenadas do jogador
			self.rect.x += dx
			self.rect.y += dy

			if self.rect.bottom > screen_height:
				self.rect.bottom = screen_height
				dy = 0

		#desenha o char na tela
		screen.blit(self.image, self.rect)

		return game_over

	def reset(self, x, y):

		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 8):
			img_right = pygame.image.load(f'char{num}.png')
			img_right = pygame.transform.scale(img_right, (25, 40))
			img_left = pygame.transform.flip(img_right, True, False)
			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.vel_y = 0
		self.jumped = False
		self.direction = 0
		self.in_air = True
		self.scroll = 0

class World():
	def __init__(self, data):
		self.tile_list = []

		#Carregar imagens
		dirt_img = pygame.image.load('dirt.jpg')
		grass_img = pygame.image.load('grass.png')

		row_count = 0
		for row in data:
			col_count = 0
			for tile in row:
				if tile == 1:
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 2:
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 3:
					lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
					lava_group.add(lava)
				if tile == 4:
					exit = Exit(col_count * tile_size, row_count * tile_size + (tile_size - 54))
					exit_group.add(exit)
				col_count += 1
			row_count += 1

	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])

class Lava(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('lava.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

class Exit(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('exit.png')
		self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 2)))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y


player = Player(50, screen_height - 130)

lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

if path.exists(f'level{level}_data'):
	pickle_in = open(f'level{level}_data', 'rb')
	world_data = pickle.load(pickle_in)
world = World(world_data)

restart_button = Button(screen_width // 2 - 116, screen_height // 2  - 50, restart_img)
start_button = Button(screen_width // 2 - 220, screen_height // 2, start_img)
quit_button = Button(screen_width // 2 + 50, screen_height // 2, quit_img)


run = True
while run:

	clock.tick(fps)
	screen.blit(sol_img,(50, 50))
	draw_bg()

	#Controle do Parallax
	key = pygame.key.get_pressed()
	if key[pygame.K_LEFT] and scroll > 0:
		scroll -= 5
	if key[pygame.K_RIGHT] and scroll < 3000:
		scroll += 5

	#botoes do menu
	if main_menu == True:
		if quit_button.draw():
			run = False
		if start_button.draw():
			main_menu = False
	else:
		world.draw()

		if game_over == 0:
			lava_group.update()

		lava_group.draw(screen)
		exit_group.draw(screen)


		game_over = player.update(game_over)

		#quando jogador morre
		if game_over == -1:
			if restart_button.draw():
				player.reset(50, screen_height - 130)
				game_over = 0

		if game_over == 1:
			level += 1
			if level <= max_levels:
				world_data = []
				world = reset_level(level)
				game_over = 0
			else:
				if restart_button.draw():
					level = 1
					world_data = []
					world = reset_level(level)
					game_over = 0

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()

pygame.quit()
