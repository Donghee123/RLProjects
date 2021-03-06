# -*- coding: utf-8 -*-
"""
DNN based basestation scheduling model
excute train
excute test
save model
분류기(Classifier) 학습하기
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.autograd import Variable 
import torch.utils.data as data_utils 
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import random
import math
import numpy
import csv
import os

#Neual Netrok nn.Module 상속 
class Net(nn.Module):
    def __init__(self):
        super(Net,self).__init__()
        self.l1 = nn.Linear(12,16)
        self.l2 = nn.Linear(16,20)
        self.l3 = nn.Linear(20,8)
        self.l4 = nn.Linear(8,12)
        
    def forward(self, x):
        
        x = x.float()
        h1 = F.relu(self.l1(x))
        h2 = F.relu(self.l2(h1))
        h3 = F.relu(self.l3(h2))
        return self.l4(h3)

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)
     
def MakeCSVFile(strFolderPath, strFilePath, artofHeader, aryOfDatas):
    strTotalPath = "%s\%s" % (strFolderPath,strFilePath)
    
    f = open(strTotalPath,'w', newline='')
    wr = csv.writer(f)
    
    wr.writerow(artofHeader)
    
    for i in range(0,len(aryOfDatas)):
        wr.writerow(aryOfDatas[i])
    
    f.close()
    
#테스트 함수    
def test(log_interval, model, test_loader):
    
    #평가 모드로 전환
    model.eval()
    
    #Test loss 수집용
    test_loss = 0
    
    #correct rate 수집용
    correct = 0
    
    with torch.no_grad():
        for data, target in test_loader:
            
            #추론 시작
            output = model(data)
           
            #추론 결과 Loss 취득
            test_loss += criterion(output, torch.max(target, 1)[1])
            
            #추론 결과 직접 비교
            if torch.max(target,1)[1] == torch.max(output,1)[1]:
                correct += 1

    
    #추론 결과 평균 수집
    test_loss /= len(test_loader.dataset)

    #추론 결과 보여줌
    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format
          (test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))
    
    artOfTempInfo = []
    artOfTempInfo.append(test_loss.item())
    artOfTempInfo.append(correct)
    artOfTempInfo.append(100. * correct / len(test_loader.dataset))
    aryofModelInfo.append(artOfTempInfo)
   

#학습 함수    
def train(epochcount):
    
    #model을 train 모드로 변경
    model.train()
    
    for epoch in range(epochcount): 
        running_loss = 0.0
        
        #i : trn_loader index, data : set <inputs, labes> 
        for i, data in enumerate(trn_loader,0):
            inputs, labels = data  
            
            #초기화
            optimizer.zero_grad()
            
            #model 유추 시작
            output = model(inputs)
           
            #오차 output, labels 
            loss = criterion(output,  torch.max(labels, 1)[1])
            
            #오차 역전파
            loss.backward()
            optimizer.step()
                           
            #오차 값 표기
            lossValue = loss.item()
            running_loss += lossValue
            
            #2000번 순회시 loss 상태 보여주기
            if i % 2000 == 1999:    # print every 2000 mini-batches
                artoftempLoss = []
                print('[%d, %5d] loss: %.3f' %(epoch + 1, i + 1, running_loss / 2000))
                artoftempLoss.append(running_loss/2000)
                aryofLoss.append(artoftempLoss)
                running_loss = 0.0
            
    
"""
Start Pandas API를 이용한 엑셀 데이터 취득 구간
"""
#100000개 데이터 수집
trndataset = pd.read_csv('./dataset/train/batch0/dataset.csv')
"""
End Pandas API를 이용한 엑셀 데이터 취득 구간
"""


"""
Start 훈련 및 테스트용 데이터 분할 구간
"""
seed = 1

#해당 각 데이터 범주 정의
X_features = ["UE0", "UE1", "UE2", "UE3","UE4", "UE5", "UE6", "UE7","UE8", "UE9", "UE10", "UE11"]
y_features = ["SelUE0", "SelUE1", "SelUE2", "SelUE3","SelUE4", "SelUE5", "SelUE6", "SelUE7","SelUE8", "SelUE9", "SelUE10", "SelUE11"]

#batch size = 1
batch_size = 1

#범주 별로 데이터 취득 X : 입력, Y : 출력
trn_X_pd, trn_y_pd = trndataset[X_features], trndataset[y_features ]

#pandas.core.frame.DataFrame -> numpy -> torch 데이터형으로 변경
trn_X = torch.from_numpy(trn_X_pd.astype(float).to_numpy())
trn_y = torch.from_numpy(trn_y_pd.astype(float).to_numpy())

#torch DataSet(input, output) 세트로 변경
trn = data_utils.TensorDataset(trn_X, trn_y)


#데이터셋 중 훈련 : 70%, 검증 : 30% 사용
trainsetSize = int(70 * len(trn) / 100)
valisetSize = len(trn) - trainsetSize

trn_set, val_set = torch.utils.data.random_split(trn, [trainsetSize, valisetSize])

#훈련용 데이터 로더
trn_loader = data_utils.DataLoader(trn_set, batch_size=batch_size, shuffle=True)
#검증용 데이터 로더
val_loader = data_utils.DataLoader(val_set, batch_size=batch_size, shuffle=True)
"""
End 훈련 및 테스트용 데이터 분할 구간
"""


"""
start module 인스턴스 생성 후 학습 및 테스트 구간
"""
torch.manual_seed(seed)
model = Net()
#손실 함수 계산 교차엔트로피
criterion = nn.CrossEntropyLoss()
#최적화 함수 SGD, 학습률 0.001, momentum 0.5
optimizer = optim.SGD(model.parameters(),lr=0.001,momentum=0.5)

aryofLoss = []
aryofModelInfo = []

log_interval = 10
           
for i in range(0,10):
    #훈련
    train(1)
    #평가
    test(log_interval, model, val_loader)

#Save Model 

modelPath = "./model"
createFolder(modelPath)   
MakeCSVFile(modelPath, "ModelLossInfo.csv", ["Loss"], aryofLoss)
MakeCSVFile(modelPath, "ModelSpec.csv",["Average Loss","Correct","Accracy"],aryofModelInfo)
torch.save(model, modelPath + '/model.pt')    

