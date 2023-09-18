import pygame
import sys
import random
import time
from pygame.locals import *

from player import Player
from tile import Tile
from enemy import Enemy
from missile import Missile

pygame.init()

WIDTH = 500
HEIGHT = 842
window_size = (WIDTH, HEIGHT)

c_black = (0, 0, 0)
c_white = (255, 255, 255)
c_green = (0, 255, 0)
c_yellow = (255, 255, 0)
c_red = (255, 0, 0)
c_red_a = (255, 0, 0, 128)
c_gray = (128, 128, 128)
c_blue = (0, 0, 255)

# config
##########################
TILE_G = 10
TILE_B = 2
TILE_J = 2
TILE_G_COLOR = c_white
TILE_B_COLOR = c_red
TILE_J_COLOR = c_yellow
TILE_B_DAMAGE = 1
TILE_J_MULTI = 2

PLAYER_COLOR = c_gray
PLAYER_HEALTH = 100
PLAYER_SCORE = 0
PLAYER_ACC = 0.5
PLAYER_FRIC = -0.12
PLAYER_JUMP_P = 15
PLAYER_JUMP_K = 5
PLAYER_MISSILE_COLOR = c_green
PLAYER_MISSILE_COOL = 3
PLAYER_FORCE_COLOR = c_blue
PLAYER_FORCE_MULTI = 1.5
PLAYER_FORCE_COOL = 3000
PLAYER_HEALTH_GAIN = 10

ENEMY_COLOR = c_red
ENEMY_PREP = 100
ENEMY_MISSILE_COLOR = c_yellow
ENEMY_MISSILE_COOL = 2000
ENEMY_MISSILE_DAMAGE = 10
##########################

FPS = 60
FramePerSec = pygame.time.Clock()

DISPLAY = pygame.display.set_mode(window_size)
pygame.display.set_caption("PGplatformer")


def generate_tile(color):
    return Tile(random.randint(50,100), 12, random.randint(0,WIDTH-10), random.randint(0, HEIGHT-50), color, WIDTH)


def check_tile(entities, target):
    if pygame.sprite.spritecollide(target, entities, False):
        return True
    for entity in entities:
        if entity == target:
            continue
        if abs(target.rect.top - entity.rect.bottom) < 50 and abs(target.rect.bottom - entity.rect.top) < 50:
            return True
    return False


def generate_level(entities, amount, color, if_first_gen):
    while len(entities) < amount:
        tile = generate_tile(color)
        if not if_first_gen: tile.rect.y -= HEIGHT
        while check_tile(entities, tile):
            tile = generate_tile(color)
            if not if_first_gen: tile.rect.y -= HEIGHT
        entities.append(tile)
    return entities


def draw(entities_group, player, enemy):
    DISPLAY.fill(c_black)
    DISPLAY.blit(player.surf, player.rect)
    DISPLAY.blit(enemy.surf, enemy.rect)
    enemy.move()
    for entities in entities_group:
        for entity in entities:
            DISPLAY.blit(entity.surf, entity.rect)
            entity.move()
    draw_stats()


def draw_stats():
    text = pygame.font.SysFont("impact", 20)
    text_score = text.render(str(player.score), True, c_black)
    text_health = text.render(f"Heath: {player.health}%", True, c_black)
    pygame.draw.line(DISPLAY, c_white, (0, 20), (WIDTH, 20), 40)
    pygame.draw.line(DISPLAY, c_gray, (0, 41), (WIDTH, 41), 1)
    pygame.draw.line(DISPLAY, c_gray, (0, 0), (WIDTH, 0), 1)
    DISPLAY.blit(text_score, (WIDTH/4*3, 5))
    DISPLAY.blit(text_health, (0, 5))


def draw_cross():
    pygame.draw.line(DISPLAY, TILE_B_COLOR, (0, 42), window_size, 20)
    pygame.draw.line(DISPLAY, TILE_B_COLOR, (window_size[0], 42), (0, window_size[1]), 20)

def draw_damage():
    damage = pygame.Surface((WIDTH, HEIGHT-41), pygame.SRCALPHA)
    damage.fill(c_red_a)
    DISPLAY.blit(damage, (0, 42))

def update(entities, player):
    hit = pygame.sprite.spritecollide(player, entities, False)
    if hit and player.vel.y > 0:
        player.player_hit(hit[0])


def if_collision(entities, target):
    hit = pygame.sprite.spritecollide(target, entities, False)
    if hit:
        return hit[0]
    return False


def update_entities(entities, target, color, amount):
    new_ent = []
    for entity in entities:
        entity.rect.y += abs(target.vel.y)
        if entity.rect.top < HEIGHT:
            new_ent.append(entity)
    return generate_level(new_ent, amount, color, False)

def update_missiles(missiles):
    new_missiles = []
    for missile in missiles:
        if missile.rect.bottom > 0 and missile.rect.top < HEIGHT:
            new_missiles.append(missile)
    return new_missiles


player = Player(WIDTH, HEIGHT, PLAYER_COLOR, PLAYER_ACC, PLAYER_FRIC, PLAYER_HEALTH)
enemy = Enemy(WIDTH, ENEMY_COLOR, ENEMY_PREP)

player_missiles = []
enemy_missiles = []

player_force = []

start_tile = Tile(WIDTH, 20, WIDTH/2, HEIGHT-10, TILE_G_COLOR, WIDTH)
start_tile.if_move = False
g_tile = Tile(WIDTH/4, 20, WIDTH/2, HEIGHT-100, TILE_G_COLOR, WIDTH)

good_entities = []
good_entities.append(start_tile)
good_entities.append(g_tile)
good_entities = generate_level(good_entities, TILE_G+1, TILE_G_COLOR, True)
bad_entities = []
bad_entities = generate_level(bad_entities, TILE_B+1, TILE_B_COLOR, True)
jump_entities = []
jump_entities = generate_level(jump_entities, TILE_J+1, TILE_J_COLOR, True)

enemy_fired_time = 0
player_force_time = 0

while True:
    current_time = pygame.time.get_ticks()
    draw((good_entities, bad_entities, jump_entities, player_missiles, enemy_missiles, player_force), player, enemy)
    update(good_entities, player)

    player.move()
    hit = if_collision(enemy_missiles, player)
    if if_collision(bad_entities, player) or hit:       # damage
        draw_damage()
        if hit:
            player.health -= ENEMY_MISSILE_DAMAGE
            enemy_missiles.remove(hit)
            hit = False
        else:
            player.health -= TILE_B_DAMAGE
    hit = if_collision(player_missiles, enemy)
    if hit:                                             # player hit
        player.health += PLAYER_HEALTH_GAIN
        player_missiles.remove(hit)
        hit = False
        if player.health > PLAYER_HEALTH:
            player.health = PLAYER_HEALTH
    if if_collision(jump_entities, player):             # turbo jump
        player.jump(PLAYER_JUMP_P*TILE_J_MULTI)
    if if_collision(player_force, enemy):               # force jump
        player.jump(PLAYER_JUMP_P*PLAYER_FORCE_MULTI)
    if player.rect.top > HEIGHT or player.health == 0:  # game over
        good_entities.clear()
        bad_entities.clear()
        jump_entities.clear()
        DISPLAY.fill(c_black)
        draw_stats()
        draw_damage()
        pygame.display.update()
        time.sleep(1)
        pygame.quit()
        sys.exit()


    if player.rect.top <= HEIGHT/2:
        player.score += 1
        enemy.score -= 1
        if enemy.score == 0:
            enemy.score = ENEMY_PREP
            enemy.up_dif()
        player.pos.y += abs(player.vel.y)
        good_entities = update_entities(good_entities, player, TILE_G_COLOR, TILE_G+1)
        bad_entities = update_entities(bad_entities, player, TILE_B_COLOR, TILE_B+1)
        jump_entities = update_entities(jump_entities, player, TILE_J_COLOR, TILE_J+1)
    
    if current_time - enemy_fired_time >= ENEMY_MISSILE_COOL:
        enemy_missiles.append(Missile(enemy.rect.left+25, enemy.rect.bottom+15, 7, 30, ENEMY_MISSILE_COLOR, 100, 10))
        enemy_fired_time = current_time

    player_missiles = update_missiles(player_missiles)
    enemy_missiles = update_missiles(enemy_missiles)
    player_force = update_missiles(player_force)

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:                                                                                # esc / quit key
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_UP and if_collision(good_entities, player):                                            # up / jump key
                player.jump(PLAYER_JUMP_P)
            if event.key == pygame.K_SPACE and len(player_missiles) < PLAYER_MISSILE_COOL:                                  # space / fire missile key
                player_missiles.append(Missile(player.pos.x, player.pos.y-52.5, 5, 25, PLAYER_MISSILE_COLOR, 100, -10))
            if event.key == pygame.K_LCTRL and current_time - player_force_time >= PLAYER_FORCE_COOL:                       # left ctrl / fire force key
                player_force.append(Missile(player.pos.x, player.pos.y-45, 10, 10, PLAYER_FORCE_COLOR, 100, -15))
                player_force_time = current_time
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP and player.if_jump:                                                                 # up / kill jump key
                player.kill_jump(PLAYER_JUMP_K)
        if event.type == QUIT:
            pygame.quit()
            sys.exit()


    pygame.display.update()
    FramePerSec.tick(FPS)
