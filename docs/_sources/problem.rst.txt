Project Background
==================


Background
-----------

Deep learning has been finding applications in areas far broader than just computer vision
or natural language processing. One of these domains is chemistry. For example:
can deep learning be used to find a synthesize molecule with a desired property,
like corrosion resistance? Before that, can deep learning even predict these
properties when only given a molecule topology? The current method for determining
chemical properties (without doing a real world experiment) typically involves
density functional theory (DFT), a very expensive computational method that
simulates molecules as a quantum system - i.e., highly nonlinear. But, if
atomistic structures can be processed to predict a given property, the result
could be backpropagated to find a molecule with a desired quantity.

These ideas draw some parallel to NLP. Organic molecules have structure and
follow a sort of 'grammar' in how atoms can stably bond, much like sentence
structure and grammar. In prediction of properties like sentiment, a discrete
sentence is brought to a continuous latent space, which is then used to predict
the property. It's no surprise then that NLP techniques likes transformers are
commonly applied.

Previous Work
-------------

This project builds on the work of Dollar, *et. al.*, (REFERENCE) which defined a network
architecture for creating this latent embedding of molecules using a transformer-based
variational autoencoder. Molecules are represented as
`SMILES <https://en.wikipedia.org/wiki/Simplified_molecular-input_line-entry_system>`_
strings, a canonical sequence that encodes the bonds and atoms of a molecule. This
model is trained by bringing the strings into a continuous latent space using an
encoder, then reconstructed to the same discrete SMILES string using a decoder.

.. figure:: images/SMILES.webp

    Example of the structure and corresponding SMILES string of Ciprofloxacin

Proposal
--------
The continuous latent space from the model developed by Dollar, *et. al.*, will
be used as the input for a separate property prediction network. The original
model was trained on SMILES strings from the ZINC (REFERENCE) dataset, but lacks
corresponding property data, so these will need to be calculated first. Then a
fully connected network will be trained, with latent representation as the input
and a desired property as the output. This network maybe entirely separate (e.g.,
using a pretrained model) or trained at the same time as the VAE to optimize the
latent space for property prediction.