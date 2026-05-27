import json
import uuid

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
    position: absolute; top: 10px; left: 10px; right: 50px;
    display: flex; justify-content: space-between;
    color: white; font-size: 14px; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); z-index: 10;
}}
#hud-left, #hud-right {{ background: rgba(0,0,0,0.7); padding: 10px 14px; border-radius: 8px; }}
#progress-bar {{
    position: absolute; right: 15px; top: 80px; bottom: 80px; width: 25px;
    background: rgba(0,0,0,0.7); border-radius: 12px; z-index: 10;
    border: 2px solid #444;
}}
#progress-fill {{
    position: absolute; bottom: 0; width: 100%;
    background: linear-gradient(to top, #00b894, #55efc4);
    border-radius: 10px; transition: height 0.15s;
}}
#progress-car {{ position: absolute; left: -8px; width: 40px; text-align: center; font-size: 18px; transition: bottom 0.15s; }}
#progress-start {{ position: absolute; bottom: -25px; width: 100%; text-align: center; font-size: 10px; color: #0f0; }}
#progress-finish {{ position: absolute; top: -25px; width: 100%; text-align: center; font-size: 10px; color: #ffd700; }}
#start-btn {{
    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
    padding: 25px 60px; font-size: 32px;
    background: linear-gradient(135deg, #00b894, #00a085);
    color: white; border: none; border-radius: 20px; cursor: pointer; z-index: 100;
    box-shadow: 0 8px 25px rgba(0,184,148,0.5); transition: all 0.3s;
}}
#start-btn:hover {{ transform: translate(-50%, -50%) scale(1.1); }}
#level-info {{
    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
    background: rgba(0,0,0,0.9); padding: 30px 50px; border-radius: 15px;
    color: white; text-align: center; z-index: 90; display: none;
}}
#level-info h2 {{ color: #ffd700; margin-bottom: 15px; }}
#level-info p {{ margin: 8px 0; }}
#leaderboard {{ margin-top: 15px; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; width: 600px; }}
#leaderboard h3 {{ color: #ffd700; margin-bottom: 10px; }}
#leaderboard-list {{ color: white; list-style: none; }}
#leaderboard-list li {{ padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }}
.multiplier {{ color: #ffd700; font-weight: bold; }}
.score-good {{ color: #00ff00; }}
.score-bad {{ color: #ff6b6b; }}
</style>
</head>
<body>
<div id="game-wrapper" tabindex="0">
    <div id="game-container">
        <canvas id="gameCanvas" width="600" height="500"></canvas>
        <div id="hud">
            <div id="hud-left">
                <div style="font-size:16px; color:#ffd700;">🏎️ <span id="level-name">Lakehouse Lane</span></div>
                <div>Level: <span id="level">1</span>/10</div>
                <div>Distance: <span id="distance">0</span>m</div>
            </div>
            <div id="hud-right">
                <div style="font-size:18px;">Score: <span id="score">0</span></div>
                <div>Multiplier: <span id="multiplier" class="multiplier">x1</span></div>
                <div>Target: <span id="target" style="color:#ffd700;">500</span></div>
            </div>
        </div>
        <div id="progress-bar">
            <div id="progress-fill" style="height: 0%"></div>
            <div id="progress-car">🏎️</div>
            <div id="progress-start">START</div>
            <div id="progress-finish">🏁</div>
        </div>
        <button id="start-btn" onclick="startGame()">▶ START</button>
        <div id="level-info">
            <h2 id="level-title">Level Complete!</h2>
            <p id="level-message"></p>
            <button onclick="continueGame()" style="margin-top:15px; padding:12px 30px; font-size:18px; background:#00b894; color:white; border:none; border-radius:10px; cursor:pointer;">Continue</button>
        </div>
    </div>
    <div id="leaderboard"><h3>🏆 Best Scores</h3><ol id="leaderboard-list"></ol></div>
</div>

<script>
const LEVELS = [
    {{ name: "Lakehouse Lane", target: 500, stars: 12, bugs: 5, length: 1500, speed: 4, color: "#3498db" }},
    {{ name: "Pipeline Pass", target: 800, stars: 14, bugs: 7, length: 1800, speed: 4.5, color: "#9b59b6" }},
    {{ name: "Warehouse Way", target: 1200, stars: 16, bugs: 9, length: 2000, speed: 5, color: "#1abc9c" }},
    {{ name: "Dataflow Drive", target: 1600, stars: 18, bugs: 11, length: 2200, speed: 5.5, color: "#e67e22" }},
    {{ name: "Notebook Narrows", target: 2000, stars: 20, bugs: 14, length: 2500, speed: 6, color: "#e74c3c" }},
    {{ name: "Eventhouse Express", target: 2500, stars: 22, bugs: 17, length: 2800, speed: 6.5, color: "#2ecc71" }},
    {{ name: "Shortcut Sprint", target: 3000, stars: 24, bugs: 20, length: 3000, speed: 7, color: "#f39c12" }},
    {{ name: "Capacity Canyon", target: 3500, stars: 26, bugs: 24, length: 3300, speed: 7.5, color: "#8e44ad" }},
    {{ name: "OneLake Overdrive", target: 4000, stars: 28, bugs: 28, length: 3600, speed: 8, color: "#00cec9" }},
    {{ name: "Spark Summit", target: 5000, stars: 32, bugs: 32, length: 4000, speed: 9, color: "#fd79a8" }}
];

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;

let gameRunning = false, currentLevel = 0, levelScore = 0, totalScore = 0, multiplier = 1;
let consecutiveStars = 0, distance = 0, raceFinished = false;
let car = {{ x: W/2, y: H - 80, width: 40, height: 60, speed: 0 }};
let stars = [], bugs = [], roadOffset = 0, keys = {{}};

const sessionId = "{session_id}";
const playerName = "{PLAYER_NAME}";

function initLevel() {{
    const level = LEVELS[currentLevel];
    distance = 0;
    levelScore = 0;
    multiplier = 1;
    consecutiveStars = 0;
    raceFinished = false;
    car.x = W/2;
    car.speed = level.speed;
    stars = [];
    bugs = [];
    
    // Spread stars evenly along track (not at start or end)
    const starSpacing = (level.length - 400) / level.stars;
    for (let i = 0; i < level.stars; i++) {{
        stars.push({{
            x: 120 + Math.random() * (W - 290),
            y: -(200 + i * starSpacing + Math.random() * 50),
            collected: false
        }});
    }}
    
    // Spread bugs evenly
    const bugSpacing = (level.length - 400) / level.bugs;
    for (let i = 0; i < level.bugs; i++) {{
        bugs.push({{
            x: 120 + Math.random() * (W - 290),
            y: -(250 + i * bugSpacing + Math.random() * 80),
            hit: false
        }});
    }}
    
    document.getElementById('level-info').style.display = 'none';
    updateHUD();
}}

function updateHUD() {{
    const level = LEVELS[currentLevel];
    document.getElementById('level').textContent = currentLevel + 1;
    document.getElementById('level-name').textContent = level.name;
    document.getElementById('score').textContent = levelScore;
    document.getElementById('score').className = levelScore >= level.target ? 'score-good' : '';
    document.getElementById('multiplier').textContent = 'x' + multiplier;
    document.getElementById('target').textContent = level.target;
    document.getElementById('distance').textContent = Math.floor(distance);
    
    const progress = Math.min(100, (distance / level.length) * 100);
    document.getElementById('progress-fill').style.height = progress + '%';
    document.getElementById('progress-car').style.bottom = 'calc(' + progress + '% - 10px)';
}}

function drawRoad() {{
    const level = LEVELS[currentLevel];
    
    // Sky gradient
    const grad = ctx.createLinearGradient(0, 0, 0, H);
    grad.addColorStop(0, '#0f0f23');
    grad.addColorStop(1, '#1a1a3e');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);
    
    // Road
    ctx.fillStyle = '#2d3436';
    ctx.fillRect(100, 0, W - 200, H);
    
    // Road edges
    ctx.fillStyle = level.color;
    ctx.fillRect(95, 0, 8, H);
    ctx.fillRect(W - 103, 0, 8, H);
    
    // Center line (dashed, moving)
    ctx.strokeStyle = 'rgba(255,255,255,0.4)';
    ctx.setLineDash([40, 25]);
    ctx.lineWidth = 4;
    ctx.beginPath();
    const offset = roadOffset % 65;
    for (let y = offset - 65; y < H + 65; y += 65) {{
        ctx.moveTo(W/2, y);
        ctx.lineTo(W/2, y + 40);
    }}
    ctx.stroke();
    ctx.setLineDash([]);
    
    // START line at beginning
    if (distance < 150) {{
        const startY = H - 30 + distance;
        if (startY > 0 && startY < H + 50) {{
            ctx.fillStyle = '#2ecc71';
            ctx.fillRect(100, startY, W - 200, 12);
            ctx.fillStyle = 'white';
            ctx.font = 'bold 20px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('🚦 START 🚦', W/2, startY - 10);
        }}
    }}
    
    // FINISH line
    const finishY = H - (distance - (LEVELS[currentLevel].length - 100));
    if (finishY > -50 && finishY < H + 50) {{
        // Checkered pattern
        const checkerSize = 20;
        for (let x = 100; x < W - 100; x += checkerSize) {{
            for (let row = 0; row < 2; row++) {{
                ctx.fillStyle = ((x / checkerSize) + row) % 2 === 0 ? '#fff' : '#000';
                ctx.fillRect(x, finishY + row * checkerSize, checkerSize, checkerSize);
            }}
        }}
        ctx.fillStyle = '#ffd700';
        ctx.font = 'bold 22px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('🏁 FINISH 🏁', W/2, finishY - 15);
    }}
    ctx.textAlign = 'left';
}}

function drawCar() {{
    ctx.save();
    ctx.translate(car.x, car.y);
    
    // Shadow
    ctx.fillStyle = 'rgba(0,0,0,0.3)';
    ctx.beginPath();
    ctx.ellipse(0, car.height/2 + 5, car.width/2 + 5, 10, 0, 0, Math.PI * 2);
    ctx.fill();
    
    // Car body
    ctx.fillStyle = '#e74c3c';
    ctx.beginPath();
    ctx.roundRect(-car.width/2, -car.height/2, car.width, car.height, 8);
    ctx.fill();
    
    // Windshield
    ctx.fillStyle = '#74b9ff';
    ctx.fillRect(-14, -car.height/2 + 8, 28, 16);
    
    // Racing stripe
    ctx.fillStyle = '#fff';
    ctx.fillRect(-3, -car.height/2, 6, car.height);
    
    // Wheels
    ctx.fillStyle = '#222';
    ctx.fillRect(-car.width/2 - 4, -car.height/2 + 8, 6, 16);
    ctx.fillRect(car.width/2 - 2, -car.height/2 + 8, 6, 16);
    ctx.fillRect(-car.width/2 - 4, car.height/2 - 24, 6, 16);
    ctx.fillRect(car.width/2 - 2, car.height/2 - 24, 6, 16);
    
    ctx.restore();
}}

function drawStars() {{
    stars.forEach(star => {{
        if (!star.collected) {{
            const screenY = star.y + distance;
            if (screenY > -40 && screenY < H + 40) {{
                ctx.font = '32px Arial';
                ctx.fillText('⭐', star.x - 16, screenY + 12);
            }}
        }}
    }});
}}

function drawBugs() {{
    bugs.forEach(bug => {{
        if (!bug.hit) {{
            const screenY = bug.y + distance;
            if (screenY > -40 && screenY < H + 40) {{
                ctx.font = '30px Arial';
                ctx.fillText('🐛', bug.x - 15, screenY + 10);
            }}
        }}
    }});
}}

function checkCollisions() {{
    if (raceFinished) return;
    
    // Stars
    stars.forEach(star => {{
        if (!star.collected) {{
            const screenY = star.y + distance;
            if (Math.abs(car.x - star.x) < 40 && Math.abs(car.y - screenY) < 45) {{
                star.collected = true;
                consecutiveStars++;
                multiplier = Math.min(10, Math.floor(consecutiveStars / 3) + 1);
                levelScore += 50 * multiplier;
                
                // Visual feedback
                showFloatingText('+' + (50 * multiplier), star.x, screenY, '#ffd700');
            }}
        }}
    }});
    
    // Bugs
    bugs.forEach(bug => {{
        if (!bug.hit) {{
            const screenY = bug.y + distance;
            if (Math.abs(car.x - bug.x) < 35 && Math.abs(car.y - screenY) < 40) {{
                bug.hit = true;
                levelScore = Math.max(0, levelScore - 30);
                consecutiveStars = 0;
                multiplier = 1;
                
                // Visual feedback
                showFloatingText('-30', bug.x, screenY, '#ff6b6b');
                canvas.style.boxShadow = '0 0 40px #e74c3c';
                setTimeout(() => canvas.style.boxShadow = '', 250);
            }}
        }}
    }});
    
    updateHUD();
}}

let floatingTexts = [];
function showFloatingText(text, x, y, color) {{
    floatingTexts.push({{ text, x, y, color, life: 30 }});
}}

function drawFloatingTexts() {{
    floatingTexts = floatingTexts.filter(ft => {{
        ft.life--;
        ft.y -= 2;
        ctx.font = 'bold 18px Arial';
        ctx.fillStyle = ft.color;
        ctx.globalAlpha = ft.life / 30;
        ctx.fillText(ft.text, ft.x, ft.y);
        ctx.globalAlpha = 1;
        return ft.life > 0;
    }});
}}

function checkFinish() {{
    const level = LEVELS[currentLevel];
    
    if (!raceFinished && distance >= level.length) {{
        raceFinished = true;
        gameRunning = false;
        
        const success = levelScore >= level.target;
        const levelInfo = document.getElementById('level-info');
        const levelTitle = document.getElementById('level-title');
        const levelMessage = document.getElementById('level-message');
        
        if (success) {{
            totalScore += levelScore;
            
            if (currentLevel >= LEVELS.length - 1) {{
                // Game complete!
                levelTitle.textContent = '🏆 CHAMPION! 🏆';
                levelTitle.style.color = '#ffd700';
                levelMessage.innerHTML = 'You conquered all 10 Fabric tracks!<br>Final Score: <b>' + totalScore + '</b>';
                saveScore();
            }} else {{
                levelTitle.textContent = '✅ Level Complete!';
                levelTitle.style.color = '#2ecc71';
                levelMessage.innerHTML = 'Score: <b>' + levelScore + '</b> / ' + level.target + '<br>Next: <b>' + LEVELS[currentLevel + 1].name + '</b>';
            }}
        }} else {{
            levelTitle.textContent = '❌ Not Enough Points!';
            levelTitle.style.color = '#e74c3c';
            levelMessage.innerHTML = 'Score: <b>' + levelScore + '</b> / ' + level.target + ' needed<br>Try again!';
        }}
        
        levelInfo.style.display = 'block';
    }}
}}

function continueGame() {{
    const level = LEVELS[currentLevel];
    const success = levelScore >= level.target;
    
    if (success && currentLevel < LEVELS.length - 1) {{
        currentLevel++;
    }}
    
    document.getElementById('level-info').style.display = 'none';
    initLevel();
    gameRunning = true;
    gameLoop();
}}

function update() {{
    if (!gameRunning) return;
    
    // Movement
    if (keys['ArrowLeft'] || keys['KeyA']) car.x = Math.max(120, car.x - 7);
    if (keys['ArrowRight'] || keys['KeyD']) car.x = Math.min(W - 120, car.x + 7);
    
    // Auto forward
    if (!raceFinished) {{
        distance += car.speed;
        roadOffset += car.speed;
    }}
    
    checkCollisions();
    checkFinish();
    updateHUD();
}}

function render() {{
    drawRoad();
    drawStars();
    drawBugs();
    drawCar();
    drawFloatingTexts();
}}

function gameLoop() {{
    update();
    render();
    if (gameRunning) requestAnimationFrame(gameLoop);
}}

function startGame() {{
    document.getElementById('start-btn').style.display = 'none';
    document.getElementById('game-wrapper').focus();
    currentLevel = 0;
    totalScore = 0;
    gameRunning = true;
    initLevel();
    gameLoop();
}}

function saveScore() {{
    const scores = JSON.parse(localStorage.getItem('fabricRacingScores') || '[]');
    scores.push({{ name: playerName, score: totalScore, level: currentLevel + 1, date: new Date().toLocaleDateString() }});
    scores.sort((a, b) => b.score - a.score);
    localStorage.setItem('fabricRacingScores', JSON.stringify(scores.slice(0, 10)));
    loadLeaderboard();
}}

function loadLeaderboard() {{
    const scores = JSON.parse(localStorage.getItem('fabricRacingScores') || '[]');
    const list = document.getElementById('leaderboard-list');
    list.innerHTML = scores.length ? scores.map((s, i) => '<li>' + (i+1) + '. ' + s.name + ' - ' + s.score + ' pts (Lv.' + s.level + ')</li>').join('') : '<li>No scores yet!</li>';
}}

document.addEventListener('keydown', e => {{ keys[e.code] = true; if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code)) e.preventDefault(); }});
document.addEventListener('keyup', e => keys[e.code] = false);

loadLeaderboard();
render();
</script>
</body>
</html>
"""

display(HTML(game_html))'''

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "id": str(uuid.uuid4())[:8],
            "metadata": {},
            "source": [
                "# 🏎️ Fabric Racing Game - Data Pipeline Edition\n",
                "\n",
                "Race from **START** to **FINISH**, collect ⭐ **data points**, avoid 🐛 **bugs**!\n",
                "\n",
                "## 🎮 Controls\n",
                "- **⬅️ Arrow Left / A**: Steer Left\n",
                "- **➡️ Arrow Right / D**: Steer Right\n",
                "\n",
                "## 📊 Scoring (per level)\n",
                "- ⭐ **Data Point**: +50 points × multiplier\n",
                "- 🔥 **Multiplier**: x2, x3... up to x10 (every 3 consecutive stars)\n",
                "- 🐛 **Bug Hit**: -30 points (resets multiplier)\n",
                "- 🏁 **Level Complete**: Reach finish with target score to advance\n",
                "\n",
                "## 🏆 Fabric Tracks\n",
                "| Level | Track | Target Score |\n",
                "|-------|-------|-------------|\n",
                "| 1 | Lakehouse Lane | 500 |\n",
                "| 2 | Pipeline Pass | 800 |\n",
                "| 3 | Warehouse Way | 1,200 |\n",
                "| 4 | Dataflow Drive | 1,600 |\n",
                "| 5 | Notebook Narrows | 2,000 |\n",
                "| 6 | Eventhouse Express | 2,500 |\n",
                "| 7 | Shortcut Sprint | 3,000 |\n",
                "| 8 | Capacity Canyon | 3,500 |\n",
                "| 9 | OneLake Overdrive | 4,000 |\n",
                "| 10 | Spark Summit | 5,000 |"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "id": str(uuid.uuid4())[:8],
            "metadata": {},
            "outputs": [],
            "source": [
                "# Configuration\n",
                "PLAYER_NAME = \"Player1\"  # Your name for the leaderboard"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "id": str(uuid.uuid4())[:8],
            "metadata": {},
            "outputs": [],
            "source": []
        }
    ],
    "metadata": {
        "language_info": { "name": "python", "version": "3.10" },
        "kernelspec": { "name": "python3", "display_name": "Python 3" }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

lines = game_code.split('\n')
source_lines = [line + '\n' for line in lines[:-1]] + [lines[-1]]
notebook["cells"][2]["source"] = source_lines

with open('catalog/fabric-racing-game/notebooks/racing_game_v2.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)

print("✅ Game rewritten!")
print("Changes:")
print("  - Each level: START → collect stars/avoid bugs → FINISH")
print("  - Score resets each level")
print("  - Must reach target score AND finish to advance")
print("  - Stars: +50 × multiplier, Bugs: -30")
print("  - Multiplier increases every 3 consecutive stars")
