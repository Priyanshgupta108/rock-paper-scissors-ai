# 🎮 Rock Paper Scissors AI

A gesture-controlled Rock Paper Scissors game where you play using real hand gestures via webcam — no buttons needed.

The AI opponent **learns your patterns** using a Markov chain and predicts your next move. The harder the difficulty, the more it exploits your habits.

## Demo
<!-- Add a GIF or screenshot here -->

## Features
- ✋ Real-time hand gesture detection using MediaPipe
- 🧠 Adaptive AI that learns your move patterns
- 🎯 3 difficulty levels — Easy, Medium, Hard
- 🏆 Best of 3 / 5 / 7 rounds with live score tracking
- 🖥️ Built with Pygame for a clean desktop UI

## Tech Stack
Python • OpenCV • MediaPipe • Pygame

## Setup

### 1. Install dependencies
pip install opencv-python mediapipe pygame numpy

### 2. Download the MediaPipe model
curl -o hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task

### 3. Run the game
python main.py

## Controls
| Key | Action |
|-----|--------|
| `1` / `2` / `3` | Set difficulty |
| `B` | Toggle Best of 3 / 5 / 7 |
| `SPACE` | Start round / Return to menu |
