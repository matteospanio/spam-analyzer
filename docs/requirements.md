## Requirements
| Done | Name | Priority | Description |
|:-:|---|:--:|--|
| ✔️ | Analyze single files | high | The app should take in input a single email file and analyze it. |
| ✔️ | Analyze a list of files | high | The app should take in input a list of email files and analyze them. |
| ✔️ |Handle non-mail files | high | The app should gently handle non email files, notifying to the user a wrong input, but should not stop its execution |
| ✔️ | Display results to STDOUT | high | The app should display an interface with a detailed analysis of each file taken in input |
| 🚧 | Output the analysis results | high | The app should output the analysis results in varoius formats (currently only json is aviable) to make possible further analysis with other tools |
| ❌ | Fast analysis | high | The analysis should be parallelized to make it faster where possible
| ❌ | Train the model on your own dataset | medium | The app should be able to personalize the ML model using a dataset provided by the user. |

✔️ = done | 🚧 = in progress | ❌ = todo
