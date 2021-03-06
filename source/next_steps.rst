Next Steps
==========

We've showed latent space that was only trained on string reconstruction can be used to accurately
predict simplistic properties of a molecule with a separate fully connected neural net. In addition,
it performs marginally well on more complex properties that would normally be much more
computational intensive. All of this on input vectors that have no context for this properties.

We'd like to see the performance of these predictions if the latent space *did* have context
of the molecular properties. However, we saw that training both the VAE and prediction greatly
decreased the performance of both.

In our next steps, we will try starting with a *pretrained VAE* model, then attach the prediction
layer and try training both at the same time. Starting with a good embedding, we should be able
to more easily fine tune the network to produce a latent space that is aware of the property
we're trying to predict. We may also need to adjust the learning rate of different sections,
possibly decreasing the learning rate of the VAE as compared to the prediction network to make
the embedding more stable.

Thanks!
^^^^^^^
Thanks for reading my Deep Learning Final! I hope you thought it was interesting.
Some of this may eventually be put into a paper, so thanks for suffering through the
formal language as well.