# ⚽ FCSamurai's Bundesligas Goal Analytics

A lightweight, powerful analytics tool designed to spot goal trends across German professional football. It analyzes recent team performance across the **1. Bundesliga**, **2. Bundesliga**, and **3. Liga** to estimate goal probabilities in upcoming fixtures.

### 📊 What Does It Do?
- **Multi-League Support:** Seamlessly switch between 1. Bundesliga, 2. Bundesliga, and 3. Liga fixtures.
- **Dual Analytical Models:** 
  - **Poisson Model (Venue & Decay Weighted):** Advanced probabilistic modeling accounting for home/away venue splits and recent match recency decay.
  - **Raw Averages (Unweighted Overall):** Direct arithmetic baseline across recent sample windows.
- **Core Goal Metrics:**
  - **Expected Goals (xG):** Projected match goal output.
  - **First Half Goals (1H Over 0.5):** Probability of at least 1 goal before halftime.
  - **Full Time Goals (FT Over 1.5):** Probability of 2 or more total match goals.
  - **Full Time Goals (FT Over 2.5):** Probability of 3 or more total match goals.
- **Customizable Windows:** Adjust the sample history window (from 5 to 20 matches) to fine-tune your analysis.
- **Live Database Sync:** Automatically fetches and syncs the latest fixtures and results straight from OpenLigaDB.

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
- **Mac:** Press `Cmd + Space`, type `Terminal`, and press `Enter`.
- **Windows:** Press the `Windows Key`, type `cmd`, and press `Enter`.

#### 4. Navigate to the Folder
Type `cd ` (include the space) in your terminal, then drag and drop the unzipped project folder directly into the terminal window. Press `Enter`.

#### 5. Install the Required Packages
Copy and paste this command into your terminal and press `Enter`:
```bash
pip install -r requirements.txt