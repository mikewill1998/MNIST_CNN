# -*- coding: utf-8 -*-
"""MINST_with_CNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YeQSm-0hofmOGUkhPN9WcnVqVLk2T9bf
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
from torchvision.datasets import MNIST
from torch.utils.data import DataLoader
import torchvision.transforms as tt

class MNISTCNN(nn.Module):
  def __init__(self, in_channels=1, num_classes=10):
    super(MNISTCNN, self).__init__()
    self.conv1 = nn.Conv2d(in_channels=in_channels, out_channels=8, kernel_size=3, stride=1, padding=1) # same convolution
    self.conv2 = nn.Conv2d(in_channels=8, out_channels=16, kernel_size=3, stride=1, padding=1)
    self.relu = nn.ReLU()
    self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
    self.fc = nn.Linear(16*7*7, num_classes)

  def forward(self, x):
    x = self.conv1(x)
    x = self.relu(x)
    x = self.pool(x)

    x = self.conv2(x)
    x = self.relu(x)
    x = self.pool(x)

    x = x.reshape(x.shape[0], -1)
    x = self.fc(x)

    return x

# hyperparameter
in_channels = 1
num_classes = 10
learning_rate = 0.001
batch_size = 64
num_epochs = 5

train_ds = MNIST(
    root='./data', train=True, download=True, transform=tt.ToTensor())
val_ds = MNIST(
    root='./data', train=False, download=True, transform=tt.ToTensor())

train_dl = DataLoader(dataset=train_ds, batch_size=batch_size, shuffle=True)
val_dl = DataLoader(dataset=val_ds, batch_size=batch_size, shuffle=False)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = MNISTCNN(in_channels=in_channels, num_classes=num_classes).to(device)

# loss and optimizer
criterion = F.cross_entropy
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

for epoch in range(num_epochs):
  for batch_idx, (data, labels) in enumerate(train_dl):
    # send data to gpu
    data = data.to(device=device)
    labels = labels.to(device=device)
    # forward pass
    scores = model(data)
    # calculate loss
    loss = criterion(scores, labels)
    # backward pass
    loss.backward()
    # update weight
    optimizer.step()
    # set gradient back to zero
    optimizer.zero_grad()

# check accuracy
def check_accuracy(dl, model):
  
  model.eval()

  with torch.no_grad():
    for x, y in dl:
      x = x.to(device=device)
      y = y.to(device=device)

      score = model(x)
      _, pred = torch.max(score, dim=1)
      acc = torch.tensor(torch.sum(pred == labels).item()/len(pred))

    print(f'validation accuracy {acc}')
  
  model.train()

check_accuracy(val_dl, model)

check_accuracy(train_dl, model)

torch.save(model.state_dict(), 'MNIST_with_CNN.pth')