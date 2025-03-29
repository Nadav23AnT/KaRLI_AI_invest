# KaRLI_AI - Reinforcement Learning Investor 🚀💸

Welcome to the **Reinforcement Learning Investor** project! This platform leverages cutting-edge **Deep Learning** and **Reinforcement Learning (RL)** technologies to create an **automated investment portfolio management system**. It aims to optimize returns while maintaining robust risk management tailored to individual user preferences. 🌟

---

## 📖 Overview

This project combines state-of-the-art AI algorithms, real-time financial market analysis, and an intuitive user interface to provide **smart, actionable investment decisions**. It bridges **advanced RL models** with seamless integration into real-world trading systems.

Key features include:
- Automated trading decisions: `Buy`, `Sell`, or `Hold` 📈📉
- Real-time portfolio analysis with visual insights 📊
- Risk management tailored to user preferences ⚖️
- Connection to live trading accounts via APIs 🔗

---

## ✨ Features

1. **User Management** 👤
   - Secure sign-up and login.
   - Personalized risk profiling and preferences.

2. **Portfolio Summary & Insights** 💼
   - Total portfolio worth and investment distribution.
   - Historical trading actions and performance metrics.

3. **Reinforcement Learning Models** 🧠
   - Intelligent decision-making using **TensorFlow**, **Stable-Baselines3**, and **OpenAI Gym**.
   - Continuous learning from live market data.

4. **Automated Trading Execution** 🤖
   - Direct integration with broker APIs for seamless trading.
   - Real-time logging of actions for full transparency.

5. **Data Management** 📂
   - Historical stock data, technical indicators, and macroeconomic factors.
   - Secure storage in **MongoDB**.

---

## 🛠️ Technologies Used

### Backend 🖥️
- **Flask**: Web server and API management.
- **TensorFlow / PyTorch**: Deep Learning framework for RL model development.
- **MongoDB**: NoSQL database for scalable user and financial data storage.

### Frontend 🌐
- **React.js**: Modern UI library for an intuitive user experience.
- **Chart.js / D3.js**: For dynamic and responsive visualizations.

### Reinforcement Learning Frameworks 🤖
- **Stable-Baselines3**: RL algorithms like PPO and DDPG.
- **OpenAI Gym**: Simulation environment for model training.

---

## 🚀 How It Works

1. **User Registration & Setup**
   - Users register and set investment preferences (e.g., risk tolerance).

2. **Data Processing & Analysis**
   - Financial market data is fetched and preprocessed.

3. **Model Training & Recommendations**
   - The RL model learns market dynamics and generates trading recommendations.

4. **Automated Trading**
   - Trades are executed via API integration, and results are logged in real-time.

---

## 📦 Getting Started

### Prerequisites
- Installed Docker
- API keys for financial data (e.g., Yahoo Finance, Alpha Vantage)

### Development Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/YourUsername/Reinforcement-Learning-Investor.git
   ```

1. Build containers:
   ```
   docker-compose build
   ```
   This will automatically build all the necessary containers for the system to run.

1. Run dev environment:
   ```
   docker-compose up -d
   ```
   Every container listens on the local storage, so any code change will not require rebuild, but may require restarting.

1. Check status:
   ```
   docker-compose ps
   ```

1. Check logs:
   ```
   docker-compose logs <service-name> --tail=50 -f
   ```

1. Use [`lazydocker`](https://github.com/jesseduffield/lazydocker/releases/tag/v0.24.1) (recommended)

---

## 🌟 Team Members

- **Nadav Chen**
- **Michael Sarusi**
- **David Elimelech**
- **Daniel Perets**
- **Itai Shalev**
- **Edwin Krasheninin**

---

## 🧩 Future Enhancements

- **Paper Trading Mode** 📝: Test strategies risk-free.
- **Enhanced Visualizations** 📈: More comprehensive portfolio insights.
- **Mobile App** 📱: Manage investments on the go.

---

## 📞 Contact

Have questions or feedback? Reach out to us:
📧 Email: Nadav2282@gmail.com

![image](https://github.com/user-attachments/assets/4a1de37a-2a6e-4561-9167-4b3fec36600f)
---

Let me know if there's anything else you'd like to add! 😊
