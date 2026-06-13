from graphics import Canvas
import random
import time

CANVAS_WIDTH = 750
CANVAS_HEIGHT = 600

clouds = []
CLOUD_WIDTH = 120
CLOUD_HEIGHT = 80

bucket_parts = []
BUCKET_WIDTH = 140

rain_drops = []
DROP_SIZE = 20

gold_rain_drops = []
GOLDEN_DROP_SIZE = 30

BASE_RAIN_SPEED = 5

stars = []
STAR_COLORS = ['white', 'yellow', 'khaki', 'gold', 'ghostwhite']

def main():
    canvas = setup_canvas()
    setup_world(canvas)

    score, score_text, level_text, lives, lives_text = setup_ui(canvas)

    spawn_counter = 0
    missed_drops = 0
    
    # Rain fall speed
    rain_speed = BASE_RAIN_SPEED

    rain_speed, level = game_difficulty(score)

    while True:
        handle_keys(canvas)
        twinkle_stars(canvas)

        # Increase level and rain speed based on score
        rain_speed, level = game_difficulty(score)

        # Start slow, gradually increase speed
        spawn_rate = max(35 - level * 2, 12)

        rain_fall(canvas, rain_speed)

        spawn_counter += 1

        # Regular Rain
        if spawn_counter % spawn_rate == 0:
            for _ in range(min(level, 3)):
                create_rain(canvas)

        # Gold Rain
        if spawn_counter % (spawn_rate * 2) == 0:
            create_gold_rain(canvas)

        # Scores
        score, score_text = handle_collisions(canvas, score, score_text)

        canvas.change_text(level_text, f"Level {level}")

        lives, missed_drops = cleanup(canvas, lives, lives_text, missed_drops)

        if lives <= 0:
            canvas.create_text(200, 300, "GAME OVER!!",
                               font='Segoe Print',
                               font_size=50,
                               color='mediumvioletred')
            break

        time.sleep(0.10)

####### SETUP
### CANVAS SETUP
def setup_canvas():
    canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, 'indigo')
    return canvas

### WORLD SETUP
def setup_world(canvas):
    # Clouds
    draw_cloud(canvas, 20, 85, 'darkgrey')
    draw_cloud(canvas, 170, 60, 'grey')
    draw_cloud(canvas, 320, 85, 'darkgrey')
    draw_cloud(canvas, 470, 60, 'grey')
    draw_cloud(canvas, 620, 85, 'darkgrey')

    # Bucket
    draw_bucket(canvas, 305, 480)

    # Starry Night
    for _ in range(100):
        x = random.randint(20, CANVAS_WIDTH - 20)
        y = random.randint(30, 250)

        star = draw_star(canvas, x, y, 5)
        stars.append(star)

### UI CONFIGURATIONS
def setup_ui(canvas):
    # Score
    score = 0
    global score_text
    score_text = canvas.create_text(
        60,
        25,
        f"Score: {score}",
        font = 'Segoe Print',
        font_size = 20,
        color = 'palevioletred'
    )

    # Level
    level_text = canvas.create_text(
    350,
    25,
    "Level 1",
    font_size = 22,
    font = 'Segoe Print',
    color="palevioletred"
    )
    
    # Lives
    lives = 5
    lives_text = canvas.create_text(
        580,
        25,
        '♥ ♥ ♥ ♥ ♥',
        font_size = 30,
        color = 'palevioletred'
    )

    return score, score_text, level_text, lives, lives_text

# GAME DIFFICULTY
def game_difficulty(score):
    level = score // 250 + 1
    rain_speed = 4 + level
    return rain_speed, level

# UPDATE LIVES IF RAIN ISN'T CAUGHT
def update_lives_display(canvas, lives_text, lives):
    hearts = "♥ " * lives

    if hearts == "":
        hearts = "☠️"

    canvas.change_text(lives_text, hearts)

####### CANVAS ELEMENTS & THEIR FUNCTIONALITY
### CLOUDS
def draw_cloud(canvas, x, y, color):
    cloud_bottom_start_y = y + (1/3) * CLOUD_HEIGHT
    cloud_bottom_end_y = y + CLOUD_HEIGHT
    cloud_top_start_x = x + (1/4) * CLOUD_WIDTH
    cloud_top_end_x = x + (3/4) * CLOUD_WIDTH
    # Bottom two puffs
    canvas.create_oval(
        x, 
        cloud_bottom_start_y,
        x + (3/4) * CLOUD_WIDTH,
        cloud_bottom_end_y,
        color
    )
    canvas.create_oval(
        x + (1/4) * CLOUD_WIDTH, 
        cloud_bottom_start_y,
        x + CLOUD_WIDTH,
        cloud_bottom_end_y,
        color
    )
    # Top puff
    canvas.create_oval(
        cloud_top_start_x,
        y,
        cloud_top_end_x,
        y + (2/3) * CLOUD_HEIGHT,
        color
    )
    # Add clouds to list
    clouds.append({
        "x1": x,
        "x2": x + CLOUD_WIDTH,
        "bottom_y": cloud_bottom_end_y
    })

### STARS
# DRAW STAR TO PLACE IN THE SKY
def draw_star(canvas, x, y, size):
    x = int(x)
    y = int(y)
    size = int(size)

    points = [
        x, y - size,
        x + size//3, y - size//3,
        x + size, y - size//3,
        x + size//2, y + size//4,
        x + (2*size)//3, y + size,
        x, y + size//2,
        x - (2*size)//3, y + size,
        x - size//2, y + size//4,
        x - size, y - size//3,
        x - size//3, y - size//3
    ]

    return canvas.create_polygon(*points, color=random.choice(STAR_COLORS))

# MAKE STARS TWINKLE
def twinkle_stars(canvas):
    global stars
    for star in stars[:]:
        if random.randint(1, 12) == 1:
            canvas.delete(star)

            x = random.randint(20, CANVAS_WIDTH - 20)
            y = random.randint(20, 200)

            new_star = draw_star(
                canvas,
                x,
                y,
                # Different sizes for the twinkle effect
                random.choice([3, 4, 5])
            )

            stars.remove(star)
            stars.append(new_star)

### RAIN DROPS
# REGULAR RAIN DROPS
def create_rain(canvas):
    # Choose cloud
    cloud = random.choice(clouds)

    # Makes rain fall directly from cloud
    left_x = random.randint(int(cloud["x1"]), int(cloud["x2"]))
    top_y = cloud["bottom_y"]
    right_x = left_x + DROP_SIZE
    bottom_y = top_y + DROP_SIZE

    # Random colour for rain drops
    color = random_rain_drop_color()

    # Create drop
    drop = canvas.create_oval(left_x, top_y, right_x, bottom_y, color)

    # Add drop to rain_drops list
    rain_drops.append(drop)

# GOLDEN RAIN DROPS
def create_gold_rain(canvas):
    # Make occurrence of gold drop rare. 1/12 chance
    chance = random.randint(1, 12)
    if chance == 1:
        # Choose cloud
        cloud = random.choice(clouds)

        # Makes rain fall directly from cloud
        left_x = random.randint(int(cloud["x1"]), int(cloud["x2"]))
        top_y = cloud["bottom_y"]
        right_x = left_x + GOLDEN_DROP_SIZE
        bottom_y = top_y + GOLDEN_DROP_SIZE

        # Create gold_drop
        gold_drop = canvas.create_oval(left_x, top_y, right_x, bottom_y, 'gold')

        # Add drop to gold_rain_drops list
        gold_rain_drops.append(gold_drop)

# RANDOM RAIN DROP COLORS
def random_rain_drop_color():
    colors = ['skyblue', 'lightskyblue', 'powderblue', 'lightblue', 'lightsteelblue']
    return random.choice(colors)

# MAKE RAIN FALL
def rain_fall(canvas, speed):
    for drop in rain_drops:
        canvas.move(drop, 0, speed)

    for gold_drop in gold_rain_drops:
        canvas.move(gold_drop, 0, speed)

# CLEAN UP DROPS THAT FALL OUTSIDE CANVAS
def cleanup(canvas, lives, lives_text, missed_drops):
    for drop in rain_drops[:]:
        if canvas.get_top_y(drop) > CANVAS_HEIGHT:
            canvas.delete(drop)
            rain_drops.remove(drop)

            # Miss 2 drops to lose a life
            missed_drops += 1
            if missed_drops >= 2:
                lives -= 1
                missed_drops = 0
            
            update_lives_display(canvas, lives_text, lives)

    for gold_drop in gold_rain_drops[:]:
        if canvas.get_top_y(gold_drop) > CANVAS_HEIGHT:
            canvas.delete(gold_drop)
            gold_rain_drops.remove(gold_drop)

            # Miss 2 drops to lose a life
            missed_drops += 1
            if missed_drops >= 2:
                lives -= 1
                missed_drops = 0
            
            update_lives_display(canvas, lives_text, lives)

    return lives, missed_drops

### BUCKET
# BUCKET
def draw_bucket(canvas, x, y):
    global bucket_parts

    # Body
    body = canvas.create_rectangle(x, y, x + BUCKET_WIDTH, CANVAS_HEIGHT, 'mediumorchid', 'darkmagenta')
    # Top rim
    top = canvas.create_oval(x, y - 20, x + BUCKET_WIDTH, y + 20, 'thistle')

    bucket_parts = [body, top]

# MAKE BUCKET MOVE
def move_bucket(canvas, dx):
    body = bucket_parts[0]

    left_x = canvas.get_left_x(body)
    right_x = left_x + BUCKET_WIDTH

    # Moving left
    if dx < 0 and left_x <= 0:
        return

    # Moving right
    if dx > 0 and right_x >= CANVAS_WIDTH:
        return

    for part in bucket_parts:
        canvas.move(part, dx, 0)

# ARROW KEYS FOR USER TO CONTROL BUCKET MOVEMENT
def handle_keys(canvas):
    keys = canvas.get_new_key_presses()
    # print(keys)  # DEBUG LINE

    for key in keys:
        if key == "LEFT_ARROW":
            move_bucket(canvas, -125)
        elif key == "RIGHT_ARROW":
            move_bucket(canvas, 125)

####### COLLISSIONS
# HANDLE COLLISSIONS SCORING FOR DIFFERENT DROPS
def handle_collisions(canvas, score, score_text):
    # Collision check for regular drops
    for drop in rain_drops[:]:
        if is_collision(canvas, drop, DROP_SIZE):
            canvas.delete(drop)
            rain_drops.remove(drop)

            score += 50
            canvas.change_text(score_text, f"Score: {score}")

    # Collision check for gold drops
    for gold_drop in gold_rain_drops[:]:
        if is_collision(canvas, gold_drop, GOLDEN_DROP_SIZE):
            canvas.delete(gold_drop)
            gold_rain_drops.remove(gold_drop)

            # Gold bonus
            score += 200
            canvas.change_text(score_text, f"Score: {score}")
    
    return score, score_text

# CHECK FOR COLLISSION BETWEEN RAINDROPS AND BUCKET AND MAKE DROP 'DISAPPEAR' INTO BUCKET
def is_collision(canvas, drop, size):
    drop_x1 = canvas.get_left_x(drop)
    drop_y1 = canvas.get_top_y(drop)
    drop_x2 = drop_x1 + size
    drop_y2 = drop_y1 + size

    bucket = bucket_parts[0]
    bx1 = canvas.get_left_x(bucket)
    by1 = canvas.get_top_y(bucket)
    bx2 = bx1 + BUCKET_WIDTH
    by2 = CANVAS_HEIGHT

    return (
        drop_x1 < bx2 and
        drop_x2 > bx1 and
        drop_y1 < by2 and
        drop_y2 > by1
    )

if __name__ == '__main__':
    main()