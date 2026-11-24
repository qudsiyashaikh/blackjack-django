# 🃏 Blackjack Game (Django Edition)

A browser-playable **Blackjack** card game built with **Django** as part of my **60-Day Unique Python Projects Challenge**. Play against the dealer using Hit and Stand actions with full Ace (`11` or `1`) adjustment and dealer draw rules.

## 🛠️ Tech Stack Used
* **Python** (Game State, Card Logic & Score Calculation)
* **Django** (Web Framework, POST Action Handling & Template Rendering)
* **HTML5 & CSS3** (Card Table UI)

## 🎯 Features
* Deal initial cards for player and dealer with hidden dealer second card until round ends.
* **Hit** to draw additional cards and **Stand** to let the dealer play up to 17.
* Automatic Ace value conversion (`11` to `1`) when score exceeds `21`.
* CSRF-protected form submissions tested locally on Brave Browser.

## ▶️ How to Run Locally
```bash
python app.py