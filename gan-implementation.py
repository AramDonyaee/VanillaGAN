import torch
import torch.optim as optim
import torch.nn as nn
from torch.utils import data
import torchvision
import matplotlib.pyplot as plt
import numpy as np


# initializing hyperparameteres
learning_rate = 3e-4
noise_dim = 32
image_dim = 28 * 28 * 1 # accroding to MNIST
batch_size = 32
num_epochs = 25


# Setting up Generator Architecture
class Generator(nn.Module):
  def __init__(self, noise_dim, image_dim):
    super(Generator, self).__init__()
    self.linear1 = nn.Linear(noise_dim, 128)
    self.relu = nn.LeakyReLU(0.01)
    self.linear2 = nn.Linear(128, image_dim)
    self.tanh = nn.Tanh()
  
  def forward(self, x):
    out = self.linear1(x)
    out = self.relu(out)
    out = self.linear2(out)
    out = self.tanh(out)
    return out

# Setting up Discriminator Architecture 
class Discriminator(nn.Module):
  def __init__(self, in_image):
    super(Discriminator, self).__init__()
    self.linear1 = nn.Linear(in_image, 64)
    self.relu = nn.LeakyReLU(0.01)
    self.linear2 = nn.Linear(64, 1)
    self.sigmoid = nn.Sigmoid() # for getting output between 0 and 1 [probability]
  
  def forward(self, x):
    out = self.linear1(x)
    out = self.relu(out)
    out = self.linear2(out)
    out = self.sigmoid(out)
    return out


discriminator = Discriminator(image_dim)
generator = Generator(noise_dim, image_dim)


# Importing and normalizing the MNIST dataset
tf = torchvision.transforms.Compose(
    [torchvision.transforms.ToTensor(),torchvision.transforms.Normalize((0.5,), (0.5,)),]
)
ds = torchvision.datasets.MNIST(root="dataset/", transform=tf, download=True)
loader = data.DataLoader(ds, batch_size=batch_size, shuffle=True)


# Visualizing real data
real_sample = iter(loader).next()[0]
img_grid_real = torchvision.utils.make_grid(real_sample, normalize=True)
npgrid = img_grid_real.cpu().numpy()
plt.imshow(np.transpose(npgrid, (1, 2, 0)), interpolation='nearest')
plt.axis('off')

# Setting up optimizers for both networks
# Specifying loss function --> BCELoss
opt_discriminator = optim.Adam(discriminator.parameters(), lr=learning_rate)
opt_generator = optim.Adam(generator.parameters(), lr=learning_rate)
criterion = nn.BCELoss()

# Starting Training our GAN
for epoch in range(num_epochs):
    for id, (training_sample, _) in enumerate(loader):
        training_sample = training_sample.view(-1, 784)
        batch_size = training_sample.shape[0]

        ### Training the Discriminator
        noise = torch.randn(batch_size, noise_dim)
        fake_sample = generator(noise)
        disc_realSample = discriminator(training_sample).view(-1)
        lossD_realSample = criterion(disc_realSample, torch.ones_like(disc_realSample))
        disc_fakeSample = discriminator(fake_sample).view(-1)
        lossD_fakeSample = criterion(disc_fakeSample, torch.zeros_like(disc_fakeSample)) 
        lossD = (lossD_realSample + lossD_fakeSample) / 2
        discriminator.zero_grad()

        # Minimizing the total classification error by backpropagating
        lossD.backward(retain_graph=True)
        opt_discriminator.step()

        ### Training the Generator
        lossD_fakeSample = discriminator(fake_sample).view(-1)
        lossG = criterion(lossD_fakeSample, torch.ones_like(lossD_fakeSample)) # maximizing the error of classification of fake image by the discriminator
        generator.zero_grad()
        lossG.backward()
        opt_generator.step()

        if id == 0:
            print( "Epoch: {epoch} \t Discriminator Loss: {lossD} Generator Loss: {lossG}".format( epoch=epoch, lossD=lossD, lossG=lossG))

# Creating Random noise (latent space generation)
latent_space_samples = torch.randn(batch_size, noise_dim)

# Visulizing fake data generated by our GAN
fake = generator(latent_space_samples).reshape(-1, 1, 28, 28)
img_grid_fake = torchvision.utils.make_grid(fake, normalize=True)
npgrid = img_grid_fake.cpu().numpy()
plt.imshow(np.transpose(npgrid, (1, 2, 0)), interpolation='nearest')
plt.axis('off')