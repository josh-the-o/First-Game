from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from ursina.prefabs.health_bar import HealthBar
from ursina.prefabs.ursfx import ursfx


app = Ursina()
random.seed(0)
Entity.default_shader = lit_with_shadows_shader

# Game Variables
level = 1
damage = 10
mob_health = 50
mob_size = 1
mob_speed = 1.5
mobs = []
gun_colors = [color.red, color.blue, color.green, color.orange, color.random_color()]
player_health = 100

# Player Setup
player = FirstPersonController(speed=20)  # Fast player speed
player.cursor.visible = False
player.gun = Entity(
    model="cube",
    color=color.red,
    scale=(0.3, 0.2, 0.5),
    position=(0.5, -0.2, 0.5),
    parent=player,
)
player.gun.muzzle_flash = Entity(
    parent=player.gun, z=0.5, world_scale=0.2, model="sphere", color=color.yellow, enabled=False
)
player.gun.on_cooldown = False
player.health_bar = Entity(
    model="quad", parent=camera.ui, color=color.red, scale=(0.3, 0.03), position=(-0.7, 0.45)
)

crosshair = Entity(model="quad", color=color.white, scale=0.01, parent=camera.ui)

# Environment Setup
Sky(texture="sky_default")
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))

ground = Entity(model="plane", texture="brick", collider="mesh", scale=(500, 1, 500), color=color.dark_gray)

# Wall Setup
walls = []
for x in range(-25, 30, 10):
    for z in range(-25, 30, 10):
        if random.random() > 0.6:  # Randomly create walls
            wall = Entity(
                model="cube",
                scale=(8, 8, 1),
                position=(x, 4, z),
                color=color.gray,
                collider="box",
            )
            walls.append(wall)

# Mob Spawning
def spawn_mob():
    global mob_health, mob_size, level
    mob_color = gun_colors[(level - 1) % len(gun_colors)]
    mob = Entity(
        model="cube",
        color=mob_color,
        scale=mob_size,
        collider="box",
        position=(random.uniform(-10, 10), 1, random.uniform(-10, 10)),
        health=mob_health,
    )
    mob.health_bar = Entity(
        parent=mob, model="cube", color=color.red, world_scale=(1.5, 0.1, 0.1), y=1.2
    )
    mobs.append(mob)

# Shooting Logic
def shoot():
    if not player.gun.on_cooldown:
        player.gun.on_cooldown = True
        bullet = Entity(
            model="sphere",
            color=color.yellow,
            scale=0.2,
            position=player.camera_pivot.world_position + Vec3(0, 0, 0) + camera.forward * 0.5,
            collider="box",
        )
        bullet.animate_position(bullet.position + camera.forward * 50, duration=1, curve=curve.linear)

        def check_collision():
            for mob in mobs:
                if bullet.intersects(mob).hit:
                    mob.health -= damage
                    mob.health_bar.world_scale_x = max(0, mob.health / mob_health)
                    if mob.health <= 0:
                        mobs.remove(mob)
                        destroy(mob)
                        destroy(mob.health_bar)
            destroy(bullet)

        invoke(check_collision, delay=0.1)
        invoke(setattr, player.gun, "on_cooldown", False, delay=0.2)

# Next Wave
def next_wave():
    global level, mob_health, mob_size, damage, mob_speed
    if not mobs:  # If all mobs are cleared
        level += 1
        mob_health += 20
        mob_size += 0.2
        mob_speed += 0.3  # Increase mob speed
        damage += 5
        player.gun.color = gun_colors[(level - 1) % len(gun_colors)]  # Change gun color
        for _ in range(level * 3):
            spawn_mob()

# Update Function
def update():
    global player_health
    if held_keys["left mouse"]:
        shoot()

    for mob in mobs:
        mob.look_at_2d(player.position, "y")
        mob.position += mob.forward * time.dt * mob_speed  # Mob speed increases per level
        if distance(mob.position, player.position) < 2:
            player_health -= 0.5  # Slower damage rate
            player.health_bar.scale_x = max(0, player_health / 100)
            if player_health <= 0:
                print("Game Over!")
                application.quit()

    next_wave()

# Spawn Initial Mobs
for _ in range(level * 3):
    spawn_mob()

app.run()
