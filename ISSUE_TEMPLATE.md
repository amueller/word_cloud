#### Description
<!-- Example: Duplicate words shown when input is sorted list -->

#### Steps/Code to Reproduce
<!--
It's unlikely your issue can be resolved unless you provide
a short, self contained correct example to reproduce (see http://sscce.org/).

Example:
```python
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from wordcloud import WordCloud
a = 'this is a wordcloud show test'
wc = WordCloud().generate(a)
wc.to_file('wc.jpg')
plt.imshow(wc)
plt.axis('off')
plt.savefig('plt.png')
```
If the code is too long, feel free to put it in a public gist and link
it in the issue: https://gist.github.com
-->

#### Expected Results
<!-- Example: No error is thrown. Please paste or describe the expected results.-->

#### Actual Results
<!-- Please paste or specifically describe the actual output or traceback. -->

#### Versions
<!--
Please run the following snippet and paste the output below.
import platform; print(platform.platform())
import sys; print("Python", sys.version)
import numpy; print("NumPy", numpy.__version__)
import matplotlib; print("matplotlib", matplotlib.__version__)
import wordcloud; print("wordcoud", wordcloud.__version__)
-->


<!-- Thanks for contributing! -->
