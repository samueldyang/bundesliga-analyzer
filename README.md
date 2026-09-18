# ⚽ FCSamurai's Bundesliga Goal Trend Dashboard

A lightweight analytics tool that helps you spot goal trends in German football matches. It analyzes recent team performance across the **1. Bundesliga**, **2. Bundesliga**, and **3. Liga** to estimate the likelihood of goals in upcoming fixtures.

### 📊 What Does It Do?
* **First Half Goals (1H Over 0.5):** Calculates how often at least 1 goal is scored before halftime in a team's recent matches.
* **Full Time Goals (FT Over 2.5):** Calculates how often a match ends with 3 or more total goals.
* **Matchup Comparison:** Pick any two teams to see their combined goal probabilities based on a customizable window of recent games (e.g., last 10 matches).
* **Live Updates:** Syncs finished match results directly from official league data with a single click.

---

## 🚀 How to Use

### Option 1: Use the Web Version (Easiest — No Installation Needed)
If you want to use the app immediately on your phone or computer without installing anything, click the link below:

👉 **[Click Here to Open the Live App](https://fcsamurai-bundesliga-analyzer.streamlit.app/)**

---

### Option 2: Run It on Your Computer (Step-by-Step for Beginners)

If you want to run the app locally on your computer, follow these step-by-step instructions:

#### 1. Install Python
1. Download Python from [python.org](https://www.python.org/downloads/).
2. Run the installer. **Important (Windows users):** Check the box that says **"Add Python to PATH"** before clicking Install.

#### 2. Download This Project
1. Scroll to the top of this GitHub page and click the green **`Code`** button.
2. Click **Download ZIP**.
3. Unzip the downloaded folder on your computer (e.g., on your Desktop).

#### 3. Open Your Terminal or Command Prompt
* **Mac:** Press `Cmd + Space`, type `Terminal`, and press `Enter`.
* **Windows:** Press the `Windows Key`, type `cmd`, and press `Enter`.

#### 4. Navigate to the Folder
Type `cd ` (include the space) in your terminal, then drag and drop the unzipped project folder directly into the terminal window. Press `Enter`.

#### 5. Install the Required Packages
Copy and paste this command into your terminal and press `Enter`:
```bash
pip install -r requirements.txt
```

#### 6. Start the App
Copy and paste this command into your terminal and press `Enter`:
```bash
streamlit run app.py
```

Your web browser will automatically open with the dashboard ready to use!
