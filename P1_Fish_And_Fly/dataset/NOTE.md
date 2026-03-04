# Important notes

### 1. Dataset
I have 2 datasets, in this folder named `dataset`.
- 1.) Training dataset: Marine-project-3
- 2.) Inference dataset: test_footage

1.) Marine-project-3/ Training data:
- This dataset is created using Roboflow.
- This dataset is used in training YOLOv8s model, used in Perception, in this project.
- It contains total 3654 images, out of which 2927 are training images and 727 are validation images.
- Here, Train : Test = 80 : 20.
- Source: Roboflow datasets and google images.

2.) test_footage / Inference videos:
- This dataset is used in Inference, in real time, by the Fish machine.
- This dataset contains video footage of actual underwater scenes.
- Source: google images.


### 2. Training

- This training dataset `Marine-project-3` is not uploaded fully in this project folder, due to resource (memory) constraint.
- The actual training dataset is saved in my Google drive and as Roboflow version. Below are the links to the original dataset.

Drive link: `https://drive.google.com/drive/folders/1t-1wKCZ-USrAGHVGqw9bXwKit7Ez-G4Z`
Roboflow link: `https://universe.roboflow.com/1conviniencestore/marine-project-uoi6r`

- I have CPU in my local, so I trained my YOLO model, using Google Colab GPU. 
- If someone has GPU in their local system, they can keep the original dataset in their local system and perform YOLO model training.

NOTE: **In my local system, I only kept 5 images and labels in both train and valid folders repsectively, to check YOLO training in local system(CPU).**


# 3. Test footage folder
- In this dataset folder, there is a sub-folder `test_footage` where there is a collection of short videos, in which inference is runned or testing is verified for the entire project.
- I mentioned this sub-folder in the `.gitignore` file due to memory constraints in github for pushing video clips.