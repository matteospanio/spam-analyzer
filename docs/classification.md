# Decision Tree Classifier

Decision Tree is a supervised learning algorithm that can be used for both classification and regression problems, but mostly it is preferred for solving classification problems. In this algorithm, we start from the root node of the tree. Root node represents entire population or sample and this further gets divided into two or more homogeneous sets. It is further divided on the basis of most significant splitter or differentiator in input variables.

Decision tree has three types of nodes:

- Root Node: It represents entire population or sample and this further gets divided into two or more homogeneous sets.

- Splitting: It is a process of dividing a node into two or more sub-nodes.

- Decision Node: When a sub-node splits into further sub-nodes, then it is called decision node.

- Leaf/ Terminal Node: Nodes do not split is called Leaf or Terminal node.

## Advantages of Decision Tree

- Simple to understand and to interpret. Trees can be visualised.

- Requires little data preparation. Other techniques often require data normalisation, dummy variables need to be created and blank values to be removed. Note however that this module does not support missing values.

- The cost of using the tree (i.e., predicting data) is logarithmic in the number of data points used to train the tree.

- Able to handle both numerical and categorical data. Other techniques are usually specialised in analysing datasets that have only one type of variable. See algorithms for more information.

- Able to handle multi-output problems.

- Uses a white box model. If a given situation is observable in a model, the explanation for the condition is easily explained by boolean logic. By contrast, in a black box model (e.g., in an artificial neural network), results may be more difficult to interpret.

## The Dataset

The dataset is a composition of spam and non-spam messages. They were taken from the SpamAssassin Public Corpus and untroubled.org.