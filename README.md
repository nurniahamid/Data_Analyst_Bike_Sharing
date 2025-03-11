# Bike Sharing Dashboard
## Setup Environment - Anaconda

conda create --name bike-sharing-dashboard python=3.9
conda activate bike-sharing-dashboard
pip install -r requirements.txt

## Setup Environment - Shell/Terminal
mkdir bike_sharing_dashboard
cd bike_sharing_dashboard
pipenv install
pipenv shell
pip install -r requirements.txt

##Run steamlit app
streamlit run dashboard.py
