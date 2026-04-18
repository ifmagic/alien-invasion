from pyscript import document, window
from pyodide.ffi import create_proxy
import asyncio
import random
import math

class Settings:
    def __init__(self):
        self.screen_height = 600
        self.screen_width = 800
        self.bg_color = "#0a0a1a"
        self.bullet_width = 4
        self.bullet_height = 18
        self.bullet_color = "#ffdd00"
        self.bullets_allowed = 6
        self.alien_drop_speed = 12
        self.fleet_direction = 1
        self.ships_limit = 3
        self.speedup_scale = 1.12
        self.score_scale = 1.5
        self.alien_bullet_color = "#ff4444"
        self.alien_bullet_speed = 3
        self.alien_fire_rate = 0.003
        self.initialize_dynamic_settings()
    
    def initialize_dynamic_settings(self):
        self.bullet_speed_factor = 3
        self.alien_speed_factor = 0.7
        self.ship_speed_factor = 4.5
        self.alien_points = 50
    
    def increase_speed(self):
        self.bullet_speed_factor *= self.speedup_scale
        self.alien_speed_factor *= self.speedup_scale
        self.ship_speed_factor *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)

class Star:
    def __init__(self, width, height):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.size = random.uniform(0.5, 2)
        self.speed = random.uniform(0.2, 0.8)
        self.brightness = random.uniform(0.3, 1)
    
    def update(self, height):
        self.y += self.speed
        if self.y > height:
            self.y = 0
            self.x = random.randint(0, 800)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 1
        self.size = random.uniform(2, 5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 0.03
        self.size *= 0.95

class Ship:
    def __init__(self, ai_setting, canvas):
        self.canvas = canvas
        self.ai_setting = ai_setting
        self.moving_right = False
        self.moving_left = False
        
        self.width = 55
        self.height = 65
        self.centerx = ai_setting.screen_width / 2
        self.bottom = ai_setting.screen_height - 15
        self.engine_glow = 0
    
    def update(self):
        self.engine_glow = (self.engine_glow + 0.1) % (2 * math.pi)
        if self.moving_right and self.centerx + self.width / 2 < self.ai_setting.screen_width:
            self.centerx += self.ai_setting.ship_speed_factor
        elif self.moving_left and self.centerx - self.width / 2 > 0:
            self.centerx -= self.ai_setting.ship_speed_factor
    
    def draw(self, ctx):
        glow_intensity = 0.5 + 0.3 * math.sin(self.engine_glow)
        
        gradient = ctx.createRadialGradient(
            self.centerx, self.bottom + 5, 0,
            self.centerx, self.bottom + 5, 30
        )
        gradient.addColorStop(0, f"rgba(59, 130, 246, {glow_intensity})")
        gradient.addColorStop(1, "rgba(59, 130, 246, 0)")
        ctx.fillStyle = gradient
        ctx.fillRect(self.centerx - 30, self.bottom - 10, 60, 40)
        
        ctx.fillStyle = "#2563eb"
        ctx.beginPath()
        ctx.moveTo(self.centerx, self.bottom - self.height)
        ctx.lineTo(self.centerx - self.width / 2, self.bottom)
        ctx.lineTo(self.centerx - self.width / 4, self.bottom - 15)
        ctx.lineTo(self.centerx, self.bottom - 5)
        ctx.lineTo(self.centerx + self.width / 4, self.bottom - 15)
        ctx.lineTo(self.centerx + self.width / 2, self.bottom)
        ctx.closePath()
        ctx.fill()
        
        ctx.fillStyle = "#60a5fa"
        ctx.beginPath()
        ctx.ellipse(self.centerx, self.bottom - self.height / 2, 8, 12, 0, 0, 2 * math.pi)
        ctx.fill()
        
        ctx.fillStyle = f"rgba(251, 191, 36, {glow_intensity})"
        ctx.beginPath()
        ctx.moveTo(self.centerx - 10, self.bottom)
        ctx.lineTo(self.centerx, self.bottom + 15 + glow_intensity * 10)
        ctx.lineTo(self.centerx + 10, self.bottom)
        ctx.closePath()
        ctx.fill()
    
    def center_ship(self):
        self.centerx = self.ai_setting.screen_width / 2

class Bullet:
    def __init__(self, ai_setting, ship):
        self.ai_setting = ai_setting
        self.x = ship.centerx - ai_setting.bullet_width / 2
        self.y = ship.bottom - ship.height
        self.width = ai_setting.bullet_width
        self.height = ai_setting.bullet_height
        self.color = ai_setting.bullet_color
        self.speed_factor = ai_setting.bullet_speed_factor
    
    def update(self):
        self.y -= self.speed_factor
    
    def draw(self, ctx):
        gradient = ctx.createLinearGradient(self.x, self.y, self.x, self.y + self.height)
        gradient.addColorStop(0, "#ffffff")
        gradient.addColorStop(0.3, "#ffdd00")
        gradient.addColorStop(1, "#ff8800")
        ctx.fillStyle = gradient
        ctx.shadowColor = "#ffdd00"
        ctx.shadowBlur = 10
        ctx.fillRect(self.x, self.y, self.width, self.height)
        ctx.shadowBlur = 0

class AlienBullet:
    def __init__(self, ai_setting, alien):
        self.ai_setting = ai_setting
        self.x = alien.x + alien.width / 2 - 2
        self.y = alien.y + alien.height
        self.width = 4
        self.height = 16
        self.color = ai_setting.alien_bullet_color
        self.speed_factor = ai_setting.alien_bullet_speed
    
    def update(self):
        self.y += self.speed_factor
    
    def draw(self, ctx):
        gradient = ctx.createLinearGradient(self.x, self.y, self.x, self.y + self.height)
        gradient.addColorStop(0, "#ff4444")
        gradient.addColorStop(0.5, "#ff0000")
        gradient.addColorStop(1, "#aa0000")
        ctx.fillStyle = gradient
        ctx.shadowColor = "#ff0000"
        ctx.shadowBlur = 8
        ctx.fillRect(self.x, self.y, self.width, self.height)
        ctx.shadowBlur = 0

class Alien:
    def __init__(self, ai_setting, x, y):
        self.ai_setting = ai_setting
        self.x = x
        self.y = y
        self.width = 44
        self.height = 34
        self.anim_offset = random.uniform(0, math.pi * 2)
    
    def check_edges(self):
        if self.x + self.width >= self.ai_setting.screen_width:
            return True
        elif self.x <= 0:
            return True
        return False
    
    def update(self):
        self.x += self.ai_setting.alien_speed_factor * self.ai_setting.fleet_direction
        self.anim_offset += 0.1
    
    def draw(self, ctx):
        bob_y = self.y + 2 * math.sin(self.anim_offset)
        
        ctx.fillStyle = "#dc2626"
        ctx.beginPath()
        ctx.ellipse(self.x + self.width / 2, bob_y + self.height / 2, 
                   self.width / 2, self.height / 2, 0, 0, 2 * math.pi)
        ctx.fill()
        
        ctx.fillStyle = "#f87171"
        ctx.beginPath()
        ctx.ellipse(self.x + self.width / 2, bob_y + self.height / 3, 
                   self.width / 3, self.height / 3, 0, 0, 2 * math.pi)
        ctx.fill()
        
        ctx.fillStyle = "#fff"
        ctx.beginPath()
        ctx.arc(self.x + self.width / 3, bob_y + self.height / 2, 6, 0, 2 * math.pi)
        ctx.arc(self.x + 2 * self.width / 3, bob_y + self.height / 2, 6, 0, 2 * math.pi)
        ctx.fill()
        
        ctx.fillStyle = "#000"
        ctx.beginPath()
        ctx.arc(self.x + self.width / 3 + 1, bob_y + self.height / 2, 3, 0, 2 * math.pi)
        ctx.arc(self.x + 2 * self.width / 3 + 1, bob_y + self.height / 2, 3, 0, 2 * math.pi)
        ctx.fill()
        
        ctx.strokeStyle = "#dc2626"
        ctx.lineWidth = 2
        ctx.beginPath()
        ctx.moveTo(self.x + self.width / 4, bob_y)
        ctx.lineTo(self.x + self.width / 4 - 5, bob_y - 8)
        ctx.moveTo(self.x + 3 * self.width / 4, bob_y)
        ctx.lineTo(self.x + 3 * self.width / 4 + 5, bob_y - 8)
        ctx.stroke()

class GameStats:
    def __init__(self, ai_setting):
        self.ai_setting = ai_setting
        self.reset_stats()
        self.game_active = False
        self.game_paused = False
        self.high_score = self.load_high_score()
    
    def load_high_score(self):
        try:
            stored = window.localStorage.getItem("alien_invasion_high_score")
            return int(stored) if stored else 0
        except:
            return 0
    
    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            try:
                window.localStorage.setItem("alien_invasion_high_score", str(self.high_score))
            except:
                pass
    
    def reset_stats(self):
        self.ships_left = self.ai_setting.ships_limit
        self.score = 0
        self.level = 1

ai_setting = Settings()
stats = GameStats(ai_setting)
canvas = None
ctx = None
ship = None
bullets = []
alien_bullets = []
aliens = []
particles = []
stars = []
keys_pressed = {}

def create_stars():
    global stars
    stars = []
    for _ in range(150):
        stars.append(Star(ai_setting.screen_width, ai_setting.screen_height))

def create_explosion(x, y, color="#ff4444"):
    for _ in range(15):
        particles.append(Particle(x, y, color))

def create_fleet():
    global aliens
    aliens = []
    alien_width = 44
    alien_height = 34
    ship_height = 65
    available_space_x = ai_setting.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    available_space_y = ai_setting.screen_height - 3 * alien_height - ship_height
    number_aliens_y = int(available_space_y / (2 * alien_height))
    
    for row_number in range(number_aliens_y):
        for alien_number in range(number_aliens_x):
            alien_x = alien_width + 2 * alien_width * alien_number
            alien_y = alien_height + 2 * alien_height * row_number + 50
            alien = Alien(ai_setting, alien_x, alien_y)
            aliens.append(alien)

def check_fleet_edges():
    for alien in aliens:
        if alien.check_edges():
            change_fleet_direction()
            break

def change_fleet_direction():
    for alien in aliens:
        alien.y += ai_setting.alien_drop_speed
    ai_setting.fleet_direction *= -1

def alien_fire():
    if aliens and random.random() < ai_setting.alien_fire_rate * (1 + stats.level * 0.1):
        shooter = random.choice(aliens)
        alien_bullets.append(AlienBullet(ai_setting, shooter))

def check_bullet_alien_collisions():
    global bullets, aliens
    bullets_to_remove = []
    aliens_to_remove = []
    
    for i, bullet in enumerate(bullets):
        for j, alien in enumerate(aliens):
            if (bullet.x < alien.x + alien.width and 
                bullet.x + bullet.width > alien.x and 
                bullet.y < alien.y + alien.height and 
                bullet.y + bullet.height > alien.y):
                bullets_to_remove.append(i)
                aliens_to_remove.append(j)
                stats.score += ai_setting.alien_points
                create_explosion(alien.x + alien.width / 2, alien.y + alien.height / 2)
    
    for i in sorted(bullets_to_remove, reverse=True):
        if i < len(bullets):
            del bullets[i]
    for j in sorted(aliens_to_remove, reverse=True):
        if j < len(aliens):
            del aliens[j]
    
    if len(aliens) == 0:
        bullets = []
        alien_bullets.clear()
        ai_setting.increase_speed()
        create_fleet()
        stats.level += 1
        stats.save_high_score()

def check_alien_bullet_ship_collisions():
    global alien_bullets
    bullets_to_remove = []
    
    ship_left = ship.centerx - ship.width / 2
    ship_right = ship.centerx + ship.width / 2
    ship_top = ship.bottom - ship.height
    ship_bottom = ship.bottom
    
    for i, bullet in enumerate(alien_bullets):
        if (bullet.x < ship_right and 
            bullet.x + bullet.width > ship_left and 
            bullet.y < ship_bottom and 
            bullet.y + bullet.height > ship_top):
            bullets_to_remove.append(i)
            return True
    
    for i in sorted(bullets_to_remove, reverse=True):
        if i < len(alien_bullets):
            del alien_bullets[i]
    return False

def check_ship_collisions():
    for alien in aliens:
        ship_left = ship.centerx - ship.width / 2
        ship_right = ship.centerx + ship.width / 2
        ship_top = ship.bottom - ship.height
        ship_bottom = ship.bottom
        
        alien_right = alien.x + alien.width
        alien_bottom = alien.y + alien.height
        
        if (alien.x < ship_right and 
            alien_right > ship_left and 
            alien.y < ship_bottom and 
            alien_bottom > ship_top):
            create_explosion(ship.centerx, ship.bottom - ship.height / 2, "#3b82f6")
            return True
    return False

def check_aliens_bottom():
    for alien in aliens:
        if alien.y + alien.height >= ai_setting.screen_height:
            return True
    return False

def update_particles():
    global particles
    particles_to_remove = []
    for i, particle in enumerate(particles):
        particle.update()
        if particle.life <= 0:
            particles_to_remove.append(i)
    
    for i in sorted(particles_to_remove, reverse=True):
        if i < len(particles):
            del particles[i]

def draw_particles(ctx):
    for particle in particles:
        ctx.globalAlpha = particle.life
        ctx.fillStyle = particle.color
        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.size, 0, 2 * math.pi)
        ctx.fill()
    ctx.globalAlpha = 1

async def game_loop():
    global canvas, ctx, ship, bullets, alien_bullets, aliens, keys_pressed, particles, stars
    
    while True:
        try:
            ctx.fillStyle = ai_setting.bg_color
            ctx.fillRect(0, 0, canvas.width, canvas.height)
            
            for star in stars:
                star.update(ai_setting.screen_height)
                ctx.fillStyle = f"rgba(255, 255, 255, {star.brightness})"
                ctx.fillRect(star.x, star.y, star.size, star.size)
            
            if stats.game_active and not stats.game_paused:
                if keys_pressed.get("ArrowRight", False):
                    ship.moving_right = True
                else:
                    ship.moving_right = False
                
                if keys_pressed.get("ArrowLeft", False):
                    ship.moving_left = True
                else:
                    ship.moving_left = False
                
                ship.update()
                
                bullets_to_remove = []
                for i, bullet in enumerate(bullets):
                    bullet.update()
                    if bullet.y + bullet.height <= 0:
                        bullets_to_remove.append(i)
                
                for i in sorted(bullets_to_remove, reverse=True):
                    if i < len(bullets):
                        del bullets[i]
                
                alien_bullets_to_remove = []
                for i, bullet in enumerate(alien_bullets):
                    bullet.update()
                    if bullet.y >= ai_setting.screen_height:
                        alien_bullets_to_remove.append(i)
                
                for i in sorted(alien_bullets_to_remove, reverse=True):
                    if i < len(alien_bullets):
                        del alien_bullets[i]
                
                check_fleet_edges()
                for alien in aliens:
                    alien.update()
                
                alien_fire()
                
                check_bullet_alien_collisions()
                
                ship_hit = check_alien_bullet_ship_collisions()
                
                if ship_hit or check_ship_collisions() or check_aliens_bottom():
                    if stats.ships_left > 0:
                        stats.ships_left -= 1
                        bullets = []
                        alien_bullets.clear()
                        aliens = []
                        create_fleet()
                        ship.center_ship()
                        await asyncio.sleep(0.5)
                    else:
                        stats.game_active = False
                        stats.save_high_score()
                
                update_particles()
            
            draw_particles(ctx)
            ship.draw(ctx)
            for bullet in bullets:
                bullet.draw(ctx)
            for bullet in alien_bullets:
                bullet.draw(ctx)
            for alien in aliens:
                alien.draw(ctx)
            
            ctx.fillStyle = "#ffffff"
            ctx.font = "bold 22px 'Orbitron', sans-serif"
            ctx.fillText(f"SCORE: {stats.score}", 20, 35)
            ctx.fillText(f"LEVEL: {stats.level}", 20, 65)
            
            ctx.fillStyle = "#facc15"
            ctx.fillText(f"HIGH: {stats.high_score}", canvas.width - 160, 35)
            
            ctx.fillStyle = "#ef4444"
            hearts = "❤ " * stats.ships_left
            ctx.fillText(hearts, canvas.width - 120, 65)
            
            if stats.game_paused:
                ctx.fillStyle = "rgba(0, 0, 0, 0.6)"
                ctx.fillRect(0, 0, canvas.width, canvas.height)
                ctx.fillStyle = "#facc15"
                ctx.font = "bold 52px 'Orbitron', sans-serif"
                ctx.textAlign = "center"
                ctx.fillText("PAUSED", canvas.width / 2, canvas.height / 2)
                ctx.font = "24px sans-serif"
                ctx.fillStyle = "#ffffff"
                ctx.fillText("Press P to Resume", canvas.width / 2, canvas.height / 2 + 50)
                ctx.textAlign = "left"
            
            if not stats.game_active:
                ctx.fillStyle = "rgba(0, 0, 0, 0.7)"
                ctx.fillRect(0, 0, canvas.width, canvas.height)
                
                if stats.score > 0:
                    ctx.fillStyle = "#ffffff"
                    ctx.font = "32px 'Orbitron', sans-serif"
                    ctx.textAlign = "center"
                    ctx.fillText(f"FINAL SCORE: {stats.score}", canvas.width / 2, canvas.height / 2 - 60)
                
                ctx.fillStyle = "#3b82f6"
                ctx.font = "bold 48px 'Orbitron', sans-serif"
                ctx.textAlign = "center"
                ctx.fillText("ALIEN INVASION", canvas.width / 2, canvas.height / 2)
                
                ctx.fillStyle = "#ffffff"
                ctx.font = "24px sans-serif"
                ctx.fillText("Press SPACE to Play", canvas.width / 2, canvas.height / 2 + 60)
                ctx.textAlign = "left"
        
        except Exception as e:
            window.console.error(f"Loop error: {e}")
        
        await asyncio.sleep(0.016)

def on_key_down(e):
    global keys_pressed, stats, ship, bullets, aliens, alien_bullets
    keys_pressed[e.key] = True
    
    if e.key == " ":
        e.preventDefault()
        if not stats.game_active:
            ai_setting.initialize_dynamic_settings()
            stats.reset_stats()
            stats.game_active = True
            bullets = []
            alien_bullets.clear()
            particles.clear()
            aliens = []
            create_fleet()
            ship.center_ship()
        elif not stats.game_paused:
            if len(bullets) < ai_setting.bullets_allowed:
                new_bullet = Bullet(ai_setting, ship)
                bullets.append(new_bullet)
    
    if e.key.lower() == "p" and stats.game_active:
        stats.game_paused = not stats.game_paused
        e.preventDefault()

def on_key_up(e):
    global keys_pressed
    keys_pressed[e.key] = False

def hide_loading_overlay():
    overlay = document.getElementById("loadingOverlay")
    if overlay:
        overlay.classList.add("hidden")

async def main():
    global canvas, ctx, ship
    window.console.log("🚀 Alien Invasion Starting...")
    
    canvas = document.getElementById("gameCanvas")
    ctx = canvas.getContext("2d")
    
    ship = Ship(ai_setting, canvas)
    create_stars()
    
    hide_loading_overlay()
    
    document.addEventListener("keydown", create_proxy(on_key_down))
    document.addEventListener("keyup", create_proxy(on_key_up))
    
    await game_loop()

asyncio.ensure_future(main())
