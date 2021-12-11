Initial Training
================


The first attempts at property prediction were made by training the VAE and
prediction network from scratch simultaneously.

Architecture
------------

The TransVAE package implements multiple transformer based variational autoencoders.
We chose to use the 4x-128 architecture, which refers to four 128 dim attention heads,
with four layers of self-attention and three layers of source-attention.
Training 100 epochs takes approximately one day on a RTX 2080Ti.

The TransVAE package also provides a method to add this property prediction network
from the command line. For all of the below, two fully connected layers of size (128x200),
(200x1) with LRU activation were attached to the 128 dim latent space for property
prediction.

.. figure:: images/initial_training.png

    Property prediction and VAE training at the same time.


Hydrogen Acceptors
------------------
The first property that we attempted to predict was the number of hydrogen acceptors.
We considered this fairly easy property because it does not require a true property
calculation and can just be determined by the number of N, O, and F's present in the
molecule. These should be embedded in the latent space, as it is directly required
for reconstruction, so it should be fairly easy for a prediction network to extract
them if reconstruction is also good.

Since this property is :math:`\in \mathbb{N}`, it was normalized to :math:`\in [0, 1]`
using min-max normalization on the training data. The same normalization as the training
was applied to the validation and testing data. A plot of the unnormalized distribution
for the training data can be seen below

.. figure:: images/hbond_dist.svg

    caption

Results
^^^^^^^

For final evaluation, the outputs had the normalization transformation undone, then
rounded to the nearest integer. After 100 epochs, this achieved 99.9% accuracy on
the training data and 99.8% accuracy on the test data, while still maintaining a reconstruction
loss comparable to the base model without a predictor. The training plots for
the property prediction and the loss from the rest of the network (reconstruction,
prediction, and KLD) are shown below.

.. figure:: images/h_acc_training.svg

    Loss

As stated above, this was expected because we knew this information must've been present in the latent space
for accurate reconstruction. The broader question was if the latent space could encode properties
that had non-linear relationships.

XTB LUMO
--------

.. _xtb_lumo_dist:

The next property we tried to predict was Lowest Unoccupied Molecular Orbital (LUMO) energy level,
as calculated with XTB. This is :math:`\in \mathbb{R}` and roughly normal, but with some far
outliers, as shown below. We applied standard normalization on the training dataset,
and the same transformation to the validation and test datasets.

.. figure:: images/xtb_lumo_dist.svg

    Loss

Results
^^^^^^^

Surprisingly, this model performed very poorly. Not only was the property prediction loss
high, but the reconstruction loss was now much higher than the models without a prediction
network.

.. _xtb_lumo_prev:

.. figure:: images/xtb_lumo_training.svg

    Loss

It seems as though the prediction network took too much of the available 'power'
of the model. The encoder/decoder were unable to accurately reconstruct the molecule,
meaning that an meaningful representation was never able to be embedded in the
bottleneck. This inspired the next idea.