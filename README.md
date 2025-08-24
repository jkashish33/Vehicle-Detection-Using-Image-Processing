# Vehicle Detection Project

## Overview
A modular vehicle detection system using Flask (RESTX), SQLAlchemy (in-memory SQLite), and Angular. Compares Haar Cascade (baseline), CNN, and other models on the COCO 2017 dataset.  
**Users can upload images or videos via API endpoints, which will be analyzed using OpenCV and the trained models. Video files are processed frame by frame.**

## Tech Stack
- Python 3.x
- Flask + Flask-RESTX (Swagger API)
- SQLAlchemy (in-memory SQLite)
- Angular (frontend)
- OpenCV, TensorFlow/Keras (for models)
- COCO 2017 Dataset

## Project Structure
```
d:\Vehicle Detection\
│
├── backend\
│   ├── app.py
│   ├── requirements.txt
│   ├── models\
│   ├── routes\
│   ├── services\
│   ├── utils\
│   └── processed\         # Stores processed images and videos
│
├── frontend\
│   └── (Angular app)
│
├── data\
│   └── coco2017\
│
└── README.md
```

## Setup

### Virtual Environment and Dataset setup
1. `python -m venv venv && venv\Scripts\activate`
2. `pip install -r requirements.txt`
3. Download and extract [COCO 2017 dataset](https://www.kaggle.com/datasets/awsaf49/coco-2017-dataset?resource=download) into `data/coco2017`

### Backend
1. `cd backend`
2. `python app.py`

### Frontend
1. `cd frontend`
2. `npm install` # Only for the first time
3. `ng serve`

> **Troubleshooting:**  
> If you see the error `'npm' is not recognized as an internal or external command`, please [download and install Node.js](https://nodejs.org/) (which includes npm) and restart your terminal.
>
> If you see the error `'ng' is not recognized as the name of a cmdlet, function, script file, or operable program`, please install the Angular CLI globally by running:
> ```
> npm install -g @angular/cli
> ```
> Then restart your terminal and try again.
>
> **If you do not see `angular.json` in the `frontend` folder, your Angular project may not have been created or initialized properly.**
> - To create a new Angular workspace in the `frontend` folder, run:
>   ```
>   cd frontend
>   npx @angular/cli new . --skip-git --skip-install
>   ```
>   or, if you want to create it in a new folder:
>   ```
>   npx @angular/cli new frontend
>   ```
> - After this, you should see `angular.json` and other Angular project files in the `frontend` directory.
> - Then run `npm install` and `ng serve` as above.

## Usage
- Access Swagger API docs at `http://localhost:5000/`
- Use Angular UI at `http://localhost:4200/`
- Upload images or videos, run detection, compare models.
- Video uploads are processed frame by frame using OpenCV and analyzed with the trained models.
- Use the `/vehicle/detect_video` endpoint for video analysis.
- **Processed images and videos are stored in the `backend/processed/` directory.**
- **Download processed files by providing the image or video name using the `/vehicle/download/<filename>` endpoint.**

## Notes
- Baseline: Haar Cascade
- Models: Haar Cascade, CNN, (optionally YOLO or SVM)
- In-memory DB for demo purposes
