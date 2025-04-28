# run_pipeline.py
# -------------------------------------------------------
import subprocess

print("🛠️ Starting full MLB 1-5 innings model pipeline...")

# Step 1: Run get_scores_full.py (scrape latest boxscores)
print("🚀 Scraping latest boxscores...")
subprocess.run(["python", "get_scores_full.py"], check=True)

# Step 2: Run 1to5_predictions_full.py (predict using latest model)
print("🚀 Predicting today's and future games...")
subprocess.run(["python", "1to5_predictions_full.py"], check=True)

# Step 3: Launch Streamlit app
print("🚀 Launching Streamlit Dashboard...")
subprocess.Popen(["streamlit", "run", "app.py"])

print("\n✅ Pipeline completed successfully! 🌟 The dashboard should open in your browser!")
