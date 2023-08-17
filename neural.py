import torch
import torch.nn as nn
import torch.optim as optim

from tqdm import tqdm

from map import *

class TestDataGenerator():
    # input consists of a tensor representation of the map and the current position of the bubble
    # output consists of a tensor representation of the direction the bubble should move in
    def generate(n_maps, n_samples_per_map, approx_optimal_path=True):
        input_tensors = []
        output_tensors = []
        for _ in tqdm(range(n_maps)):
            map = MapGenerator().generate(1000, 1000)
            for _ in range(n_samples_per_map):
                position = MapGenerator().generate_valid_position(map)
                input_tensor, output_tensor = TestDataGenerator.generate_sample(map, position[0], position[1], approx_optimal_path)
                input_tensors.append(input_tensor)
                output_tensors.append(output_tensor)
        return input_tensors, output_tensors
    
    @staticmethod
    def generate_sample(map, x, y, approx_optimal_path=True):
        map_tensor = TestDataGenerator.map_to_tensor(map) # 43
        position_tensor = TestDataGenerator.position_to_tensor(x, y) # 2

        input_tensor = torch.cat((map_tensor, position_tensor), 0) # 45
        output_tensor = TestDataGenerator.get_optimal_direction(map, x, y, approx_optimal_path)

        return input_tensor, output_tensor

    @staticmethod
    def map_to_tensor(map):
        # 10 Obstacles with x, y, width, height
        # 1 Goal with x, y, radius
        map_tensor = torch.zeros(4 * 10 + 3)
        for i, obstacle in enumerate(map.obstacles):
            map_tensor[i * 4 + 0] = obstacle.x
            map_tensor[i * 4 + 1] = obstacle.y
            map_tensor[i * 4 + 2] = obstacle.width
            map_tensor[i * 4 + 3] = obstacle.height
        map_tensor[4 * 10 + 0] = map.goal.x
        map_tensor[4 * 10 + 1] = map.goal.y
        map_tensor[4 * 10 + 2] = map.goal.radius
        return map_tensor
    
    def position_to_tensor(x, y):
        return torch.tensor([x, y], dtype=torch.float32)

    @staticmethod
    def get_optimal_direction(map, x, y, approx_optimal_path=True):
        if approx_optimal_path:
            optimal_path_to_goal = MapPathFinder.generate_approx_path_from(map, x, y)
        else:
            optimal_path_to_goal = MapPathFinder.generate_optimal_path_from(map, x, y)
        if len(optimal_path_to_goal) > 1:
            optimal_direction = optimal_path_to_goal[0].direction_to_checkpoint(optimal_path_to_goal[1])
            return torch.tensor([optimal_direction[0], optimal_direction[1]], dtype=torch.float32)
        else:
            return torch.tensor([0, 0], dtype=torch.float32)

    
if __name__ == "__main__":
    # set pytorch seed
    torch.manual_seed(0)
    seed(1)

    num_epochs = 30
    batch_size = 10


    bubble_network = nn.Sequential(
        nn.Linear(45, 100),
        nn.ReLU(),
        nn.Linear(100, 100),
        nn.ReLU(),
        nn.Linear(100, 2)
    )

    loss_fn = nn.MSELoss()
    optimizer = optim.Adam(bubble_network.parameters(), lr=0.001)

    # load training data from data/ folder if available
    try:
        input_tensors = torch.load("data/input_tensors.pt")
        output_tensors = torch.load("data/output_tensors.pt")
    except:
        input_tensors, output_tensors = TestDataGenerator.generate(1000, 10)

        # store training data to data/ folder
        torch.save(input_tensors, "data/input_tensors.pt")
        torch.save(output_tensors, "data/output_tensors.pt")

    # check if cuda is available
    if torch.cuda.is_available():
        bubble_network.cuda()
        loss_fn.cuda()
        input_tensors = [input_tensor.cuda() for input_tensor in input_tensors]
        output_tensors = [output_tensor.cuda() for output_tensor in output_tensors]

    for epoch in range(num_epochs):
        for i in range(0, len(input_tensors), batch_size):
            batch_input = input_tensors[i:i+batch_size]
            batch_output = output_tensors[i:i+batch_size]

            batch_output = torch.stack(batch_output)
            batch_output = batch_output.view(batch_size, 2)

            optimizer.zero_grad()
            output = bubble_network.forward(torch.stack(batch_input))
            loss = loss_fn(output, batch_output)
            loss.backward()
            optimizer.step()
        print("Epoch: {}, Loss: {}".format(epoch, loss.item()))

    # test network
    map = MapGenerator().generate(1000, 1000)
    position = MapGenerator().generate_valid_position(map)
    input_tensor, output_tensor = TestDataGenerator.generate_sample(map, position[0], position[1])
    output = bubble_network.forward(input_tensor)
    print("Input: {}".format(input_tensor))
    print("Output: {}".format(output))
    print("Expected: {}".format(output_tensor))
    print("Distance: {}".format(output_tensor - output))
    print("Distance: {}".format(torch.dist(output_tensor, output)))
        
            