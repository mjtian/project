from __future__ import division
import numpy as np
import torch
from torch import nn
from torchvision import transforms

from utils import load_MNIST, random_draw ,SimpleMLP,ScalableTanh
from realnvp import Realnvp
from gaussian import Gaussian
import math

def train():
    train_data, train_label, test_data, test_label = load_MNIST()
    lr = 1e-4
    Epoch = 10
    Batchsize_test = 20
    Batchsize_train = 600
    Iteration = len(train_data) // Batchsize_train
    depth = 10
    # an epoch means running through the training set roughly once



    x_test = random_draw(test_data, Batchsize_test)
    x_test1 = torch.from_numpy(x_test).to(torch.float32)

    x_test11 = x_test1.reshape(-1,28*28)
    tList = [SimpleMLP([392,392*2,392,392*2,392],[nn.ELU(),nn.ELU(),nn.ELU(),None]) for _ in range(depth)]
    sList = [SimpleMLP([392,392*2,392,392*2,392],[nn.ELU(),nn.ELU(),nn.ELU(),ScalableTanh(392)]) for _ in range(depth)]
    p = Gaussian([28*28])
    f = Realnvp(sList,tList,prior=p)
    # import pdb
    # pdb.set_trace()
    logp1 = f.logProbability(x_test11)
    loss1= -logp1.mean()
    print('Before Training.\nTest loss = %.4f' %loss1)

    params = list(f.parameters())
    params = list(filter(lambda p: p.requires_grad, params))
    nparams = sum([np.prod(p.size()) for p in params])
    print ('total nubmer of trainable parameters:', nparams)
    optimizer = torch.optim.Adam(params, lr=lr)

    TrainLOSS = []
    TestLOSS = []
    for epoch in range(Epoch):

        for j in range(Iteration):
           x_train= random_draw(train_data,Batchsize_train)
           x_train1 = torch.from_numpy(x_train).to(torch.float32)
           x_train11 = x_train1.reshape(-1,28*28)
           logp = f.logProbability(x_train11)
           loss = -logp.mean()

           TrainLOSS.append(loss.item())

           f.zero_grad()
           loss.backward()
           optimizer.step()

           x = random_draw(test_data, Batchsize_test)
           x1 = torch.from_numpy(x).to(torch.float32)
           x11 = x1.reshape(-1,28*28)
           logp2 = f.logProbability(x11)
           loss2= -logp2.mean()

           TestLOSS.append(loss2.item())

        print("epoch = %d, loss = %.4f, test loss = %.4f" %(epoch, loss, loss2))

    trainLoss = np.array(TrainLOSS)
    testLoss = np.array(TestLOSS)

    x = random_draw(test_data, Batchsize_test)
    x1 = torch.from_numpy(x).to(torch.float32)
    x11 = x1.reshape(-1,28*28)
    logp2 = f.logProbability(x11)
    loss2= -logp2.mean()
    print('After Training.\nTest loss = %.4f' %loss2)

    from matplotlib import pyplot as plt

    samples = f.sample(1)[0].detach().numpy().reshape(28,28)
    a = plt.matshow(samples,cmap="gray")
    plt.colorbar(a)
    plt.figure()
    plt.plot(trainLoss,label="Training")
    plt.plot(testLoss,label="Test")
    plt.legend()

    plt.show()

if __name__ == "__main__":
    train()
