# Alien Invasion - 浏览器版

一个基于 PyScript 和 HTML5 Canvas 的太空射击游戏，是经典 Pygame 版本的浏览器移植版。

## 游戏介绍

Alien Invasion 是一款经典的太空射击游戏，玩家控制一艘蓝色飞船，通过左右移动和发射子弹来消灭不断入侵的红色外星人。游戏包含以下特色：

- 🎮 流畅的游戏体验
- 🚀 可控制的飞船移动
- 🔫 子弹发射系统
- 👾 外星人群体移动和攻击
- 📈 分数和等级系统
- 💖 3 条生命值
- ⚡ 随关卡增加的游戏速度

## 技术栈

- **前端**：HTML5, CSS, JavaScript
- **Python**：使用 PyScript 运行在浏览器中
- **渲染**：HTML5 Canvas
- **部署**：GitHub Pages

## 如何运行

### 本地运行

1. 克隆项目到本地：
   ```bash
   git clone https://github.com/your-username/alien-invasion.git
   cd alien-invasion
   ```

2. 启动本地 HTTP 服务器：
   ```bash
   python3 -m http.server 8000
   ```

3. 打开浏览器访问：
   ```
   http://localhost:8000
   ```

### 如何玩

1. 按 **空格键** 开始游戏
2. 使用 **左/右方向键** 移动飞船
3. 按 **空格键** 发射子弹
4. 消灭所有外星人进入下一关
5. 小心外星人的攻击，你有 3 条生命

## 部署到 GitHub Pages

项目已配置 GitHub Actions，当代码推送到 `main` 分支时，会自动部署到 GitHub Pages。

1. 确保你的仓库已启用 GitHub Pages
2. 推送到 `main` 分支
3. 等待 GitHub Actions 完成部署
4. 访问 `https://your-username.github.io/alien-invasion` 玩游戏

## 开发说明

- 游戏使用 PyScript 2024.1.1 版本
- 所有游戏逻辑都在 `main.py` 中实现
- 样式在 `styles.css` 中定义
- 游戏使用 Canvas API 进行绘制

## 未来计划

- 添加音效
- 实现更复杂的外星人行为
- 添加电源-ups
- 增加游戏难度设置
- 实现最高分保存

