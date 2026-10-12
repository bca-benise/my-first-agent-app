(() => {
  const canvas = document.getElementById("game-canvas");
  const ctx = canvas.getContext("2d");

  const overlay = document.getElementById("game-over-overlay");
  const btnRestart = document.getElementById("btn-restart");
  const victoryBanner = document.getElementById("victory-banner");
  const btnWinRestart = document.getElementById("btn-win-restart");

  const elements = {
    player: {
      card: document.getElementById("card-player"),
      status: document.getElementById("status-player"),
      len: document.getElementById("len-player"),
      score: document.getElementById("score-player"),
    },
    npc1: {
      card: document.getElementById("card-npc1"),
      status: document.getElementById("status-npc1"),
      len: document.getElementById("len-npc1"),
      score: document.getElementById("score-npc1"),
    },
    npc2: {
      card: document.getElementById("card-npc2"),
      status: document.getElementById("status-npc2"),
      len: document.getElementById("len-npc2"),
      score: document.getElementById("score-npc2"),
    },
  };

  const SNAKE_COLORS = {
    player: {
      body: "#00c482",
      head: "#38ffc0",
      eye: "#082018",
    },
    npc_1: {
      body: "#9b30c9",
      head: "#df80ff",
      eye: "#200830",
    },
    npc_2: {
      body: "#e67e22",
      head: "#ffb84d",
      eye: "#381a04",
    },
  };

  let latestState = null;
  let isGameOverVisible = false;
  let isVictoryVisible = false;

  function sendDirection(dir) {
    fetch("/api/direction", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ direction: dir }),
    }).catch(() => {});
  }

  function sendRestart() {
    fetch("/api/restart", {
      method: "POST",
    })
      .then(() => {
        overlay.classList.add("hidden");
        victoryBanner.classList.add("hidden");
        isGameOverVisible = false;
        isVictoryVisible = false;
      })
      .catch(() => {});
  }

  window.addEventListener("keydown", (e) => {
    const key = e.key.toLowerCase();
    if (key === "arrowup" || key === "w") {
      sendDirection("UP");
      e.preventDefault();
    } else if (key === "arrowdown" || key === "s") {
      sendDirection("DOWN");
      e.preventDefault();
    } else if (key === "arrowleft" || key === "a") {
      sendDirection("LEFT");
      e.preventDefault();
    } else if (key === "arrowright" || key === "d") {
      sendDirection("RIGHT");
      e.preventDefault();
    } else if (key === " " || key === "r" || key === "enter") {
      if (isGameOverVisible || isVictoryVisible) {
        sendRestart();
        e.preventDefault();
      }
    }
  });

  btnRestart.addEventListener("click", () => {
    sendRestart();
  });

  btnWinRestart.addEventListener("click", () => {
    sendRestart();
  });

  function updateScoreboard(snakes) {
    snakes.forEach((snake) => {
      let ui = null;
      if (snake.id === "player") ui = elements.player;
      else if (snake.id === "npc_1") ui = elements.npc1;
      else if (snake.id === "npc_2") ui = elements.npc2;

      if (!ui) return;

      const isAlive = snake.status === "ALIVE";
      ui.len.textContent = snake.length;
      ui.score.textContent = snake.score;
      ui.status.textContent = isAlive ? "ALIVE" : "ELIMINATED";

      if (isAlive) {
        ui.card.classList.remove("dead");
        ui.status.classList.remove("eliminated");
      } else {
        ui.card.classList.add("dead");
        ui.status.classList.add("eliminated");
      }
    });
  }

  function render(state) {
    if (!state) return;

    const cols = state.dimensions.width;
    const rows = state.dimensions.height;
    const cellWidth = canvas.width / cols;
    const cellHeight = canvas.height / rows;

    // Clear background
    ctx.fillStyle = "#0f131d";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Subtle grid pattern
    ctx.strokeStyle = "rgba(255, 255, 255, 0.03)";
    ctx.lineWidth = 1;
    for (let x = 0; x <= canvas.width; x += cellWidth) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y <= canvas.height; y += cellHeight) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }

    // Render apples
    state.apples.forEach((apple) => {
      const cx = apple.position.x * cellWidth + cellWidth / 2;
      const cy = apple.position.y * cellHeight + cellHeight / 2;
      const radius = Math.min(cellWidth, cellHeight) * 0.42;

      ctx.save();
      if (apple.kind === "GREEN") {
        ctx.fillStyle = "#2ecc71";
        ctx.shadowColor = "#2ecc71";
        ctx.shadowBlur = 10;
      } else {
        ctx.fillStyle = "#ff3b5c";
        ctx.shadowColor = "#ff3b5c";
        ctx.shadowBlur = 8;
      }

      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fill();

      // Apple shine
      ctx.fillStyle = "rgba(255, 255, 255, 0.5)";
      ctx.beginPath();
      ctx.arc(cx - radius * 0.35, cy - radius * 0.35, radius * 0.25, 0, Math.PI * 2);
      ctx.fill();

      ctx.restore();
    });

    // Render snakes
    state.snakes.forEach((snake) => {
      if (snake.status !== "ALIVE" || snake.body.length === 0) return;

      const colors = SNAKE_COLORS[snake.id] || {
        body: "#aaa",
        head: "#fff",
        eye: "#000",
      };

      // Draw body
      ctx.fillStyle = colors.body;
      for (let i = 1; i < snake.body.length; i++) {
        const seg = snake.body[i];
        const pad = 2;
        ctx.fillRect(
          seg.x * cellWidth + pad,
          seg.y * cellHeight + pad,
          cellWidth - pad * 2,
          cellHeight - pad * 2
        );
      }

      // Draw head
      const head = snake.body[0];
      const hx = head.x * cellWidth;
      const hy = head.y * cellHeight;
      const pad = 1;

      ctx.save();
      ctx.fillStyle = colors.head;
      ctx.fillRect(hx + pad, hy + pad, cellWidth - pad * 2, cellHeight - pad * 2);

      // Draw eyes pointing towards direction
      ctx.fillStyle = colors.eye;
      const eyeSize = Math.max(2, cellWidth * 0.16);
      let eye1 = { x: hx + cellWidth * 0.3, y: hy + cellHeight * 0.3 };
      let eye2 = { x: hx + cellWidth * 0.7, y: hy + cellHeight * 0.3 };

      if (snake.direction === "DOWN") {
        eye1 = { x: hx + cellWidth * 0.3, y: hy + cellHeight * 0.7 };
        eye2 = { x: hx + cellWidth * 0.7, y: hy + cellHeight * 0.7 };
      } else if (snake.direction === "LEFT") {
        eye1 = { x: hx + cellWidth * 0.3, y: hy + cellHeight * 0.3 };
        eye2 = { x: hx + cellWidth * 0.3, y: hy + cellHeight * 0.7 };
      } else if (snake.direction === "RIGHT") {
        eye1 = { x: hx + cellWidth * 0.7, y: hy + cellHeight * 0.3 };
        eye2 = { x: hx + cellWidth * 0.7, y: hy + cellHeight * 0.7 };
      }

      ctx.beginPath();
      ctx.arc(eye1.x, eye1.y, eyeSize, 0, Math.PI * 2);
      ctx.arc(eye2.x, eye2.y, eyeSize, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    });

    // Update scoreboard
    updateScoreboard(state.snakes);

    // Update victory banner
    if (state.is_player_winner && !state.is_game_over) {
      if (!isVictoryVisible) {
        victoryBanner.classList.remove("hidden");
        isVictoryVisible = true;
      }
    } else {
      if (isVictoryVisible) {
        victoryBanner.classList.add("hidden");
        isVictoryVisible = false;
      }
    }

    // Update game over overlay
    if (state.is_game_over) {
      if (!isGameOverVisible) {
        overlay.classList.remove("hidden");
        isGameOverVisible = true;
      }
    } else {
      if (isGameOverVisible) {
        overlay.classList.add("hidden");
        isGameOverVisible = false;
      }
    }
  }

  function startStateSync() {
    let sseActive = false;
    try {
      const eventSource = new EventSource("/api/stream");
      eventSource.onmessage = (event) => {
        sseActive = true;
        const state = JSON.parse(event.data);
        latestState = state;
        render(state);
      };

      eventSource.onerror = () => {
        sseActive = false;
        eventSource.close();
        startPolling();
      };
    } catch (err) {
      startPolling();
    }

    function startPolling() {
      setInterval(() => {
        if (sseActive) return;
        fetch("/api/state")
          .then((res) => res.json())
          .then((state) => {
            latestState = state;
            render(state);
          })
          .catch(() => {});
      }, 100);
    }
  }

  startStateSync();
})();
