# 🃏 Card Image Classification with PyTorch

This project is a deep learning-based image classification system for recognizing playing cards using PyTorch. Built from scratch and trained on a Kaggle playing card dataset, the model achieves 96.23% test accuracy, demonstrating robust generalization and strong feature learning.

---

## 📂 Dataset

- **Source**: [Kaggle Playing Cards Dataset](https://www.kaggle.com/datasets/gpiosenka/cards-image-datasetclassification) 
- **Structure**: Images are organized in class-labeled folders (`train/<class_name>/image.jpg`, `val/<class_name>/image.jpg`)
- **Classes**: Includes standard playing cards (e.g., "two of hearts", "king of spades", etc.)

---

## 📊 Model Performance 

After training for 5 epochs on a stratified dataset, the model reached:

✅ Accuracy: 96.23%

📉 Final Loss: ~0.15

---
## 🔁 Training vs. Validation Loss

| Epoch | Training Loss | Validation Loss | Accuracy     |
| ----- | ------------- | --------------- | ------------ |
| 1     | 0.55          | 0.22            | 43.2%        |
| 2     | 0.33          | 0.15            | 65.6%        |
| 3     | 0.25          | 0.20            | 89.9%        |
| 4     | 0.18          | 0.15            | 92.0%        |
| 5     | 0.15          | 0.14            | **96.23%** ✅|

### 📉 Loss Curve
![Loss over Epochs](output.png)

---

## 📌 Features

- End-to-end training pipeline using PyTorch
- Live validation monitoring per epoch
- GPU support (CUDA fallback to CPU)
- Inference on individual images with softmax probability scores
- Visual output of top 5 class predictions
- Trained model saving and loading for future inference

---

## ⚙️ Installation & Setup

1. **Clone the repository**  
   ```bash
   git clone https://github.com/jan257/Card-Classifier-using-PyTorch.git
   cd Card-Classifier-using-PyTorch
   ```
   
2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```
   
3. **Install dependencies**
   ```bash
   pip install torch torchvision timm 
   ```

4. **Download and prepare dataset**
   
- Download the dataset from Kaggle
- Unzip it into the root directory under /train, /val, and /test folders

---

## Technologies Used
  - Python 3.10+
  - PyTorch
  - torchvision
  - matplotlib
  - PIL (Pillow)

---
## 🤝 Acknowledgements
- Dataset: [Kaggle Playing Cards Dataset](https://www.kaggle.com/datasets/gpiosenka/cards-image-datasetclassification) 
- Framework: PyTorch
---

## 👩‍💻 Author

**Jahnavi P**  
📍 Bangalore, India  
🔗 [LinkedIn](https://www.linkedin.com/in/jahnavi-p-a68788233) 

---
