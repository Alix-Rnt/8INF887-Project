import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from NeuralNet import NeuralNet
import os

class CheckersNet(nn.Module):
    def __init__(self, game):
        super().__init__()

        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()

        self.conv1 = nn.Conv2d(4, 256, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(256, 256, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(256, 256, kernel_size=3, padding=1)
        self.conv4 = nn.Conv2d(256, 256, kernel_size=3, padding=1)

        self.bn1 = nn.BatchNorm2d(256)
        self.bn2 = nn.BatchNorm2d(256)
        self.bn3 = nn.BatchNorm2d(256)
        self.bn4 = nn.BatchNorm2d(256)

        self.pi_conv = nn.Conv2d(256, 2, kernel_size=1)
        self.pi_bn = nn.BatchNorm2d(2)
        self.pi_fc = nn.Linear(2 * self.board_x * self.board_y, self.action_size)

        self.v_conv = nn.Conv2d(256, 1, kernel_size=1)
        self.v_bn = nn.BatchNorm2d(1)
        self.v_fc1 = nn.Linear(1 * self.board_x * self.board_y, 256)
        self.v_fc2 = nn.Linear(256, 1)

    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.relu(self.bn3(self.conv3(x)))
        x = F.relu(self.bn4(self.conv4(x)))

        pi = F.relu(self.pi_bn(self.pi_conv(x)))
        pi = pi.view(pi.size(0), -1)
        pi = self.pi_fc(pi)
        pi = F.log_softmax(pi, dim=1)

        v = F.relu(self.v_bn(self.v_conv(x)))
        v = v.view(v.size(0), -1)
        v = F.relu(self.v_fc1(v))
        v = torch.tanh(self.v_fc2(v))

        return pi, v

class CheckersNetWrapper(NeuralNet):
    def __init__(self, game):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.net = CheckersNet(game).to(self.device)

    def _encode_board(self, board):
        pieces = board[:-1]
        planes = np.array([
            pieces == 1,
            pieces == 2,
            pieces == -1,
            pieces == -2,
        ], dtype=np.float32)
        return planes

    def train(self, examples):
        optimizer = torch.optim.Adam(self.net.parameters(), lr=1e-3)
        self.net.train()

        for epoch in range(10):
            np.random.shuffle(examples)
            batch_size = 64
            total_loss = 0

            for i in range(0, len(examples), batch_size):
                batch = examples[i:i+batch_size]
                boards, pis, vs = zip(*batch)

                boards = torch.tensor(
                    np.array([self._encode_board(b) for b in boards]),
                    dtype=torch.float32
                ).to(self.device)
                pis = torch.tensor(np.array(pis), dtype=torch.float32).to(self.device)
                vs  = torch.tensor(np.array(vs),  dtype=torch.float32).to(self.device)

                log_pi_pred, v_pred = self.net(boards)

                loss_pi = -torch.sum(pis * log_pi_pred) / len(batch)
                loss_v  = F.mse_loss(v_pred.squeeze(1), vs)
                loss    = loss_pi + loss_v

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                total_loss += loss.item()

            print(f"Epoch {epoch+1} — loss : {total_loss / len(examples):.4f}")

    def predict(self, board):
        self.net.eval()
        with torch.no_grad():
            x = torch.tensor(self._encode_board(board), dtype=torch.float32).unsqueeze(0).to(self.device)
            log_pi, v = self.net(x)
            pi = torch.exp(log_pi).cpu().numpy()[0]
            v  = v.cpu().numpy()[0][0]
        return pi, v

    def save_checkpoint(self, folder, filename):
        os.makedirs(folder, exist_ok=True)
        torch.save(self.net.state_dict(), os.path.join(folder, filename))

    def load_checkpoint(self, folder, filename):
        path = os.path.join(folder, filename)
        self.net.load_state_dict(torch.load(path, map_location=self.device))