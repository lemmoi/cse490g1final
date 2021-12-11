Training With a Frozen VAE
==========================

Since training the VAE and prediction network at the same time was not
successful for complex electronic properties like LUMO, the next idea
was to freeze a well-trained VAE and train the prediction network separately.
Though the embedding would only have structure information captured for
reconstruction, it could potentially be enough to predict properties from
directly.

To do this, we extracted the latent space for the train and test sets from
the 4x-128 model `published here. <https://github.com/oriondollar/TransVAE/blob/master/checkpoints/trans4x-128_zinc.ckpt>`_
These fixed vectors were fed
directly into the property prediction network, which allowed for much faster
iteration of design, since the forward pass no longer needed to go through
the encoder.

After many trials on SASA (below), the best performing network
was found to be 3 layer fully connected with 256 dimensions per layer. The
first two layers also were followed by ReLU and batch normalization. Training
was performed for 70 epochs with a batch size of 128, the Adam optimizer with default
parameters, a starting learning rate of 0.001, and Pytorch's dynamic learning rate
scheduler `ReduceLROnPlateau <https://pytorch.org/docs/stable/generated/torch.optim.lr_scheduler.ReduceLROnPlateau.html>`_
based on the test set loss.

.. figure:: images/frozen.png

    Architecture for training property prediction with frozen latent spaces.

For each below property, three data normalization schemes were trialed

* No normalization
* Min_Max normalization
* Z_std normalization (bringing to :math:`\mathcal{N}(0, 1)`)

Solvent Accessible Surface Area (SASA)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We began with the solvent accessible surface area (SASA),
as we expected it to be the easiest to predict from
solely structure. Since ZINC is composed of small drug like molecules,
there aren't many conformers that sterically hinder solvent access, so
this should be roughly proportional to the size of the structure.

Below is the distribution of SASA in the training data.

.. figure:: images/sasa_area_dist.svg

    Distribution of SASA in the training data.

The below plots show the normalized training and testing loss for each
normalization scheme on the left. The areas where steep drops can be
seen are where the learning rate scheduler reduced the learning rate
by a factor of 10. In order to compare the three schemes, the test
loss for each was denormalized and is shown in the larger plot.


.. figure:: images/sasa_area.svg
    :width: 900

    Left plots: SASA training and testing loss for each normalization scheme,
    with loss dependent on the scheme. Right plot: testing loss denormalized
    for each scheme so they can be directly compared. The black dot represents
    the best model.

Here we can see that no normalization scheme performed best, and ended
with an average loss of around 140. Since this is L2 loss, this is a
deviation of :math:`12 \mathrm{A}^2`, which seems pretty good from the above
distribution!

With the best model (indicated by the black dot on the plot above), we ran
prediction on all test and training data to generate the below plot. On the
x-axis is the true value, and on the y-axis is the predicted. If our model
was perfect, the scatterplot would fall exactly on on the :math:`y=x` line.
It's not perfect, but it clearly follows a good correlation (training :math:`r^2 = 0.725`,
testing :math:`r^2 = 0.782`).

.. figure:: images/sasa_area_pred.png
    :width: 600

    Actual SASA values vs Predicted SASA values. Perfect prediction falls on the
    black line.

An interesting note is the tail in the training data towards :math:`300 \mathrm{A}^2`.
**The train/test split was originally done by ensuring the same distribution of number
and types of tokens**, but clearly this doesn't reflect SASA. This likely explains why
the test loss was lower than the training loss - the test data actually has less
variation. We will see this trend repeated with other properties.

D4 Dispersion :math:`P_{int}`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As stated, we expected SASA perform fairly well, as it should largely be resolved
from structural information. Now we begin examining properties that would
normally require quantum mechanical calculations. The same pipeline we performed
for SASA is repeated here for :math:`P_{int}`, as calculated with D4. Below is
the distribution of the training data.

.. figure:: images/d4_disp_pint_dist.svg

    Distribution of :math:`P_{int}` in the training data.

Again, the plots with the three normalization schemes.


.. figure:: images/d4_disp.svg
    :width: 900

    Left plots: :math:`P_{int}` training and testing loss for each normalization scheme,
    with loss dependent on the scheme. Right plot: testing loss denormalized
    for each scheme so they can be directly compared. The black dot represents
    the best model.

This time, bringing the labels to a standard normal performed best, though marginally.
Using the best model, we plot the actual vs predicted values.

.. figure:: images/d4_disp_pint_pred.png
    :width: 600

    Actual :math:`P_{int}` values vs Predicted :math:`P_{int}` values. Perfect prediction falls on the
    black line.

This has fairly similar performance to SASA, with training :math:`r^2 = 0.746` and testing :math:`r^2 = 0.761`.
Again, wee see additional spread of the training data over the test data.
Overall, this is very promising. Since this model was trained using the frozen VAE,
the training data has no context of this property - it was predicted entirely
based on what the VAE learned for reconstruction.

XTB LUMO (Revisited)
^^^^^^^^^^^^^^^^^^^^
Finally, we revisit LUMO with this scheme. Recall when we attempted to train the VAE and this
prediction from scratch, both suffered. Will this perform better?

We've already covered the distribution of the training data in :ref:`the first attempt. <xtb_lumo_dist>`
Here are the plots of the three normalization schemes.

.. figure:: images/xtb_lumo.svg
    :width: 900

    Left plots: LUMO training and testing loss for each normalization scheme,
    with loss dependent on the scheme. Right plot: testing loss denormalized
    for each scheme so they can be directly compared. The black dot represents
    the best model.

Wow, this does much better! Standard normalization works best again, but had
some overfitting the training data towards the end, and the best model was at
epoch 54.

We can directly compare the standard normal loss (bottom left plot) to the
:ref:`previous training attempt (upper plot)<xtb_lumo_prev>`,
since it also used the standard normal scheme. That had a training loss of around 0.5,
while this achieves below 0.25, a 50% improvement. This validates our idea that
a good embedded representation was never achieved when training both at the same time.

Lastly, the actual vs predicted values of the final model.

.. figure:: images/xtb_lumo_pred.png
    :width: 600

    Actual LUMO values vs Predicted LUMO values. Perfect prediction falls on the
    black line.

This has worse predictions (training :math:`r^2 = 0.646`,
testing :math:`r^2 = 0.688`), though we expected LUMO to be more difficult to predict
since it's traditional calculation is more complex. An obvious feature is the
outliers above -0.1eV that is mostly composed of the training data. We need
to perform more investigation into this - are they inaccuracies by the DFT calculation,
or complex molecules that are vastly different from the rest of the data? Additionally,
the training data has much more variation than the testing data.

Another interesting feature is the model predicting such a wide range for the values near
-0.14eV. This seems to be the limit of what this prediction network can learn from embeddings
that were only trained for reconstruction, which leads into our next steps.
