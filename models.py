import torch
import torch.nn as nn

# Определяем модель
class NeuralNetwork_n_ratio(nn.Module):
    def __init__(self, input_size):
        super(NeuralNetwork_n_ratio, self).__init__()
        self.input_layer = nn.Linear(input_size, 64)
        self.hidden1 = nn.Linear(64, 128)
        self.hidden2 = nn.Linear(128, 64)
        self.hidden3 = nn.Linear(64, 32)
        self.output_layer = nn.Linear(32, 1)
        
        self.batch_norm1 = nn.BatchNorm1d(64)
        self.batch_norm2 = nn.BatchNorm1d(128)
        self.batch_norm3 = nn.BatchNorm1d(64)
        self.batch_norm4 = nn.BatchNorm1d(32)
        
        self.dropout = nn.Dropout(0.2)
        self.activation = nn.LeakyReLU()

    def forward(self, x):
        x = self.activation(self.batch_norm1(self.input_layer(x)))
        x = self.dropout(x)
        x = self.activation(self.batch_norm2(self.hidden1(x)))
        x = self.dropout(x)
        x = self.activation(self.batch_norm3(self.hidden2(x)))
        x = self.dropout(x)
        x = self.activation(self.batch_norm4(self.hidden3(x)))
        x = self.output_layer(x)
        return x
    
# Определяем модель
class NeuralNetwork_Vsyn_m(nn.Module):
    def __init__(self, input_size):
        super(NeuralNetwork_Vsyn_m, self).__init__()
        self.input_layer = nn.Linear(input_size, 64)
        self.hidden1 = nn.Linear(64, 128)
        self.hidden2 = nn.Linear(128, 64)
        self.hidden3 = nn.Linear(64, 32)
        self.output_layer = nn.Linear(32, 1)
        
        self.batch_norm1 = nn.BatchNorm1d(64)
        self.batch_norm2 = nn.BatchNorm1d(128)
        self.batch_norm3 = nn.BatchNorm1d(64)
        self.batch_norm4 = nn.BatchNorm1d(32)
        
        self.dropout = nn.Dropout(0.2)
        self.activation = nn.LeakyReLU()

    def forward(self, x):
        x = self.activation(self.batch_norm1(self.input_layer(x)))
        x = self.dropout(x)
        x = self.activation(self.batch_norm2(self.hidden1(x)))
        x = self.dropout(x)
        x = self.activation(self.batch_norm3(self.hidden2(x)))
        x = self.dropout(x)
        x = self.activation(self.batch_norm4(self.hidden3(x)))
        x = self.output_layer(x)
        return x
