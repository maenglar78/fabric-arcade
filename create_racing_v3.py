import json
import uuid

# Game HTML code
game_code = r'''from IPython.display import display, HTML
import uuid

session_id = str(uuid.uuid4())

game_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
#game-wrapper {{ 
    width: 100%; display: flex; flex-direction: column; align-items: center;
    font-family: 'Segoe UI', Arial, sans-serif;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    padding: 20px; border-radius: 15px;
}}
#game-container {{ 
    position: relative; width: 600px; height: 500px;
    background: #2d3436; border-radius: 10px; overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}}
canvas {{ display: block; }}
#hud {{
    position: absolute; top: 10px; left: 10px; right: 10px;
    display: flex; justify-content: space-between;
    color: white; font-size: 14px; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); z-index: 10;
}}
#hud-left, #hud-right {{ background: rgba(0,0,0,0.6); padding: 8px 12px; border-radius: 8px; }}
#progress-bar {{
    position: absolute; right: 10px; top: 60px; bottom: 60px; width: 30px;
    background: rgba(0,0,0,0.6); border-radius: 15px; z-index: 10;
}}
#progress-fill {{
    position: absolute; bottom: 0; width: 100%;
    background: linear-gradient(to top, #00b894, #00cec9);
    border-radius: 15px; transition: height 0.1s;
}}
#progress-car {{ position: absolute; right: -5px; width: 40px; text-align: center; font-size: 20px; transition: bottom 0.1s; }}
#start-btn {{
    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
    padding: 20px 50px; font-size: 28px;
    background: linear-gradient(135deg, #e74c3c, #c0392b);
    color: white; border: none; border-radius: 15px; cursor: pointer; z-index: 100;
    box-shadow: 0 8px 25px rgba(231,76,60,0.4); transition: all 0.3s;
}}
#start-btn:hover {{ transform: translate(-50%, -50%) scale(1.1); }}
#leaderboard {{ margin-top: 15px; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; width: 600px; }}
#leaderboard h3 {{ color: #ffd700; margin-bottom: 10px; }}
#leaderboard-list {{ color: white; list-style: none; }}
#leaderboard-list li {{ padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }}
.multiplier {{ color: #ffd700; font-weight: bold; }}
</style>
</head>
<body>
<div id="game-wrapper" tabindex="0">
    <div id="game-container">
        <canvas id="gameCanvas" width="600" height="500"></canvas>
        <div id="hud">
            <div id="hud-left">
                <div>🏎️ <span id="level-name">Lakehouse Lane</span></div>
                <div>Level: <span id="level">1</span>/10</div>
            </div>
            <div id="hud-right">
                <div>Score: <span id="score">0</span></div>
                <div>Multiplier: <span id="multiplier" class="multiplier">x1</span></div>
                <div>Target: <span id="target">1000</span></div>
            </div>
        </div>
        <div id="progress-bar">
            <div id="progress-fill" style="height: 0%"></div>
            <div id="progress-car">🏎️</div>
        </div>
        <button id="start-btn" onclick="startGame()">▶ START RACE</button>
    </div>
    <div id="leaderboard"><h3>🏆 Leaderboard</h3><ol id="leaderboard-list"></ol></div>
</div>

<script>
const LEVELS = [
    {{ name: "Lakehouse Lane", target: 1000, dataPoints: 8, bugs: 4, speed: 3, color: "#3498db" }},
    {{ name: "Pipeline Pass", target: 2000, dataPoints: 10, bugs: 6, speed: 3.5, color: "#9b59b6" }},
    {{ name: "Warehouse Way", target: 3500, dataPoints: 12, bugs: 8, speed: 4, color: "#1abc9c" }},
    {{ name: "Dataflow Drive", target: 5000, dataPoints: 14, bugs: 10, speed: 4.5, color: "#e67e22" }},
    {{ name: "Notebook Narrows", target: 7000, dataPoints: 16, bugs: 14, speed: 5, color: "#e74c3c" }},
    {{ name: "Eventhouse Express", target: 9500, dataPoints: 18, bugs: 18, speed: 5.5, color: "#2ecc71" }},
    {{ name: "Shortcut Sprint", target: 12500, dataPoints: 20, bugs: 22, speed: 6, color: "#f39c12" }},
    {{ name: "Capacity Canyon", target: 16000, dataPoints: 22, bugs: 26, speed: 6.5, color: "#8e44ad" }},
    {{ name: "OneLake Overdrive", target: 20000, dataPoints: 24, bugs: 30, speed: 7, color: "#00cec9" }},
    {{ name: "Spark Summit", target: 25000, dataPoints: 28, bugs: 35, speed: 8, color: "#fd79a8" }}
];

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;

let gameRunning = false, currentLevel = 0, score = 0, multiplier = 1;
let consecutiveStars = 0, distance = 0, trackLength = 3000;
let car = {{ x: W/2, y: H - 80, width: 40, height: 60, speed: 0, maxSpeed: 8 }};
let dataPoints = [], bugs = [], roadOffset = 0, keys = {{}};

const sessionId = "{session_id}";
const playerName = "{PLAYER_NAME}";

function initLevel() {{
    const level = LEVELS[currentLevel];
    distance = 0;
    trackLength = 2000 + currentLevel * 500;
    car.x = W/2;
    car.speed = level.speed;
    dataPoints = [];
    bugs = [];
    
    for (let i = 0; i < level.dataPoints; i++) {{
        dataPoints.push({{ x: 100 + Math.random() * (W - 250), y: -200 - (i * (trackLength / level.dataPoints)), collected: false }});
    }}
    for (let i = 0; i < level.bugs; i++) {{
        bugs.push({{ x: 100 + Math.random() * (W - 250), y: -300 - (i * (trackLength / level.bugs)), hit: false }});
    }}
    updateHUD();
}}

function updateHUD() {{
    const level = LEVELS[currentLevel];
    document.getElementById('level').textContent = currentLevel + 1;
    document.getElementById('level-name').textContent = level.name;
    document.getElementById('score').textContent = score;
    document.getElementById('multiplier').textContent = 'x' + multiplier;
    document.getElementById('target').textContent = level.target;
    const progress = Math.min(100, (distance / trackLength) * 100);
    document.getElementById('progress-fill').style.height = progress + '%';
    document.getElementById('progress-car').style.bottom = (progress * 0.9) + '%';
}}

function drawRoad() {{
    const level = LEVELS[currentLevel];
    const grad = ctx.createLinearGradient(0, 0, 0, H);
    grad.addColorStop(0, '#1a1a2e'); grad.addColorStop(1, '#16213e');
    ctx.fillStyle = grad; ctx.fillRect(0, 0, W, H);
    
    ctx.fillStyle = '#2d3436'; ctx.fillRect(80, 0, W - 160, H);
    ctx.fillStyle = level.color; ctx.fillRect(75, 0, 8, H); ctx.fillRect(W - 83, 0, 8, H);
    
    ctx.strokeStyle = 'rgba(255,255,255,0.3)'; ctx.setLineDash([40, 30]); ctx.lineWidth = 3;
    for (let i = 0; i < 3; i++) {{
        ctx.beginPath(); ctx.moveTo(180 + i * 120, (roadOffset % 70) - 70);
        for (let y = (roadOffset % 70) - 70; y < H + 70; y += 70) ctx.lineTo(180 + i * 120, y);
        ctx.stroke();
    }}
    ctx.setLineDash([]);
    
    if (distance < 100) {{
        ctx.fillStyle = '#2ecc71'; ctx.fillRect(80, H - 50 - distance, W - 160, 10);
        ctx.fillStyle = 'white'; ctx.font = 'bold 16px Arial'; ctx.fillText('START', W/2 - 30, H - 35 - distance);
    }}
    
    if (distance > trackLength - H) {{
        const finishY = H - (distance - (trackLength - H));
        if (finishY > 0 && finishY < H) {{
            ctx.fillStyle = '#ffd700'; ctx.fillRect(80, finishY, W - 160, 15);
            for (let i = 0; i < 20; i++) {{ ctx.fillStyle = i % 2 === 0 ? 'black' : 'white'; ctx.fillRect(80 + i * 22, finishY, 22, 15); }}
            ctx.fillStyle = 'white'; ctx.font = 'bold 18px Arial'; ctx.fillText('🏁 FINISH 🏁', W/2 - 50, finishY - 10);
        }}
    }}
}}

function drawCar() {{
    ctx.save(); ctx.translate(car.x, car.y);
    ctx.fillStyle = '#e74c3c'; ctx.beginPath(); ctx.roundRect(-car.width/2, -car.height/2, car.width, car.height, 8); ctx.fill();
    ctx.fillStyle = '#74b9ff'; ctx.fillRect(-15, -car.height/2 + 10, 30, 15);
    ctx.fillStyle = '#2d3436';
    ctx.fillRect(-car.width/2 - 5, -car.height/2 + 5, 8, 18); ctx.fillRect(car.width/2 - 3, -car.height/2 + 5, 8, 18);
    ctx.fillRect(-car.width/2 - 5, car.height/2 - 23, 8, 18); ctx.fillRect(car.width/2 - 3, car.height/2 - 23, 8, 18);
    ctx.restore();
}}

function drawDataPoints() {{
    dataPoints.forEach(dp => {{
        if (!dp.collected) {{
            const screenY = dp.y + distance;
            if (screenY > -30 && screenY < H + 30) {{ ctx.font = '28px Arial'; ctx.fillText('⭐', dp.x - 14, screenY + 10); }}
        }}
    }});
}}

function drawBugs() {{
    bugs.forEach(bug => {{
        if (!bug.hit) {{
            const screenY = bug.y + distance;
            if (screenY > -30 && screenY < H + 30) {{ ctx.font = '26px Arial'; ctx.fillText('🐛', bug.x - 13, screenY + 8); }}
        }}
    }});
}}

function checkCollisions() {{
    dataPoints.forEach(dp => {{
        if (!dp.collected) {{
            const screenY = dp.y + distance;
            if (Math.abs(car.x - dp.x) < 35 && Math.abs(car.y - screenY) < 40) {{
                dp.collected = true; consecutiveStars++;
                multiplier = Math.min(10, Math.floor(consecutiveStars / 2) + 1);
                score += 100 * multiplier; updateHUD();
            }}
        }}
    }});
    
    bugs.forEach(bug => {{
        if (!bug.hit) {{
            const screenY = bug.y + distance;
            if (Math.abs(car.x - bug.x) < 30 && Math.abs(car.y - screenY) < 35) {{
                bug.hit = true; score = Math.max(0, score - 50);
                consecutiveStars = 0; multiplier = 1; car.speed = Math.max(2, car.speed - 1);
                updateHUD(); canvas.style.boxShadow = '0 0 30px #e74c3c';
                setTimeout(() => canvas.style.boxShadow = '', 200);
            }}
        }}
    }});
}}

function checkFinish() {{
    if (distance >= trackLength) {{
        score += 1000;
        const level = LEVELS[currentLevel];
        
        if (score >= level.target) {{
            if (currentLevel < LEVELS.length - 1) {{
                currentLevel++;
                showMessage('🎉 Level Complete! Next: ' + LEVELS[currentLevel].name);
                setTimeout(() => initLevel(), 2000);
            }} else {{
                gameRunning = false;
                showMessage('🏆 CHAMPION! You beat all 10 tracks!');
                saveScore();
                document.getElementById('start-btn').style.display = 'block';
                document.getElementById('start-btn').textContent = '🔄 PLAY AGAIN';
            }}
        }} else {{
            showMessage('❌ Need ' + level.target + ' points! Try again.');
            setTimeout(() => initLevel(), 2000);
        }}
    }}
}}

function showMessage(text) {{
    ctx.fillStyle = 'rgba(0,0,0,0.8)'; ctx.fillRect(0, H/2 - 50, W, 100);
    ctx.fillStyle = 'white'; ctx.font = 'bold 24px Arial'; ctx.textAlign = 'center';
    ctx.fillText(text, W/2, H/2 + 8); ctx.textAlign = 'left';
}}

function update() {{
    if (!gameRunning) return;
    if (keys['ArrowLeft'] || keys['KeyA']) car.x = Math.max(100, car.x - 6);
    if (keys['ArrowRight'] || keys['KeyD']) car.x = Math.min(W - 100, car.x + 6);
    if (keys['ArrowUp'] || keys['KeyW']) car.speed = Math.min(car.maxSpeed, car.speed + 0.2);
    if (keys['ArrowDown'] || keys['KeyS']) car.speed = Math.max(2, car.speed - 0.3);
    distance += car.speed; roadOffset += car.speed;
    checkCollisions(); checkFinish(); updateHUD();
}}

function render() {{ drawRoad(); drawDataPoints(); drawBugs(); drawCar(); }}
function gameLoop() {{ update(); render(); if (gameRunning) requestAnimationFrame(gameLoop); }}

function startGame() {{
    document.getElementById('start-btn').style.display = 'none';
    document.getElementById('game-wrapper').focus();
    currentLevel = 0; score = 0; multiplier = 1; consecutiveStars = 0;
    gameRunning = true; initLevel(); gameLoop();
}}

function saveScore() {{
    const scores = JSON.parse(localStorage.getItem('fabricRacingScores') || '[]');
    scores.push({{ name: playerName, score: score, level: currentLevel + 1, date: new Date().toLocaleDateString() }});
    scores.sort((a, b) => b.score - a.score);
    localStorage.setItem('fabricRacingScores', JSON.stringify(scores.slice(0, 10)));
    loadLeaderboard();
}}

function loadLeaderboard() {{
    const scores = JSON.parse(localStorage.getItem('fabricRacingScores') || '[]');
    const list = document.getElementById('leaderboard-list');
    list.innerHTML = scores.length ? scores.map((s, i) => '<li>' + (i+1) + '. ' + s.name + ' - ' + s.score + ' pts (Level ' + s.level + ')</li>').join('') : '<li>No scores yet!</li>';
}}

document.addEventListener('keydown', e => {{ keys[e.code] = true; if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code)) e.preventDefault(); }});
document.addEventListener('keyup', e => keys[e.code] = false);

loadLeaderboard(); render();
</script>
</body>
</html>
"""

display(HTML(game_html))'''

# Create notebook structure
notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "id": str(uuid.uuid4())[:8],
            "metadata": {},
            "source": [
                "# 🏎️ Fabric Racing Game - Data Pipeline Edition\n",
                "\n",
                "Race through **10 Fabric-themed tracks**, collect ⭐ **data points**, avoid 🐛 **bugs**, and reach the finish line!\n",
                "\n",
                "## 🎮 Controls\n",
                "- **⬅️ Arrow Left / A**: Steer Left\n",
                "- **➡️ Arrow Right / D**: Steer Right\n",
                "- **⬆️ Arrow Up / W**: Speed Boost\n",
                "- **⬇️ Arrow Down / S**: Brake\n",
                "\n",
                "## 📊 Scoring\n",
                "- ⭐ **Data Point**: +100 points × multiplier\n",
                "- 🔥 **Consecutive Multiplier**: x2, x3... up to x10!\n",
                "- 🐛 **Bug Hit**: -50 points + speed penalty\n",
                "- 🏁 **Finish Bonus**: +1000 points\n",
                "\n",
                "## 🏆 Fabric Track Names\n",
                "| Level | Track | Target | Data Points | Bugs |\n",
                "|-------|-------|--------|-------------|------|\n",
                "| 1 | Lakehouse Lane | 1,000 | 8 | 4 |\n",
                "| 2 | Pipeline Pass | 2,000 | 10 | 6 |\n",
                "| 3 | Warehouse Way | 3,500 | 12 | 8 |\n",
                "| 4 | Dataflow Drive | 5,000 | 14 | 10 |\n",
                "| 5 | Notebook Narrows | 7,000 | 16 | 14 |\n",
                "| 6 | Eventhouse Express | 9,500 | 18 | 18 |\n",
                "| 7 | Shortcut Sprint | 12,500 | 20 | 22 |\n",
                "| 8 | Capacity Canyon | 16,000 | 22 | 26 |\n",
                "| 9 | OneLake Overdrive | 20,000 | 24 | 30 |\n",
                "| 10 | Spark Summit | 25,000 | 28 | 35 |"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "id": str(uuid.uuid4())[:8],
            "metadata": {},
            "outputs": [],
            "source": [
                "# Configuration - Update these values!\n",
                "EVENTSTREAM_ENDPOINT = \"<YOUR_CUSTOM_ENDPOINT_URL>\"\n",
                "PLAYER_NAME = \"Player1\"  # Your name for the leaderboard"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "id": str(uuid.uuid4())[:8],
            "metadata": {},
            "outputs": [],
            "source": []  # Will be filled below
        }
    ],
    "metadata": {
        "language_info": {
            "name": "python",
            "version": "3.10"
        },
        "kernelspec": {
            "name": "python3",
            "display_name": "Python 3"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

# Split game code into lines with proper newlines
lines = game_code.split('\n')
source_lines = [line + '\n' for line in lines[:-1]] + [lines[-1]]
notebook["cells"][2]["source"] = source_lines

# Save notebook
with open('catalog/fabric-racing-game/notebooks/racing_game_v2.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)

print("✅ Notebook updated with vertical scrolling game!")
print("\nFabric-themed Track Names:")
tracks = [
    "Lakehouse Lane", "Pipeline Pass", "Warehouse Way", "Dataflow Drive",
    "Notebook Narrows", "Eventhouse Express", "Shortcut Sprint",
    "Capacity Canyon", "OneLake Overdrive", "Spark Summit"
]
for i, name in enumerate(tracks, 1):
    print(f"  {i}. {name}")
