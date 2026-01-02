import pygame, random, math, time

pygame.init()
pygame.mixer.init()

# ================== SETTINGS ==================
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shoot the UFOs!")
clock = pygame.time.Clock()

# ================== GAME STATES ==================
running = True
in_game = False
paused = False
countdown = True
counter = 3
last_time = time.time()
count_sound_played = False

score = 0
sound_on = True
volume = 0.5
slider_drag = False

# ================== SOUNDS ==================
shoot_sound = pygame.mixer.Sound("sounds/laser-gun.mp3")
click_sound = pygame.mixer.Sound("sounds/mouse-click.mp3")
hit_sound = pygame.mixer.Sound("sounds/explosion.mp3")
count_sound = pygame.mixer.Sound("sounds/countdown.mp3")

pygame.mixer.music.load("sounds/bg.mp3")
pygame.mixer.music.play(-1)

def set_volume(v):
    shoot_sound.set_volume(v)
    click_sound.set_volume(v)
    hit_sound.set_volume(v)
    count_sound.set_volume(v)
    pygame.mixer.music.set_volume(v)

set_volume(volume)

# ================== IMAGES ==================
bg = pygame.transform.scale(pygame.image.load("images/bg.jpg"), (WIDTH, HEIGHT))
player_img = pygame.transform.scale(pygame.image.load("images/spaceship.png").convert_alpha(), (80,100))
enemy_img = pygame.transform.scale(pygame.image.load("images/ufo.png").convert_alpha(), (40,40))
explosion_img = pygame.transform.scale(pygame.image.load("images/explosion.png").convert_alpha(), (50,50))
heart_img = pygame.transform.scale(pygame.image.load("images/heart.png").convert_alpha(), (30,30))

# ================== CLASSES ==================
class Player:
    def __init__(self):
        self.x = WIDTH//2
        self.y = HEIGHT-110
        self.lives = 3
    def draw(self):
        screen.blit(player_img,(self.x,self.y))

class Enemy:
    def __init__(self):
        self.reset()
    def reset(self):
        self.x = random.randint(0, WIDTH-40)
        self.y = random.randint(-300,-40)
        self.speed = random.uniform(0.7,1.3)
        self.base_x = self.x
        self.angle = 0
        self.zigzag_speed = random.uniform(0.03,0.06)
        self.zigzag_width = random.randint(20,50)
    def draw(self):
        self.y += self.speed
        self.angle += self.zigzag_speed
        self.x = self.base_x + math.sin(self.angle)*self.zigzag_width
        screen.blit(enemy_img,(self.x,self.y))
        if self.y > HEIGHT:
            self.reset()

class Bullet:
    def __init__(self,x,y):
        self.x,self.y = x,y
    def draw(self):
        pygame.draw.rect(screen,(255,0,0),(self.x,self.y,3,8))
        self.y -= 8

class Explosion:
    def __init__(self,x,y):
        self.x,self.y = x,y
        self.counter = 15
    def draw(self):
        screen.blit(explosion_img,(self.x,self.y))
        self.counter -= 1

# ================== UI ==================
def draw_center_text(text, size=50, y_offset=0):
    font = pygame.font.SysFont("", size)
    rendered = font.render(text, True, (255,255,255))
    screen.blit(rendered, (WIDTH//2 - rendered.get_width()//2,
                           HEIGHT//2 - rendered.get_height()//2 + y_offset))

def draw_hearts(lives):
    for i in range(lives):
        screen.blit(heart_img,(50+i*35,10))

def draw_score():
    font = pygame.font.SysFont("",26)
    txt = font.render(f"Score: {score}", True, (255,255,255))
    screen.blit(txt,(WIDTH-130,10))

def pause_button():
    rect = pygame.Rect(10,10,30,30)
    pygame.draw.rect(screen,(180,180,180),rect,border_radius=6)
    font = pygame.font.SysFont("",22)
    txt = font.render("||", True, (0,0,0))
    screen.blit(txt,(rect.x+rect.width//2 - txt.get_width()//2,
                     rect.y+rect.height//2 - txt.get_height()//2))
    return rect

def button(text,x,y,w,h):
    rect = pygame.Rect(x,y,w,h)
    pygame.draw.rect(screen,(90,150,200),rect,border_radius=12)
    font = pygame.font.SysFont("",30)
    t = font.render(text,True,(255,255,255))
    screen.blit(t,(x+w//2-t.get_width()//2,y+h//2-t.get_height()//2))
    return rect

def volume_slider(x,y,w):
    global volume
    pygame.draw.rect(screen,(160,160,160),(x,y,w,6),border_radius=4)
    knob_x = x + int(volume*w)
    knob = pygame.Rect(knob_x-7,y-8,14,22)
    pygame.draw.rect(screen,(255,255,255),knob,border_radius=6)
    return knob

# ================== RESET ==================
def reset_game():
    global score, in_game, paused, countdown, counter, count_sound_played
    score = 0
    player.lives = 3
    bullets.clear()
    explosions.clear()
    enemies.clear()
    for _ in range(7): enemies.append(Enemy())
    countdown = True
    counter = 3
    count_sound_played = False
    in_game = False
    paused = False

# ================== OBJECTS ==================
player = Player()
enemies = [Enemy() for _ in range(7)]
bullets = []
explosions = []
SPEED = 5

# Pause objects
btn_resume = None
slider_knob = None

# ================== MAIN LOOP ==================
while running:
    clock.tick(60)
    screen.blit(bg,(0,0))
    mouse = pygame.mouse.get_pos()

    # ⏳ COUNTDOWN
    if countdown:
        draw_center_text("GO!" if counter < 0 else str(counter),80)
        if not count_sound_played:
            count_sound.play()
            count_sound_played = True
        if time.time()-last_time>=1:
            last_time=time.time()
            counter-=1
            if counter < -1:
                countdown=False
                in_game=True
                count_sound_played = False

    # ⏸️ PAUSE
    elif paused:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        screen.blit(overlay,(0,0))

        draw_center_text("PAUSED",60,-100)
        draw_center_text("VOLUME",30,-20)
        slider_knob = volume_slider(WIDTH//2-120, HEIGHT//2,240)
        btn_resume = button("RESUME", WIDTH//2-110, HEIGHT//2+60, 220, 55)

    # 🎮 GAMEPLAY
    elif in_game:
        player.draw()
        draw_hearts(player.lives)
        draw_score()
        pause_rect = pause_button()

        for e_obj in enemies:
            e_obj.draw()
            for b in bullets[:]:
                if e_obj.x<b.x<e_obj.x+40 and e_obj.y<b.y<e_obj.y+40:
                    score+=10
                    explosions.append(Explosion(e_obj.x,e_obj.y))
                    bullets.remove(b)
                    e_obj.reset()

            if (e_obj.x<player.x+80 and e_obj.x+40>player.x and
                e_obj.y<player.y+100 and e_obj.y+40>player.y):
                player.lives-=1
                if sound_on: hit_sound.play()
                e_obj.reset()
                if player.lives<=0:
                    pygame.mixer.music.load("sounds/game-over.mp3")
                    pygame.mixer.music.play()
                    in_game=False

        for b in bullets[:]:
            b.draw()
            if b.y<0: bullets.remove(b)

        for ex in explosions[:]:
            ex.draw()
            if ex.counter<=0: explosions.remove(ex)

        keys=pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x>0: player.x-=SPEED
        if keys[pygame.K_RIGHT] and player.x<WIDTH-80: player.x+=SPEED

    # ☠️ GAME OVER
    else:
        draw_center_text("GAME OVER",60,-40)
        draw_center_text(f"Score: {score}",30,30)
        btn_retry = button("PLAY AGAIN",WIDTH//2-110,HEIGHT//2+70,220,55)

    # ================== EVENTS ==================
    for e in pygame.event.get():
        if e.type==pygame.QUIT: running=False

        # KEY EVENTS
        if e.type==pygame.KEYDOWN:
            # Shoot
            if in_game and e.key==pygame.K_UP:
                bullets.append(Bullet(player.x+40,player.y))
                if sound_on: shoot_sound.play()
            # ESC to pause/resume
            if in_game and e.key==pygame.K_ESCAPE:
                paused = not paused
                if sound_on: click_sound.play()
            # ENTER to resume from pause or after death
            if (paused or not in_game) and e.key==pygame.K_RETURN:
                if paused:
                    paused=False
                    if sound_on: click_sound.play()
                elif not in_game and not countdown:
                    pygame.mixer.music.load("sounds/bg.mp3")
                    pygame.mixer.music.play(-1)
                    reset_game()
                    if sound_on: click_sound.play()

        # MOUSE PAUSE
        if in_game and e.type==pygame.MOUSEBUTTONDOWN:
            if pause_rect.collidepoint(e.pos):
                paused = True
                if sound_on: click_sound.play()

        # PAUSE EVENTS
        if paused:
            if e.type==pygame.MOUSEBUTTONDOWN:
                if btn_resume and btn_resume.collidepoint(e.pos):
                    paused=False
                    if sound_on: click_sound.play()
                if slider_knob and slider_knob.collidepoint(e.pos):
                    slider_drag=True
            if e.type==pygame.MOUSEBUTTONUP:
                slider_drag=False
            if e.type==pygame.MOUSEMOTION and slider_drag:
                volume=(e.pos[0]-(WIDTH//2-120))/240
                volume=max(0,min(1,volume))
                set_volume(volume)

        # GAME OVER EVENTS (mouse)
        if not in_game and not countdown and e.type==pygame.MOUSEBUTTONDOWN:
            if btn_retry.collidepoint(e.pos):
                if sound_on: click_sound.play()
                pygame.mixer.music.load("sounds/bg.mp3")
                pygame.mixer.music.play(-1)
                reset_game()

    pygame.display.update()

pygame.quit()
