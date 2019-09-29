# -*- coding: utf-8 -*-
"""Dataloader3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FVN6lJqXOvUac5SHwVZgV79sk2v7OtsX
"""

# Commented out IPython magic to ensure Python compatibility.
from __future__ import print_function
from __future__ import division
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import torchvision
from torchvision import datasets, models, transforms
# %matplotlib inline
import matplotlib.pyplot as plt
import time
import os
import copy
from torch.autograd import Variable
import os.path


torch.cuda.current_device()
import torch.nn as nn
import torch.utils.data
import seaborn as sns
sns.set_style("whitegrid")
import pickle

import random
import math
import pandas as pd
import scipy.io

from torchvision import transforms

import torch.nn as nn
import torch.utils.data
import seaborn as sns
import time

sns.set_style("whitegrid")
import torch.nn.functional as F


from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics.pairwise import pairwise_distances_argmin
import sklearn.metrics as metrics

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics.pairwise import pairwise_distances_argmin
import sklearn.metrics as metrics

torch.cuda.empty_cache()

'''
# 创建一个 FeatureFlaten 的层级
class FeatureFlaten(nn.Module):
    def __init__(self):
        super(FeatureFlaten, self).__init__()
    def forward(self, x):
        x = x.view(-1, self.num_flat_features(x))
        return x
    def num_flat_features(self, x):
        size = x.size()[1:]  # all dimensions except the batch dimension
        num_features = 1
        for s in size:
            num_features *= s
        return num_features
    def __repr__(self):
        return 'FeatureFlaten()'

'''      
      
class AutoEncoder(nn.Module):
    def __init__(self):
      super(AutoEncoder, self).__init__()
        
      self.encoder = nn.Sequential(
            nn.Conv2d(1, 64, 3, stride=1, padding=1),  # b, 344, 344
            
            nn.ReLU(True),
            nn.Conv2d(64, 32, 3, stride=2, padding=1), #172
            nn.ReLU(True),
            nn.MaxPool2d(2, stride=2),# 86
            nn.Conv2d(32, 16, 3, stride=2, padding=1),  # b, 16, 43, 43
            nn.ReLU(True),
           # nn.MaxPool2d(2, stride=2),  # b, 10, 42, 42
            nn.Conv2d(16, 1, 3, stride=1, padding=1),  # b, 2, 14, 14
            nn.ReLU(True),          
          )
      
      self.fc1 = nn.Linear(21 * 21, 300)
      
      self.fc2 = nn.Linear(300, 21 * 21)

      self.decoder = nn.Sequential(

          #  nn.ConvTranspose2d(2, 8, 2, stride=1, padding=1),
          #  nn.ReLU(True),
            nn.ConvTranspose2d(1, 16, 3, stride=1, padding=1),  # b, 
            nn.ReLU(True),           
            nn.ConvTranspose2d(16, 32, 3, stride=2, padding=1),  # b, 
            nn.ReLU(True),
            nn.Upsample(size=172, mode='nearest'),
            nn.ConvTranspose2d(32, 64, 3, stride=2, padding=1),            
            nn.ReLU(True),
            nn.ConvTranspose2d(64, 1, 3, stride=1, padding=1),  # b
            nn.Upsample(size=344, mode='nearest'),
            nn.Sigmoid()


          )
       

  
    def forward(self, x):
        encoded = self.encoder(x)
        #encoded = encoded.view(encoded.size(0), -1)
        #encoded = self.fc1(encoded)

        #decoded = (self.fc2(encoded)).view(-1, 1, 43, 43)       
        decoded = self.decoder(encoded)
        return encoded, decoded




def train(model0, model1, model2, iterator, optimizer0, optimizer1, optimizer2, criterion, clip, device, correlationCoefficientList):
    model0.train()
    model1.train()
    model2.train()
    epoch_loss = 0

    for i, batch in enumerate(iterator):  # torch.Size([32, 3, 344, 344])
        src = batch[0].to(device)
        decoded = torch.zeros(32, 3, 344, 344)
        
        src0 = src[:,0,:,:]
        src0 = src0.unsqueeze(1)
        
        encoded, decoded0 = model0(src0.float())
        loss0 = criterion(decoded0, src0.float())  # mean square error
        optimizer0.zero_grad()  # clear gradients for this training step
        loss0.backward()  # backpropagation, compute gradients
        torch.nn.utils.clip_grad_norm_(model0.parameters(), clip)
        optimizer0.step()  # apply gradients

        epoch_loss += loss0.item()
        
        src1 = src[:,1,:,:]
        src1 = src1.unsqueeze(1)
        encoded, decoded1 = model1(src1.float())
        loss1 = criterion(decoded1, src1.float())  # mean square error
        optimizer1.zero_grad()  # clear gradients for this training step
        loss1.backward()  # backpropagation, compute gradients
        torch.nn.utils.clip_grad_norm_(model1.parameters(), clip)
        optimizer1.step()  # apply gradients

        epoch_loss += loss1.item()
        
        
        src2 = src[:,2,:,:]
        src2 = src2.unsqueeze(1)
        encoded, decoded2 = model2(src2.float())
        loss2 = criterion(decoded2, src2.float())  # mean square error
        optimizer2.zero_grad()  # clear gradients for this training step
        loss2.backward()  # backpropagation, compute gradients
        torch.nn.utils.clip_grad_norm_(model2.parameters(), clip)
        optimizer2.step()  # apply gradients

        epoch_loss += loss2.item()
        
        decoded = torch.cat((decoded0, decoded1, decoded2), 1)
        

        if i % 20 == 0:
            print("batch lossxxx:", epoch_loss)
            
       
        if i % 60 == 0:
            img_true = src[0].cpu().numpy()
            img_true = np.transpose(img_true, (1, 2, 0))  # 把channel那一维放到最后
            plt.imshow(img_true)
            plt.show()
            
            time.sleep(1)
            img_decoded = decoded[0].cpu().detach().numpy()
            img_decoded = np.transpose(img_decoded, (1, 2, 0))  # 把channel那一维放到最后
            plt.imshow(img_decoded)
            plt.show()
                    
    return epoch_loss / len(iterator), correlationCoefficientList


def evaluate(model, iterator, criterion, device, correlationCoefficientList_eva):
    model.eval()

    epoch_loss = 0

    with torch.no_grad():
      for i, batch in enumerate(iterator):
            src = batch[0].to(device)
            

            encoded, decoded = model(src.float())  # turn off teacher forcing
            loss = criterion(decoded.float(), src.float())
            epoch_loss += loss.item()
                        
            if i % 20 == 0: 
              img_true = src[0].cpu().numpy()
              img_true = np.transpose(img_true, (1, 2, 0))  # 把channel那一维放到最后
              plt.imshow(img_true)
              plt.show()
            
              time.sleep(1)
              img_decoded = decoded[0].cpu().detach().numpy()
              img_decoded = np.transpose(img_decoded, (1, 2, 0))  # 把channel那一维放到最后
              plt.imshow(img_decoded)
              plt.show()

    return epoch_loss / len(iterator), correlationCoefficientList_eva


def epoch_time(start_time, end_time):
    elapsed_time = end_time - start_time
    elapsed_mins = int(elapsed_time / 60)
    elapsed_secs = int(elapsed_time - (elapsed_mins * 60))
    return elapsed_mins, elapsed_secs







# normalize=transforms.Normalize(mean=[.5,.5,.5],std=[.5,.5,.5])

torch.cuda.empty_cache()
data_transforms = transforms.Compose([
        transforms.RandomResizedCrop(344),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor()])


path1 = 'drive/My Drive/Colab Notebooks/UF_code/images/train/'
# 需要把图片放在"../images/train/0/"中
train_dset =  datasets.ImageFolder(path1, transform=data_transforms)
train_loader = torch.utils.data.DataLoader(train_dset,
                     batch_size=32,
                     num_workers=0,
                     shuffle=True)

path2 = 'drive/My Drive/Colab Notebooks/UF_code/images/validation/'
validation_dset =  datasets.ImageFolder(path2, transform=data_transforms)
validation_loader = torch.utils.data.DataLoader(validation_dset,
                     batch_size=32,
                     num_workers=0,
                     shuffle=True)


'''-------------------------------------------------------------------------'''
'''--------------------------- Hyper Parameters ----------------------------'''
'''-------------------------------------------------------------------------'''
EPOCH = 80
LR = 0.0004  # learning rate
CLIP = 1
# baseline 100th measurement in Rawdata_data00025

N_FILE = 2

BASELINE_FILE = 197
BASELINE_MEASUREMENT = 1

Loading_DATA = True
SAVE_CREATED_DATA = True
WITH_MASS_LABEL = True

ANALYSIS_DATA = True
TRAIN = True
EVALUATE = False
COMPRRSSION_DATA = True
DETECTION_ANOMALY = True



device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

autoencoder0 = AutoEncoder().to(device)
autoencoder1 = AutoEncoder().to(device)
autoencoder2 = AutoEncoder().to(device)

optimizer0 = torch.optim.Adam(autoencoder0.parameters(), lr=LR)
optimizer1 = torch.optim.Adam(autoencoder1.parameters(), lr=LR)
optimizer2 = torch.optim.Adam(autoencoder2.parameters(), lr=LR)
loss_func = nn.MSELoss()

loss_record = []
correlationCoefficientList = []
correlationCoefficientList_eva = []


if TRAIN:


    best_valid_loss = float('inf')

    for epoch in range(EPOCH):
        # for step, (x, b_label) in enumerate(train_loader):

        start_time = time.time()
        
        

        train_loss, correlationCoefficientList = train(autoencoder0, autoencoder1, autoencoder2, train_loader, optimizer0, optimizer1, optimizer2,
                                                                             loss_func, CLIP, device,
                                                                             correlationCoefficientList)
        
       # valid_loss, correlationCoefficientList_eva = evaluate(autoencoder, validation_loader,loss_func, device,correlationCoefficientList_eva)

        end_time = time.time()

        epoch_mins, epoch_secs = epoch_time(start_time, end_time)

       # if valid_loss < best_valid_loss:
       #     best_valid_loss = valid_loss


        print(f'Epoch: {epoch + 1:02} | Time: {epoch_mins}m {epoch_secs}s')
        print(f'\tTrain Loss: {train_loss:.3f} | Train PPL: {math.exp(train_loss):7.3f}')
      #  print(f'\t Val. Loss: {valid_loss:.3f} |  Val. PPL: {math.exp(valid_loss):7.3f}')

      #  loss_record.append([train_loss, valid_loss])

from google.colab import drive
drive.mount('/content/drive')
