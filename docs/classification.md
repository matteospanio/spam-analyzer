# The classification task

The task could be solved in a programmatic way, chaining a long set of `if` statements based on the features extracted from the email. However, this approach is not scalable and it is not easy to maintain. Moreover, it is not possible to improve the accuracy of the model without changing the code and, the most important, the analysis would be based on the conaissance of the programmer and not on the data. Since we live in the data era, we should use the data to solve the problem, not the programmer's knowledge. So I decided to use a machine learning algorithm to solve the problem.

## Advantages of a white box approach


## The Dataset

The dataset is a composition of spam and non-spam messages. They were taken from the SpamAssassin Public Corpus](https://spamassassin.apache.org/old/publiccorpus/), [untroubled.org](http://untroubled.org/spam/) and personal emails.