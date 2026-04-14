from pyscript import document, window
from pyodide.ffi import create_proxy
import asyncio 

# 游戏设置类
class Settings:
    def __init__(self):
        self.screen_height = 600
        self.screen_width = 800
        self.bg_color = "#000000"
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = "#ffdd00"
        self.bullets_allowed = 5
        self.alien_drop_speed = 10
        self.fleet_direction = 1
        self.ships_limit = 3
        self.speedup_scale = 1.1
        self.score_scale = 1.5
        self.initialize_dynamic_settings()
    
    def initialize_dynamic_settings(self):
        self.bullet_speed_factor = 2
        self.alien_speed_factor = 0.5
        self.ship_speed_factor = 3
        self.alien_points = 50
    
    def increase_speed(self):
        self.bullet_speed_factor *= self.speedup_scale
        self.alien_speed_factor *= self.speedup_scale
        self.ship_speed_factor *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)

# 飞船类
class Ship:
    def __init__(self, ai_setting, canvas):
        self.canvas = canvas
        self.ai_setting = ai_setting
        self.moving_right = False
        self.moving_left = False
        
        self.width = 50
        self.height = 60
        self.centerx = ai_setting.screen_width / 2
        self.bottom = ai_setting.screen_height - 10
    
    def update(self):
        if self.moving_right and self.centerx + self.width / 2 < self.ai_setting.screen_width:
            self.centerx += self.ai_setting.ship_speed_factor
        elif self.moving_left and self.centerx - self.width / 2 > 0:
            self.centerx -= self.ai_setting.ship_speed_factor
    
    def draw(self, ctx):
        ctx.fillStyle = "#3b82f6"
        ctx.beginPath()
        ctx.moveTo(self.centerx, self.bottom - self.height)
        ctx.lineTo(self.centerx - self.width / 2, self.bottom)
        ctx.lineTo(self.centerx + self.width / 2, self.bottom)
        ctx.closePath()
        ctx.fill()
    
    def center_ship(self):
        self.centerx = self.ai_setting.screen_width / 2

# 子弹类
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
        ctx.fillStyle = self.color
        ctx.fillRect(self.x, self.y, self.width, self.height)

# 外星人类
class Alien:
    def __init__(self, ai_setting, x, y):
        self.ai_setting = ai_setting
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
    
    def check_edges(self):
        if self.x + self.width >= self.ai_setting.screen_width:
            return True
        elif self.x <= 0:
            return True
        return False
    
    def update(self):
        self.x += self.ai_setting.alien_speed_factor * self.ai_setting.fleet_direction
    
    def draw(self, ctx):
        ctx.fillStyle = "#ef4444"
        ctx.beginPath()
        ctx.arc(self.x + self.width / 2, self.y + self.height / 2, self.width / 2, 0, 2 * 3.14159)
        ctx.fill()
        ctx.fillStyle = "#000"
        ctx.beginPath()
        ctx.arc(self.x + self.width / 3, self.y + self.height / 2, 5, 0, 2 * 3.14159)
        ctx.arc(self.x + 2 * self.width / 3, self.y + self.height / 2, 5, 0, 2 * 3.14159)
        ctx.fill()

# 游戏统计类
class GameStats:
    def __init__(self, ai_setting):
        self.ai_setting = ai_setting
        self.reset_stats()
        self.game_active = False
        self.high_score = 0
    
    def reset_stats(self):
        self.ships_left = self.ai_setting.ships_limit
        self.score = 0
        self.level = 1

# 全局变量
ai_setting = Settings()
stats = GameStats(ai_setting)
canvas = None
ctx = None
ship = None
bullets = []
aliens = []
keys_pressed = {}

def create_fleet():
    global aliens
    aliens = []
    alien_width = 40
    alien_height = 30
    ship_height = 60
    available_space_x = ai_setting.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    available_space_y = ai_setting.screen_height - 3 * alien_height - ship_height
    number_aliens_y = int(available_space_y / (2 * alien_height))
    
    for row_number in range(number_aliens_y):
        for alien_number in range(number_aliens_x):
            alien_x = alien_width + 2 * alien_width * alien_number
            alien_y = alien_height + 2 * alien_height * row_number
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
    
    # 反向删除以避免索引问题
    for i in sorted(bullets_to_remove, reverse=True):
        if i < len(bullets):
            del bullets[i]
    for j in sorted(aliens_to_remove, reverse=True):
        if j < len(aliens):
            del aliens[j]
    
    if len(aliens) == 0:
        bullets = []
        ai_setting.increase_speed()
        create_fleet()
        stats.level += 1

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
            return True
    return False

def check_aliens_bottom():
    for alien in aliens:
        if alien.y + alien.height >= ai_setting.screen_height:
            return True
    return False

async def game_loop():
    global canvas, ctx, ship, bullets, aliens, keys_pressed
    window.console.log("游戏循环开始")
    
    while True:
        try:
            # 清除画布
            ctx.fillStyle = ai_setting.bg_color
            ctx.fillRect(0, 0, canvas.width, canvas.height)
            
            if stats.game_active:
                # 更新飞船
                if keys_pressed.get("ArrowRight", False):
                    ship.moving_right = True
                else:
                    ship.moving_right = False
                
                if keys_pressed.get("ArrowLeft", False):
                    ship.moving_left = True
                else:
                    ship.moving_left = False
                
                ship.update()
                
                # 更新子弹
                bullets_to_remove = []
                for i, bullet in enumerate(bullets):
                    bullet.update()
                    if bullet.y + bullet.height <= 0:
                        bullets_to_remove.append(i)
                
                for i in sorted(bullets_to_remove, reverse=True):
                    if i < len(bullets):
                        del bullets[i]
                
                # 更新外星人
                check_fleet_edges()
                for alien in aliens:
                    alien.update()
                
                # 碰撞检测
                check_bullet_alien_collisions()
                
                if check_ship_collisions() or check_aliens_bottom():
                    if stats.ships_left > 0:
                        stats.ships_left -= 1
                        bullets = []
                        aliens = []
                        create_fleet()
                        ship.center_ship()
                        await asyncio.sleep(0.5)
                    else:
                        stats.game_active = False
            
            # 绘制游戏对象
            ship.draw(ctx)
            for bullet in bullets:
                bullet.draw(ctx)
            for alien in aliens:
                alien.draw(ctx)
            
            # 显示分数和等级
            ctx.fillStyle = "#ffffff"
            ctx.font = "24px Arial"
            ctx.fillText(f"Score: {stats.score}", 10, 30)
            ctx.fillText(f"Level: {stats.level}", 10, 60)
            ctx.fillText(f"Ships: {stats.ships_left}", 10, 90)
            
            if not stats.game_active:
                ctx.fillStyle = "#3b82f6"
                ctx.font = "48px Arial"
                ctx.fillText("Press Space to Play", canvas.width / 2 - 200, canvas.height / 2)
        
        except Exception as e:
            window.console.error(f"循环错误: {e}")
        
        await asyncio.sleep(0.016)

def on_key_down(e):
    global keys_pressed, stats, ship, bullets, aliens
    keys_pressed[e.key] = True
    
    if e.key == " ":
        if not stats.game_active:
            ai_setting.initialize_dynamic_settings()
            stats.reset_stats()
            stats.game_active = True
            bullets = []
            aliens = []
            create_fleet()
            ship.center_ship()
        else:
            if len(bullets) < ai_setting.bullets_allowed:
                new_bullet = Bullet(ai_setting, ship)
                bullets.append(new_bullet)
    e.preventDefault()

def on_key_up(e):
    global keys_pressed
    keys_pressed[e.key] = False
    e.preventDefault()

async def main():
    global canvas, ctx, ship, bullets, aliens
    window.console.log("主函数开始")
    
    # 获取 Canvas 元素和 2D 上下文
    canvas = document.getElementById("gameCanvas")
    ctx = canvas.getContext("2d")
    
    # 初始化游戏对象
    ship = Ship(ai_setting, canvas)
    
    # 添加键盘事件监听
    document.addEventListener("keydown", create_proxy(on_key_down))
    document.addEventListener("keyup", create_proxy(on_key_up))
    
    # 启动游戏循环
    await game_loop()

# 启动主函数
asyncio.ensure_future(main())
