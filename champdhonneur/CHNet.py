import torch
import torch.nn as nn
import torch.nn.functional as F

class HexNet(nn.Module):
    def __init__(self, num_channels, vec_size, board_size):
        super(HexNet, self).__init__()

        self.conv1 = nn.Conv2d(num_channels, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)

        self.fc_vec = nn.Linear(vec_size, 32)

        self.fc_combined = nn.Linear(64 * board_size * board_size + 32, 256)

        self.policy_head = nn.Linear(256, board_size * board_size)
        self.value_head = nn.Linear(256, 1)

    def forward(self, board, vector):
        x_board = F.relu(self.conv1(board))
        x_board = F.relu(self.conv2(x_board))
        x_board = x_board.view(x_board.size(0), -1)
        
        x_vec = F.relu(self.fc_vec(vector))
        
        combined = torch.cat((x_board, x_vec), dim=1)
        combined = F.relu(self.fc_combined(combined))

        policy = F.softmax(self.policy_head(combined), dim=1)
        value = torch.tanh(self.value_head(combined))
        
        return policy, value